"""
GridWorks Infra - Enterprise Authentication System
Multi-tenant authentication with JWT, API keys, and OAuth2 support
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader
from pydantic import BaseModel, Field
import jwt
import hashlib
import secrets
import redis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from ..database.models import (
    EnterpriseClient, APIKey, User, Role, Permission,
    ClientSubscription, AuditLog
)
from ..database.session import get_db
from ..config import settings
from ..utils.encryption import encrypt_data, decrypt_data


class TokenData(BaseModel):
    """JWT Token payload structure"""
    client_id: str
    user_id: str
    email: str
    roles: List[str]
    permissions: List[str]
    tier: str
    exp: datetime


class APIKeyData(BaseModel):
    """API Key metadata"""
    key_id: str
    client_id: str
    name: str
    permissions: List[str]
    rate_limit: int
    expires_at: Optional[datetime]


class EnterpriseAuth:
    """
    Enterprise authentication handler for B2B clients
    Supports JWT tokens, API keys, and OAuth2
    """
    
    def __init__(self):
        self.security = HTTPBearer()
        self.api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
        self.redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
        self.jwt_algorithm = "HS256"
        self.jwt_expiration = timedelta(hours=24)
        self.refresh_expiration = timedelta(days=30)
    
    async def create_access_token(
        self,
        client_id: str,
        user_id: str,
        email: str,
        roles: List[str],
        permissions: List[str],
        tier: str,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Create JWT access and refresh tokens"""
        
        # Create access token
        access_exp = datetime.utcnow() + self.jwt_expiration
        access_payload = {
            "client_id": client_id,
            "user_id": user_id,
            "email": email,
            "roles": roles,
            "permissions": permissions,
            "tier": tier,
            "exp": access_exp,
            "type": "access"
        }
        
        access_token = jwt.encode(
            access_payload,
            settings.JWT_SECRET_KEY,
            algorithm=self.jwt_algorithm
        )
        
        # Create refresh token
        refresh_exp = datetime.utcnow() + self.refresh_expiration
        refresh_payload = {
            "client_id": client_id,
            "user_id": user_id,
            "exp": refresh_exp,
            "type": "refresh"
        }
        
        refresh_token = jwt.encode(
            refresh_payload,
            settings.JWT_SECRET_KEY,
            algorithm=self.jwt_algorithm
        )
        
        # Store tokens in Redis for invalidation support
        await self._store_token_metadata(
            user_id, access_token, refresh_token, db
        )
        
        # Log authentication event
        await self._log_auth_event(
            client_id, user_id, "token_created", db
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": int(self.jwt_expiration.total_seconds()),
            "tier": tier,
            "permissions": permissions
        }
    
    async def verify_token(
        self,
        credentials: HTTPAuthorizationCredentials,
        db: AsyncSession
    ) -> TokenData:
        """Verify and decode JWT token"""
        
        token = credentials.credentials
        
        try:
            # Decode token
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[self.jwt_algorithm]
            )
            
            # Check token type
            if payload.get("type") != "access":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type"
                )
            
            # Check if token is blacklisted
            if await self._is_token_blacklisted(token):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has been invalidated"
                )
            
            # Verify client subscription is active
            client = await self._get_client(payload["client_id"], db)
            if not client or not client.is_active:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Client subscription is inactive"
                )
            
            return TokenData(**payload)
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    
    async def create_api_key(
        self,
        client_id: str,
        name: str,
        permissions: List[str],
        rate_limit: int,
        expires_in_days: Optional[int],
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Generate new API key for client"""
        
        # Generate secure API key
        key_prefix = "gw_"
        key_secret = secrets.token_urlsafe(32)
        api_key = f"{key_prefix}{key_secret}"
        
        # Hash key for storage
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        # Calculate expiration
        expires_at = None
        if expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
        
        # Store API key in database
        db_key = APIKey(
            client_id=client_id,
            key_hash=key_hash,
            key_prefix=api_key[:8],  # Store prefix for identification
            name=name,
            permissions=permissions,
            rate_limit=rate_limit,
            expires_at=expires_at,
            last_used_at=None,
            is_active=True
        )
        
        db.add(db_key)
        await db.commit()
        
        # Store key metadata in Redis for fast lookup
        await self._store_api_key_metadata(
            api_key, client_id, db_key.id, permissions, rate_limit
        )
        
        # Log API key creation
        await self._log_auth_event(
            client_id, None, "api_key_created", db,
            {"key_id": str(db_key.id), "name": name}
        )
        
        return {
            "api_key": api_key,
            "key_id": str(db_key.id),
            "name": name,
            "permissions": permissions,
            "rate_limit": rate_limit,
            "expires_at": expires_at,
            "note": "Store this key securely. It cannot be retrieved again."
        }
    
    async def verify_api_key(
        self,
        api_key: str,
        db: AsyncSession
    ) -> APIKeyData:
        """Verify API key and return metadata"""
        
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API key required"
            )
        
        # Check Redis cache first
        cached_data = await self._get_api_key_from_cache(api_key)
        if cached_data:
            return APIKeyData(**cached_data)
        
        # Hash the key
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        # Lookup in database
        result = await db.execute(
            select(APIKey).where(
                and_(
                    APIKey.key_hash == key_hash,
                    APIKey.is_active == True
                )
            )
        )
        db_key = result.scalar_one_or_none()
        
        if not db_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key"
            )
        
        # Check expiration
        if db_key.expires_at and db_key.expires_at < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API key has expired"
            )
        
        # Update last used timestamp
        db_key.last_used_at = datetime.utcnow()
        await db.commit()
        
        # Cache the key data
        key_data = APIKeyData(
            key_id=str(db_key.id),
            client_id=db_key.client_id,
            name=db_key.name,
            permissions=db_key.permissions,
            rate_limit=db_key.rate_limit,
            expires_at=db_key.expires_at
        )
        
        await self._store_api_key_metadata(
            api_key,
            db_key.client_id,
            str(db_key.id),
            db_key.permissions,
            db_key.rate_limit
        )
        
        return key_data
    
    async def check_permissions(
        self,
        required_permissions: List[str],
        user_permissions: List[str]
    ) -> bool:
        """Check if user has required permissions"""
        
        # Check for admin override
        if "admin.*" in user_permissions:
            return True
        
        # Check each required permission
        for required in required_permissions:
            # Direct match
            if required in user_permissions:
                continue
            
            # Wildcard match (e.g., "trading.*" matches "trading.execute")
            namespace = required.split('.')[0]
            if f"{namespace}.*" in user_permissions:
                continue
            
            return False
        
        return True
    
    async def _store_token_metadata(
        self,
        user_id: str,
        access_token: str,
        refresh_token: str,
        db: AsyncSession
    ):
        """Store token metadata in Redis"""
        
        # Store tokens with expiration
        access_key = f"token:access:{user_id}"
        refresh_key = f"token:refresh:{user_id}"
        
        self.redis_client.setex(
            access_key,
            int(self.jwt_expiration.total_seconds()),
            access_token
        )
        
        self.redis_client.setex(
            refresh_key,
            int(self.refresh_expiration.total_seconds()),
            refresh_token
        )
    
    async def _store_api_key_metadata(
        self,
        api_key: str,
        client_id: str,
        key_id: str,
        permissions: List[str],
        rate_limit: int
    ):
        """Cache API key metadata in Redis"""
        
        cache_key = f"apikey:{api_key}"
        cache_data = {
            "key_id": key_id,
            "client_id": client_id,
            "permissions": permissions,
            "rate_limit": rate_limit
        }
        
        # Cache for 1 hour
        self.redis_client.hset(
            cache_key,
            mapping={k: str(v) for k, v in cache_data.items()}
        )
        self.redis_client.expire(cache_key, 3600)
    
    async def _get_api_key_from_cache(self, api_key: str) -> Optional[Dict]:
        """Get API key data from Redis cache"""
        
        cache_key = f"apikey:{api_key}"
        data = self.redis_client.hgetall(cache_key)
        
        if data:
            # Parse permissions list
            data["permissions"] = eval(data.get("permissions", "[]"))
            data["rate_limit"] = int(data.get("rate_limit", 1000))
            return data
        
        return None
    
    async def _is_token_blacklisted(self, token: str) -> bool:
        """Check if token is in blacklist"""
        
        blacklist_key = f"blacklist:{token}"
        return bool(self.redis_client.exists(blacklist_key))
    
    async def _get_client(
        self,
        client_id: str,
        db: AsyncSession
    ) -> Optional[EnterpriseClient]:
        """Get client with active subscription"""
        
        result = await db.execute(
            select(EnterpriseClient).where(
                EnterpriseClient.id == client_id
            )
        )
        return result.scalar_one_or_none()
    
    async def _log_auth_event(
        self,
        client_id: str,
        user_id: Optional[str],
        event_type: str,
        db: AsyncSession,
        metadata: Optional[Dict] = None
    ):
        """Log authentication events for audit"""
        
        log_entry = AuditLog(
            client_id=client_id,
            user_id=user_id,
            event_type=f"auth.{event_type}",
            metadata=metadata or {},
            ip_address=None,  # To be set by request handler
            user_agent=None,  # To be set by request handler
            timestamp=datetime.utcnow()
        )
        
        db.add(log_entry)
        await db.commit()


# Dependency injection functions
auth_handler = EnterpriseAuth()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(auth_handler.security),
    db: AsyncSession = Depends(get_db)
) -> TokenData:
    """Get current authenticated user from JWT"""
    return await auth_handler.verify_token(credentials, db)


async def get_api_key_data(
    api_key: str = Depends(auth_handler.api_key_header),
    db: AsyncSession = Depends(get_db)
) -> APIKeyData:
    """Get API key data from header"""
    return await auth_handler.verify_api_key(api_key, db)


class PermissionChecker:
    """Permission checking dependency"""
    
    def __init__(self, required_permissions: List[str]):
        self.required_permissions = required_permissions
    
    async def __call__(
        self,
        user: TokenData = Depends(get_current_user)
    ) -> TokenData:
        """Check if user has required permissions"""
        
        if not await auth_handler.check_permissions(
            self.required_permissions,
            user.permissions
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        
        return user