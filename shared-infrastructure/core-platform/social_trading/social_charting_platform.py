#!/usr/bin/env python3
"""
GridWorks Social Charting Platform
==================================
WebRTC-powered shared charts with ZK-proof verification and community features
"""

import asyncio
import json
import uuid
import hashlib
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from enum import Enum
from dataclasses import dataclass, asdict, field
import logging
from pathlib import Path
import time

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChartSharingPermission(Enum):
    """Chart sharing permission levels"""
    PUBLIC = "public"           # Visible to all community members
    FRIENDS = "friends"         # Visible to connected friends only
    PREMIUM = "premium"         # Visible to premium subscribers only
    PRIVATE = "private"         # Private to creator only
    VERIFIED_ONLY = "verified"  # Only ZK-verified analysts


class AnalysisType(Enum):
    """Types of chart analysis"""
    TECHNICAL_ANALYSIS = "technical_analysis"
    PATTERN_RECOGNITION = "pattern_recognition"
    SUPPORT_RESISTANCE = "support_resistance"
    TREND_ANALYSIS = "trend_analysis"
    VOLUME_ANALYSIS = "volume_analysis"
    FIBONACCI_ANALYSIS = "fibonacci_analysis"
    WAVE_ANALYSIS = "wave_analysis"
    PREDICTION = "prediction"


class InteractionType(Enum):
    """Types of chart interactions"""
    LIKE = "like"
    COMMENT = "comment"
    SHARE = "share"
    FOLLOW_ANALYST = "follow_analyst"
    COPY_ANALYSIS = "copy_analysis"
    CHALLENGE = "challenge"
    VERIFY = "verify"


@dataclass
class DrawingAnnotation:
    """Chart drawing/annotation data"""
    annotation_id: str
    type: str  # "line", "rectangle", "circle", "text", "fibonacci", "trend_line"
    coordinates: List[Tuple[float, float]]
    style: Dict[str, Any]  # Color, thickness, etc.
    label: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ChartAnalysis:
    """Shared chart analysis data"""
    analysis_id: str
    analyst_id: str
    analyst_name: str
    symbol: str
    timeframe: str
    analysis_type: AnalysisType
    title: str
    description: str
    annotations: List[DrawingAnnotation]
    price_targets: List[float]
    stop_loss: Optional[float]
    confidence_score: float
    chart_image_base64: str
    created_at: datetime
    expires_at: Optional[datetime]
    permission_level: ChartSharingPermission
    zk_verified: bool = False
    zk_proof_hash: Optional[str] = None
    
    # Community engagement
    likes_count: int = 0
    comments_count: int = 0
    shares_count: int = 0
    views_count: int = 0
    
    # Performance tracking
    accuracy_score: Optional[float] = None
    outcome_verified: bool = False
    
    @property
    def engagement_score(self) -> float:
        """Calculate engagement score"""
        return (self.likes_count * 1.0 + 
                self.comments_count * 2.0 + 
                self.shares_count * 3.0) / max(self.views_count, 1)
    
    @property
    def is_expired(self) -> bool:
        """Check if analysis has expired"""
        return self.expires_at and datetime.now() > self.expires_at


@dataclass
class AnalystProfile:
    """Social trading analyst profile"""
    analyst_id: str
    username: str
    display_name: str
    bio: str
    profile_image_url: str
    verification_level: str  # "basic", "verified", "expert", "institutional"
    specializations: List[str]  # Asset classes, strategies
    
    # Performance metrics
    total_analyses: int = 0
    accuracy_rate: float = 0.0
    avg_return: float = 0.0
    followers_count: int = 0
    following_count: int = 0
    
    # Reputation system
    reputation_score: float = 0.0
    badges: List[str] = field(default_factory=list)
    verified_predictions: int = 0
    
    # ZK credentials
    zk_public_key: Optional[str] = None
    zk_credential_hash: Optional[str] = None
    
    join_date: datetime = field(default_factory=datetime.now)
    last_active: datetime = field(default_factory=datetime.now)


@dataclass
class ChartComment:
    """Comment on shared chart analysis"""
    comment_id: str
    analysis_id: str
    user_id: str
    username: str
    content: str
    parent_comment_id: Optional[str]  # For nested comments
    likes_count: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    edited_at: Optional[datetime] = None


@dataclass
class CommunityChallenge:
    """Community trading challenge"""
    challenge_id: str
    title: str
    description: str
    symbol: str
    start_date: datetime
    end_date: datetime
    entry_fee: float
    prize_pool: float
    max_participants: int
    
    # Challenge rules
    challenge_type: str  # "prediction", "analysis", "return_competition"
    success_criteria: Dict[str, Any]
    
    # Participants
    participants: List[str] = field(default_factory=list)
    submissions: Dict[str, str] = field(default_factory=dict)  # user_id -> analysis_id
    
    # Results
    winner_id: Optional[str] = None
    results_announced: bool = False
    leaderboard: List[Dict[str, Any]] = field(default_factory=list)


class ZKProofVerification:
    """Zero-Knowledge proof verification for analyst credentials"""
    
    def __init__(self):
        """Initialize ZK proof system"""
        self.verified_analysts = {}
        self.proof_cache = {}
    
    async def generate_analyst_proof(self, analyst_id: str, credentials: Dict[str, Any]) -> str:
        """Generate ZK proof for analyst credentials"""
        
        # Mock ZK proof generation (replace with actual zk-SNARKs implementation)
        proof_data = {
            'analyst_id': analyst_id,
            'credentials': credentials,
            'timestamp': datetime.now().isoformat(),
            'nonce': str(uuid.uuid4())
        }
        
        # Create hash-based proof (simplified)
        proof_string = json.dumps(proof_data, sort_keys=True)
        proof_hash = hashlib.sha256(proof_string.encode()).hexdigest()
        
        # Store proof
        self.proof_cache[proof_hash] = proof_data
        
        logger.info(f"Generated ZK proof for analyst {analyst_id}: {proof_hash[:16]}...")
        return proof_hash
    
    async def verify_analyst_proof(self, proof_hash: str, public_claims: Dict[str, Any]) -> bool:
        """Verify ZK proof without revealing private information"""
        
        # Mock verification (replace with actual zk-SNARKs verification)
        if proof_hash not in self.proof_cache:
            return False
        
        proof_data = self.proof_cache[proof_hash]
        
        # Verify claims match proof
        for claim_key, claim_value in public_claims.items():
            if claim_key in proof_data['credentials']:
                if proof_data['credentials'][claim_key] != claim_value:
                    return False
        
        logger.info(f"ZK proof verification successful: {proof_hash[:16]}...")
        return True
    
    async def verify_analysis_integrity(self, analysis: ChartAnalysis) -> bool:
        """Verify analysis hasn't been tampered with using ZK proofs"""
        
        if not analysis.zk_verified or not analysis.zk_proof_hash:
            return False
        
        # Generate hash of current analysis data
        analysis_data = {
            'analyst_id': analysis.analyst_id,
            'symbol': analysis.symbol,
            'analysis_type': analysis.analysis_type.value,
            'annotations': [asdict(ann) for ann in analysis.annotations],
            'price_targets': analysis.price_targets,
            'created_at': analysis.created_at.isoformat()
        }
        
        current_hash = hashlib.sha256(
            json.dumps(analysis_data, sort_keys=True).encode()
        ).hexdigest()
        
        return current_hash == analysis.zk_proof_hash


class WebRTCChartSharing:
    """WebRTC-based real-time chart sharing"""
    
    def __init__(self):
        """Initialize WebRTC chart sharing"""
        self.active_sessions = {}
        self.session_participants = {}
        
        # Mock WebRTC (replace with actual WebRTC implementation)
        self.webrtc_client = self._initialize_mock_webrtc()
    
    def _initialize_mock_webrtc(self):
        """Initialize mock WebRTC client"""
        class MockWebRTCClient:
            def __init__(self):
                self.connections = {}
            
            async def create_session(self, session_id: str) -> str:
                # Mock session creation
                session_url = f"wss://webrtc.gridworks.com/session/{session_id}"
                logger.info(f"Created WebRTC session: {session_id}")
                return session_url
            
            async def join_session(self, session_id: str, user_id: str) -> bool:
                # Mock joining session
                if session_id not in self.connections:
                    self.connections[session_id] = []
                self.connections[session_id].append(user_id)
                logger.info(f"User {user_id} joined session {session_id}")
                return True
            
            async def broadcast_chart_update(self, session_id: str, chart_data: Dict) -> bool:
                # Mock broadcasting chart updates
                participants = self.connections.get(session_id, [])
                logger.info(f"Broadcasting to {len(participants)} participants in session {session_id}")
                return True
        
        return MockWebRTCClient()
    
    async def create_live_chart_session(
        self, 
        host_id: str, 
        symbol: str, 
        permission_level: ChartSharingPermission = ChartSharingPermission.PUBLIC
    ) -> str:
        """Create live chart sharing session"""
        
        session_id = str(uuid.uuid4())
        
        # Create WebRTC session
        session_url = await self.webrtc_client.create_session(session_id)
        
        # Store session info
        self.active_sessions[session_id] = {
            'host_id': host_id,
            'symbol': symbol,
            'permission_level': permission_level,
            'created_at': datetime.now(),
            'session_url': session_url,
            'max_participants': 100,
            'recording_enabled': True
        }
        
        self.session_participants[session_id] = [host_id]
        
        logger.info(f"Created live chart session {session_id} for {symbol}")
        return session_id
    
    async def join_live_session(self, session_id: str, user_id: str) -> bool:
        """Join live chart sharing session"""
        
        if session_id not in self.active_sessions:
            return False
        
        session_info = self.active_sessions[session_id]
        
        # Check permissions
        if not await self._check_session_permission(session_info, user_id):
            return False
        
        # Check capacity
        current_participants = len(self.session_participants.get(session_id, []))
        if current_participants >= session_info['max_participants']:
            return False
        
        # Join WebRTC session
        success = await self.webrtc_client.join_session(session_id, user_id)
        
        if success:
            self.session_participants[session_id].append(user_id)
            logger.info(f"User {user_id} joined live session {session_id}")
        
        return success
    
    async def broadcast_chart_annotation(
        self, 
        session_id: str, 
        user_id: str, 
        annotation: DrawingAnnotation
    ) -> bool:
        """Broadcast chart annotation to all session participants"""
        
        if session_id not in self.active_sessions:
            return False
        
        if user_id not in self.session_participants.get(session_id, []):
            return False
        
        # Prepare broadcast data
        broadcast_data = {
            'type': 'chart_annotation',
            'annotation': asdict(annotation),
            'user_id': user_id,
            'timestamp': datetime.now().isoformat()
        }
        
        # Broadcast to all participants
        success = await self.webrtc_client.broadcast_chart_update(session_id, broadcast_data)
        
        if success:
            logger.info(f"Broadcasted annotation from {user_id} in session {session_id}")
        
        return success
    
    async def _check_session_permission(self, session_info: Dict, user_id: str) -> bool:
        """Check if user has permission to join session"""
        
        permission_level = session_info['permission_level']
        
        if permission_level == ChartSharingPermission.PUBLIC:
            return True
        elif permission_level == ChartSharingPermission.PRIVATE:
            return user_id == session_info['host_id']
        elif permission_level == ChartSharingPermission.PREMIUM:
            # Check if user has premium subscription
            return await self._is_premium_user(user_id)
        elif permission_level == ChartSharingPermission.VERIFIED_ONLY:
            # Check if user is verified analyst
            return await self._is_verified_analyst(user_id)
        
        return False
    
    async def _is_premium_user(self, user_id: str) -> bool:
        """Check if user has premium subscription"""
        # Mock implementation
        return True  # For demo purposes
    
    async def _is_verified_analyst(self, user_id: str) -> bool:
        """Check if user is verified analyst"""
        # Mock implementation
        return True  # For demo purposes


class SocialChartingPlatform:
    """Main social charting platform"""
    
    def __init__(self):
        """Initialize social charting platform"""
        self.shared_analyses = {}
        self.analyst_profiles = {}
        self.community_challenges = {}
        self.interactions = []
        
        # Initialize sub-systems
        self.zk_verification = ZKProofVerification()
        self.webrtc_sharing = WebRTCChartSharing()
        
        # Leaderboards
        self.analyst_leaderboard = []
        self.weekly_top_analyses = []
    
    async def create_analyst_profile(
        self, 
        user_id: str, 
        username: str, 
        display_name: str,
        bio: str = "",
        specializations: List[str] = None
    ) -> AnalystProfile:
        """Create social trading analyst profile"""
        
        profile = AnalystProfile(
            analyst_id=user_id,
            username=username,
            display_name=display_name,
            bio=bio,
            profile_image_url=f"https://cdn.gridworks.com/avatars/{user_id}.jpg",
            verification_level="basic",
            specializations=specializations or []
        )
        
        self.analyst_profiles[user_id] = profile
        
        logger.info(f"Created analyst profile for {username}")
        return profile
    
    async def share_chart_analysis(
        self, 
        analyst_id: str,
        symbol: str,
        timeframe: str,
        analysis_type: AnalysisType,
        title: str,
        description: str,
        annotations: List[DrawingAnnotation],
        chart_image_base64: str,
        price_targets: List[float] = None,
        stop_loss: float = None,
        permission_level: ChartSharingPermission = ChartSharingPermission.PUBLIC,
        expires_in_hours: int = 24
    ) -> ChartAnalysis:
        """Share chart analysis with community"""
        
        analysis_id = str(uuid.uuid4())
        
        # Create analysis
        analysis = ChartAnalysis(
            analysis_id=analysis_id,
            analyst_id=analyst_id,
            analyst_name=self.analyst_profiles.get(analyst_id, {}).get('display_name', 'Unknown'),
            symbol=symbol,
            timeframe=timeframe,
            analysis_type=analysis_type,
            title=title,
            description=description,
            annotations=annotations,
            price_targets=price_targets or [],
            stop_loss=stop_loss,
            confidence_score=0.8,  # Would be calculated based on historical accuracy
            chart_image_base64=chart_image_base64,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(hours=expires_in_hours),
            permission_level=permission_level
        )
        
        # Generate ZK proof if analyst is verified
        if await self._is_verified_analyst(analyst_id):
            analysis.zk_verified = True
            analysis.zk_proof_hash = await self._generate_analysis_proof(analysis)
        
        # Store analysis
        self.shared_analyses[analysis_id] = analysis
        
        # Update analyst stats
        if analyst_id in self.analyst_profiles:
            self.analyst_profiles[analyst_id].total_analyses += 1
        
        logger.info(f"Shared chart analysis: {title} for {symbol}")
        return analysis
    
    async def _generate_analysis_proof(self, analysis: ChartAnalysis) -> str:
        """Generate ZK proof for analysis integrity"""
        
        analysis_data = {
            'analyst_id': analysis.analyst_id,
            'symbol': analysis.symbol,
            'analysis_type': analysis.analysis_type.value,
            'annotations': [asdict(ann) for ann in analysis.annotations],
            'price_targets': analysis.price_targets,
            'created_at': analysis.created_at.isoformat()
        }
        
        proof_hash = hashlib.sha256(
            json.dumps(analysis_data, sort_keys=True).encode()
        ).hexdigest()
        
        return proof_hash
    
    async def get_community_feed(
        self, 
        user_id: str, 
        symbols: List[str] = None,
        analysis_types: List[AnalysisType] = None,
        limit: int = 20
    ) -> List[ChartAnalysis]:
        """Get personalized community feed"""
        
        # Filter analyses based on permissions and preferences
        relevant_analyses = []
        
        for analysis in self.shared_analyses.values():
            # Check permissions
            if not await self._can_view_analysis(user_id, analysis):
                continue
            
            # Filter by symbols
            if symbols and analysis.symbol not in symbols:
                continue
            
            # Filter by analysis types
            if analysis_types and analysis.analysis_type not in analysis_types:
                continue
            
            # Skip expired analyses
            if analysis.is_expired:
                continue
            
            relevant_analyses.append(analysis)
        
        # Sort by engagement and recency
        relevant_analyses.sort(
            key=lambda a: (a.engagement_score, a.created_at), 
            reverse=True
        )
        
        return relevant_analyses[:limit]
    
    async def interact_with_analysis(
        self, 
        user_id: str, 
        analysis_id: str, 
        interaction_type: InteractionType,
        content: str = None
    ) -> bool:
        """Interact with shared analysis"""
        
        if analysis_id not in self.shared_analyses:
            return False
        
        analysis = self.shared_analyses[analysis_id]
        
        # Update interaction counts
        if interaction_type == InteractionType.LIKE:
            analysis.likes_count += 1
            
        elif interaction_type == InteractionType.COMMENT:
            if content:
                comment = ChartComment(
                    comment_id=str(uuid.uuid4()),
                    analysis_id=analysis_id,
                    user_id=user_id,
                    username=self.analyst_profiles.get(user_id, {}).get('username', 'Anonymous'),
                    content=content,
                    parent_comment_id=None
                )
                analysis.comments_count += 1
                
        elif interaction_type == InteractionType.SHARE:
            analysis.shares_count += 1
            
        elif interaction_type == InteractionType.FOLLOW_ANALYST:
            if analysis.analyst_id in self.analyst_profiles:
                self.analyst_profiles[analysis.analyst_id].followers_count += 1
        
        # Log interaction
        self.interactions.append({
            'user_id': user_id,
            'analysis_id': analysis_id,
            'interaction_type': interaction_type.value,
            'content': content,
            'timestamp': datetime.now()
        })
        
        logger.info(f"User {user_id} {interaction_type.value} analysis {analysis_id}")
        return True
    
    async def create_community_challenge(
        self,
        creator_id: str,
        title: str,
        description: str,
        symbol: str,
        duration_days: int,
        entry_fee: float,
        prize_pool: float,
        challenge_type: str = "prediction"
    ) -> CommunityChallenge:
        """Create community trading challenge"""
        
        challenge_id = str(uuid.uuid4())
        
        challenge = CommunityChallenge(
            challenge_id=challenge_id,
            title=title,
            description=description,
            symbol=symbol,
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=duration_days),
            entry_fee=entry_fee,
            prize_pool=prize_pool,
            max_participants=100,
            challenge_type=challenge_type,
            success_criteria={'accuracy_threshold': 0.7}
        )
        
        self.community_challenges[challenge_id] = challenge
        
        logger.info(f"Created community challenge: {title}")
        return challenge
    
    async def join_challenge(self, user_id: str, challenge_id: str) -> bool:
        """Join community challenge"""
        
        if challenge_id not in self.community_challenges:
            return False
        
        challenge = self.community_challenges[challenge_id]
        
        # Check if challenge is still open
        if datetime.now() > challenge.end_date:
            return False
        
        # Check if user already joined
        if user_id in challenge.participants:
            return False
        
        # Check capacity
        if len(challenge.participants) >= challenge.max_participants:
            return False
        
        # Add participant
        challenge.participants.append(user_id)
        
        logger.info(f"User {user_id} joined challenge {challenge_id}")
        return True
    
    async def update_analyst_leaderboard(self):
        """Update analyst leaderboard based on performance"""
        
        # Calculate scores for all analysts
        analyst_scores = []
        
        for analyst_id, profile in self.analyst_profiles.items():
            # Calculate comprehensive score
            score = (
                profile.accuracy_rate * 0.4 +
                profile.avg_return * 0.3 +
                profile.reputation_score * 0.2 +
                min(profile.followers_count / 1000, 1.0) * 0.1
            )
            
            analyst_scores.append({
                'analyst_id': analyst_id,
                'username': profile.username,
                'display_name': profile.display_name,
                'score': score,
                'accuracy_rate': profile.accuracy_rate,
                'avg_return': profile.avg_return,
                'followers_count': profile.followers_count,
                'verification_level': profile.verification_level
            })
        
        # Sort by score
        analyst_scores.sort(key=lambda x: x['score'], reverse=True)
        
        # Update leaderboard
        self.analyst_leaderboard = analyst_scores[:50]  # Top 50
        
        logger.info(f"Updated analyst leaderboard with {len(self.analyst_leaderboard)} analysts")
    
    async def get_trending_analyses(self, timeframe_hours: int = 24, limit: int = 10) -> List[ChartAnalysis]:
        """Get trending analyses based on engagement"""
        
        cutoff_time = datetime.now() - timedelta(hours=timeframe_hours)
        
        # Filter recent analyses
        recent_analyses = [
            analysis for analysis in self.shared_analyses.values()
            if analysis.created_at > cutoff_time and not analysis.is_expired
        ]
        
        # Sort by engagement score
        recent_analyses.sort(key=lambda a: a.engagement_score, reverse=True)
        
        return recent_analyses[:limit]
    
    async def verify_analysis_outcome(self, analysis_id: str, actual_outcome: Dict[str, float]) -> bool:
        """Verify analysis outcome for accuracy tracking"""
        
        if analysis_id not in self.shared_analyses:
            return False
        
        analysis = self.shared_analyses[analysis_id]
        
        # Calculate accuracy based on price targets
        if analysis.price_targets and 'final_price' in actual_outcome:
            final_price = actual_outcome['final_price']
            initial_price = actual_outcome.get('initial_price', 0)
            
            if initial_price > 0:
                actual_return = (final_price - initial_price) / initial_price
                
                # Find closest target
                closest_target = min(analysis.price_targets, 
                                   key=lambda t: abs(t - final_price))
                predicted_return = (closest_target - initial_price) / initial_price
                
                # Calculate accuracy (inverse of prediction error)
                error = abs(actual_return - predicted_return)
                accuracy = max(0, 1 - error)
                
                analysis.accuracy_score = accuracy
                analysis.outcome_verified = True
                
                # Update analyst stats
                if analysis.analyst_id in self.analyst_profiles:
                    profile = self.analyst_profiles[analysis.analyst_id]
                    
                    # Update running averages
                    total_verified = profile.verified_predictions
                    current_avg_accuracy = profile.accuracy_rate
                    
                    new_accuracy = (current_avg_accuracy * total_verified + accuracy) / (total_verified + 1)
                    profile.accuracy_rate = new_accuracy
                    profile.verified_predictions += 1
                
                logger.info(f"Verified analysis {analysis_id} with accuracy {accuracy:.2f}")
                return True
        
        return False
    
    async def _can_view_analysis(self, user_id: str, analysis: ChartAnalysis) -> bool:
        """Check if user can view analysis based on permissions"""
        
        if analysis.permission_level == ChartSharingPermission.PUBLIC:
            return True
        elif analysis.permission_level == ChartSharingPermission.PRIVATE:
            return user_id == analysis.analyst_id
        elif analysis.permission_level == ChartSharingPermission.PREMIUM:
            return await self._is_premium_user(user_id)
        elif analysis.permission_level == ChartSharingPermission.VERIFIED_ONLY:
            return await self._is_verified_analyst(user_id)
        
        return False
    
    async def _is_premium_user(self, user_id: str) -> bool:
        """Check if user has premium subscription"""
        # Mock implementation
        return True
    
    async def _is_verified_analyst(self, user_id: str) -> bool:
        """Check if user is verified analyst"""
        if user_id in self.analyst_profiles:
            return self.analyst_profiles[user_id].verification_level in ['verified', 'expert', 'institutional']
        return False
    
    async def get_platform_statistics(self) -> Dict[str, Any]:
        """Get platform usage statistics"""
        
        total_analyses = len(self.shared_analyses)
        total_analysts = len(self.analyst_profiles)
        total_interactions = len(self.interactions)
        
        # Calculate engagement metrics
        if total_analyses > 0:
            avg_engagement = sum(a.engagement_score for a in self.shared_analyses.values()) / total_analyses
            total_views = sum(a.views_count for a in self.shared_analyses.values())
        else:
            avg_engagement = 0
            total_views = 0
        
        return {
            'total_analyses': total_analyses,
            'total_analysts': total_analysts,
            'total_interactions': total_interactions,
            'avg_engagement_score': avg_engagement,
            'total_views': total_views,
            'active_challenges': len([c for c in self.community_challenges.values() 
                                    if datetime.now() <= c.end_date]),
            'verified_analysts': len([p for p in self.analyst_profiles.values() 
                                    if p.verification_level in ['verified', 'expert']]),
            'zk_verified_analyses': len([a for a in self.shared_analyses.values() 
                                       if a.zk_verified])
        }


# Example usage and testing
async def main():
    """Example usage of social charting platform"""
    
    # Initialize platform
    platform = SocialChartingPlatform()
    
    # Create analyst profiles
    analyst1 = await platform.create_analyst_profile(
        user_id="analyst1",
        username="chart_master",
        display_name="Chart Master",
        bio="10 years of technical analysis experience",
        specializations=["technical_analysis", "pattern_recognition"]
    )
    
    # Create sample annotations
    annotations = [
        DrawingAnnotation(
            annotation_id=str(uuid.uuid4()),
            type="trend_line",
            coordinates=[(100, 200), (400, 150)],
            style={"color": "blue", "thickness": 2},
            label="Upward trend"
        ),
        DrawingAnnotation(
            annotation_id=str(uuid.uuid4()),
            type="rectangle",
            coordinates=[(150, 180), (350, 120)],
            style={"color": "red", "fill": "transparent"},
            label="Resistance zone"
        )
    ]
    
    # Share chart analysis
    analysis = await platform.share_chart_analysis(
        analyst_id="analyst1",
        symbol="RELIANCE",
        timeframe="1D",
        analysis_type=AnalysisType.TECHNICAL_ANALYSIS,
        title="RELIANCE Bullish Breakout Setup",
        description="Strong support at 2400, expecting breakout above 2600",
        annotations=annotations,
        chart_image_base64="base64_encoded_chart_image",
        price_targets=[2700, 2800],
        stop_loss=2350
    )
    
    print(f"Created analysis: {analysis.title}")
    print(f"Analysis ID: {analysis.analysis_id}")
    print(f"ZK Verified: {analysis.zk_verified}")
    
    # Create live chart session
    session_id = await platform.webrtc_sharing.create_live_chart_session(
        host_id="analyst1",
        symbol="RELIANCE"
    )
    
    print(f"Created live session: {session_id}")
    
    # Interact with analysis
    await platform.interact_with_analysis(
        user_id="user2",
        analysis_id=analysis.analysis_id,
        interaction_type=InteractionType.LIKE
    )
    
    await platform.interact_with_analysis(
        user_id="user3",
        analysis_id=analysis.analysis_id,
        interaction_type=InteractionType.COMMENT,
        content="Great analysis! I agree with the breakout setup."
    )
    
    # Get community feed
    feed = await platform.get_community_feed("user2", symbols=["RELIANCE"])
    print(f"Community feed has {len(feed)} analyses")
    
    # Create community challenge
    challenge = await platform.create_community_challenge(
        creator_id="analyst1",
        title="NIFTY Weekly Prediction Challenge",
        description="Predict NIFTY direction for next week",
        symbol="NIFTY",
        duration_days=7,
        entry_fee=100,
        prize_pool=5000
    )
    
    print(f"Created challenge: {challenge.title}")
    
    # Get platform statistics
    stats = await platform.get_platform_statistics()
    print(f"Platform Statistics: {stats}")


if __name__ == "__main__":
    asyncio.run(main())