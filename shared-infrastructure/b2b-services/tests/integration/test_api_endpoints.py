"""
GridWorks B2B Services - API Integration Tests
Comprehensive test coverage for all API endpoints
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient
from datetime import datetime, timedelta
import json
from unittest.mock import patch, AsyncMock

from ...main import app
from ...database.models import EnterpriseClient, User, APIKey
from ...config import settings


class TestPartnersAPI:
    """Integration tests for Partners API endpoints."""
    
    async def test_client_registration_flow(self, test_client: AsyncClient, test_db_session):
        """Test complete client registration flow."""
        registration_data = {
            "company_name": "Test Financial Corp",
            "legal_entity_name": "Test Financial Corporation Ltd",
            "registration_number": "TFC123456789",
            "tax_id": "TAX987654321",
            "primary_contact_name": "John Smith",
            "primary_contact_email": "john.smith@testfinancial.com",
            "primary_contact_phone": "+1234567890",
            "address_line1": "123 Financial Street",
            "city": "Mumbai",
            "state": "Maharashtra",
            "country": "India",
            "postal_code": "400001",
            "tier": "enterprise",
            "requested_services": ["ai_suite", "trading_infrastructure"]
        }
        
        response = await test_client.post("/api/v1/partners/register", json=registration_data)
        
        assert response.status_code == 201
        response_data = response.json()
        
        # Verify registration response
        assert "client_id" in response_data
        assert "access_token" in response_data
        assert "refresh_token" in response_data
        assert response_data["tier"] == "enterprise"
        assert response_data["status"] == "pending_verification"
        
        # Verify trial subscription was created
        assert "trial_subscription" in response_data
        assert response_data["trial_subscription"]["status"] == "active"
        assert response_data["trial_subscription"]["trial_days_remaining"] > 0
        
        # Verify client can access profile with token
        headers = {"Authorization": f"Bearer {response_data['access_token']}"}
        profile_response = await test_client.get("/api/v1/partners/profile", headers=headers)
        
        assert profile_response.status_code == 200
        profile_data = profile_response.json()
        assert profile_data["company_name"] == registration_data["company_name"]
        assert profile_data["tier"] == "enterprise"
    
    async def test_service_activation_flow(self, test_client: AsyncClient, override_auth_dependencies):
        """Test service activation and configuration."""
        # First get available services
        response = await test_client.get("/api/v1/partners/services/available")
        assert response.status_code == 200
        
        available_services = response.json()
        assert len(available_services["services"]) > 0
        
        # Find AI Suite service
        ai_suite_service = next(
            (s for s in available_services["services"] if s["service_type"] == "ai_suite"),
            None
        )
        assert ai_suite_service is not None
        
        # Activate AI Suite service
        activation_data = {
            "service_id": ai_suite_service["id"],
            "configuration": {
                "languages": ["en", "hi", "ta"],
                "response_time_tier": "premium",
                "audio_enabled": True,
                "whatsapp_integration": True
            },
            "tier": "enterprise"
        }
        
        activation_response = await test_client.post(
            "/api/v1/partners/services/activate",
            json=activation_data
        )
        
        assert activation_response.status_code == 200
        activation_result = activation_response.json()
        
        assert activation_result["status"] == "activated"
        assert activation_result["service_type"] == "ai_suite"
        assert "configuration" in activation_result
        assert "api_endpoints" in activation_result
        assert len(activation_result["api_endpoints"]) > 0
    
    async def test_api_key_management(self, test_client: AsyncClient, override_auth_dependencies):
        """Test API key creation, listing, and revocation."""
        # Create API key
        api_key_data = {
            "name": "Production API Key",
            "permissions": ["ai_suite.*", "trading.read"],
            "rate_limit": 10000,
            "expires_in_days": 90,
            "ip_allowlist": ["192.168.1.0/24", "10.0.0.0/8"]
        }
        
        create_response = await test_client.post(
            "/api/v1/partners/api-keys",
            json=api_key_data
        )
        
        assert create_response.status_code == 201
        created_key = create_response.json()
        
        assert "api_key" in created_key
        assert created_key["api_key"].startswith(settings.API_KEY_PREFIX)
        assert created_key["name"] == api_key_data["name"]
        assert created_key["permissions"] == api_key_data["permissions"]
        assert created_key["rate_limit"] == api_key_data["rate_limit"]
        assert "expires_at" in created_key
        
        # List API keys
        list_response = await test_client.get("/api/v1/partners/api-keys")
        assert list_response.status_code == 200
        
        api_keys = list_response.json()
        assert len(api_keys["api_keys"]) >= 1
        
        # Find our created key
        our_key = next(
            (k for k in api_keys["api_keys"] if k["name"] == api_key_data["name"]),
            None
        )
        assert our_key is not None
        assert our_key["is_active"] is True
        
        # Revoke API key
        key_id = our_key["id"]
        revoke_response = await test_client.delete(f"/api/v1/partners/api-keys/{key_id}")
        assert revoke_response.status_code == 200
        
        revoke_result = revoke_response.json()
        assert revoke_result["status"] == "revoked"
        
        # Verify key is deactivated
        list_response_after = await test_client.get("/api/v1/partners/api-keys")
        updated_keys = list_response_after.json()
        
        revoked_key = next(
            (k for k in updated_keys["api_keys"] if k["id"] == key_id),
            None
        )
        assert revoked_key["is_active"] is False
    
    async def test_usage_reporting_and_analytics(self, test_client: AsyncClient, override_auth_dependencies):
        """Test usage reporting and analytics generation."""
        # Generate usage report
        report_request = {
            "service_types": ["ai_suite", "trading_infrastructure"],
            "start_date": (datetime.utcnow() - timedelta(days=30)).isoformat(),
            "end_date": datetime.utcnow().isoformat(),
            "granularity": "daily",
            "include_costs": True
        }
        
        report_response = await test_client.post(
            "/api/v1/partners/usage/report",
            json=report_request
        )
        
        assert report_response.status_code == 200
        report_data = report_response.json()
        
        assert "report_id" in report_data
        assert "usage_summary" in report_data
        assert "cost_breakdown" in report_data
        assert "service_metrics" in report_data
        
        # Verify usage summary structure
        usage_summary = report_data["usage_summary"]
        assert "total_requests" in usage_summary
        assert "total_cost" in usage_summary
        assert "average_response_time" in usage_summary
        
        # Verify service metrics
        service_metrics = report_data["service_metrics"]
        assert isinstance(service_metrics, list)
        
        for metric in service_metrics:
            assert "service_type" in metric
            assert "requests_count" in metric
            assert "success_rate" in metric
            assert "cost" in metric
    
    async def test_billing_and_invoices(self, test_client: AsyncClient, override_auth_dependencies):
        """Test billing information and invoice retrieval."""
        # Get billing invoices
        invoices_response = await test_client.get("/api/v1/partners/billing/invoices")
        assert invoices_response.status_code == 200
        
        invoices_data = invoices_response.json()
        assert "invoices" in invoices_data
        assert "pagination" in invoices_data
        assert "billing_summary" in invoices_data
        
        # Verify billing summary
        billing_summary = invoices_data["billing_summary"]
        assert "current_month_cost" in billing_summary
        assert "previous_month_cost" in billing_summary
        assert "outstanding_amount" in billing_summary
        assert "next_billing_date" in billing_summary
        
        # Test invoice filtering
        filtered_response = await test_client.get(
            "/api/v1/partners/billing/invoices",
            params={
                "status": "paid",
                "start_date": (datetime.utcnow() - timedelta(days=90)).isoformat(),
                "limit": 10
            }
        )
        
        assert filtered_response.status_code == 200
        filtered_data = filtered_response.json()
        
        # Verify all returned invoices match filter
        for invoice in filtered_data["invoices"]:
            assert invoice["status"] == "paid"


class TestAIServicesAPI:
    """Integration tests for AI Services API endpoints."""
    
    async def test_ai_support_request_flow(self, test_client: AsyncClient, override_service_dependencies):
        """Test complete AI support request flow."""
        support_request = {
            "user_message": "What is the difference between NSE and BSE?",
            "language": "en",
            "user_context": {
                "user_id": "test_user_123",
                "session_id": "session_456",
                "preferences": {
                    "complexity": "intermediate",
                    "format": "detailed"
                }
            },
            "conversation_history": [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hello! How can I help you with your financial questions today?"}
            ],
            "channel": "api",
            "audio_format": "mp3"
        }
        
        response = await test_client.post(
            "/api/v1/ai-services/support/query",
            json=support_request
        )
        
        assert response.status_code == 200
        response_data = response.json()
        
        # Verify AI support response structure
        assert "request_id" in response_data
        assert "response_text" in response_data
        assert "language" in response_data
        assert "confidence_score" in response_data
        assert "response_time_ms" in response_data
        assert "model_used" in response_data
        assert "follow_up_suggestions" in response_data
        
        # Verify response quality
        assert response_data["language"] == "en"
        assert response_data["confidence_score"] >= 0.8
        assert response_data["response_time_ms"] <= 5000  # 5 seconds max
        assert len(response_data["follow_up_suggestions"]) >= 2
        
        # Verify audio response if requested
        if support_request["audio_format"]:
            assert "response_audio" in response_data
    
    async def test_multi_language_support(self, test_client: AsyncClient, override_service_dependencies):
        """Test AI support in multiple Indian languages."""
        languages = ["hi", "ta", "te", "mr", "gu"]
        
        for lang in languages:
            support_request = {
                "user_message": "What is mutual fund?",
                "language": lang,
                "user_context": {"user_id": f"test_user_{lang}"},
                "conversation_history": [],
                "channel": "api"
            }
            
            response = await test_client.post(
                "/api/v1/ai-services/support/query",
                json=support_request
            )
            
            assert response.status_code == 200
            response_data = response.json()
            
            assert response_data["language"] == lang
            assert response_data["confidence_score"] >= 0.8
            assert len(response_data["response_text"]) > 0
    
    async def test_ai_intelligence_morning_pulse(self, test_client: AsyncClient, override_service_dependencies):
        """Test AI intelligence morning pulse generation."""
        intelligence_request = {
            "intelligence_type": "morning_pulse",
            "market_region": "india",
            "user_context": {
                "user_id": "trader_123",
                "client_tier": "enterprise"
            },
            "custom_parameters": {
                "focus_sectors": ["banking", "it", "pharma"],
                "include_global_cues": True,
                "delivery_format": "detailed"
            }
        }
        
        response = await test_client.post(
            "/api/v1/ai-services/intelligence/analyze",
            json=intelligence_request
        )
        
        assert response.status_code == 200
        response_data = response.json()
        
        # Verify intelligence response structure
        assert "intelligence_type" in response_data
        assert "market_region" in response_data
        assert "summary" in response_data
        assert "key_insights" in response_data
        assert "data_points" in response_data
        assert "confidence_score" in response_data
        assert "risk_level" in response_data
        assert "actionable_recommendations" in response_data
        assert "timestamp" in response_data
        
        # Verify quality requirements
        assert response_data["intelligence_type"] == "morning_pulse"
        assert response_data["market_region"] == "india"
        assert response_data["confidence_score"] >= 0.85
        assert len(response_data["key_insights"]) >= 3
        assert len(response_data["actionable_recommendations"]) >= 2
        assert response_data["risk_level"] in ["low", "moderate", "high"]
    
    async def test_ai_moderation_spam_detection(self, test_client: AsyncClient, override_service_dependencies):
        """Test AI moderation and spam detection."""
        # Test spam content
        spam_content = {
            "content": "🚀🚀 GUARANTEED 500% RETURNS! Join our premium group for ₹999 only! WhatsApp: +91XXXXXXXXX 💰💰",
            "content_type": "text",
            "user_context": {
                "user_id": "suspicious_user",
                "user_reputation": "low"
            },
            "channel": "whatsapp",
            "metadata": {
                "message_type": "broadcast",
                "urgency_markers": True
            }
        }
        
        spam_response = await test_client.post(
            "/api/v1/ai-services/moderation/check",
            json=spam_content
        )
        
        assert spam_response.status_code == 200
        spam_data = spam_response.json()
        
        # Verify spam detection
        assert spam_data["action"] == "block"
        assert spam_data["confidence_score"] >= 0.95
        assert len(spam_data["spam_categories"]) > 0
        assert spam_data["risk_level"] == "high"
        assert spam_data["escalation_required"] is True
        
        # Test legitimate content
        legitimate_content = {
            "content": "NIFTY 50 closed at 21,450 today, showing a gain of 0.8% from yesterday. Banking sector led the rally.",
            "content_type": "text",
            "user_context": {
                "user_id": "verified_analyst",
                "user_reputation": "high",
                "expert_verified": True
            },
            "channel": "telegram",
            "metadata": {
                "analysis_type": "market_update"
            }
        }
        
        legitimate_response = await test_client.post(
            "/api/v1/ai-services/moderation/check",
            json=legitimate_content
        )
        
        assert legitimate_response.status_code == 200
        legitimate_data = legitimate_response.json()
        
        # Verify legitimate content approval
        assert legitimate_data["action"] == "allow"
        assert legitimate_data["confidence_score"] >= 0.90
        assert len(legitimate_data["spam_categories"]) == 0
        assert legitimate_data["risk_level"] == "low"
        assert legitimate_data["escalation_required"] is False


class TestAnonymousServicesAPI:
    """Integration tests for Anonymous Services API endpoints."""
    
    async def test_zk_proof_generation_flow(self, test_client: AsyncClient, override_service_dependencies):
        """Test complete ZK proof generation flow."""
        zk_proof_request = {
            "portfolio_data": {
                "holdings": [
                    {"symbol": "RELIANCE", "quantity": 100, "value": 2500000},
                    {"symbol": "TCS", "quantity": 50, "value": 1800000},
                    {"symbol": "HDFC", "quantity": 75, "value": 1200000}
                ],
                "total_value": 5500000,
                "currency": "INR",
                "last_updated": datetime.utcnow().isoformat()
            },
            "privacy_tier": "onyx",
            "proof_requirements": ["portfolio_ownership", "net_worth_threshold"],
            "user_context": {
                "user_id": "anonymous_user_123",
                "privacy_level": "standard"
            },
            "verification_parameters": {
                "min_net_worth": 5000000,
                "max_net_worth": 20000000,
                "proof_validity_hours": 24
            }
        }
        
        response = await test_client.post(
            "/api/v1/anonymous-services/zk-proof/generate",
            json=zk_proof_request
        )
        
        assert response.status_code == 200
        response_data = response.json()
        
        # Verify ZK proof response
        assert "proof_id" in response_data
        assert "status" in response_data
        assert "proof_data" in response_data
        assert "verification_hash" in response_data
        assert "confidence_score" in response_data
        assert "expires_at" in response_data
        
        assert response_data["status"] == "verified"
        assert response_data["confidence_score"] >= 0.95
        assert response_data["proof_id"].startswith("zkp_onyx_")
        
        # Verify proof data doesn't reveal sensitive information
        proof_json = json.dumps(response_data["proof_data"])
        assert "RELIANCE" not in proof_json
        assert "2500000" not in proof_json
        assert "5500000" not in proof_json
        
        # Test proof verification
        verify_request = {
            "proof_id": response_data["proof_id"],
            "verification_hash": response_data["verification_hash"]
        }
        
        verify_response = await test_client.post(
            "/api/v1/anonymous-services/zk-proof/verify",
            json=verify_request
        )
        
        assert verify_response.status_code == 200
        verify_data = verify_response.json()
        
        assert verify_data["is_valid"] is True
        assert verify_data["confidence"] >= 0.95
        assert verify_data["privacy_preserved"] is True
    
    async def test_anonymous_identity_creation(self, test_client: AsyncClient, override_service_dependencies):
        """Test anonymous identity creation for different tiers."""
        # Test Obsidian tier identity
        identity_request = {
            "privacy_tier": "obsidian",
            "portfolio_value": 35000000,
            "risk_profile": "moderate",
            "investment_preferences": ["equity", "mutual_funds", "bonds"],
            "user_context": {
                "original_user_id": "real_user_456",
                "verification_level": "kyc_completed"
            },
            "emergency_contacts": ["emergency@user.com"],
            "compliance_requirements": ["fatca", "pep_check"]
        }
        
        response = await test_client.post(
            "/api/v1/anonymous-services/identity/create",
            json=identity_request
        )
        
        assert response.status_code == 201
        response_data = response.json()
        
        # Verify anonymous identity response
        assert "identity_id" in response_data
        assert "privacy_tier" in response_data
        assert "public_key" in response_data
        assert "proof_requirements" in response_data
        assert "created_at" in response_data
        
        assert response_data["identity_id"].startswith("anon_obsidian_")
        assert response_data["privacy_tier"] == "obsidian"
        assert len(response_data["public_key"]) > 0
        assert len(response_data["proof_requirements"]) >= 2
        
        # Verify original identity is not revealed
        response_json = json.dumps(response_data)
        assert "real_user_456" not in response_json
        assert "35000000" not in response_json
    
    async def test_butler_ai_interaction(self, test_client: AsyncClient, override_service_dependencies):
        """Test Butler AI mediation system."""
        # First create anonymous identity
        identity_request = {
            "privacy_tier": "void",
            "portfolio_value": 100000000,
            "risk_profile": "aggressive",
            "investment_preferences": ["derivatives", "alternatives"],
            "user_context": {"original_user_id": "whale_user"},
            "butler_preferences": {
                "personality": "nexus",
                "communication_style": "analytical"
            }
        }
        
        identity_response = await test_client.post(
            "/api/v1/anonymous-services/identity/create",
            json=identity_request
        )
        
        assert identity_response.status_code == 201
        identity_data = identity_response.json()
        
        # Test Butler AI interaction
        butler_request = {
            "anonymous_identity_id": identity_data["identity_id"],
            "interaction_type": "portfolio_analysis",
            "message": "Analyze my derivatives exposure and suggest optimizations",
            "context": {
                "market_conditions": "volatile",
                "time_horizon": "6_months"
            }
        }
        
        butler_response = await test_client.post(
            "/api/v1/anonymous-services/butler/interact",
            json=butler_request
        )
        
        assert butler_response.status_code == 200
        butler_data = butler_response.json()
        
        # Verify Butler AI response
        assert "interaction_id" in butler_data
        assert "butler_personality" in butler_data
        assert "response" in butler_data
        assert "privacy_maintained" in butler_data
        
        assert butler_data["butler_personality"] == "nexus"
        assert butler_data["privacy_maintained"] is True
        assert len(butler_data["response"]["analysis"]) > 0
        assert len(butler_data["response"]["recommendations"]) > 0
        
        # Verify no identity leakage
        response_json = json.dumps(butler_data)
        assert "whale_user" not in response_json


class TestTradingServicesAPI:
    """Integration tests for Trading Services API endpoints."""
    
    async def test_trading_account_setup(self, test_client: AsyncClient, override_auth_dependencies):
        """Test trading account setup and configuration."""
        account_setup = {
            "account_type": "institutional",
            "risk_profile": "moderate",
            "trading_preferences": {
                "markets": ["nse", "bse", "mcx"],
                "instruments": ["equity", "derivatives", "commodities"],
                "order_types": ["market", "limit", "stop_loss", "bracket"]
            },
            "risk_limits": {
                "daily_loss_limit": 1000000,
                "position_size_limit": 5000000,
                "sector_concentration_limit": 0.3
            },
            "compliance_settings": {
                "regulatory_jurisdiction": "india",
                "reporting_requirements": ["sebi", "rbi"],
                "kyc_level": "enhanced"
            }
        }
        
        response = await test_client.post(
            "/api/v1/trading-services/account/setup",
            json=account_setup
        )
        
        assert response.status_code == 201
        response_data = response.json()
        
        # Verify account setup response
        assert "account_id" in response_data
        assert "status" in response_data
        assert "trading_permissions" in response_data
        assert "risk_limits" in response_data
        assert "api_credentials" in response_data
        
        assert response_data["status"] == "active"
        assert len(response_data["trading_permissions"]["markets"]) == 3
        assert response_data["risk_limits"]["daily_loss_limit"] == 1000000
    
    async def test_order_management_flow(self, test_client: AsyncClient, override_auth_dependencies):
        """Test complete order management flow."""
        # Place order
        order_request = {
            "symbol": "RELIANCE",
            "exchange": "NSE",
            "order_type": "limit",
            "side": "buy",
            "quantity": 100,
            "price": 2500.0,
            "time_in_force": "day",
            "client_order_id": "test_order_123",
            "risk_checks": {
                "position_limit_check": True,
                "margin_requirement_check": True,
                "sector_limit_check": True
            }
        }
        
        order_response = await test_client.post(
            "/api/v1/trading-services/orders/place",
            json=order_request
        )
        
        assert order_response.status_code == 201
        order_data = order_response.json()
        
        # Verify order placement
        assert "order_id" in order_data
        assert "status" in order_data
        assert "execution_details" in order_data
        
        assert order_data["status"] == "pending"
        assert order_data["execution_details"]["symbol"] == "RELIANCE"
        assert order_data["execution_details"]["quantity"] == 100
        
        order_id = order_data["order_id"]
        
        # Get order status
        status_response = await test_client.get(f"/api/v1/trading-services/orders/{order_id}")
        assert status_response.status_code == 200
        
        status_data = status_response.json()
        assert status_data["order_id"] == order_id
        assert "current_status" in status_data
        assert "execution_history" in status_data
        
        # Cancel order
        cancel_response = await test_client.delete(f"/api/v1/trading-services/orders/{order_id}")
        assert cancel_response.status_code == 200
        
        cancel_data = cancel_response.json()
        assert cancel_data["status"] == "cancelled"
        assert cancel_data["cancellation_time"] is not None
    
    async def test_risk_management_system(self, test_client: AsyncClient, override_auth_dependencies):
        """Test risk management and monitoring."""
        # Get current risk exposure
        risk_response = await test_client.get("/api/v1/trading-services/risk/exposure")
        assert risk_response.status_code == 200
        
        risk_data = risk_response.json()
        
        # Verify risk exposure data
        assert "total_exposure" in risk_data
        assert "sector_exposure" in risk_data
        assert "position_summary" in risk_data
        assert "risk_metrics" in risk_data
        
        # Test risk limit updates
        limit_update = {
            "daily_loss_limit": 2000000,
            "position_size_limit": 10000000,
            "sector_limits": {
                "banking": 0.4,
                "it": 0.3,
                "pharma": 0.2
            }
        }
        
        limit_response = await test_client.put(
            "/api/v1/trading-services/risk/limits",
            json=limit_update
        )
        
        assert limit_response.status_code == 200
        limit_data = limit_response.json()
        
        assert limit_data["status"] == "updated"
        assert limit_data["effective_from"] is not None


class TestBankingServicesAPI:
    """Integration tests for Banking Services API endpoints."""
    
    async def test_virtual_account_creation(self, test_client: AsyncClient, override_auth_dependencies):
        """Test virtual account creation and management."""
        account_request = {
            "account_type": "business",
            "currency": "INR",
            "account_purpose": "trading_settlement",
            "beneficiary_details": {
                "name": "Test Financial Corp",
                "type": "corporation",
                "registration_number": "TFC123456"
            },
            "compliance_level": "enhanced",
            "features": ["multi_currency", "real_time_settlement", "automated_reconciliation"]
        }
        
        response = await test_client.post(
            "/api/v1/banking-services/accounts/create",
            json=account_request
        )
        
        assert response.status_code == 201
        response_data = response.json()
        
        # Verify account creation
        assert "account_id" in response_data
        assert "account_number" in response_data
        assert "ifsc_code" in response_data
        assert "status" in response_data
        assert "features" in response_data
        
        assert response_data["status"] == "active"
        assert response_data["currency"] == "INR"
        assert len(response_data["features"]) == 3
    
    async def test_payment_processing_flow(self, test_client: AsyncClient, override_auth_dependencies):
        """Test payment processing and settlement."""
        # Initiate payment
        payment_request = {
            "amount": 1000000,
            "currency": "INR",
            "payment_type": "transfer",
            "sender": {
                "account_id": "test_sender_account",
                "name": "Test Sender Corp"
            },
            "receiver": {
                "account_number": "1234567890",
                "ifsc_code": "HDFC0001234",
                "name": "Test Receiver Corp"
            },
            "payment_method": "neft",
            "reference": "TXN123456789",
            "compliance_checks": ["sanctions_screening", "pep_check"]
        }
        
        payment_response = await test_client.post(
            "/api/v1/banking-services/payments/initiate",
            json=payment_request
        )
        
        assert payment_response.status_code == 201
        payment_data = payment_response.json()
        
        # Verify payment initiation
        assert "transaction_id" in payment_data
        assert "status" in payment_data
        assert "estimated_settlement_time" in payment_data
        assert "compliance_status" in payment_data
        
        assert payment_data["status"] == "processing"
        assert payment_data["compliance_status"] == "cleared"
        
        transaction_id = payment_data["transaction_id"]
        
        # Check payment status
        status_response = await test_client.get(
            f"/api/v1/banking-services/payments/{transaction_id}/status"
        )
        
        assert status_response.status_code == 200
        status_data = status_response.json()
        
        assert status_data["transaction_id"] == transaction_id
        assert "current_status" in status_data
        assert "settlement_details" in status_data
    
    async def test_compliance_automation(self, test_client: AsyncClient, override_auth_dependencies):
        """Test automated compliance and reporting."""
        # Get compliance status
        compliance_response = await test_client.get("/api/v1/banking-services/compliance/status")
        assert compliance_response.status_code == 200
        
        compliance_data = compliance_response.json()
        
        # Verify compliance data structure
        assert "overall_status" in compliance_data
        assert "kyc_status" in compliance_data
        assert "aml_status" in compliance_data
        assert "regulatory_reports" in compliance_data
        
        # Generate compliance report
        report_request = {
            "report_type": "monthly_transaction_summary",
            "period": {
                "start_date": (datetime.utcnow() - timedelta(days=30)).isoformat(),
                "end_date": datetime.utcnow().isoformat()
            },
            "include_sections": ["transaction_summary", "risk_analysis", "compliance_exceptions"],
            "format": "pdf"
        }
        
        report_response = await test_client.post(
            "/api/v1/banking-services/compliance/reports/generate",
            json=report_request
        )
        
        assert report_response.status_code == 200
        report_data = report_response.json()
        
        assert "report_id" in report_data
        assert "status" in report_data
        assert "download_url" in report_data
        assert "generated_at" in report_data
        
        assert report_data["status"] == "completed"


class TestAPIAuthentication:
    """Integration tests for API authentication and authorization."""
    
    async def test_jwt_token_authentication(self, test_client: AsyncClient, test_enterprise_client, test_user):
        """Test JWT token-based authentication."""
        # Login to get token
        login_data = {
            "email": test_user.email,
            "password": "test_password_123"
        }
        
        with patch('bcrypt.checkpw', return_value=True):
            login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        
        assert login_response.status_code == 200
        token_data = login_response.json()
        
        assert "access_token" in token_data
        assert "refresh_token" in token_data
        assert "token_type" in token_data
        
        # Use token to access protected endpoint
        headers = {"Authorization": f"Bearer {token_data['access_token']}"}
        protected_response = await test_client.get("/api/v1/partners/profile", headers=headers)
        
        assert protected_response.status_code == 200
    
    async def test_api_key_authentication(self, test_client: AsyncClient, test_api_key):
        """Test API key-based authentication."""
        # Use API key to access endpoint
        headers = {"X-API-Key": test_api_key._test_key_value}
        
        response = await test_client.get("/api/v1/partners/services/available", headers=headers)
        assert response.status_code == 200
    
    async def test_rate_limiting(self, test_client: AsyncClient, test_api_key):
        """Test rate limiting enforcement."""
        headers = {"X-API-Key": test_api_key._test_key_value}
        
        # Make requests up to rate limit
        responses = []
        for i in range(10):  # Assuming rate limit is higher than 10
            response = await test_client.get("/api/v1/partners/services/available", headers=headers)
            responses.append(response)
        
        # All requests should succeed initially
        assert all(r.status_code == 200 for r in responses)
        
        # Check rate limit headers
        last_response = responses[-1]
        assert "X-RateLimit-Limit" in last_response.headers
        assert "X-RateLimit-Remaining" in last_response.headers
        assert "X-RateLimit-Reset" in last_response.headers
    
    async def test_permission_based_access_control(self, test_client: AsyncClient):
        """Test permission-based access control."""
        # Test with limited permissions
        limited_permissions = ["ai_suite.support.query"]
        
        # Mock user with limited permissions
        with patch('...auth.enterprise_auth.get_current_user') as mock_auth:
            mock_auth.return_value.permissions = limited_permissions
            
            # Should allow AI support access
            ai_response = await test_client.post(
                "/api/v1/ai-services/support/query",
                json={"user_message": "test", "language": "en"}
            )
            assert ai_response.status_code == 200
            
            # Should deny trading access
            trading_response = await test_client.post(
                "/api/v1/trading-services/orders/place",
                json={"symbol": "TEST", "side": "buy", "quantity": 10}
            )
            assert trading_response.status_code == 403


class TestErrorHandling:
    """Integration tests for error handling and edge cases."""
    
    async def test_invalid_request_data(self, test_client: AsyncClient, override_auth_dependencies):
        """Test handling of invalid request data."""
        # Invalid AI support request
        invalid_request = {
            "user_message": "",  # Empty message
            "language": "invalid_lang",  # Invalid language
            "user_context": "not_an_object"  # Invalid context
        }
        
        response = await test_client.post(
            "/api/v1/ai-services/support/query",
            json=invalid_request
        )
        
        assert response.status_code == 422  # Validation error
        error_data = response.json()
        
        assert "detail" in error_data
        assert "validation_errors" in error_data["detail"]
    
    async def test_service_unavailable_scenarios(self, test_client: AsyncClient, override_auth_dependencies):
        """Test handling of service unavailable scenarios."""
        # Mock service failure
        with patch('...ai_suite.support_engine.SupportEngine.process_support_request') as mock_service:
            mock_service.side_effect = Exception("Service temporarily unavailable")
            
            request_data = {
                "user_message": "What is stock market?",
                "language": "en",
                "user_context": {"user_id": "test"}
            }
            
            response = await test_client.post(
                "/api/v1/ai-services/support/query",
                json=request_data
            )
            
            assert response.status_code == 503  # Service unavailable
            error_data = response.json()
            
            assert "error" in error_data
            assert "service_unavailable" in error_data["error"]
    
    async def test_database_connection_failure(self, test_client: AsyncClient):
        """Test handling of database connection failures."""
        # Mock database connection failure
        with patch('...database.session.get_db') as mock_db:
            mock_db.side_effect = Exception("Database connection failed")
            
            response = await test_client.get("/api/v1/partners/profile")
            
            assert response.status_code == 503
            error_data = response.json()
            
            assert "database_error" in error_data["error"]