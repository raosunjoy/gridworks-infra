"""
GridWorks Infra - Security Middleware
Rate limiting, IP filtering, and request validation for B2B APIs
"""

import time
import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Callable
from fastapi import Request, Response, HTTPException, status
from fastapi.security import HTTPBearer
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import redis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..database.models import EnterpriseClient, APIKey, AuditLog
from ..database.session import get_db
from ..config import settings
from ..utils.encryption import decrypt_request, encrypt_response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware for API requests
    Supports both user-based and IP-based rate limiting
    """
    
    def __init__(self, app, redis_client: redis.Redis):
        super().__init__(app)
        self.redis_client = redis_client
        self.default_limit = 100  # requests per minute
        self.window_size = 60  # seconds
    
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health checks
        if request.url.path.endswith("/health"):
            return await call_next(request)
        
        # Determine rate limit key
        client_id = request.state.client_id if hasattr(request.state, "client_id") else None
        api_key_id = request.state.api_key_id if hasattr(request.state, "api_key_id") else None
        
        if client_id:
            rate_key = f"rate_limit:client:{client_id}"
            limit = request.state.rate_limit if hasattr(request.state, "rate_limit") else self.default_limit
        elif api_key_id:
            rate_key = f"rate_limit:api_key:{api_key_id}"
            limit = request.state.rate_limit if hasattr(request.state, "rate_limit") else self.default_limit
        else:
            # IP-based rate limiting for unauthenticated requests
            client_ip = request.client.host
            rate_key = f"rate_limit:ip:{client_ip}"
            limit = 20  # Lower limit for unauthenticated requests
        
        # Check rate limit
        current_count = self.redis_client.incr(rate_key)
        if current_count == 1:
            self.redis_client.expire(rate_key, self.window_size)
        
        if current_count > limit:
            # Calculate retry after
            ttl = self.redis_client.ttl(rate_key)
            retry_after = max(ttl, 1)
            
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Rate limit exceeded",
                    "retry_after": retry_after,
                    "limit": limit,
                    "window": self.window_size
                },
                headers={
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(time.time()) + retry_after),
                    "Retry-After": str(retry_after)
                }
            )
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        remaining = max(0, limit - current_count)
        reset_time = int(time.time()) + self.redis_client.ttl(rate_key)
        
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(reset_time)
        
        return response


class IPFilterMiddleware(BaseHTTPMiddleware):
    """
    IP filtering middleware for enterprise clients
    Supports allowlists at client and API key levels
    """
    
    async def dispatch(self, request: Request, call_next):
        # Skip IP filtering for public endpoints
        public_paths = ["/api/v1/partners/register", "/api/v1/partners/health"]
        if any(request.url.path.startswith(path) for path in public_paths):
            return await call_next(request)
        
        # Get client IP
        client_ip = request.client.host
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        
        # Check if request has authentication context
        if hasattr(request.state, "allowed_ips") and request.state.allowed_ips:
            allowed_ips = request.state.allowed_ips
            
            # Check if IP is allowed
            if not self._is_ip_allowed(client_ip, allowed_ips):
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={
                        "error": "Access denied",
                        "message": "Your IP address is not authorized"
                    }
                )
        
        # Store client IP for audit logging
        request.state.client_ip = client_ip
        
        return await call_next(request)
    
    def _is_ip_allowed(self, client_ip: str, allowed_ips: List[str]) -> bool:
        """Check if IP is in allowlist (supports CIDR notation)"""
        import ipaddress
        
        try:
            client_addr = ipaddress.ip_address(client_ip)
        except ValueError:
            return False
        
        for allowed in allowed_ips:
            try:
                # Check if it's a single IP
                if "/" not in allowed:
                    if client_addr == ipaddress.ip_address(allowed):
                        return True
                else:
                    # Check if it's a CIDR range
                    if client_addr in ipaddress.ip_network(allowed, strict=False):
                        return True
            except ValueError:
                continue
        
        return False


class RequestValidationMiddleware(BaseHTTPMiddleware):
    """
    Request validation and security checks
    Includes request signing, replay attack prevention, and input validation
    """
    
    def __init__(self, app, redis_client: redis.Redis):
        super().__init__(app)
        self.redis_client = redis_client
        self.max_request_size = 10 * 1024 * 1024  # 10MB
        self.request_timeout = 300  # 5 minutes
    
    async def dispatch(self, request: Request, call_next):
        # Check request size
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.max_request_size:
            return JSONResponse(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                content={"error": "Request entity too large"}
            )
        
        # Validate request signature if present
        signature = request.headers.get("X-GridWorks-Signature")
        if signature and hasattr(request.state, "client_secret"):
            # Read request body
            body = await request.body()
            
            # Verify signature
            expected_signature = self._calculate_signature(
                request.method,
                str(request.url),
                body,
                request.state.client_secret
            )
            
            if not hmac.compare_digest(signature, expected_signature):
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"error": "Invalid request signature"}
                )
            
            # Check for replay attacks
            request_id = request.headers.get("X-Request-ID")
            if request_id:
                if not await self._check_request_freshness(request_id):
                    return JSONResponse(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        content={"error": "Duplicate or expired request"}
                    )
        
        # Add security headers to response
        response = await call_next(request)
        
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response
    
    def _calculate_signature(
        self,
        method: str,
        url: str,
        body: bytes,
        secret: str
    ) -> str:
        """Calculate HMAC signature for request"""
        message = f"{method}\n{url}\n{body.decode('utf-8')}"
        signature = hmac.new(
            secret.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    async def _check_request_freshness(self, request_id: str) -> bool:
        """Check if request is fresh (not a replay)"""
        key = f"request_id:{request_id}"
        
        # Try to set the key with NX (only if not exists)
        result = self.redis_client.set(
            key,
            "1",
            ex=self.request_timeout,
            nx=True
        )
        
        return bool(result)


class AuditLoggingMiddleware(BaseHTTPMiddleware):
    """
    Comprehensive audit logging for all API requests
    Logs request details, response status, and performance metrics
    """
    
    def __init__(self, app, get_db_func: Callable):
        super().__init__(app)
        self.get_db = get_db_func
    
    async def dispatch(self, request: Request, call_next):
        # Skip logging for health checks
        if request.url.path.endswith("/health"):
            return await call_next(request)
        
        # Capture request details
        start_time = time.time()
        request_body = None
        
        # Try to read request body for logging (if JSON)
        if request.headers.get("content-type") == "application/json":
            try:
                body_bytes = await request.body()
                request_body = body_bytes.decode("utf-8")
                # Recreate request with body
                async def receive():
                    return {"type": "http.request", "body": body_bytes}
                request._receive = receive
            except:
                pass
        
        # Process request
        response = await call_next(request)
        
        # Calculate response time
        response_time = (time.time() - start_time) * 1000  # ms
        
        # Log audit entry
        await self._log_request(
            request,
            response,
            request_body,
            response_time
        )
        
        return response
    
    async def _log_request(
        self,
        request: Request,
        response: Response,
        request_body: Optional[str],
        response_time: float
    ):
        """Log request to audit table"""
        try:
            async for db in self.get_db():
                audit_log = AuditLog(
                    client_id=getattr(request.state, "client_id", None),
                    user_id=getattr(request.state, "user_id", None),
                    event_type="api_request",
                    resource_type="api",
                    resource_id=request.url.path,
                    action=request.method,
                    ip_address=getattr(request.state, "client_ip", request.client.host),
                    user_agent=request.headers.get("user-agent"),
                    api_key_id=getattr(request.state, "api_key_id", None),
                    request_data={
                        "method": request.method,
                        "path": request.url.path,
                        "query": dict(request.query_params),
                        "headers": dict(request.headers),
                        "body": request_body
                    },
                    response_data={
                        "status_code": response.status_code,
                        "response_time_ms": response_time
                    },
                    status="success" if response.status_code < 400 else "failure",
                    timestamp=datetime.utcnow()
                )
                
                db.add(audit_log)
                await db.commit()
        except Exception as e:
            # Log error but don't fail the request
            print(f"Audit logging error: {e}")


class EncryptionMiddleware(BaseHTTPMiddleware):
    """
    End-to-end encryption for sensitive data
    Encrypts responses and decrypts requests for configured endpoints
    """
    
    def __init__(self, app, encryption_endpoints: List[str]):
        super().__init__(app)
        self.encryption_endpoints = encryption_endpoints
    
    async def dispatch(self, request: Request, call_next):
        # Check if endpoint requires encryption
        requires_encryption = any(
            request.url.path.startswith(endpoint)
            for endpoint in self.encryption_endpoints
        )
        
        if requires_encryption and hasattr(request.state, "encryption_key"):
            # Decrypt request body if present
            if request.method in ["POST", "PUT", "PATCH"]:
                encrypted_body = await request.body()
                if encrypted_body:
                    try:
                        decrypted_body = decrypt_request(
                            encrypted_body,
                            request.state.encryption_key
                        )
                        # Replace request body
                        async def receive():
                            return {
                                "type": "http.request",
                                "body": decrypted_body
                            }
                        request._receive = receive
                    except Exception as e:
                        return JSONResponse(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            content={"error": "Failed to decrypt request"}
                        )
        
        # Process request
        response = await call_next(request)
        
        # Encrypt response if needed
        if requires_encryption and hasattr(request.state, "encryption_key"):
            if 200 <= response.status_code < 300:
                # Read response body
                body = b""
                async for chunk in response.body_iterator:
                    body += chunk
                
                # Encrypt response
                try:
                    encrypted_body = encrypt_response(
                        body,
                        request.state.encryption_key
                    )
                    
                    # Create new response with encrypted body
                    return Response(
                        content=encrypted_body,
                        status_code=response.status_code,
                        headers=dict(response.headers),
                        media_type="application/octet-stream"
                    )
                except Exception as e:
                    # Return original response if encryption fails
                    pass
        
        return response


class CORSMiddleware(BaseHTTPMiddleware):
    """
    CORS middleware for B2B API access
    Configurable per client with strict origin validation
    """
    
    def __init__(self, app, allowed_origins: List[str]):
        super().__init__(app)
        self.allowed_origins = allowed_origins
    
    async def dispatch(self, request: Request, call_next):
        origin = request.headers.get("origin")
        
        # Handle preflight requests
        if request.method == "OPTIONS":
            response = Response(status_code=200)
        else:
            response = await call_next(request)
        
        # Add CORS headers if origin is allowed
        if origin in self.allowed_origins or "*" in self.allowed_origins:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = (
                "Authorization, Content-Type, X-API-Key, X-Request-ID, "
                "X-GridWorks-Signature"
            )
            response.headers["Access-Control-Max-Age"] = "3600"
        
        return response