"""
GridWorks AI Suite - Support Engine
Multi-language AI support with financial domain expertise and WhatsApp integration
"""

import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Union
from enum import Enum
import openai
import anthropic
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
import redis
import json
import hashlib
from dataclasses import dataclass

from ..database.models import EnterpriseClient, User, UsageRecord, AuditLog
from ..database.session import get_db
from ..config import settings
from ..utils.language_detection import detect_language, translate_text
from ..utils.whatsapp_client import WhatsAppBusinessClient
from ..utils.voice_synthesis import generate_voice_response


class SupportTier(str, Enum):
    """Support service tiers"""
    COMMUNITY = "community"      # Basic AI support
    PROFESSIONAL = "professional"  # Enhanced AI with priority
    ENTERPRISE = "enterprise"    # Dedicated support with SLA
    QUANTUM = "quantum"          # Custom AI with instant response


class ResponseFormat(str, Enum):
    """Response format options"""
    TEXT = "text"
    AUDIO = "audio"
    BOTH = "both"


class SupportChannel(str, Enum):
    """Support channels"""
    API = "api"
    WHATSAPP = "whatsapp"
    EMAIL = "email"
    CHAT = "chat"


@dataclass
class SupportRequest:
    """Support request data structure"""
    client_id: str
    user_id: Optional[str]
    query: str
    language: str
    channel: SupportChannel
    priority: SupportTier
    context: Dict[str, Any]
    session_id: Optional[str] = None


@dataclass
class SupportResponse:
    """Support response data structure"""
    request_id: str
    response_text: str
    response_audio: Optional[bytes]
    language: str
    confidence_score: float
    response_time_ms: int
    tokens_used: int
    model_used: str
    follow_up_suggestions: List[str]


class AIModelOrchestrator:
    """
    Orchestrates different AI models based on query complexity and client tier
    """
    
    def __init__(self):
        self.openai_client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.anthropic_client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
        
        # Model configuration per tier
        self.tier_models = {
            SupportTier.COMMUNITY: {
                "primary": "gpt-3.5-turbo",
                "fallback": "claude-3-haiku-20240307",
                "max_tokens": 1000,
                "temperature": 0.3
            },
            SupportTier.PROFESSIONAL: {
                "primary": "gpt-4-turbo-preview",
                "fallback": "claude-3-sonnet-20240229",
                "max_tokens": 2000,
                "temperature": 0.2
            },
            SupportTier.ENTERPRISE: {
                "primary": "gpt-4-turbo-preview",
                "fallback": "claude-3-opus-20240229",
                "max_tokens": 4000,
                "temperature": 0.1
            },
            SupportTier.QUANTUM: {
                "primary": "gpt-4-turbo-preview",
                "fallback": "claude-3-opus-20240229",
                "max_tokens": 8000,
                "temperature": 0.1,
                "custom_instructions": True
            }
        }
    
    async def get_model_response(
        self,
        query: str,
        language: str,
        tier: SupportTier,
        context: Dict[str, Any],
        client_id: str
    ) -> Dict[str, Any]:
        """Get AI model response based on tier and context"""
        
        model_config = self.tier_models[tier]
        
        # Build financial domain context
        financial_context = await self._build_financial_context(query, client_id)
        
        # Create system prompt based on language and tier
        system_prompt = await self._create_system_prompt(language, tier, financial_context)
        
        # Get response from primary model
        try:
            if model_config["primary"].startswith("gpt"):
                response = await self._get_openai_response(
                    query, system_prompt, model_config, context
                )
            else:
                response = await self._get_anthropic_response(
                    query, system_prompt, model_config, context
                )
            
            response["model_used"] = model_config["primary"]
            return response
            
        except Exception as e:
            # Fallback to secondary model
            try:
                if model_config["fallback"].startswith("claude"):
                    response = await self._get_anthropic_response(
                        query, system_prompt, model_config, context
                    )
                else:
                    response = await self._get_openai_response(
                        query, system_prompt, model_config, context
                    )
                
                response["model_used"] = model_config["fallback"]
                response["fallback_used"] = True
                return response
                
            except Exception as fallback_error:
                # Return error response
                return {
                    "response": "I apologize, but our AI services are temporarily unavailable. Please try again in a few moments.",
                    "confidence_score": 0.0,
                    "tokens_used": 0,
                    "model_used": "error",
                    "error": str(fallback_error)
                }
    
    async def _get_openai_response(
        self,
        query: str,
        system_prompt: str,
        model_config: Dict,
        context: Dict
    ) -> Dict[str, Any]:
        """Get response from OpenAI models"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ]
        
        # Add conversation history if available
        if context.get("conversation_history"):
            for msg in context["conversation_history"][-5:]:  # Last 5 messages
                messages.insert(-1, msg)
        
        response = await self.openai_client.chat.completions.create(
            model=model_config["primary"],
            messages=messages,
            max_tokens=model_config["max_tokens"],
            temperature=model_config["temperature"],
            presence_penalty=0.1,
            frequency_penalty=0.1
        )
        
        return {
            "response": response.choices[0].message.content,
            "confidence_score": 0.95,  # OpenAI doesn't provide confidence scores
            "tokens_used": response.usage.total_tokens,
            "finish_reason": response.choices[0].finish_reason
        }
    
    async def _get_anthropic_response(
        self,
        query: str,
        system_prompt: str,
        model_config: Dict,
        context: Dict
    ) -> Dict[str, Any]:
        """Get response from Anthropic Claude models"""
        
        response = await self.anthropic_client.messages.create(
            model=model_config["fallback"],
            max_tokens=model_config["max_tokens"],
            temperature=model_config["temperature"],
            system=system_prompt,
            messages=[{"role": "user", "content": query}]
        )
        
        return {
            "response": response.content[0].text,
            "confidence_score": 0.90,  # Anthropic doesn't provide confidence scores
            "tokens_used": response.usage.input_tokens + response.usage.output_tokens,
            "stop_reason": response.stop_reason
        }
    
    async def _create_system_prompt(
        self,
        language: str,
        tier: SupportTier,
        financial_context: Dict
    ) -> str:
        """Create contextual system prompt"""
        
        base_prompt = f"""You are an expert financial services AI assistant for GridWorks Infrastructure Services, 
        the leading B2B financial technology platform. You specialize in:

        1. Trading and investment strategies
        2. Financial market analysis
        3. Regulatory compliance (SEBI, RBI, global regulations)
        4. Risk management
        5. Portfolio optimization
        6. Technical analysis
        7. B2B financial infrastructure solutions

        Language: Respond in {language}
        Service Tier: {tier.value}
        
        Context: {json.dumps(financial_context, indent=2)}
        
        Guidelines:
        - Provide accurate, actionable financial advice
        - Include relevant market data and regulatory information
        - Suggest specific next steps when appropriate
        - Maintain professional tone suitable for financial professionals
        - If unsure, clearly state limitations and suggest human expert consultation
        """
        
        if tier == SupportTier.QUANTUM:
            base_prompt += """
        
        QUANTUM TIER ENHANCEMENTS:
        - Provide ultra-detailed analysis with multiple scenarios
        - Include quantitative models and calculations
        - Reference latest market research and regulatory updates
        - Offer custom implementation strategies
        - Provide direct access to GridWorks expert network if needed
        """
        
        return base_prompt
    
    async def _build_financial_context(
        self,
        query: str,
        client_id: str
    ) -> Dict[str, Any]:
        """Build financial context for the query"""
        
        # Cache key for context
        cache_key = f"financial_context:{hashlib.md5(query.encode()).hexdigest()[:8]}"
        
        # Check cache first
        cached_context = self.redis_client.get(cache_key)
        if cached_context:
            return json.loads(cached_context)
        
        context = {
            "market_status": await self._get_market_status(),
            "key_indices": await self._get_key_indices(),
            "regulatory_updates": await self._get_recent_regulatory_updates(),
            "client_tier": await self._get_client_tier(client_id)
        }
        
        # Cache for 5 minutes
        self.redis_client.setex(cache_key, 300, json.dumps(context))
        
        return context
    
    async def _get_market_status(self) -> Dict[str, Any]:
        """Get current market status"""
        # This would integrate with market data APIs
        return {
            "session": "open" if 9 <= datetime.now().hour <= 15 else "closed",
            "volatility": "moderate",
            "sentiment": "neutral"
        }
    
    async def _get_key_indices(self) -> Dict[str, float]:
        """Get key market indices"""
        # This would integrate with market data APIs
        return {
            "nifty_50": 21500.0,
            "sensex": 71000.0,
            "bank_nifty": 46500.0
        }
    
    async def _get_recent_regulatory_updates(self) -> List[str]:
        """Get recent regulatory updates"""
        return [
            "SEBI updates on AI-based trading algorithms",
            "RBI guidelines on digital payment systems",
            "New compliance requirements for fintech platforms"
        ]
    
    async def _get_client_tier(self, client_id: str) -> str:
        """Get client tier from database"""
        # This would query the database
        return "enterprise"


class SupportEngine:
    """
    Main AI Support Engine with multi-language support and channel integration
    """
    
    def __init__(self):
        self.model_orchestrator = AIModelOrchestrator()
        self.whatsapp_client = WhatsAppBusinessClient()
        self.redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
        
        # Response time SLAs per tier (seconds)
        self.response_slas = {
            SupportTier.COMMUNITY: 30,
            SupportTier.PROFESSIONAL: 15,
            SupportTier.ENTERPRISE: 5,
            SupportTier.QUANTUM: 2
        }
    
    async def process_support_request(
        self,
        request: SupportRequest,
        db: AsyncSession
    ) -> SupportResponse:
        """Process a support request and generate response"""
        
        start_time = datetime.utcnow()
        request_id = f"req_{int(start_time.timestamp())}_{request.client_id[:8]}"
        
        try:
            # Detect language if not provided
            if not request.language:
                request.language = await detect_language(request.query)
            
            # Get client tier and validate
            tier = await self._validate_client_tier(request.client_id, request.priority, db)
            
            # Check rate limits
            await self._check_rate_limits(request.client_id, tier)
            
            # Get AI response
            ai_response = await self.model_orchestrator.get_model_response(
                query=request.query,
                language=request.language,
                tier=tier,
                context=request.context,
                client_id=request.client_id
            )
            
            # Generate audio response if requested
            audio_response = None
            if request.context.get("response_format") in [ResponseFormat.AUDIO, ResponseFormat.BOTH]:
                audio_response = await generate_voice_response(
                    ai_response["response"],
                    request.language
                )
            
            # Calculate response time
            response_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            # Generate follow-up suggestions
            follow_ups = await self._generate_follow_up_suggestions(
                request.query,
                ai_response["response"],
                request.language
            )
            
            # Create response object
            response = SupportResponse(
                request_id=request_id,
                response_text=ai_response["response"],
                response_audio=audio_response,
                language=request.language,
                confidence_score=ai_response["confidence_score"],
                response_time_ms=response_time,
                tokens_used=ai_response["tokens_used"],
                model_used=ai_response["model_used"],
                follow_up_suggestions=follow_ups
            )
            
            # Log usage for billing
            await self._log_usage(request, response, db)
            
            # Send response via appropriate channel
            if request.channel == SupportChannel.WHATSAPP:
                await self._send_whatsapp_response(request, response)
            
            return response
            
        except Exception as e:
            # Log error and return error response
            await self._log_error(request_id, request, str(e), db)
            
            error_response = SupportResponse(
                request_id=request_id,
                response_text="I apologize, but I'm unable to process your request right now. Our team has been notified and will assist you shortly.",
                response_audio=None,
                language=request.language or "en",
                confidence_score=0.0,
                response_time_ms=int((datetime.utcnow() - start_time).total_seconds() * 1000),
                tokens_used=0,
                model_used="error_handler",
                follow_up_suggestions=[]
            )
            
            return error_response
    
    async def _validate_client_tier(
        self,
        client_id: str,
        requested_tier: SupportTier,
        db: AsyncSession
    ) -> SupportTier:
        """Validate client tier and return appropriate tier"""
        
        # Get client subscription
        result = await db.execute(
            select(EnterpriseClient).where(EnterpriseClient.id == client_id)
        )
        client = result.scalar_one_or_none()
        
        if not client:
            raise ValueError(f"Client {client_id} not found")
        
        # Map client tier to support tier
        tier_mapping = {
            "growth": SupportTier.COMMUNITY,
            "enterprise": SupportTier.PROFESSIONAL,
            "quantum": SupportTier.ENTERPRISE,
            "custom": SupportTier.QUANTUM
        }
        
        allowed_tier = tier_mapping.get(client.tier, SupportTier.COMMUNITY)
        
        # Return the lower of requested vs allowed tier
        tier_hierarchy = [
            SupportTier.COMMUNITY,
            SupportTier.PROFESSIONAL,
            SupportTier.ENTERPRISE,
            SupportTier.QUANTUM
        ]
        
        requested_level = tier_hierarchy.index(requested_tier)
        allowed_level = tier_hierarchy.index(allowed_tier)
        
        return tier_hierarchy[min(requested_level, allowed_level)]
    
    async def _check_rate_limits(self, client_id: str, tier: SupportTier):
        """Check rate limits for client and tier"""
        
        # Rate limits per tier (requests per hour)
        rate_limits = {
            SupportTier.COMMUNITY: 50,
            SupportTier.PROFESSIONAL: 200,
            SupportTier.ENTERPRISE: 1000,
            SupportTier.QUANTUM: 5000
        }
        
        rate_key = f"support_rate:{client_id}:{tier.value}"
        current_count = self.redis_client.incr(rate_key)
        
        if current_count == 1:
            self.redis_client.expire(rate_key, 3600)  # 1 hour
        
        if current_count > rate_limits[tier]:
            raise ValueError(f"Rate limit exceeded for tier {tier.value}")
    
    async def _generate_follow_up_suggestions(
        self,
        query: str,
        response: str,
        language: str
    ) -> List[str]:
        """Generate contextual follow-up suggestions"""
        
        # Simple keyword-based suggestions (can be enhanced with ML)
        suggestions = []
        
        if any(word in query.lower() for word in ["trading", "trade", "buy", "sell"]):
            suggestions.extend([
                "How do I implement risk management for this strategy?",
                "What are the regulatory requirements for this trade?",
                "Can you help me optimize my portfolio allocation?"
            ])
        
        if any(word in query.lower() for word in ["market", "analysis", "forecast"]):
            suggestions.extend([
                "What technical indicators should I consider?",
                "How do global markets affect this analysis?",
                "Can you provide sector-specific insights?"
            ])
        
        if any(word in query.lower() for word in ["compliance", "regulation", "sebi", "rbi"]):
            suggestions.extend([
                "What documentation do I need for compliance?",
                "How do I stay updated on regulatory changes?",
                "Can you help me with audit preparation?"
            ])
        
        # Translate suggestions to requested language
        if language != "en" and suggestions:
            translated_suggestions = []
            for suggestion in suggestions[:3]:  # Limit to 3 suggestions
                translated = await translate_text(suggestion, "en", language)
                translated_suggestions.append(translated)
            return translated_suggestions
        
        return suggestions[:3]
    
    async def _send_whatsapp_response(
        self,
        request: SupportRequest,
        response: SupportResponse
    ):
        """Send response via WhatsApp Business API"""
        
        if request.context.get("whatsapp_number"):
            await self.whatsapp_client.send_message(
                to_number=request.context["whatsapp_number"],
                message=response.response_text,
                audio_data=response.response_audio
            )
    
    async def _log_usage(
        self,
        request: SupportRequest,
        response: SupportResponse,
        db: AsyncSession
    ):
        """Log usage for billing and analytics"""
        
        usage_record = UsageRecord(
            client_id=request.client_id,
            service_type="ai_suite",
            service_name="support_engine",
            endpoint="ai_support",
            timestamp=datetime.utcnow(),
            request_count=1,
            response_time_ms=response.response_time_ms,
            billable_units=response.tokens_used / 1000,  # Per 1K tokens
            unit_cost=0.002,  # $0.002 per 1K tokens
            total_cost=response.tokens_used / 1000 * 0.002,
            metrics={
                "model_used": response.model_used,
                "language": response.language,
                "confidence_score": response.confidence_score,
                "channel": request.channel.value,
                "tier": request.priority.value
            }
        )
        
        db.add(usage_record)
        await db.commit()
    
    async def _log_error(
        self,
        request_id: str,
        request: SupportRequest,
        error_message: str,
        db: AsyncSession
    ):
        """Log errors for monitoring and debugging"""
        
        audit_log = AuditLog(
            client_id=request.client_id,
            user_id=request.user_id,
            event_type="ai_support.error",
            resource_type="support_request",
            resource_id=request_id,
            action="process_request",
            status="error",
            error_message=error_message,
            metadata={
                "query": request.query[:200],  # First 200 chars only
                "language": request.language,
                "channel": request.channel.value,
                "tier": request.priority.value
            },
            timestamp=datetime.utcnow()
        )
        
        db.add(audit_log)
        await db.commit()


# Dependency injection for FastAPI
support_engine = SupportEngine()

async def get_support_engine() -> SupportEngine:
    """Get support engine instance"""
    return support_engine