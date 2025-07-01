"""
GridWorks Auto-Debit Consent Management System
Account Aggregator framework integration for seamless per-trade fee collection
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from dataclasses import dataclass, field
import json
import uuid
import hashlib
import hmac

from app.ai_support.models import SupportTier
from app.billing.setu_integration import SetuAPIClient

logger = logging.getLogger(__name__)


class ConsentStatus(Enum):
    """Account Aggregator consent status"""
    PENDING = "pending"
    APPROVED = "approved"
    ACTIVE = "active"
    PAUSED = "paused"
    REVOKED = "revoked"
    EXPIRED = "expired"


class ConsentFrequency(Enum):
    """Consent collection frequency"""
    DAILY = "daily"
    WEEKLY = "weekly"  
    MONTHLY = "monthly"
    PER_TRANSACTION = "per_transaction"


class ConsentPurpose(Enum):
    """Purpose codes for AA framework"""
    TRADING_FEES = "trading_fees"
    SUBSCRIPTION_RENEWAL = "subscription_renewal"
    PORTFOLIO_MANAGEMENT = "portfolio_management"
    INVESTMENT_ADVISORY = "investment_advisory"


@dataclass
class ConsentRequest:
    """AA framework consent request structure"""
    consent_id: str
    user_id: str
    phone: str
    purpose: ConsentPurpose
    max_amount: int  # In paise
    frequency: ConsentFrequency
    validity_start: datetime
    validity_end: datetime
    accounts_requested: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConsentDetails:
    """Active consent details"""
    consent_id: str
    user_id: str
    status: ConsentStatus
    purpose: ConsentPurpose
    max_amount: int
    frequency: ConsentFrequency
    accounts_linked: List[Dict[str, Any]]
    usage_count: int
    amount_used: int
    last_used: Optional[datetime]
    expires_at: datetime
    created_at: datetime
    updated_at: datetime


class AutoDebitConsentManager:
    """
    Account Aggregator based auto-debit consent management
    
    Features:
    - SEBI-compliant consent collection
    - Automated consent renewal
    - Usage monitoring and limits
    - Tier-based consent requirements
    - Intelligent retry mechanisms
    """
    
    def __init__(self):
        self.setu_client = SetuAPIClient()
        
        # Tier-based consent limits
        self.tier_limits = {
            SupportTier.LITE: {
                "max_amount": 50000,  # ₹500 per transaction
                "daily_limit": 500000,  # ₹5,000 per day
                "monthly_limit": 5000000,  # ₹50,000 per month
                "frequency": ConsentFrequency.DAILY
            },
            SupportTier.PRO: {
                "max_amount": 100000,  # ₹1,000 per transaction
                "daily_limit": 1000000,  # ₹10,000 per day
                "monthly_limit": 10000000,  # ₹1,00,000 per month
                "frequency": ConsentFrequency.DAILY
            },
            SupportTier.ELITE: {
                "max_amount": 500000,  # ₹5,000 per transaction
                "daily_limit": 5000000,  # ₹50,000 per day
                "monthly_limit": 50000000,  # ₹5,00,000 per month
                "frequency": ConsentFrequency.WEEKLY
            }
        }
        
        logger.info("Auto-Debit Consent Manager initialized")
    
    async def initiate_consent_request(
        self,
        user_id: str,
        phone: str,
        tier: SupportTier,
        purpose: ConsentPurpose = ConsentPurpose.TRADING_FEES
    ) -> Dict[str, Any]:
        """Initiate consent request for auto-debit"""
        
        try:
            logger.info(f"Initiating consent request for {tier.value} user {user_id}")
            
            # Get tier-specific limits
            limits = self.tier_limits.get(tier, self.tier_limits[SupportTier.LITE])
            
            # Generate consent request
            consent_request = ConsentRequest(
                consent_id=f"CONSENT_{uuid.uuid4().hex[:12].upper()}",
                user_id=user_id,
                phone=phone,
                purpose=purpose,
                max_amount=limits["max_amount"],
                frequency=limits["frequency"],
                validity_start=datetime.now(),
                validity_end=datetime.now() + timedelta(days=365),
                metadata={
                    "tier": tier.value,
                    "daily_limit": limits["daily_limit"],
                    "monthly_limit": limits["monthly_limit"],
                    "created_via": "gridworks_app"
                }
            )
            
            # Create consent via Account Aggregator
            aa_response = await self._create_aa_consent(consent_request)
            
            if aa_response["success"]:
                # Store consent details
                await self._store_consent_request(consent_request, aa_response)
                
                # Send user notification
                await self._send_consent_notification(user_id, phone, consent_request)
                
                return {
                    "success": True,
                    "consent_id": consent_request.consent_id,
                    "consent_url": aa_response["consent_url"],
                    "max_amount": limits["max_amount"] / 100,  # Convert to rupees
                    "frequency": limits["frequency"].value,
                    "expires_at": consent_request.validity_end.isoformat(),
                    "tier_limits": {
                        "per_transaction": limits["max_amount"] / 100,
                        "daily": limits["daily_limit"] / 100,
                        "monthly": limits["monthly_limit"] / 100
                    }
                }
            else:
                return {
                    "success": False,
                    "error": aa_response.get("error", "Consent creation failed")
                }
                
        except Exception as e:
            logger.error(f"Consent initiation failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _create_aa_consent(
        self,
        consent_request: ConsentRequest
    ) -> Dict[str, Any]:
        """Create consent via Account Aggregator framework"""
        
        try:
            async with self.setu_client as client:
                # Prepare AA consent request
                aa_data = {
                    "consentId": consent_request.consent_id,
                    "timestamp": datetime.now().isoformat(),
                    "customer": {
                        "id": consent_request.user_id,
                        "phone": consent_request.phone
                    },
                    "purpose": {
                        "code": consent_request.purpose.value,
                        "refUri": "https://gridworks.ai/consent-purpose",
                        "text": self._get_purpose_text(consent_request.purpose),
                        "Category": {
                            "type": "string"
                        }
                    },
                    "fiTypes": ["DEPOSIT"],  # Bank account data
                    "consentTypes": ["TRANSACTIONS", "PROFILE"],
                    "fetchType": "PERIODIC",
                    "frequency": {
                        "unit": self._get_aa_frequency(consent_request.frequency),
                        "value": 1
                    },
                    "DataFilter": [
                        {
                            "type": "RANGE",
                            "operator": ">=",
                            "value": "0"
                        }
                    ],
                    "DataLife": {
                        "unit": "YEAR",
                        "value": 1
                    },
                    "DataConsumer": {
                        "id": "gridworks-platform",
                        "type": "FIP"
                    },
                    "Permissions": [
                        {
                            "text": f"Auto-debit up to ₹{consent_request.max_amount/100} for {consent_request.purpose.value}",
                            "url": "https://gridworks.ai/permissions"
                        }
                    ]
                }
                
                # Make AA consent request
                response = await client._make_request(
                    "POST",
                    "/account-aggregator/consent",
                    data=aa_data
                )
                
                if response.status_code == 201:
                    data = response.json()
                    return {
                        "success": True,
                        "consent_handle": data["consentHandle"],
                        "consent_url": data["url"],
                        "session_id": data.get("sessionId"),
                        "expires_at": data.get("expiresAt")
                    }
                else:
                    return {
                        "success": False,
                        "error": f"AA consent creation failed: {response.text}"
                    }
                    
        except Exception as e:
            logger.error(f"AA consent creation error: {e}")
            return {"success": False, "error": str(e)}
    
    async def check_consent_status(
        self,
        consent_id: str
    ) -> Dict[str, Any]:
        """Check consent approval status"""
        
        try:
            async with self.setu_client as client:
                response = await client._make_request(
                    "GET",
                    f"/account-aggregator/consent/{consent_id}"
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    status_mapping = {
                        "PENDING": ConsentStatus.PENDING,
                        "ACTIVE": ConsentStatus.ACTIVE,
                        "PAUSED": ConsentStatus.PAUSED,
                        "REVOKED": ConsentStatus.REVOKED,
                        "EXPIRED": ConsentStatus.EXPIRED
                    }
                    
                    consent_status = status_mapping.get(
                        data["consentStatus"], 
                        ConsentStatus.PENDING
                    )
                    
                    return {
                        "success": True,
                        "consent_id": consent_id,
                        "status": consent_status.value,
                        "accounts_linked": data.get("linkedAccounts", []),
                        "approved_at": data.get("approvedAt"),
                        "expires_at": data.get("expiresAt")
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Consent status check failed: {response.text}"
                    }
                    
        except Exception as e:
            logger.error(f"Consent status check error: {e}")
            return {"success": False, "error": str(e)}
    
    async def execute_auto_debit(
        self,
        consent_id: str,
        amount: int,
        description: str,
        trade_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute auto-debit using approved consent"""
        
        try:
            # Validate consent is active
            consent_check = await self.check_consent_status(consent_id)
            
            if not consent_check["success"]:
                return consent_check
            
            if consent_check["status"] != ConsentStatus.ACTIVE.value:
                return {
                    "success": False,
                    "error": f"Consent not active: {consent_check['status']}"
                }
            
            # Get consent details for validation
            consent_details = await self._get_consent_details(consent_id)
            
            # Validate transaction limits
            validation = await self._validate_transaction_limits(
                consent_details, amount
            )
            
            if not validation["valid"]:
                return {
                    "success": False,
                    "error": validation["error"],
                    "limit_exceeded": True
                }
            
            # Execute debit via AA framework
            debit_result = await self._execute_aa_debit(
                consent_id, amount, description, trade_metadata
            )
            
            if debit_result["success"]:
                # Update usage tracking
                await self._update_consent_usage(
                    consent_id, amount, trade_metadata
                )
                
                # Log successful transaction
                await self._log_auto_debit_transaction(
                    consent_id, amount, debit_result["transaction_id"], "success"
                )
                
                return {
                    "success": True,
                    "transaction_id": debit_result["transaction_id"],
                    "amount": amount / 100,  # Convert to rupees
                    "consent_id": consent_id,
                    "executed_at": datetime.now().isoformat(),
                    "remaining_limits": await self._get_remaining_limits(consent_id)
                }
            else:
                return debit_result
                
        except Exception as e:
            logger.error(f"Auto-debit execution failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _execute_aa_debit(
        self,
        consent_id: str,
        amount: int,
        description: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute debit through Account Aggregator"""
        
        try:
            async with self.setu_client as client:
                debit_data = {
                    "consentId": consent_id,
                    "amount": {
                        "value": amount,
                        "currency": "INR"
                    },
                    "purpose": description,
                    "txnId": f"TXN_{uuid.uuid4().hex[:12].upper()}",
                    "timestamp": datetime.now().isoformat(),
                    "additionalInfo": metadata
                }
                
                response = await client._make_request(
                    "POST",
                    "/account-aggregator/debit",
                    data=debit_data
                )
                
                if response.status_code == 201:
                    data = response.json()
                    return {
                        "success": True,
                        "transaction_id": data["txnId"],
                        "reference_id": data.get("referenceId"),
                        "status": data.get("status", "pending")
                    }
                else:
                    return {
                        "success": False,
                        "error": f"AA debit failed: {response.text}"
                    }
                    
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _validate_transaction_limits(
        self,
        consent_details: ConsentDetails,
        amount: int
    ) -> Dict[str, Any]:
        """Validate transaction against consent limits"""
        
        try:
            # Check per-transaction limit
            if amount > consent_details.max_amount:
                return {
                    "valid": False,
                    "error": f"Amount ₹{amount/100} exceeds per-transaction limit ₹{consent_details.max_amount/100}"
                }
            
            # Check daily usage limit
            daily_usage = await self._get_daily_usage(consent_details.consent_id)
            tier_limits = self.tier_limits.get(
                SupportTier(consent_details.metadata.get("tier", "LITE"))
            )
            
            if daily_usage + amount > tier_limits["daily_limit"]:
                return {
                    "valid": False,
                    "error": f"Daily limit exceeded. Used: ₹{daily_usage/100}, Limit: ₹{tier_limits['daily_limit']/100}"
                }
            
            # Check monthly usage limit
            monthly_usage = await self._get_monthly_usage(consent_details.consent_id)
            
            if monthly_usage + amount > tier_limits["monthly_limit"]:
                return {
                    "valid": False,
                    "error": f"Monthly limit exceeded. Used: ₹{monthly_usage/100}, Limit: ₹{tier_limits['monthly_limit']/100}"
                }
            
            return {"valid": True}
            
        except Exception as e:
            logger.error(f"Limit validation error: {e}")
            return {"valid": False, "error": "Validation failed"}
    
    async def renew_consent(
        self,
        consent_id: str,
        extend_days: int = 365
    ) -> Dict[str, Any]:
        """Renew expiring consent automatically"""
        
        try:
            consent_details = await self._get_consent_details(consent_id)
            
            if not consent_details:
                return {"success": False, "error": "Consent not found"}
            
            # Create renewal request
            new_validity_end = datetime.now() + timedelta(days=extend_days)
            
            async with self.setu_client as client:
                renewal_data = {
                    "consentId": consent_id,
                    "extendsTo": new_validity_end.isoformat(),
                    "reason": "automatic_renewal"
                }
                
                response = await client._make_request(
                    "POST",
                    f"/account-aggregator/consent/{consent_id}/renew",
                    data=renewal_data
                )
                
                if response.status_code == 200:
                    # Update stored consent details
                    await self._update_consent_expiry(consent_id, new_validity_end)
                    
                    return {
                        "success": True,
                        "consent_id": consent_id,
                        "extended_to": new_validity_end.isoformat(),
                        "status": "renewed"
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Consent renewal failed: {response.text}"
                    }
                    
        except Exception as e:
            logger.error(f"Consent renewal error: {e}")
            return {"success": False, "error": str(e)}
    
    async def revoke_consent(
        self,
        consent_id: str,
        reason: str = "user_request"
    ) -> Dict[str, Any]:
        """Revoke user consent"""
        
        try:
            async with self.setu_client as client:
                revoke_data = {
                    "consentId": consent_id,
                    "reason": reason,
                    "timestamp": datetime.now().isoformat()
                }
                
                response = await client._make_request(
                    "POST",
                    f"/account-aggregator/consent/{consent_id}/revoke",
                    data=revoke_data
                )
                
                if response.status_code == 200:
                    # Update stored consent status
                    await self._update_consent_status(consent_id, ConsentStatus.REVOKED)
                    
                    return {
                        "success": True,
                        "consent_id": consent_id,
                        "status": "revoked",
                        "revoked_at": datetime.now().isoformat()
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Consent revocation failed: {response.text}"
                    }
                    
        except Exception as e:
            logger.error(f"Consent revocation error: {e}")
            return {"success": False, "error": str(e)}
    
    def _get_purpose_text(self, purpose: ConsentPurpose) -> str:
        """Get user-friendly purpose text"""
        
        purpose_texts = {
            ConsentPurpose.TRADING_FEES: "Automatic collection of trading fees for executed trades",
            ConsentPurpose.SUBSCRIPTION_RENEWAL: "Automatic renewal of GridWorks subscription",
            ConsentPurpose.PORTFOLIO_MANAGEMENT: "Portfolio management and rebalancing fees",
            ConsentPurpose.INVESTMENT_ADVISORY: "Investment advisory and coaching fees"
        }
        
        return purpose_texts.get(purpose, "GridWorks automated payments")
    
    def _get_aa_frequency(self, frequency: ConsentFrequency) -> str:
        """Convert internal frequency to AA format"""
        
        frequency_mapping = {
            ConsentFrequency.DAILY: "DAY",
            ConsentFrequency.WEEKLY: "WEEK",
            ConsentFrequency.MONTHLY: "MONTH",
            ConsentFrequency.PER_TRANSACTION: "TRANSACTION"
        }
        
        return frequency_mapping.get(frequency, "DAY")
    
    async def _send_consent_notification(
        self,
        user_id: str,
        phone: str,
        consent_request: ConsentRequest
    ):
        """Send consent approval notification to user"""
        
        # This would integrate with WhatsApp client
        logger.info(f"Consent notification sent to {phone} for consent {consent_request.consent_id}")
    
    async def _store_consent_request(
        self,
        consent_request: ConsentRequest,
        aa_response: Dict[str, Any]
    ):
        """Store consent request in database"""
        
        # Mock implementation - replace with actual database storage
        logger.info(f"Stored consent request: {consent_request.consent_id}")
    
    async def _get_consent_details(self, consent_id: str) -> Optional[ConsentDetails]:
        """Get consent details from database"""
        
        # Mock implementation - replace with actual database query
        return ConsentDetails(
            consent_id=consent_id,
            user_id="mock_user",
            status=ConsentStatus.ACTIVE,
            purpose=ConsentPurpose.TRADING_FEES,
            max_amount=50000,
            frequency=ConsentFrequency.DAILY,
            accounts_linked=[],
            usage_count=0,
            amount_used=0,
            last_used=None,
            expires_at=datetime.now() + timedelta(days=365),
            created_at=datetime.now(),
            updated_at=datetime.now(),
            metadata={"tier": "LITE"}
        )
    
    async def _get_daily_usage(self, consent_id: str) -> int:
        """Get daily usage amount for consent"""
        
        # Mock implementation - replace with actual database query
        return 0
    
    async def _get_monthly_usage(self, consent_id: str) -> int:
        """Get monthly usage amount for consent"""
        
        # Mock implementation - replace with actual database query
        return 0
    
    async def _update_consent_usage(
        self,
        consent_id: str,
        amount: int,
        metadata: Dict[str, Any]
    ):
        """Update consent usage tracking"""
        
        # Mock implementation - replace with actual database update
        logger.info(f"Updated usage for consent {consent_id}: ₹{amount/100}")
    
    async def _log_auto_debit_transaction(
        self,
        consent_id: str,
        amount: int,
        transaction_id: str,
        status: str
    ):
        """Log auto-debit transaction"""
        
        # Mock implementation - replace with actual logging
        logger.info(f"Auto-debit logged: {transaction_id}, ₹{amount/100}, {status}")
    
    async def _get_remaining_limits(self, consent_id: str) -> Dict[str, int]:
        """Get remaining transaction limits"""
        
        # Mock implementation - replace with actual calculation
        return {
            "daily_remaining": 450000,  # ₹4,500
            "monthly_remaining": 4500000  # ₹45,000
        }
    
    async def _update_consent_expiry(self, consent_id: str, new_expiry: datetime):
        """Update consent expiry date"""
        
        # Mock implementation - replace with actual database update
        logger.info(f"Updated consent {consent_id} expiry to {new_expiry}")
    
    async def _update_consent_status(self, consent_id: str, status: ConsentStatus):
        """Update consent status"""
        
        # Mock implementation - replace with actual database update
        logger.info(f"Updated consent {consent_id} status to {status.value}")


# Demo usage
async def demo_auto_debit_consent():
    """Demonstrate auto-debit consent flow"""
    
    print("💳 GridWorks Auto-Debit Consent System Demo")
    print("=" * 60)
    
    consent_manager = AutoDebitConsentManager()
    
    # Test consent initiation
    consent_result = await consent_manager.initiate_consent_request(
        user_id="demo_user_001",
        phone="+919876543210",
        tier=SupportTier.PRO,
        purpose=ConsentPurpose.TRADING_FEES
    )
    
    print("✅ Consent Request Created:")
    print(f"Consent ID: {consent_result.get('consent_id')}")
    print(f"Max Amount: ₹{consent_result.get('max_amount')}")
    print(f"Consent URL: {consent_result.get('consent_url')}")
    
    # Test auto-debit execution
    if consent_result["success"]:
        debit_result = await consent_manager.execute_auto_debit(
            consent_id=consent_result["consent_id"],
            amount=500,  # ₹5 trading fee
            description="Trading fee for RELIANCE trade",
            trade_metadata={
                "symbol": "RELIANCE",
                "quantity": 100,
                "trade_type": "BUY"
            }
        )
        
        print(f"\n💰 Auto-Debit Executed:")
        print(f"Transaction ID: {debit_result.get('transaction_id')}")
        print(f"Amount: ₹{debit_result.get('amount')}")
        print(f"Status: {debit_result.get('success')}")


if __name__ == "__main__":
    asyncio.run(demo_auto_debit_consent())