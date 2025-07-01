"""
Tier-Integrated AI API Endpoints
FastAPI endpoints that integrate AI services with user tier system
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from datetime import datetime

from app.tier_integration.tier_ai_manager import TierAIManager, UserTier
from app.models.user import User, get_current_user

router = APIRouter(prefix="/ai", tags=["AI Services"])
tier_ai_manager = TierAIManager()


# Request/Response Models
class SupportQueryRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = {}
    language: str = "english"


class SupportQueryResponse(BaseModel):
    success: bool
    message: str
    actions: List[Dict[str, Any]] = []
    response_time: float
    upsell_offer: Optional[Dict[str, Any]] = None
    quota_info: Optional[Dict[str, Any]] = None


class MorningPulseResponse(BaseModel):
    success: bool
    format: str
    content: Dict[str, Any]
    upsell_offer: Optional[Dict[str, Any]] = None


class ExpertGroupRequest(BaseModel):
    action: str
    group_id: Optional[str] = None
    message_content: Optional[str] = None
    group_settings: Optional[Dict[str, Any]] = {}


# AI Support Endpoints
@router.post("/support/query", response_model=SupportQueryResponse)
async def ai_support_query(
    request: SupportQueryRequest,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user)
):
    """
    Handle AI support query with tier-specific features and intelligent upselling
    """
    
    try:
        # Get user tier
        user_tier = UserTier(user.tier)
        
        # Process AI support request
        result = await tier_ai_manager.handle_ai_support_request(
            user_id=str(user.id),
            user_tier=user_tier,
            query=request.message,
            context={
                **request.context,
                "balance": user.balance,
                "recent_orders": await user.get_recent_orders(),
                "portfolio_value": user.portfolio_value
            }
        )
        
        # Background task for analytics
        background_tasks.add_task(
            track_ai_usage,
            user_id=user.id,
            service="support",
            tier=user_tier.value,
            success=result.get("success", False)
        )
        
        return SupportQueryResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI support error: {str(e)}")


@router.get("/support/quota")
async def get_support_quota(user: User = Depends(get_current_user)):
    """Get current AI support quota and usage"""
    
    user_tier = UserTier(user.tier)
    quota_info = await tier_ai_manager._check_support_quota(str(user.id), user_tier)
    
    return {
        "tier": user_tier.value,
        "quota": quota_info,
        "tier_limits": tier_ai_manager.AIServiceQuota.TIER_QUOTAS[user_tier]
    }


# Intelligence Service Endpoints
@router.get("/intelligence/morning-pulse", response_model=MorningPulseResponse)
async def get_morning_pulse(
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user)
):
    """
    Get morning pulse with tier-specific format and features
    """
    
    try:
        user_tier = UserTier(user.tier)
        
        result = await tier_ai_manager.handle_morning_pulse_request(
            user_id=str(user.id),
            user_tier=user_tier
        )
        
        # Background analytics
        background_tasks.add_task(
            track_ai_usage,
            user_id=user.id,
            service="intelligence",
            tier=user_tier.value,
            success=result.get("success", False)
        )
        
        return MorningPulseResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Intelligence service error: {str(e)}")


@router.post("/intelligence/custom-alert")
async def create_custom_alert(
    alert_config: Dict[str, Any],
    user: User = Depends(get_current_user)
):
    """Create custom market alert (Pro+ feature)"""
    
    user_tier = UserTier(user.tier)
    
    # Check tier access
    quota = tier_ai_manager.AIServiceQuota.TIER_QUOTAS[user_tier]
    
    if quota["custom_alerts"] == 0:
        upsell = await tier_ai_manager.upsell_triggers.get_intelligence_upsell(user_tier)
        raise HTTPException(
            status_code=402,
            detail={
                "error": "tier_restriction",
                "message": "Custom alerts available in Pro tier and above",
                "upsell": upsell
            }
        )
    
    # Create alert logic here
    return {
        "success": True,
        "alert_id": f"alert_{user.id}_{datetime.now().timestamp()}",
        "message": "Custom alert created successfully"
    }


# Expert Groups Endpoints
@router.post("/groups/action")
async def expert_group_action(
    request: ExpertGroupRequest,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user)
):
    """
    Handle expert group actions with tier-specific permissions
    """
    
    try:
        user_tier = UserTier(user.tier)
        
        result = await tier_ai_manager.handle_expert_group_request(
            user_id=str(user.id),
            user_tier=user_tier,
            action=request.action,
            data={
                "group_id": request.group_id,
                "message_content": request.message_content,
                "group_settings": request.group_settings,
                "user_profile": {
                    "username": user.username,
                    "display_name": user.display_name,
                    "reputation": user.reputation_score
                }
            }
        )
        
        # Background analytics
        background_tasks.add_task(
            track_ai_usage,
            user_id=user.id,
            service="moderator",
            tier=user_tier.value,
            success=result.get("success", False)
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Expert group error: {str(e)}")


@router.get("/groups/my-groups")
async def get_my_expert_groups(user: User = Depends(get_current_user)):
    """Get user's expert groups based on tier"""
    
    user_tier = UserTier(user.tier)
    quota = tier_ai_manager.AIServiceQuota.TIER_QUOTAS[user_tier]
    
    # Mock data - in production would query database
    groups = []
    
    if quota["group_access"] != "observer":
        groups = [
            {
                "group_id": "nifty_pro_signals",
                "name": "Nifty Pro Signals",
                "role": "member",
                "subscription_price": 1999,
                "expert": "Expert Raj"
            }
        ]
    
    if quota["group_access"] in ["creator", "platform_admin"]:
        groups.append({
            "group_id": f"my_expert_group_{user.id}",
            "name": f"{user.display_name}'s Trading Signals",
            "role": "owner",
            "members_count": 47,
            "monthly_revenue": 23500,
            "rating": 4.7
        })
    
    return {
        "groups": groups,
        "tier_access": quota["group_access"],
        "can_create_groups": quota.get("expert_verification", False)
    }


# Tier Management Endpoints
@router.get("/tier/features")
async def get_tier_features(user: User = Depends(get_current_user)):
    """Get current tier features and upgrade options"""
    
    user_tier = UserTier(user.tier)
    
    # Current tier features
    current_features = tier_ai_manager.AIServiceQuota.TIER_QUOTAS[user_tier]
    ai_config = await tier_ai_manager.get_user_ai_config(user_tier)
    
    # Next tier features (for upsell)
    next_tier = None
    next_features = None
    
    tier_progression = {
        UserTier.LITE: UserTier.PRO,
        UserTier.PRO: UserTier.ELITE,
        UserTier.ELITE: UserTier.BLACK
    }
    
    if user_tier in tier_progression:
        next_tier = tier_progression[user_tier]
        next_features = tier_ai_manager.AIServiceQuota.TIER_QUOTAS[next_tier]
    
    return {
        "current_tier": {
            "name": user_tier.value,
            "features": current_features,
            "ai_config": ai_config
        },
        "next_tier": {
            "name": next_tier.value if next_tier else None,
            "features": next_features,
            "upgrade_benefits": await get_upgrade_benefits(user_tier, next_tier) if next_tier else None
        },
        "usage_analytics": await get_user_ai_analytics(user.id)
    }


@router.post("/tier/upgrade-preview")
async def preview_tier_upgrade(
    target_tier: str,
    user: User = Depends(get_current_user)
):
    """Preview what user gets with tier upgrade"""
    
    current_tier = UserTier(user.tier)
    target_tier_enum = UserTier(target_tier)
    
    # Validate upgrade path
    valid_upgrades = {
        UserTier.LITE: [UserTier.PRO, UserTier.ELITE, UserTier.BLACK],
        UserTier.PRO: [UserTier.ELITE, UserTier.BLACK],
        UserTier.ELITE: [UserTier.BLACK]
    }
    
    if target_tier_enum not in valid_upgrades.get(current_tier, []):
        raise HTTPException(status_code=400, detail="Invalid upgrade path")
    
    # Get feature comparison
    current_features = tier_ai_manager.AIServiceQuota.TIER_QUOTAS[current_tier]
    target_features = tier_ai_manager.AIServiceQuota.TIER_QUOTAS[target_tier_enum]
    
    # Calculate ROI for user
    roi_analysis = await calculate_upgrade_roi(user, current_tier, target_tier_enum)
    
    return {
        "upgrade_summary": {
            "from": current_tier.value,
            "to": target_tier_enum.value,
            "new_features": get_feature_diff(current_features, target_features),
            "roi_analysis": roi_analysis
        },
        "pricing": get_tier_pricing(target_tier_enum),
        "trial_available": target_tier_enum in [UserTier.PRO, UserTier.ELITE]
    }


# Analytics and Insights
@router.get("/analytics/ai-usage")
async def get_ai_usage_analytics(user: User = Depends(get_current_user)):
    """Get detailed AI usage analytics for the user"""
    
    return await get_user_ai_analytics(user.id)


@router.get("/analytics/upsell-insights")
async def get_upsell_insights(user: User = Depends(get_current_user)):
    """Get personalized upsell insights based on usage patterns"""
    
    user_tier = UserTier(user.tier)
    
    # Check all upsell triggers
    support_upsell = await tier_ai_manager.upsell_triggers.check_support_upsell(str(user.id), user_tier)
    intelligence_upsell = await tier_ai_manager.upsell_triggers.check_intelligence_upsell(str(user.id), user_tier)
    moderator_upsell = await tier_ai_manager.upsell_triggers.check_moderator_upsell(str(user.id), user_tier)
    
    return {
        "current_tier": user_tier.value,
        "active_upsells": {
            "support": support_upsell,
            "intelligence": intelligence_upsell,
            "moderator": moderator_upsell
        },
        "usage_based_recommendations": await get_usage_recommendations(user.id, user_tier),
        "tier_progression_timeline": await get_progression_timeline(user.id, user_tier)
    }


# Helper Functions
async def track_ai_usage(user_id: int, service: str, tier: str, success: bool):
    """Background task to track AI service usage"""
    
    # In production, this would write to analytics database
    usage_data = {
        "user_id": user_id,
        "service": service,
        "tier": tier,
        "success": success,
        "timestamp": datetime.now().isoformat()
    }
    
    print(f"📊 AI Usage Tracked: {usage_data}")


async def get_upgrade_benefits(current_tier: UserTier, next_tier: UserTier) -> Dict[str, Any]:
    """Get specific benefits of upgrading to next tier"""
    
    benefits = {
        (UserTier.LITE, UserTier.PRO): {
            "support": "Unlimited queries + 15s response time + WhatsApp delivery",
            "intelligence": "Voice notes + 3 daily trade ideas + backtesting",
            "groups": "Join expert groups + participate in discussions",
            "roi_estimate": "Average Pro user makes ₹15,000 more per month"
        },
        (UserTier.PRO, UserTier.ELITE): {
            "support": "Personal AI butler + video support + 10s response",
            "intelligence": "5 trade ideas + video briefings + portfolio optimization", 
            "groups": "Create expert groups + earn up to ₹50,000/month",
            "roi_estimate": "Elite experts average ₹25,000 monthly revenue"
        },
        (UserTier.ELITE, UserTier.BLACK): {
            "support": "Dedicated manager + 5s response + institutional access",
            "intelligence": "Institutional research + unlimited alerts + multi-asset",
            "groups": "Platform admin + white label + unlimited earning",
            "roi_estimate": "Black users save ₹10L/year in research costs"
        }
    }
    
    return benefits.get((current_tier, next_tier), {})


async def calculate_upgrade_roi(user: User, current_tier: UserTier, target_tier: UserTier) -> Dict[str, Any]:
    """Calculate ROI for tier upgrade based on user's profile"""
    
    # Mock ROI calculation - in production would use ML models
    tier_prices = {
        UserTier.PRO: 999,
        UserTier.ELITE: 4999,
        UserTier.BLACK: 25000
    }
    
    upgrade_cost = tier_prices[target_tier]
    
    # Estimate benefits based on user profile
    portfolio_value = user.portfolio_value or 500000
    
    estimated_benefits = {
        UserTier.PRO: min(portfolio_value * 0.02, 15000),  # 2% or ₹15K max
        UserTier.ELITE: min(portfolio_value * 0.03, 35000), # 3% or ₹35K max  
        UserTier.BLACK: min(portfolio_value * 0.05, 100000) # 5% or ₹1L max
    }
    
    monthly_benefit = estimated_benefits[target_tier]
    payback_months = upgrade_cost / max(monthly_benefit - tier_prices.get(current_tier, 0), 1)
    
    return {
        "upgrade_cost": upgrade_cost,
        "estimated_monthly_benefit": monthly_benefit,
        "payback_period_months": round(payback_months, 1),
        "annual_roi_percentage": round(((monthly_benefit * 12) / upgrade_cost - 1) * 100, 1)
    }


async def get_user_ai_analytics(user_id: int) -> Dict[str, Any]:
    """Get comprehensive AI usage analytics for user"""
    
    # Mock analytics - in production would query database
    return {
        "daily_usage": {
            "support_queries": 12,
            "morning_pulse_opens": 8,
            "group_interactions": 25
        },
        "weekly_trends": {
            "most_active_service": "intelligence",
            "usage_growth": 15,  # 15% growth
            "engagement_score": 0.78
        },
        "feature_adoption": {
            "voice_notes": True,
            "trade_ideas": True,
            "expert_groups": True,
            "custom_alerts": False
        },
        "satisfaction_indicators": {
            "response_ratings": 4.6,
            "feature_usage_depth": 0.82,
            "retention_probability": 0.91
        }
    }


async def get_usage_recommendations(user_id: int, user_tier: UserTier) -> List[Dict[str, Any]]:
    """Get personalized usage recommendations"""
    
    recommendations = []
    
    if user_tier == UserTier.LITE:
        recommendations = [
            {
                "type": "feature_discovery",
                "title": "Try Morning Voice Intelligence",
                "description": "Get trade ideas delivered via WhatsApp voice notes",
                "action": "upgrade_to_pro"
            }
        ]
    elif user_tier == UserTier.PRO:
        recommendations = [
            {
                "type": "monetization",
                "title": "Start Your Expert Group",
                "description": "Your accuracy is 78% - start earning from your calls",
                "action": "upgrade_to_elite"
            }
        ]
    
    return recommendations


async def get_progression_timeline(user_id: int, user_tier: UserTier) -> Dict[str, Any]:
    """Get personalized tier progression timeline"""
    
    if user_tier == UserTier.LITE:
        return {
            "current_tier": "lite",
            "next_milestone": "pro",
            "estimated_timeline": "2-4 weeks based on your usage",
            "requirements": [
                "Use morning pulse for 7 days",
                "Make 3 profitable trades using AI insights",
                "Try expert group trial"
            ]
        }
    elif user_tier == UserTier.PRO:
        return {
            "current_tier": "pro", 
            "next_milestone": "elite",
            "estimated_timeline": "1-2 months based on your portfolio",
            "requirements": [
                "Build consistent track record (60+ days)",
                "Portfolio value ₹5L+ recommended",
                "High engagement with AI features"
            ]
        }
    else:
        return {"message": "You're at a premium tier!"}


def get_feature_diff(current_features: Dict, target_features: Dict) -> List[str]:
    """Get list of new features in target tier"""
    
    new_features = []
    
    for key, value in target_features.items():
        current_value = current_features.get(key)
        
        if current_value != value:
            if isinstance(value, bool) and value and not current_value:
                new_features.append(f"✅ {key.replace('_', ' ').title()}")
            elif isinstance(value, (int, str)) and value != current_value:
                new_features.append(f"📈 {key.replace('_', ' ').title()}: {current_value} → {value}")
    
    return new_features


def get_tier_pricing(tier: UserTier) -> Dict[str, Any]:
    """Get pricing information for tier"""
    
    pricing = {
        UserTier.PRO: {
            "monthly": 999,
            "annual": 9990,  # 2 months free
            "trial": "7 days free"
        },
        UserTier.ELITE: {
            "monthly": 4999,
            "annual": 49990,  # 2 months free
            "trial": "14 days free"
        },
        UserTier.BLACK: {
            "monthly": 25000,
            "annual": 250000,  # 2 months free
            "trial": "Personal consultation"
        }
    }
    
    return pricing.get(tier, {})