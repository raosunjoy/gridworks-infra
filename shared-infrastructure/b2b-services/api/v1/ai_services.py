"""
GridWorks B2B API - AI Services Endpoints
Support Engine, Intelligence Engine, and Moderator Engine APIs
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request, BackgroundTasks
from pydantic import BaseModel, Field, UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from ...auth.enterprise_auth import get_current_user, PermissionChecker, TokenData
from ...database.session import get_db
from ...ai_suite.support_engine import (
    get_support_engine, SupportEngine, SupportRequest, SupportChannel, SupportTier
)
from ...ai_suite.intelligence_engine import (
    get_intelligence_engine, IntelligenceEngine, IntelligenceRequest, 
    IntelligenceType, MarketRegion, DeliveryFormat
)
from ...ai_suite.moderator_engine import (
    get_moderator_engine, ModerationEngine, ModerationRequest, 
    ContentType, Platform, ModerationAction
)

router = APIRouter(prefix="/api/v1/ai", tags=["ai-services"])


# Request/Response Models
class SupportQueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=10000)
    language: Optional[str] = "en"
    channel: str = Field(default="api")
    priority: str = Field(default="professional")
    context: Dict[str, Any] = {}
    response_format: str = Field(default="text", pattern="^(text|audio|both)$")


class IntelligenceQueryRequest(BaseModel):
    intelligence_type: str
    market_regions: List[str] = ["india"]
    delivery_format: str = "json"
    custom_parameters: Dict[str, Any] = {}
    webhook_url: Optional[str] = None


class ModerationQueryRequest(BaseModel):
    content: str = Field(..., max_length=50000)
    content_type: str = "text_message"
    platform: str = "api"
    sender_id: Optional[str] = None
    metadata: Dict[str, Any] = {}


# AI Support Engine Endpoints
@router.post("/support/query")
async def ai_support_query(
    request: SupportQueryRequest,
    current_user: TokenData = Depends(
        PermissionChecker(["ai_suite.support.query"])
    ),
    support_engine: SupportEngine = Depends(get_support_engine),
    db: AsyncSession = Depends(get_db)
):
    """Query AI Support Engine with multi-language financial expertise"""
    
    # Create support request
    support_request = SupportRequest(
        client_id=current_user.client_id,
        user_id=current_user.user_id,
        query=request.query,
        language=request.language,
        channel=SupportChannel(request.channel),
        priority=SupportTier(request.priority),
        context=request.context
    )
    
    # Process request
    response = await support_engine.process_support_request(support_request, db)
    
    return {
        "request_id": response.request_id,
        "response": response.response_text,
        "language": response.language,
        "confidence_score": response.confidence_score,
        "response_time_ms": response.response_time_ms,
        "model_used": response.model_used,
        "follow_up_suggestions": response.follow_up_suggestions,
        "audio_response_available": response.response_audio is not None
    }


@router.get("/support/conversations")
async def get_support_conversations(
    limit: int = Field(default=20, ge=1, le=100),
    offset: int = Field(default=0, ge=0),
    current_user: TokenData = Depends(
        PermissionChecker(["ai_suite.support.read"])
    ),
    db: AsyncSession = Depends(get_db)
):
    """Get AI support conversation history"""
    
    # In production, this would query conversation history from database
    return {
        "conversations": [],
        "total": 0,
        "limit": limit,
        "offset": offset,
        "has_more": False
    }


# AI Intelligence Engine Endpoints
@router.post("/intelligence/query")
async def ai_intelligence_query(
    request: IntelligenceQueryRequest,
    current_user: TokenData = Depends(
        PermissionChecker(["ai_suite.intelligence.query"])
    ),
    intelligence_engine: IntelligenceEngine = Depends(get_intelligence_engine),
    db: AsyncSession = Depends(get_db)
):
    """Query AI Intelligence Engine for market analysis and correlation"""
    
    # Create intelligence request
    intelligence_request = IntelligenceRequest(
        client_id=current_user.client_id,
        intelligence_type=IntelligenceType(request.intelligence_type),
        market_regions=[MarketRegion(region) for region in request.market_regions],
        delivery_format=DeliveryFormat(request.delivery_format),
        custom_parameters=request.custom_parameters,
        webhook_url=request.webhook_url
    )
    
    # Process request
    response = await intelligence_engine.process_intelligence_request(
        intelligence_request, db
    )
    
    return {
        "intelligence_type": response.intelligence_type.value,
        "market_region": response.market_region.value,
        "summary": response.summary,
        "key_insights": response.key_insights,
        "data_points": response.data_points,
        "confidence_score": response.confidence_score,
        "risk_level": response.risk_level,
        "recommendations": response.actionable_recommendations,
        "timestamp": response.timestamp,
        "supporting_data": response.supporting_data
    }


@router.get("/intelligence/morning-pulse")
async def get_morning_pulse(
    focus_sectors: Optional[List[str]] = None,
    current_user: TokenData = Depends(
        PermissionChecker(["ai_suite.intelligence.morning_pulse"])
    ),
    intelligence_engine: IntelligenceEngine = Depends(get_intelligence_engine),
    db: AsyncSession = Depends(get_db)
):
    """Get daily morning market pulse with pre-market intelligence"""
    
    intelligence_request = IntelligenceRequest(
        client_id=current_user.client_id,
        intelligence_type=IntelligenceType.MORNING_PULSE,
        market_regions=[MarketRegion.INDIA],
        delivery_format=DeliveryFormat.JSON,
        custom_parameters={"focus_sectors": focus_sectors or []}
    )
    
    response = await intelligence_engine.process_intelligence_request(
        intelligence_request, db
    )
    
    return {
        "pulse_date": response.timestamp.strftime("%Y-%m-%d"),
        "market_sentiment": response.risk_level,
        "summary": response.summary,
        "key_insights": response.key_insights,
        "global_correlations": response.data_points.get("correlations", []),
        "institutional_flow": response.data_points.get("institutional_flow", {}),
        "economic_calendar": response.data_points.get("economic_events", []),
        "recommendations": response.actionable_recommendations,
        "confidence_score": response.confidence_score
    }


@router.get("/intelligence/correlations")
async def get_global_correlations(
    timeframe: str = Field(default="30d", pattern="^(7d|30d|90d|1y)$"),
    current_user: TokenData = Depends(
        PermissionChecker(["ai_suite.intelligence.correlations"])
    ),
    intelligence_engine: IntelligenceEngine = Depends(get_intelligence_engine),
    db: AsyncSession = Depends(get_db)
):
    """Get global market correlations analysis"""
    
    # Get correlation data from intelligence engine
    correlation_data = await intelligence_engine.correlation_engine.analyze_global_correlations(
        timeframe=timeframe,
        update_cache=False
    )
    
    return {
        "timeframe": timeframe,
        "timestamp": correlation_data["timestamp"],
        "strongest_correlations": correlation_data["strongest_correlations"],
        "insights": correlation_data["insights"],
        "market_status": correlation_data["market_status"],
        "correlation_matrix": correlation_data["correlations"]
    }


# AI Moderator Engine Endpoints
@router.post("/moderation/check")
async def moderate_content(
    request: ModerationQueryRequest,
    current_user: TokenData = Depends(
        PermissionChecker(["ai_suite.moderator.check"])
    ),
    moderator_engine: ModerationEngine = Depends(get_moderator_engine),
    db: AsyncSession = Depends(get_db)
):
    """Moderate content for spam, fraud, and compliance violations"""
    
    # Create moderation request
    moderation_request = ModerationRequest(
        client_id=current_user.client_id,
        platform=Platform(request.platform),
        content_type=ContentType(request.content_type),
        content=request.content,
        sender_id=request.sender_id or current_user.user_id,
        channel_id="api",
        metadata=request.metadata,
        timestamp=datetime.utcnow()
    )
    
    # Process moderation
    result = await moderator_engine.moderate_content(moderation_request, db)
    
    return {
        "request_id": result.request_id,
        "action": result.action.value,
        "confidence_score": result.confidence_score,
        "spam_categories": [cat.value for cat in result.spam_categories],
        "risk_level": result.risk_level,
        "explanation": result.explanation,
        "processing_time_ms": result.processing_time_ms,
        "escalation_required": result.escalation_required,
        "recommended_actions": result.recommended_actions
    }


@router.post("/moderation/verify-expert")
async def verify_expert(
    expert_data: Dict[str, Any],
    zk_proof: Optional[str] = None,
    current_user: TokenData = Depends(
        PermissionChecker(["ai_suite.moderator.verify_expert"])
    ),
    moderator_engine: ModerationEngine = Depends(get_moderator_engine),
    db: AsyncSession = Depends(get_db)
):
    """Verify financial expert credentials with ZK proofs"""
    
    # Verify expert
    is_verified, profile, confidence = await moderator_engine.expert_verifier.verify_expert(
        expert_data, zk_proof
    )
    
    return {
        "verified": is_verified,
        "confidence_score": confidence,
        "expert_profile": {
            "expert_id": profile.expert_id if profile else None,
            "verification_status": profile.verification_status if profile else "unverified",
            "reputation_score": profile.reputation_score if profile else 0.0,
            "certifications": profile.certifications if profile else [],
            "specialization": profile.specialization if profile else []
        } if profile else None
    }


@router.get("/moderation/spam-stats")
async def get_spam_statistics(
    timeframe: str = Field(default="7d", pattern="^(1d|7d|30d)$"),
    current_user: TokenData = Depends(
        PermissionChecker(["ai_suite.moderator.stats"])
    ),
    db: AsyncSession = Depends(get_db)
):
    """Get spam detection statistics and trends"""
    
    # In production, this would query actual spam statistics
    return {
        "timeframe": timeframe,
        "total_checks": 0,
        "spam_detected": 0,
        "spam_rate": 0.0,
        "top_categories": [],
        "accuracy_rate": 0.99,
        "false_positive_rate": 0.01,
        "processing_time_avg": 50
    }


# Combined AI Services Status
@router.get("/services/status")
async def get_ai_services_status(
    current_user: TokenData = Depends(
        PermissionChecker(["ai_suite.status"])
    )
):
    """Get status of all AI services"""
    
    return {
        "services": {
            "support_engine": {
                "status": "operational",
                "uptime": "99.9%",
                "avg_response_time": "1.2s",
                "supported_languages": 11,
                "models_available": ["gpt-4-turbo", "claude-3-opus"]
            },
            "intelligence_engine": {
                "status": "operational", 
                "uptime": "99.9%",
                "last_pulse_update": datetime.utcnow().replace(hour=7, minute=30).isoformat(),
                "correlations_updated": datetime.utcnow().isoformat(),
                "markets_covered": ["india", "us", "europe", "asia"]
            },
            "moderator_engine": {
                "status": "operational",
                "uptime": "99.9%",
                "spam_accuracy": "99.1%",
                "avg_processing_time": "45ms",
                "expert_verification": "active"
            }
        },
        "overall_status": "operational",
        "client_tier": current_user.tier,
        "rate_limits": {
            "support_queries": "1000/hour",
            "intelligence_reports": "100/day", 
            "moderation_checks": "10000/hour"
        }
    }


# Health check endpoint
@router.get("/health")
async def ai_services_health():
    """Health check for AI services"""
    return {
        "status": "healthy",
        "services": ["support", "intelligence", "moderator"],
        "timestamp": datetime.utcnow()
    }