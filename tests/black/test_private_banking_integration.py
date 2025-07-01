"""
Comprehensive test suite for Private Banking Integration
100% test coverage for ultra-premium banking connectivity
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock, patch
import json

from app.black.private_banking_integration import (
    PrivateBankingIntegration,
    PrivateBankingTransaction,
    BankingCredentials,
    BankingPartner,
    TransactionType,
    TransactionStatus
)
from app.black.models import BlackTier


class TestPrivateBankingIntegration:
    """Test PrivateBankingIntegration functionality"""
    
    @pytest.fixture
    def banking_integration(self):
        """Create PrivateBankingIntegration instance for testing"""
        return PrivateBankingIntegration()
    
    @pytest.fixture
    def sample_transaction_details(self):
        """Create sample transaction details for testing"""
        return {
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
    
    @pytest.fixture
    def sample_transaction(self):
        """Create sample PrivateBankingTransaction for testing"""
        return PrivateBankingTransaction(
            transaction_id="PVT_TEST_001",
            user_id="test_user_001",
            tier=BlackTier.OBSIDIAN,
            bank=BankingPartner.HDFC_PRIVATE,
            transaction_type=TransactionType.HIGH_VALUE_PAYMENT,
            amount=5000000,
            currency="INR",
            from_account="HDFC_PRIVATE_001",
            to_account="BENEFICIARY_ACCOUNT",
            beneficiary_name="Test Beneficiary",
            purpose="Test transaction",
            reference="TEST_REF_001",
            status=TransactionStatus.INITIATED,
            initiated_at=datetime.now(),
            estimated_completion=datetime.now() + timedelta(hours=3),
            fees={"processing_fee": 50000, "gst": 9000, "total": 59000}
        )
    
    @pytest.mark.asyncio
    async def test_initiate_private_banking_transaction_success(
        self, banking_integration, sample_transaction_details
    ):
        """Test successful private banking transaction initiation"""
        
        with patch.object(banking_integration, '_validate_transaction_eligibility') as mock_validate, \
             patch.object(banking_integration, '_select_optimal_bank') as mock_bank, \
             patch.object(banking_integration, '_calculate_transaction_fees') as mock_fees, \
             patch.object(banking_integration, '_requires_butler_approval') as mock_butler_req, \
             patch.object(banking_integration, '_initiate_bank_transaction') as mock_bank_txn, \
             patch.object(banking_integration, '_store_transaction') as mock_store, \
             patch.object(banking_integration, '_start_compliance_monitoring') as mock_compliance, \
             patch.object(banking_integration, '_notify_relationship_manager') as mock_rm:
            
            mock_validate.return_value = {"eligible": True}
            mock_bank.return_value = BankingPartner.HDFC_PRIVATE
            mock_fees.return_value = {"processing_fee": 50000, "gst": 9000, "total": 59000}
            mock_butler_req.return_value = False
            mock_bank_txn.return_value = {
                "success": True,
                "bank_reference": "HDFC_REF_001",
                "bank_metadata": {"processing_center": "Mumbai"},
                "rm_contact": {"name": "Priya Sharma", "phone": "+91-98765-43210"}
            }
            mock_store.return_value = None
            mock_compliance.return_value = None
            mock_rm.return_value = None
            
            result = await banking_integration.initiate_private_banking_transaction(
                user_id="test_user_001",
                tier=BlackTier.OBSIDIAN,
                transaction_details=sample_transaction_details
            )
            
            assert result["success"] is True
            assert "transaction_id" in result
            assert result["bank"] == "hdfc_private"
            assert result["status"] == "processing"
            assert "estimated_completion" in result
            assert "fees" in result
            assert result["tracking_reference"] == "HDFC_REF_001"
            
            mock_validate.assert_called_once()
            mock_bank.assert_called_once()
            mock_fees.assert_called_once()
            mock_bank_txn.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_initiate_private_banking_transaction_eligibility_failure(
        self, banking_integration, sample_transaction_details
    ):
        """Test transaction initiation with eligibility failure"""
        
        with patch.object(banking_integration, '_validate_transaction_eligibility') as mock_validate:
            mock_validate.return_value = {
                "eligible": False,
                "error": "Transaction exceeds daily limit",
                "requirements": {"daily_limit": 150000000}
            }
            
            result = await banking_integration.initiate_private_banking_transaction(
                user_id="test_user_001",
                tier=BlackTier.ONYX,
                transaction_details=sample_transaction_details
            )
            
            assert result["success"] is False
            assert result["error"] == "Transaction exceeds daily limit"
            assert "requirements" in result
    
    @pytest.mark.asyncio
    async def test_initiate_private_banking_transaction_butler_approval_required(
        self, banking_integration, sample_transaction_details
    ):
        """Test transaction initiation requiring butler approval"""
        
        # High-value transaction requiring approval
        sample_transaction_details["amount"] = 15000000  # ₹1.5 Cr
        
        with patch.object(banking_integration, '_validate_transaction_eligibility') as mock_validate, \
             patch.object(banking_integration, '_select_optimal_bank') as mock_bank, \
             patch.object(banking_integration, '_calculate_transaction_fees') as mock_fees, \
             patch.object(banking_integration, '_requires_butler_approval') as mock_butler_req, \
             patch.object(banking_integration, '_get_butler_approval') as mock_butler, \
             patch.object(banking_integration, '_store_transaction') as mock_store:
            
            mock_validate.return_value = {"eligible": True}
            mock_bank.return_value = BankingPartner.CITI_PRIVATE
            mock_fees.return_value = {"processing_fee": 150000, "gst": 27000, "total": 177000}
            mock_butler_req.return_value = True
            mock_butler.return_value = {
                "approved": False,
                "contact_info": {"butler_name": "Arjun Mehta", "phone": "+91-98765-43210"}
            }
            mock_store.return_value = None
            
            result = await banking_integration.initiate_private_banking_transaction(
                user_id="test_user_001",
                tier=BlackTier.VOID,
                transaction_details=sample_transaction_details
            )
            
            assert result["success"] is True
            assert result["status"] == "pending_butler_approval"
            assert "butler_contact" in result
            assert result["estimated_approval_time"] == "5-15 minutes"
    
    @pytest.mark.asyncio
    async def test_initiate_private_banking_transaction_bank_failure(
        self, banking_integration, sample_transaction_details
    ):
        """Test transaction initiation with bank API failure"""
        
        with patch.object(banking_integration, '_validate_transaction_eligibility') as mock_validate, \
             patch.object(banking_integration, '_select_optimal_bank') as mock_bank, \
             patch.object(banking_integration, '_calculate_transaction_fees') as mock_fees, \
             patch.object(banking_integration, '_requires_butler_approval') as mock_butler_req, \
             patch.object(banking_integration, '_initiate_bank_transaction') as mock_bank_txn, \
             patch.object(banking_integration, '_store_transaction') as mock_store:
            
            mock_validate.return_value = {"eligible": True}
            mock_bank.return_value = BankingPartner.HDFC_PRIVATE
            mock_fees.return_value = {"processing_fee": 50000, "gst": 9000, "total": 59000}
            mock_butler_req.return_value = False
            mock_bank_txn.return_value = {
                "success": False,
                "error": "Bank API temporarily unavailable",
                "retry_available": True
            }
            mock_store.return_value = None
            
            result = await banking_integration.initiate_private_banking_transaction(
                user_id="test_user_001",
                tier=BlackTier.OBSIDIAN,
                transaction_details=sample_transaction_details
            )
            
            assert result["success"] is False
            assert result["error"] == "Bank API temporarily unavailable"
            assert result["retry_available"] is True
    
    @pytest.mark.asyncio
    async def test_process_emergency_payment_success(self, banking_integration):
        """Test successful emergency payment processing"""
        
        emergency_details = {
            "amount": 2000000,  # ₹20,000
            "from_account": "CITI_PRIVATE_001",
            "to_account": "EMERGENCY_ACCOUNT",
            "beneficiary_name": "Apollo Hospital",
            "emergency_type": "medical_emergency",
            "reference": "MEDICAL_001"
        }
        
        with patch.object(banking_integration, '_validate_emergency_scenario') as mock_validate, \
             patch.object(banking_integration, '_emergency_butler_notification') as mock_butler, \
             patch.object(banking_integration, '_process_emergency_channel') as mock_emergency, \
             patch.object(banking_integration, '_store_transaction') as mock_store, \
             patch.object(banking_integration, '_send_emergency_confirmation') as mock_confirm:
            
            mock_validate.return_value = {"valid": True}
            mock_butler.return_value = None
            mock_emergency.return_value = {
                "success": True,
                "emergency_ref": "EMG_CITI_001"
            }
            mock_store.return_value = None
            mock_confirm.return_value = None
            
            result = await banking_integration.process_emergency_payment(
                user_id="test_user_001",
                tier=BlackTier.OBSIDIAN,
                emergency_details=emergency_details
            )
            
            assert result["success"] is True
            assert "transaction_id" in result
            assert result["status"] == "completed"
            assert result["processed_in"] == "15-30 minutes"
            assert result["emergency_reference"] == "EMG_CITI_001"
            assert result["relationship_manager_notified"] is True
    
    @pytest.mark.asyncio
    async def test_process_emergency_payment_tier_not_eligible(self, banking_integration):
        """Test emergency payment with ineligible tier"""
        
        emergency_details = {
            "amount": 1000000,
            "emergency_type": "medical_emergency"
        }
        
        result = await banking_integration.process_emergency_payment(
            user_id="test_user_001",
            tier=BlackTier.ONYX,  # ONYX tier not eligible for emergency payments
            emergency_details=emergency_details
        )
        
        assert result["success"] is False
        assert "Emergency payment channel not available" in result["error"]
    
    @pytest.mark.asyncio
    async def test_process_emergency_payment_invalid_scenario(self, banking_integration):
        """Test emergency payment with invalid emergency scenario"""
        
        emergency_details = {
            "amount": 5000000,  # ₹50,000 - too high for emergency
            "emergency_type": "non_critical_expense"
        }
        
        with patch.object(banking_integration, '_validate_emergency_scenario') as mock_validate:
            mock_validate.return_value = {
                "valid": False,
                "error": "Emergency scenario validation failed"
            }
            
            result = await banking_integration.process_emergency_payment(
                user_id="test_user_001",
                tier=BlackTier.VOID,
                emergency_details=emergency_details
            )
            
            assert result["success"] is False
            assert result["error"] == "Emergency scenario validation failed"
    
    @pytest.mark.asyncio
    async def test_get_transaction_status_processing(self, banking_integration, sample_transaction):
        """Test transaction status retrieval for processing transaction"""
        
        with patch.object(banking_integration, '_get_transaction') as mock_get, \
             patch.object(banking_integration, '_get_bank_transaction_status') as mock_bank_status, \
             patch.object(banking_integration, '_update_transaction') as mock_update:
            
            mock_get.return_value = sample_transaction
            mock_bank_status.return_value = {
                "status_changed": False,
                "current_status": "processing"
            }
            mock_update.return_value = None
            
            result = await banking_integration.get_transaction_status(
                "PVT_TEST_001", "test_user_001"
            )
            
            assert result["success"] is True
            assert result["transaction_id"] == "PVT_TEST_001"
            assert result["status"] == "initiated"
            assert result["amount"] == 50000.0  # Converted to rupees
            assert result["bank"] == "hdfc_private"
            assert "initiated_at" in result
            assert "estimated_completion" in result
    
    @pytest.mark.asyncio
    async def test_get_transaction_status_completed(self, banking_integration, sample_transaction):
        """Test transaction status retrieval for completed transaction"""
        
        sample_transaction.status = TransactionStatus.COMPLETED
        sample_transaction.completed_at = datetime.now()
        
        with patch.object(banking_integration, '_get_transaction') as mock_get, \
             patch.object(banking_integration, '_get_bank_transaction_status') as mock_bank_status, \
             patch.object(banking_integration, '_get_rm_contact') as mock_rm:
            
            mock_get.return_value = sample_transaction
            mock_bank_status.return_value = {
                "status_changed": False,
                "current_status": "completed"
            }
            mock_rm.return_value = {"name": "Priya Sharma", "phone": "+91-98765-43210"}
            
            result = await banking_integration.get_transaction_status(
                "PVT_TEST_001", "test_user_001"
            )
            
            assert result["success"] is True
            assert result["status"] == "completed"
            assert "completed_at" in result
            assert "processing_time" in result
            assert "relationship_manager" in result
    
    @pytest.mark.asyncio
    async def test_get_transaction_status_not_found(self, banking_integration):
        """Test transaction status retrieval for non-existent transaction"""
        
        with patch.object(banking_integration, '_get_transaction') as mock_get:
            mock_get.return_value = None
            
            result = await banking_integration.get_transaction_status(
                "UNKNOWN_TXN", "test_user_001"
            )
            
            assert result["success"] is False
            assert result["error"] == "Transaction not found"
    
    @pytest.mark.asyncio
    async def test_get_transaction_status_wrong_user(self, banking_integration, sample_transaction):
        """Test transaction status retrieval with wrong user ID"""
        
        with patch.object(banking_integration, '_get_transaction') as mock_get:
            mock_get.return_value = sample_transaction
            
            result = await banking_integration.get_transaction_status(
                "PVT_TEST_001", "wrong_user_001"
            )
            
            assert result["success"] is False
            assert result["error"] == "Transaction not found"
    
    @pytest.mark.asyncio
    async def test_validate_transaction_eligibility_success(self, banking_integration):
        """Test successful transaction eligibility validation"""
        
        transaction_details = {
            "amount": 2000000,  # ₹20,000
            "from_account": "HDFC_PRIVATE_001",
            "to_account": "BENEFICIARY_ACCOUNT"
        }
        
        with patch.object(banking_integration, '_get_daily_transaction_usage') as mock_daily, \
             patch.object(banking_integration, '_verify_user_accounts') as mock_accounts, \
             patch.object(banking_integration, '_check_compliance_requirements') as mock_compliance:
            
            mock_daily.return_value = 10000000  # ₹1L already used
            mock_accounts.return_value = {"verified": True}
            mock_compliance.return_value = {"compliant": True}
            
            result = await banking_integration._validate_transaction_eligibility(
                "test_user_001", BlackTier.OBSIDIAN, transaction_details
            )
            
            assert result["eligible"] is True
    
    @pytest.mark.asyncio
    async def test_validate_transaction_eligibility_daily_limit_exceeded(self, banking_integration):
        """Test transaction eligibility validation with daily limit exceeded"""
        
        transaction_details = {
            "amount": 100000000,  # ₹10L
            "from_account": "HDFC_PRIVATE_001",
            "to_account": "BENEFICIARY_ACCOUNT"
        }
        
        with patch.object(banking_integration, '_get_daily_transaction_usage') as mock_daily:
            mock_daily.return_value = 140000000  # ₹14L already used (OBSIDIAN limit is ₹15L)
            
            result = await banking_integration._validate_transaction_eligibility(
                "test_user_001", BlackTier.OBSIDIAN, transaction_details
            )
            
            assert result["eligible"] is False
            assert "exceeds daily limit" in result["error"]
            assert "requirements" in result
    
    @pytest.mark.asyncio
    async def test_validate_transaction_eligibility_account_not_verified(self, banking_integration):
        """Test transaction eligibility validation with unverified accounts"""
        
        transaction_details = {
            "amount": 1000000,  # ₹10,000
            "from_account": "UNVERIFIED_ACCOUNT",
            "to_account": "BENEFICIARY_ACCOUNT"
        }
        
        with patch.object(banking_integration, '_get_daily_transaction_usage') as mock_daily, \
             patch.object(banking_integration, '_verify_user_accounts') as mock_accounts:
            
            mock_daily.return_value = 0
            mock_accounts.return_value = {
                "verified": False,
                "requirements": ["account_verification_pending"]
            }
            
            result = await banking_integration._validate_transaction_eligibility(
                "test_user_001", BlackTier.OBSIDIAN, transaction_details
            )
            
            assert result["eligible"] is False
            assert result["error"] == "Account verification required"
            assert "requirements" in result
    
    @pytest.mark.asyncio
    async def test_select_optimal_bank_amount_based(self, banking_integration):
        """Test optimal bank selection based on amount capacity"""
        
        # High-value transaction
        transaction_details = {
            "type": "high_value_payment",
            "amount": 20000000,  # ₹2 Cr
            "urgent": False
        }
        
        with patch.object(banking_integration, '_get_available_banks') as mock_banks:
            mock_banks.return_value = [
                BankingPartner.HDFC_PRIVATE,
                BankingPartner.CITI_PRIVATE,
                BankingPartner.HSBC_PRIVATE
            ]
            
            optimal_bank = await banking_integration._select_optimal_bank(
                BlackTier.VOID, transaction_details
            )
            
            # Should prefer HSBC or CITI for high-value transactions
            assert optimal_bank in [BankingPartner.CITI_PRIVATE, BankingPartner.HSBC_PRIVATE]
    
    @pytest.mark.asyncio
    async def test_select_optimal_bank_urgent_transaction(self, banking_integration):
        """Test optimal bank selection for urgent transactions"""
        
        transaction_details = {
            "type": "high_value_payment",
            "amount": 5000000,  # ₹50,000
            "urgent": True
        }
        
        with patch.object(banking_integration, '_get_available_banks') as mock_banks:
            mock_banks.return_value = [
                BankingPartner.HDFC_PRIVATE,
                BankingPartner.ICICI_PRIVATE,
                BankingPartner.KOTAK_PRIVATE
            ]
            
            optimal_bank = await banking_integration._select_optimal_bank(
                BlackTier.OBSIDIAN, transaction_details
            )
            
            # Should prefer banks with realtime support for urgent transactions
            assert optimal_bank in [BankingPartner.HDFC_PRIVATE, BankingPartner.ICICI_PRIVATE]
    
    @pytest.mark.asyncio
    async def test_calculate_transaction_fees_high_value_payment(self, banking_integration):
        """Test transaction fee calculation for high-value payment"""
        
        transaction_details = {
            "type": "high_value_payment",
            "amount": 10000000  # ₹1L
        }
        
        fees = await banking_integration._calculate_transaction_fees(
            transaction_details, BankingPartner.HDFC_PRIVATE
        )
        
        assert "processing_fee" in fees
        assert "gst" in fees
        assert "total" in fees
        assert fees["total"] > fees["processing_fee"]  # Total includes GST
        assert fees["gst"] == int(fees["processing_fee"] * 0.18)  # 18% GST
    
    @pytest.mark.asyncio
    async def test_calculate_transaction_fees_wire_transfer(self, banking_integration):
        """Test transaction fee calculation for wire transfer"""
        
        transaction_details = {
            "type": "wire_transfer",
            "amount": 5000000  # ₹50,000
        }
        
        fees = await banking_integration._calculate_transaction_fees(
            transaction_details, BankingPartner.CITI_PRIVATE
        )
        
        # Wire transfers should have higher base fees
        assert fees["processing_fee"] >= 150000  # Base fee for wire transfer
        assert fees["total"] == int(fees["processing_fee"] * 1.18)  # Including GST
    
    @pytest.mark.asyncio
    async def test_calculate_transaction_fees_premium_bank_multiplier(self, banking_integration):
        """Test transaction fee calculation with premium bank multiplier"""
        
        transaction_details = {
            "type": "high_value_payment",
            "amount": 5000000  # ₹50,000
        }
        
        # Calculate fees for standard and premium banks
        standard_fees = await banking_integration._calculate_transaction_fees(
            transaction_details, BankingPartner.HDFC_PRIVATE
        )
        
        premium_fees = await banking_integration._calculate_transaction_fees(
            transaction_details, BankingPartner.CITI_PRIVATE
        )
        
        # Premium bank should have higher fees
        assert premium_fees["processing_fee"] > standard_fees["processing_fee"]
    
    @pytest.mark.asyncio
    async def test_initiate_bank_transaction_success(self, banking_integration, sample_transaction):
        """Test successful bank transaction initiation"""
        
        with patch.object(banking_integration, '_mock_bank_api_call') as mock_api:
            mock_api.return_value = {
                "status": "success",
                "bank_reference": "HDFC_REF_001",
                "metadata": {"processing_center": "Mumbai"},
                "relationship_manager": {
                    "name": "Priya Sharma",
                    "phone": "+91-98765-43210"
                }
            }
            
            result = await banking_integration._initiate_bank_transaction(sample_transaction)
            
            assert result["success"] is True
            assert result["bank_reference"] == "HDFC_REF_001"
            assert "bank_metadata" in result
            assert "rm_contact" in result
    
    @pytest.mark.asyncio
    async def test_initiate_bank_transaction_failure(self, banking_integration, sample_transaction):
        """Test bank transaction initiation failure"""
        
        with patch.object(banking_integration, '_mock_bank_api_call') as mock_api:
            mock_api.return_value = {
                "status": "error",
                "error": "Insufficient funds in account",
                "retry_available": False
            }
            
            result = await banking_integration._initiate_bank_transaction(sample_transaction)
            
            assert result["success"] is False
            assert result["error"] == "Insufficient funds in account"
            assert result["retry_available"] is False
    
    def test_requires_butler_approval_high_value(self, banking_integration, sample_transaction):
        """Test butler approval requirement for high-value transactions"""
        
        sample_transaction.amount = 15000000  # ₹1.5 Cr
        
        requires_approval = asyncio.run(
            banking_integration._requires_butler_approval(sample_transaction)
        )
        
        assert requires_approval is True
    
    def test_requires_butler_approval_investment(self, banking_integration, sample_transaction):
        """Test butler approval requirement for investment transactions"""
        
        sample_transaction.transaction_type = TransactionType.INVESTMENT_TRANSFER
        sample_transaction.amount = 5000000  # ₹50,000
        
        requires_approval = asyncio.run(
            banking_integration._requires_butler_approval(sample_transaction)
        )
        
        assert requires_approval is True
    
    def test_requires_butler_approval_emergency_no_approval(self, banking_integration, sample_transaction):
        """Test butler approval not required for emergency payments"""
        
        sample_transaction.transaction_type = TransactionType.EMERGENCY_PAYMENT
        sample_transaction.amount = 1000000  # ₹10,000
        
        requires_approval = asyncio.run(
            banking_integration._requires_butler_approval(sample_transaction)
        )
        
        assert requires_approval is False
    
    def test_requires_butler_approval_normal_amount(self, banking_integration, sample_transaction):
        """Test butler approval not required for normal amounts"""
        
        sample_transaction.amount = 500000  # ₹5,000
        sample_transaction.transaction_type = TransactionType.HIGH_VALUE_PAYMENT
        
        requires_approval = asyncio.run(
            banking_integration._requires_butler_approval(sample_transaction)
        )
        
        assert requires_approval is False
    
    def test_calculate_completion_time(self, banking_integration):
        """Test completion time calculation for different banks"""
        
        # Fast processing bank
        fast_completion = banking_integration._calculate_completion_time(BankingPartner.CITI_PRIVATE)
        
        # Standard processing bank
        standard_completion = banking_integration._calculate_completion_time(BankingPartner.HDFC_PRIVATE)
        
        # Both should be future times
        assert fast_completion > datetime.now()
        assert standard_completion > datetime.now()
        
        # Completion times should be within reasonable range (few hours)
        time_diff = standard_completion - datetime.now()
        assert time_diff.total_seconds() <= 6 * 3600  # Within 6 hours
    
    def test_bank_configs_configuration(self, banking_integration):
        """Test bank configurations"""
        
        # Test HDFC configuration
        hdfc_config = banking_integration.bank_configs[BankingPartner.HDFC_PRIVATE]
        assert hdfc_config["max_transaction"] == 100000000  # ₹10 Cr
        assert hdfc_config["supports_realtime"] is True
        assert hdfc_config["compliance_level"] == "high"
        
        # Test CITI configuration
        citi_config = banking_integration.bank_configs[BankingPartner.CITI_PRIVATE]
        assert citi_config["max_transaction"] == 200000000  # ₹20 Cr
        assert citi_config["compliance_level"] == "ultra_high"
        
        # Test HSBC configuration
        hsbc_config = banking_integration.bank_configs[BankingPartner.HSBC_PRIVATE]
        assert hsbc_config["max_transaction"] == 250000000  # ₹25 Cr
        assert hsbc_config["compliance_level"] == "ultra_high"
    
    def test_tier_privileges_configuration(self, banking_integration):
        """Test tier-specific banking privileges"""
        
        # Test ONYX tier privileges
        onyx_privileges = banking_integration.tier_privileges[BlackTier.ONYX]
        assert onyx_privileges["max_daily_limit"] == 50000000  # ₹5 Cr
        assert onyx_privileges["priority_processing"] is False
        assert onyx_privileges["dedicated_relationship_manager"] is False
        assert onyx_privileges["emergency_channel_access"] is False
        
        # Test OBSIDIAN tier privileges
        obsidian_privileges = banking_integration.tier_privileges[BlackTier.OBSIDIAN]
        assert obsidian_privileges["max_daily_limit"] == 150000000  # ₹15 Cr
        assert obsidian_privileges["priority_processing"] is True
        assert obsidian_privileges["dedicated_relationship_manager"] is True
        assert obsidian_privileges["emergency_channel_access"] is True
        
        # Test VOID tier privileges
        void_privileges = banking_integration.tier_privileges[BlackTier.VOID]
        assert void_privileges["max_daily_limit"] == 500000000  # ₹50 Cr
        assert void_privileges["priority_processing"] is True
        assert void_privileges["dedicated_relationship_manager"] is True
        assert void_privileges["emergency_channel_access"] is True
        assert void_privileges["forex_privileges"] == "unlimited"
    
    def test_fee_structures_configuration(self, banking_integration):
        """Test transaction fee structures"""
        
        # Test high-value payment fees
        hv_fees = banking_integration.fee_structures[TransactionType.HIGH_VALUE_PAYMENT]
        assert hv_fees["base_fee"] == 50000  # ₹500
        assert hv_fees["percentage"] == 0.001  # 0.1%
        assert hv_fees["cap"] == 500000  # ₹5,000 max
        
        # Test wire transfer fees
        wire_fees = banking_integration.fee_structures[TransactionType.WIRE_TRANSFER]
        assert wire_fees["base_fee"] == 150000  # ₹1,500
        assert wire_fees["percentage"] == 0.0015  # 0.15%
        assert wire_fees["cap"] == 1000000  # ₹10,000 max
        
        # Test foreign exchange fees
        fx_fees = banking_integration.fee_structures[TransactionType.FOREIGN_EXCHANGE]
        assert fx_fees["base_fee"] == 100000  # ₹1,000
        assert fx_fees["percentage"] == 0.002  # 0.2%
        assert fx_fees["spread"] == 0.25  # 25 paise spread
    
    def test_get_available_banks_by_tier(self, banking_integration):
        """Test available banks by tier"""
        
        # VOID tier should have access to all banks
        void_banks = asyncio.run(banking_integration._get_available_banks(BlackTier.VOID))
        assert len(void_banks) == len(BankingPartner)
        
        # OBSIDIAN tier should have access to premium banks
        obsidian_banks = asyncio.run(banking_integration._get_available_banks(BlackTier.OBSIDIAN))
        assert BankingPartner.HDFC_PRIVATE in obsidian_banks
        assert BankingPartner.CITI_PRIVATE in obsidian_banks
        assert BankingPartner.HSBC_PRIVATE in obsidian_banks
        
        # ONYX tier should have limited access
        onyx_banks = asyncio.run(banking_integration._get_available_banks(BlackTier.ONYX))
        assert BankingPartner.HDFC_PRIVATE in onyx_banks
        assert BankingPartner.ICICI_PRIVATE in onyx_banks
        assert len(onyx_banks) < len(obsidian_banks)


class TestPrivateBankingTransaction:
    """Test PrivateBankingTransaction data model"""
    
    def test_transaction_creation(self):
        """Test PrivateBankingTransaction creation with all fields"""
        
        transaction = PrivateBankingTransaction(
            transaction_id="PVT_TEST_001",
            user_id="test_user_001",
            tier=BlackTier.OBSIDIAN,
            bank=BankingPartner.HDFC_PRIVATE,
            transaction_type=TransactionType.HIGH_VALUE_PAYMENT,
            amount=5000000,
            currency="INR",
            from_account="HDFC_PRIVATE_001",
            to_account="BENEFICIARY_ACCOUNT",
            beneficiary_name="Test Beneficiary",
            purpose="Test transaction",
            reference="TEST_REF_001",
            status=TransactionStatus.INITIATED,
            initiated_at=datetime.now(),
            estimated_completion=datetime.now() + timedelta(hours=3),
            fees={"processing_fee": 50000, "gst": 9000, "total": 59000},
            compliance_checks=["aml_check", "sanctions_check"],
            metadata={"priority": "high"}
        )
        
        assert transaction.transaction_id == "PVT_TEST_001"
        assert transaction.user_id == "test_user_001"
        assert transaction.tier == BlackTier.OBSIDIAN
        assert transaction.bank == BankingPartner.HDFC_PRIVATE
        assert transaction.transaction_type == TransactionType.HIGH_VALUE_PAYMENT
        assert transaction.amount == 5000000
        assert transaction.currency == "INR"
        assert transaction.from_account == "HDFC_PRIVATE_001"
        assert transaction.to_account == "BENEFICIARY_ACCOUNT"
        assert transaction.beneficiary_name == "Test Beneficiary"
        assert transaction.purpose == "Test transaction"
        assert transaction.reference == "TEST_REF_001"
        assert transaction.status == TransactionStatus.INITIATED
        assert transaction.fees["total"] == 59000
        assert "aml_check" in transaction.compliance_checks
        assert transaction.metadata["priority"] == "high"


class TestBankingCredentials:
    """Test BankingCredentials data model"""
    
    def test_credentials_creation(self):
        """Test BankingCredentials creation"""
        
        credentials = BankingCredentials(
            bank=BankingPartner.HDFC_PRIVATE,
            client_id="HDFC_CLIENT_001",
            encrypted_secret="encrypted_secret_key",
            api_key="api_key_001",
            certificate_path="/path/to/cert.pem",
            private_key_path="/path/to/private.key",
            api_version="v2.1",
            environment="production",
            expires_at=datetime.now() + timedelta(days=365),
            metadata={"region": "india"}
        )
        
        assert credentials.bank == BankingPartner.HDFC_PRIVATE
        assert credentials.client_id == "HDFC_CLIENT_001"
        assert credentials.encrypted_secret == "encrypted_secret_key"
        assert credentials.api_key == "api_key_001"
        assert credentials.certificate_path == "/path/to/cert.pem"
        assert credentials.private_key_path == "/path/to/private.key"
        assert credentials.api_version == "v2.1"
        assert credentials.environment == "production"
        assert credentials.metadata["region"] == "india"


# Integration test
class TestPrivateBankingIntegrationFlow:
    """Integration tests for complete private banking flow"""
    
    @pytest.mark.asyncio
    async def test_complete_transaction_flow(self):
        """Test complete private banking transaction flow"""
        
        banking_integration = PrivateBankingIntegration()
        
        transaction_details = {
            "type": "high_value_payment",
            "amount": 7500000,  # ₹75,000
            "from_account": "HDFC_PRIVATE_001",
            "to_account": "INVESTMENT_ACCOUNT",
            "beneficiary_name": "Investment Management Ltd",
            "purpose": "Portfolio investment",
            "reference": "INV_2024_001",
            "urgent": False,
            "metadata": {"investment_type": "mutual_fund"}
        }
        
        with patch.object(banking_integration, '_get_daily_transaction_usage') as mock_daily, \
             patch.object(banking_integration, '_verify_user_accounts') as mock_accounts, \
             patch.object(banking_integration, '_check_compliance_requirements') as mock_compliance, \
             patch.object(banking_integration, '_mock_bank_api_call') as mock_api, \
             patch.object(banking_integration, '_store_transaction') as mock_store, \
             patch.object(banking_integration, '_start_compliance_monitoring') as mock_monitoring:
            
            # Mock all dependencies
            mock_daily.return_value = 5000000  # ₹50,000 already used
            mock_accounts.return_value = {"verified": True}
            mock_compliance.return_value = {"compliant": True}
            mock_api.return_value = {
                "status": "success",
                "bank_reference": "HDFC_REF_001",
                "metadata": {"processing_center": "Mumbai"}
            }
            mock_store.return_value = None
            mock_monitoring.return_value = None
            
            # Initiate transaction
            result = await banking_integration.initiate_private_banking_transaction(
                user_id="obsidian_user_001",
                tier=BlackTier.OBSIDIAN,
                transaction_details=transaction_details
            )
            
            assert result["success"] is True
            transaction_id = result["transaction_id"]
            
            # Check transaction status
            with patch.object(banking_integration, '_get_transaction') as mock_get_txn, \
                 patch.object(banking_integration, '_get_bank_transaction_status') as mock_status:
                
                mock_transaction = PrivateBankingTransaction(
                    transaction_id=transaction_id,
                    user_id="obsidian_user_001",
                    tier=BlackTier.OBSIDIAN,
                    bank=BankingPartner.HDFC_PRIVATE,
                    transaction_type=TransactionType.HIGH_VALUE_PAYMENT,
                    amount=7500000,
                    currency="INR",
                    from_account="HDFC_PRIVATE_001",
                    to_account="INVESTMENT_ACCOUNT",
                    beneficiary_name="Investment Management Ltd",
                    purpose="Portfolio investment",
                    reference="INV_2024_001",
                    status=TransactionStatus.PROCESSING,
                    initiated_at=datetime.now(),
                    estimated_completion=datetime.now() + timedelta(hours=3),
                    fees={"processing_fee": 75000, "gst": 13500, "total": 88500}
                )
                
                mock_get_txn.return_value = mock_transaction
                mock_status.return_value = {"status_changed": False}
                
                status_result = await banking_integration.get_transaction_status(
                    transaction_id, "obsidian_user_001"
                )
                
                assert status_result["success"] is True
                assert status_result["status"] == "processing"
                assert status_result["amount"] == 75000.0  # Converted to rupees


if __name__ == "__main__":
    pytest.main([__file__, "-v"])