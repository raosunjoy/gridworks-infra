"""
GridWorks Black - Private Banking API Integration
Ultra-premium banking connectivity for high-value transactions
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from dataclasses import dataclass, field
import json
import uuid
import hmac
import hashlib
import ssl
import aiohttp
from cryptography.fernet import Fernet

from app.black.models import BlackTier
from app.black.butler_payment_system import ButlerPaymentSystem

logger = logging.getLogger(__name__)


class BankingPartner(Enum):
    """Supported private banking partners"""
    HDFC_PRIVATE = "hdfc_private"
    ICICI_PRIVATE = "icici_private"
    KOTAK_PRIVATE = "kotak_private"
    AXIS_PRIVATE = "axis_private"
    SBI_PRIVATE = "sbi_private"
    CITI_PRIVATE = "citi_private"
    STANDARD_CHARTERED = "standard_chartered"
    HSBC_PRIVATE = "hsbc_private"


class TransactionType(Enum):
    """Types of private banking transactions"""
    HIGH_VALUE_PAYMENT = "high_value_payment"
    WIRE_TRANSFER = "wire_transfer"
    FOREIGN_EXCHANGE = "foreign_exchange"
    INVESTMENT_TRANSFER = "investment_transfer"
    LUXURY_PURCHASE = "luxury_purchase"
    EMERGENCY_PAYMENT = "emergency_payment"
    PORTFOLIO_FUNDING = "portfolio_funding"


class TransactionStatus(Enum):
    """Transaction processing status"""
    INITIATED = "initiated"
    PENDING_APPROVAL = "pending_approval"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    UNDER_REVIEW = "under_review"


@dataclass
class BankingCredentials:
    """Secure banking API credentials"""
    bank: BankingPartner
    client_id: str
    encrypted_secret: str
    api_key: str
    certificate_path: str
    private_key_path: str
    api_version: str
    environment: str  # sandbox, production
    expires_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PrivateBankingTransaction:
    """Private banking transaction details"""
    transaction_id: str
    user_id: str
    tier: BlackTier
    bank: BankingPartner
    transaction_type: TransactionType
    amount: int
    currency: str
    from_account: str
    to_account: str
    beneficiary_name: str
    purpose: str
    reference: str
    status: TransactionStatus
    initiated_at: datetime
    estimated_completion: Optional[datetime]
    completed_at: Optional[datetime]
    fees: Dict[str, int] = field(default_factory=dict)
    compliance_checks: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class PrivateBankingIntegration:
    """
    Private Banking API Integration System
    
    Features:
    - Multi-bank connectivity (8 private banks)
    - High-value transaction processing
    - Real-time compliance checking
    - Secure API communication
    - Butler coordination for approvals
    - Emergency payment channels
    - Foreign exchange capabilities
    """
    
    def __init__(self):
        self.butler_system = ButlerPaymentSystem()
        
        # Bank API configurations
        self.bank_configs = {
            BankingPartner.HDFC_PRIVATE: {
                "base_url": "https://api.hdfcbank.com/private",
                "auth_method": "oauth2",
                "supports_realtime": True,
                "max_transaction": 100000000,  # ₹10 Cr
                "processing_time": "2-4 hours",
                "compliance_level": "high"
            },
            BankingPartner.ICICI_PRIVATE: {
                "base_url": "https://corporate.icicibank.com/api/private",
                "auth_method": "certificate",
                "supports_realtime": True,
                "max_transaction": 150000000,  # ₹15 Cr
                "processing_time": "1-3 hours",
                "compliance_level": "high"
            },
            BankingPartner.KOTAK_PRIVATE: {
                "base_url": "https://netbanking.kotak.com/api/private",
                "auth_method": "api_key",
                "supports_realtime": True,
                "max_transaction": 75000000,   # ₹7.5 Cr
                "processing_time": "2-6 hours",
                "compliance_level": "medium"
            },
            BankingPartner.CITI_PRIVATE: {
                "base_url": "https://online.citibank.co.in/api/private",
                "auth_method": "oauth2",
                "supports_realtime": True,
                "max_transaction": 200000000,  # ₹20 Cr
                "processing_time": "30min-2hours",
                "compliance_level": "ultra_high"
            },
            BankingPartner.HSBC_PRIVATE: {
                "base_url": "https://www.hsbc.co.in/api/private",
                "auth_method": "certificate",
                "supports_realtime": True,
                "max_transaction": 250000000,  # ₹25 Cr
                "processing_time": "1-4 hours",
                "compliance_level": "ultra_high"
            }
        }
        
        # Tier-specific banking privileges
        self.tier_privileges = {
            BlackTier.ONYX: {
                "max_daily_limit": 50000000,    # ₹5 Cr
                "priority_processing": False,
                "dedicated_relationship_manager": False,
                "emergency_channel_access": False,
                "forex_privileges": "basic"
            },
            BlackTier.OBSIDIAN: {
                "max_daily_limit": 150000000,   # ₹15 Cr
                "priority_processing": True,
                "dedicated_relationship_manager": True,
                "emergency_channel_access": True,
                "forex_privileges": "premium"
            },
            BlackTier.VOID: {
                "max_daily_limit": 500000000,   # ₹50 Cr
                "priority_processing": True,
                "dedicated_relationship_manager": True,
                "emergency_channel_access": True,
                "forex_privileges": "unlimited"
            }
        }
        
        # Transaction fee structures
        self.fee_structures = {
            TransactionType.HIGH_VALUE_PAYMENT: {
                "base_fee": 50000,  # ₹500
                "percentage": 0.001,  # 0.1%
                "cap": 500000  # ₹5,000 max
            },
            TransactionType.WIRE_TRANSFER: {
                "base_fee": 150000,  # ₹1,500
                "percentage": 0.0015,
                "cap": 1000000  # ₹10,000 max
            },
            TransactionType.FOREIGN_EXCHANGE: {
                "base_fee": 100000,  # ₹1,000
                "percentage": 0.002,
                "spread": 0.25  # 25 paise spread
            }
        }
        
        logger.info("Private Banking Integration initialized")
    
    async def initiate_private_banking_transaction(
        self,
        user_id: str,
        tier: BlackTier,
        transaction_details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Initiate high-value transaction through private banking"""
        
        try:
            logger.info(f"Initiating private banking transaction for {tier.value} user {user_id}")
            
            # Validate transaction eligibility
            eligibility = await self._validate_transaction_eligibility(
                user_id, tier, transaction_details
            )
            
            if not eligibility["eligible"]:
                return {
                    "success": False,
                    "error": eligibility["error"],
                    "requirements": eligibility.get("requirements")
                }
            
            # Select optimal bank
            selected_bank = await self._select_optimal_bank(
                tier, transaction_details
            )
            
            # Calculate fees
            fee_calculation = await self._calculate_transaction_fees(
                transaction_details, selected_bank
            )
            
            # Create transaction record
            transaction = PrivateBankingTransaction(
                transaction_id=f"PVT_{uuid.uuid4().hex[:12].upper()}",
                user_id=user_id,
                tier=tier,
                bank=selected_bank,
                transaction_type=TransactionType(transaction_details["type"]),
                amount=transaction_details["amount"],
                currency=transaction_details.get("currency", "INR"),
                from_account=transaction_details["from_account"],
                to_account=transaction_details["to_account"],
                beneficiary_name=transaction_details["beneficiary_name"],
                purpose=transaction_details["purpose"],
                reference=transaction_details.get("reference", ""),
                status=TransactionStatus.INITIATED,
                initiated_at=datetime.now(),
                estimated_completion=self._calculate_completion_time(selected_bank),
                fees=fee_calculation,
                metadata=transaction_details.get("metadata", {})
            )
            
            # Butler approval if required
            if await self._requires_butler_approval(transaction):
                butler_approval = await self._get_butler_approval(transaction)
                
                if not butler_approval["approved"]:
                    transaction.status = TransactionStatus.PENDING_APPROVAL
                    await self._store_transaction(transaction)
                    
                    return {
                        "success": True,
                        "transaction_id": transaction.transaction_id,
                        "status": "pending_butler_approval",
                        "butler_contact": butler_approval["contact_info"],
                        "estimated_approval_time": "5-15 minutes"
                    }
            
            # Initiate bank API transaction
            bank_response = await self._initiate_bank_transaction(transaction)
            
            if bank_response["success"]:
                transaction.status = TransactionStatus.PROCESSING
                transaction.metadata.update(bank_response["bank_metadata"])
                await self._store_transaction(transaction)
                
                # Start compliance monitoring
                await self._start_compliance_monitoring(transaction)
                
                # Notify relationship manager if applicable
                if self.tier_privileges[tier]["dedicated_relationship_manager"]:
                    await self._notify_relationship_manager(transaction)
                
                return {
                    "success": True,
                    "transaction_id": transaction.transaction_id,
                    "bank": selected_bank.value,
                    "status": "processing",
                    "estimated_completion": transaction.estimated_completion.isoformat(),
                    "fees": {k: v/100 for k, v in fee_calculation.items()},  # Convert to rupees
                    "tracking_reference": bank_response["bank_reference"],
                    "relationship_manager": bank_response.get("rm_contact")
                }
            else:
                transaction.status = TransactionStatus.FAILED
                await self._store_transaction(transaction)
                
                return {
                    "success": False,
                    "transaction_id": transaction.transaction_id,
                    "error": bank_response["error"],
                    "retry_available": bank_response.get("retry_available", False)
                }
                
        except Exception as e:
            logger.error(f"Private banking transaction initiation failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def process_emergency_payment(
        self,
        user_id: str,
        tier: BlackTier,
        emergency_details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process emergency payment through priority channels"""
        
        try:
            if tier not in [BlackTier.OBSIDIAN, BlackTier.VOID]:
                return {
                    "success": False,
                    "error": "Emergency payment channel not available for this tier"
                }
            
            # Validate emergency scenario
            emergency_validation = await self._validate_emergency_scenario(
                user_id, emergency_details
            )
            
            if not emergency_validation["valid"]:
                return {
                    "success": False,
                    "error": emergency_validation["error"]
                }
            
            # Create emergency transaction
            emergency_transaction = PrivateBankingTransaction(
                transaction_id=f"EMG_{uuid.uuid4().hex[:12].upper()}",
                user_id=user_id,
                tier=tier,
                bank=BankingPartner.CITI_PRIVATE,  # Primary emergency bank
                transaction_type=TransactionType.EMERGENCY_PAYMENT,
                amount=emergency_details["amount"],
                currency=emergency_details.get("currency", "INR"),
                from_account=emergency_details["from_account"],
                to_account=emergency_details["to_account"],
                beneficiary_name=emergency_details["beneficiary_name"],
                purpose=f"EMERGENCY: {emergency_details['emergency_type']}",
                reference=emergency_details.get("reference", ""),
                status=TransactionStatus.PROCESSING,
                initiated_at=datetime.now(),
                estimated_completion=datetime.now() + timedelta(minutes=30),
                metadata={
                    "emergency_type": emergency_details["emergency_type"],
                    "priority": "critical",
                    "expedited": True,
                    **emergency_details.get("metadata", {})
                }
            )
            
            # Immediate butler notification
            await self._emergency_butler_notification(emergency_transaction)
            
            # Process through emergency channel
            emergency_response = await self._process_emergency_channel(emergency_transaction)
            
            if emergency_response["success"]:
                emergency_transaction.status = TransactionStatus.COMPLETED
                emergency_transaction.completed_at = datetime.now()
                await self._store_transaction(emergency_transaction)
                
                # Send emergency confirmation
                await self._send_emergency_confirmation(emergency_transaction)
                
                return {
                    "success": True,
                    "transaction_id": emergency_transaction.transaction_id,
                    "status": "completed",
                    "processed_in": "15-30 minutes",
                    "emergency_reference": emergency_response["emergency_ref"],
                    "relationship_manager_notified": True,
                    "compliance_post_review": True
                }
            else:
                return {
                    "success": False,
                    "error": emergency_response["error"],
                    "fallback_options": await self._get_emergency_fallback_options(emergency_transaction)
                }
                
        except Exception as e:
            logger.error(f"Emergency payment processing failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_transaction_status(
        self,
        transaction_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """Get real-time transaction status"""
        
        try:
            # Get transaction from storage
            transaction = await self._get_transaction(transaction_id)
            
            if not transaction or transaction.user_id != user_id:
                return {"success": False, "error": "Transaction not found"}
            
            # Get real-time status from bank if processing
            if transaction.status == TransactionStatus.PROCESSING:
                bank_status = await self._get_bank_transaction_status(transaction)
                
                if bank_status["status_changed"]:
                    transaction.status = TransactionStatus(bank_status["new_status"])
                    if bank_status["new_status"] == "completed":
                        transaction.completed_at = datetime.now()
                    
                    await self._update_transaction(transaction)
            
            # Prepare response
            response = {
                "success": True,
                "transaction_id": transaction_id,
                "status": transaction.status.value,
                "amount": transaction.amount / 100,  # Convert to rupees
                "currency": transaction.currency,
                "bank": transaction.bank.value,
                "initiated_at": transaction.initiated_at.isoformat(),
                "estimated_completion": transaction.estimated_completion.isoformat() if transaction.estimated_completion else None,
                "fees": {k: v/100 for k, v in transaction.fees.items()},
                "compliance_status": "clear"
            }
            
            if transaction.completed_at:
                response["completed_at"] = transaction.completed_at.isoformat()
                response["processing_time"] = str(transaction.completed_at - transaction.initiated_at)
            
            # Add tier-specific information
            if transaction.tier in [BlackTier.OBSIDIAN, BlackTier.VOID]:
                response["relationship_manager"] = await self._get_rm_contact(transaction)
                response["priority_processing"] = True
            
            return response
            
        except Exception as e:
            logger.error(f"Transaction status retrieval failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _validate_transaction_eligibility(
        self,
        user_id: str,
        tier: BlackTier,
        transaction_details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate if user is eligible for private banking transaction"""
        
        try:
            amount = transaction_details["amount"]
            tier_privileges = self.tier_privileges[tier]
            
            # Check daily limit
            daily_usage = await self._get_daily_transaction_usage(user_id)
            if daily_usage + amount > tier_privileges["max_daily_limit"]:
                return {
                    "eligible": False,
                    "error": f"Transaction exceeds daily limit of ₹{tier_privileges['max_daily_limit']/100:,.0f}",
                    "requirements": {
                        "daily_limit": tier_privileges["max_daily_limit"] / 100,
                        "current_usage": daily_usage / 100,
                        "available": (tier_privileges["max_daily_limit"] - daily_usage) / 100
                    }
                }
            
            # Check account verification
            account_verification = await self._verify_user_accounts(
                user_id, transaction_details
            )
            
            if not account_verification["verified"]:
                return {
                    "eligible": False,
                    "error": "Account verification required",
                    "requirements": account_verification["requirements"]
                }
            
            # Check compliance requirements
            compliance_check = await self._check_compliance_requirements(
                user_id, transaction_details
            )
            
            if not compliance_check["compliant"]:
                return {
                    "eligible": False,
                    "error": "Compliance requirements not met",
                    "requirements": compliance_check["requirements"]
                }
            
            return {"eligible": True}
            
        except Exception as e:
            logger.error(f"Eligibility validation error: {e}")
            return {"eligible": False, "error": "Validation failed"}
    
    async def _select_optimal_bank(
        self,
        tier: BlackTier,
        transaction_details: Dict[str, Any]
    ) -> BankingPartner:
        """Select optimal bank based on transaction requirements"""
        
        try:
            amount = transaction_details["amount"]
            transaction_type = TransactionType(transaction_details["type"])
            urgency = transaction_details.get("urgent", False)
            
            # Get available banks for tier
            available_banks = await self._get_available_banks(tier)
            
            # Score banks based on criteria
            bank_scores = {}
            
            for bank in available_banks:
                config = self.bank_configs[bank]
                score = 0
                
                # Amount capacity
                if amount <= config["max_transaction"]:
                    score += 30
                else:
                    continue  # Skip banks that can't handle the amount
                
                # Processing time (for urgent transactions)
                if urgency and config["supports_realtime"]:
                    score += 25
                
                # Compliance level
                if transaction_type in [TransactionType.FOREIGN_EXCHANGE, TransactionType.INVESTMENT_TRANSFER]:
                    if config["compliance_level"] in ["high", "ultra_high"]:
                        score += 20
                
                # Tier-specific preferences
                if tier == BlackTier.VOID:
                    if bank in [BankingPartner.CITI_PRIVATE, BankingPartner.HSBC_PRIVATE]:
                        score += 15  # Premium banks for VOID tier
                
                bank_scores[bank] = score
            
            # Select bank with highest score
            optimal_bank = max(bank_scores.items(), key=lambda x: x[1])[0]
            
            logger.info(f"Selected {optimal_bank.value} for transaction (score: {bank_scores[optimal_bank]})")
            return optimal_bank
            
        except Exception as e:
            logger.error(f"Bank selection error: {e}")
            # Fallback to default premium bank
            return BankingPartner.HDFC_PRIVATE
    
    async def _calculate_transaction_fees(
        self,
        transaction_details: Dict[str, Any],
        bank: BankingPartner
    ) -> Dict[str, int]:
        """Calculate transaction fees"""
        
        try:
            amount = transaction_details["amount"]
            transaction_type = TransactionType(transaction_details["type"])
            
            fee_structure = self.fee_structures.get(transaction_type, {
                "base_fee": 100000,  # ₹1,000 default
                "percentage": 0.002,
                "cap": 1000000  # ₹10,000 max
            })
            
            # Calculate percentage fee
            percentage_fee = int(amount * fee_structure["percentage"])
            
            # Apply cap
            percentage_fee = min(percentage_fee, fee_structure["cap"])
            
            # Add base fee
            total_fee = fee_structure["base_fee"] + percentage_fee
            
            # Bank-specific adjustments
            bank_multiplier = {
                BankingPartner.CITI_PRIVATE: 1.2,      # Premium pricing
                BankingPartner.HSBC_PRIVATE: 1.15,     # Premium pricing
                BankingPartner.HDFC_PRIVATE: 1.0,      # Standard pricing
                BankingPartner.ICICI_PRIVATE: 0.95,    # Competitive pricing
                BankingPartner.KOTAK_PRIVATE: 0.9      # Most competitive
            }.get(bank, 1.0)
            
            total_fee = int(total_fee * bank_multiplier)
            
            return {
                "processing_fee": total_fee,
                "gst": int(total_fee * 0.18),  # 18% GST
                "total": int(total_fee * 1.18)
            }
            
        except Exception as e:
            logger.error(f"Fee calculation error: {e}")
            return {"processing_fee": 100000, "gst": 18000, "total": 118000}
    
    async def _initiate_bank_transaction(
        self,
        transaction: PrivateBankingTransaction
    ) -> Dict[str, Any]:
        """Initiate transaction with selected bank"""
        
        try:
            bank_config = self.bank_configs[transaction.bank]
            
            # Prepare bank API request
            api_request = {
                "transaction_id": transaction.transaction_id,
                "amount": transaction.amount,
                "currency": transaction.currency,
                "from_account": transaction.from_account,
                "to_account": transaction.to_account,
                "beneficiary_name": transaction.beneficiary_name,
                "purpose": transaction.purpose,
                "reference": transaction.reference,
                "priority": "high" if transaction.tier in [BlackTier.OBSIDIAN, BlackTier.VOID] else "normal"
            }
            
            # Mock bank API call
            # In production, this would make actual API calls to banks
            bank_response = await self._mock_bank_api_call(
                transaction.bank, "initiate_transaction", api_request
            )
            
            if bank_response["status"] == "success":
                return {
                    "success": True,
                    "bank_reference": bank_response["bank_reference"],
                    "bank_metadata": bank_response["metadata"],
                    "rm_contact": bank_response.get("relationship_manager")
                }
            else:
                return {
                    "success": False,
                    "error": bank_response["error"],
                    "retry_available": bank_response.get("retry_available", False)
                }
                
        except Exception as e:
            logger.error(f"Bank transaction initiation error: {e}")
            return {"success": False, "error": str(e)}
    
    async def _mock_bank_api_call(
        self,
        bank: BankingPartner,
        operation: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Mock bank API call for demonstration"""
        
        # Simulate API processing delay
        await asyncio.sleep(0.1)
        
        # Mock successful response
        return {
            "status": "success",
            "bank_reference": f"{bank.value.upper()}_{uuid.uuid4().hex[:8].upper()}",
            "metadata": {
                "bank_name": bank.value.replace("_", " ").title(),
                "processing_center": "Mumbai",
                "estimated_completion": "2-4 hours"
            },
            "relationship_manager": {
                "name": "Priya Sharma",
                "email": "priya.sharma@bank.com",
                "phone": "+91-98765-43210",
                "available_24x7": True
            }
        }
    
    async def _requires_butler_approval(
        self,
        transaction: PrivateBankingTransaction
    ) -> bool:
        """Check if transaction requires butler approval"""
        
        # High-value transactions require butler approval
        if transaction.amount > 10000000:  # ₹1 Cr
            return True
        
        # Investment transactions require approval
        if transaction.transaction_type == TransactionType.INVESTMENT_TRANSFER:
            return True
        
        # Emergency payments get expedited approval
        if transaction.transaction_type == TransactionType.EMERGENCY_PAYMENT:
            return False
        
        return False
    
    async def _get_butler_approval(
        self,
        transaction: PrivateBankingTransaction
    ) -> Dict[str, Any]:
        """Get butler approval for high-value transaction"""
        
        try:
            # Use butler payment system for approval
            payment_context = {
                "payment_id": transaction.transaction_id,
                "user_id": transaction.user_id,
                "tier": transaction.tier,
                "amount": transaction.amount,
                "currency": transaction.currency,
                "category": "investment",  # Map to butler category
                "recipient": transaction.beneficiary_name,
                "description": f"Private banking: {transaction.purpose}",
                "risk_factors": ["high_value", "private_banking"],
                "time_sensitive": False,
                "recurring": False
            }
            
            # Mock butler approval (would use actual butler system)
            return {
                "approved": True,
                "butler_id": "premium_butler_001",
                "approval_time": datetime.now(),
                "conditions": ["compliance_verification"],
                "contact_info": {
                    "butler_name": "Arjun Mehta",
                    "phone": "+91-98765-43210"
                }
            }
            
        except Exception as e:
            logger.error(f"Butler approval error: {e}")
            return {"approved": False, "error": str(e)}
    
    def _calculate_completion_time(self, bank: BankingPartner) -> datetime:
        """Calculate estimated completion time"""
        
        config = self.bank_configs[bank]
        processing_time = config["processing_time"]
        
        # Parse processing time and add to current time
        if "min" in processing_time:
            hours = 0.5  # 30 minutes
        elif "hour" in processing_time:
            hours = 3  # Average 3 hours
        else:
            hours = 4  # Default 4 hours
        
        return datetime.now() + timedelta(hours=hours)
    
    async def _store_transaction(self, transaction: PrivateBankingTransaction):
        """Store transaction in secure database"""
        
        # Mock implementation
        logger.info(f"Stored private banking transaction: {transaction.transaction_id}")
    
    async def _get_available_banks(self, tier: BlackTier) -> List[BankingPartner]:
        """Get available banks for tier"""
        
        if tier == BlackTier.VOID:
            return list(BankingPartner)  # All banks available
        elif tier == BlackTier.OBSIDIAN:
            return [
                BankingPartner.HDFC_PRIVATE,
                BankingPartner.ICICI_PRIVATE,
                BankingPartner.CITI_PRIVATE,
                BankingPartner.HSBC_PRIVATE
            ]
        else:  # ONYX
            return [
                BankingPartner.HDFC_PRIVATE,
                BankingPartner.ICICI_PRIVATE,
                BankingPartner.KOTAK_PRIVATE
            ]


# Demo usage
async def demo_private_banking_integration():
    """Demonstrate private banking integration"""
    
    print("🏛️ GridWorks Black - Private Banking Integration Demo")
    print("=" * 60)
    
    banking_integration = PrivateBankingIntegration()
    
    # Test high-value transaction
    transaction_details = {
        "type": "high_value_payment",
        "amount": 5000000,  # ₹50,000
        "from_account": "HDFC_PRIVATE_001",
        "to_account": "BENEFICIARY_ACCOUNT",
        "beneficiary_name": "Luxury Asset Management Ltd",
        "purpose": "Investment portfolio funding",
        "reference": "INV_2024_Q1_001",
        "urgent": False,
        "metadata": {"investment_type": "equity_portfolio"}
    }
    
    transaction_result = await banking_integration.initiate_private_banking_transaction(
        user_id="void_user_001",
        tier=BlackTier.VOID,
        transaction_details=transaction_details
    )
    
    print("💰 Private Banking Transaction:")
    print(f"Success: {transaction_result.get('success')}")
    print(f"Transaction ID: {transaction_result.get('transaction_id')}")
    print(f"Bank: {transaction_result.get('bank')}")
    print(f"Status: {transaction_result.get('status')}")
    print(f"Estimated Completion: {transaction_result.get('estimated_completion')}")
    
    # Test emergency payment
    emergency_details = {
        "amount": 2000000,  # ₹20,000
        "from_account": "CITI_PRIVATE_001",
        "to_account": "EMERGENCY_ACCOUNT",
        "beneficiary_name": "Apollo Hospital",
        "emergency_type": "medical_emergency",
        "reference": "MEDICAL_001"
    }
    
    emergency_result = await banking_integration.process_emergency_payment(
        user_id="obsidian_user_001",
        tier=BlackTier.OBSIDIAN,
        emergency_details=emergency_details
    )
    
    print(f"\n🚨 Emergency Payment:")
    print(f"Success: {emergency_result.get('success')}")
    print(f"Transaction ID: {emergency_result.get('transaction_id')}")
    print(f"Status: {emergency_result.get('status')}")
    print(f"Processed In: {emergency_result.get('processed_in')}")


if __name__ == "__main__":
    asyncio.run(demo_private_banking_integration())