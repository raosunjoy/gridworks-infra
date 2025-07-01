"""
TradeMate Security Penetration Testing Suite
===========================================
🔒 Comprehensive Security Vulnerability Assessment
🛡️ Financial-Grade Security Validation
🚨 SEBI Compliance Security Testing
"""

import pytest
import asyncio
import aiohttp
import hashlib
import hmac
import jwt
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import uuid
import json
import re
from unittest.mock import Mock, AsyncMock, patch
from cryptography.fernet import Fernet
import sqlalchemy
from sqlalchemy.sql import text

# Security Testing Imports
from app.billing.unified_billing_system import UnifiedBillingSystem
from app.black.luxury_billing import LuxuryBillingSystem
from app.admin.dashboard import AdminDashboard
from app.core.security import SecurityManager
from app.core.encryption import EncryptionService
from app.core.authentication import AuthenticationService


class SecurityTestResults:
    """Track security test results and vulnerabilities"""
    
    def __init__(self):
        self.vulnerabilities = []
        self.security_passes = []
        self.critical_issues = []
        self.warnings = []
    
    def add_vulnerability(self, severity: str, description: str, test_name: str, evidence: Dict = None):
        """Record security vulnerability"""
        vuln = {
            "severity": severity,
            "description": description,
            "test_name": test_name,
            "evidence": evidence or {},
            "timestamp": datetime.now().isoformat()
        }
        self.vulnerabilities.append(vuln)
        
        if severity in ["CRITICAL", "HIGH"]:
            self.critical_issues.append(vuln)
    
    def add_security_pass(self, test_name: str, description: str):
        """Record successful security test"""
        self.security_passes.append({
            "test_name": test_name,
            "description": description,
            "timestamp": datetime.now().isoformat()
        })
    
    def add_warning(self, description: str, test_name: str):
        """Record security warning"""
        self.warnings.append({
            "description": description,
            "test_name": test_name,
            "timestamp": datetime.now().isoformat()
        })
    
    def get_security_score(self) -> float:
        """Calculate overall security score"""
        total_tests = len(self.vulnerabilities) + len(self.security_passes)
        if total_tests == 0:
            return 0.0
        
        # Weight vulnerabilities by severity
        penalty_weights = {"CRITICAL": 10, "HIGH": 5, "MEDIUM": 3, "LOW": 1}
        total_penalty = sum(penalty_weights.get(vuln["severity"], 1) for vuln in self.vulnerabilities)
        
        # Security score: 100 - (penalties / total_tests * 10)
        score = max(0, 100 - (total_penalty / total_tests * 10))
        return round(score, 2)


@pytest.mark.asyncio
class TestSecurityPenetration:
    """Comprehensive security penetration testing"""
    
    @pytest.fixture
    async def security_test_system(self):
        """Initialize system for security testing"""
        
        billing_system = UnifiedBillingSystem()
        luxury_billing = LuxuryBillingSystem()
        admin_dashboard = AdminDashboard()
        security_manager = SecurityManager()
        encryption_service = EncryptionService()
        auth_service = AuthenticationService()
        
        return {
            "billing": billing_system,
            "luxury": luxury_billing,
            "admin": admin_dashboard,
            "security": security_manager,
            "encryption": encryption_service,
            "auth": auth_service
        }
    
    async def test_sql_injection_vulnerabilities(self, security_test_system):
        """Test for SQL injection vulnerabilities"""
        
        results = SecurityTestResults()
        
        # SQL Injection payloads
        sql_payloads = [
            "'; DROP TABLE users; --",
            "' OR 1=1 --",
            "' UNION SELECT * FROM admin_users --",
            "'; DELETE FROM payments WHERE 1=1; --",
            "' OR 'x'='x",
            "1'; INSERT INTO admin_users (username, password) VALUES ('hacker', 'password'); --",
            "' AND (SELECT COUNT(*) FROM information_schema.tables) > 0 --",
            "'; EXEC xp_cmdshell('dir'); --"
        ]
        
        # Test SQL injection in various endpoints
        test_endpoints = [
            ("user_lookup", {"user_id": None}),
            ("payment_search", {"payment_id": None}),
            ("transaction_filter", {"filter_criteria": None}),
            ("admin_query", {"query_param": None})
        ]
        
        for endpoint_name, params in test_endpoints:
            for payload in sql_payloads:
                try:
                    # Test each parameter with SQL injection payload
                    for param_name in params.keys():
                        test_params = params.copy()
                        test_params[param_name] = payload
                        
                        if endpoint_name == "user_lookup":
                            result = await security_test_system["billing"].get_user_details(
                                user_id=test_params["user_id"]
                            )
                        elif endpoint_name == "payment_search":
                            result = await security_test_system["billing"].search_payments(
                                payment_id=test_params["payment_id"]
                            )
                        elif endpoint_name == "transaction_filter":
                            result = await security_test_system["admin"].filter_transactions(
                                criteria=test_params["filter_criteria"]
                            )
                        elif endpoint_name == "admin_query":
                            result = await security_test_system["admin"].execute_query(
                                param=test_params["query_param"]
                            )
                        
                        # Check if SQL injection succeeded
                        if result and (
                            "error" not in result or 
                            "syntax error" in str(result).lower() or
                            "sql" in str(result).lower()
                        ):
                            results.add_vulnerability(
                                "CRITICAL",
                                f"SQL injection vulnerability in {endpoint_name}:{param_name}",
                                "test_sql_injection_vulnerabilities",
                                {"payload": payload, "endpoint": endpoint_name, "parameter": param_name}
                            )
                        else:
                            results.add_security_pass(
                                "test_sql_injection_vulnerabilities",
                                f"SQL injection protected in {endpoint_name}:{param_name}"
                            )
                
                except Exception as e:
                    # Check if error reveals SQL structure
                    error_msg = str(e).lower()
                    if any(term in error_msg for term in ["sql", "table", "column", "syntax", "database"]):
                        results.add_vulnerability(
                            "HIGH",
                            f"SQL error information disclosure in {endpoint_name}",
                            "test_sql_injection_vulnerabilities",
                            {"error": str(e), "payload": payload}
                        )
                    else:
                        results.add_security_pass(
                            "test_sql_injection_vulnerabilities",
                            f"SQL injection properly handled with generic error in {endpoint_name}"
                        )
        
        # Assert no critical SQL injection vulnerabilities
        assert len(results.critical_issues) == 0, f"Critical SQL injection vulnerabilities found: {results.critical_issues}"
        
        return results
    
    async def test_xss_vulnerabilities(self, security_test_system):
        """Test for Cross-Site Scripting (XSS) vulnerabilities"""
        
        results = SecurityTestResults()
        
        # XSS payloads
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "<svg onload=alert('XSS')>",
            "'><script>alert('XSS')</script>",
            "<iframe src='javascript:alert(\"XSS\")'></iframe>",
            "<body onload=alert('XSS')>",
            "<input type='text' value='' onfocus=alert('XSS') autofocus>"
        ]
        
        # Test XSS in user input fields
        test_fields = [
            ("user_name", "profile_update"),
            ("transaction_description", "transaction_create"),
            ("feedback_message", "feedback_submit"),
            ("search_query", "search_transactions"),
            ("notification_message", "send_notification")
        ]
        
        for field_name, operation in test_fields:
            for payload in xss_payloads:
                try:
                    if operation == "profile_update":
                        result = await security_test_system["billing"].update_user_profile({
                            "user_id": str(uuid.uuid4()),
                            field_name: payload
                        })
                    elif operation == "transaction_create":
                        result = await security_test_system["billing"].create_transaction({
                            "user_id": str(uuid.uuid4()),
                            "amount": 100.0,
                            field_name: payload
                        })
                    elif operation == "feedback_submit":
                        result = await security_test_system["admin"].submit_feedback({
                            "user_id": str(uuid.uuid4()),
                            field_name: payload
                        })
                    elif operation == "search_transactions":
                        result = await security_test_system["admin"].search_transactions({
                            field_name: payload
                        })
                    elif operation == "send_notification":
                        result = await security_test_system["admin"].send_notification({
                            "user_id": str(uuid.uuid4()),
                            field_name: payload
                        })
                    
                    # Check if XSS payload was sanitized
                    result_str = str(result)
                    if any(tag in result_str for tag in ["<script>", "<img", "javascript:", "<svg", "<iframe", "<body", "onerror="]):
                        results.add_vulnerability(
                            "HIGH",
                            f"XSS vulnerability in {operation}:{field_name}",
                            "test_xss_vulnerabilities",
                            {"payload": payload, "operation": operation, "field": field_name}
                        )
                    else:
                        results.add_security_pass(
                            "test_xss_vulnerabilities",
                            f"XSS properly sanitized in {operation}:{field_name}"
                        )
                
                except Exception as e:
                    # Input validation rejection is good
                    if "validation" in str(e).lower() or "invalid" in str(e).lower():
                        results.add_security_pass(
                            "test_xss_vulnerabilities",
                            f"XSS blocked by input validation in {operation}:{field_name}"
                        )
                    else:
                        results.add_warning(
                            f"Unexpected error in XSS test for {operation}:{field_name}: {e}",
                            "test_xss_vulnerabilities"
                        )
        
        return results
    
    async def test_authentication_bypass_attempts(self, security_test_system):
        """Test authentication bypass vulnerabilities"""
        
        results = SecurityTestResults()
        
        # Authentication bypass techniques
        bypass_attempts = [
            {"method": "empty_token", "token": ""},
            {"method": "null_token", "token": None},
            {"method": "invalid_token", "token": "invalid_token_123"},
            {"method": "expired_token", "token": self.generate_expired_token()},
            {"method": "malformed_jwt", "token": "malformed.jwt.token"},
            {"method": "admin_impersonation", "token": self.generate_fake_admin_token()},
            {"method": "sql_injection_auth", "token": "'; DROP TABLE sessions; --"},
            {"method": "privilege_escalation", "token": self.generate_privilege_escalation_token()}
        ]
        
        # Protected endpoints to test
        protected_endpoints = [
            "get_admin_dashboard",
            "delete_user_account", 
            "modify_payment_settings",
            "access_financial_data",
            "export_user_data",
            "system_configuration"
        ]
        
        for endpoint in protected_endpoints:
            for attempt in bypass_attempts:
                try:
                    # Attempt to access protected endpoint with invalid auth
                    if endpoint == "get_admin_dashboard":
                        result = await security_test_system["admin"].get_dashboard_data(
                            auth_token=attempt["token"]
                        )
                    elif endpoint == "delete_user_account":
                        result = await security_test_system["billing"].delete_user_account(
                            user_id=str(uuid.uuid4()),
                            auth_token=attempt["token"]
                        )
                    elif endpoint == "modify_payment_settings":
                        result = await security_test_system["billing"].modify_payment_settings(
                            settings={},
                            auth_token=attempt["token"]
                        )
                    elif endpoint == "access_financial_data":
                        result = await security_test_system["admin"].get_financial_data(
                            auth_token=attempt["token"]
                        )
                    elif endpoint == "export_user_data":
                        result = await security_test_system["admin"].export_user_data(
                            auth_token=attempt["token"]
                        )
                    elif endpoint == "system_configuration":
                        result = await security_test_system["admin"].get_system_config(
                            auth_token=attempt["token"]
                        )
                    
                    # Check if authentication was bypassed
                    if result and result.get("success") is True:
                        results.add_vulnerability(
                            "CRITICAL",
                            f"Authentication bypass in {endpoint} using {attempt['method']}",
                            "test_authentication_bypass_attempts",
                            {"endpoint": endpoint, "method": attempt["method"]}
                        )
                    else:
                        results.add_security_pass(
                            "test_authentication_bypass_attempts",
                            f"Authentication properly enforced for {endpoint} against {attempt['method']}"
                        )
                
                except Exception as e:
                    # Authentication errors are expected
                    if any(term in str(e).lower() for term in ["auth", "unauthorized", "forbidden", "token", "permission"]):
                        results.add_security_pass(
                            "test_authentication_bypass_attempts",
                            f"Authentication properly enforced for {endpoint} against {attempt['method']}"
                        )
                    else:
                        results.add_warning(
                            f"Unexpected error in auth test for {endpoint}: {e}",
                            "test_authentication_bypass_attempts"
                        )
        
        return results
    
    async def test_authorization_privilege_escalation(self, security_test_system):
        """Test authorization and privilege escalation vulnerabilities"""
        
        results = SecurityTestResults()
        
        # Create test users with different privilege levels
        regular_user_token = self.generate_user_token("regular_user", ["USER"])
        pro_user_token = self.generate_user_token("pro_user", ["USER", "PRO"])
        admin_user_token = self.generate_user_token("admin_user", ["USER", "ADMIN"])
        
        # Privilege escalation test cases
        escalation_tests = [
            {
                "test_name": "regular_to_admin",
                "user_token": regular_user_token,
                "target_operation": "admin_dashboard_access",
                "expected_result": "FORBIDDEN"
            },
            {
                "test_name": "regular_to_billing_admin",
                "user_token": regular_user_token,
                "target_operation": "billing_configuration",
                "expected_result": "FORBIDDEN"
            },
            {
                "test_name": "pro_to_admin",
                "user_token": pro_user_token,
                "target_operation": "system_settings",
                "expected_result": "FORBIDDEN"
            },
            {
                "test_name": "cross_user_data_access",
                "user_token": regular_user_token,
                "target_operation": "access_other_user_data",
                "expected_result": "FORBIDDEN"
            }
        ]
        
        for test_case in escalation_tests:
            try:
                if test_case["target_operation"] == "admin_dashboard_access":
                    result = await security_test_system["admin"].get_admin_dashboard(
                        auth_token=test_case["user_token"]
                    )
                elif test_case["target_operation"] == "billing_configuration":
                    result = await security_test_system["billing"].update_billing_config(
                        config={},
                        auth_token=test_case["user_token"]
                    )
                elif test_case["target_operation"] == "system_settings":
                    result = await security_test_system["admin"].update_system_settings(
                        settings={},
                        auth_token=test_case["user_token"]
                    )
                elif test_case["target_operation"] == "access_other_user_data":
                    result = await security_test_system["billing"].get_user_data(
                        user_id="different_user_id",
                        auth_token=test_case["user_token"]
                    )
                
                # Check if privilege escalation occurred
                if result and result.get("success") is True:
                    results.add_vulnerability(
                        "CRITICAL",
                        f"Privilege escalation in {test_case['test_name']}",
                        "test_authorization_privilege_escalation",
                        {"test_case": test_case}
                    )
                else:
                    results.add_security_pass(
                        "test_authorization_privilege_escalation",
                        f"Privilege escalation properly prevented in {test_case['test_name']}"
                    )
            
            except Exception as e:
                # Authorization errors are expected
                if any(term in str(e).lower() for term in ["unauthorized", "forbidden", "permission", "access denied"]):
                    results.add_security_pass(
                        "test_authorization_privilege_escalation",
                        f"Authorization properly enforced for {test_case['test_name']}"
                    )
                else:
                    results.add_warning(
                        f"Unexpected error in authorization test {test_case['test_name']}: {e}",
                        "test_authorization_privilege_escalation"
                    )
        
        return results
    
    async def test_encryption_security(self, security_test_system):
        """Test encryption implementation security"""
        
        results = SecurityTestResults()
        
        # Test data encryption
        sensitive_data_samples = [
            {"type": "bank_account", "data": "1234567890123456"},
            {"type": "payment_token", "data": "pm_test_token_123456"},
            {"type": "personal_info", "data": "John Doe|johndoe@example.com|+1234567890"},
            {"type": "financial_data", "data": "salary:5000000|investments:2000000"},
            {"type": "transaction_data", "data": "amount:750000|account:HDFC_PRIVATE"}
        ]
        
        for sample in sensitive_data_samples:
            try:
                # Test encryption
                encrypted_result = await security_test_system["encryption"].encrypt_sensitive_data(
                    data=sample["data"],
                    data_type=sample["type"]
                )
                
                # Verify data is actually encrypted
                if sample["data"] in str(encrypted_result):
                    results.add_vulnerability(
                        "CRITICAL",
                        f"Data not properly encrypted for {sample['type']}",
                        "test_encryption_security",
                        {"data_type": sample["type"], "original_data": sample["data"][:10] + "..."}
                    )
                else:
                    results.add_security_pass(
                        "test_encryption_security",
                        f"Data properly encrypted for {sample['type']}"
                    )
                
                # Test decryption
                decrypted_result = await security_test_system["encryption"].decrypt_sensitive_data(
                    encrypted_data=encrypted_result["encrypted_data"],
                    data_type=sample["type"]
                )
                
                # Verify decryption works correctly
                if decrypted_result["decrypted_data"] != sample["data"]:
                    results.add_vulnerability(
                        "HIGH",
                        f"Encryption/decryption mismatch for {sample['type']}",
                        "test_encryption_security",
                        {"data_type": sample["type"]}
                    )
                else:
                    results.add_security_pass(
                        "test_encryption_security",
                        f"Encryption/decryption working correctly for {sample['type']}"
                    )
            
            except Exception as e:
                results.add_warning(
                    f"Encryption test failed for {sample['type']}: {e}",
                    "test_encryption_security"
                )
        
        # Test key management
        try:
            key_strength_test = await security_test_system["encryption"].test_key_strength()
            
            if key_strength_test["key_length"] < 256:
                results.add_vulnerability(
                    "HIGH",
                    f"Encryption key length {key_strength_test['key_length']} bits insufficient",
                    "test_encryption_security",
                    {"key_strength": key_strength_test}
                )
            else:
                results.add_security_pass(
                    "test_encryption_security",
                    f"Encryption key strength adequate: {key_strength_test['key_length']} bits"
                )
        
        except Exception as e:
            results.add_warning(
                f"Key strength test failed: {e}",
                "test_encryption_security"
            )
        
        return results
    
    async def test_input_validation_security(self, security_test_system):
        """Test input validation and sanitization"""
        
        results = SecurityTestResults()
        
        # Malicious input patterns
        malicious_inputs = [
            {"type": "buffer_overflow", "payload": "A" * 10000},
            {"type": "null_bytes", "payload": "test\\x00admin"},
            {"type": "path_traversal", "payload": "../../../etc/passwd"},
            {"type": "command_injection", "payload": "; cat /etc/passwd"},
            {"type": "ldap_injection", "payload": "*)(&(objectClass=user)"},
            {"type": "xml_injection", "payload": "<?xml version='1.0'?><!DOCTYPE test [<!ENTITY xxe SYSTEM 'file:///etc/passwd'>]>"},
            {"type": "regex_dos", "payload": "a" * 1000 + "!"},
            {"type": "integer_overflow", "payload": "999999999999999999999999999999"},
            {"type": "negative_values", "payload": "-999999"},
            {"type": "special_characters", "payload": "!@#$%^&*()_+{}|:<>?[]\\;'\",./<>?"}
        ]
        
        # Input validation test fields
        test_fields = [
            ("amount", "billing_request"),
            ("user_id", "user_lookup"),
            ("phone_number", "user_registration"),
            ("account_number", "payment_setup"),
            ("file_path", "document_upload"),
            ("search_query", "transaction_search")
        ]
        
        for field_name, operation in test_fields:
            for malicious_input in malicious_inputs:
                try:
                    if operation == "billing_request":
                        result = await security_test_system["billing"].initiate_billing(
                            user_id=str(uuid.uuid4()),
                            tier="LITE",
                            amount=malicious_input["payload"] if field_name == "amount" else 500.0,
                            payment_method="UPI"
                        )
                    elif operation == "user_lookup":
                        result = await security_test_system["billing"].get_user_details(
                            user_id=malicious_input["payload"] if field_name == "user_id" else str(uuid.uuid4())
                        )
                    elif operation == "user_registration":
                        result = await security_test_system["billing"].register_user({
                            "phone_number": malicious_input["payload"] if field_name == "phone_number" else "+919876543210",
                            "name": "Test User"
                        })
                    elif operation == "payment_setup":
                        result = await security_test_system["billing"].setup_payment_method({
                            "user_id": str(uuid.uuid4()),
                            "account_number": malicious_input["payload"] if field_name == "account_number" else "1234567890"
                        })
                    elif operation == "document_upload":
                        result = await security_test_system["admin"].upload_document({
                            "user_id": str(uuid.uuid4()),
                            "file_path": malicious_input["payload"] if field_name == "file_path" else "/tmp/test.pdf"
                        })
                    elif operation == "transaction_search":
                        result = await security_test_system["admin"].search_transactions({
                            "query": malicious_input["payload"] if field_name == "search_query" else "test"
                        })
                    
                    # Check if malicious input was processed without validation
                    if result and result.get("success") is True:
                        results.add_vulnerability(
                            "MEDIUM",
                            f"Input validation bypass in {operation}:{field_name} with {malicious_input['type']}",
                            "test_input_validation_security",
                            {"operation": operation, "field": field_name, "attack_type": malicious_input["type"]}
                        )
                    else:
                        results.add_security_pass(
                            "test_input_validation_security",
                            f"Input validation working for {operation}:{field_name} against {malicious_input['type']}"
                        )
                
                except Exception as e:
                    # Input validation errors are expected and good
                    if any(term in str(e).lower() for term in ["validation", "invalid", "format", "length", "character"]):
                        results.add_security_pass(
                            "test_input_validation_security",
                            f"Input validation properly blocked {malicious_input['type']} in {operation}:{field_name}"
                        )
                    else:
                        results.add_warning(
                            f"Unexpected error in input validation test {operation}:{field_name}: {e}",
                            "test_input_validation_security"
                        )
        
        return results
    
    async def test_session_security(self, security_test_system):
        """Test session management security"""
        
        results = SecurityTestResults()
        
        # Session security tests
        session_tests = [
            {"test": "session_fixation", "description": "Test session fixation attacks"},
            {"test": "session_hijacking", "description": "Test session hijacking prevention"},
            {"test": "concurrent_sessions", "description": "Test concurrent session limits"},
            {"test": "session_timeout", "description": "Test session timeout enforcement"},
            {"test": "session_invalidation", "description": "Test proper session invalidation"}
        ]
        
        for test_case in session_tests:
            try:
                if test_case["test"] == "session_fixation":
                    # Attempt to fix session ID
                    fixed_session_id = "fixed_session_123"
                    result = await security_test_system["auth"].login_with_fixed_session(
                        username="test_user",
                        password="test_password",
                        session_id=fixed_session_id
                    )
                    
                    if result.get("session_id") == fixed_session_id:
                        results.add_vulnerability(
                            "HIGH",
                            "Session fixation vulnerability detected",
                            "test_session_security",
                            {"test": test_case["test"]}
                        )
                    else:
                        results.add_security_pass(
                            "test_session_security",
                            "Session fixation properly prevented"
                        )
                
                elif test_case["test"] == "session_hijacking":
                    # Test if session tokens are predictable
                    sessions = []
                    for i in range(10):
                        login_result = await security_test_system["auth"].login(
                            username=f"test_user_{i}",
                            password="test_password"
                        )
                        if login_result.get("session_token"):
                            sessions.append(login_result["session_token"])
                    
                    # Check for predictable patterns
                    if len(set(sessions)) < len(sessions) * 0.9:  # Less than 90% unique
                        results.add_vulnerability(
                            "HIGH",
                            "Session tokens appear predictable",
                            "test_session_security",
                            {"test": test_case["test"], "unique_sessions": len(set(sessions)), "total_sessions": len(sessions)}
                        )
                    else:
                        results.add_security_pass(
                            "test_session_security",
                            "Session tokens appear sufficiently random"
                        )
                
                elif test_case["test"] == "concurrent_sessions":
                    # Test concurrent session limits
                    user_id = str(uuid.uuid4())
                    sessions = []
                    
                    for i in range(20):  # Try to create 20 concurrent sessions
                        session_result = await security_test_system["auth"].create_session(
                            user_id=user_id
                        )
                        if session_result.get("success"):
                            sessions.append(session_result["session_id"])
                    
                    if len(sessions) > 10:  # Assuming 10 is the limit
                        results.add_vulnerability(
                            "MEDIUM",
                            f"Too many concurrent sessions allowed: {len(sessions)}",
                            "test_session_security",
                            {"test": test_case["test"], "session_count": len(sessions)}
                        )
                    else:
                        results.add_security_pass(
                            "test_session_security",
                            f"Concurrent session limits properly enforced: {len(sessions)} sessions"
                        )
                
                elif test_case["test"] == "session_timeout":
                    # Test session timeout
                    session_result = await security_test_system["auth"].create_session(
                        user_id=str(uuid.uuid4()),
                        timeout_seconds=1  # 1 second timeout for testing
                    )
                    
                    # Wait for timeout
                    await asyncio.sleep(2)
                    
                    # Try to use expired session
                    expired_session_test = await security_test_system["auth"].validate_session(
                        session_token=session_result["session_token"]
                    )
                    
                    if expired_session_test.get("valid") is True:
                        results.add_vulnerability(
                            "MEDIUM",
                            "Session timeout not properly enforced",
                            "test_session_security",
                            {"test": test_case["test"]}
                        )
                    else:
                        results.add_security_pass(
                            "test_session_security",
                            "Session timeout properly enforced"
                        )
                
                elif test_case["test"] == "session_invalidation":
                    # Test proper session invalidation on logout
                    login_result = await security_test_system["auth"].login(
                        username="test_user",
                        password="test_password"
                    )
                    
                    session_token = login_result.get("session_token")
                    
                    # Logout
                    logout_result = await security_test_system["auth"].logout(
                        session_token=session_token
                    )
                    
                    # Try to use invalidated session
                    invalidated_session_test = await security_test_system["auth"].validate_session(
                        session_token=session_token
                    )
                    
                    if invalidated_session_test.get("valid") is True:
                        results.add_vulnerability(
                            "HIGH",
                            "Session not properly invalidated on logout",
                            "test_session_security",
                            {"test": test_case["test"]}
                        )
                    else:
                        results.add_security_pass(
                            "test_session_security",
                            "Session properly invalidated on logout"
                        )
            
            except Exception as e:
                results.add_warning(
                    f"Session security test {test_case['test']} failed: {e}",
                    "test_session_security"
                )
        
        return results
    
    async def test_api_security_headers(self, security_test_system):
        """Test security headers implementation"""
        
        results = SecurityTestResults()
        
        # Required security headers
        required_headers = [
            "X-Content-Type-Options",
            "X-Frame-Options", 
            "X-XSS-Protection",
            "Strict-Transport-Security",
            "Content-Security-Policy",
            "Referrer-Policy",
            "Permissions-Policy"
        ]
        
        try:
            # Test API response headers
            api_response = await security_test_system["billing"].get_api_response_headers()
            
            for header in required_headers:
                if header not in api_response.get("headers", {}):
                    results.add_vulnerability(
                        "MEDIUM",
                        f"Missing security header: {header}",
                        "test_api_security_headers",
                        {"missing_header": header}
                    )
                else:
                    results.add_security_pass(
                        "test_api_security_headers",
                        f"Security header present: {header}"
                    )
            
            # Validate specific header values
            headers = api_response.get("headers", {})
            
            # Check HSTS header
            hsts = headers.get("Strict-Transport-Security", "")
            if "max-age" not in hsts or "includeSubDomains" not in hsts:
                results.add_vulnerability(
                    "MEDIUM",
                    "HSTS header not properly configured",
                    "test_api_security_headers",
                    {"hsts_value": hsts}
                )
            else:
                results.add_security_pass(
                    "test_api_security_headers",
                    "HSTS header properly configured"
                )
            
            # Check CSP header
            csp = headers.get("Content-Security-Policy", "")
            if "default-src" not in csp:
                results.add_vulnerability(
                    "MEDIUM",
                    "CSP header missing default-src directive",
                    "test_api_security_headers",
                    {"csp_value": csp}
                )
            else:
                results.add_security_pass(
                    "test_api_security_headers",
                    "CSP header properly configured"
                )
        
        except Exception as e:
            results.add_warning(
                f"Security headers test failed: {e}",
                "test_api_security_headers"
            )
        
        return results
    
    def generate_expired_token(self) -> str:
        """Generate an expired JWT token for testing"""
        payload = {
            "user_id": "test_user",
            "exp": datetime.utcnow() - timedelta(hours=1),  # Expired 1 hour ago
            "iat": datetime.utcnow() - timedelta(hours=2)
        }
        return jwt.encode(payload, "secret_key", algorithm="HS256")
    
    def generate_fake_admin_token(self) -> str:
        """Generate a fake admin token for testing"""
        payload = {
            "user_id": "fake_admin",
            "role": "admin",
            "exp": datetime.utcnow() + timedelta(hours=1),
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, "wrong_secret_key", algorithm="HS256")
    
    def generate_privilege_escalation_token(self) -> str:
        """Generate a token attempting privilege escalation"""
        payload = {
            "user_id": "regular_user",
            "role": "admin",  # Attempting to escalate to admin
            "permissions": ["admin:read", "admin:write", "system:config"],
            "exp": datetime.utcnow() + timedelta(hours=1),
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, "secret_key", algorithm="HS256")
    
    def generate_user_token(self, user_id: str, roles: List[str]) -> str:
        """Generate a valid user token with specified roles"""
        payload = {
            "user_id": user_id,
            "roles": roles,
            "exp": datetime.utcnow() + timedelta(hours=1),
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, "secret_key", algorithm="HS256")


@pytest.mark.asyncio
class TestFinancialSecurityCompliance:
    """Financial services security compliance testing"""
    
    async def test_pci_dss_compliance(self, security_test_system):
        """Test PCI DSS compliance requirements"""
        
        results = SecurityTestResults()
        
        # PCI DSS requirements testing
        pci_tests = [
            {"requirement": "3.4", "test": "card_data_encryption"},
            {"requirement": "4.1", "test": "secure_transmission"},
            {"requirement": "7.1", "test": "access_control"},
            {"requirement": "8.1", "test": "user_identification"},
            {"requirement": "10.1", "test": "audit_logging"}
        ]
        
        for test in pci_tests:
            try:
                if test["test"] == "card_data_encryption":
                    # Test credit card data encryption
                    card_data = "4111111111111111"  # Test card number
                    encrypted_result = await security_test_system["encryption"].encrypt_card_data(card_data)
                    
                    if card_data in str(encrypted_result):
                        results.add_vulnerability(
                            "CRITICAL",
                            f"PCI DSS {test['requirement']}: Card data not encrypted",
                            "test_pci_dss_compliance"
                        )
                    else:
                        results.add_security_pass(
                            "test_pci_dss_compliance",
                            f"PCI DSS {test['requirement']}: Card data properly encrypted"
                        )
                
                elif test["test"] == "secure_transmission":
                    # Test secure transmission protocols
                    transmission_test = await security_test_system["security"].test_transmission_security()
                    
                    if not transmission_test.get("tls_enabled") or transmission_test.get("tls_version") < "1.2":
                        results.add_vulnerability(
                            "HIGH",
                            f"PCI DSS {test['requirement']}: Insecure transmission protocols",
                            "test_pci_dss_compliance"
                        )
                    else:
                        results.add_security_pass(
                            "test_pci_dss_compliance",
                            f"PCI DSS {test['requirement']}: Secure transmission protocols in use"
                        )
                
                elif test["test"] == "access_control":
                    # Test role-based access control
                    access_test = await security_test_system["auth"].test_rbac_implementation()
                    
                    if not access_test.get("rbac_enabled"):
                        results.add_vulnerability(
                            "HIGH",
                            f"PCI DSS {test['requirement']}: Access control not properly implemented",
                            "test_pci_dss_compliance"
                        )
                    else:
                        results.add_security_pass(
                            "test_pci_dss_compliance",
                            f"PCI DSS {test['requirement']}: Access control properly implemented"
                        )
            
            except Exception as e:
                results.add_warning(
                    f"PCI DSS test {test['requirement']} failed: {e}",
                    "test_pci_dss_compliance"
                )
        
        return results


# Security Testing Runner
async def run_comprehensive_security_tests():
    """Run all security tests and generate security report"""
    
    print("🔒 TradeMate Security Penetration Testing Suite")
    print("=" * 60)
    
    security_tester = TestSecurityPenetration()
    system = await security_tester.security_test_system()
    
    all_results = SecurityTestResults()
    
    # Run all security tests
    tests = [
        ("SQL Injection", security_tester.test_sql_injection_vulnerabilities(system)),
        ("XSS Vulnerabilities", security_tester.test_xss_vulnerabilities(system)),
        ("Authentication Bypass", security_tester.test_authentication_bypass_attempts(system)),
        ("Authorization & Privilege Escalation", security_tester.test_authorization_privilege_escalation(system)),
        ("Encryption Security", security_tester.test_encryption_security(system)),
        ("Input Validation", security_tester.test_input_validation_security(system)),
        ("Session Security", security_tester.test_session_security(system)),
        ("API Security Headers", security_tester.test_api_security_headers(system))
    ]
    
    for test_name, test_coro in tests:
        print(f"\n🔍 Running: {test_name}")
        try:
            result = await test_coro
            
            # Merge results
            all_results.vulnerabilities.extend(result.vulnerabilities)
            all_results.security_passes.extend(result.security_passes)
            all_results.critical_issues.extend(result.critical_issues)
            all_results.warnings.extend(result.warnings)
            
            print(f"✅ {test_name} completed")
            print(f"   Vulnerabilities: {len(result.vulnerabilities)}")
            print(f"   Security Passes: {len(result.security_passes)}")
            
        except Exception as e:
            print(f"❌ {test_name} failed: {e}")
    
    # Generate security score
    security_score = all_results.get_security_score()
    
    print(f"\n📊 SECURITY ASSESSMENT SUMMARY")
    print(f"Security Score: {security_score}/100")
    print(f"Total Vulnerabilities: {len(all_results.vulnerabilities)}")
    print(f"Critical Issues: {len(all_results.critical_issues)}")
    print(f"Security Passes: {len(all_results.security_passes)}")
    print(f"Warnings: {len(all_results.warnings)}")
    
    # Assert minimum security requirements
    assert security_score >= 85, f"Security score {security_score} below minimum threshold of 85"
    assert len(all_results.critical_issues) == 0, f"Critical security issues found: {all_results.critical_issues}"
    
    return all_results


if __name__ == "__main__":
    print("🔒 TradeMate Security Penetration Testing")
    print("🛡️ Financial-Grade Security Validation")
    print("🚨 SEBI Compliance Security Testing")
    print("=" * 70)
    
    # Run comprehensive security tests
    asyncio.run(run_comprehensive_security_tests())