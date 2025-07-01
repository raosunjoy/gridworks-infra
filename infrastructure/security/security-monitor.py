#!/usr/bin/env python3
"""
TradeMate Security Monitoring and Continuous Compliance
Real-time security monitoring with tier-specific alerting
"""

import asyncio
import logging
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any
import subprocess
import requests
from prometheus_client import start_http_server, Gauge, Counter, Histogram
import hashlib
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TradeMateSecurityMonitor:
    """Continuous security monitoring for TradeMate infrastructure"""
    
    def __init__(self):
        # Security metrics
        self.security_events = Counter(
            'trademate_security_events_total',
            'Total security events by tier and severity',
            ['tier', 'severity', 'event_type']
        )
        
        self.compliance_score = Gauge(
            'trademate_compliance_score',
            'Security compliance score by tier',
            ['tier', 'framework']
        )
        
        self.vulnerability_count = Gauge(
            'trademate_vulnerabilities_total',
            'Number of vulnerabilities by severity',
            ['tier', 'severity']
        )
        
        self.failed_auth_attempts = Counter(
            'trademate_failed_auth_attempts_total',
            'Failed authentication attempts by tier',
            ['tier', 'source_ip']
        )
        
        self.security_scan_duration = Histogram(
            'trademate_security_scan_duration_seconds',
            'Time taken for security scans',
            ['scan_type', 'tier']
        )
        
        # Security thresholds
        self.thresholds = {
            'shared': {
                'max_failed_auth_per_minute': 100,
                'min_compliance_score': 95.0,
                'max_critical_vulnerabilities': 0,
                'max_high_vulnerabilities': 2
            },
            'premium': {
                'max_failed_auth_per_minute': 50,
                'min_compliance_score': 98.0,
                'max_critical_vulnerabilities': 0,
                'max_high_vulnerabilities': 0
            }
        }
        
        # Monitoring state
        self.last_scan_time = {}
        self.security_incidents = []
        self.blocked_ips = set()
        
    async def monitor_kubernetes_security(self) -> Dict[str, Any]:
        """Monitor Kubernetes security configurations"""
        try:
            security_issues = []
            
            # Check pod security policies
            result = subprocess.run(
                ['kubectl', 'get', 'podsecuritypolicy', '-o', 'json'],
                capture_output=True, text=True, timeout=30
            )
            
            if result.returncode == 0:
                psp_data = json.loads(result.stdout)
                psp_count = len(psp_data.get('items', []))
                
                if psp_count < 2:  # Should have shared and premium PSPs
                    security_issues.append({
                        'severity': 'HIGH',
                        'issue': 'Insufficient Pod Security Policies',
                        'details': f'Only {psp_count} PSPs found, expected 2'
                    })
            
            # Check network policies
            for namespace in ['shared', 'premium']:
                result = subprocess.run(
                    ['kubectl', 'get', 'networkpolicy', '-n', namespace, '-o', 'json'],
                    capture_output=True, text=True, timeout=30
                )
                
                if result.returncode == 0:
                    np_data = json.loads(result.stdout)
                    if len(np_data.get('items', [])) == 0:
                        security_issues.append({
                            'severity': 'CRITICAL',
                            'issue': f'No Network Policy in {namespace} namespace',
                            'details': 'Network segmentation not enforced'
                        })
            
            # Check RBAC configurations
            result = subprocess.run(
                ['kubectl', 'get', 'rolebinding', '--all-namespaces', '-o', 'json'],
                capture_output=True, text=True, timeout=30
            )
            
            if result.returncode == 0:
                rb_data = json.loads(result.stdout)
                
                # Check for overly permissive bindings
                for binding in rb_data.get('items', []):
                    if binding.get('roleRef', {}).get('name') == 'cluster-admin':
                        security_issues.append({
                            'severity': 'HIGH',
                            'issue': 'Overly permissive RBAC binding',
                            'details': f"cluster-admin binding in {binding.get('metadata', {}).get('namespace')}"
                        })
            
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'total_issues': len(security_issues),
                'issues': security_issues
            }
            
        except Exception as e:
            logger.error(f"Kubernetes security monitoring failed: {e}")
            return {'error': str(e)}
    
    async def monitor_authentication_security(self) -> Dict[str, Any]:
        """Monitor authentication security across tiers"""
        try:
            auth_issues = []
            
            # Check for authentication anomalies (simulated)
            for tier in ['shared', 'premium']:
                # Simulate checking authentication logs
                failed_attempts = self._get_failed_auth_count(tier)
                threshold = self.thresholds[tier]['max_failed_auth_per_minute']
                
                if failed_attempts > threshold:
                    auth_issues.append({
                        'tier': tier,
                        'severity': 'HIGH',
                        'issue': 'High authentication failure rate',
                        'details': f'{failed_attempts} failed attempts/min (threshold: {threshold})',
                        'failed_attempts': failed_attempts,
                        'threshold': threshold
                    })
                    
                    # Update metrics
                    self.security_events.labels(
                        tier=tier, 
                        severity='HIGH', 
                        event_type='auth_anomaly'
                    ).inc()
            
            # Check for brute force attacks
            suspicious_ips = self._detect_brute_force_attacks()
            for ip, attempts in suspicious_ips.items():
                auth_issues.append({
                    'severity': 'CRITICAL',
                    'issue': 'Brute force attack detected',
                    'details': f'IP {ip} made {attempts} failed attempts',
                    'source_ip': ip,
                    'attempts': attempts
                })
                
                # Block suspicious IP
                self.blocked_ips.add(ip)
                self._block_ip(ip)
            
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'total_issues': len(auth_issues),
                'issues': auth_issues,
                'blocked_ips': list(self.blocked_ips)
            }
            
        except Exception as e:
            logger.error(f"Authentication security monitoring failed: {e}")
            return {'error': str(e)}
    
    async def monitor_compliance_status(self) -> Dict[str, Any]:
        """Monitor ongoing compliance status"""
        try:
            compliance_issues = []
            
            # Run SEBI compliance check
            result = subprocess.run(
                ['python3', '/scripts/sebi-compliance-check.py'],
                capture_output=True, text=True, timeout=60
            )
            
            if result.returncode == 0:
                compliance_data = json.loads(result.stdout)
                
                # Check compliance scores
                for tier in ['shared', 'premium']:
                    tier_score = compliance_data.get('tier_compliance', {}).get(tier, {}).get('score', 0)
                    min_score = self.thresholds[tier]['min_compliance_score']
                    
                    # Update metrics
                    self.compliance_score.labels(tier=tier, framework='sebi').set(tier_score)
                    
                    if tier_score < min_score:
                        compliance_issues.append({
                            'tier': tier,
                            'severity': 'HIGH',
                            'issue': 'Compliance score below threshold',
                            'details': f'Score: {tier_score}%, Required: {min_score}%',
                            'current_score': tier_score,
                            'required_score': min_score
                        })
                
                # Check for critical violations
                critical_violations = compliance_data.get('critical_violations', [])
                for violation in critical_violations:
                    compliance_issues.append({
                        'tier': violation.get('tier'),
                        'severity': 'CRITICAL',
                        'issue': 'Critical compliance violation',
                        'details': violation.get('requirement'),
                        'regulation': violation.get('regulation')
                    })
            
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'total_issues': len(compliance_issues),
                'issues': compliance_issues
            }
            
        except Exception as e:
            logger.error(f"Compliance monitoring failed: {e}")
            return {'error': str(e)}
    
    async def monitor_vulnerability_status(self) -> Dict[str, Any]:
        """Monitor vulnerability scan results"""
        try:
            vuln_issues = []
            
            # Check latest vulnerability scan results
            for tier in ['shared', 'premium']:
                # Read vulnerability scan results (simulated file path)
                scan_file = f'/tmp/{tier}-vulnerability-scan.json'
                
                try:
                    with open(scan_file, 'r') as f:
                        scan_data = json.load(f)
                    
                    # Count vulnerabilities by severity
                    critical_count = len(scan_data.get('critical_vulnerabilities', []))
                    high_count = len(scan_data.get('high_vulnerabilities', []))
                    medium_count = len(scan_data.get('medium_vulnerabilities', []))
                    low_count = len(scan_data.get('low_vulnerabilities', []))
                    
                    # Update metrics
                    self.vulnerability_count.labels(tier=tier, severity='critical').set(critical_count)
                    self.vulnerability_count.labels(tier=tier, severity='high').set(high_count)
                    self.vulnerability_count.labels(tier=tier, severity='medium').set(medium_count)
                    self.vulnerability_count.labels(tier=tier, severity='low').set(low_count)
                    
                    # Check against thresholds
                    max_critical = self.thresholds[tier]['max_critical_vulnerabilities']
                    max_high = self.thresholds[tier]['max_high_vulnerabilities']
                    
                    if critical_count > max_critical:
                        vuln_issues.append({
                            'tier': tier,
                            'severity': 'CRITICAL',
                            'issue': 'Critical vulnerabilities detected',
                            'details': f'{critical_count} critical vulnerabilities (max: {max_critical})',
                            'count': critical_count,
                            'threshold': max_critical
                        })
                    
                    if high_count > max_high:
                        vuln_issues.append({
                            'tier': tier,
                            'severity': 'HIGH',
                            'issue': 'High-severity vulnerabilities detected',
                            'details': f'{high_count} high vulnerabilities (max: {max_high})',
                            'count': high_count,
                            'threshold': max_high
                        })
                
                except FileNotFoundError:
                    vuln_issues.append({
                        'tier': tier,
                        'severity': 'MEDIUM',
                        'issue': 'Vulnerability scan data not found',
                        'details': f'No recent scan data for {tier} tier'
                    })
            
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'total_issues': len(vuln_issues),
                'issues': vuln_issues
            }
            
        except Exception as e:
            logger.error(f"Vulnerability monitoring failed: {e}")
            return {'error': str(e)}
    
    def _get_failed_auth_count(self, tier: str) -> int:
        """Get failed authentication count for tier (simulated)"""
        # In real implementation, would query actual logs
        # Simulating varied failure rates
        if tier == 'shared':
            return 45  # Below threshold of 100
        else:
            return 25  # Below threshold of 50
    
    def _detect_brute_force_attacks(self) -> Dict[str, int]:
        """Detect brute force attacks (simulated)"""
        # In real implementation, would analyze actual logs
        # Simulating occasional attacks
        suspicious_ips = {}
        
        # Simulate detection logic
        import random
        if random.random() < 0.1:  # 10% chance of detecting an attack
            suspicious_ips['192.168.1.100'] = 150
        
        return suspicious_ips
    
    def _block_ip(self, ip: str):
        """Block suspicious IP address"""
        try:
            # In real implementation, would update firewall rules
            logger.warning(f"Blocking suspicious IP: {ip}")
            
            # Update security event metric
            self.security_events.labels(
                tier='global',
                severity='CRITICAL',
                event_type='ip_blocked'
            ).inc()
            
        except Exception as e:
            logger.error(f"Failed to block IP {ip}: {e}")
    
    async def generate_security_report(self) -> Dict[str, Any]:
        """Generate comprehensive security report"""
        logger.info("Generating security monitoring report")
        
        # Run all monitoring checks
        k8s_results = await self.monitor_kubernetes_security()
        auth_results = await self.monitor_authentication_security()
        compliance_results = await self.monitor_compliance_status()
        vuln_results = await self.monitor_vulnerability_status()
        
        # Aggregate results
        total_issues = (
            k8s_results.get('total_issues', 0) +
            auth_results.get('total_issues', 0) +
            compliance_results.get('total_issues', 0) +
            vuln_results.get('total_issues', 0)
        )
        
        # Calculate security score
        critical_issues = sum(1 for result in [k8s_results, auth_results, compliance_results, vuln_results]
                            for issue in result.get('issues', [])
                            if issue.get('severity') == 'CRITICAL')
        
        high_issues = sum(1 for result in [k8s_results, auth_results, compliance_results, vuln_results]
                        for issue in result.get('issues', [])
                        if issue.get('severity') == 'HIGH')
        
        # Security score calculation (100 - penalties)
        security_score = 100 - (critical_issues * 20) - (high_issues * 10)
        security_score = max(0, security_score)  # Don't go below 0
        
        report = {
            'timestamp': datetime.utcnow().isoformat(),
            'security_score': security_score,
            'total_issues': total_issues,
            'critical_issues': critical_issues,
            'high_issues': high_issues,
            'monitoring_results': {
                'kubernetes_security': k8s_results,
                'authentication_security': auth_results,
                'compliance_status': compliance_results,
                'vulnerability_status': vuln_results
            },
            'blocked_ips': list(self.blocked_ips),
            'recommendations': self._generate_security_recommendations(total_issues, critical_issues, high_issues)
        }
        
        return report
    
    def _generate_security_recommendations(self, total_issues: int, critical_issues: int, high_issues: int) -> List[Dict[str, Any]]:
        """Generate security recommendations"""
        recommendations = []
        
        if critical_issues > 0:
            recommendations.append({
                'priority': 'CRITICAL',
                'action': 'Immediately address critical security issues',
                'details': f'{critical_issues} critical issues require immediate attention',
                'timeline': 'Within 1 hour'
            })
        
        if high_issues > 0:
            recommendations.append({
                'priority': 'HIGH',
                'action': 'Address high-severity security issues',
                'details': f'{high_issues} high-severity issues need resolution',
                'timeline': 'Within 24 hours'
            })
        
        if total_issues > 10:
            recommendations.append({
                'priority': 'MEDIUM',
                'action': 'Review security monitoring processes',
                'details': 'High number of security issues detected',
                'timeline': 'Within 1 week'
            })
        
        if len(self.blocked_ips) > 0:
            recommendations.append({
                'priority': 'HIGH',
                'action': 'Review blocked IP addresses',
                'details': f'{len(self.blocked_ips)} IPs currently blocked',
                'timeline': 'Daily review'
            })
        
        return recommendations
    
    async def continuous_monitoring(self):
        """Main continuous monitoring loop"""
        logger.info("Starting TradeMate continuous security monitoring")
        
        while True:
            try:
                # Generate security report
                report = await self.generate_security_report()
                
                # Log security status
                logger.info(f"Security Score: {report['security_score']}/100, "
                          f"Issues: {report['total_issues']} "
                          f"(Critical: {report['critical_issues']}, High: {report['high_issues']})")
                
                # Save report for external access
                with open('/tmp/security-monitoring-report.json', 'w') as f:
                    json.dump(report, f, indent=2)
                
                # Send alerts for critical issues
                if report['critical_issues'] > 0:
                    await self._send_critical_alert(report)
                
                # Wait before next check
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"Error in continuous monitoring: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error
    
    async def _send_critical_alert(self, report: Dict[str, Any]):
        """Send critical security alert"""
        try:
            # In real implementation, would integrate with AlertManager
            alert_data = {
                'alert': 'TradeMate Critical Security Issue',
                'severity': 'CRITICAL',
                'summary': f"{report['critical_issues']} critical security issues detected",
                'details': report['monitoring_results'],
                'timestamp': report['timestamp']
            }
            
            logger.critical(f"🚨 CRITICAL SECURITY ALERT: {alert_data['summary']}")
            
            # Would send to Slack, PagerDuty, etc.
            
        except Exception as e:
            logger.error(f"Failed to send critical alert: {e}")

def main():
    """Main function for security monitoring"""
    monitor = TradeMateSecurityMonitor()
    
    # Start metrics server
    metrics_port = int(os.getenv('METRICS_PORT', 9091))
    start_http_server(metrics_port)
    logger.info(f"Security metrics server started on port {metrics_port}")
    
    # Start continuous monitoring
    loop = asyncio.get_event_loop()
    loop.run_until_complete(monitor.continuous_monitoring())

if __name__ == '__main__':
    main()
