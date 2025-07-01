"""
GridWorks Black Market Butler
AI-powered concierge for ultra-premium trading experience
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import openai
from dataclasses import dataclass

from .models import BlackUser, BlackTier, MarketButlerProfile

logger = logging.getLogger(__name__)


@dataclass
class ButlerConversation:
    """Butler conversation context"""
    user_id: str
    butler_id: str
    conversation_id: str
    context: Dict[str, Any]
    conversation_history: List[Dict[str, Any]]
    created_at: datetime
    last_activity: datetime
    status: str  # active, archived, escalated


@dataclass
class MarketOpportunity:
    """Market opportunity identified by butler"""
    opportunity_id: str
    title: str
    description: str
    asset_class: str
    symbol: str
    recommendation: str  # buy, sell, hold, watch
    confidence: float
    time_horizon: str
    entry_price: Optional[float]
    target_price: Optional[float]
    stop_loss: Optional[float]
    rationale: str
    risk_level: str
    position_size_suggestion: str
    urgency: str  # low, medium, high, critical
    expires_at: datetime


class MarketButler:
    """
    AI-powered market butler for GridWorks Black users
    
    Butler Tiers:
    - Onyx Butler: Professional advisor with market insights
    - Obsidian Butler: Expert strategist with institutional access
    - Void Butler: Elite concierge with billionaire network access
    """
    
    def __init__(self):
        # Butler profiles by tier
        self.butler_profiles: Dict[str, MarketButlerProfile] = {}
        
        # Active conversations
        self.active_conversations: Dict[str, ButlerConversation] = {}
        
        # Market intelligence
        self.market_intelligence = MarketIntelligenceEngine()
        
        # Portfolio analytics
        self.portfolio_analyzer = PortfolioAnalyzer()
        
        # Communication channels
        self.communication_manager = CommunicationManager()
        
        # Performance tracking
        self.performance_tracker = ButlerPerformanceTracker()
        
        logger.info("Market Butler system initialized")
    
    async def start_butler_services(self):
        """Start butler services"""
        
        try:
            # Initialize butler profiles
            await self._initialize_butler_profiles()
            
            # Start background services
            asyncio.create_task(self._start_market_monitoring())
            asyncio.create_task(self._start_opportunity_scanning())
            asyncio.create_task(self._start_performance_monitoring())
            
            logger.info("Butler services started")
            
        except Exception as e:
            logger.error(f"Butler service startup failed: {e}")
            raise
    
    async def connect_user_butler(
        self,
        user_id: str,
        butler_id: str
    ) -> Dict[str, Any]:
        """Connect user to their dedicated butler"""
        
        try:
            butler_profile = self.butler_profiles.get(butler_id)
            if not butler_profile:
                return {"success": False, "error": "Butler not found"}
            
            # Create conversation context
            conversation_id = f"butler_{user_id}_{int(datetime.utcnow().timestamp())}"
            
            conversation = ButlerConversation(
                user_id=user_id,
                butler_id=butler_id,
                conversation_id=conversation_id,
                context=await self._build_user_context(user_id),
                conversation_history=[],
                created_at=datetime.utcnow(),
                last_activity=datetime.utcnow(),
                status="active"
            )
            
            self.active_conversations[conversation_id] = conversation
            
            # Generate welcome message
            welcome_message = await self._generate_butler_welcome(
                user_id, butler_profile
            )
            
            return {
                "success": True,
                "conversation_id": conversation_id,
                "butler_profile": {
                    "name": butler_profile.name,
                    "specializations": butler_profile.specializations,
                    "experience_years": butler_profile.experience_years,
                    "satisfaction_rating": butler_profile.client_satisfaction
                },
                "welcome_message": welcome_message,
                "communication_channels": ["chat", "voice", "video"]
            }
            
        except Exception as e:
            logger.error(f"Butler connection failed: {e}")
            return {"success": False, "error": "Butler connection failed"}
    
    async def handle_service_request(
        self,
        butler_id: str,
        user_id: str,
        service_request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle butler service request"""
        
        try:
            request_type = service_request.get("type")
            message = service_request.get("message", "")
            
            # Get butler profile
            butler_profile = self.butler_profiles.get(butler_id)
            if not butler_profile:
                return {"success": False, "error": "Butler not available"}
            
            # Find or create conversation
            conversation = await self._get_or_create_conversation(user_id, butler_id)
            
            # Process request based on type
            if request_type == "market_analysis":
                response = await self._handle_market_analysis_request(
                    conversation, service_request
                )
            elif request_type == "portfolio_review":
                response = await self._handle_portfolio_review_request(
                    conversation, service_request
                )
            elif request_type == "trade_assistance":
                response = await self._handle_trade_assistance_request(
                    conversation, service_request
                )
            elif request_type == "research_request":
                response = await self._handle_research_request(
                    conversation, service_request
                )
            elif request_type == "general_chat":
                response = await self._handle_general_chat(
                    conversation, message
                )
            else:
                response = await self._handle_general_inquiry(
                    conversation, service_request
                )
            
            # Update conversation history
            await self._update_conversation_history(
                conversation, service_request, response
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Butler service request failed: {e}")
            return {
                "success": False,
                "error": "Butler service temporarily unavailable"
            }
    
    async def _handle_market_analysis_request(
        self,
        conversation: ButlerConversation,
        request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle market analysis request"""
        
        symbol = request.get("symbol", "")
        analysis_type = request.get("analysis_type", "comprehensive")
        
        # Get market intelligence
        market_data = await self.market_intelligence.get_comprehensive_analysis(
            symbol, analysis_type
        )
        
        # Get butler's tier-specific insights
        butler_tier = self._get_butler_tier(conversation.butler_id)
        insights = await self._generate_tier_specific_insights(
            market_data, butler_tier
        )
        
        # Format response based on butler persona
        response_message = await self._format_market_analysis_response(
            conversation, market_data, insights
        )
        
        return {
            "success": True,
            "type": "market_analysis",
            "message": response_message,
            "data": {
                "symbol": symbol,
                "analysis": market_data,
                "butler_insights": insights,
                "confidence": market_data.get("confidence", 0.8)
            },
            "suggested_actions": insights.get("suggested_actions", []),
            "follow_up_questions": insights.get("follow_up_questions", [])
        }
    
    async def _handle_portfolio_review_request(
        self,
        conversation: ButlerConversation,
        request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle portfolio review request"""
        
        # Get portfolio analysis
        portfolio_analysis = await self.portfolio_analyzer.analyze_portfolio(
            conversation.user_id
        )
        
        # Generate butler recommendations
        recommendations = await self._generate_portfolio_recommendations(
            portfolio_analysis, conversation.butler_id
        )
        
        # Format response
        response_message = await self._format_portfolio_review_response(
            conversation, portfolio_analysis, recommendations
        )
        
        return {
            "success": True,
            "type": "portfolio_review",
            "message": response_message,
            "data": {
                "portfolio_summary": portfolio_analysis["summary"],
                "performance_metrics": portfolio_analysis["metrics"],
                "recommendations": recommendations,
                "risk_assessment": portfolio_analysis["risk_assessment"]
            },
            "action_items": recommendations.get("action_items", [])
        }
    
    async def _handle_trade_assistance_request(
        self,
        conversation: ButlerConversation,
        request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle trade assistance request"""
        
        trade_intent = request.get("trade_intent", {})
        symbol = trade_intent.get("symbol", "")
        action = trade_intent.get("action", "")  # buy/sell
        
        # Analyze trade opportunity
        trade_analysis = await self._analyze_trade_opportunity(
            symbol, action, conversation.user_id
        )
        
        # Generate butler guidance
        guidance = await self._generate_trade_guidance(
            trade_analysis, conversation.butler_id
        )
        
        response_message = await self._format_trade_assistance_response(
            conversation, trade_analysis, guidance
        )
        
        return {
            "success": True,
            "type": "trade_assistance",
            "message": response_message,
            "data": {
                "trade_analysis": trade_analysis,
                "butler_guidance": guidance,
                "execution_options": guidance.get("execution_options", [])
            },
            "quick_actions": ["execute", "modify", "research_more", "cancel"]
        }
    
    async def _handle_research_request(
        self,
        conversation: ButlerConversation,
        request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle research request"""
        
        research_topic = request.get("topic", "")
        depth = request.get("depth", "standard")
        
        # Perform research
        research_results = await self._perform_market_research(
            research_topic, depth, conversation.butler_id
        )
        
        response_message = await self._format_research_response(
            conversation, research_results
        )
        
        return {
            "success": True,
            "type": "research",
            "message": response_message,
            "data": research_results,
            "delivery_format": ["summary", "detailed_report", "presentation"]
        }
    
    async def _handle_general_chat(
        self,
        conversation: ButlerConversation,
        message: str
    ) -> Dict[str, Any]:
        """Handle general chat with butler"""
        
        # Use GPT-4 for natural conversation
        chat_response = await self._generate_butler_chat_response(
            conversation, message
        )
        
        return {
            "success": True,
            "type": "chat",
            "message": chat_response,
            "conversation_context": "maintained"
        }
    
    async def _generate_butler_chat_response(
        self,
        conversation: ButlerConversation,
        user_message: str
    ) -> str:
        """Generate natural chat response using GPT-4"""
        
        butler_profile = self.butler_profiles[conversation.butler_id]
        butler_tier = self._get_butler_tier(conversation.butler_id)
        
        # Build conversation context
        context_prompt = self._build_butler_prompt(
            butler_profile, butler_tier, conversation.context
        )
        
        # Get recent conversation history
        recent_history = conversation.conversation_history[-10:]  # Last 10 messages
        
        messages = [
            {"role": "system", "content": context_prompt},
            *[
                {"role": "user" if msg["sender"] == "user" else "assistant", "content": msg["message"]}
                for msg in recent_history
            ],
            {"role": "user", "content": user_message}
        ]
        
        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"GPT-4 chat response failed: {e}")
            return await self._get_fallback_butler_response(butler_tier)
    
    def _build_butler_prompt(
        self,
        butler_profile: MarketButlerProfile,
        butler_tier: str,
        user_context: Dict[str, Any]
    ) -> str:
        """Build butler persona prompt"""
        
        if butler_tier == "void":
            return f"""You are {butler_profile.name}, an elite market butler for GridWorks Void tier clients. 
You serve billionaire-level investors with access to exclusive markets, private equity, and government relations.
Your communication style is sophisticated, discreet, and focused on ultra-premium opportunities.
You have access to insider intelligence and can arrange exclusive investment opportunities.
User context: Portfolio ₹{user_context.get('portfolio_value', 0):,.0f}, Risk appetite: {user_context.get('risk_appetite', 'unknown')}
Respond with the elegance befitting a client of this caliber."""

        elif butler_tier == "obsidian":
            return f"""You are {butler_profile.name}, a premium market butler for GridWorks Obsidian tier clients.
You serve HNI clients with institutional-level market access and sophisticated strategies.
Your communication style is professional, insightful, and focused on institutional opportunities.
You provide detailed analysis and strategic guidance for complex portfolios.
User context: Portfolio ₹{user_context.get('portfolio_value', 0):,.0f}, Risk appetite: {user_context.get('risk_appetite', 'unknown')}
Provide expert-level guidance with institutional perspective."""

        else:  # onyx
            return f"""You are {butler_profile.name}, a professional market butler for GridWorks Onyx tier clients.
You serve affluent traders with premium market insights and personalized guidance.
Your communication style is knowledgeable, helpful, and focused on growth opportunities.
You provide clear analysis and actionable recommendations.
User context: Portfolio ₹{user_context.get('portfolio_value', 0):,.0f}, Risk appetite: {user_context.get('risk_appetite', 'unknown')}
Provide professional guidance with clear explanations."""
    
    async def _get_fallback_butler_response(self, butler_tier: str) -> str:
        """Get fallback response when AI is unavailable"""
        
        if butler_tier == "void":
            return "◆ I apologize for the brief delay. Let me gather the latest market intelligence for you. How may I assist with your portfolio strategy today?"
        elif butler_tier == "obsidian":
            return "⚫ My apologies for the momentary pause. I'm analyzing current market conditions to provide you with the most relevant insights. How can I help you today?"
        else:
            return "🖤 Thank you for your patience. I'm here to help with your trading decisions and market analysis. What would you like to discuss?"
    
    def _get_butler_tier(self, butler_id: str) -> str:
        """Get butler tier from ID"""
        if "void" in butler_id:
            return "void"
        elif "obsidian" in butler_id:
            return "obsidian"
        else:
            return "onyx"
    
    async def _initialize_butler_profiles(self):
        """Initialize butler profiles for different tiers"""
        
        # Void Butler (Ultra-premium)
        self.butler_profiles["butler_void_001"] = MarketButlerProfile(
            butler_id="butler_void_001",
            name="Arjun Mehta",
            specializations=["private_equity", "government_relations", "billionaire_networks", "custom_derivatives"],
            languages=["English", "Hindi"],
            experience_years=20,
            certification_level="CFA, FRM, Billionaire Advisory",
            client_satisfaction=0.98,
            average_response_time=30.0,  # 30 seconds
            success_rate=0.95,
            portfolio_performance=0.35,  # 35% alpha
            working_hours={"24x7": True},
            time_zone="IST",
            current_load=1,
            max_clients=5,
            preferred_channels=["video", "call", "secure_chat"],
            contact_info={"secure_line": "+91-XXXX-VOID"},
            availability_status="available"
        )
        
        # Obsidian Butler (Premium)
        self.butler_profiles["butler_obsidian_001"] = MarketButlerProfile(
            butler_id="butler_obsidian_001",
            name="Priya Sharma",
            specializations=["institutional_trading", "hedge_funds", "structured_products"],
            languages=["English", "Hindi", "Gujarati"],
            experience_years=15,
            certification_level="CFA, FRM",
            client_satisfaction=0.94,
            average_response_time=120.0,  # 2 minutes
            success_rate=0.90,
            portfolio_performance=0.25,  # 25% alpha
            working_hours={"market_hours": True, "extended": True},
            time_zone="IST",
            current_load=8,
            max_clients=20,
            preferred_channels=["call", "chat", "video"],
            contact_info={"direct_line": "+91-XXXX-OBS"},
            availability_status="available"
        )
        
        # Onyx Butler (Professional)
        self.butler_profiles["butler_onyx_001"] = MarketButlerProfile(
            butler_id="butler_onyx_001",
            name="Rajesh Kumar",
            specializations=["equity_research", "portfolio_optimization", "risk_management"],
            languages=["English", "Hindi", "Tamil"],
            experience_years=10,
            certification_level="CFA",
            client_satisfaction=0.90,
            average_response_time=300.0,  # 5 minutes
            success_rate=0.85,
            portfolio_performance=0.18,  # 18% alpha
            working_hours={"market_hours": True},
            time_zone="IST",
            current_load=25,
            max_clients=50,
            preferred_channels=["chat", "call"],
            contact_info={"support_line": "+91-XXXX-ONX"},
            availability_status="available"
        )
        
        logger.info(f"Initialized {len(self.butler_profiles)} butler profiles")
    
    async def get_butler_status(self, butler_id: str) -> Dict[str, Any]:
        """Get butler status and availability"""
        
        butler_profile = self.butler_profiles.get(butler_id)
        if not butler_profile:
            return {"available": False, "error": "Butler not found"}
        
        return {
            "available": butler_profile.availability_status == "available",
            "name": butler_profile.name,
            "response_time": f"{butler_profile.average_response_time:.0f} seconds",
            "satisfaction_rating": f"{butler_profile.client_satisfaction:.1%}",
            "specializations": butler_profile.specializations,
            "current_load": f"{butler_profile.current_load}/{butler_profile.max_clients} clients"
        }
    
    async def notify_trade_execution(
        self,
        butler_id: str,
        user_id: str,
        trade_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Notify butler of trade execution"""
        
        try:
            # Find conversation
            conversation = await self._get_active_conversation(user_id, butler_id)
            if not conversation:
                return {"success": False, "error": "No active conversation"}
            
            # Generate trade notification
            notification = await self._generate_trade_notification(
                trade_result, conversation.butler_id
            )
            
            # Update conversation
            await self._update_conversation_history(
                conversation,
                {"type": "trade_executed", "trade_result": trade_result},
                {"type": "trade_notification", "message": notification}
            )
            
            return {"success": True, "notification": notification}
            
        except Exception as e:
            logger.error(f"Trade notification failed: {e}")
            return {"success": False, "error": "Notification failed"}
    
    async def get_utilization_metrics(self) -> Dict[str, Any]:
        """Get butler utilization metrics"""
        
        total_butlers = len(self.butler_profiles)
        active_conversations = len(self.active_conversations)
        
        utilization_by_tier = {}
        for butler_id, profile in self.butler_profiles.items():
            tier = self._get_butler_tier(butler_id)
            if tier not in utilization_by_tier:
                utilization_by_tier[tier] = {"total": 0, "utilized": 0}
            utilization_by_tier[tier]["total"] += 1
            if profile.current_load > 0:
                utilization_by_tier[tier]["utilized"] += 1
        
        return {
            "total_butlers": total_butlers,
            "active_conversations": active_conversations,
            "utilization_by_tier": utilization_by_tier,
            "average_response_time": sum(
                profile.average_response_time for profile in self.butler_profiles.values()
            ) / total_butlers if total_butlers > 0 else 0,
            "average_satisfaction": sum(
                profile.client_satisfaction for profile in self.butler_profiles.values()
            ) / total_butlers if total_butlers > 0 else 0
        }
    
    async def _build_user_context(self, user_id: str) -> Dict[str, Any]:
        """Build user context for butler conversations"""
        
        # Mock user context - would integrate with actual user data
        return {
            "portfolio_value": 50000000,  # ₹5 Cr
            "risk_appetite": "aggressive",
            "investment_preferences": ["equities", "derivatives"],
            "trading_experience": "expert",
            "preferred_sectors": ["technology", "pharmaceuticals"],
            "recent_activity": "high"
        }
    
    async def _get_or_create_conversation(
        self,
        user_id: str,
        butler_id: str
    ) -> ButlerConversation:
        """Get existing or create new conversation"""
        
        # Look for existing active conversation
        for conversation in self.active_conversations.values():
            if conversation.user_id == user_id and conversation.butler_id == butler_id:
                return conversation
        
        # Create new conversation
        conversation_id = f"butler_{user_id}_{int(datetime.utcnow().timestamp())}"
        conversation = ButlerConversation(
            user_id=user_id,
            butler_id=butler_id,
            conversation_id=conversation_id,
            context=await self._build_user_context(user_id),
            conversation_history=[],
            created_at=datetime.utcnow(),
            last_activity=datetime.utcnow(),
            status="active"
        )
        
        self.active_conversations[conversation_id] = conversation
        return conversation
    
    async def _update_conversation_history(
        self,
        conversation: ButlerConversation,
        request: Dict[str, Any],
        response: Dict[str, Any]
    ):
        """Update conversation history"""
        
        conversation.conversation_history.extend([
            {
                "timestamp": datetime.utcnow().isoformat(),
                "sender": "user",
                "type": request.get("type", "message"),
                "message": request.get("message", ""),
                "data": request
            },
            {
                "timestamp": datetime.utcnow().isoformat(),
                "sender": "butler",
                "type": response.get("type", "response"),
                "message": response.get("message", ""),
                "data": response
            }
        ])
        
        conversation.last_activity = datetime.utcnow()
        
        # Keep only last 100 messages
        if len(conversation.conversation_history) > 100:
            conversation.conversation_history = conversation.conversation_history[-100:]
    
    async def _start_market_monitoring(self):
        """Start market monitoring service"""
        
        while True:
            try:
                await asyncio.sleep(60)  # Every minute
                
                # Monitor market for opportunities
                await self._scan_market_opportunities()
                
            except Exception as e:
                logger.error(f"Market monitoring error: {e}")
    
    async def _start_opportunity_scanning(self):
        """Start opportunity scanning service"""
        
        while True:
            try:
                await asyncio.sleep(300)  # Every 5 minutes
                
                # Scan for new opportunities
                opportunities = await self._identify_market_opportunities()
                
                # Notify relevant butlers
                for opportunity in opportunities:
                    await self._notify_butlers_of_opportunity(opportunity)
                
            except Exception as e:
                logger.error(f"Opportunity scanning error: {e}")
    
    async def _start_performance_monitoring(self):
        """Start butler performance monitoring"""
        
        while True:
            try:
                await asyncio.sleep(900)  # Every 15 minutes
                
                # Monitor butler performance
                await self.performance_tracker.update_metrics()
                
            except Exception as e:
                logger.error(f"Performance monitoring error: {e}")


class MarketIntelligenceEngine:
    """Market intelligence for butler analysis"""
    
    async def get_comprehensive_analysis(self, symbol: str, analysis_type: str) -> Dict[str, Any]:
        """Get comprehensive market analysis"""
        
        # Mock market analysis - would integrate with real data
        return {
            "symbol": symbol,
            "current_price": 3850.50,
            "day_change": 2.3,
            "technical_analysis": {
                "trend": "bullish",
                "support": 3800,
                "resistance": 3900,
                "rsi": 65.2
            },
            "fundamental_analysis": {
                "pe_ratio": 28.5,
                "market_cap": "₹14.2 L Cr",
                "revenue_growth": 15.2
            },
            "sentiment": "positive",
            "confidence": 0.85
        }


class PortfolioAnalyzer:
    """Portfolio analysis for butler insights"""
    
    async def analyze_portfolio(self, user_id: str) -> Dict[str, Any]:
        """Analyze user portfolio"""
        
        # Mock portfolio analysis - would integrate with real data
        return {
            "summary": {
                "total_value": 50000000,
                "day_change": 2.1,
                "ytd_return": 18.5
            },
            "metrics": {
                "sharpe_ratio": 1.85,
                "beta": 0.92,
                "max_drawdown": -12.3
            },
            "risk_assessment": {
                "risk_level": "moderate_aggressive",
                "concentration_risk": "medium",
                "sector_exposure": "balanced"
            }
        }


class CommunicationManager:
    """Manage butler communication channels"""
    
    async def send_message(self, butler_id: str, user_id: str, message: str, channel: str):
        """Send message through specified channel"""
        # Would integrate with actual communication APIs
        logger.info(f"Butler {butler_id} message sent to {user_id} via {channel}")


class ButlerPerformanceTracker:
    """Track butler performance metrics"""
    
    async def update_metrics(self):
        """Update performance metrics"""
        # Would track actual performance metrics
        logger.debug("Butler performance metrics updated")