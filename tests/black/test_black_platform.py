"""
TradeMate Black Platform Test Suite
Comprehensive testing for ultra-premium trading platform
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch
import json

from app.black.app_core import TradeMateBlackApp
from app.black.models import BlackTier, BlackUser, AccessLevel
from app.black.authentication import BlackAuthentication
from app.black.market_butler import MarketButler
from app.black.luxury_ux import LuxuryUIComponents
from app.black.concierge_services import ConciergeServices
from app.black.invitation_system import ExclusiveInvitationSystem
from app.black.black_card_system import TradeMateBlackCardSystem


class TestTradeMateBlackApp:
    """Test suite for TradeMate Black core application"""
    
    @pytest.fixture
    async def black_app(self):
        """Initialize Black app for testing"""
        app = TradeMateBlackApp()
        await app.start()
        return app
    
    @pytest.fixture
    def void_user(self):
        """Create Void tier test user"""
        return BlackUser(
            user_id="void_test_user_001",
            tier=BlackTier.VOID,
            access_level=AccessLevel.EXCLUSIVE,
            portfolio_value=100000000000,  # ₹100 Cr
            net_worth=500000000000,        # ₹500 Cr
            risk_appetite="ultra_aggressive",
            investment_preferences=[],
            invitation_code="VOID2024001",
            invited_by="founder",
            joining_date=datetime.utcnow(),
            tier_progression_date=datetime.utcnow(),
            dedicated_butler="butler_void_001",
            butler_contact_preference="video",
            kyc_level="ultra_premium",
            aml_score=0.95,
            risk_score=0.1,
            compliance_status="verified",
            trading_hours_preference="24x7",
            notification_preferences={"market_alerts": True},
            privacy_settings={"public_profile": False},
            is_active=True,
            last_activity=datetime.utcnow(),
            session_count=0,
            total_trades=0,
            total_volume=0.0
        )
    
    @pytest.fixture
    def obsidian_user(self):
        """Create Obsidian tier test user"""
        return BlackUser(
            user_id="obsidian_test_user_001",
            tier=BlackTier.OBSIDIAN,
            access_level=AccessLevel.CONCIERGE,
            portfolio_value=30000000000,   # ₹30 Cr
            net_worth=80000000000,         # ₹80 Cr
            risk_appetite="aggressive",
            investment_preferences=[],
            invitation_code="OBS2024001",
            invited_by="void_user_001",
            joining_date=datetime.utcnow(),
            tier_progression_date=datetime.utcnow(),
            dedicated_butler="butler_obsidian_001",
            butler_contact_preference="call",
            kyc_level="premium",
            aml_score=0.92,
            risk_score=0.15,
            compliance_status="verified",
            trading_hours_preference="market_hours",
            notification_preferences={"market_alerts": True},
            privacy_settings={"public_profile": False},
            is_active=True,
            last_activity=datetime.utcnow(),
            session_count=0,
            total_trades=0,
            total_volume=0.0
        )
    
    @pytest.mark.asyncio
    async def test_black_app_initialization(self, black_app):
        """Test Black app initializes correctly"""
        assert black_app.is_running is True
        assert black_app.startup_time is not None
        assert len(black_app.user_profiles) > 0
        assert "void_user_001" in black_app.user_profiles
        
    @pytest.mark.asyncio
    async def test_void_user_authentication(self, black_app, void_user):
        """Test Void tier user authentication"""
        user_credentials = {
            "user_id": void_user.user_id,
            "secure_enclave_token": "test_token",
            "face_id_token": "test_face_id",
            "device_fingerprint": "test_fingerprint"
        }
        
        device_info = {
            "platform": "ios_native",
            "device_id": "test_device_001",
            "location": {"country": "IN"}
        }
        
        result = await black_app.authenticate_user(user_credentials, device_info)
        
        assert result["success"] is True
        assert result["security_level"] == "maximum"
        assert "session_id" in result
        assert result["user_profile"] is not None
        
    @pytest.mark.asyncio
    async def test_obsidian_user_authentication(self, black_app, obsidian_user):
        """Test Obsidian tier user authentication"""
        user_credentials = {
            "user_id": obsidian_user.user_id,
            "tee_token": "test_tee_token",
            "fingerprint_token": "test_fingerprint"
        }
        
        device_info = {
            "platform": "android_native",
            "device_id": "test_device_002",
            "location": {"country": "IN"}
        }
        
        result = await black_app.authenticate_user(user_credentials, device_info)
        
        assert result["success"] is True
        assert result["security_level"] == "maximum"
        assert "butler_connection" in result
        
    @pytest.mark.asyncio
    async def test_dashboard_data_retrieval(self, black_app):
        """Test dashboard data retrieval for different tiers"""
        # Create test session
        session_id = "test_session_001"
        user_id = "void_user_001"
        
        # Mock session
        black_app.active_sessions[session_id] = Mock()
        black_app.active_sessions[session_id].user_id = user_id
        black_app.active_sessions[session_id].last_activity = datetime.utcnow()
        black_app.active_sessions[session_id].screens_visited = []
        
        dashboard_data = await black_app.get_dashboard_data(session_id)
        
        assert "user_tier" in dashboard_data
        assert "portfolio_summary" in dashboard_data
        assert "market_insights" in dashboard_data
        assert "butler_status" in dashboard_data
        assert "exclusive_opportunities" in dashboard_data
        
    @pytest.mark.asyncio
    async def test_trade_execution_void_tier(self, black_app):
        """Test trade execution for Void tier with premium features"""
        session_id = "test_session_void"
        user_id = "void_user_001"
        
        # Mock session
        black_app.active_sessions[session_id] = Mock()
        black_app.active_sessions[session_id].user_id = user_id
        black_app.active_sessions[session_id].trades_executed = 0
        black_app.active_sessions[session_id].volume_traded = 0.0
        black_app.active_sessions[session_id].actions_performed = []
        
        trade_request = {
            "symbol": "TCS",
            "quantity": 1000,
            "price": 3850.00,
            "amount": 3850000,
            "order_type": "market"
        }
        
        result = await black_app.execute_black_trade(session_id, trade_request)
        
        assert result["success"] is True
        assert "trade_id" in result
        assert "premium_features_used" in result
        assert "zero_slippage_guarantee" in result["premium_features_used"]
        assert result["fees"]["brokerage"] == 0  # Zero brokerage for Black
        
    @pytest.mark.asyncio
    async def test_butler_service_request(self, black_app):
        """Test butler service request handling"""
        session_id = "test_session_butler"
        user_id = "void_user_001"
        
        # Mock session
        black_app.active_sessions[session_id] = Mock()
        black_app.active_sessions[session_id].user_id = user_id
        black_app.active_sessions[session_id].butler_conversations = []
        
        service_request = {
            "type": "market_analysis",
            "message": "Analyze TCS stock for next quarter",
            "priority": "high"
        }
        
        result = await black_app.request_butler_service(session_id, service_request)
        
        assert result["success"] is True
        assert "response" in result or "message" in result
        
    @pytest.mark.asyncio
    async def test_platform_metrics(self, black_app):
        """Test platform metrics retrieval"""
        metrics = await black_app.get_platform_metrics()
        
        assert "platform_status" in metrics
        assert "active_sessions" in metrics
        assert "total_users" in metrics
        assert "tier_distribution" in metrics
        assert metrics["platform_status"] == "operational"
        
    @pytest.mark.asyncio
    async def test_welcome_message_generation(self, black_app, void_user):
        """Test tier-specific welcome message generation"""
        welcome_message = await black_app._generate_welcome_message(void_user)
        
        assert "◆" in welcome_message  # Void symbol
        assert "Void" in welcome_message
        assert "privileges" in welcome_message.lower()
        
    @pytest.mark.asyncio
    async def test_portfolio_summary_void_tier(self, black_app, void_user):
        """Test portfolio summary for Void tier includes exclusive holdings"""
        portfolio_summary = await black_app._get_portfolio_summary(void_user)
        
        assert "total_value" in portfolio_summary
        assert "exclusive_holdings" in portfolio_summary
        assert len(portfolio_summary["exclusive_holdings"]) > 0
        assert portfolio_summary["total_value"] == void_user.portfolio_value
        
    @pytest.mark.asyncio
    async def test_exclusive_market_insights_void(self, black_app, void_user):
        """Test Void tier gets ultra-exclusive market insights"""
        insights = await black_app._get_exclusive_market_insights(void_user)
        
        assert len(insights) > 0
        void_insight = insights[0]
        assert void_insight["type"] == "void_exclusive"
        assert void_insight["confidence"] > 90
        assert void_insight["time_sensitive"] is True
        
    @pytest.mark.asyncio
    async def test_exclusive_opportunities_void(self, black_app, void_user):
        """Test Void tier gets exclusive investment opportunities"""
        opportunities = await black_app._get_exclusive_opportunities(void_user)
        
        assert len(opportunities) > 0
        opportunity = opportunities[0]
        assert opportunity.minimum_investment >= 100000000  # ₹10 Cr minimum
        assert BlackTier.VOID in opportunity.tier_requirements
        
    @pytest.mark.asyncio
    async def test_session_creation_and_tracking(self, black_app, void_user):
        """Test session creation and activity tracking"""
        device_info = {
            "platform": "ios_native",
            "device_id": "test_device_003",
            "location": {"country": "IN", "city": "Mumbai"}
        }
        
        auth_result = {
            "method": "hardware_biometric",
            "device_fingerprint": "test_fp_001",
            "risk_score": 0.05
        }
        
        session = await black_app._create_black_session(void_user, device_info, auth_result)
        
        assert session.user_id == void_user.user_id
        assert session.session_duration == 0.0
        assert len(session.screens_visited) == 0
        assert session.risk_score == 0.05
        assert session.session_id in black_app.active_sessions
        
    @pytest.mark.asyncio
    async def test_error_handling_invalid_session(self, black_app):
        """Test error handling for invalid session"""
        result = await black_app.get_dashboard_data("invalid_session_id")
        
        assert "error" in result
        assert result["error"] == "Invalid session"
        
    @pytest.mark.asyncio
    async def test_error_handling_invalid_user(self, black_app):
        """Test error handling for invalid user"""
        session_id = "test_session_invalid"
        
        # Mock session with invalid user
        black_app.active_sessions[session_id] = Mock()
        black_app.active_sessions[session_id].user_id = "invalid_user_id"
        
        result = await black_app.get_dashboard_data(session_id)
        
        assert "error" in result
        assert result["error"] == "User profile not found"


class TestBlackAuthentication:
    """Test suite for Black authentication system"""
    
    @pytest.fixture
    async def auth_system(self):
        """Initialize authentication system"""
        auth = BlackAuthentication()
        await auth.initialize()
        return auth
    
    @pytest.mark.asyncio
    async def test_authentication_initialization(self, auth_system):
        """Test authentication system initializes correctly"""
        assert len(auth_system.device_registry) >= 0
        assert len(auth_system.active_sessions) >= 0
        assert auth_system.ios_secure_enclave is not None
        assert auth_system.android_tee is not None
        
    @pytest.mark.asyncio
    async def test_ios_secure_enclave_authentication(self, auth_system):
        """Test iOS Secure Enclave authentication"""
        user_credentials = {
            "user_id": "test_void_user",
            "secure_enclave_token": "valid_token_123",
            "face_id_token": "face_id_valid"
        }
        
        device_info = {
            "platform": "ios_native",
            "device_id": "iphone_test_001",
            "model": "iPhone 14 Pro",
            "os_version": "16.5",
            "location": {"country": "IN"}
        }
        
        result = await auth_system.authenticate_black_user(user_credentials, device_info)
        
        assert result["success"] is True
        assert result["security_level"] == "maximum"
        assert "session_token" in result
        assert "hardware_features" in result
        
    @pytest.mark.asyncio
    async def test_android_tee_authentication(self, auth_system):
        """Test Android TEE authentication"""
        user_credentials = {
            "user_id": "test_obsidian_user",
            "tee_token": "valid_tee_token_456",
            "fingerprint_token": "fingerprint_valid"
        }
        
        device_info = {
            "platform": "android_native",
            "device_id": "android_test_001",
            "model": "Samsung Galaxy S23 Ultra",
            "os_version": "13",
            "location": {"country": "IN"}
        }
        
        result = await auth_system.authenticate_black_user(user_credentials, device_info)
        
        assert result["success"] is True
        assert result["authentication_method"] == "hardware_biometric_multi_factor"
        assert "biometric_features" in result
        
    @pytest.mark.asyncio
    async def test_device_validation_and_registration(self, auth_system):
        """Test device validation and new device registration"""
        device_info = {
            "platform": "ios_native",
            "device_id": "new_device_001",
            "model": "iPhone 15 Pro",
            "os_version": "17.0",
            "security_features": ["secure_enclave", "face_id"],
            "location": {"country": "IN"}
        }
        
        validation = await auth_system._validate_device(device_info)
        
        assert validation["valid"] is True
        assert "fingerprint" in validation
        assert validation["platform"] == "ios_native"
        
    @pytest.mark.asyncio
    async def test_risk_assessment_low_risk(self, auth_system):
        """Test risk assessment for normal usage"""
        result = await auth_system.risk_analyzer.assess_authentication_risk(
            "test_user_001",
            {"location": {"country": "IN"}, "first_seen": False},
            {"user_id": "test_user_001"}
        )
        
        assert "risk_score" in result
        assert result["risk_score"] < 0.3  # Should be low risk
        assert result["assessment"] == "low"
        
    @pytest.mark.asyncio
    async def test_risk_assessment_high_risk(self, auth_system):
        """Test risk assessment for suspicious activity"""
        result = await auth_system.risk_analyzer.assess_authentication_risk(
            "test_user_002",
            {"location": {"country": "US"}, "first_seen": True},  # Foreign + new device
            {"user_id": "test_user_002"}
        )
        
        assert result["risk_score"] >= 0.3  # Should be higher risk
        assert "foreign_location" in result["risk_factors"]
        assert "new_device" in result["risk_factors"]
        
    @pytest.mark.asyncio
    async def test_session_encryption_and_storage(self, auth_system):
        """Test session data encryption and secure storage"""
        session_data = {
            "session_id": "test_session_crypto_001",
            "user_id": "test_user_crypto",
            "created_at": datetime.utcnow().isoformat(),
            "security_level": "maximum"
        }
        
        encrypted_session = await auth_system._encrypt_session_data(session_data)
        
        assert isinstance(encrypted_session, bytes)
        assert len(encrypted_session) > len(json.dumps(session_data))
        
    @pytest.mark.asyncio
    async def test_authentication_failure_invalid_credentials(self, auth_system):
        """Test authentication failure with invalid credentials"""
        user_credentials = {
            "user_id": "test_user_invalid"
            # Missing required tokens
        }
        
        device_info = {
            "platform": "ios_native",
            "device_id": "test_device_invalid"
        }
        
        result = await auth_system.authenticate_black_user(user_credentials, device_info)
        
        assert result["success"] is False
        assert "error" in result
        
    @pytest.mark.asyncio
    async def test_platform_validation_unsupported(self, auth_system):
        """Test platform validation rejects unsupported platforms"""
        device_info = {
            "platform": "web_browser",  # Unsupported for Black tier
            "device_id": "web_device_001"
        }
        
        validation = await auth_system._validate_device(device_info)
        
        assert validation["valid"] is False
        assert "Unsupported platform" in validation["error"]


class TestMarketButler:
    """Test suite for Market Butler AI system"""
    
    @pytest.fixture
    async def market_butler(self):
        """Initialize Market Butler"""
        butler = MarketButler()
        await butler.start_butler_services()
        return butler
    
    @pytest.mark.asyncio
    async def test_butler_initialization(self, market_butler):
        """Test Market Butler initializes with correct butler profiles"""
        assert len(market_butler.butler_profiles) >= 3  # Void, Obsidian, Onyx butlers
        assert "butler_void_001" in market_butler.butler_profiles
        assert "butler_obsidian_001" in market_butler.butler_profiles
        
    @pytest.mark.asyncio
    async def test_user_butler_connection_void(self, market_butler):
        """Test connecting Void user to dedicated butler"""
        result = await market_butler.connect_user_butler("void_user_001", "butler_void_001")
        
        assert result["success"] is True
        assert "conversation_id" in result
        assert "butler_profile" in result
        assert result["butler_profile"]["name"] == "Arjun Mehta"
        assert "video" in result["communication_channels"]
        
    @pytest.mark.asyncio
    async def test_market_analysis_request(self, market_butler):
        """Test market analysis service request"""
        service_request = {
            "type": "market_analysis",
            "symbol": "TCS",
            "analysis_type": "comprehensive",
            "message": "Analyze TCS for Q4 earnings"
        }
        
        result = await market_butler.handle_service_request(
            "butler_void_001", "void_user_001", service_request
        )
        
        assert result["success"] is True
        assert result["type"] == "market_analysis"
        assert "data" in result
        assert "symbol" in result["data"]
        assert result["data"]["symbol"] == "TCS"
        
    @pytest.mark.asyncio
    async def test_portfolio_review_request(self, market_butler):
        """Test portfolio review service request"""
        service_request = {
            "type": "portfolio_review",
            "message": "Review my portfolio allocation and suggest optimizations"
        }
        
        result = await market_butler.handle_service_request(
            "butler_obsidian_001", "obsidian_user_001", service_request
        )
        
        assert result["success"] is True
        assert result["type"] == "portfolio_review"
        assert "portfolio_summary" in result["data"]
        assert "recommendations" in result["data"]
        
    @pytest.mark.asyncio
    async def test_trade_assistance_request(self, market_butler):
        """Test trade assistance request"""
        service_request = {
            "type": "trade_assistance",
            "trade_intent": {
                "symbol": "RELIANCE",
                "action": "buy",
                "quantity": 500
            },
            "message": "Help me execute this Reliance trade with optimal timing"
        }
        
        result = await market_butler.handle_service_request(
            "butler_void_001", "void_user_001", service_request
        )
        
        assert result["success"] is True
        assert result["type"] == "trade_assistance"
        assert "trade_analysis" in result["data"]
        assert "execution_options" in result["data"]
        
    @pytest.mark.asyncio
    async def test_butler_chat_conversation(self, market_butler):
        """Test general chat conversation with butler"""
        service_request = {
            "type": "general_chat",
            "message": "What's your view on the current market sentiment?"
        }
        
        result = await market_butler.handle_service_request(
            "butler_void_001", "void_user_001", service_request
        )
        
        assert result["success"] is True
        assert result["type"] == "chat"
        assert "message" in result
        assert len(result["message"]) > 0
        
    @pytest.mark.asyncio
    async def test_butler_status_retrieval(self, market_butler):
        """Test butler status and availability"""
        status = await market_butler.get_butler_status("butler_void_001")
        
        assert "available" in status
        assert "name" in status
        assert "response_time" in status
        assert "satisfaction_rating" in status
        assert status["name"] == "Arjun Mehta"
        
    @pytest.mark.asyncio
    async def test_trade_execution_notification(self, market_butler):
        """Test butler notification of trade execution"""
        trade_result = {
            "trade_id": "BLACK_12345",
            "symbol": "TCS",
            "quantity": 1000,
            "price": 3850.00,
            "status": "executed"
        }
        
        result = await market_butler.notify_trade_execution(
            "butler_void_001", "void_user_001", trade_result
        )
        
        assert result["success"] is True
        assert "notification" in result
        
    @pytest.mark.asyncio
    async def test_butler_utilization_metrics(self, market_butler):
        """Test butler system utilization metrics"""
        metrics = await market_butler.get_utilization_metrics()
        
        assert "total_butlers" in metrics
        assert "active_conversations" in metrics
        assert "utilization_by_tier" in metrics
        assert "average_response_time" in metrics
        assert "average_satisfaction" in metrics
        
    @pytest.mark.asyncio
    async def test_butler_tier_assignment(self, market_butler):
        """Test butler tier assignment logic"""
        void_tier = market_butler._get_butler_tier("butler_void_001")
        obsidian_tier = market_butler._get_butler_tier("butler_obsidian_001")
        onyx_tier = market_butler._get_butler_tier("butler_onyx_001")
        
        assert void_tier == "void"
        assert obsidian_tier == "obsidian"
        assert onyx_tier == "onyx"
        
    @pytest.mark.asyncio
    async def test_butler_error_handling(self, market_butler):
        """Test butler error handling for invalid requests"""
        result = await market_butler.handle_service_request(
            "invalid_butler_id", "invalid_user_id", {}
        )
        
        assert result["success"] is False
        assert "error" in result


class TestLuxuryUX:
    """Test suite for Luxury UX system"""
    
    @pytest.fixture
    async def luxury_ux(self):
        """Initialize Luxury UX system"""
        ux = LuxuryUIComponents()
        return ux
    
    @pytest.fixture
    def void_user(self):
        """Create Void tier user for UX testing"""
        return BlackUser(
            user_id="void_ux_test_001",
            tier=BlackTier.VOID,
            access_level=AccessLevel.EXCLUSIVE,
            portfolio_value=100000000000,
            net_worth=500000000000,
            risk_appetite="ultra_aggressive",
            investment_preferences=[],
            invitation_code="VOID2024001",
            invited_by="founder",
            joining_date=datetime.utcnow() - timedelta(days=365),
            tier_progression_date=datetime.utcnow() - timedelta(days=180),
            dedicated_butler="butler_void_001",
            butler_contact_preference="video",
            kyc_level="ultra_premium",
            aml_score=0.95,
            risk_score=0.1,
            compliance_status="verified",
            trading_hours_preference="24x7",
            notification_preferences={"market_alerts": True},
            privacy_settings={"public_profile": False},
            is_active=True,
            last_activity=datetime.utcnow(),
            session_count=50,
            total_trades=150,
            total_volume=10000000000.0
        )
    
    @pytest.mark.asyncio
    async def test_void_tier_ux_preparation(self, luxury_ux, void_user):
        """Test Void tier UX context preparation"""
        context = await luxury_ux.prepare_user_context(void_user)
        
        assert "theme" in context
        assert "animations" in context
        assert "personalization" in context
        assert "exclusive_widgets" in context
        assert context["luxury_level"] > 0.9  # Void should have maximum luxury
        
    @pytest.mark.asyncio
    async def test_void_tier_features(self, luxury_ux):
        """Test Void tier gets all luxury features"""
        features = await luxury_ux.get_tier_features(BlackTier.VOID)
        
        assert "theme" in features
        assert features["theme"] == "◆ Void Transcendent"
        assert "reality_distortion" in features["special_effects"]
        assert features["animation_tier"] == "transcendent"
        assert features["particle_density"] == "maximum"
        
    @pytest.mark.asyncio
    async def test_obsidian_tier_features(self, luxury_ux):
        """Test Obsidian tier gets imperial features"""
        features = await luxury_ux.get_tier_features(BlackTier.OBSIDIAN)
        
        assert features["theme"] == "⚫ Obsidian Imperial"
        assert "Holographic Chart Analysis" in features["exclusive_features"]
        assert features["animation_tier"] == "imperial"
        
    @pytest.mark.asyncio
    async def test_onyx_tier_features(self, luxury_ux):
        """Test Onyx tier gets professional features"""
        features = await luxury_ux.get_tier_features(BlackTier.ONYX)
        
        assert features["theme"] == "🖤 Onyx Professional"
        assert "Crystalline Portfolio View" in features["exclusive_features"]
        assert features["animation_tier"] == "professional"
        
    @pytest.mark.asyncio
    async def test_tier_theme_configuration(self, luxury_ux):
        """Test tier-specific theme configuration"""
        void_theme = await luxury_ux._get_tier_theme(BlackTier.VOID)
        obsidian_theme = await luxury_ux._get_tier_theme(BlackTier.OBSIDIAN)
        onyx_theme = await luxury_ux._get_tier_theme(BlackTier.ONYX)
        
        assert "void_black" in void_theme["primary_colors"]
        assert "obsidian_deep" in obsidian_theme["primary_colors"]
        assert "onyx_black" in onyx_theme["primary_colors"]
        
    @pytest.mark.asyncio
    async def test_animation_preparation(self, luxury_ux):
        """Test tier-specific animation preparation"""
        void_animations = await luxury_ux._prepare_tier_animations(BlackTier.VOID)
        obsidian_animations = await luxury_ux._prepare_tier_animations(BlackTier.OBSIDIAN)
        
        assert void_animations["particle_count"] > obsidian_animations["particle_count"]
        assert void_animations["duration"] > obsidian_animations["duration"]
        assert "reality_distortion" in void_animations["effects"]
        
    @pytest.mark.asyncio
    async def test_exclusive_widgets_void(self, luxury_ux):
        """Test Void tier gets exclusive widgets"""
        widgets = await luxury_ux._get_tier_exclusive_widgets(
            BlackTier.VOID, AccessLevel.EXCLUSIVE
        )
        
        assert len(widgets) >= 3  # Should have multiple exclusive widgets
        widget_types = [w["widget_type"] for w in widgets]
        assert "void_insights" in widget_types
        assert "quantum_butler" in widget_types
        
    @pytest.mark.asyncio
    async def test_haptic_configuration(self, luxury_ux):
        """Test tier-specific haptic feedback configuration"""
        void_haptics = await luxury_ux._configure_tier_haptics(BlackTier.VOID)
        onyx_haptics = await luxury_ux._configure_tier_haptics(BlackTier.ONYX)
        
        assert void_haptics["intensity"] > onyx_haptics["intensity"]
        assert "quantum_resonance" in void_haptics["trade_execution"]
        assert "reality_ripple" in void_haptics["market_insight"]
        
    @pytest.mark.asyncio
    async def test_luxury_level_calculation(self, luxury_ux, void_user):
        """Test luxury experience level calculation"""
        luxury_level = luxury_ux._calculate_luxury_level(void_user)
        
        assert luxury_level >= 0.9  # Void with high portfolio and tenure
        assert luxury_level <= 1.0
        
    @pytest.mark.asyncio
    async def test_personalization_engine(self, luxury_ux, void_user):
        """Test personalization engine for user elements"""
        personalization = await luxury_ux.personalization.generate_user_elements(void_user)
        
        assert "personal_greeting" in personalization
        assert "custom_color_temperature" in personalization
        assert "interaction_speed" in personalization
        assert "luxury_intensity" in personalization


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])