#!/usr/bin/env python3
"""
TradeMate Penetration Testing Automation
Comprehensive security testing for tier-specific endpoints
"""

import asyncio
import aiohttp
import json
import logging
import time
import subprocess
from datetime import datetime
from typing import Dict, List, Any
import ssl
import socket
from urllib.parse import urljoin

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TradeMateSecurityTester:
    """Automated penetration testing for TradeMate infrastructure"""
    
    def __init__(self):
        self.test_results = {
            'timestamp': datetime.utcnow().isoformat(),
            'test_framework_version': '2.0.0',
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'critical_vulnerabilities': [],
            'high_vulnerabilities': [],
            'medium_vulnerabilities': [],
            'low_vulnerabilities': [],
            'tier_results': {
                'shared': {'score': 0, 'tests': []},
                'premium': {'score': 0, 'tests': []}
            },
            'recommendations': []
        }
        
        self.endpoints = {
            'shared': {
                'base_url': 'https://api.trademate.ai',
                'health': '/health',
                'auth': '/api/v1/auth/login',
                'trading': '/api/v1/trades',
                'portfolio': '/api/v1/portfolio',
                'whatsapp': '/api/v1/whatsapp/webhook'
            },
            'premium': {
                'base_url': 'https://premium.trademate.ai',
                'health': '/health',
                'auth': '/api/v1/auth/login',
                'institutional': '/api/v1/institutional',
                'algo_trading': '/api/v1/algo',
                'hni_portfolio': '/api/v1/hni/portfolio',
                'api_trading': '/api/v1/trading/api'
            }
        }
        
        # Security test payloads
        self.sql_injection_payloads = [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "' UNION SELECT * FROM information_schema.tables --",
            "'; EXEC xp_cmdshell('dir'); --"
        ]
        
        self.xss_payloads = [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>",
            "<svg onload=alert('XSS')>"
        ]
        
        self.command_injection_payloads = [
            "; ls -la",
            "| whoami",
            "& cat /etc/passwd",
            "`id`"
        ]
    
    async def test_ssl_tls_configuration(self, tier: str) -> Dict[str, Any]:
        """Test SSL/TLS configuration"""
        try:
            base_url = self.endpoints[tier]['base_url']
            hostname = base_url.replace('https://', '').replace('http://', '')
            
            # Test SSL certificate
            context = ssl.create_default_context()
            
            with socket.create_connection((hostname, 443), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    
                    # Check certificate validity
                    not_after = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                    days_until_expiry = (not_after - datetime.utcnow()).days
                    
                    # Check TLS version
                    tls_version = ssock.version()
                    
                    # Check cipher suite
                    cipher = ssock.cipher()
                    
                    vulnerabilities = []
                    
                    if days_until_expiry < 30:
                        vulnerabilities.append({
                            'severity': 'HIGH',
                            'issue': 'SSL certificate expires soon',
                            'details': f'Certificate expires in {days_until_expiry} days'
                        })
                    
                    if tls_version in ['TLSv1', 'TLSv1.1']:
                        vulnerabilities.append({
                            'severity': 'HIGH',
                            'issue': 'Weak TLS version',
                            'details': f'Using {tls_version}, should use TLSv1.2 or TLSv1.3'
                        })
                    
                    return {
                        'test': 'SSL/TLS Configuration',
                        'status': 'PASS' if len(vulnerabilities) == 0 else 'FAIL',
                        'details': {
                            'certificate_valid': True,
                            'days_until_expiry': days_until_expiry,
                            'tls_version': tls_version,
                            'cipher_suite': cipher[0] if cipher else None,
                            'vulnerabilities': vulnerabilities
                        }
                    }
                    
        except Exception as e:
            logger.error(f"SSL/TLS test failed for {tier}: {e}")
            return {
                'test': 'SSL/TLS Configuration',
                'status': 'ERROR',
                'details': {'error': str(e)}
            }
    
    async def test_sql_injection(self, session: aiohttp.ClientSession, tier: str) -> Dict[str, Any]:
        """Test for SQL injection vulnerabilities"""
        vulnerabilities = []
        base_url = self.endpoints[tier]['base_url']
        
        # Test endpoints that might be vulnerable to SQL injection
        test_endpoints = ['/api/v1/auth/login', '/api/v1/search', '/api/v1/portfolio']
        
        for endpoint in test_endpoints:
            for payload in self.sql_injection_payloads:
                try:
                    # Test GET parameters
                    url = urljoin(base_url, endpoint)
                    params = {'q': payload, 'search': payload}
                    
                    async with session.get(url, params=params, timeout=10) as response:
                        response_text = await response.text()
                        
                        # Check for SQL error messages
                        sql_errors = [
                            'SQL syntax error',
                            'mysql_fetch',
                            'ORA-',
                            'Microsoft OLE DB',
                            'PostgreSQL query failed'
                        ]
                        
                        for error in sql_errors:
                            if error.lower() in response_text.lower():
                                vulnerabilities.append({
                                    'severity': 'CRITICAL',
                                    'endpoint': endpoint,
                                    'payload': payload,
                                    'error_message': error,
                                    'details': 'SQL error message detected in response'
                                })
                    
                    # Test POST data
                    if endpoint == '/api/v1/auth/login':
                        data = {
                            'username': payload,
                            'password': payload
                        }
                        
                        async with session.post(url, json=data, timeout=10) as response:
                            response_text = await response.text()
                            
                            for error in sql_errors:
                                if error.lower() in response_text.lower():
                                    vulnerabilities.append({
                                        'severity': 'CRITICAL',
                                        'endpoint': endpoint,
                                        'payload': payload,
                                        'method': 'POST',
                                        'error_message': error
                                    })
                
                except Exception as e:
                    # Timeout or connection errors are expected
                    continue
        
        return {
            'test': 'SQL Injection',
            'status': 'PASS' if len(vulnerabilities) == 0 else 'FAIL',
            'vulnerabilities_found': len(vulnerabilities),
            'details': vulnerabilities
        }
    
    async def test_xss_vulnerabilities(self, session: aiohttp.ClientSession, tier: str) -> Dict[str, Any]:
        """Test for Cross-Site Scripting vulnerabilities"""
        vulnerabilities = []
        base_url = self.endpoints[tier]['base_url']
        
        # Test endpoints that might reflect user input
        test_endpoints = ['/api/v1/search', '/api/v1/profile', '/api/v1/feedback']
        
        for endpoint in test_endpoints:
            for payload in self.xss_payloads:
                try:
                    url = urljoin(base_url, endpoint)
                    params = {'q': payload, 'message': payload}
                    
                    async with session.get(url, params=params, timeout=10) as response:
                        response_text = await response.text()
                        
                        # Check if payload is reflected in response
                        if payload in response_text and 'text/html' in response.headers.get('content-type', ''):
                            vulnerabilities.append({
                                'severity': 'HIGH',
                                'endpoint': endpoint,
                                'payload': payload,
                                'details': 'XSS payload reflected in HTML response'
                            })
                
                except Exception as e:
                    continue
        
        return {
            'test': 'Cross-Site Scripting (XSS)',
            'status': 'PASS' if len(vulnerabilities) == 0 else 'FAIL',
            'vulnerabilities_found': len(vulnerabilities),
            'details': vulnerabilities
        }
    
    async def test_authentication_bypass(self, session: aiohttp.ClientSession, tier: str) -> Dict[str, Any]:
        """Test for authentication bypass vulnerabilities"""
        vulnerabilities = []
        base_url = self.endpoints[tier]['base_url']
        
        # Test protected endpoints without authentication
        protected_endpoints = [
            '/api/v1/portfolio',
            '/api/v1/trades',
            '/api/v1/profile'
        ]
        
        if tier == 'premium':
            protected_endpoints.extend([
                '/api/v1/institutional',
                '/api/v1/algo',
                '/api/v1/hni/portfolio'
            ])
        
        for endpoint in protected_endpoints:
            try:
                url = urljoin(base_url, endpoint)
                
                # Test without any authentication
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        vulnerabilities.append({
                            'severity': 'CRITICAL',
                            'endpoint': endpoint,
                            'details': 'Protected endpoint accessible without authentication'
                        })
                
                # Test with invalid/expired token
                headers = {'Authorization': 'Bearer invalid_token_12345'}
                async with session.get(url, headers=headers, timeout=10) as response:
                    if response.status == 200:
                        vulnerabilities.append({
                            'severity': 'CRITICAL',
                            'endpoint': endpoint,
                            'details': 'Protected endpoint accessible with invalid token'
                        })
            
            except Exception as e:
                continue
        
        return {
            'test': 'Authentication Bypass',
            'status': 'PASS' if len(vulnerabilities) == 0 else 'FAIL',
            'vulnerabilities_found': len(vulnerabilities),
            'details': vulnerabilities
        }
    
    async def test_rate_limiting(self, session: aiohttp.ClientSession, tier: str) -> Dict[str, Any]:
        """Test rate limiting implementation"""
        vulnerabilities = []
        base_url = self.endpoints[tier]['base_url']
        
        # Test rate limiting on authentication endpoint
        auth_url = urljoin(base_url, '/api/v1/auth/login')
        
        try:
            # Send rapid requests to test rate limiting
            tasks = []
            for i in range(50):  # Send 50 requests rapidly
                task = session.post(
                    auth_url,
                    json={'username': f'test{i}', 'password': 'invalid'},
                    timeout=5
                )
                tasks.append(task)
            
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Count successful responses (should be rate limited)
            success_count = sum(1 for r in responses 
                              if not isinstance(r, Exception) and hasattr(r, 'status') and r.status not in [429, 503])
            
            if success_count > 20:  # If more than 20 requests succeeded
                vulnerabilities.append({
                    'severity': 'MEDIUM',
                    'endpoint': '/api/v1/auth/login',
                    'details': f'Rate limiting may be insufficient: {success_count}/50 requests succeeded',
                    'successful_requests': success_count
                })
        
        except Exception as e:
            logger.error(f"Rate limiting test failed for {tier}: {e}")
        
        return {
            'test': 'Rate Limiting',
            'status': 'PASS' if len(vulnerabilities) == 0 else 'FAIL',
            'vulnerabilities_found': len(vulnerabilities),
            'details': vulnerabilities
        }
    
    async def test_information_disclosure(self, session: aiohttp.ClientSession, tier: str) -> Dict[str, Any]:
        """Test for information disclosure vulnerabilities"""
        vulnerabilities = []
        base_url = self.endpoints[tier]['base_url']
        
        # Test common information disclosure endpoints
        disclosure_endpoints = [
            '/.env',
            '/config.json',
            '/api/v1/debug',
            '/health/detailed',
            '/metrics',
            '/.git/config',
            '/admin',
            '/debug'
        ]
        
        for endpoint in disclosure_endpoints:
            try:
                url = urljoin(base_url, endpoint)
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        response_text = await response.text()
                        
                        # Check for sensitive information
                        sensitive_patterns = [
                            'password',
                            'secret',
                            'api_key',
                            'database',
                            'mongodb',
                            'mysql',
                            'postgres'
                        ]
                        
                        for pattern in sensitive_patterns:
                            if pattern.lower() in response_text.lower():
                                vulnerabilities.append({
                                    'severity': 'HIGH',
                                    'endpoint': endpoint,
                                    'pattern': pattern,
                                    'details': f'Sensitive information disclosed: {pattern}'
                                })
                                break
            
            except Exception as e:
                continue
        
        return {
            'test': 'Information Disclosure',
            'status': 'PASS' if len(vulnerabilities) == 0 else 'FAIL',
            'vulnerabilities_found': len(vulnerabilities),
            'details': vulnerabilities
        }
    
    async def run_security_tests(self) -> Dict[str, Any]:
        """Run comprehensive security tests"""
        logger.info("Starting TradeMate security testing")
        
        # SSL/TLS tests (no session needed)
        for tier in ['shared', 'premium']:
            ssl_result = await self.test_ssl_tls_configuration(tier)
            self.test_results['tier_results'][tier]['tests'].append(ssl_result)
        
        # HTTP-based tests
        timeout = aiohttp.ClientTimeout(total=30, connect=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            
            for tier in ['shared', 'premium']:
                logger.info(f"Testing {tier} tier security")
                
                # Run all security tests
                tests = [
                    self.test_sql_injection(session, tier),
                    self.test_xss_vulnerabilities(session, tier),
                    self.test_authentication_bypass(session, tier),
                    self.test_rate_limiting(session, tier),
                    self.test_information_disclosure(session, tier)
                ]
                
                results = await asyncio.gather(*tests, return_exceptions=True)
                
                # Process results
                tier_passed = 0
                for result in results:
                    if isinstance(result, Exception):
                        logger.error(f"Test failed with exception: {result}")
                        continue
                    
                    self.test_results['tier_results'][tier]['tests'].append(result)
                    
                    if result['status'] == 'PASS':
                        tier_passed += 1
                    
                    # Categorize vulnerabilities
                    if 'details' in result and isinstance(result['details'], list):
                        for vuln in result['details']:
                            severity = vuln.get('severity', 'LOW')
                            if severity == 'CRITICAL':
                                self.test_results['critical_vulnerabilities'].append(vuln)
                            elif severity == 'HIGH':
                                self.test_results['high_vulnerabilities'].append(vuln)
                            elif severity == 'MEDIUM':
                                self.test_results['medium_vulnerabilities'].append(vuln)
                            else:
                                self.test_results['low_vulnerabilities'].append(vuln)
                
                # Calculate tier score
                tier_tests = len([t for t in self.test_results['tier_results'][tier]['tests'] if not isinstance(t, Exception)])
                if tier_tests > 0:
                    self.test_results['tier_results'][tier]['score'] = (tier_passed / tier_tests) * 100
        
        # Calculate overall metrics
        total_tests = sum(len(self.test_results['tier_results'][tier]['tests']) for tier in ['shared', 'premium'])
        total_passed = sum(1 for tier in ['shared', 'premium'] 
                          for test in self.test_results['tier_results'][tier]['tests'] 
                          if test.get('status') == 'PASS')
        
        self.test_results['total_tests'] = total_tests
        self.test_results['passed_tests'] = total_passed
        self.test_results['failed_tests'] = total_tests - total_passed
        
        # Generate recommendations
        self._generate_security_recommendations()
        
        return self.test_results
    
    def _generate_security_recommendations(self):
        """Generate security recommendations based on test results"""
        recommendations = []
        
        # Critical vulnerabilities
        if len(self.test_results['critical_vulnerabilities']) > 0:
            recommendations.append({
                'priority': 'CRITICAL',
                'category': 'SECURITY',
                'recommendation': 'Immediately address critical security vulnerabilities',
                'impact': 'Critical vulnerabilities can lead to complete system compromise',
                'count': len(self.test_results['critical_vulnerabilities'])
            })
        
        # High severity vulnerabilities
        if len(self.test_results['high_vulnerabilities']) > 0:
            recommendations.append({
                'priority': 'HIGH',
                'category': 'SECURITY',
                'recommendation': 'Address high-severity security issues before production',
                'impact': 'High-severity issues can compromise user data and system integrity',
                'count': len(self.test_results['high_vulnerabilities'])
            })
        
        # Premium tier specific recommendations
        premium_score = self.test_results['tier_results']['premium']['score']
        if premium_score < 90:
            recommendations.append({
                'priority': 'HIGH',
                'category': 'PREMIUM_SECURITY',
                'recommendation': 'Premium tier requires enhanced security due to high-value clients',
                'impact': 'Premium clients expect higher security standards',
                'current_score': premium_score
            })
        
        # General security recommendations
        if self.test_results['failed_tests'] > 0:
            recommendations.append({
                'priority': 'MEDIUM',
                'category': 'GENERAL',
                'recommendation': 'Implement regular security testing and monitoring',
                'impact': 'Continuous security testing prevents vulnerabilities from reaching production'
            })
        
        self.test_results['recommendations'] = recommendations

def main():
    """Main function for security testing"""
    tester = TradeMateSecurityTester()
    
    # Run async security tests
    loop = asyncio.get_event_loop()
    results = loop.run_until_complete(tester.run_security_tests())
    
    # Output results
    print(json.dumps(results, indent=2))
    
    # Return exit code based on security test results
    critical_count = len(results['critical_vulnerabilities'])
    high_count = len(results['high_vulnerabilities'])
    
    if critical_count > 0:
        logger.error(f"❌ {critical_count} critical security vulnerabilities found")
        return 2
    elif high_count > 0:
        logger.warning(f"⚠️ {high_count} high-severity security issues found")
        return 1
    else:
        logger.info("✅ No critical security vulnerabilities detected")
        return 0

if __name__ == '__main__':
    exit(main())
