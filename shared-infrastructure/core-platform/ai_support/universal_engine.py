"""
Universal AI Support Engine
Core intelligence that serves all tiers with universal understanding
"""

import asyncio
import openai
import json
import time
import hashlib
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging

from .models import (
    SupportMessage, UniversalQuery, SupportResponse, UserContext,
    SupportTier, QueryCategory, UrgencyLevel, TierConfig
)

logger = logging.getLogger(__name__)


class UniversalTrainingModule:
    """Universal query classification and intent detection"""
    
    def __init__(self):
        # Universal query patterns (same for all tiers)
        self.query_patterns = {
            QueryCategory.ORDER_MANAGEMENT: {
                "keywords": ["order", "buy", "sell", "cancel", "modify", "failed", "pending", "executed"],
                "intents": ["cancel_order", "modify_order", "check_status", "understand_failure", "retry_order"],
                "entities": ["order_id", "symbol", "quantity", "price", "amount"]
            },
            QueryCategory.PORTFOLIO_QUERIES: {
                "keywords": ["portfolio", "holdings", "pnl", "profit", "loss", "balance", "positions"],
                "intents": ["view_portfolio", "calculate_pnl", "analyze_performance", "risk_assessment"],
                "entities": ["symbol", "quantity", "investment_amount", "current_value"]
            },
            QueryCategory.PAYMENT_ISSUES: {
                "keywords": ["money", "payment", "deposit", "withdraw", "upi", "bank", "transfer", "stuck"],
                "intents": ["add_money", "withdraw_money", "payment_failed", "upi_issue"],
                "entities": ["amount", "upi_id", "bank_account", "transaction_id"]
            },
            QueryCategory.KYC_COMPLIANCE: {
                "keywords": ["kyc", "verification", "documents", "aadhar", "pan", "rejected", "pending"],
                "intents": ["check_kyc_status", "upload_documents", "understand_rejection", "update_kyc"],
                "entities": ["document_type", "rejection_reason", "kyc_status"]
            },
            QueryCategory.TECHNICAL_SUPPORT: {
                "keywords": ["app", "login", "password", "otp", "whatsapp", "error", "crash", "slow"],
                "intents": ["login_issue", "app_problem", "whatsapp_setup", "password_reset"],
                "entities": ["error_code", "device_type", "app_version"]
            },
            QueryCategory.MARKET_QUERIES: {
                "keywords": ["price", "market", "stock", "nifty", "sensex", "news", "analysis"],
                "intents": ["price_inquiry", "market_analysis", "stock_research", "market_hours"],
                "entities": ["symbol", "index", "price_target", "time_frame"]
            }
        }
        
        # Urgency detection patterns
        self.urgency_keywords = {
            UrgencyLevel.CRITICAL: ["emergency", "urgent", "stuck", "loss", "hack", "fraud"],
            UrgencyLevel.URGENT: ["failed", "error", "problem", "issue", "help"],
            UrgencyLevel.HIGH: ["cancel", "modify", "stop", "block"],
            UrgencyLevel.MEDIUM: ["question", "how", "why", "when"],
            UrgencyLevel.LOW: ["info", "learn", "understand", "explain"]
        }
    
    async def classify_query(self, message: SupportMessage) -> UniversalQuery:
        """Classify any support query universally"""
        
        text = message.message.lower()
        
        # Detect category
        category = await self._detect_category(text)
        
        # Extract intent
        intent = await self._extract_intent(text, category)
        
        # Assess urgency
        urgency = await self._assess_urgency(text, message.user_tier)
        
        # Calculate complexity
        complexity = await self._assess_complexity(text, category)
        
        # Extract entities
        entities = await self._extract_entities(text, category)
        
        # Extract keywords
        keywords = await self._extract_keywords(text)
        
        return UniversalQuery(
            category=category,
            intent=intent,
            urgency=urgency,
            complexity=complexity,
            language=message.language,
            entities=entities,
            confidence=0.85,  # Would be from ML model in production
            keywords=keywords
        )
    
    async def _detect_category(self, text: str) -> QueryCategory:
        """Detect query category from text"""
        
        category_scores = {}
        
        for category, patterns in self.query_patterns.items():
            score = 0
            for keyword in patterns["keywords"]:
                if keyword in text:
                    score += 1
            category_scores[category] = score
        
        # Return category with highest score
        best_category = max(category_scores, key=category_scores.get)
        return best_category if category_scores[best_category] > 0 else QueryCategory.GENERAL_INQUIRY
    
    async def _extract_intent(self, text: str, category: QueryCategory) -> str:
        """Extract specific intent within category"""
        
        if category not in self.query_patterns:
            return "general_inquiry"
            
        intents = self.query_patterns[category]["intents"]
        
        # Simple keyword matching (would be ML-based in production)
        for intent in intents:
            intent_keywords = intent.split("_")
            if any(keyword in text for keyword in intent_keywords):
                return intent
                
        return intents[0]  # Default to first intent
    
    async def _assess_urgency(self, text: str, tier: SupportTier) -> UrgencyLevel:
        """Assess query urgency"""
        
        base_urgency = UrgencyLevel.MEDIUM
        
        for urgency_level, keywords in self.urgency_keywords.items():
            if any(keyword in text for keyword in keywords):
                base_urgency = urgency_level
                break
        
        # Tier-based urgency boost
        tier_boost = {
            SupportTier.BLACK: 1,
            SupportTier.ELITE: 0,
            SupportTier.PRO: 0,
            SupportTier.LITE: -1
        }
        
        urgency_value = min(5, max(1, base_urgency.value + tier_boost.get(tier, 0)))
        return UrgencyLevel(urgency_value)
    
    async def _assess_complexity(self, text: str, category: QueryCategory) -> int:
        """Assess query complexity (1-5 scale)"""
        
        complexity_map = {
            QueryCategory.ORDER_MANAGEMENT: 3,
            QueryCategory.PORTFOLIO_QUERIES: 4,
            QueryCategory.PAYMENT_ISSUES: 2,
            QueryCategory.KYC_COMPLIANCE: 3,
            QueryCategory.TECHNICAL_SUPPORT: 2,
            QueryCategory.MARKET_QUERIES: 4,
            QueryCategory.COMPLAINT: 3,
            QueryCategory.GENERAL_INQUIRY: 1
        }
        
        base_complexity = complexity_map.get(category, 2)
        
        # Adjust based on text length and technical terms
        if len(text.split()) > 20:
            base_complexity += 1
        if any(term in text for term in ["algorithm", "derivative", "portfolio", "analysis"]):
            base_complexity += 1
            
        return min(5, base_complexity)
    
    async def _extract_entities(self, text: str, category: QueryCategory) -> Dict[str, Any]:
        """Extract relevant entities from text"""
        
        entities = {}
        
        if category not in self.query_patterns:
            return entities
            
        entity_types = self.query_patterns[category]["entities"]
        
        # Simple regex-based extraction (would be NER model in production)
        import re
        
        if "order_id" in entity_types:
            order_match = re.search(r'order[#\s]*(\d+)', text)
            if order_match:
                entities["order_id"] = order_match.group(1)
        
        if "symbol" in entity_types:
            # Common Indian stock symbols
            symbols = ["RELIANCE", "TCS", "INFY", "HDFC", "ICICI", "SBI", "ITC", "HDFCBANK"]
            for symbol in symbols:
                if symbol.lower() in text.lower():
                    entities["symbol"] = symbol
                    break
        
        if "amount" in entity_types:
            amount_match = re.search(r'₹?\s?(\d+(?:,\d+)*(?:\.\d+)?)', text)
            if amount_match:
                entities["amount"] = amount_match.group(1)
        
        return entities
    
    async def _extract_keywords(self, text: str) -> List[str]:
        """Extract key terms from text"""
        
        # Simple keyword extraction (would be more sophisticated in production)
        words = text.lower().split()
        
        # Filter common words
        stop_words = {"i", "me", "my", "you", "the", "a", "an", "is", "are", "was", "were", "and", "or", "but"}
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        return keywords[:10]  # Return top 10 keywords


class GPT4SupportAgent:
    """GPT-4 powered support agent with universal intelligence"""
    
    def __init__(self):
        self.client = openai.AsyncOpenAI()
        self.system_prompts = self._load_system_prompts()
        
    def _load_system_prompts(self) -> Dict[str, str]:
        """Load category-specific system prompts"""
        
        return {
            "order_management": """
You are a SEBI-certified trading support specialist for GridWorks.
Help users with order-related issues quickly and accurately.

RULES:
1. Always explain in user's language ({language})
2. Use simple terms (explain like they're 15 years old)
3. Provide exact amounts, order IDs when available
4. Offer immediate solutions (UPI top-up, retry buttons)
5. If uncertain, escalate to human with context

CONTEXT:
User tier: {user_tier}
Recent orders: {recent_orders}
Account balance: {balance}
""",
            
            "portfolio_queries": """
You are GridWorks's portfolio analysis expert.
Help users understand their investments clearly.

FOCUS:
- Current holdings and P&L explanation
- Risk analysis in simple language  
- Actionable suggestions (buy/sell/hold)
- Market context and comparisons

Be encouraging but honest about risks.
Always explain in {language}.
""",
            
            "payment_issues": """
You are GridWorks's payment and banking specialist.
Resolve money-related issues quickly.

EXPERTISE:
- UPI integration troubleshooting
- Bank transfer guidance
- Balance and withdrawal issues
- Payment failure analysis

Provide step-by-step solutions.
Language: {language}
""",
            
            "kyc_compliance": """
You are GridWorks's KYC and compliance specialist.
Help users with verification and documentation.

KNOWLEDGE:
- SEBI KYC requirements
- Document verification process
- Rejection reason explanations
- Regulatory compliance guidance

Always maintain privacy and security.
Language: {language}
""",
            
            "technical_support": """
You are GridWorks's technical support specialist.
Solve app and platform issues efficiently.

SKILLS:
- Mobile app troubleshooting
- WhatsApp integration help
- Login and access issues
- Performance optimization

Provide clear, step-by-step solutions.
Language: {language}
""",
            
            "market_queries": """
You are GridWorks's market intelligence specialist.
Provide market insights and stock analysis.

EXPERTISE:
- Real-time price information
- Market trend analysis
- Stock research and recommendations
- Economic news interpretation

Keep explanations simple but informative.
Language: {language}
"""
        }
    
    async def generate_response(
        self,
        query: UniversalQuery,
        user_context: UserContext,
        message: SupportMessage
    ) -> Dict[str, Any]:
        """Generate AI response for any query universally"""
        
        category_key = query.category.value
        system_prompt = self.system_prompts.get(category_key, self.system_prompts["market_queries"])
        
        # Format system prompt with context
        formatted_prompt = system_prompt.format(
            language=query.language,
            user_tier=user_context.tier.value,
            recent_orders=user_context.recent_orders[-3:] if user_context.recent_orders else [],
            balance=user_context.balance
        )
        
        # Build conversation messages
        messages = [
            {"role": "system", "content": formatted_prompt},
            {"role": "user", "content": message.message}
        ]
        
        try:
            start_time = time.time()
            
            response = await self.client.chat.completions.create(
                model="gpt-4-turbo",
                messages=messages,
                max_tokens=400,
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            response_time = time.time() - start_time
            result = json.loads(response.choices[0].message.content)
            
            return {
                "success": True,
                "message": result.get("message", ""),
                "actions": result.get("actions", []),
                "escalate": result.get("escalate", False),
                "confidence": result.get("confidence", 0.8),
                "response_time": response_time,
                "follow_up": result.get("follow_up", None)
            }
            
        except Exception as e:
            logger.error(f"GPT-4 response generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "escalate": True,
                "response_time": time.time() - start_time if 'start_time' in locals() else 0
            }


class UniversalAISupport:
    """Main AI support engine serving all tiers"""
    
    def __init__(self):
        self.training_module = UniversalTrainingModule()
        self.ai_agent = GPT4SupportAgent()
        self.tier_configs = self._load_tier_configs()
        
    def _load_tier_configs(self) -> Dict[SupportTier, TierConfig]:
        """Load tier-specific configurations"""
        
        return {
            SupportTier.LITE: TierConfig(
                tier=SupportTier.LITE,
                max_ai_response_time=30.0,
                human_escalation_threshold=0.9,
                max_human_wait_time=120,
                features=["ai_chat", "basic_zk"],
                agent_tier="junior",
                personality_tone="friendly_helpful",
                max_response_length=100,
                visual_style={"color": "blue", "emoji": "basic"}
            ),
            
            SupportTier.PRO: TierConfig(
                tier=SupportTier.PRO,
                max_ai_response_time=15.0,
                human_escalation_threshold=0.8,
                max_human_wait_time=30,
                features=["ai_chat", "voice_support", "priority_queue", "enhanced_zk"],
                agent_tier="senior",
                personality_tone="professional_smart",
                max_response_length=200,
                visual_style={"color": "blue_gold", "emoji": "strategic"}
            ),
            
            SupportTier.ELITE: TierConfig(
                tier=SupportTier.ELITE,
                max_ai_response_time=10.0,
                human_escalation_threshold=0.7,
                max_human_wait_time=5,
                features=["ai_chat", "voice_support", "video_support", "premium_zk", "predictive_alerts"],
                agent_tier="expert",
                personality_tone="expert_advisor",
                max_response_length=300,
                visual_style={"color": "platinum_gold", "emoji": "sophisticated"}
            ),
            
            SupportTier.BLACK: TierConfig(
                tier=SupportTier.BLACK,
                max_ai_response_time=5.0,
                human_escalation_threshold=0.6,
                max_human_wait_time=1,
                features=["ai_chat", "voice_support", "video_support", "market_butler", "white_glove"],
                agent_tier="dedicated",
                personality_tone="concierge_butler",
                max_response_length=400,
                visual_style={"color": "black_gold", "emoji": "exclusive"}
            )
        }
    
    async def process_support_request(
        self,
        message: SupportMessage,
        user_context: UserContext
    ) -> SupportResponse:
        """Main entry point for processing support requests"""
        
        start_time = time.time()
        
        try:
            # Step 1: Universal query classification
            query = await self.training_module.classify_query(message)
            
            # Step 2: Get tier configuration
            tier_config = self.tier_configs[message.user_tier]
            
            # Step 3: Decide AI vs human routing
            should_escalate = query.confidence < tier_config.human_escalation_threshold
            
            if should_escalate:
                # Route to human escalation
                response = await self._create_escalation_response(message, query, tier_config)
            else:
                # Generate AI response
                ai_result = await self.ai_agent.generate_response(query, user_context, message)
                
                if ai_result["success"] and not ai_result["escalate"]:
                    response = await self._create_ai_response(ai_result, query, tier_config)
                else:
                    response = await self._create_escalation_response(message, query, tier_config)
            
            # Step 4: Add universal features
            response.response_time = time.time() - start_time
            
            return response
            
        except Exception as e:
            logger.error(f"Support request processing failed: {e}")
            return await self._create_error_response(message, str(e))
    
    async def _create_ai_response(
        self,
        ai_result: Dict[str, Any],
        query: UniversalQuery,
        tier_config: TierConfig
    ) -> SupportResponse:
        """Create AI-generated response"""
        
        return SupportResponse(
            message=ai_result["message"],
            actions=ai_result["actions"],
            tier_features=[],  # Will be populated by UX renderer
            escalate=False,
            confidence=ai_result["confidence"],
            response_time=ai_result["response_time"],
            follow_up=ai_result.get("follow_up")
        )
    
    async def _create_escalation_response(
        self,
        message: SupportMessage,
        query: UniversalQuery,
        tier_config: TierConfig
    ) -> SupportResponse:
        """Create human escalation response"""
        
        wait_time = tier_config.max_human_wait_time
        
        escalation_message = f"I'm connecting you to our {tier_config.agent_tier} support specialist. Expected wait time: {wait_time} minutes."
        
        return SupportResponse(
            message=escalation_message,
            actions=[{"type": "human_escalation", "wait_time": wait_time}],
            tier_features=[],
            escalate=True,
            confidence=0.0,
            response_time=0.0
        )
    
    async def _create_error_response(self, message: SupportMessage, error: str) -> SupportResponse:
        """Create error response"""
        
        return SupportResponse(
            message="I'm experiencing technical difficulties. Let me connect you to a human agent.",
            actions=[{"type": "human_escalation", "reason": "system_error"}],
            tier_features=[],
            escalate=True,
            confidence=0.0,
            response_time=0.0
        )