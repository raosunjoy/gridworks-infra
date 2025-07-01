"""
GridWorks B2B Services - Authentication Unit Tests
Comprehensive test coverage for enterprise authentication system
"""

import pytest
import pytest_asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
import jwt
import hashlib
import secrets
from fastapi import HTTPException

from ...auth.enterprise_auth import (
    EnterpriseAuth, TokenData, APIKeyData,
    auth_handler, get_current_user, get_api_key_data, PermissionChecker
)
from ...database.models import EnterpriseClient, User, APIKey, AuditLog
from ...config import settings


class TestEnterpriseAuth:
    """Test suite for EnterpriseAuth class."""
    
    @pytest_asyncio.fixture
    async def auth_system(self, mock_redis):
        """Create EnterpriseAuth instance with mocked dependencies."""
        with patch('redis.Redis.from_url', return_value=mock_redis):
            return EnterpriseAuth()
    
    @pytest_asyncio.fixture
    async def sample_token_data(self):
        """Sample token data for testing."""
        return {
            "client_id": "test-client-123",
            "user_id": "test-user-456",
            "email": "test@example.com",
            "roles": ["admin", "trader"],
            "permissions": ["ai_suite.*", "trading.execute"],
            "tier": "enterprise"
        }
    
    @pytest_asyncio.fixture
    async def sample_api_key_data(self):
        """Sample API key data for testing."""
        return {
            "client_id": "test-client-123",
            "name": "Test API Key",
            "permissions": ["ai_suite.support.query", "trading.read"],
            "rate_limit": 5000,
            "expires_in_days": 30
        }
    
    async def test_create_access_token_success(self, auth_system, test_db_session, sample_token_data):
        """Test successful access token creation."""
        result = await auth_system.create_access_token(
            client_id=sample_token_data["client_id"],
            user_id=sample_token_data["user_id"],
            email=sample_token_data["email"],
            roles=sample_token_data["roles"],
            permissions=sample_token_data["permissions"],
            tier=sample_token_data["tier"],
            db=test_db_session
        )
        
        assert "access_token" in result
        assert "refresh_token" in result
        assert result["token_type"] == "bearer"
        assert result["tier"] == sample_token_data["tier"]
        assert result["permissions"] == sample_token_data["permissions"]
        assert isinstance(result["expires_in"], int)
        
        # Verify token can be decoded
        decoded = jwt.decode(
            result["access_token"],
            settings.JWT_SECRET_KEY,
            algorithms=["HS256"]
        )
        assert decoded["client_id"] == sample_token_data["client_id"]
        assert decoded["user_id"] == sample_token_data["user_id"]
        assert decoded["type"] == "access"
    
    async def test_verify_token_success(self, auth_system, test_db_session, test_enterprise_client):
        """Test successful token verification."""
        # Create a valid token
        token_result = await auth_system.create_access_token(
            client_id=str(test_enterprise_client.id),
            user_id="test-user-123",
            email="test@example.com",
            roles=["admin"],
            permissions=["ai_suite.*"],
            tier="enterprise",
            db=test_db_session
        )
        
        # Mock credentials
        from fastapi.security import HTTPAuthorizationCredentials
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=token_result["access_token"]
        )
        
        # Verify token
        with patch.object(auth_system, '_get_client', return_value=test_enterprise_client):
            with patch.object(auth_system, '_is_token_blacklisted', return_value=False):
                token_data = await auth_system.verify_token(credentials, test_db_session)
                
                assert isinstance(token_data, TokenData)
                assert token_data.client_id == str(test_enterprise_client.id)
                assert token_data.email == "test@example.com"
    
    async def test_verify_token_expired(self, auth_system, test_db_session):
        """Test token verification with expired token."""
        # Create expired token
        expired_payload = {
            "client_id": "test-client",
            "user_id": "test-user",
            "email": "test@example.com",
            "exp": datetime.utcnow() - timedelta(hours=1),
            "type": "access"
        }
        
        expired_token = jwt.encode(
            expired_payload,
            settings.JWT_SECRET_KEY,
            algorithm="HS256"
        )
        
        from fastapi.security import HTTPAuthorizationCredentials
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=expired_token
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await auth_system.verify_token(credentials, test_db_session)
        
        assert exc_info.value.status_code == 401
        assert "expired" in exc_info.value.detail.lower()
    
    async def test_verify_token_invalid(self, auth_system, test_db_session):
        """Test token verification with invalid token."""
        from fastapi.security import HTTPAuthorizationCredentials
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="invalid.token.here"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await auth_system.verify_token(credentials, test_db_session)
        
        assert exc_info.value.status_code == 401
        assert "invalid" in exc_info.value.detail.lower()
    
    async def test_verify_token_blacklisted(self, auth_system, test_db_session, test_enterprise_client):
        """Test token verification with blacklisted token."""
        # Create valid token
        token_result = await auth_system.create_access_token(
            client_id=str(test_enterprise_client.id),
            user_id="test-user",
            email="test@example.com",
            roles=["admin"],
            permissions=["ai_suite.*"],
            tier="enterprise",
            db=test_db_session
        )
        
        from fastapi.security import HTTPAuthorizationCredentials
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=token_result["access_token"]
        )
        
        # Mock blacklisted token
        with patch.object(auth_system, '_is_token_blacklisted', return_value=True):
            with pytest.raises(HTTPException) as exc_info:
                await auth_system.verify_token(credentials, test_db_session)
            
            assert exc_info.value.status_code == 401
            assert "invalidated" in exc_info.value.detail.lower()
    
    async def test_create_api_key_success(self, auth_system, test_db_session, sample_api_key_data):
        """Test successful API key creation."""
        result = await auth_system.create_api_key(
            client_id=sample_api_key_data["client_id"],
            name=sample_api_key_data["name"],
            permissions=sample_api_key_data["permissions"],
            rate_limit=sample_api_key_data["rate_limit"],
            expires_in_days=sample_api_key_data["expires_in_days"],
            db=test_db_session
        )
        
        assert "api_key" in result
        assert result["api_key"].startswith(settings.API_KEY_PREFIX)
        assert result["name"] == sample_api_key_data["name"]
        assert result["permissions"] == sample_api_key_data["permissions"]
        assert result["rate_limit"] == sample_api_key_data["rate_limit"]
        assert "expires_at" in result
        assert "note" in result
    
    async def test_verify_api_key_success(self, auth_system, test_db_session, test_api_key):
        """Test successful API key verification."""
        with patch.object(auth_system, '_get_api_key_from_cache', return_value=None):
            # Mock database query
            with patch('sqlalchemy.ext.asyncio.AsyncSession.execute') as mock_execute:
                mock_result = MagicMock()
                mock_result.scalar_one_or_none.return_value = test_api_key
                mock_execute.return_value = mock_result
                
                api_key_data = await auth_system.verify_api_key(
                    test_api_key._test_key_value,
                    test_db_session
                )
                
                assert isinstance(api_key_data, APIKeyData)
                assert api_key_data.key_id == str(test_api_key.id)
                assert api_key_data.client_id == str(test_api_key.client_id)
                assert api_key_data.name == test_api_key.name
    
    async def test_verify_api_key_invalid(self, auth_system, test_db_session):
        """Test API key verification with invalid key."""
        with patch.object(auth_system, '_get_api_key_from_cache', return_value=None):
            with patch('sqlalchemy.ext.asyncio.AsyncSession.execute') as mock_execute:
                mock_result = MagicMock()
                mock_result.scalar_one_or_none.return_value = None
                mock_execute.return_value = mock_result
                
                with pytest.raises(HTTPException) as exc_info:
                    await auth_system.verify_api_key("invalid_key", test_db_session)
                
                assert exc_info.value.status_code == 401
                assert "invalid" in exc_info.value.detail.lower()
    
    async def test_verify_api_key_expired(self, auth_system, test_db_session, test_api_key):
        """Test API key verification with expired key."""
        # Set expiration in the past
        test_api_key.expires_at = datetime.utcnow() - timedelta(days=1)
        
        with patch.object(auth_system, '_get_api_key_from_cache', return_value=None):
            with patch('sqlalchemy.ext.asyncio.AsyncSession.execute') as mock_execute:
                mock_result = MagicMock()
                mock_result.scalar_one_or_none.return_value = test_api_key
                mock_execute.return_value = mock_result
                
                with pytest.raises(HTTPException) as exc_info:
                    await auth_system.verify_api_key(
                        test_api_key._test_key_value,
                        test_db_session
                    )
                
                assert exc_info.value.status_code == 401
                assert "expired" in exc_info.value.detail.lower()
    
    @pytest.mark.parametrize("user_permissions,required_permissions,expected", [
        (["admin.*"], ["ai_suite.support.query"], True),
        (["ai_suite.*"], ["ai_suite.support.query"], True),
        (["ai_suite.support.query"], ["ai_suite.support.query"], True),
        (["trading.*"], ["ai_suite.support.query"], False),
        (["ai_suite.support.read"], ["ai_suite.support.query"], False),
        (["ai_suite.*", "trading.*"], ["ai_suite.support.query", "trading.execute"], True),
        (["ai_suite.*"], ["ai_suite.support.query", "trading.execute"], False),
    ])
    async def test_check_permissions(self, auth_system, user_permissions, required_permissions, expected):
        """Test permission checking logic."""
        result = await auth_system.check_permissions(required_permissions, user_permissions)
        assert result == expected
    
    async def test_rate_limiting_logic(self, auth_system, mock_redis):
        """Test rate limiting functionality."""
        client_id = "test-client-123"
        tier = "enterprise"
        
        # Mock Redis incr to simulate rate limiting
        mock_redis._data = {}
        
        # First call should pass
        await auth_system._check_rate_limits(client_id, tier)
        
        # Simulate hitting rate limit
        mock_redis._data[f"support_rate:{client_id}:{tier}"] = "1001"  # Over limit of 1000
        
        with pytest.raises(ValueError) as exc_info:
            await auth_system._check_rate_limits(client_id, tier)
        
        assert "rate limit exceeded" in str(exc_info.value).lower()
    
    async def test_token_caching(self, auth_system, mock_redis):
        """Test token metadata caching."""
        user_id = "test-user-123"
        access_token = "test-access-token"
        refresh_token = "test-refresh-token"
        
        await auth_system._store_token_metadata(
            user_id, access_token, refresh_token, None
        )
        
        # Check if tokens are stored in Redis
        access_key = f"token:access:{user_id}"
        refresh_key = f"token:refresh:{user_id}"
        
        assert access_key in mock_redis._data
        assert refresh_key in mock_redis._data
        assert mock_redis._data[access_key] == access_token
        assert mock_redis._data[refresh_key] == refresh_token
    
    async def test_api_key_caching(self, auth_system, mock_redis):
        """Test API key metadata caching."""
        api_key = "gw_test_api_key"
        client_id = "test-client-123"
        key_id = "key-456"
        permissions = ["ai_suite.*"]
        rate_limit = 5000
        
        await auth_system._store_api_key_metadata(
            api_key, client_id, key_id, permissions, rate_limit
        )
        
        # Check if API key is cached
        cache_key = f"apikey:{api_key}"
        assert cache_key in mock_redis._data
        
        # Test retrieval from cache
        cached_data = await auth_system._get_api_key_from_cache(api_key)
        assert cached_data is not None
        assert cached_data["client_id"] == client_id
        assert cached_data["key_id"] == key_id
        assert cached_data["permissions"] == permissions
        assert cached_data["rate_limit"] == rate_limit


class TestPermissionChecker:
    """Test suite for PermissionChecker dependency."""
    
    @pytest_asyncio.fixture
    async def permission_checker(self):
        """Create PermissionChecker instance."""
        return PermissionChecker(["ai_suite.support.query", "trading.read"])
    
    async def test_permission_check_success(self, permission_checker, mock_auth_user):
        """Test successful permission check."""
        # Mock user with sufficient permissions
        mock_auth_user.permissions = ["ai_suite.*", "trading.*"]
        
        result = await permission_checker(mock_auth_user)
        assert result == mock_auth_user
    
    async def test_permission_check_failure(self, permission_checker, mock_auth_user):
        """Test permission check failure."""
        # Mock user with insufficient permissions
        mock_auth_user.permissions = ["banking.*"]
        
        with pytest.raises(HTTPException) as exc_info:
            await permission_checker(mock_auth_user)
        
        assert exc_info.value.status_code == 403
        assert "insufficient permissions" in exc_info.value.detail.lower()
    
    async def test_admin_override(self, permission_checker, mock_auth_user):
        """Test admin permission override."""
        # Mock user with admin permissions
        mock_auth_user.permissions = ["admin.*"]
        
        result = await permission_checker(mock_auth_user)
        assert result == mock_auth_user


class TestDependencyInjection:
    """Test suite for dependency injection functions."""
    
    async def test_get_current_user_success(self, test_db_session, mock_auth_user):
        """Test get_current_user dependency."""
        from fastapi.security import HTTPAuthorizationCredentials
        
        # Mock valid token
        with patch('...auth.enterprise_auth.auth_handler.verify_token') as mock_verify:
            mock_verify.return_value = mock_auth_user
            
            credentials = HTTPAuthorizationCredentials(
                scheme="Bearer",
                credentials="valid_token"
            )
            
            result = await get_current_user(credentials, test_db_session)
            assert result == mock_auth_user
    
    async def test_get_api_key_data_success(self, test_db_session, mock_api_key_data):
        """Test get_api_key_data dependency."""
        with patch('...auth.enterprise_auth.auth_handler.verify_api_key') as mock_verify:
            mock_verify.return_value = mock_api_key_data
            
            result = await get_api_key_data("gw_test_key", test_db_session)
            assert result == mock_api_key_data


class TestSecurityFeatures:
    """Test suite for security-specific features."""
    
    async def test_password_hashing(self):
        """Test password hashing functionality."""
        import bcrypt
        
        password = "test_password_123"
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        
        # Verify password can be checked
        assert bcrypt.checkpw(password.encode(), hashed)
        assert not bcrypt.checkpw("wrong_password".encode(), hashed)
    
    async def test_token_signature_verification(self):
        """Test JWT token signature verification."""
        payload = {
            "client_id": "test-client",
            "user_id": "test-user",
            "exp": datetime.utcnow() + timedelta(hours=1)
        }
        
        # Create token with correct key
        token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")
        
        # Verify with correct key
        decoded = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
        assert decoded["client_id"] == payload["client_id"]
        
        # Verify fails with wrong key
        with pytest.raises(jwt.InvalidTokenError):
            jwt.decode(token, "wrong_key", algorithms=["HS256"])
    
    async def test_api_key_hashing(self):
        """Test API key hashing for storage."""
        api_key = "gw_test_" + secrets.token_urlsafe(32)
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        # Verify hash is deterministic
        key_hash2 = hashlib.sha256(api_key.encode()).hexdigest()
        assert key_hash == key_hash2
        
        # Verify different keys produce different hashes
        api_key2 = "gw_test_" + secrets.token_urlsafe(32)
        key_hash3 = hashlib.sha256(api_key2.encode()).hexdigest()
        assert key_hash != key_hash3
    
    async def test_timing_attack_protection(self, auth_system):
        """Test protection against timing attacks."""
        import time
        
        # Test with valid and invalid keys
        valid_key = "gw_test_valid_key"
        invalid_key = "gw_test_invalid_key"
        
        # Time the operations (in real implementation, these should take similar time)
        start_time = time.time()
        try:
            await auth_system.verify_api_key(valid_key, None)
        except:
            pass
        valid_time = time.time() - start_time
        
        start_time = time.time()
        try:
            await auth_system.verify_api_key(invalid_key, None)
        except:
            pass
        invalid_time = time.time() - start_time
        
        # Times should be similar (within reasonable variance)
        # This is a basic test - real timing attack protection would be more sophisticated
        time_difference = abs(valid_time - invalid_time)
        assert time_difference < 0.1  # Allow 100ms variance


class TestErrorHandling:
    """Test suite for error handling scenarios."""
    
    async def test_database_connection_error(self, auth_system):
        """Test handling of database connection errors."""
        # Mock database session that raises exception
        mock_db = MagicMock()
        mock_db.execute.side_effect = Exception("Database connection failed")
        
        with pytest.raises(Exception):
            await auth_system.verify_api_key("test_key", mock_db)
    
    async def test_redis_connection_error(self, auth_system):
        """Test handling of Redis connection errors."""
        # Mock Redis that raises exception
        with patch.object(auth_system.redis_client, 'get', side_effect=Exception("Redis unavailable")):
            # Should not raise exception, should fallback gracefully
            result = await auth_system._get_api_key_from_cache("test_key")
            assert result is None
    
    async def test_malformed_token_handling(self, auth_system, test_db_session):
        """Test handling of malformed tokens."""
        from fastapi.security import HTTPAuthorizationCredentials
        
        malformed_tokens = [
            "not.a.token",
            "definitely_not_jwt",
            "",
            "Bearer invalid",
            "header.payload"  # Missing signature
        ]
        
        for token in malformed_tokens:
            credentials = HTTPAuthorizationCredentials(
                scheme="Bearer",
                credentials=token
            )
            
            with pytest.raises(HTTPException) as exc_info:
                await auth_system.verify_token(credentials, test_db_session)
            
            assert exc_info.value.status_code == 401


class TestAuditLogging:
    """Test suite for audit logging functionality."""
    
    async def test_audit_log_creation(self, auth_system, test_db_session):
        """Test audit log entry creation."""
        from ...database.models import AuditLog
        
        # Mock audit log data
        audit_data = {
            "client_id": "test-client-123",
            "user_id": "test-user-456",
            "action": "token_created",
            "resource": "access_token",
            "ip_address": "192.168.1.100",
            "user_agent": "Test User Agent",
            "details": {"token_type": "access", "expires_in": 86400}
        }
        
        # Create audit log entry
        await auth_system._create_audit_log(audit_data, test_db_session)
        
        # Verify audit log was created
        from sqlalchemy import select
        result = await test_db_session.execute(
            select(AuditLog).where(AuditLog.action == "token_created")
        )
        audit_log = result.scalar_one_or_none()
        
        assert audit_log is not None
        assert audit_log.client_id == audit_data["client_id"]
        assert audit_log.user_id == audit_data["user_id"]
        assert audit_log.action == audit_data["action"]
        assert audit_log.ip_address == audit_data["ip_address"]
    
    async def test_audit_log_search(self, auth_system, test_db_session):
        """Test audit log search functionality."""
        # Create multiple audit log entries
        audit_entries = [
            {
                "client_id": "test-client-123",
                "action": "token_created",
                "resource": "access_token",
                "ip_address": "192.168.1.100"
            },
            {
                "client_id": "test-client-123",
                "action": "api_key_created",
                "resource": "api_key",
                "ip_address": "192.168.1.101"
            },
            {
                "client_id": "test-client-456",
                "action": "token_created",
                "resource": "refresh_token",
                "ip_address": "192.168.1.102"
            }
        ]
        
        for entry in audit_entries:
            await auth_system._create_audit_log(entry, test_db_session)
        
        # Search by client_id
        results = await auth_system._search_audit_logs(
            client_id="test-client-123",
            db=test_db_session
        )
        
        assert len(results) == 2
        assert all(log.client_id == "test-client-123" for log in results)
    
    async def test_audit_log_retention(self, auth_system, test_db_session):
        """Test audit log retention policy."""
        from datetime import datetime, timedelta
        from ...database.models import AuditLog
        
        # Create old audit log entry
        old_entry = AuditLog(
            client_id="test-client-123",
            action="old_action",
            resource="test_resource",
            ip_address="192.168.1.100",
            created_at=datetime.utcnow() - timedelta(days=400)  # Older than retention period
        )
        
        test_db_session.add(old_entry)
        await test_db_session.commit()
        
        # Run retention cleanup
        deleted_count = await auth_system._cleanup_old_audit_logs(
            retention_days=365,
            db=test_db_session
        )
        
        assert deleted_count >= 1


class TestMultiTenancy:
    """Test suite for multi-tenant functionality."""
    
    async def test_client_isolation(self, auth_system, test_db_session):
        """Test that clients are properly isolated."""
        # Create tokens for different clients
        client1_token = await auth_system.create_access_token(
            client_id="client-1",
            user_id="user-1",
            email="user1@client1.com",
            roles=["admin"],
            permissions=["ai_suite.*"],
            tier="enterprise",
            db=test_db_session
        )
        
        client2_token = await auth_system.create_access_token(
            client_id="client-2",
            user_id="user-2",
            email="user2@client2.com",
            roles=["user"],
            permissions=["trading.*"],
            tier="growth",
            db=test_db_session
        )
        
        # Verify tokens contain correct client information
        import jwt
        decoded1 = jwt.decode(
            client1_token["access_token"],
            settings.JWT_SECRET_KEY,
            algorithms=["HS256"]
        )
        decoded2 = jwt.decode(
            client2_token["access_token"],
            settings.JWT_SECRET_KEY,
            algorithms=["HS256"]
        )
        
        assert decoded1["client_id"] == "client-1"
        assert decoded2["client_id"] == "client-2"
        assert decoded1["tier"] == "enterprise"
        assert decoded2["tier"] == "growth"
    
    async def test_cross_client_access_denied(self, auth_system, test_db_session, test_enterprise_client):
        """Test that cross-client access is denied."""
        # Create token for one client
        token_result = await auth_system.create_access_token(
            client_id="different-client-id",
            user_id="test-user",
            email="test@different.com",
            roles=["admin"],
            permissions=["admin.*"],
            tier="enterprise",
            db=test_db_session
        )
        
        from fastapi.security import HTTPAuthorizationCredentials
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=token_result["access_token"]
        )
        
        # Mock client lookup to return different client
        with patch.object(auth_system, '_get_client', return_value=test_enterprise_client):
            with pytest.raises(HTTPException) as exc_info:
                await auth_system.verify_token(credentials, test_db_session)
            
            assert exc_info.value.status_code == 401
            assert "client mismatch" in exc_info.value.detail.lower()


class TestLoadTesting:
    """Test suite for load testing authentication system."""
    
    async def test_concurrent_token_creation(self, auth_system, test_db_session):
        """Test concurrent token creation performance."""
        import asyncio
        import time
        
        # Create multiple tokens concurrently
        start_time = time.time()
        
        tasks = []
        for i in range(10):
            task = auth_system.create_access_token(
                client_id=f"client-{i}",
                user_id=f"user-{i}",
                email=f"user{i}@test.com",
                roles=["user"],
                permissions=["basic.*"],
                tier="growth",
                db=test_db_session
            )
            tasks.append(task)
        
        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Verify all tokens were created successfully
        assert len(results) == 10
        assert all("access_token" in result for result in results)
        
        # Performance check - should complete within reasonable time
        assert total_time < 5.0  # Less than 5 seconds for 10 concurrent operations
    
    async def test_token_verification_performance(self, auth_system, test_db_session, test_enterprise_client):
        """Test token verification performance under load."""
        import asyncio
        import time
        
        # Create a token to verify
        token_result = await auth_system.create_access_token(
            client_id=str(test_enterprise_client.id),
            user_id="test-user",
            email="test@example.com",
            roles=["user"],
            permissions=["basic.*"],
            tier="enterprise",
            db=test_db_session
        )
        
        from fastapi.security import HTTPAuthorizationCredentials
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=token_result["access_token"]
        )
        
        # Perform multiple verifications
        start_time = time.time()
        
        with patch.object(auth_system, '_get_client', return_value=test_enterprise_client):
            with patch.object(auth_system, '_is_token_blacklisted', return_value=False):
                tasks = []
                for _ in range(20):
                    task = auth_system.verify_token(credentials, test_db_session)
                    tasks.append(task)
                
                results = await asyncio.gather(*tasks)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Verify all verifications succeeded
        assert len(results) == 20
        assert all(result.client_id == str(test_enterprise_client.id) for result in results)
        
        # Performance check
        assert total_time < 2.0  # Less than 2 seconds for 20 verifications
        
        # Average time per verification should be reasonable
        avg_time = total_time / 20
        assert avg_time < 0.1  # Less than 100ms per verification


class TestEdgeCases:
    """Test suite for edge cases and boundary conditions."""
    
    async def test_extremely_long_permissions_list(self, auth_system, test_db_session):
        """Test handling of very long permissions lists."""
        # Create a token with many permissions
        long_permissions = [f"service_{i}.action_{j}" for i in range(10) for j in range(10)]
        
        token_result = await auth_system.create_access_token(
            client_id="test-client",
            user_id="test-user",
            email="test@example.com",
            roles=["admin"],
            permissions=long_permissions,
            tier="enterprise",
            db=test_db_session
        )
        
        # Verify token was created successfully
        assert "access_token" in token_result
        assert token_result["permissions"] == long_permissions
        
        # Test permission checking with long list
        has_permission = await auth_system.check_permissions(
            ["service_5.action_7"],
            long_permissions
        )
        assert has_permission is True
    
    async def test_unicode_in_token_data(self, auth_system, test_db_session):
        """Test handling of unicode characters in token data."""
        # Create token with unicode characters
        token_result = await auth_system.create_access_token(
            client_id="test-client-unicode",
            user_id="test-user-unicode",
            email="тест@пример.com",  # Cyrillic characters
            roles=["admin"],
            permissions=["unicode.test"],
            tier="enterprise",
            db=test_db_session
        )
        
        # Verify token creation succeeded
        assert "access_token" in token_result
        
        # Decode and verify unicode data is preserved
        import jwt
        decoded = jwt.decode(
            token_result["access_token"],
            settings.JWT_SECRET_KEY,
            algorithms=["HS256"]
        )
        assert decoded["email"] == "тест@пример.com"
    
    async def test_maximum_api_key_length(self, auth_system, test_db_session):
        """Test API key creation at maximum length."""
        # Create API key with maximum allowed parameters
        max_permissions = [f"service_{i}.*" for i in range(50)]  # Large permission set
        
        api_key_result = await auth_system.create_api_key(
            client_id="test-client-max",
            name="Maximum Length API Key Test with Very Long Name That Tests Boundary Conditions",
            permissions=max_permissions,
            rate_limit=100000,  # Maximum rate limit
            expires_in_days=365,  # Maximum expiration
            db=test_db_session
        )
        
        # Verify API key creation succeeded
        assert "api_key" in api_key_result
        assert len(api_key_result["permissions"]) == 50
        assert api_key_result["rate_limit"] == 100000
    
    async def test_token_at_max_expiration(self, auth_system, test_db_session):
        """Test token creation at maximum expiration time."""
        from datetime import datetime, timedelta
        
        # Mock settings to allow longer expiration
        with patch.object(settings, 'JWT_ACCESS_TOKEN_EXPIRE_MINUTES', 525600):  # 1 year
            token_result = await auth_system.create_access_token(
                client_id="test-client-max-exp",
                user_id="test-user-max-exp",
                email="maxexp@test.com",
                roles=["user"],
                permissions=["basic.*"],
                tier="enterprise",
                db=test_db_session
            )
        
        # Verify token was created with extended expiration
        import jwt
        decoded = jwt.decode(
            token_result["access_token"],
            settings.JWT_SECRET_KEY,
            algorithms=["HS256"]
        )
        
        exp_time = datetime.fromtimestamp(decoded["exp"])
        now = datetime.utcnow()
        time_diff = exp_time - now
        
        # Should be close to 1 year (allowing for processing time)
        assert time_diff.days >= 364
        assert time_diff.days <= 366