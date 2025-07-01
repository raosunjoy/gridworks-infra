"""
TradeMate Black Concierge Services Test Suite
Comprehensive testing for Vertu-style concierge system
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch
import json

from app.black.concierge_services import ConciergeServices, ServiceType, ServicePriority
from app.black.concierge_operations import VertuConciergeCenter, ConciergeSpecialty
from app.black.luxury_partner_network import LuxuryPartnerNetwork, PartnerCategory
from app.black.black_card_system import TradeMateBlackCardSystem, EmergencyType
from app.black.models import BlackTier, BlackUser, AccessLevel


class TestConciergeServices:
    """Test suite for Concierge Services"""
    
    @pytest.fixture
    async def concierge_services(self):
        """Initialize concierge services"""
        services = ConciergeServices()
        await services.initialize_services()
        return services
    
    @pytest.fixture
    def void_user(self):
        """Create Void tier test user"""
        return BlackUser(
            user_id="void_concierge_test_001",
            tier=BlackTier.VOID,
            access_level=AccessLevel.EXCLUSIVE,
            portfolio_value=100000000000,
            net_worth=500000000000,
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
    
    @pytest.mark.asyncio
    async def test_concierge_initialization(self, concierge_services):
        """Test concierge services initialize correctly"""
        assert len(concierge_services.service_teams) >= 4
        assert "trading" in concierge_services.service_teams
        assert "wealth" in concierge_services.service_teams
        assert "lifestyle" in concierge_services.service_teams
        assert "institutional" in concierge_services.service_teams
        
    @pytest.mark.asyncio
    async def test_private_jet_booking_request(self, concierge_services, void_user):
        """Test private jet booking service request"""
        service_request = {
            "type": "private_jet_booking",
            "description": "Book private jet from Mumbai to Dubai for tomorrow",
            "departure": "Mumbai",
            "destination": "Dubai", 
            "date": (datetime.utcnow() + timedelta(days=1)).isoformat(),
            "passengers": 4,
            "urgency": "high"
        }
        
        result = await concierge_services.submit_service_request(
            void_user.user_id,
            ServiceType.PRIVATE_JET_BOOKING,
            service_request,
            ServicePriority.URGENT
        )
        
        assert result["success"] is True
        assert "request_id" in result
        assert result["service_type"] == "private_jet_booking"
        assert result["priority"] == "urgent"
        assert "estimated_completion" in result
        
    @pytest.mark.asyncio
    async def test_luxury_yacht_charter(self, concierge_services, void_user):
        """Test luxury yacht charter service"""
        service_request = {
            "type": "luxury_yacht_charter",
            "description": "Charter yacht for weekend in Goa",
            "location": "Goa",
            "duration": "3 days",
            "guests": 8,
            "amenities": ["chef", "crew", "water_sports"]
        }
        
        result = await concierge_services.submit_service_request(
            void_user.user_id,
            ServiceType.LUXURY_YACHT_CHARTER,
            service_request,
            ServicePriority.STANDARD
        )
        
        assert result["success"] is True
        assert result["service_type"] == "luxury_yacht_charter"
        
    @pytest.mark.asyncio
    async def test_michelin_restaurant_reservation(self, concierge_services, void_user):
        """Test Michelin restaurant reservation"""
        service_request = {
            "type": "michelin_reservations",
            "description": "Reserve table at Trishna for anniversary dinner",
            "restaurant": "Trishna Mumbai",
            "date": (datetime.utcnow() + timedelta(days=7)).isoformat(),
            "party_size": 2,
            "special_requests": "Anniversary celebration, wine pairing"
        }
        
        result = await concierge_services.submit_service_request(
            void_user.user_id,
            ServiceType.MICHELIN_RESERVATIONS,
            service_request,
            ServicePriority.STANDARD
        )
        
        assert result["success"] is True
        assert "tracking_url" in result
        
    @pytest.mark.asyncio
    async def test_art_acquisition_service(self, concierge_services, void_user):
        """Test art acquisition service for Void tier"""
        service_request = {
            "type": "art_acquisition",
            "description": "Acquire contemporary Indian art piece",
            "artist": "Anish Kapoor",
            "budget_range": "₹5-10 Cr",
            "style": "contemporary sculpture",
            "timeline": "3 months"
        }
        
        result = await concierge_services.submit_service_request(
            void_user.user_id,
            ServiceType.ART_ACQUISITION,
            service_request,
            ServicePriority.STANDARD
        )
        
        assert result["success"] is True
        assert result["service_type"] == "art_acquisition"
        
    @pytest.mark.asyncio
    async def test_emergency_medical_service(self, concierge_services, void_user):
        """Test emergency medical service"""
        service_request = {
            "type": "medical_emergency",
            "description": "Medical emergency requiring immediate assistance",
            "location": "Mumbai Bandra",
            "severity": "high",
            "patient_info": "Conscious, chest pain"
        }
        
        result = await concierge_services.submit_service_request(
            void_user.user_id,
            ServiceType.MEDICAL_EMERGENCY,
            service_request,
            ServicePriority.EMERGENCY
        )
        
        assert result["success"] is True
        assert result["priority"] == "emergency"
        # Emergency services should have very fast response
        estimated_completion = datetime.fromisoformat(result["estimated_completion"])
        assert estimated_completion < datetime.utcnow() + timedelta(minutes=30)
        
    @pytest.mark.asyncio
    async def test_security_escort_service(self, concierge_services, void_user):
        """Test security escort service"""
        service_request = {
            "type": "security_escort",
            "description": "Security escort for high-value transaction",
            "location": "Mumbai Financial District",
            "duration": "4 hours",
            "threat_level": "medium",
            "personnel_required": 2
        }
        
        result = await concierge_services.submit_service_request(
            void_user.user_id,
            ServiceType.SECURITY_ESCORT,
            service_request,
            ServicePriority.URGENT
        )
        
        assert result["success"] is True
        assert result["service_type"] == "security_escort"
        
    @pytest.mark.asyncio
    async def test_billionaire_networking_service(self, concierge_services, void_user):
        """Test billionaire networking service (Void exclusive)"""
        service_request = {
            "type": "billionaire_networking",
            "description": "Introduction to tech billionaire for investment opportunity",
            "target_profile": "Tech entrepreneur, AI/ML space",
            "purpose": "Series C investment opportunity",
            "investment_range": "₹100-500 Cr"
        }
        
        result = await concierge_services.submit_service_request(
            void_user.user_id,
            ServiceType.BILLIONAIRE_NETWORKING,
            service_request,
            ServicePriority.STANDARD
        )
        
        assert result["success"] is True
        assert result["service_type"] == "billionaire_networking"
        
    @pytest.mark.asyncio
    async def test_government_relations_service(self, concierge_services, void_user):
        """Test government relations service (Void exclusive)"""
        service_request = {
            "type": "government_introductions",
            "description": "Policy briefing on upcoming fintech regulations",
            "department": "Ministry of Finance",
            "purpose": "Regulatory compliance discussion",
            "timeline": "Next 30 days"
        }
        
        result = await concierge_services.submit_service_request(
            void_user.user_id,
            ServiceType.GOVERNMENT_INTRODUCTIONS,
            service_request,
            ServicePriority.HIGH
        )
        
        assert result["success"] is True
        
    @pytest.mark.asyncio
    async def test_service_availability_tier_restrictions(self, concierge_services):
        """Test service availability respects tier restrictions"""
        # Create Onyx user (lower tier)
        onyx_user = BlackUser(
            user_id="onyx_test_001",
            tier=BlackTier.ONYX,
            access_level=AccessLevel.STANDARD,
            portfolio_value=5000000000,  # ₹5 Cr
            net_worth=15000000000,       # ₹15 Cr
            risk_appetite="moderate",
            investment_preferences=[],
            invitation_code="ONX2024001",
            invited_by="referral",
            joining_date=datetime.utcnow(),
            tier_progression_date=datetime.utcnow(),
            dedicated_butler="butler_onyx_001",
            butler_contact_preference="chat",
            kyc_level="enhanced",
            aml_score=0.90,
            risk_score=0.20,
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
        
        # Try to access Void-exclusive service
        service_request = {
            "type": "billionaire_networking",
            "description": "Request billionaire introduction"
        }
        
        result = await concierge_services.submit_service_request(
            onyx_user.user_id,
            ServiceType.BILLIONAIRE_NETWORKING,
            service_request,
            ServicePriority.STANDARD
        )
        
        assert result["success"] is False
        assert "not available" in result["error"]
        assert "alternative_services" in result
        
    @pytest.mark.asyncio
    async def test_active_requests_retrieval(self, concierge_services, void_user):
        """Test retrieval of active concierge requests"""
        # Submit a request first
        service_request = {
            "type": "luxury_shopping",
            "description": "Personal shopping for luxury watches"
        }
        
        await concierge_services.submit_service_request(
            void_user.user_id,
            ServiceType.LUXURY_SHOPPING,
            service_request,
            ServicePriority.STANDARD
        )
        
        # Get active requests
        active_requests = await concierge_services.get_active_requests(void_user.user_id)
        
        assert len(active_requests) > 0
        request = active_requests[0]
        assert "request_id" in request
        assert "service_type" in request
        assert "status" in request
        assert "progress_percentage" in request
        
    @pytest.mark.asyncio
    async def test_service_metrics(self, concierge_services):
        """Test service performance metrics"""
        metrics = await concierge_services.get_service_metrics()
        
        assert "total_active_requests" in metrics
        assert "completion_rate" in metrics
        assert "tier_metrics" in metrics
        assert "average_response_time" in metrics
        assert "quality_score" in metrics
        
        # Check tier-specific metrics
        for tier in ["VOID", "OBSIDIAN", "ONYX"]:
            assert tier in metrics["tier_metrics"]
            tier_metric = metrics["tier_metrics"][tier]
            assert "total_requests" in tier_metric
            assert "sla_compliance" in tier_metric
            
    @pytest.mark.asyncio
    async def test_service_level_monitoring(self, concierge_services):
        """Test service level agreement monitoring"""
        # This should run without errors
        await concierge_services.monitor_service_levels()
        
        # Verify monitoring doesn't break the system
        assert concierge_services is not None
        
    @pytest.mark.asyncio
    async def test_request_status_updates(self, concierge_services, void_user):
        """Test service request status updates"""
        # Submit initial request
        service_request = {
            "type": "executive_assistant",
            "description": "Schedule board meeting coordination"
        }
        
        result = await concierge_services.submit_service_request(
            void_user.user_id,
            ServiceType.EXECUTIVE_ASSISTANT,
            service_request,
            ServicePriority.STANDARD
        )
        
        request_id = result["request_id"]
        
        # Update status
        status_update = {
            "status": "in_progress",
            "message": "Meeting coordination initiated",
            "completion_percentage": 50,
            "specialist": "Executive Assistant Team",
            "next_steps": ["Confirm attendee availability", "Book conference room"]
        }
        
        update_result = await concierge_services.update_request_status(
            request_id, status_update
        )
        
        assert update_result["success"] is True
        assert update_result["status"] == "in_progress"
        assert "progress_update" in update_result
        assert "sla_status" in update_result


class TestVertuConciergeCenter:
    """Test suite for Vertu Concierge Operations Center"""
    
    @pytest.fixture
    async def concierge_center(self):
        """Initialize Vertu Concierge Center"""
        center = VertuConciergeCenter()
        await center.initialize_operations()
        return center
    
    @pytest.fixture
    def void_user(self):
        """Create Void tier test user"""
        return BlackUser(
            user_id="void_vertu_test_001",
            tier=BlackTier.VOID,
            access_level=AccessLevel.EXCLUSIVE,
            portfolio_value=100000000000,
            net_worth=500000000000,
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
    
    @pytest.mark.asyncio
    async def test_vertu_center_initialization(self, concierge_center):
        """Test Vertu concierge center initializes with specialists"""
        assert len(concierge_center.specialists) >= 3
        assert "void_lead" in concierge_center.specialists
        assert "void_lifestyle" in concierge_center.specialists
        
    @pytest.mark.asyncio
    async def test_immediate_acknowledgment(self, concierge_center, void_user):
        """Test immediate acknowledgment for Void users"""
        acknowledgment = await concierge_center._send_immediate_acknowledgment(void_user)
        
        assert "message" in acknowledgment
        assert "◆" in acknowledgment["message"]  # Void symbol
        assert "Void concierge" in acknowledgment["message"]
        assert acknowledgment["response_time"] == "immediate"
        
    @pytest.mark.asyncio
    async def test_request_classification(self, concierge_center):
        """Test request classification system"""
        emergency_request = {
            "message": "Emergency medical assistance needed immediately",
            "location": "Mumbai"
        }
        
        classification = await concierge_center._classify_request(
            emergency_request, BlackTier.VOID
        )
        
        assert classification["emergency"] is True
        assert classification["priority"] in ["critical", "highest"]
        assert classification["response_time_target"] == "immediate"
        
    @pytest.mark.asyncio
    async def test_luxury_lifestyle_classification(self, concierge_center):
        """Test luxury lifestyle service classification"""
        luxury_request = {
            "message": "Need to book a yacht for next weekend in Goa",
            "type": "lifestyle"
        }
        
        classification = await concierge_center._classify_request(
            luxury_request, BlackTier.VOID
        )
        
        assert classification["service_category"] == "luxury_lifestyle"
        assert classification["emergency"] is False
        assert classification["estimated_complexity"] in ["low", "medium", "high"]
        
    @pytest.mark.asyncio
    async def test_concierge_request_handling(self, concierge_center, void_user):
        """Test complete concierge request handling flow"""
        request = {
            "message": "I need assistance booking a private dining experience at a Michelin restaurant",
            "type": "dining",
            "urgency": "standard",
            "date": (datetime.utcnow() + timedelta(days=3)).isoformat()
        }
        
        result = await concierge_center.handle_concierge_request(void_user, request)
        
        assert "immediate_acknowledgment" in result
        assert "service_classification" in result
        assert "routing_details" in result
        assert "service_response" in result
        assert "tracking_id" in result
        
    @pytest.mark.asyncio
    async def test_specialist_assignment(self, concierge_center):
        """Test specialist assignment logic"""
        # Mock request object
        mock_request = Mock()
        mock_request.service_type = ConciergeSpecialty.LUXURY_LIFESTYLE.value
        
        assignment = await concierge_center.coordination_engine.assign_specialist(mock_request)
        
        assert assignment is not None
        
    @pytest.mark.asyncio
    async def test_time_greeting_logic(self, concierge_center):
        """Test time-based greeting logic"""
        greeting = concierge_center._get_time_greeting()
        
        assert greeting in ["morning", "afternoon", "evening"]
        
    @pytest.mark.asyncio
    async def test_response_time_targets(self, concierge_center):
        """Test response time targets by tier"""
        void_target = concierge_center._get_response_time_target(BlackTier.VOID, False)
        obsidian_target = concierge_center._get_response_time_target(BlackTier.OBSIDIAN, False)
        emergency_target = concierge_center._get_response_time_target(BlackTier.VOID, True)
        
        assert void_target == "under_3_rings"
        assert obsidian_target == "under_30_seconds"
        assert emergency_target == "immediate"


class TestLuxuryPartnerNetwork:
    """Test suite for Luxury Partner Network"""
    
    @pytest.fixture
    async def partner_network(self):
        """Initialize luxury partner network"""
        network = LuxuryPartnerNetwork()
        await network.initialize_network()
        return network
    
    @pytest.fixture
    def void_user(self):
        """Create Void tier test user"""
        return BlackUser(
            user_id="void_partner_test_001",
            tier=BlackTier.VOID,
            access_level=AccessLevel.EXCLUSIVE,
            portfolio_value=100000000000,
            net_worth=500000000000,
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
    
    @pytest.mark.asyncio
    async def test_partner_network_initialization(self, partner_network):
        """Test partner network initializes with luxury partners"""
        assert len(partner_network.partners) >= 5
        assert "four_seasons" in partner_network.partners
        assert "netjets" in partner_network.partners
        assert "sothebys" in partner_network.partners
        assert "oberoi" in partner_network.partners
        
    @pytest.mark.asyncio
    async def test_four_seasons_partner_details(self, partner_network):
        """Test Four Seasons partner configuration"""
        four_seasons = partner_network.partners["four_seasons"]
        
        assert four_seasons.company_name == "Four Seasons Hotels and Resorts"
        assert four_seasons.brand_tier == "Heritage"
        assert four_seasons.category == PartnerCategory.TRAVEL_HOSPITALITY
        assert four_seasons.preferred_partner is True
        assert four_seasons.exclusive_deals is True
        assert BlackTier.VOID in four_seasons.tier_availability
        
    @pytest.mark.asyncio
    async def test_netjets_partner_details(self, partner_network):
        """Test NetJets partner configuration"""
        netjets = partner_network.partners["netjets"]
        
        assert netjets.company_name == "NetJets India"
        assert netjets.category == PartnerCategory.PRIVATE_AVIATION
        assert "Global Citation fleet" in netjets.specializations
        assert "Same-day availability" in netjets.exclusive_services
        assert netjets.response_time_sla == "1 hour"
        
    @pytest.mark.asyncio
    async def test_sothebys_void_exclusivity(self, partner_network):
        """Test Sotheby's Void-exclusive access"""
        sothebys = partner_network.partners["sothebys"]
        
        assert sothebys.tier_availability == [BlackTier.VOID]  # Void exclusive
        assert "Private viewing access" in sothebys.exclusive_services
        assert sothebys.commission_structure["purchase"] == 0.15
        
    @pytest.mark.asyncio
    async def test_hotel_booking_request(self, partner_network, void_user):
        """Test hotel booking through Four Seasons"""
        service_request = {
            "type": "hotel_booking",
            "description": "Presidential suite at Four Seasons Mumbai",
            "location": "Mumbai",
            "check_in": (datetime.utcnow() + timedelta(days=7)).isoformat(),
            "check_out": (datetime.utcnow() + timedelta(days=10)).isoformat(),
            "guests": 2,
            "special_requests": "Anniversary celebration, helicopter transfer"
        }
        
        result = await partner_network.request_service(void_user, service_request)
        
        assert result["success"] is True
        assert "booking_id" in result
        assert "partner" in result
        assert "exclusive_benefits" in result
        
    @pytest.mark.asyncio
    async def test_private_jet_booking(self, partner_network, void_user):
        """Test private jet booking through NetJets"""
        service_request = {
            "type": "private_jet",
            "description": "Mumbai to Dubai, tomorrow morning",
            "departure": "Mumbai",
            "destination": "Dubai",
            "date": (datetime.utcnow() + timedelta(days=1)).isoformat(),
            "passengers": 4
        }
        
        result = await partner_network.request_service(void_user, service_request)
        
        assert result["success"] is True
        assert "estimated_cost" in result
        assert "booking_confirmation" in result
        
    @pytest.mark.asyncio
    async def test_art_acquisition_sothebys(self, partner_network, void_user):
        """Test art acquisition through Sotheby's (Void exclusive)"""
        service_request = {
            "type": "art_acquisition",
            "description": "Contemporary Indian art acquisition",
            "artist": "Anish Kapoor",
            "budget": "₹5-10 Cr",
            "timeline": "Next auction season"
        }
        
        result = await partner_network.request_service(void_user, service_request)
        
        assert result["success"] is True
        assert "partner" in result
        
    @pytest.mark.asyncio
    async def test_tier_benefits_void(self, partner_network):
        """Test Void tier benefits across partner network"""
        benefits = await partner_network.get_tier_benefits(BlackTier.VOID)
        
        assert benefits["tier"] == "VOID"
        assert benefits["total_partners"] > 0
        assert "benefits_by_category" in benefits
        assert "exclusive_deals" in benefits
        assert "tier_privileges" in benefits
        
        # Check for ultra-premium privileges
        privileges = benefits["tier_privileges"]
        assert "Bespoke service creation" in privileges
        assert "Unlimited concierge support" in privileges
        
    @pytest.mark.asyncio
    async def test_tier_benefits_onyx(self, partner_network):
        """Test Onyx tier benefits are more limited"""
        benefits = await partner_network.get_tier_benefits(BlackTier.ONYX)
        
        assert benefits["tier"] == "ONYX"
        void_benefits = await partner_network.get_tier_benefits(BlackTier.VOID)
        
        # Onyx should have fewer total partners available
        assert benefits["total_partners"] <= void_benefits["total_partners"]
        
    @pytest.mark.asyncio
    async def test_partner_service_unavailable(self, partner_network):
        """Test handling when no suitable partners available"""
        # Create request that matches no partners
        service_request = {
            "type": "unknown_service",
            "description": "Service not offered by any partner",
            "location": "Mars"  # Impossible location
        }
        
        # Create basic user
        basic_user = BlackUser(
            user_id="basic_test_001",
            tier=BlackTier.ONYX,
            access_level=AccessLevel.STANDARD,
            portfolio_value=5000000000,
            net_worth=15000000000,
            risk_appetite="moderate",
            investment_preferences=[],
            invitation_code="ONX2024001",
            invited_by="referral",
            joining_date=datetime.utcnow(),
            tier_progression_date=datetime.utcnow(),
            dedicated_butler="butler_onyx_001",
            butler_contact_preference="chat",
            kyc_level="enhanced",
            aml_score=0.90,
            risk_score=0.20,
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
        
        result = await partner_network.request_service(basic_user, service_request)
        
        assert result["success"] is False
        assert "alternatives" in result


class TestBlackCardSystem:
    """Test suite for Black Card System"""
    
    @pytest.fixture
    async def card_system(self):
        """Initialize Black Card system"""
        system = TradeMateBlackCardSystem()
        await system.initialize_card_system()
        return system
    
    @pytest.fixture
    def void_user(self):
        """Create Void tier user for card testing"""
        return BlackUser(
            user_id="void_card_test_001",
            tier=BlackTier.VOID,
            access_level=AccessLevel.EXCLUSIVE,
            portfolio_value=100000000000,
            net_worth=500000000000,
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
    
    @pytest.mark.asyncio
    async def test_card_system_initialization(self, card_system):
        """Test card system initializes correctly"""
        assert len(card_system.cards) >= 0
        assert card_system.emergency_system is not None
        assert card_system.card_auth is not None
        assert card_system.manufacturing is not None
        
    @pytest.mark.asyncio
    async def test_void_card_issuance(self, card_system, void_user):
        """Test issuing Black Card to Void user"""
        delivery_address = {
            "street": "Antilia, Altamount Road",
            "city": "Mumbai",
            "state": "Maharashtra",
            "country": "India",
            "postal_code": "400026"
        }
        
        result = await card_system.issue_black_card(
            void_user, delivery_address, expedited=True
        )
        
        assert result["success"] is True
        assert "card_id" in result
        assert "card_number" in result
        assert "estimated_delivery" in result
        assert "card_specifications" in result
        
        # Check Void tier specifications
        specs = result["card_specifications"]
        assert specs["material"] == "ceramic_carbon_hybrid"
        assert specs["color_scheme"] == "void_transcendent_minimal"
        assert specs["inlay_material"] == "platinum"
        
    @pytest.mark.asyncio
    async def test_obsidian_card_specifications(self, card_system):
        """Test Obsidian tier card specifications"""
        obsidian_user = BlackUser(
            user_id="obsidian_card_test_001",
            tier=BlackTier.OBSIDIAN,
            access_level=AccessLevel.CONCIERGE,
            portfolio_value=30000000000,
            net_worth=80000000000,
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
        
        specs = await card_system._generate_card_specifications(obsidian_user)
        
        assert specs["material"] == "titanium_carbon_composite"
        assert specs["color_scheme"] == "obsidian_gold_imperial"
        assert specs["inlay_material"] == "24k_gold"
        assert specs["weight_grams"] == 18.0
        
    @pytest.mark.asyncio
    async def test_card_activation(self, card_system, void_user):
        """Test Black Card activation process"""
        # First issue a card
        delivery_address = {"city": "Mumbai"}
        issue_result = await card_system.issue_black_card(void_user, delivery_address)
        card_id = issue_result["card_id"]
        
        # Simulate card delivery and activation
        card = card_system.cards[card_id]
        card.status = "shipping"  # Simulate card shipped
        
        activation_data = {
            "biometric_data": "fingerprint_scan_data",
            "device_pairing": "iphone_15_pro_001",
            "security_questions": {"question1": "answer1"}
        }
        
        result = await card_system.activate_card(card_id, activation_data)
        
        assert result["success"] is True
        assert "activation_date" in result
        assert result["card_status"] == "active"
        assert "emergency_number" in result
        assert "concierge_number" in result
        
    @pytest.mark.asyncio
    async def test_medical_emergency_activation(self, card_system, void_user):
        """Test medical emergency activation"""
        # Create active card
        delivery_address = {"city": "Mumbai"}
        issue_result = await card_system.issue_black_card(void_user, delivery_address)
        card_id = issue_result["card_id"]
        
        # Activate card
        card = card_system.cards[card_id]
        card.status = "active"
        
        location_data = {
            "latitude": 19.0760,
            "longitude": 72.8777,
            "address": "Bandra West, Mumbai",
            "accuracy": "high"
        }
        
        result = await card_system.handle_emergency_activation(
            card_id, EmergencyType.MEDICAL, location_data
        )
        
        assert result["success"] is True
        assert "emergency_id" in result
        assert result["response_initiated"] is True
        assert "estimated_response_time" in result
        
        # Void tier should get fastest response
        response_time = result["estimated_response_time"]
        assert "5-10 minutes" in response_time
        
    @pytest.mark.asyncio
    async def test_security_emergency_activation(self, card_system, void_user):
        """Test security emergency activation"""
        # Create and activate card
        delivery_address = {"city": "Mumbai"}
        issue_result = await card_system.issue_black_card(void_user, delivery_address)
        card_id = issue_result["card_id"]
        
        card = card_system.cards[card_id]
        card.status = "active"
        
        location_data = {
            "latitude": 28.6139,
            "longitude": 77.2090,
            "address": "Connaught Place, Delhi"
        }
        
        result = await card_system.handle_emergency_activation(
            card_id, EmergencyType.SECURITY, location_data
        )
        
        assert result["success"] is True
        assert "Armed response team" in result["instructions"]
        
    @pytest.mark.asyncio
    async def test_card_authentication(self, card_system, void_user):
        """Test card-based transaction authentication"""
        # Create and activate card
        delivery_address = {"city": "Mumbai"}
        issue_result = await card_system.issue_black_card(void_user, delivery_address)
        card_id = issue_result["card_id"]
        
        card = card_system.cards[card_id]
        card.status = "active"
        
        transaction_data = {
            "type": "trade_execution",
            "amount": 10000000,  # ₹1 Cr
            "location": {"city": "Mumbai"},
            "biometric_verification": "face_id_confirmed"
        }
        
        result = await card_system.authenticate_card_transaction(card_id, transaction_data)
        
        assert result["authenticated"] is True
        assert "authentication_method" in result
        assert result["confidence"] > 0.9
        
    @pytest.mark.asyncio
    async def test_card_status_retrieval(self, card_system, void_user):
        """Test comprehensive card status retrieval"""
        # Create card
        delivery_address = {"city": "Mumbai"}
        issue_result = await card_system.issue_black_card(void_user, delivery_address)
        card_id = issue_result["card_id"]
        
        status = await card_system.get_card_status(card_id)
        
        assert status["found"] is True
        assert "card_info" in status
        assert "technology_status" in status
        assert "usage_statistics" in status
        assert "security_status" in status
        assert status["card_info"]["tier"] == "VOID"
        
    @pytest.mark.asyncio
    async def test_card_eligibility_validation(self, card_system, void_user):
        """Test card eligibility validation"""
        eligibility = await card_system._validate_card_eligibility(void_user)
        
        assert eligibility["eligible"] is True
        
    @pytest.mark.asyncio
    async def test_ineligible_user_card_request(self, card_system):
        """Test card request from ineligible user"""
        # Create user with unverified compliance
        ineligible_user = BlackUser(
            user_id="ineligible_test_001",
            tier=BlackTier.ONYX,
            access_level=AccessLevel.STANDARD,
            portfolio_value=5000000000,
            net_worth=15000000000,
            risk_appetite="moderate",
            investment_preferences=[],
            invitation_code="ONX2024001",
            invited_by="referral",
            joining_date=datetime.utcnow(),
            tier_progression_date=datetime.utcnow(),
            dedicated_butler="butler_onyx_001",
            butler_contact_preference="chat",
            kyc_level="enhanced",
            aml_score=0.90,
            risk_score=0.20,
            compliance_status="pending",  # Not verified
            trading_hours_preference="market_hours",
            notification_preferences={"market_alerts": True},
            privacy_settings={"public_profile": False},
            is_active=True,
            last_activity=datetime.utcnow(),
            session_count=0,
            total_trades=0,
            total_volume=0.0
        )
        
        eligibility = await card_system._validate_card_eligibility(ineligible_user)
        
        assert eligibility["eligible"] is False
        assert "Compliance verification required" in eligibility["reason"]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])