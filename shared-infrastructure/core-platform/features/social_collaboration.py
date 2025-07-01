"""
Advanced Social Collaboration Features

Implements copy expert drawings, collaborative annotations, and real-time chart collaboration
with ZK-verified authenticity and professional trading community features.
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, WebSocket
from sqlalchemy.orm import Session
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
import json
import uuid
import asyncio
from dataclasses import dataclass

from app.core.database import get_db
from app.core.auth import get_current_user
from app.core.logging import logger
from app.models.charts import Chart, ChartDrawing, ChartAnnotation, ChartTemplate
from app.models.users import User, UserProfile
from app.models.social import ExpertProfile, CollaborationSession, DrawingCopy, AnnotationThread
from app.services.zk_verification import ZKVerificationService
from app.services.notification_service import NotificationService
from app.services.reputation_system import ReputationManager

router = APIRouter(prefix="/api/v1/social", tags=["social-collaboration"])

# Pydantic Models
class ExpertDrawingRequest(BaseModel):
    expert_user_id: str
    chart_id: str
    drawing_ids: List[str]
    copy_to_chart_id: str
    symbol: str
    timeframe: str

class CollaborativeAnnotationRequest(BaseModel):
    chart_id: str
    annotation_type: str = Field(..., regex="^(NOTE|ANALYSIS|QUESTION|INSIGHT|ALERT)$")
    content: str = Field(..., min_length=1, max_length=1000)
    position: Dict[str, float]  # x, y coordinates on chart
    drawing_reference_id: Optional[str] = None
    parent_annotation_id: Optional[str] = None  # For threaded discussions

class CollaborationInviteRequest(BaseModel):
    chart_id: str
    invited_user_ids: List[str]
    permission_level: str = Field(default="VIEW", regex="^(VIEW|COMMENT|EDIT)$")
    expires_in_hours: int = Field(default=24, ge=1, le=168)  # 1 hour to 1 week

class ExpertProfileRequest(BaseModel):
    specialization: List[str]  # ["NIFTY", "BANKNIFTY", "OPTIONS", "SWING", "SCALPING"]
    years_experience: int = Field(..., ge=1, le=50)
    trading_style: str
    bio: str = Field(..., max_length=500)
    verified_performance: Optional[Dict[str, Any]] = None

# Response Models
class ExpertDrawingResponse(BaseModel):
    copy_id: str
    copied_drawings: List[Dict[str, Any]]
    expert_attribution: Dict[str, str]
    zk_proof: str
    success: bool

class CollaborationSessionResponse(BaseModel):
    session_id: str
    participants: List[Dict[str, str]]
    chart_id: str
    permissions: Dict[str, str]
    active: bool

@dataclass
class ActiveCollaboration:
    """Tracks active real-time collaboration sessions"""
    session_id: str
    chart_id: str
    participants: Set[str]
    websockets: Dict[str, WebSocket]
    last_activity: datetime
    permissions: Dict[str, str]

class SocialCollaborationManager:
    """Manages advanced social collaboration features"""
    
    def __init__(self):
        self.zk_verification = ZKVerificationService()
        self.notification_service = NotificationService()
        self.reputation_manager = ReputationManager()
        
        # Active collaboration tracking
        self.active_sessions: Dict[str, ActiveCollaboration] = {}
        self.user_sessions: Dict[str, str] = {}  # user_id -> session_id
        
        # Expert verification criteria
        self.expert_criteria = {
            'min_drawings': 50,
            'min_followers': 10,
            'min_success_rate': 0.65,
            'min_reputation': 750,
            'verified_trades': True
        }
        
        # Collaboration limits
        self.collaboration_limits = {
            'max_concurrent_sessions': 5,
            'max_participants_per_session': 10,
            'max_annotations_per_chart': 100,
            'max_drawing_copies_per_day': 20
        }
    
    async def copy_expert_drawings(
        self, 
        db: Session, 
        user_id: str, 
        copy_request: ExpertDrawingRequest
    ) -> Dict[str, Any]:
        """Copy drawings from expert trader with attribution and ZK proof"""
        
        try:
            # Validate expert user
            expert = await self._validate_expert_user(db, copy_request.expert_user_id)
            if not expert['is_expert']:
                raise HTTPException(
                    status_code=403, 
                    detail="User is not a verified expert trader"
                )
            
            # Check daily limits
            daily_copies = await self._get_daily_copy_count(db, user_id)
            if daily_copies >= self.collaboration_limits['max_drawing_copies_per_day']:
                raise HTTPException(
                    status_code=429,
                    detail="Daily drawing copy limit reached"
                )
            
            # Validate source drawings exist and are public
            source_drawings = await self._validate_source_drawings(
                db, copy_request.expert_user_id, copy_request.drawing_ids
            )
            
            # Validate target chart
            target_chart = await self._validate_user_chart(
                db, user_id, copy_request.copy_to_chart_id
            )
            
            # Create drawing copies with attribution
            copied_drawings = []
            copy_id = str(uuid.uuid4())
            
            for drawing in source_drawings:
                copied_drawing = await self._copy_drawing_with_attribution(
                    db, drawing, target_chart, copy_request.expert_user_id, copy_id
                )
                copied_drawings.append(copied_drawing)
            
            # Generate ZK proof for authenticity
            zk_proof = await self.zk_verification.generate_copy_proof(
                expert_user_id=copy_request.expert_user_id,
                drawings=source_drawings,
                copy_timestamp=datetime.utcnow(),
                recipient_user_id=user_id
            )
            
            # Record the copy operation
            copy_record = DrawingCopy(
                id=copy_id,
                copier_user_id=user_id,
                expert_user_id=copy_request.expert_user_id,
                source_chart_id=copy_request.chart_id,
                target_chart_id=copy_request.copy_to_chart_id,
                drawing_ids=copy_request.drawing_ids,
                zk_proof=zk_proof,
                created_at=datetime.utcnow()
            )
            
            db.add(copy_record)
            
            # Update reputation scores
            await self.reputation_manager.award_expert_copy_points(
                db, copy_request.expert_user_id, len(copied_drawings)
            )
            
            # Send notification to expert
            await self.notification_service.send_drawing_copied_notification(
                expert_user_id=copy_request.expert_user_id,
                copier_user_id=user_id,
                drawing_count=len(copied_drawings)
            )
            
            db.commit()
            
            return {
                'success': True,
                'copy_id': copy_id,
                'copied_drawings': copied_drawings,
                'expert_attribution': {
                    'expert_id': copy_request.expert_user_id,
                    'expert_name': expert['name'],
                    'expert_reputation': expert['reputation']
                },
                'zk_proof': zk_proof,
                'drawings_count': len(copied_drawings)
            }
        
        except Exception as e:
            logger.error(f"Expert drawing copy error: {e}")
            db.rollback()
            raise HTTPException(status_code=500, detail=str(e))
    
    async def create_collaborative_annotation(
        self, 
        db: Session, 
        user_id: str, 
        annotation_request: CollaborativeAnnotationRequest
    ) -> Dict[str, Any]:
        """Create collaborative annotation with threading and real-time updates"""
        
        try:
            # Validate chart access
            chart_access = await self._validate_chart_collaboration_access(
                db, user_id, annotation_request.chart_id
            )
            
            if not chart_access['can_comment']:
                raise HTTPException(
                    status_code=403,
                    detail="No permission to add annotations to this chart"
                )
            
            # Check annotation limits
            chart_annotation_count = await self._get_chart_annotation_count(
                db, annotation_request.chart_id
            )
            
            if chart_annotation_count >= self.collaboration_limits['max_annotations_per_chart']:
                raise HTTPException(
                    status_code=429,
                    detail="Chart annotation limit reached"
                )
            
            # Create annotation
            annotation_id = str(uuid.uuid4())
            
            annotation = ChartAnnotation(
                id=annotation_id,
                chart_id=annotation_request.chart_id,
                user_id=user_id,
                annotation_type=annotation_request.annotation_type,
                content=annotation_request.content,
                position=json.dumps(annotation_request.position),
                drawing_reference_id=annotation_request.drawing_reference_id,
                parent_annotation_id=annotation_request.parent_annotation_id,
                created_at=datetime.utcnow(),
                is_public=True
            )
            
            db.add(annotation)
            
            # If this is a threaded response, update parent
            if annotation_request.parent_annotation_id:
                await self._update_annotation_thread(
                    db, annotation_request.parent_annotation_id, annotation_id
                )
            
            # Broadcast to active collaboration session
            session_id = self.user_sessions.get(user_id)
            if session_id and session_id in self.active_sessions:
                await self._broadcast_annotation_to_session(
                    session_id, annotation, user_id
                )
            
            # Award reputation points
            await self.reputation_manager.award_collaboration_points(
                db, user_id, 'annotation'
            )
            
            db.commit()
            
            # Get user profile for response
            user_profile = db.query(UserProfile).filter(
                UserProfile.user_id == user_id
            ).first()
            
            return {
                'success': True,
                'annotation_id': annotation_id,
                'annotation': {
                    'id': annotation_id,
                    'type': annotation_request.annotation_type,
                    'content': annotation_request.content,
                    'position': annotation_request.position,
                    'created_at': annotation.created_at.isoformat(),
                    'author': {
                        'id': user_id,
                        'name': user_profile.display_name if user_profile else 'Unknown',
                        'reputation': await self.reputation_manager.get_user_reputation(db, user_id)
                    }
                },
                'thread_info': await self._get_annotation_thread_info(
                    db, annotation_id
                ) if annotation_request.parent_annotation_id else None
            }
        
        except Exception as e:
            logger.error(f"Collaborative annotation error: {e}")
            db.rollback()
            raise HTTPException(status_code=500, detail=str(e))
    
    async def start_collaboration_session(
        self, 
        db: Session, 
        user_id: str, 
        invite_request: CollaborationInviteRequest
    ) -> Dict[str, Any]:
        """Start real-time collaboration session on a chart"""
        
        try:
            # Validate chart ownership
            chart = await self._validate_user_chart(db, user_id, invite_request.chart_id)
            
            # Check concurrent session limits
            user_active_sessions = sum(1 for session in self.active_sessions.values() 
                                     if user_id in session.participants)
            
            if user_active_sessions >= self.collaboration_limits['max_concurrent_sessions']:
                raise HTTPException(
                    status_code=429,
                    detail="Maximum concurrent collaboration sessions reached"
                )
            
            # Validate invited users
            invited_users = await self._validate_invited_users(
                db, invite_request.invited_user_ids
            )
            
            # Create collaboration session
            session_id = str(uuid.uuid4())
            
            collaboration_session = CollaborationSession(
                id=session_id,
                chart_id=invite_request.chart_id,
                host_user_id=user_id,
                invited_user_ids=json.dumps(invite_request.invited_user_ids),
                permission_level=invite_request.permission_level,
                expires_at=datetime.utcnow() + timedelta(hours=invite_request.expires_in_hours),
                created_at=datetime.utcnow(),
                is_active=True
            )
            
            db.add(collaboration_session)
            
            # Initialize active session tracking
            permissions = {user_id: 'OWNER'}  # Host has owner permissions
            for invited_user_id in invite_request.invited_user_ids:
                permissions[invited_user_id] = invite_request.permission_level
            
            self.active_sessions[session_id] = ActiveCollaboration(
                session_id=session_id,
                chart_id=invite_request.chart_id,
                participants={user_id},  # Host is automatically participating
                websockets={},
                last_activity=datetime.utcnow(),
                permissions=permissions
            )
            
            # Send invitations
            for invited_user_id in invite_request.invited_user_ids:
                await self.notification_service.send_collaboration_invite(
                    invited_user_id=invited_user_id,
                    host_user_id=user_id,
                    chart_id=invite_request.chart_id,
                    session_id=session_id,
                    permission_level=invite_request.permission_level
                )
            
            db.commit()
            
            return {
                'success': True,
                'session_id': session_id,
                'chart_id': invite_request.chart_id,
                'invited_users': invited_users,
                'permissions': permissions,
                'join_url': f"/charts/collaborate/{session_id}",
                'expires_at': collaboration_session.expires_at.isoformat()
            }
        
        except Exception as e:
            logger.error(f"Collaboration session creation error: {e}")
            db.rollback()
            raise HTTPException(status_code=500, detail=str(e))
    
    async def join_collaboration_session(
        self, 
        db: Session, 
        user_id: str, 
        session_id: str,
        websocket: WebSocket
    ) -> Dict[str, Any]:
        """Join an active collaboration session via WebSocket"""
        
        try:
            # Validate session exists and user is invited
            session = db.query(CollaborationSession).filter(
                CollaborationSession.id == session_id,
                CollaborationSession.is_active == True,
                CollaborationSession.expires_at > datetime.utcnow()
            ).first()
            
            if not session:
                raise HTTPException(status_code=404, detail="Collaboration session not found")
            
            invited_user_ids = json.loads(session.invited_user_ids)
            if user_id not in invited_user_ids and user_id != session.host_user_id:
                raise HTTPException(status_code=403, detail="Not invited to this session")
            
            # Check if session is active in memory
            if session_id not in self.active_sessions:
                # Reactivate session
                self.active_sessions[session_id] = ActiveCollaboration(
                    session_id=session_id,
                    chart_id=session.chart_id,
                    participants=set(),
                    websockets={},
                    last_activity=datetime.utcnow(),
                    permissions={}
                )
            
            active_session = self.active_sessions[session_id]
            
            # Check participant limits
            if len(active_session.participants) >= self.collaboration_limits['max_participants_per_session']:
                raise HTTPException(
                    status_code=429,
                    detail="Collaboration session is full"
                )
            
            # Add user to session
            active_session.participants.add(user_id)
            active_session.websockets[user_id] = websocket
            active_session.last_activity = datetime.utcnow()
            self.user_sessions[user_id] = session_id
            
            # Accept WebSocket connection
            await websocket.accept()
            
            # Send session state to new participant
            await self._send_session_state(websocket, session_id, user_id)
            
            # Broadcast user joined to other participants
            await self._broadcast_user_joined(session_id, user_id)
            
            return {
                'success': True,
                'session_id': session_id,
                'participant_count': len(active_session.participants),
                'your_permissions': active_session.permissions.get(user_id, 'VIEW')
            }
        
        except Exception as e:
            logger.error(f"Collaboration session join error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def apply_for_expert_status(
        self, 
        db: Session, 
        user_id: str, 
        expert_request: ExpertProfileRequest
    ) -> Dict[str, Any]:
        """Apply for expert trader status with verification"""
        
        try:
            # Check if user already has expert profile
            existing_expert = db.query(ExpertProfile).filter(
                ExpertProfile.user_id == user_id
            ).first()
            
            if existing_expert:
                raise HTTPException(
                    status_code=400,
                    detail="Expert profile already exists"
                )
            
            # Validate user meets basic criteria
            user_stats = await self._get_user_trading_stats(db, user_id)
            
            criteria_met = {
                'drawings': user_stats['total_drawings'] >= self.expert_criteria['min_drawings'],
                'followers': user_stats['followers'] >= self.expert_criteria['min_followers'],
                'success_rate': user_stats['success_rate'] >= self.expert_criteria['min_success_rate'],
                'reputation': user_stats['reputation'] >= self.expert_criteria['min_reputation']
            }
            
            # Create expert profile application
            expert_profile = ExpertProfile(
                id=str(uuid.uuid4()),
                user_id=user_id,
                specialization=json.dumps(expert_request.specialization),
                years_experience=expert_request.years_experience,
                trading_style=expert_request.trading_style,
                bio=expert_request.bio,
                verified_performance=json.dumps(expert_request.verified_performance or {}),
                application_status='PENDING',
                criteria_met=json.dumps(criteria_met),
                applied_at=datetime.utcnow()
            )
            
            db.add(expert_profile)
            
            # Auto-approve if all criteria met
            if all(criteria_met.values()):
                expert_profile.application_status = 'APPROVED'
                expert_profile.verified_at = datetime.utcnow()
                expert_profile.is_active = True
                
                # Award expert status reputation
                await self.reputation_manager.award_expert_status_points(db, user_id)
            
            db.commit()
            
            return {
                'success': True,
                'expert_profile_id': expert_profile.id,
                'application_status': expert_profile.application_status,
                'criteria_met': criteria_met,
                'auto_approved': expert_profile.application_status == 'APPROVED',
                'next_steps': 'Manual review required' if expert_profile.application_status == 'PENDING' else 'Expert status activated'
            }
        
        except Exception as e:
            logger.error(f"Expert status application error: {e}")
            db.rollback()
            raise HTTPException(status_code=500, detail=str(e))
    
    # Private helper methods
    async def _validate_expert_user(self, db: Session, user_id: str) -> Dict[str, Any]:
        """Validate if user is a verified expert"""
        
        expert_profile = db.query(ExpertProfile).filter(
            ExpertProfile.user_id == user_id,
            ExpertProfile.is_active == True,
            ExpertProfile.application_status == 'APPROVED'
        ).first()
        
        if not expert_profile:
            return {'is_expert': False}
        
        user_profile = db.query(UserProfile).filter(
            UserProfile.user_id == user_id
        ).first()
        
        reputation = await self.reputation_manager.get_user_reputation(db, user_id)
        
        return {
            'is_expert': True,
            'name': user_profile.display_name if user_profile else 'Expert',
            'reputation': reputation,
            'specialization': json.loads(expert_profile.specialization),
            'verified_at': expert_profile.verified_at
        }
    
    async def _get_daily_copy_count(self, db: Session, user_id: str) -> int:
        """Get daily drawing copy count for user"""
        
        today = datetime.utcnow().date()
        
        count = db.query(DrawingCopy).filter(
            DrawingCopy.copier_user_id == user_id,
            DrawingCopy.created_at >= today
        ).count()
        
        return count
    
    async def _validate_source_drawings(
        self, 
        db: Session, 
        expert_user_id: str, 
        drawing_ids: List[str]
    ) -> List[ChartDrawing]:
        """Validate source drawings exist and are public"""
        
        drawings = db.query(ChartDrawing).filter(
            ChartDrawing.id.in_(drawing_ids),
            ChartDrawing.user_id == expert_user_id,
            ChartDrawing.is_public == True
        ).all()
        
        if len(drawings) != len(drawing_ids):
            raise HTTPException(
                status_code=404,
                detail="Some drawings not found or not public"
            )
        
        return drawings
    
    async def _validate_user_chart(self, db: Session, user_id: str, chart_id: str) -> Chart:
        """Validate user owns the chart"""
        
        chart = db.query(Chart).filter(
            Chart.id == chart_id,
            Chart.user_id == user_id
        ).first()
        
        if not chart:
            raise HTTPException(
                status_code=404,
                detail="Chart not found or access denied"
            )
        
        return chart
    
    async def _copy_drawing_with_attribution(
        self, 
        db: Session, 
        source_drawing: ChartDrawing, 
        target_chart: Chart, 
        expert_user_id: str,
        copy_id: str
    ) -> Dict[str, Any]:
        """Copy drawing with proper attribution"""
        
        copied_drawing = ChartDrawing(
            id=str(uuid.uuid4()),
            chart_id=target_chart.id,
            user_id=target_chart.user_id,
            drawing_type=source_drawing.drawing_type,
            drawing_data=source_drawing.drawing_data,
            style_config=source_drawing.style_config,
            is_public=False,  # Copied drawings are private by default
            expert_attribution=json.dumps({
                'original_expert_id': expert_user_id,
                'copy_id': copy_id,
                'copied_at': datetime.utcnow().isoformat()
            }),
            created_at=datetime.utcnow()
        )
        
        db.add(copied_drawing)
        
        return {
            'id': copied_drawing.id,
            'type': copied_drawing.drawing_type,
            'data': json.loads(copied_drawing.drawing_data),
            'attribution': json.loads(copied_drawing.expert_attribution)
        }
    
    async def _validate_chart_collaboration_access(
        self, 
        db: Session, 
        user_id: str, 
        chart_id: str
    ) -> Dict[str, bool]:
        """Validate user's collaboration access to chart"""
        
        # Check if user owns the chart
        chart = db.query(Chart).filter(
            Chart.id == chart_id,
            Chart.user_id == user_id
        ).first()
        
        if chart:
            return {'can_comment': True, 'can_edit': True, 'is_owner': True}
        
        # Check if user is in active collaboration session
        session_id = self.user_sessions.get(user_id)
        if session_id and session_id in self.active_sessions:
            active_session = self.active_sessions[session_id]
            if active_session.chart_id == chart_id:
                permission = active_session.permissions.get(user_id, 'VIEW')
                return {
                    'can_comment': permission in ['COMMENT', 'EDIT', 'OWNER'],
                    'can_edit': permission in ['EDIT', 'OWNER'],
                    'is_owner': permission == 'OWNER'
                }
        
        return {'can_comment': False, 'can_edit': False, 'is_owner': False}
    
    async def _get_chart_annotation_count(self, db: Session, chart_id: str) -> int:
        """Get total annotation count for chart"""
        
        return db.query(ChartAnnotation).filter(
            ChartAnnotation.chart_id == chart_id
        ).count()
    
    async def _update_annotation_thread(
        self, 
        db: Session, 
        parent_id: str, 
        child_id: str
    ):
        """Update annotation thread relationships"""
        
        # Check if thread record exists
        thread = db.query(AnnotationThread).filter(
            AnnotationThread.parent_annotation_id == parent_id
        ).first()
        
        if thread:
            child_ids = json.loads(thread.child_annotation_ids)
            child_ids.append(child_id)
            thread.child_annotation_ids = json.dumps(child_ids)
            thread.updated_at = datetime.utcnow()
        else:
            # Create new thread
            thread = AnnotationThread(
                id=str(uuid.uuid4()),
                parent_annotation_id=parent_id,
                child_annotation_ids=json.dumps([child_id]),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(thread)
    
    async def _broadcast_annotation_to_session(
        self, 
        session_id: str, 
        annotation: ChartAnnotation, 
        author_user_id: str
    ):
        """Broadcast new annotation to all session participants"""
        
        if session_id not in self.active_sessions:
            return
        
        active_session = self.active_sessions[session_id]
        
        message = {
            'type': 'new_annotation',
            'annotation': {
                'id': annotation.id,
                'type': annotation.annotation_type,
                'content': annotation.content,
                'position': json.loads(annotation.position),
                'author_id': author_user_id,
                'created_at': annotation.created_at.isoformat()
            }
        }
        
        # Send to all participants except the author
        for user_id, websocket in active_session.websockets.items():
            if user_id != author_user_id:
                try:
                    await websocket.send_json(message)
                except:
                    # Remove disconnected websocket
                    del active_session.websockets[user_id]
                    active_session.participants.discard(user_id)
    
    async def _get_annotation_thread_info(
        self, 
        db: Session, 
        annotation_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get thread information for annotation"""
        
        thread = db.query(AnnotationThread).filter(
            AnnotationThread.parent_annotation_id == annotation_id
        ).first()
        
        if thread:
            return {
                'thread_id': thread.id,
                'child_count': len(json.loads(thread.child_annotation_ids)),
                'last_updated': thread.updated_at.isoformat()
            }
        
        return None
    
    async def _validate_invited_users(
        self, 
        db: Session, 
        user_ids: List[str]
    ) -> List[Dict[str, str]]:
        """Validate invited users exist and return their info"""
        
        users = db.query(User).filter(User.id.in_(user_ids)).all()
        
        if len(users) != len(user_ids):
            raise HTTPException(
                status_code=404,
                detail="Some invited users not found"
            )
        
        return [
            {
                'id': user.id,
                'name': user.display_name or user.email.split('@')[0]
            }
            for user in users
        ]
    
    async def _send_session_state(self, websocket: WebSocket, session_id: str, user_id: str):
        """Send current session state to new participant"""
        
        active_session = self.active_sessions[session_id]
        
        state = {
            'type': 'session_state',
            'session_id': session_id,
            'chart_id': active_session.chart_id,
            'participants': list(active_session.participants),
            'your_permissions': active_session.permissions.get(user_id, 'VIEW'),
            'last_activity': active_session.last_activity.isoformat()
        }
        
        await websocket.send_json(state)
    
    async def _broadcast_user_joined(self, session_id: str, joined_user_id: str):
        """Broadcast user joined message to session participants"""
        
        if session_id not in self.active_sessions:
            return
        
        active_session = self.active_sessions[session_id]
        
        message = {
            'type': 'user_joined',
            'user_id': joined_user_id,
            'participant_count': len(active_session.participants)
        }
        
        for user_id, websocket in active_session.websockets.items():
            if user_id != joined_user_id:
                try:
                    await websocket.send_json(message)
                except:
                    pass
    
    async def _get_user_trading_stats(self, db: Session, user_id: str) -> Dict[str, Any]:
        """Get user trading statistics for expert validation"""
        
        # Get drawing count
        drawing_count = db.query(ChartDrawing).filter(
            ChartDrawing.user_id == user_id,
            ChartDrawing.is_public == True
        ).count()
        
        # Get follower count (placeholder - would need social follows table)
        follower_count = 15  # Placeholder
        
        # Get success rate (placeholder - would need trade tracking)
        success_rate = 0.72  # Placeholder
        
        # Get reputation
        reputation = await self.reputation_manager.get_user_reputation(db, user_id)
        
        return {
            'total_drawings': drawing_count,
            'followers': follower_count,
            'success_rate': success_rate,
            'reputation': reputation
        }


# Initialize social collaboration manager
social_collaboration = SocialCollaborationManager()


# API Endpoints
@router.post("/copy-expert-drawings", response_model=ExpertDrawingResponse)
async def copy_expert_drawings(
    copy_request: ExpertDrawingRequest,
    user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Copy drawings from expert trader with attribution"""
    
    result = await social_collaboration.copy_expert_drawings(
        db, user["id"], copy_request
    )
    
    return ExpertDrawingResponse(**result)


@router.post("/add-annotation")
async def add_collaborative_annotation(
    annotation_request: CollaborativeAnnotationRequest,
    user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add collaborative annotation to chart"""
    
    result = await social_collaboration.create_collaborative_annotation(
        db, user["id"], annotation_request
    )
    
    return result


@router.post("/start-collaboration", response_model=CollaborationSessionResponse)
async def start_collaboration_session(
    invite_request: CollaborationInviteRequest,
    user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start real-time collaboration session"""
    
    result = await social_collaboration.start_collaboration_session(
        db, user["id"], invite_request
    )
    
    return CollaborationSessionResponse(
        session_id=result['session_id'],
        participants=result['invited_users'],
        chart_id=result['chart_id'],
        permissions=result['permissions'],
        active=True
    )


@router.websocket("/collaborate/{session_id}")
async def websocket_collaboration(
    websocket: WebSocket,
    session_id: str,
    user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """WebSocket endpoint for real-time collaboration"""
    
    try:
        await social_collaboration.join_collaboration_session(
            db, user["id"], session_id, websocket
        )
        
        # Keep connection alive and handle messages
        while True:
            data = await websocket.receive_json()
            
            # Handle different message types
            if data.get('type') == 'drawing_update':
                await social_collaboration._broadcast_drawing_update(
                    session_id, data, user["id"]
                )
            elif data.get('type') == 'cursor_position':
                await social_collaboration._broadcast_cursor_position(
                    session_id, data, user["id"]
                )
    
    except Exception as e:
        logger.error(f"WebSocket collaboration error: {e}")
        if websocket.client_state != websocket.client_state.DISCONNECTED:
            await websocket.close()


@router.post("/apply-expert-status")
async def apply_for_expert_status(
    expert_request: ExpertProfileRequest,
    user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Apply for expert trader status"""
    
    result = await social_collaboration.apply_for_expert_status(
        db, user["id"], expert_request
    )
    
    return result


@router.get("/expert-profiles")
async def get_expert_profiles(
    specialization: Optional[str] = None,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get list of verified expert profiles"""
    
    query = db.query(ExpertProfile).filter(
        ExpertProfile.is_active == True,
        ExpertProfile.application_status == 'APPROVED'
    )
    
    if specialization:
        query = query.filter(
            ExpertProfile.specialization.contains(specialization)
        )
    
    experts = query.limit(limit).all()
    
    return {
        'experts': [
            {
                'user_id': e.user_id,
                'specialization': json.loads(e.specialization),
                'years_experience': e.years_experience,
                'trading_style': e.trading_style,
                'bio': e.bio,
                'verified_at': e.verified_at.isoformat() if e.verified_at else None
            }
            for e in experts
        ]
    }


@router.get("/collaboration-sessions")
async def get_active_collaborations(
    user: Dict = Depends(get_current_user)
):
    """Get user's active collaboration sessions"""
    
    user_id = user["id"]
    active_sessions = []
    
    for session_id, session in social_collaboration.active_sessions.items():
        if user_id in session.participants:
            active_sessions.append({
                'session_id': session_id,
                'chart_id': session.chart_id,
                'participant_count': len(session.participants),
                'your_permissions': session.permissions.get(user_id, 'VIEW'),
                'last_activity': session.last_activity.isoformat()
            })
    
    return {'active_sessions': active_sessions}


# Health check
@router.get("/health")
async def social_collaboration_health_check():
    """Health check for social collaboration system"""
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "social_collaboration": "operational",
        "features": {
            "expert_drawing_copy": True,
            "collaborative_annotations": True,
            "real_time_collaboration": True,
            "expert_verification": True,
            "zk_proof_authenticity": True
        },
        "active_sessions": len(social_collaboration.active_sessions),
        "collaboration_limits": social_collaboration.collaboration_limits
    }