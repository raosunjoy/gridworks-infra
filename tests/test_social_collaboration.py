"""
Comprehensive test suite for Social Collaboration Features
Tests expert drawing copy, collaborative annotations, and real-time collaboration
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock, patch
import json
import uuid

from fastapi.testclient import TestClient
from fastapi import HTTPException, WebSocket

from app.features.social_collaboration import (
    SocialCollaborationManager,
    ExpertDrawingRequest,
    CollaborativeAnnotationRequest,
    CollaborationInviteRequest,
    ExpertProfileRequest,
    ActiveCollaboration
)


class TestSocialCollaborationManagerInit:
    """Test Social Collaboration Manager initialization"""
    
    def test_manager_initialization(self):
        """Test manager initialization with default settings"""
        manager = SocialCollaborationManager()
        
        assert manager.zk_verification is not None
        assert manager.notification_service is not None
        assert manager.reputation_manager is not None
        
        # Check criteria configuration
        assert 'min_drawings' in manager.expert_criteria
        assert 'min_followers' in manager.expert_criteria
        assert 'min_success_rate' in manager.expert_criteria
        assert 'min_reputation' in manager.expert_criteria
        
        # Check collaboration limits
        assert 'max_concurrent_sessions' in manager.collaboration_limits
        assert 'max_participants_per_session' in manager.collaboration_limits
        assert 'max_annotations_per_chart' in manager.collaboration_limits
        
        # Check active sessions tracking
        assert isinstance(manager.active_sessions, dict)
        assert isinstance(manager.user_sessions, dict)
    
    def test_expert_criteria_values(self):
        """Test expert criteria have reasonable values"""
        manager = SocialCollaborationManager()
        
        criteria = manager.expert_criteria
        assert criteria['min_drawings'] >= 10
        assert 0 < criteria['min_success_rate'] <= 1
        assert criteria['min_reputation'] > 0
        assert criteria['min_followers'] > 0
    
    def test_collaboration_limits_values(self):
        """Test collaboration limits are reasonable"""
        manager = SocialCollaborationManager()
        
        limits = manager.collaboration_limits
        assert limits['max_concurrent_sessions'] > 0
        assert limits['max_participants_per_session'] > 1
        assert limits['max_annotations_per_chart'] > 10
        assert limits['max_drawing_copies_per_day'] > 5


class TestExpertDrawingCopy:
    """Test expert drawing copy functionality"""
    
    @pytest.mark.asyncio
    async def test_successful_drawing_copy(
        self, 
        db_session, 
        test_user, 
        expert_user,
        test_drawing,
        mock_zk_verification,
        mock_notification_service,
        mock_reputation_manager
    ):
        """Test successful copying of expert drawings"""
        manager = SocialCollaborationManager()
        manager.zk_verification = mock_zk_verification
        manager.notification_service = mock_notification_service
        manager.reputation_manager = mock_reputation_manager
        
        # Mock ZK proof generation
        mock_zk_verification.generate_copy_proof.return_value = "zk_proof_abc123"
        
        with patch.object(manager, '_validate_expert_user',
                         return_value={'is_expert': True, 'name': 'Expert', 'reputation': 850}):
            with patch.object(manager, '_get_daily_copy_count', return_value=5):
                with patch.object(manager, '_validate_source_drawings', 
                                 return_value=[test_drawing]):
                    with patch.object(manager, '_validate_user_chart',
                                     return_value=Mock(id='chart_123', user_id=test_user.id)):
                        with patch.object(manager, '_copy_drawing_with_attribution',
                                         return_value={'id': 'copied_123', 'type': 'trend_line'}):
                            
                            copy_request = ExpertDrawingRequest(
                                expert_user_id=expert_user.id,
                                chart_id='source_chart_123',
                                drawing_ids=[test_drawing.id],
                                copy_to_chart_id='target_chart_123',
                                symbol='RELIANCE',
                                timeframe='15m'
                            )
                            
                            result = await manager.copy_expert_drawings(
                                db_session, test_user.id, copy_request
                            )
                            
                            assert result['success'] is True
                            assert 'copy_id' in result
                            assert len(result['copied_drawings']) == 1
                            assert result['expert_attribution']['expert_id'] == expert_user.id
                            assert result['zk_proof'] == "zk_proof_abc123"
                            
                            # Verify services were called
                            mock_zk_verification.generate_copy_proof.assert_called_once()
                            mock_notification_service.send_drawing_copied_notification.assert_called_once()
                            mock_reputation_manager.award_expert_copy_points.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_copy_from_non_expert(self, db_session, test_user):
        """Test copying from non-expert user should fail"""
        manager = SocialCollaborationManager()
        
        with patch.object(manager, '_validate_expert_user',
                         return_value={'is_expert': False}):
            
            copy_request = ExpertDrawingRequest(
                expert_user_id='non_expert_user',
                chart_id='chart_123',
                drawing_ids=['drawing_123'],
                copy_to_chart_id='target_chart_123',
                symbol='RELIANCE',
                timeframe='15m'
            )
            
            with pytest.raises(HTTPException) as exc_info:
                await manager.copy_expert_drawings(
                    db_session, test_user.id, copy_request
                )
            
            assert exc_info.value.status_code == 403
            assert "not a verified expert" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_daily_copy_limit_exceeded(self, db_session, test_user, expert_user):
        """Test daily copy limit enforcement"""
        manager = SocialCollaborationManager()
        
        with patch.object(manager, '_validate_expert_user',
                         return_value={'is_expert': True}):
            with patch.object(manager, '_get_daily_copy_count', 
                             return_value=manager.collaboration_limits['max_drawing_copies_per_day']):
                
                copy_request = ExpertDrawingRequest(
                    expert_user_id=expert_user.id,
                    chart_id='chart_123',
                    drawing_ids=['drawing_123'],
                    copy_to_chart_id='target_chart_123',
                    symbol='RELIANCE',
                    timeframe='15m'
                )
                
                with pytest.raises(HTTPException) as exc_info:
                    await manager.copy_expert_drawings(
                        db_session, test_user.id, copy_request
                    )
                
                assert exc_info.value.status_code == 429
                assert "Daily drawing copy limit reached" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_invalid_source_drawings(self, db_session, test_user, expert_user):
        """Test copying invalid or non-public drawings"""
        manager = SocialCollaborationManager()
        
        with patch.object(manager, '_validate_expert_user',
                         return_value={'is_expert': True}):
            with patch.object(manager, '_get_daily_copy_count', return_value=5):
                with patch.object(manager, '_validate_source_drawings',
                                 side_effect=HTTPException(status_code=404, detail="Drawings not found")):
                    
                    copy_request = ExpertDrawingRequest(
                        expert_user_id=expert_user.id,
                        chart_id='chart_123',
                        drawing_ids=['invalid_drawing_123'],
                        copy_to_chart_id='target_chart_123',
                        symbol='RELIANCE',
                        timeframe='15m'
                    )
                    
                    with pytest.raises(HTTPException) as exc_info:
                        await manager.copy_expert_drawings(
                            db_session, test_user.id, copy_request
                        )
                    
                    assert exc_info.value.status_code == 404
    
    @pytest.mark.asyncio
    async def test_copy_multiple_drawings(
        self, 
        db_session, 
        test_user, 
        expert_user,
        mock_zk_verification
    ):
        """Test copying multiple drawings at once"""
        manager = SocialCollaborationManager()
        manager.zk_verification = mock_zk_verification
        
        # Mock multiple drawings
        mock_drawings = [
            Mock(id='drawing_1', drawing_type='trend_line'),
            Mock(id='drawing_2', drawing_type='fibonacci'),
            Mock(id='drawing_3', drawing_type='support_line')
        ]
        
        with patch.object(manager, '_validate_expert_user',
                         return_value={'is_expert': True, 'name': 'Expert', 'reputation': 900}):
            with patch.object(manager, '_get_daily_copy_count', return_value=2):
                with patch.object(manager, '_validate_source_drawings', 
                                 return_value=mock_drawings):
                    with patch.object(manager, '_validate_user_chart',
                                     return_value=Mock(id='chart_123')):
                        with patch.object(manager, '_copy_drawing_with_attribution',
                                         side_effect=[
                                             {'id': 'copied_1', 'type': 'trend_line'},
                                             {'id': 'copied_2', 'type': 'fibonacci'},
                                             {'id': 'copied_3', 'type': 'support_line'}
                                         ]):
                            
                            copy_request = ExpertDrawingRequest(
                                expert_user_id=expert_user.id,
                                chart_id='source_chart_123',
                                drawing_ids=['drawing_1', 'drawing_2', 'drawing_3'],
                                copy_to_chart_id='target_chart_123',
                                symbol='RELIANCE',
                                timeframe='15m'
                            )
                            
                            result = await manager.copy_expert_drawings(
                                db_session, test_user.id, copy_request
                            )
                            
                            assert result['success'] is True
                            assert len(result['copied_drawings']) == 3
                            assert result['drawings_count'] == 3


class TestCollaborativeAnnotations:
    """Test collaborative annotation functionality"""
    
    @pytest.mark.asyncio
    async def test_create_annotation_success(
        self, 
        db_session, 
        test_user,
        mock_reputation_manager
    ):
        """Test successful annotation creation"""
        manager = SocialCollaborationManager()
        manager.reputation_manager = mock_reputation_manager
        
        with patch.object(manager, '_validate_chart_collaboration_access',
                         return_value={'can_comment': True, 'can_edit': True}):
            with patch.object(manager, '_get_chart_annotation_count', return_value=25):
                with patch.object(manager, '_broadcast_annotation_to_session') as mock_broadcast:
                    
                    annotation_request = CollaborativeAnnotationRequest(
                        chart_id='chart_123',
                        annotation_type='ANALYSIS',
                        content='Strong resistance level at this price point',
                        position={'x': 150.5, 'y': 2500.0},
                        drawing_reference_id='drawing_123'
                    )
                    
                    result = await manager.create_collaborative_annotation(
                        db_session, test_user.id, annotation_request
                    )
                    
                    assert result['success'] is True
                    assert 'annotation_id' in result
                    assert result['annotation']['type'] == 'ANALYSIS'
                    assert result['annotation']['content'] == 'Strong resistance level at this price point'
                    assert result['annotation']['position'] == {'x': 150.5, 'y': 2500.0}
                    
                    # Verify reputation points awarded
                    mock_reputation_manager.award_collaboration_points.assert_called_once_with(
                        db_session, test_user.id, 'annotation'
                    )
    
    @pytest.mark.asyncio
    async def test_create_threaded_annotation(self, db_session, test_user):
        """Test creating threaded annotation response"""
        manager = SocialCollaborationManager()
        
        with patch.object(manager, '_validate_chart_collaboration_access',
                         return_value={'can_comment': True}):
            with patch.object(manager, '_get_chart_annotation_count', return_value=15):
                with patch.object(manager, '_update_annotation_thread') as mock_update_thread:
                    with patch.object(manager, '_get_annotation_thread_info',
                                     return_value={'thread_id': 'thread_123', 'child_count': 2}):
                        
                        annotation_request = CollaborativeAnnotationRequest(
                            chart_id='chart_123',
                            annotation_type='QUESTION',
                            content='What makes you think this is a strong resistance?',
                            position={'x': 150.5, 'y': 2500.0},
                            parent_annotation_id='parent_annotation_123'
                        )
                        
                        result = await manager.create_collaborative_annotation(
                            db_session, test_user.id, annotation_request
                        )
                        
                        assert result['success'] is True
                        assert result['thread_info'] is not None
                        assert result['thread_info']['thread_id'] == 'thread_123'
                        
                        # Verify thread was updated
                        mock_update_thread.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_annotation_access_denied(self, db_session, test_user):
        """Test annotation creation with insufficient permissions"""
        manager = SocialCollaborationManager()
        
        with patch.object(manager, '_validate_chart_collaboration_access',
                         return_value={'can_comment': False, 'can_edit': False}):
            
            annotation_request = CollaborativeAnnotationRequest(
                chart_id='chart_123',
                annotation_type='NOTE',
                content='This should fail',
                position={'x': 100.0, 'y': 200.0}
            )
            
            with pytest.raises(HTTPException) as exc_info:
                await manager.create_collaborative_annotation(
                    db_session, test_user.id, annotation_request
                )
            
            assert exc_info.value.status_code == 403
            assert "No permission to add annotations" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_annotation_limit_exceeded(self, db_session, test_user):
        """Test annotation creation when chart limit is exceeded"""
        manager = SocialCollaborationManager()
        
        with patch.object(manager, '_validate_chart_collaboration_access',
                         return_value={'can_comment': True}):
            with patch.object(manager, '_get_chart_annotation_count',
                             return_value=manager.collaboration_limits['max_annotations_per_chart']):
                
                annotation_request = CollaborativeAnnotationRequest(
                    chart_id='chart_123',
                    annotation_type='NOTE',
                    content='This should fail due to limit',
                    position={'x': 100.0, 'y': 200.0}
                )
                
                with pytest.raises(HTTPException) as exc_info:
                    await manager.create_collaborative_annotation(
                        db_session, test_user.id, annotation_request
                    )
                
                assert exc_info.value.status_code == 429
                assert "annotation limit reached" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_real_time_annotation_broadcast(self, db_session, test_user):
        """Test real-time annotation broadcasting to session participants"""
        manager = SocialCollaborationManager()
        
        # Setup active session
        session_id = 'session_123'
        manager.user_sessions[test_user.id] = session_id
        
        mock_websocket = AsyncMock()
        manager.active_sessions[session_id] = ActiveCollaboration(
            session_id=session_id,
            chart_id='chart_123',
            participants={test_user.id, 'other_user_id'},
            websockets={'other_user_id': mock_websocket},
            last_activity=datetime.utcnow(),
            permissions={}
        )
        
        with patch.object(manager, '_validate_chart_collaboration_access',
                         return_value={'can_comment': True}):
            with patch.object(manager, '_get_chart_annotation_count', return_value=10):
                
                annotation_request = CollaborativeAnnotationRequest(
                    chart_id='chart_123',
                    annotation_type='INSIGHT',
                    content='Real-time annotation test',
                    position={'x': 200.0, 'y': 300.0}
                )
                
                result = await manager.create_collaborative_annotation(
                    db_session, test_user.id, annotation_request
                )
                
                assert result['success'] is True
                
                # Verify WebSocket broadcast
                mock_websocket.send_json.assert_called_once()
                broadcast_message = mock_websocket.send_json.call_args[0][0]
                assert broadcast_message['type'] == 'new_annotation'
                assert broadcast_message['annotation']['content'] == 'Real-time annotation test'


class TestCollaborationSessions:
    """Test real-time collaboration session functionality"""
    
    @pytest.mark.asyncio
    async def test_start_collaboration_session_success(
        self, 
        db_session, 
        test_user,
        mock_notification_service
    ):
        """Test successful collaboration session creation"""
        manager = SocialCollaborationManager()
        manager.notification_service = mock_notification_service
        
        with patch.object(manager, '_validate_user_chart',
                         return_value=Mock(id='chart_123', user_id=test_user.id)):
            with patch.object(manager, '_validate_invited_users',
                             return_value=[
                                 {'id': 'user1', 'name': 'User One'},
                                 {'id': 'user2', 'name': 'User Two'}
                             ]):
                
                invite_request = CollaborationInviteRequest(
                    chart_id='chart_123',
                    invited_user_ids=['user1', 'user2'],
                    permission_level='COMMENT',
                    expires_in_hours=12
                )
                
                result = await manager.start_collaboration_session(
                    db_session, test_user.id, invite_request
                )
                
                assert result['success'] is True
                assert 'session_id' in result
                assert result['chart_id'] == 'chart_123'
                assert len(result['invited_users']) == 2
                assert result['permissions'][test_user.id] == 'OWNER'
                assert result['permissions']['user1'] == 'COMMENT'
                assert result['permissions']['user2'] == 'COMMENT'
                
                # Verify session is tracked
                session_id = result['session_id']
                assert session_id in manager.active_sessions
                
                # Verify invitations were sent
                assert mock_notification_service.send_collaboration_invite.call_count == 2
    
    @pytest.mark.asyncio
    async def test_start_session_concurrent_limit(self, db_session, test_user):
        """Test collaboration session creation with concurrent limit exceeded"""
        manager = SocialCollaborationManager()
        
        # Create max concurrent sessions
        max_sessions = manager.collaboration_limits['max_concurrent_sessions']
        for i in range(max_sessions):
            session_id = f'session_{i}'
            manager.active_sessions[session_id] = ActiveCollaboration(
                session_id=session_id,
                chart_id=f'chart_{i}',
                participants={test_user.id},
                websockets={},
                last_activity=datetime.utcnow(),
                permissions={}
            )
        
        with patch.object(manager, '_validate_user_chart',
                         return_value=Mock(id='chart_new', user_id=test_user.id)):
            
            invite_request = CollaborationInviteRequest(
                chart_id='chart_new',
                invited_user_ids=['user1'],
                permission_level='VIEW'
            )
            
            with pytest.raises(HTTPException) as exc_info:
                await manager.start_collaboration_session(
                    db_session, test_user.id, invite_request
                )
            
            assert exc_info.value.status_code == 429
            assert "Maximum concurrent collaboration sessions reached" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_join_collaboration_session_success(
        self, 
        db_session, 
        test_user,
        mock_websocket
    ):
        """Test successful joining of collaboration session"""
        manager = SocialCollaborationManager()
        
        # Create existing session
        session_id = 'session_123'
        
        # Mock database session
        mock_db_session = Mock()
        mock_db_session.id = session_id
        mock_db_session.chart_id = 'chart_123'
        mock_db_session.host_user_id = 'host_user'
        mock_db_session.invited_user_ids = json.dumps([test_user.id])
        mock_db_session.permission_level = 'EDIT'
        mock_db_session.is_active = True
        mock_db_session.expires_at = datetime.utcnow() + timedelta(hours=2)
        
        with patch.object(db_session, 'query') as mock_query:
            mock_query.return_value.filter.return_value.first.return_value = mock_db_session
            
            with patch.object(manager, '_send_session_state') as mock_send_state:
                with patch.object(manager, '_broadcast_user_joined') as mock_broadcast:
                    
                    result = await manager.join_collaboration_session(
                        db_session, test_user.id, session_id, mock_websocket
                    )
                    
                    assert result['success'] is True
                    assert result['session_id'] == session_id
                    assert result['participant_count'] == 1
                    assert result['your_permissions'] == 'EDIT'
                    
                    # Verify WebSocket was accepted
                    mock_websocket.accept.assert_called_once()
                    
                    # Verify session state was sent
                    mock_send_state.assert_called_once()
                    
                    # Verify broadcast
                    mock_broadcast.assert_called_once()
                    
                    # Verify user is tracked in session
                    assert test_user.id in manager.active_sessions[session_id].participants
                    assert manager.user_sessions[test_user.id] == session_id
    
    @pytest.mark.asyncio
    async def test_join_session_not_invited(self, db_session, test_user, mock_websocket):
        """Test joining session when not invited"""
        manager = SocialCollaborationManager()
        
        # Mock database session with different invited users
        mock_db_session = Mock()
        mock_db_session.id = 'session_123'
        mock_db_session.host_user_id = 'host_user'
        mock_db_session.invited_user_ids = json.dumps(['other_user'])  # Not test_user
        mock_db_session.is_active = True
        mock_db_session.expires_at = datetime.utcnow() + timedelta(hours=2)
        
        with patch.object(db_session, 'query') as mock_query:
            mock_query.return_value.filter.return_value.first.return_value = mock_db_session
            
            with pytest.raises(HTTPException) as exc_info:
                await manager.join_collaboration_session(
                    db_session, test_user.id, 'session_123', mock_websocket
                )
            
            assert exc_info.value.status_code == 403
            assert "Not invited to this session" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_join_session_participants_limit(
        self, 
        db_session, 
        test_user, 
        mock_websocket
    ):
        """Test joining session when participants limit is reached"""
        manager = SocialCollaborationManager()
        
        # Create session at capacity
        session_id = 'session_123'
        max_participants = manager.collaboration_limits['max_participants_per_session']
        
        participants = {f'user_{i}' for i in range(max_participants)}
        manager.active_sessions[session_id] = ActiveCollaboration(
            session_id=session_id,
            chart_id='chart_123',
            participants=participants,
            websockets={},
            last_activity=datetime.utcnow(),
            permissions={}
        )
        
        # Mock database session
        mock_db_session = Mock()
        mock_db_session.id = session_id
        mock_db_session.host_user_id = 'host_user'
        mock_db_session.invited_user_ids = json.dumps([test_user.id])
        mock_db_session.is_active = True
        mock_db_session.expires_at = datetime.utcnow() + timedelta(hours=2)
        
        with patch.object(db_session, 'query') as mock_query:
            mock_query.return_value.filter.return_value.first.return_value = mock_db_session
            
            with pytest.raises(HTTPException) as exc_info:
                await manager.join_collaboration_session(
                    db_session, test_user.id, session_id, mock_websocket
                )
            
            assert exc_info.value.status_code == 429
            assert "Collaboration session is full" in str(exc_info.value.detail)


class TestExpertStatusApplication:
    """Test expert status application functionality"""
    
    @pytest.mark.asyncio
    async def test_expert_application_auto_approved(
        self, 
        db_session, 
        test_user,
        mock_reputation_manager
    ):
        """Test expert application that meets all criteria for auto-approval"""
        manager = SocialCollaborationManager()
        manager.reputation_manager = mock_reputation_manager
        
        # Mock user stats that meet all criteria
        mock_stats = {
            'total_drawings': 60,  # Above min_drawings (50)
            'followers': 15,       # Above min_followers (10)
            'success_rate': 0.75,  # Above min_success_rate (0.65)
            'reputation': 800      # Above min_reputation (750)
        }
        
        with patch.object(manager, '_get_user_trading_stats', return_value=mock_stats):
            
            expert_request = ExpertProfileRequest(
                specialization=['NIFTY', 'OPTIONS'],
                years_experience=5,
                trading_style='Swing Trading',
                bio='Experienced trader with consistent track record',
                verified_performance={'win_rate': 0.75, 'total_trades': 500}
            )
            
            result = await manager.apply_for_expert_status(
                db_session, test_user.id, expert_request
            )
            
            assert result['success'] is True
            assert 'expert_profile_id' in result
            assert result['application_status'] == 'APPROVED'
            assert result['auto_approved'] is True
            assert all(result['criteria_met'].values())  # All criteria should be met
            
            # Verify expert status points were awarded
            mock_reputation_manager.award_expert_status_points.assert_called_once_with(
                db_session, test_user.id
            )
    
    @pytest.mark.asyncio
    async def test_expert_application_pending_review(self, db_session, test_user):
        """Test expert application that requires manual review"""
        manager = SocialCollaborationManager()
        
        # Mock user stats that don't meet all criteria
        mock_stats = {
            'total_drawings': 30,  # Below min_drawings (50)
            'followers': 15,       # Above min_followers (10)
            'success_rate': 0.68,  # Above min_success_rate (0.65)
            'reputation': 700      # Below min_reputation (750)
        }
        
        with patch.object(manager, '_get_user_trading_stats', return_value=mock_stats):
            
            expert_request = ExpertProfileRequest(
                specialization=['EQUITY'],
                years_experience=3,
                trading_style='Day Trading',
                bio='Aspiring expert trader'
            )
            
            result = await manager.apply_for_expert_status(
                db_session, test_user.id, expert_request
            )
            
            assert result['success'] is True
            assert result['application_status'] == 'PENDING'
            assert result['auto_approved'] is False
            assert not all(result['criteria_met'].values())  # Some criteria not met
            assert result['next_steps'] == 'Manual review required'
    
    @pytest.mark.asyncio
    async def test_duplicate_expert_application(self, db_session, test_user):
        """Test duplicate expert application should fail"""
        manager = SocialCollaborationManager()
        
        # Mock existing expert profile
        with patch.object(db_session, 'query') as mock_query:
            mock_query.return_value.filter.return_value.first.return_value = Mock()  # Existing profile
            
            expert_request = ExpertProfileRequest(
                specialization=['CRYPTO'],
                years_experience=2,
                trading_style='Scalping',
                bio='Already applied'
            )
            
            with pytest.raises(HTTPException) as exc_info:
                await manager.apply_for_expert_status(
                    db_session, test_user.id, expert_request
                )
            
            assert exc_info.value.status_code == 400
            assert "Expert profile already exists" in str(exc_info.value.detail)


class TestSocialCollaborationHelpers:
    """Test helper methods for social collaboration"""
    
    @pytest.mark.asyncio
    async def test_validate_expert_user_success(self, db_session, expert_user):
        """Test successful expert user validation"""
        manager = SocialCollaborationManager()
        
        # Mock expert profile query
        mock_expert_profile = Mock()
        mock_expert_profile.user_id = expert_user.id
        mock_expert_profile.is_active = True
        mock_expert_profile.application_status = 'APPROVED'
        mock_expert_profile.specialization = json.dumps(['NIFTY', 'OPTIONS'])
        mock_expert_profile.verified_at = datetime.utcnow()
        
        # Mock user profile query
        mock_user_profile = Mock()
        mock_user_profile.display_name = 'Expert Trader'
        
        with patch.object(db_session, 'query') as mock_query:
            mock_query.return_value.filter.return_value.first.side_effect = [
                mock_expert_profile,  # First call for ExpertProfile
                mock_user_profile     # Second call for UserProfile
            ]
            
            with patch.object(manager.reputation_manager, 'get_user_reputation',
                             return_value=850):
                
                result = await manager._validate_expert_user(db_session, expert_user.id)
                
                assert result['is_expert'] is True
                assert result['name'] == 'Expert Trader'
                assert result['reputation'] == 850
                assert result['specialization'] == ['NIFTY', 'OPTIONS']
    
    @pytest.mark.asyncio
    async def test_validate_expert_user_not_expert(self, db_session, test_user):
        """Test expert user validation for non-expert"""
        manager = SocialCollaborationManager()
        
        with patch.object(db_session, 'query') as mock_query:
            mock_query.return_value.filter.return_value.first.return_value = None
            
            result = await manager._validate_expert_user(db_session, test_user.id)
            
            assert result['is_expert'] is False
    
    @pytest.mark.asyncio
    async def test_get_daily_copy_count(self, db_session, test_user):
        """Test daily copy count calculation"""
        manager = SocialCollaborationManager()
        
        with patch.object(db_session, 'query') as mock_query:
            mock_query.return_value.filter.return_value.count.return_value = 8
            
            count = await manager._get_daily_copy_count(db_session, test_user.id)
            
            assert count == 8
    
    @pytest.mark.asyncio
    async def test_validate_chart_collaboration_access_owner(self, db_session, test_user):
        """Test chart collaboration access for chart owner"""
        manager = SocialCollaborationManager()
        
        # Mock chart owned by user
        mock_chart = Mock()
        mock_chart.id = 'chart_123'
        mock_chart.user_id = test_user.id
        
        with patch.object(db_session, 'query') as mock_query:
            mock_query.return_value.filter.return_value.first.return_value = mock_chart
            
            access = await manager._validate_chart_collaboration_access(
                db_session, test_user.id, 'chart_123'
            )
            
            assert access['can_comment'] is True
            assert access['can_edit'] is True
            assert access['is_owner'] is True
    
    @pytest.mark.asyncio
    async def test_validate_chart_collaboration_access_participant(self, db_session, test_user):
        """Test chart collaboration access for session participant"""
        manager = SocialCollaborationManager()
        
        # Setup active session
        session_id = 'session_123'
        manager.user_sessions[test_user.id] = session_id
        manager.active_sessions[session_id] = ActiveCollaboration(
            session_id=session_id,
            chart_id='chart_123',
            participants={test_user.id},
            websockets={},
            last_activity=datetime.utcnow(),
            permissions={test_user.id: 'EDIT'}
        )
        
        # Mock chart not owned by user
        with patch.object(db_session, 'query') as mock_query:
            mock_query.return_value.filter.return_value.first.return_value = None
            
            access = await manager._validate_chart_collaboration_access(
                db_session, test_user.id, 'chart_123'
            )
            
            assert access['can_comment'] is True
            assert access['can_edit'] is True
            assert access['is_owner'] is False
    
    @pytest.mark.asyncio
    async def test_validate_chart_collaboration_access_denied(self, db_session, test_user):
        """Test chart collaboration access denied"""
        manager = SocialCollaborationManager()
        
        # Mock chart not owned by user and no active session
        with patch.object(db_session, 'query') as mock_query:
            mock_query.return_value.filter.return_value.first.return_value = None
            
            access = await manager._validate_chart_collaboration_access(
                db_session, test_user.id, 'chart_123'
            )
            
            assert access['can_comment'] is False
            assert access['can_edit'] is False
            assert access['is_owner'] is False


class TestSocialCollaborationAPIEndpoints:
    """Test social collaboration API endpoints"""
    
    def test_copy_expert_drawings_endpoint(self, test_client, auth_headers):
        """Test /api/v1/social/copy-expert-drawings endpoint"""
        copy_data = {
            "expert_user_id": "expert_123",
            "chart_id": "source_chart_123",
            "drawing_ids": ["drawing_1", "drawing_2"],
            "copy_to_chart_id": "target_chart_123",
            "symbol": "RELIANCE",
            "timeframe": "15m"
        }
        
        with patch('app.features.social_collaboration.social_collaboration') as mock_manager:
            mock_manager.copy_expert_drawings.return_value = {
                'success': True,
                'copy_id': 'copy_123',
                'copied_drawings': [
                    {'id': 'copied_1', 'type': 'trend_line'},
                    {'id': 'copied_2', 'type': 'fibonacci'}
                ],
                'expert_attribution': {
                    'expert_id': 'expert_123',
                    'expert_name': 'Expert Trader',
                    'expert_reputation': 850
                },
                'zk_proof': 'zk_proof_abc123'
            }
            
            response = test_client.post(
                "/api/v1/social/copy-expert-drawings",
                json=copy_data,
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data['success'] is True
            assert data['copy_id'] == 'copy_123'
            assert len(data['copied_drawings']) == 2
    
    def test_add_annotation_endpoint(self, test_client, auth_headers):
        """Test /api/v1/social/add-annotation endpoint"""
        annotation_data = {
            "chart_id": "chart_123",
            "annotation_type": "ANALYSIS",
            "content": "Strong support level here",
            "position": {"x": 150.0, "y": 2500.0},
            "drawing_reference_id": "drawing_123"
        }
        
        with patch('app.features.social_collaboration.social_collaboration') as mock_manager:
            mock_manager.create_collaborative_annotation.return_value = {
                'success': True,
                'annotation_id': 'annotation_123',
                'annotation': {
                    'id': 'annotation_123',
                    'type': 'ANALYSIS',
                    'content': 'Strong support level here',
                    'position': {'x': 150.0, 'y': 2500.0},
                    'created_at': datetime.utcnow().isoformat(),
                    'author': {
                        'id': 'user_123',
                        'name': 'Test User',
                        'reputation': 650
                    }
                }
            }
            
            response = test_client.post(
                "/api/v1/social/add-annotation",
                json=annotation_data,
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data['success'] is True
            assert data['annotation']['content'] == 'Strong support level here'
    
    def test_start_collaboration_endpoint(self, test_client, auth_headers):
        """Test /api/v1/social/start-collaboration endpoint"""
        collaboration_data = {
            "chart_id": "chart_123",
            "invited_user_ids": ["user_1", "user_2"],
            "permission_level": "COMMENT",
            "expires_in_hours": 24
        }
        
        with patch('app.features.social_collaboration.social_collaboration') as mock_manager:
            mock_manager.start_collaboration_session.return_value = {
                'success': True,
                'session_id': 'session_123',
                'chart_id': 'chart_123',
                'invited_users': [
                    {'id': 'user_1', 'name': 'User One'},
                    {'id': 'user_2', 'name': 'User Two'}
                ],
                'permissions': {
                    'user_123': 'OWNER',
                    'user_1': 'COMMENT',
                    'user_2': 'COMMENT'
                },
                'join_url': '/charts/collaborate/session_123',
                'expires_at': (datetime.utcnow() + timedelta(hours=24)).isoformat()
            }
            
            response = test_client.post(
                "/api/v1/social/start-collaboration",
                json=collaboration_data,
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data['session_id'] == 'session_123'
            assert len(data['participants']) == 2
    
    def test_apply_expert_status_endpoint(self, test_client, auth_headers):
        """Test /api/v1/social/apply-expert-status endpoint"""
        expert_data = {
            "specialization": ["NIFTY", "OPTIONS"],
            "years_experience": 5,
            "trading_style": "Swing Trading",
            "bio": "Experienced trader with proven track record",
            "verified_performance": {"win_rate": 0.75, "total_trades": 500}
        }
        
        with patch('app.features.social_collaboration.social_collaboration') as mock_manager:
            mock_manager.apply_for_expert_status.return_value = {
                'success': True,
                'expert_profile_id': 'expert_profile_123',
                'application_status': 'APPROVED',
                'criteria_met': {
                    'drawings': True,
                    'followers': True,
                    'success_rate': True,
                    'reputation': True
                },
                'auto_approved': True,
                'next_steps': 'Expert status activated'
            }
            
            response = test_client.post(
                "/api/v1/social/apply-expert-status",
                json=expert_data,
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data['success'] is True
            assert data['application_status'] == 'APPROVED'
            assert data['auto_approved'] is True
    
    def test_get_expert_profiles_endpoint(self, test_client):
        """Test /api/v1/social/expert-profiles endpoint"""
        with patch('app.models.social.ExpertProfile') as mock_expert_model:
            # Mock database query would go here
            pass
        
        response = test_client.get("/api/v1/social/expert-profiles?specialization=NIFTY&limit=10")
        
        # Response format depends on actual implementation
        assert response.status_code == 200
    
    def test_health_endpoint(self, test_client):
        """Test /api/v1/social/health endpoint"""
        response = test_client.get("/api/v1/social/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'healthy'
        assert data['social_collaboration'] == 'operational'
        assert 'features' in data
        assert data['features']['expert_drawing_copy'] is True
        assert data['features']['collaborative_annotations'] is True


class TestSocialCollaborationIntegration:
    """Integration tests for social collaboration features"""
    
    @pytest.mark.asyncio
    async def test_complete_collaboration_workflow(
        self, 
        db_session, 
        test_user, 
        expert_user,
        mock_websocket
    ):
        """Test complete collaboration workflow"""
        manager = SocialCollaborationManager()
        
        # Step 1: Start collaboration session
        with patch.object(manager, '_validate_user_chart', return_value=Mock()):
            with patch.object(manager, '_validate_invited_users',
                             return_value=[{'id': test_user.id, 'name': 'Test User'}]):
                
                invite_request = CollaborationInviteRequest(
                    chart_id='chart_123',
                    invited_user_ids=[test_user.id],
                    permission_level='EDIT'
                )
                
                session_result = await manager.start_collaboration_session(
                    db_session, expert_user.id, invite_request
                )
                
                assert session_result['success'] is True
                session_id = session_result['session_id']
        
        # Step 2: Join session
        mock_db_session = Mock()
        mock_db_session.id = session_id
        mock_db_session.chart_id = 'chart_123'
        mock_db_session.host_user_id = expert_user.id
        mock_db_session.invited_user_ids = json.dumps([test_user.id])
        mock_db_session.is_active = True
        mock_db_session.expires_at = datetime.utcnow() + timedelta(hours=2)
        
        with patch.object(db_session, 'query') as mock_query:
            mock_query.return_value.filter.return_value.first.return_value = mock_db_session
            
            join_result = await manager.join_collaboration_session(
                db_session, test_user.id, session_id, mock_websocket
            )
            
            assert join_result['success'] is True
        
        # Step 3: Add collaborative annotation
        with patch.object(manager, '_get_chart_annotation_count', return_value=5):
            
            annotation_request = CollaborativeAnnotationRequest(
                chart_id='chart_123',
                annotation_type='INSIGHT',
                content='Great analysis on this setup!',
                position={'x': 100.0, 'y': 200.0}
            )
            
            annotation_result = await manager.create_collaborative_annotation(
                db_session, test_user.id, annotation_request
            )
            
            assert annotation_result['success'] is True
        
        # Verify session state
        assert session_id in manager.active_sessions
        assert test_user.id in manager.active_sessions[session_id].participants
        assert manager.user_sessions[test_user.id] == session_id
    
    @pytest.mark.asyncio
    async def test_expert_copy_to_collaboration_workflow(
        self, 
        db_session, 
        test_user, 
        expert_user
    ):
        """Test workflow from expert drawing copy to collaboration"""
        manager = SocialCollaborationManager()
        
        # Step 1: Copy expert drawings
        with patch.object(manager, '_validate_expert_user',
                         return_value={'is_expert': True, 'name': 'Expert', 'reputation': 900}):
            with patch.object(manager, '_get_daily_copy_count', return_value=3):
                with patch.object(manager, '_validate_source_drawings',
                                 return_value=[Mock(id='drawing_1')]):
                    with patch.object(manager, '_validate_user_chart',
                                     return_value=Mock(id='chart_123')):
                        with patch.object(manager, '_copy_drawing_with_attribution',
                                         return_value={'id': 'copied_1', 'type': 'trend_line'}):
                            
                            copy_request = ExpertDrawingRequest(
                                expert_user_id=expert_user.id,
                                chart_id='expert_chart',
                                drawing_ids=['drawing_1'],
                                copy_to_chart_id='chart_123',
                                symbol='RELIANCE',
                                timeframe='15m'
                            )
                            
                            copy_result = await manager.copy_expert_drawings(
                                db_session, test_user.id, copy_request
                            )
                            
                            assert copy_result['success'] is True
        
        # Step 2: Add annotation about copied drawing
        with patch.object(manager, '_get_chart_annotation_count', return_value=2):
            
            annotation_request = CollaborativeAnnotationRequest(
                chart_id='chart_123',
                annotation_type='QUESTION',
                content='Why did you choose this trend line angle?',
                position={'x': 150.0, 'y': 250.0},
                drawing_reference_id='copied_1'
            )
            
            annotation_result = await manager.create_collaborative_annotation(
                db_session, test_user.id, annotation_request
            )
            
            assert annotation_result['success'] is True
            
        # Verify the workflow created proper attribution and discussion
        assert copy_result['expert_attribution']['expert_id'] == expert_user.id
        assert annotation_result['annotation']['drawing_reference_id'] == 'copied_1'