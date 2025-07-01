"""
GridWorks Subscription Management System
Stripe + Setu API integration with WhatsApp-native billing
"""

import asyncio
import stripe
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass

from app.core.config import settings
from app.ai_support.models import SupportTier
from app.whatsapp.client import WhatsAppClient

logger = logging.getLogger(__name__)

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


class SubscriptionStatus(Enum):
    """Subscription status types"""
    ACTIVE = "active"
    TRIAL = "trial"
    PENDING = "pending"
    PAYMENT_FAILED = "payment_failed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class BillingCycle(Enum):
    """Billing cycle options"""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUAL = "annual"


@dataclass
class TierPricing:
    """Tier pricing configuration"""
    tier: SupportTier
    monthly_price: int  # In paise (₹99 = 9900 paise)
    quarterly_price: int
    annual_price: int
    setup_fee: int
    per_trade_fee: int
    features: List[str]


class SubscriptionManager:
    """
    Comprehensive subscription management for GridWorks multi-tier platform
    
    Features:
    - Stripe subscription integration
    - WhatsApp-native billing experience
    - Setu API for seamless payment collection
    - Per-trade charge automation
    - Tier upgrade/downgrade management
    """
    
    def __init__(self):
        self.whatsapp_client = WhatsAppClient()
        self.setu_client = SetuBillingClient()
        
        # Tier pricing configuration
        self.tier_pricing = {
            SupportTier.LITE: TierPricing(
                tier=SupportTier.LITE,
                monthly_price=0,  # Free tier
                quarterly_price=0,
                annual_price=0,
                setup_fee=0,
                per_trade_fee=200,  # ₹2 per trade
                features=["Basic Trading", "AI Support", "11 Languages"]
            ),
            SupportTier.PRO: TierPricing(
                tier=SupportTier.PRO,
                monthly_price=9900,  # ₹99/month
                quarterly_price=26700,  # ₹267/quarter (10% discount)
                annual_price=95400,  # ₹954/year (20% discount)
                setup_fee=0,
                per_trade_fee=500,  # ₹5 per trade
                features=["Professional Tools", "Advanced AI", "Priority Support", "Voice Trading"]
            ),
            SupportTier.ELITE: TierPricing(
                tier=SupportTier.ELITE,
                monthly_price=299900,  # ₹2,999/month
                quarterly_price=809700,  # ₹8,097/quarter (10% discount)
                annual_price=2879200,  # ₹28,792/year (20% discount)
                setup_fee=2500000,  # ₹25,000 setup fee
                per_trade_fee=1000,  # ₹10 per trade (but free for >₹50L trades)
                features=["Executive Analytics", "Dedicated Support", "Portfolio Management", "Market Intelligence"]
            ),
            SupportTier.BLACK: TierPricing(
                tier=SupportTier.BLACK,
                monthly_price=1500000,  # ₹15,000/month
                quarterly_price=4050000,  # ₹40,500/quarter (10% discount)
                annual_price=14400000,  # ₹1,44,000/year (20% discount)
                setup_fee=10000000,  # ₹1,00,000 setup fee
                per_trade_fee=0,  # No per-trade fees for Black tier
                features=["Concierge Service", "Butler AI", "Emergency Response", "Luxury Partners", "Zero Fees"]
            )
        }
        
        logger.info("Subscription Manager initialized with Stripe + Setu integration")
    
    async def create_subscription(
        self,
        user_id: str,
        phone: str,
        tier: SupportTier,
        billing_cycle: BillingCycle = BillingCycle.MONTHLY,
        payment_method: str = "upi"
    ) -> Dict[str, Any]:
        """Create new subscription with WhatsApp-native experience"""
        
        try:
            logger.info(f"Creating {tier.value} subscription for user {user_id}")
            
            # Step 1: Get tier pricing
            pricing = self.tier_pricing[tier]
            
            if tier == SupportTier.LITE:
                # Free tier - just activate
                return await self._activate_free_tier(user_id, phone)
            
            # Step 2: Create Stripe customer
            stripe_customer = await self._create_stripe_customer(user_id, phone)
            
            # Step 3: Calculate pricing based on cycle
            amount = self._get_cycle_price(pricing, billing_cycle)
            
            # Step 4: Send WhatsApp billing request
            billing_request = await self._send_whatsapp_billing_request(
                phone, tier, amount, billing_cycle, stripe_customer["id"]
            )
            
            # Step 5: Create Setu payment link for seamless UPI
            if payment_method == "upi":
                payment_link = await self.setu_client.create_payment_link(
                    amount=amount,
                    customer_id=stripe_customer["id"],
                    description=f"GridWorks {tier.value} Subscription",
                    callback_url=f"https://api.gridworks.ai/billing/callback"
                )
                
                # Send UPI payment link via WhatsApp
                await self._send_upi_payment_link(phone, payment_link, tier, amount)
            
            # Step 6: Create pending subscription in Stripe
            subscription = stripe.Subscription.create(
                customer=stripe_customer["id"],
                items=[{
                    "price_data": {
                        "currency": "inr",
                        "product_data": {
                            "name": f"GridWorks {tier.value} Subscription"
                        },
                        "unit_amount": amount,
                        "recurring": {
                            "interval": "month" if billing_cycle == BillingCycle.MONTHLY else 
                                      "year" if billing_cycle == BillingCycle.ANNUAL else "month",
                            "interval_count": 3 if billing_cycle == BillingCycle.QUARTERLY else 1
                        }
                    }
                }],
                payment_behavior="default_incomplete",
                expand=["latest_invoice.payment_intent"]
            )
            
            return {
                "success": True,
                "subscription_id": subscription.id,
                "customer_id": stripe_customer["id"],
                "payment_link": payment_link.get("payment_url") if payment_method == "upi" else None,
                "amount": amount / 100,  # Convert paise to rupees
                "tier": tier.value,
                "billing_cycle": billing_cycle.value,
                "status": "pending_payment",
                "features": pricing.features
            }
            
        except Exception as e:
            logger.error(f"Subscription creation failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _send_whatsapp_billing_request(
        self,
        phone: str,
        tier: SupportTier,
        amount: int,
        billing_cycle: BillingCycle,
        customer_id: str
    ) -> Dict[str, Any]:
        """Send billing request via WhatsApp with interactive elements"""
        
        # Convert amount from paise to rupees
        amount_rupees = amount / 100
        
        # Tier-specific messaging
        tier_messages = {
            SupportTier.PRO: f"🚀 Welcome to GridWorks PRO!\n\n₹{amount_rupees:,.0f}/{billing_cycle.value} subscription includes:\n⚡ Professional trading tools\n🤖 Advanced AI support\n🎤 Voice trading\n📊 Premium analytics\n\n*Tap below to complete payment*",
            SupportTier.ELITE: f"👑 Welcome to GridWorks ELITE!\n\n₹{amount_rupees:,.0f}/{billing_cycle.value} subscription includes:\n🏛️ Executive analytics\n📹 Dedicated support specialist\n📊 Portfolio management\n🎯 Market intelligence\n\n*White-glove payment processing below*",
            SupportTier.BLACK: f"◆ Welcome to GridWorks BLACK!\n\n₹{amount_rupees:,.0f}/{billing_cycle.value} subscription includes:\n🎩 24/7 concierge service\n🤖 Dedicated butler AI\n🚁 Emergency response\n🏛️ Luxury partner network\n💳 Zero trading fees\n\n*Exclusive payment processing below*"
        }
        
        message = tier_messages.get(tier, f"Subscription: ₹{amount_rupees:,.0f}/{billing_cycle.value}")
        
        # Send interactive WhatsApp message
        await self.whatsapp_client.send_interactive_message(
            phone=phone,
            message=message,
            buttons=[
                {"id": f"pay_upi_{customer_id}", "title": "Pay with UPI"},
                {"id": f"pay_card_{customer_id}", "title": "Pay with Card"},
                {"id": f"help_billing_{customer_id}", "title": "Need Help?"}
            ]
        )
        
        return {"sent": True, "customer_id": customer_id}
    
    async def _send_upi_payment_link(
        self,
        phone: str,
        payment_link: Dict[str, Any],
        tier: SupportTier,
        amount: int
    ):
        """Send UPI payment link via WhatsApp"""
        
        amount_rupees = amount / 100
        
        # Tier-specific UPI messaging
        upi_message = f"💳 *UPI Payment Link*\n\n"
        upi_message += f"Amount: ₹{amount_rupees:,.0f}\n"
        upi_message += f"Service: GridWorks {tier.value}\n\n"
        upi_message += f"🔗 Secure Payment: {payment_link['payment_url']}\n\n"
        upi_message += f"✅ Pay with any UPI app\n"
        upi_message += f"🔒 Bank-grade security\n"
        upi_message += f"⚡ Instant activation\n\n"
        upi_message += f"*Questions? Reply 'help' anytime*"
        
        await self.whatsapp_client.send_message(phone, upi_message)
    
    async def handle_subscription_payment_success(
        self,
        subscription_id: str,
        payment_intent_id: str
    ) -> Dict[str, Any]:
        """Handle successful subscription payment"""
        
        try:
            # Retrieve subscription from Stripe
            subscription = stripe.Subscription.retrieve(subscription_id)
            customer = stripe.Customer.retrieve(subscription.customer)
            
            # Get user info from customer metadata
            user_id = customer.metadata.get("user_id")
            phone = customer.metadata.get("phone")
            tier = SupportTier(customer.metadata.get("tier"))
            
            # Activate subscription
            await self._activate_subscription(user_id, tier, subscription_id)
            
            # Send confirmation via WhatsApp
            await self._send_subscription_confirmation(phone, tier, subscription)
            
            # Setup per-trade billing if applicable
            if tier in [SupportTier.LITE, SupportTier.PRO, SupportTier.ELITE]:
                await self._setup_per_trade_billing(user_id, tier)
            
            return {
                "success": True,
                "subscription_activated": True,
                "user_id": user_id,
                "tier": tier.value
            }
            
        except Exception as e:
            logger.error(f"Payment success handling failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def collect_per_trade_fee(
        self,
        user_id: str,
        trade_amount: float,
        symbol: str,
        trade_id: str
    ) -> Dict[str, Any]:
        """Collect per-trade fees automatically"""
        
        try:
            # Get user's current tier
            user_tier = await self._get_user_tier(user_id)
            pricing = self.tier_pricing[user_tier]
            
            # Calculate fee
            if user_tier == SupportTier.BLACK:
                # No per-trade fees for Black tier
                return {"fee_collected": 0, "tier": "BLACK", "waived": True}
            
            # Calculate fee based on tier and trade amount
            if user_tier == SupportTier.ELITE and trade_amount >= 5000000:  # ₹50L+
                # Free for large trades in ELITE
                fee_amount = 0
                waived = True
            else:
                fee_amount = pricing.per_trade_fee
                waived = False
            
            if fee_amount > 0:
                # Collect fee via Setu API (instant debit)
                fee_collection = await self.setu_client.collect_instant_fee(
                    user_id=user_id,
                    amount=fee_amount,
                    description=f"Trading fee for {symbol} - {trade_id}",
                    metadata={
                        "trade_id": trade_id,
                        "symbol": symbol,
                        "trade_amount": trade_amount,
                        "tier": user_tier.value
                    }
                )
                
                if fee_collection["success"]:
                    # Log successful fee collection
                    await self._log_fee_collection(user_id, trade_id, fee_amount, "success")
                    
                    return {
                        "fee_collected": fee_amount / 100,  # Convert to rupees
                        "transaction_id": fee_collection["transaction_id"],
                        "tier": user_tier.value,
                        "waived": False
                    }
                else:
                    # Handle fee collection failure
                    await self._handle_fee_collection_failure(user_id, trade_id, fee_amount)
                    return {"fee_collected": 0, "error": "Collection failed", "retry_scheduled": True}
            
            return {"fee_collected": 0, "tier": user_tier.value, "waived": waived}
            
        except Exception as e:
            logger.error(f"Per-trade fee collection failed: {e}")
            return {"fee_collected": 0, "error": str(e)}
    
    async def handle_subscription_upgrade(
        self,
        user_id: str,
        phone: str,
        current_tier: SupportTier,
        target_tier: SupportTier
    ) -> Dict[str, Any]:
        """Handle tier upgrade with prorated billing"""
        
        try:
            # Calculate proration
            proration = await self._calculate_tier_upgrade_proration(
                current_tier, target_tier, user_id
            )
            
            # Send upgrade offer via WhatsApp
            upgrade_message = f"🚀 *Upgrade to {target_tier.value}*\n\n"
            upgrade_message += f"Current: {current_tier.value}\n"
            upgrade_message += f"Upgrade to: {target_tier.value}\n\n"
            
            if proration["credit_amount"] > 0:
                upgrade_message += f"💰 Credit: ₹{proration['credit_amount']:.0f}\n"
            
            upgrade_message += f"💳 Additional: ₹{proration['additional_amount']:.0f}\n"
            upgrade_message += f"📅 Next billing: {proration['next_billing_date']}\n\n"
            
            # Add tier-specific benefits
            target_pricing = self.tier_pricing[target_tier]
            upgrade_message += "*New features:*\n"
            for feature in target_pricing.features:
                upgrade_message += f"✅ {feature}\n"
            
            # Send interactive upgrade option
            await self.whatsapp_client.send_interactive_message(
                phone=phone,
                message=upgrade_message,
                buttons=[
                    {"id": f"upgrade_confirm_{user_id}", "title": "Upgrade Now"},
                    {"id": f"upgrade_later_{user_id}", "title": "Maybe Later"},
                    {"id": f"upgrade_help_{user_id}", "title": "Learn More"}
                ]
            )
            
            return {
                "upgrade_offer_sent": True,
                "proration": proration,
                "target_tier": target_tier.value
            }
            
        except Exception as e:
            logger.error(f"Upgrade handling failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _create_stripe_customer(self, user_id: str, phone: str) -> Dict[str, Any]:
        """Create Stripe customer with metadata"""
        
        customer = stripe.Customer.create(
            phone=phone,
            metadata={
                "user_id": user_id,
                "phone": phone,
                "platform": "gridworks",
                "created_via": "whatsapp"
            }
        )
        
        return customer
    
    def _get_cycle_price(self, pricing: TierPricing, cycle: BillingCycle) -> int:
        """Get price based on billing cycle"""
        
        if cycle == BillingCycle.MONTHLY:
            return pricing.monthly_price
        elif cycle == BillingCycle.QUARTERLY:
            return pricing.quarterly_price
        elif cycle == BillingCycle.ANNUAL:
            return pricing.annual_price
        
        return pricing.monthly_price
    
    async def _activate_free_tier(self, user_id: str, phone: str) -> Dict[str, Any]:
        """Activate free LITE tier"""
        
        # No payment required, just activate
        await self._activate_subscription(user_id, SupportTier.LITE, None)
        
        # Send welcome message
        welcome_message = "🎉 *Welcome to GridWorks LITE!*\n\n"
        welcome_message += "✅ Free basic trading\n"
        welcome_message += "🤖 AI support\n"
        welcome_message += "🗣️ 11 Indian languages\n"
        welcome_message += "💳 ₹2 per trade\n\n"
        welcome_message += "*Start trading: Type 'buy TCS 10 shares'*"
        
        await self.whatsapp_client.send_message(phone, welcome_message)
        
        return {
            "success": True,
            "tier": "LITE",
            "subscription_fee": 0,
            "per_trade_fee": 2,
            "status": "active"
        }


class SetuBillingClient:
    """Setu API client for seamless billing integration"""
    
    def __init__(self):
        self.base_url = settings.SETU_BASE_URL
        self.client_id = settings.SETU_CLIENT_ID
        self.client_secret = settings.SETU_CLIENT_SECRET
    
    async def create_payment_link(
        self,
        amount: int,
        customer_id: str,
        description: str,
        callback_url: str
    ) -> Dict[str, Any]:
        """Create UPI payment link via Setu"""
        
        # Mock implementation - replace with actual Setu API calls
        return {
            "payment_url": f"upi://pay?pa=gridworks@paytm&pn=GridWorks&am={amount/100}&cu=INR&tn={description}",
            "payment_id": f"SETU_{customer_id}_{int(datetime.now().timestamp())}",
            "expires_at": (datetime.now() + timedelta(hours=1)).isoformat()
        }
    
    async def collect_instant_fee(
        self,
        user_id: str,
        amount: int,
        description: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Collect instant fee via Setu Account Aggregator"""
        
        # Mock implementation - replace with actual Setu API
        return {
            "success": True,
            "transaction_id": f"TXN_{user_id}_{int(datetime.now().timestamp())}",
            "amount": amount,
            "status": "success",
            "collected_at": datetime.now().isoformat()
        }


# Demo usage
async def demo_subscription_flow():
    """Demonstrate subscription flow"""
    
    print("🚀 GridWorks Subscription Management Demo")
    print("=" * 50)
    
    manager = SubscriptionManager()
    
    # Test PRO subscription creation
    result = await manager.create_subscription(
        user_id="user_demo_001",
        phone="+919876543210",
        tier=SupportTier.PRO,
        billing_cycle=BillingCycle.MONTHLY,
        payment_method="upi"
    )
    
    print(f"✅ PRO Subscription Created:")
    print(f"Amount: ₹{result.get('amount', 0)}")
    print(f"Features: {result.get('features', [])}")
    print(f"Payment Link: {result.get('payment_link', 'N/A')}")
    
    # Test per-trade fee collection
    trade_fee = await manager.collect_per_trade_fee(
        user_id="user_demo_001",
        trade_amount=100000,  # ₹1L trade
        symbol="TCS",
        trade_id="TRADE_001"
    )
    
    print(f"\n💳 Per-Trade Fee:")
    print(f"Fee Collected: ₹{trade_fee.get('fee_collected', 0)}")
    print(f"Tier: {trade_fee.get('tier', 'Unknown')}")


if __name__ == "__main__":
    asyncio.run(demo_subscription_flow())