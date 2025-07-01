"""
GridWorks AI SDK Manager
Unified interface for all AI services with enterprise integration capabilities
"""

import asyncio
import json
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import hashlib
from decimal import Decimal

# Import all AI services
from app.ai_support import UniversalAISupport, TierUXRenderer, WhatsAppSupportHandler
from app.ai_intelligence import AIIntelligenceService, GlobalMorningPulse, UserTier as IntelligenceTier
from app.ai_moderator import AIModerator, ExpertVerificationEngine, GroupManager

logger = logging.getLogger(__name__)


class ServiceType(Enum):
    SUPPORT = "support"
    INTELLIGENCE = "intelligence"
    MODERATOR = "moderator"
    ALL = "all"


class IntegrationType(Enum):
    WHATSAPP_BUSINESS = "whatsapp_business"
    REST_API = "rest_api"
    WEBHOOK = "webhook"
    SDK_EMBEDDED = "sdk_embedded"


@dataclass
class ClientConfiguration:
    """Client configuration for SDK integration"""
    client_id: str
    client_name: str
    api_key: str
    services: List[ServiceType]
    integration_type: IntegrationType
    whatsapp_config: Optional[Dict[str, Any]] = None
    webhook_urls: Optional[Dict[str, str]] = None
    custom_settings: Optional[Dict[str, Any]] = None
    tier_mapping: Optional[Dict[str, str]] = None
    rate_limits: Optional[Dict[str, int]] = None
    billing_config: Optional[Dict[str, Any]] = None


@dataclass
class APIResponse:
    """Standardized API response structure"""
    success: bool
    service: str
    data: Any
    error: Optional[str] = None
    response_time: Optional[float] = None
    request_id: Optional[str] = None
    billing_info: Optional[Dict[str, Any]] = None


class GridWorksSDK:
    """Main SDK manager class for all GridWorks AI services"""
    
    def __init__(self, client_config: ClientConfiguration):
        self.client_config = client_config
        self.client_id = client_config.client_id
        
        # Initialize service instances
        self.support_service = None
        self.intelligence_service = None
        self.moderator_service = None
        
        # Request tracking
        self.request_count = 0
        self.billing_tracker = {}
        
        # Rate limiting
        self.rate_limiter = RateLimiter(client_config.rate_limits or {})
        
        logger.info(f"Initialized GridWorks SDK for client: {client_config.client_name}")
    
    async def initialize_services(self) -> Dict[str, bool]:
        """Initialize requested AI services"""
        
        initialization_status = {}
        
        try:
            # Initialize AI Support Service
            if ServiceType.SUPPORT in self.client_config.services or ServiceType.ALL in self.client_config.services:
                await self._initialize_support_service()
                initialization_status["support"] = True
                logger.info("AI Support Service initialized")
            
            # Initialize AI Intelligence Service
            if ServiceType.INTELLIGENCE in self.client_config.services or ServiceType.ALL in self.client_config.services:
                await self._initialize_intelligence_service()
                initialization_status["intelligence"] = True
                logger.info("AI Intelligence Service initialized")
            
            # Initialize AI Moderator Service
            if ServiceType.MODERATOR in self.client_config.services or ServiceType.ALL in self.client_config.services:
                await self._initialize_moderator_service()
                initialization_status["moderator"] = True
                logger.info("AI Moderator Service initialized")
            
            return initialization_status
            
        except Exception as e:
            logger.error(f"Service initialization failed: {e}")
            raise
    
    async def _initialize_support_service(self):
        """Initialize AI Support Service"""
        
        self.support_service = UniversalAISupport()
        
        # Configure WhatsApp integration if specified
        if self.client_config.whatsapp_config:
            self.whatsapp_handler = WhatsAppSupportHandler(
                self.client_config.whatsapp_config
            )
    
    async def _initialize_intelligence_service(self):
        """Initialize AI Intelligence Service"""
        
        self.intelligence_service = AIIntelligenceService()
        
        # Configure custom data sources if specified
        custom_settings = self.client_config.custom_settings or {}
        if "data_sources" in custom_settings:
            # In production, would configure additional data sources
            pass
    
    async def _initialize_moderator_service(self):
        """Initialize AI Moderator Service"""
        
        self.group_manager = GroupManager()
        self.expert_verifier = ExpertVerificationEngine()
    
    # =============================================================================
    # UNIFIED API METHODS
    # =============================================================================
    
    async def process_request(
        self, 
        service: str, 
        action: str, 
        data: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> APIResponse:
        """Unified request processing for all services"""
        
        start_time = datetime.now()
        request_id = self._generate_request_id()
        
        try:
            # Rate limiting check
            if not await self.rate_limiter.check_rate_limit(self.client_id, service):
                return APIResponse(
                    success=False,
                    service=service,
                    data=None,
                    error="Rate limit exceeded",
                    request_id=request_id
                )
            
            # Route to appropriate service
            if service == "support":
                result = await self._handle_support_request(action, data, user_context)
            elif service == "intelligence":
                result = await self._handle_intelligence_request(action, data, user_context)
            elif service == "moderator":
                result = await self._handle_moderator_request(action, data, user_context)
            else:
                return APIResponse(
                    success=False,
                    service=service,
                    data=None,
                    error=f"Unknown service: {service}",
                    request_id=request_id
                )
            
            # Calculate response time
            response_time = (datetime.now() - start_time).total_seconds()
            
            # Track billing
            billing_info = await self._track_billing(service, action, response_time)
            
            return APIResponse(
                success=True,
                service=service,
                data=result,
                response_time=response_time,
                request_id=request_id,
                billing_info=billing_info
            )
            
        except Exception as e:
            logger.error(f"Request processing failed: {e}")
            response_time = (datetime.now() - start_time).total_seconds()
            
            return APIResponse(
                success=False,
                service=service,
                data=None,
                error=str(e),
                response_time=response_time,
                request_id=request_id
            )
    
    # =============================================================================
    # AI SUPPORT SERVICE METHODS
    # =============================================================================
    
    async def _handle_support_request(
        self, 
        action: str, 
        data: Dict[str, Any],
        user_context: Optional[Dict[str, Any]]
    ) -> Any:
        """Handle AI Support service requests"""
        
        if not self.support_service:
            raise ValueError("AI Support service not initialized")
        
        if action == "query":
            return await self._handle_support_query(data, user_context)
        elif action == "escalate":
            return await self._handle_support_escalation(data, user_context)
        elif action == "get_history":
            return await self._get_support_history(data, user_context)
        else:
            raise ValueError(f"Unknown support action: {action}")
    
    async def _handle_support_query(
        self, 
        data: Dict[str, Any], 
        user_context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Handle support query"""
        
        from app.ai_support.models import SupportMessage, UserContext, SupportTier
        
        # Convert data to support message
        message = SupportMessage(
            message_id=data.get("message_id", self._generate_request_id()),
            user_id=data["user_id"],
            message=data["message"],
            timestamp=datetime.now(timezone.utc),
            user_tier=SupportTier(data.get("user_tier", "lite")),
            language=data.get("language", "english"),
            channel=data.get("channel", "api")
        )
        
        # Create user context
        context = UserContext(
            user_id=data["user_id"],
            tier=SupportTier(data.get("user_tier", "lite")),
            balance=user_context.get("balance", 0) if user_context else 0,
            recent_orders=user_context.get("recent_orders", []) if user_context else [],
            preferences=user_context.get("preferences", {}) if user_context else {}
        )
        
        # Process support request
        response = await self.support_service.process_support_request(message, context)
        
        # Convert to dict for JSON serialization
        result = {
            "message": response.message,
            "actions": response.actions,
            "escalate": response.escalate,
            "confidence": response.confidence,
            "response_time": response.response_time
        }
        
        # Handle WhatsApp delivery if configured
        if self.client_config.whatsapp_config and data.get("deliver_via_whatsapp"):
            await self._deliver_via_whatsapp(data["user_id"], result)
        
        return result
    
    async def _deliver_via_whatsapp(self, user_id: str, response: Dict[str, Any]):
        """Deliver response via WhatsApp"""
        
        if hasattr(self, 'whatsapp_handler'):
            await self.whatsapp_handler.send_message(
                user_id=user_id,
                message=response["message"],
                actions=response.get("actions", [])
            )
    
    # =============================================================================
    # AI INTELLIGENCE SERVICE METHODS
    # =============================================================================
    
    async def _handle_intelligence_request(
        self, 
        action: str, 
        data: Dict[str, Any],
        user_context: Optional[Dict[str, Any]]
    ) -> Any:
        """Handle AI Intelligence service requests"""
        
        if not self.intelligence_service:
            raise ValueError("AI Intelligence service not initialized")
        
        if action == "morning_pulse":
            return await self._get_morning_pulse(data, user_context)
        elif action == "custom_alert":
            return await self._get_custom_alert(data, user_context)
        elif action == "market_analysis":
            return await self._get_market_analysis(data, user_context)
        else:
            raise ValueError(f"Unknown intelligence action: {action}")
    
    async def _get_morning_pulse(
        self, 
        data: Dict[str, Any], 
        user_context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Get morning pulse report"""
        
        user_tier = IntelligenceTier(data.get("user_tier", "pro"))
        user_id = data["user_id"]
        
        # Generate morning pulse
        pulse_report = await self.intelligence_service.generate_morning_pulse(user_id, user_tier)
        
        # Convert to serializable format
        result = {
            "timestamp": pulse_report.timestamp.isoformat(),
            "global_triggers": pulse_report.global_triggers,
            "india_correlations": pulse_report.india_correlations,
            "trade_ideas": [asdict(idea) for idea in pulse_report.trade_ideas],
            "risk_alerts": pulse_report.risk_alerts,
            "institutional_flows": pulse_report.institutional_flows,
            "voice_note_url": pulse_report.voice_note_url,
            "text_summary": pulse_report.text_summary,
            "user_tier": pulse_report.user_tier.value
        }
        
        # Handle delivery preferences
        delivery_channels = data.get("delivery_channels", ["api"])
        if "whatsapp" in delivery_channels and self.client_config.whatsapp_config:
            await self._deliver_pulse_via_whatsapp(user_id, result)
        
        return result
    
    async def _deliver_pulse_via_whatsapp(self, user_id: str, pulse_data: Dict[str, Any]):
        """Deliver morning pulse via WhatsApp"""
        
        # Create WhatsApp-friendly summary
        summary = f"🌅 Morning Pulse Alert!\n\n"
        
        if pulse_data["global_triggers"]:
            trigger = pulse_data["global_triggers"][0]
            summary += f"📊 {trigger.get('market', 'Global')}: {trigger.get('change', 0):+.1f}%\n"
        
        if pulse_data["trade_ideas"]:
            idea = pulse_data["trade_ideas"][0]
            summary += f"💡 {idea['action']} {idea['symbol']} @ ₹{idea['entry_price']}\n"
        
        summary += f"\n📱 Full report: {pulse_data.get('voice_note_url', 'Available in app')}"
        
        if hasattr(self, 'whatsapp_handler'):
            await self.whatsapp_handler.send_message(
                user_id=user_id,
                message=summary
            )
    
    # =============================================================================
    # AI MODERATOR SERVICE METHODS
    # =============================================================================
    
    async def _handle_moderator_request(
        self, 
        action: str, 
        data: Dict[str, Any],
        user_context: Optional[Dict[str, Any]]
    ) -> Any:
        """Handle AI Moderator service requests"""
        
        if not hasattr(self, 'group_manager'):
            raise ValueError("AI Moderator service not initialized")
        
        if action == "moderate_message":
            return await self._moderate_message(data, user_context)
        elif action == "verify_expert":
            return await self._verify_expert(data, user_context)
        elif action == "get_group_analytics":
            return await self._get_group_analytics(data, user_context)
        elif action == "create_group":
            return await self._create_moderated_group(data, user_context)
        else:
            raise ValueError(f"Unknown moderator action: {action}")
    
    async def _moderate_message(
        self, 
        data: Dict[str, Any], 
        user_context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Moderate a group message"""
        
        from app.ai_moderator.moderator_engine import GroupMessage
        
        # Get or create group moderator
        group_id = data["group_id"]
        moderator = await self.group_manager.get_group_moderator(group_id)
        
        if not moderator:
            # Create group with default config
            group_config = {
                "group_id": group_id,
                "name": f"Group {group_id}",
                "max_members": 50,
                "language": data.get("language", "english")
            }
            moderator = await self.group_manager.create_group(group_config)
        
        # Create message object
        message = GroupMessage(
            message_id=data["message_id"],
            user_id=data["user_id"],
            username=data.get("username", "User"),
            content=data["content"],
            timestamp=datetime.fromisoformat(data.get("timestamp", datetime.now().isoformat())),
            group_id=group_id,
            language=data.get("language", "english")
        )
        
        # Process message
        result = await moderator.process_message(message)
        
        return result
    
    async def _verify_expert(
        self, 
        data: Dict[str, Any], 
        user_context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Verify expert credentials"""
        
        expert_id = data["expert_id"]
        credentials = data["credentials"]
        
        # Verify expert
        verification_result = await self.expert_verifier.verify_expert(expert_id, credentials)
        
        return verification_result
    
    # =============================================================================
    # BILLING AND ANALYTICS
    # =============================================================================
    
    async def _track_billing(self, service: str, action: str, response_time: float) -> Dict[str, Any]:
        """Track billing information"""
        
        self.request_count += 1
        
        # Get billing config
        billing_config = self.client_config.billing_config or {}
        billing_model = billing_config.get("model", "per_request")
        
        if billing_model == "per_request":
            cost = self._calculate_per_request_cost(service, action)
        elif billing_model == "monthly_flat":
            cost = 0  # Flat rate billed separately
        else:
            cost = 0
        
        # Track in client's billing
        if self.client_id not in self.billing_tracker:
            self.billing_tracker[self.client_id] = {
                "total_requests": 0,
                "total_cost": 0,
                "services_used": set(),
                "last_request": None
            }
        
        self.billing_tracker[self.client_id]["total_requests"] += 1
        self.billing_tracker[self.client_id]["total_cost"] += cost
        self.billing_tracker[self.client_id]["services_used"].add(service)
        self.billing_tracker[self.client_id]["last_request"] = datetime.now()
        
        return {
            "cost": cost,
            "billing_model": billing_model,
            "total_requests_today": self.request_count,
            "response_time": response_time
        }
    
    def _calculate_per_request_cost(self, service: str, action: str) -> float:
        """Calculate cost per request"""
        
        # Default pricing (in INR)
        pricing = {
            "support": {
                "query": 0.50,
                "escalate": 1.00,
                "get_history": 0.25
            },
            "intelligence": {
                "morning_pulse": 2.00,
                "custom_alert": 1.50,
                "market_analysis": 3.00
            },
            "moderator": {
                "moderate_message": 0.30,
                "verify_expert": 10.00,
                "get_group_analytics": 1.00,
                "create_group": 5.00
            }
        }
        
        return pricing.get(service, {}).get(action, 1.00)
    
    def _generate_request_id(self) -> str:
        """Generate unique request ID"""
        
        timestamp = datetime.now().isoformat()
        unique_string = f"{self.client_id}_{timestamp}_{self.request_count}"
        return hashlib.md5(unique_string.encode()).hexdigest()[:12]
    
    # =============================================================================
    # CLIENT MANAGEMENT METHODS
    # =============================================================================
    
    async def get_client_analytics(self) -> Dict[str, Any]:
        """Get comprehensive client analytics"""
        
        client_data = self.billing_tracker.get(self.client_id, {})
        
        return {
            "client_id": self.client_id,
            "client_name": self.client_config.client_name,
            "services_configured": [service.value for service in self.client_config.services],
            "integration_type": self.client_config.integration_type.value,
            "usage_statistics": {
                "total_requests": client_data.get("total_requests", 0),
                "total_cost": client_data.get("total_cost", 0),
                "services_used": list(client_data.get("services_used", [])),
                "last_request": client_data.get("last_request", {}).isoformat() if client_data.get("last_request") else None
            },
            "rate_limits": self.rate_limiter.get_current_usage(self.client_id),
            "service_health": await self._check_service_health()
        }
    
    async def _check_service_health(self) -> Dict[str, str]:
        """Check health of all services"""
        
        health_status = {}
        
        if self.support_service:
            health_status["support"] = "healthy"
        
        if self.intelligence_service:
            health_status["intelligence"] = "healthy"
        
        if hasattr(self, 'group_manager'):
            health_status["moderator"] = "healthy"
        
        return health_status
    
    async def update_client_config(self, updates: Dict[str, Any]) -> bool:
        """Update client configuration"""
        
        try:
            # Update allowed fields
            allowed_updates = ["custom_settings", "rate_limits", "billing_config"]
            
            for key, value in updates.items():
                if key in allowed_updates:
                    setattr(self.client_config, key, value)
            
            # Reinitialize services if needed
            if "custom_settings" in updates:
                await self.initialize_services()
            
            return True
            
        except Exception as e:
            logger.error(f"Client config update failed: {e}")
            return False


class RateLimiter:
    """Rate limiting for API requests"""
    
    def __init__(self, rate_limits: Dict[str, int]):
        self.rate_limits = rate_limits
        self.request_counts = {}
        self.last_reset = datetime.now()
    
    async def check_rate_limit(self, client_id: str, service: str) -> bool:
        """Check if request is within rate limits"""
        
        # Reset counts every hour
        now = datetime.now()
        if now - self.last_reset > timedelta(hours=1):
            self.request_counts = {}
            self.last_reset = now
        
        # Get limits for service
        service_limit = self.rate_limits.get(service, 1000)  # Default 1000/hour
        
        # Check current count
        key = f"{client_id}_{service}"
        current_count = self.request_counts.get(key, 0)
        
        if current_count >= service_limit:
            return False
        
        # Increment count
        self.request_counts[key] = current_count + 1
        return True
    
    def get_current_usage(self, client_id: str) -> Dict[str, Any]:
        """Get current usage statistics"""
        
        usage = {}
        
        for key, count in self.request_counts.items():
            if key.startswith(f"{client_id}_"):
                service = key.split("_", 1)[1]
                limit = self.rate_limits.get(service, 1000)
                usage[service] = {
                    "current": count,
                    "limit": limit,
                    "remaining": limit - count
                }
        
        return usage


# =============================================================================
# CONVENIENCE CLASSES FOR SPECIFIC INTEGRATIONS
# =============================================================================

class WhatsAppSDK(GridWorksSDK):
    """Specialized SDK for WhatsApp Business integrations"""
    
    def __init__(self, whatsapp_config: Dict[str, Any], services: List[ServiceType]):
        client_config = ClientConfiguration(
            client_id=whatsapp_config["business_account_id"],
            client_name=whatsapp_config.get("business_name", "WhatsApp Business"),
            api_key=whatsapp_config["access_token"],
            services=services,
            integration_type=IntegrationType.WHATSAPP_BUSINESS,
            whatsapp_config=whatsapp_config
        )
        
        super().__init__(client_config)
    
    async def handle_whatsapp_webhook(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming WhatsApp webhook"""
        
        # Extract message data
        message_data = self._extract_message_data(webhook_data)
        
        if message_data["type"] == "support_query":
            return await self.process_request(
                service="support",
                action="query",
                data=message_data["data"]
            )
        elif message_data["type"] == "group_message":
            return await self.process_request(
                service="moderator",
                action="moderate_message",
                data=message_data["data"]
            )
        else:
            return {"success": False, "error": "Unknown message type"}
    
    def _extract_message_data(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract structured data from WhatsApp webhook"""
        
        # Simplified extraction (in production, would handle full WhatsApp webhook format)
        return {
            "type": "support_query",
            "data": {
                "user_id": webhook_data.get("from", "unknown"),
                "message": webhook_data.get("text", ""),
                "message_id": webhook_data.get("id", ""),
                "user_tier": "lite"
            }
        }


class BrokerSDK(GridWorksSDK):
    """Specialized SDK for broker integrations"""
    
    def __init__(self, broker_config: Dict[str, Any]):
        client_config = ClientConfiguration(
            client_id=broker_config["broker_id"],
            client_name=broker_config["broker_name"],
            api_key=broker_config["api_key"],
            services=[ServiceType.SUPPORT, ServiceType.INTELLIGENCE],
            integration_type=IntegrationType.REST_API,
            tier_mapping=broker_config.get("tier_mapping", {}),
            billing_config=broker_config.get("billing_config", {})
        )
        
        super().__init__(client_config)
    
    async def handle_customer_query(
        self, 
        user_id: str, 
        query: str, 
        user_tier: str = "lite"
    ) -> Dict[str, Any]:
        """Handle customer support query"""
        
        return await self.process_request(
            service="support",
            action="query",
            data={
                "user_id": user_id,
                "message": query,
                "user_tier": user_tier,
                "channel": "broker_app"
            }
        )
    
    async def get_daily_market_intelligence(self, user_ids: List[str]) -> List[Dict[str, Any]]:
        """Get daily market intelligence for multiple users"""
        
        results = []
        
        for user_id in user_ids:
            result = await self.process_request(
                service="intelligence",
                action="morning_pulse",
                data={
                    "user_id": user_id,
                    "user_tier": "pro",
                    "delivery_channels": ["api"]
                }
            )
            results.append(result)
        
        return results


class TradingGroupSDK(GridWorksSDK):
    """Specialized SDK for trading group management"""
    
    def __init__(self, group_config: Dict[str, Any]):
        client_config = ClientConfiguration(
            client_id=group_config["group_id"],
            client_name=group_config["group_name"],
            api_key=group_config["api_key"],
            services=[ServiceType.MODERATOR],
            integration_type=IntegrationType.WEBHOOK,
            webhook_urls=group_config.get("webhook_urls", {}),
            custom_settings=group_config.get("moderation_settings", {})
        )
        
        super().__init__(client_config)
    
    async def setup_expert_group(
        self, 
        expert_id: str, 
        group_settings: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Set up a new expert-led group"""
        
        # First verify the expert
        verification_result = await self.process_request(
            service="moderator",
            action="verify_expert",
            data={
                "expert_id": expert_id,
                "credentials": group_settings.get("expert_credentials", [])
            }
        )
        
        if verification_result.success and verification_result.data["overall_status"] == "approved":
            # Create the group
            group_result = await self.process_request(
                service="moderator",
                action="create_group",
                data={
                    "group_id": f"expert_{expert_id}_{datetime.now().strftime('%Y%m%d')}",
                    "expert_id": expert_id,
                    "settings": group_settings
                }
            )
            
            return {
                "success": True,
                "expert_verification": verification_result.data,
                "group_creation": group_result.data
            }
        else:
            return {
                "success": False,
                "error": "Expert verification failed",
                "verification_details": verification_result.data
            }


# =============================================================================
# FACTORY FUNCTIONS
# =============================================================================

def create_whatsapp_sdk(whatsapp_config: Dict[str, Any]) -> WhatsAppSDK:
    """Factory function to create WhatsApp SDK"""
    
    return WhatsAppSDK(
        whatsapp_config=whatsapp_config,
        services=[ServiceType.SUPPORT, ServiceType.INTELLIGENCE, ServiceType.MODERATOR]
    )


def create_broker_sdk(broker_config: Dict[str, Any]) -> BrokerSDK:
    """Factory function to create Broker SDK"""
    
    return BrokerSDK(broker_config)


def create_trading_group_sdk(group_config: Dict[str, Any]) -> TradingGroupSDK:
    """Factory function to create Trading Group SDK"""
    
    return TradingGroupSDK(group_config)


def create_enterprise_sdk(enterprise_config: Dict[str, Any]) -> GridWorksSDK:
    """Factory function to create full enterprise SDK"""
    
    client_config = ClientConfiguration(
        client_id=enterprise_config["enterprise_id"],
        client_name=enterprise_config["enterprise_name"],
        api_key=enterprise_config["api_key"],
        services=[ServiceType.ALL],
        integration_type=IntegrationType(enterprise_config["integration_type"]),
        whatsapp_config=enterprise_config.get("whatsapp_config"),
        webhook_urls=enterprise_config.get("webhook_urls"),
        custom_settings=enterprise_config.get("custom_settings"),
        tier_mapping=enterprise_config.get("tier_mapping"),
        rate_limits=enterprise_config.get("rate_limits"),
        billing_config=enterprise_config.get("billing_config")
    )
    
    return GridWorksSDK(client_config)