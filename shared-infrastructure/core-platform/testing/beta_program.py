"""?
GridWorks Beta Testing Program

Manages the beta testing program for the advanced charting platform.
Handles user registration, access control, feedback collection, and analytics.
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
import uuid
import json

from app.core.database import get_db
from app.core.auth import get_current_user
from app.core.logging import logger
from app.models.beta_testing import BetaUser, BetaFeedback, BetaSession, BetaMetrics
from app.services.notification import NotificationService
from app.services.analytics import AnalyticsService

router = APIRouter(prefix="/api/v1/beta", tags=["beta-testing"])

# Pydantic models
class BetaRegistrationRequest(BaseModel):
    user_id: str
    email: str
    phone: Optional[str] = None
    trading_experience: str = Field(..., description="Beginner, Intermediate, Advanced")
    primary_use_case: str
    platform_preference: str = Field(..., description="Web, Mobile, Both")
    current_tools: List[str] = Field(default_factory=list)
    expectations: str
    availability: Dict[str, Any] = Field(default_factory=dict)

class BetaFeedbackRequest(BaseModel):
    feature: str
    rating: int = Field(..., ge=1, le=5)
    feedback_text: str
    bug_reports: List[Dict[str, Any]] = Field(default_factory=list)
    suggestions: str = ""
    usability_score: int = Field(..., ge=1, le=10)
    performance_rating: int = Field(..., ge=1, le=5)
    likelihood_to_recommend: int = Field(..., ge=1, le=10)

class BetaSessionRequest(BaseModel):
    feature_tested: str
    duration_minutes: int
    tasks_completed: List[str]
    issues_encountered: List[Dict[str, Any]] = Field(default_factory=list)
    performance_metrics: Dict[str, Any] = Field(default_factory=dict)
    user_satisfaction: int = Field(..., ge=1, le=5)

class BetaAnalyticsRequest(BaseModel):
    event_name: str
    event_data: Dict[str, Any]
    session_id: str
    timestamp: Optional[datetime] = None

# Response models
class BetaUserResponse(BaseModel):
    beta_user_id: str
    status: str
    access_level: str
    features_enabled: List[str]
    feedback_count: int
    sessions_count: int
    joined_date: datetime

class BetaStatsResponse(BaseModel):
    total_users: int
    active_users: int
    feedback_items: int
    average_rating: float
    completion_rate: float
    top_features: List[Dict[str, Any]]
    bug_count: int


class BetaTestingManager:
    """Manages the beta testing program"""
    
    def __init__(self):
        self.notification_service = NotificationService()
        self.analytics_service = AnalyticsService()
        
        # Beta program configuration
        self.config = {
            'max_beta_users': 500,
            'auto_approval': False,
            'testing_phases': {
                'phase_1': {
                    'name': 'Core Charting Features',
                    'max_users': 50,
                    'features': ['basic_charts', 'indicators', 'real_time_data'],
                    'duration_days': 14
                },
                'phase_2': {
                    'name': 'Advanced Features',
                    'max_users': 150,
                    'features': ['drawing_tools', 'voice_commands', 'ai_patterns'],
                    'duration_days': 21
                },
                'phase_3': {
                    'name': 'Full Platform',
                    'max_users': 300,
                    'features': ['all_features'],
                    'duration_days': 30
                }
            }
        }
    
    async def register_beta_user(self, db: Session, registration: BetaRegistrationRequest) -> BetaUser:
        """Register a new beta user"""
        
        # Check if user is already registered
        existing_user = db.query(BetaUser).filter(
            BetaUser.user_id == registration.user_id
        ).first()
        
        if existing_user:
            raise HTTPException(status_code=400, detail="User already registered for beta")
        
        # Check capacity
        current_users = db.query(BetaUser).filter(
            BetaUser.status.in_(['approved', 'active'])
        ).count()
        
        if current_users >= self.config['max_beta_users']:
            raise HTTPException(status_code=400, detail="Beta program is currently full")
        
        # Determine phase and access level
        phase = self._determine_phase(db, registration)
        access_level = self._determine_access_level(registration)
        
        # Create beta user
        beta_user = BetaUser(
            beta_user_id=str(uuid.uuid4()),
            user_id=registration.user_id,
            email=registration.email,
            phone=registration.phone,
            status='pending' if not self.config['auto_approval'] else 'approved',
            access_level=access_level,
            phase=phase,
            trading_experience=registration.trading_experience,
            primary_use_case=registration.primary_use_case,
            platform_preference=registration.platform_preference,
            current_tools=json.dumps(registration.current_tools),
            expectations=registration.expectations,
            availability=json.dumps(registration.availability),
            features_enabled=json.dumps(self.config['testing_phases'][phase]['features']),
            joined_date=datetime.utcnow()
        )
        
        db.add(beta_user)
        db.commit()
        db.refresh(beta_user)
        
        # Send welcome email
        await self._send_welcome_email(beta_user)
        
        # Track registration event
        await self.analytics_service.track_event({
            'event': 'beta_user_registered',
            'user_id': registration.user_id,
            'phase': phase,
            'access_level': access_level
        })
        
        return beta_user
    
    def _determine_phase(self, db: Session, registration: BetaRegistrationRequest) -> str:
        """Determine which testing phase the user should join"""
        
        # Count users in each phase
        phase_counts = {}
        for phase_id in self.config['testing_phases']:
            count = db.query(BetaUser).filter(
                BetaUser.phase == phase_id,
                BetaUser.status.in_(['approved', 'active'])
            ).count()
            phase_counts[phase_id] = count
        
        # Assign to earliest available phase
        for phase_id, phase_config in self.config['testing_phases'].items():
            if phase_counts.get(phase_id, 0) < phase_config['max_users']:
                return phase_id
        
        # Default to last phase if all are full
        return 'phase_3'
    
    def _determine_access_level(self, registration: BetaRegistrationRequest) -> str:
        """Determine access level based on user profile"""
        
        # Premium access for experienced traders
        if registration.trading_experience == 'Advanced':
            return 'premium'
        
        # Standard access for most users
        elif registration.trading_experience == 'Intermediate':
            return 'standard'
        
        # Basic access for beginners
        else:
            return 'basic'
    
    async def _send_welcome_email(self, beta_user: BetaUser):
        """Send welcome email to beta user"""
        
        try:
            await self.notification_service.send_email(
                to=beta_user.email,
                subject="Welcome to GridWorks Beta Program!",
                template="beta_welcome",
                data={
                    'user_id': beta_user.user_id,
                    'phase': beta_user.phase,
                    'access_level': beta_user.access_level,
                    'features': json.loads(beta_user.features_enabled)
                }
            )
        except Exception as e:
            logger.error(f"Failed to send beta welcome email: {e}")
    
    async def collect_feedback(self, db: Session, user_id: str, feedback: BetaFeedbackRequest) -> BetaFeedback:
        """Collect feedback from beta user"""
        
        # Verify beta user
        beta_user = db.query(BetaUser).filter(
            BetaUser.user_id == user_id,
            BetaUser.status == 'active'
        ).first()
        
        if not beta_user:
            raise HTTPException(status_code=404, detail="Beta user not found or not active")
        
        # Create feedback record
        feedback_record = BetaFeedback(
            feedback_id=str(uuid.uuid4()),
            beta_user_id=beta_user.beta_user_id,
            feature=feedback.feature,
            rating=feedback.rating,
            feedback_text=feedback.feedback_text,
            bug_reports=json.dumps(feedback.bug_reports),
            suggestions=feedback.suggestions,
            usability_score=feedback.usability_score,
            performance_rating=feedback.performance_rating,
            likelihood_to_recommend=feedback.likelihood_to_recommend,
            submitted_date=datetime.utcnow()
        )
        
        db.add(feedback_record)
        db.commit()
        db.refresh(feedback_record)
        
        # Update user feedback count
        beta_user.feedback_count = (beta_user.feedback_count or 0) + 1
        db.commit()
        
        # Track feedback event
        await self.analytics_service.track_event({
            'event': 'beta_feedback_submitted',
            'user_id': user_id,
            'feature': feedback.feature,
            'rating': feedback.rating,
            'usability_score': feedback.usability_score
        })
        
        # Send acknowledgment
        await self._send_feedback_acknowledgment(beta_user, feedback_record)
        
        return feedback_record
    
    async def _send_feedback_acknowledgment(self, beta_user: BetaUser, feedback: BetaFeedback):
        """Send feedback acknowledgment to beta user"""
        
        try:
            await self.notification_service.send_email(
                to=beta_user.email,
                subject="Thank you for your feedback!",
                template="feedback_acknowledgment",
                data={
                    'feature': feedback.feature,
                    'rating': feedback.rating
                }
            )
        except Exception as e:
            logger.error(f"Failed to send feedback acknowledgment: {e}")
    
    async def log_session(self, db: Session, user_id: str, session: BetaSessionRequest) -> BetaSession:
        """Log a beta testing session"""
        
        # Verify beta user
        beta_user = db.query(BetaUser).filter(
            BetaUser.user_id == user_id,
            BetaUser.status == 'active'
        ).first()
        
        if not beta_user:
            raise HTTPException(status_code=404, detail="Beta user not found or not active")
        
        # Create session record
        session_record = BetaSession(
            session_id=str(uuid.uuid4()),
            beta_user_id=beta_user.beta_user_id,
            feature_tested=session.feature_tested,
            duration_minutes=session.duration_minutes,
            tasks_completed=json.dumps(session.tasks_completed),
            issues_encountered=json.dumps(session.issues_encountered),
            performance_metrics=json.dumps(session.performance_metrics),
            user_satisfaction=session.user_satisfaction,
            session_date=datetime.utcnow()
        )
        
        db.add(session_record)
        db.commit()
        db.refresh(session_record)
        
        # Update user session count
        beta_user.sessions_count = (beta_user.sessions_count or 0) + 1
        db.commit()
        
        # Track session event
        await self.analytics_service.track_event({
            'event': 'beta_session_completed',
            'user_id': user_id,
            'feature': session.feature_tested,
            'duration': session.duration_minutes,
            'satisfaction': session.user_satisfaction
        })
        
        return session_record
    
    def get_beta_statistics(self, db: Session) -> Dict[str, Any]:
        """Get comprehensive beta program statistics"""
        
        # Basic counts
        total_users = db.query(BetaUser).count()
        active_users = db.query(BetaUser).filter(BetaUser.status == 'active').count()
        feedback_items = db.query(BetaFeedback).count()
        
        # Average rating
        avg_rating_result = db.query(db.func.avg(BetaFeedback.rating)).scalar()
        average_rating = float(avg_rating_result) if avg_rating_result else 0.0
        
        # Completion rate (users who completed at least one session)
        completed_users = db.query(BetaUser).filter(BetaUser.sessions_count > 0).count()
        completion_rate = (completed_users / total_users * 100) if total_users > 0 else 0.0
        
        # Top features by feedback volume
        top_features = db.query(
            BetaFeedback.feature,
            db.func.count(BetaFeedback.feedback_id).label('feedback_count'),
            db.func.avg(BetaFeedback.rating).label('avg_rating')
        ).group_by(BetaFeedback.feature).order_by(
            db.func.count(BetaFeedback.feedback_id).desc()
        ).limit(10).all()
        
        # Bug count
        bug_count = db.query(BetaFeedback).filter(
            BetaFeedback.bug_reports != '[]'
        ).count()
        
        return {
            'total_users': total_users,
            'active_users': active_users,
            'feedback_items': feedback_items,
            'average_rating': round(average_rating, 2),
            'completion_rate': round(completion_rate, 2),
            'top_features': [
                {
                    'feature': feature.feature,
                    'feedback_count': feature.feedback_count,
                    'avg_rating': round(float(feature.avg_rating), 2)
                }
                for feature in top_features
            ],
            'bug_count': bug_count
        }


# Initialize beta testing manager
beta_manager = BetaTestingManager()


# API Endpoints
@router.post("/register", response_model=BetaUserResponse)
async def register_for_beta(
    registration: BetaRegistrationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Register for the beta testing program"""
    
    try:
        beta_user = await beta_manager.register_beta_user(db, registration)
        
        return BetaUserResponse(
            beta_user_id=beta_user.beta_user_id,
            status=beta_user.status,
            access_level=beta_user.access_level,
            features_enabled=json.loads(beta_user.features_enabled),
            feedback_count=beta_user.feedback_count or 0,
            sessions_count=beta_user.sessions_count or 0,
            joined_date=beta_user.joined_date
        )
    
    except Exception as e:
        logger.error(f"Beta registration error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/feedback")
async def submit_feedback(
    feedback: BetaFeedbackRequest,
    user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit beta testing feedback"""
    
    try:
        feedback_record = await beta_manager.collect_feedback(
            db, user["id"], feedback
        )
        
        return {
            "success": True,
            "feedback_id": feedback_record.feedback_id,
            "message": "Thank you for your feedback!"
        }
    
    except Exception as e:
        logger.error(f"Feedback submission error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/session")
async def log_testing_session(
    session: BetaSessionRequest,
    user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Log a beta testing session"""
    
    try:
        session_record = await beta_manager.log_session(
            db, user["id"], session
        )
        
        return {
            "success": True,
            "session_id": session_record.session_id,
            "message": "Session logged successfully"
        }
    
    except Exception as e:
        logger.error(f"Session logging error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_beta_status(
    user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's beta testing status"""
    
    beta_user = db.query(BetaUser).filter(
        BetaUser.user_id == user["id"]
    ).first()
    
    if not beta_user:
        return {"enrolled": False}
    
    return {
        "enrolled": True,
        "status": beta_user.status,
        "access_level": beta_user.access_level,
        "phase": beta_user.phase,
        "features_enabled": json.loads(beta_user.features_enabled),
        "feedback_count": beta_user.feedback_count or 0,
        "sessions_count": beta_user.sessions_count or 0
    }


@router.get("/statistics", response_model=BetaStatsResponse)
async def get_beta_statistics(
    user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get beta program statistics (admin only)"""
    
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    stats = beta_manager.get_beta_statistics(db)
    
    return BetaStatsResponse(**stats)


@router.post("/analytics")
async def track_beta_analytics(
    analytics: BetaAnalyticsRequest,
    user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Track beta testing analytics events"""
    
    try:
        # Verify beta user
        beta_user = db.query(BetaUser).filter(
            BetaUser.user_id == user["id"],
            BetaUser.status == 'active'
        ).first()
        
        if not beta_user:
            raise HTTPException(status_code=404, detail="Beta user not found")
        
        # Create metrics record
        metrics_record = BetaMetrics(
            metrics_id=str(uuid.uuid4()),
            beta_user_id=beta_user.beta_user_id,
            session_id=analytics.session_id,
            event_name=analytics.event_name,
            event_data=json.dumps(analytics.event_data),
            timestamp=analytics.timestamp or datetime.utcnow()
        )
        
        db.add(metrics_record)
        db.commit()
        
        # Track in analytics service
        await beta_manager.analytics_service.track_event({
            'event': f'beta_{analytics.event_name}',
            'user_id': user["id"],
            'session_id': analytics.session_id,
            **analytics.event_data
        })
        
        return {"success": True, "message": "Analytics tracked"}
    
    except Exception as e:
        logger.error(f"Analytics tracking error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users")
async def list_beta_users(
    user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """List beta users (admin only)"""
    
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    beta_users = db.query(BetaUser).offset(skip).limit(limit).all()
    
    return [
        {
            "beta_user_id": bu.beta_user_id,
            "user_id": bu.user_id,
            "email": bu.email,
            "status": bu.status,
            "access_level": bu.access_level,
            "phase": bu.phase,
            "feedback_count": bu.feedback_count or 0,
            "sessions_count": bu.sessions_count or 0,
            "joined_date": bu.joined_date
        }
        for bu in beta_users
    ]


@router.post("/users/{beta_user_id}/approve")
async def approve_beta_user(
    beta_user_id: str,
    user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Approve a beta user (admin only)"""
    
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    beta_user = db.query(BetaUser).filter(
        BetaUser.beta_user_id == beta_user_id
    ).first()
    
    if not beta_user:
        raise HTTPException(status_code=404, detail="Beta user not found")
    
    beta_user.status = 'active'
    beta_user.approved_date = datetime.utcnow()
    db.commit()
    
    # Send approval notification
    try:
        await beta_manager.notification_service.send_email(
            to=beta_user.email,
            subject="GridWorks Beta Access Approved!",
            template="beta_approval",
            data={
                'access_level': beta_user.access_level,
                'features': json.loads(beta_user.features_enabled)
            }
        )
    except Exception as e:
        logger.error(f"Failed to send approval email: {e}")
    
    return {"success": True, "message": "Beta user approved"}


# Health check
@router.get("/health")
async def beta_health_check():
    """Health check for beta testing system"""
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "beta_program": "active"
    }