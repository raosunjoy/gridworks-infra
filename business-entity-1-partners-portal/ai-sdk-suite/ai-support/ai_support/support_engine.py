"""
GridWorks AI Support Engine - Main Integration Module
Complete AI support system with tier-specific UX and human escalation
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from .models import SupportMessage, SupportTier, UserContext, MessageType
from .universal_engine import UniversalAISupport
from .tier_ux import TierUXRenderer, WhatsAppUXFormatter
from .whatsapp_handler import WhatsAppSupportHandler
from .escalation_system import EscalationSystem, EscalationReason
from .zk_proof_engine import ZKSupportIntegration
from .performance_monitor import PerformanceMonitor, MetricType

logger = logging.getLogger(__name__)


class GridWorksAISupportEngine:
    """
    Complete AI Support Engine for GridWorks
    
    Features:
    - Universal AI that serves all tiers
    - Tier-specific UX differentiation  
    - Human escalation with priority routing
    - ZK proof transparency
    - Real-time performance monitoring
    - WhatsApp-first experience
    """
    
    def __init__(self):
        # Core components
        self.ai_engine = UniversalAISupport()
        self.ux_renderer = TierUXRenderer()
        self.whatsapp_handler = WhatsAppSupportHandler()
        self.escalation_system = EscalationSystem()
        self.zk_integration = ZKSupportIntegration()
        self.performance_monitor = PerformanceMonitor()
        
        # System status
        self.is_running = False
        
        logger.info("GridWorks AI Support Engine initialized")
    
    async def start(self):
        """Start the AI support engine"""
        
        try:
            self.is_running = True
            
            # Start background services
            logger.info("Starting AI Support Engine services...")
            
            # Start WhatsApp message processor
            # asyncio.create_task(self._start_whatsapp_processor())
            
            # Start performance monitoring
            # asyncio.create_task(self._start_performance_monitoring())
            
            logger.info("AI Support Engine started successfully")
            
        except Exception as e:
            logger.error(f"Engine startup failed: {e}")
            raise
    
    async def stop(self):
        """Stop the AI support engine"""
        
        self.is_running = False
        logger.info("AI Support Engine stopped")
    
    async def process_support_message(
        self,
        phone: str,
        message_text: str,
        message_type: str = "text",
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Main entry point for processing support messages
        
        Args:
            phone: User's phone number
            message_text: The support message
            message_type: Type of message (text, voice, image)
            language: Detected language
            
        Returns:
            Complete support response with tier-specific UX
        """
        
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Step 1: Get user context and create support message
            user_context = await self._get_user_context(phone)
            if not user_context:
                return await self._create_error_response("User not found")
            
            support_message = SupportMessage(
                id="",  # Will be generated
                user_id=user_context.user_id,
                phone=phone,
                message=message_text,
                message_type=MessageType(message_type),
                language=language,
                timestamp=datetime.utcnow(),
                user_tier=user_context.tier,
                priority=await self._calculate_priority(message_text, user_context.tier)
            )
            
            # Step 2: Process with AI engine
            ai_response = await self.ai_engine.process_support_request(
                support_message, user_context
            )
            
            # Step 3: Check if escalation needed
            if ai_response.escalate:
                escalation_result = await self.escalation_system.escalate_to_human(
                    support_message,
                    {"ai_response": ai_response.message},
                    EscalationReason.LOW_CONFIDENCE
                )
                
                # Update response with escalation info
                ai_response.message = f"Connecting you to our support team. {escalation_result.get('estimated_response', '')}"
            
            # Step 4: Render tier-specific UX
            tier_response = await self.ux_renderer.render_tier_response(
                ai_response, support_message, user_context
            )
            
            # Step 5: Format for WhatsApp
            whatsapp_message = await WhatsAppUXFormatter.format_for_whatsapp(tier_response)
            
            # Step 6: Generate ZK proof for transparency
            zk_proof_result = await self.zk_integration.create_support_proof(
                ticket_id=support_message.id or f"TM{int(asyncio.get_event_loop().time())}",
                user_id=user_context.user_id,
                original_message=message_text,
                ai_response=ai_response.message,
                resolution_summary=tier_response["message"],
                response_time=asyncio.get_event_loop().time() - start_time
            )
            
            # Step 7: Record performance metrics
            processing_time = (asyncio.get_event_loop().time() - start_time) * 1000  # ms
            await self.performance_monitor.record_metric(
                MetricType.RESPONSE_TIME,
                user_context.tier,
                processing_time,
                {
                    "escalated": ai_response.escalate,
                    "confidence": ai_response.confidence,
                    "language": language
                }
            )
            
            # Step 8: Create final response
            final_response = {
                "success": True,
                "message": whatsapp_message,
                "tier_response": tier_response,
                "zk_proof": zk_proof_result,
                "performance": {
                    "processing_time_ms": processing_time,
                    "tier": user_context.tier.value,
                    "escalated": ai_response.escalate,
                    "confidence": ai_response.confidence
                }
            }
            
            logger.info(f"Support processed: {user_context.tier.value} | {processing_time:.1f}ms")
            return final_response
            
        except Exception as e:
            logger.error(f"Support processing failed: {e}")
            return await self._create_error_response(str(e))
    
    async def _get_user_context(self, phone: str) -> Optional[UserContext]:
        """Get user context from phone number"""
        
        # This would integrate with user database in production
        # For now, return mock data based on phone pattern
        
        if phone.endswith("0001"):
            return UserContext(
                user_id="user_black_001",
                tier=SupportTier.BLACK,
                name="Rajesh Gupta",
                portfolio_value=5000000,
                recent_orders=[
                    {"id": "12345", "symbol": "TCS", "quantity": 100, "status": "failed"},
                    {"id": "12346", "symbol": "RELIANCE", "quantity": 50, "status": "completed"}
                ],
                balance=100000,
                kyc_status="verified",
                preferred_language="en",
                trading_history={"total_trades": 500, "success_rate": 98},
                risk_profile="aggressive"
            )
        elif phone.endswith("0002"):
            return UserContext(
                user_id="user_elite_001",
                tier=SupportTier.ELITE,
                name="Priya Sharma",
                portfolio_value=1500000,
                recent_orders=[
                    {"id": "12347", "symbol": "INFY", "quantity": 20, "status": "pending"}
                ],
                balance=50000,
                kyc_status="verified",
                preferred_language="en",
                trading_history={"total_trades": 200, "success_rate": 96},
                risk_profile="moderate"
            )
        elif phone.endswith("0003"):
            return UserContext(
                user_id="user_pro_001",
                tier=SupportTier.PRO,
                name="Amit Kumar",
                portfolio_value=300000,
                recent_orders=[
                    {"id": "12348", "symbol": "HDFC", "quantity": 10, "status": "completed"}
                ],
                balance=15000,
                kyc_status="verified",
                preferred_language="hi",
                trading_history={"total_trades": 50, "success_rate": 94},
                risk_profile="moderate"
            )
        else:
            return UserContext(
                user_id="user_lite_001",
                tier=SupportTier.LITE,
                name="User",
                portfolio_value=50000,
                recent_orders=[
                    {"id": "12349", "symbol": "SBI", "quantity": 5, "status": "failed"}
                ],
                balance=5000,
                kyc_status="pending",
                preferred_language="hi",
                trading_history={"total_trades": 10, "success_rate": 90},
                risk_profile="conservative"
            )
    
    async def _calculate_priority(self, message: str, tier: SupportTier) -> int:
        """Calculate message priority"""
        
        # Base priority by tier
        tier_priority = {
            SupportTier.BLACK: 5,
            SupportTier.ELITE: 4,
            SupportTier.PRO: 3,
            SupportTier.LITE: 2
        }
        
        base_priority = tier_priority[tier]
        
        # Boost for urgent keywords
        urgent_keywords = ["stuck", "money", "lost", "error", "failed", "urgent", "help"]
        if any(keyword in message.lower() for keyword in urgent_keywords):
            base_priority = min(5, base_priority + 1)
        
        return base_priority
    
    async def _create_error_response(self, error: str) -> Dict[str, Any]:
        """Create error response"""
        
        return {
            "success": False,
            "error": error,
            "message": "I'm experiencing technical difficulties. Our team will help you shortly.",
            "escalated": True
        }
    
    async def get_performance_dashboard(self) -> Dict[str, Any]:
        """Get real-time performance dashboard"""
        
        return await self.performance_monitor.get_performance_dashboard()
    
    async def verify_support_proof(self, proof_id: str, user_data: Dict[str, str] = None) -> Dict[str, Any]:
        """Verify ZK proof for support interaction"""
        
        return await self.zk_integration.verify_support_claim(proof_id, user_data)


# Example usage and testing
async def demo_support_engine():
    """Demonstrate the AI support engine capabilities"""
    
    print("🚀 GridWorks AI Support Engine Demo")
    print("=" * 50)
    
    # Initialize engine
    engine = GridWorksAISupportEngine()
    await engine.start()
    
    # Test scenarios for different tiers
    test_scenarios = [
        {
            "phone": "+919876540001",  # BLACK tier
            "message": "My TCS order failed, need immediate help",
            "expected_tier": "BLACK"
        },
        {
            "phone": "+919876540002",  # ELITE tier
            "message": "Portfolio analysis required for my INFY position",
            "expected_tier": "ELITE"
        },
        {
            "phone": "+919876540003",  # PRO tier
            "message": "HDFC order status check karna hai",
            "expected_tier": "PRO",
            "language": "hi"
        },
        {
            "phone": "+919876540004",  # LITE tier
            "message": "SBI order kyun fail hua?",
            "expected_tier": "LITE",
            "language": "hi"
        }
    ]
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n📱 Test Scenario {i}: {scenario['expected_tier']} Tier")
        print("-" * 30)
        
        # Process support message
        result = await engine.process_support_message(
            phone=scenario["phone"],
            message_text=scenario["message"],
            language=scenario.get("language", "en")
        )
        
        if result["success"]:
            print(f"✅ Response ({result['performance']['processing_time_ms']:.1f}ms):")
            print(f"Tier: {result['performance']['tier']}")
            print(f"Escalated: {result['performance']['escalated']}")
            print(f"Confidence: {result['performance']['confidence']:.2f}")
            print(f"ZK Proof: {result['zk_proof']['proof_generated']}")
            print("\nFormatted Response:")
            print(result["message"])
        else:
            print(f"❌ Error: {result['error']}")
    
    # Show performance dashboard
    print(f"\n📊 Performance Dashboard")
    print("-" * 30)
    dashboard = await engine.get_performance_dashboard()
    
    for tier, sla_data in dashboard.get("sla_status", {}).items():
        print(f"\n{tier.upper()} Tier SLA Status:")
        for metric, status in sla_data.items():
            if status:
                print(f"  {metric}: {status['current']} ({status['status']})")
    
    print(f"\nSystem Health: {dashboard.get('system_health', {}).get('system_status', 'unknown')}")
    
    # Stop engine
    await engine.stop()
    print("\n✅ Demo completed!")


if __name__ == "__main__":
    # Run demo
    asyncio.run(demo_support_engine())