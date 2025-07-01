#!/usr/bin/env python3
"""
GridWorks Regulatory Compliance Framework
=========================================
Comprehensive SEBI compliance and audit trail system for financial planning suite
"""

import asyncio
import json
import uuid
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from enum import Enum
from dataclasses import dataclass, asdict, field
import logging
import os
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ComplianceLevel(Enum):
    """Compliance severity levels"""
    INFO = "info"
    WARNING = "warning"
    VIOLATION = "violation"
    CRITICAL = "critical"


class AdviceType(Enum):
    """Types of financial advice for compliance tracking"""
    GENERAL_EDUCATION = "general_education"
    INVESTMENT_GUIDANCE = "investment_guidance"
    SPECIFIC_RECOMMENDATION = "specific_recommendation"
    MARKET_ANALYSIS = "market_analysis"
    RISK_ASSESSMENT = "risk_assessment"
    STRATEGY_BUILDING = "strategy_building"


class SEBIRegulation(Enum):
    """SEBI regulations relevant to financial advice"""
    INVESTMENT_ADVISOR_REGULATIONS_2013 = "ia_regulations_2013"
    RESEARCH_ANALYST_REGULATIONS_2014 = "ra_regulations_2014"
    PORTFOLIO_MANAGER_REGULATIONS_2020 = "pm_regulations_2020"
    MUTUAL_FUND_REGULATIONS_1996 = "mf_regulations_1996"
    SECURITIES_CONTRACTS_REGULATION_ACT = "scra_1956"


@dataclass
class ComplianceRule:
    """Individual compliance rule definition"""
    rule_id: str
    rule_name: str
    description: str
    regulation: SEBIRegulation
    severity: ComplianceLevel
    keywords_forbidden: List[str]
    keywords_required: List[str]
    pattern_checks: List[str]  # Regex patterns
    applicable_advice_types: List[AdviceType]
    auto_enforce: bool = True


@dataclass
class ComplianceViolation:
    """Compliance violation record"""
    violation_id: str
    rule_id: str
    advice_id: str
    user_id: str
    violation_type: ComplianceLevel
    description: str
    violating_content: str
    timestamp: datetime
    resolved: bool = False
    resolution_notes: Optional[str] = None
    human_reviewed: bool = False


@dataclass
class AuditLogEntry:
    """Audit log entry for all financial advice interactions"""
    log_id: str
    timestamp: datetime
    user_id: str
    advice_id: Optional[str]
    action_type: str  # "advice_request", "advice_generated", "compliance_check", etc.
    details: Dict[str, Any]
    ip_address: Optional[str] = None
    session_id: Optional[str] = None
    compliance_status: Optional[str] = None
    
    def to_hash(self) -> str:
        """Generate hash for integrity checking"""
        content = f"{self.timestamp.isoformat()}{self.user_id}{self.action_type}{json.dumps(self.details, sort_keys=True)}"
        return hashlib.sha256(content.encode()).hexdigest()


@dataclass
class ComplianceReport:
    """Compliance assessment report"""
    report_id: str
    advice_id: str
    advice_content: str
    advice_type: AdviceType
    overall_status: ComplianceLevel
    violations: List[ComplianceViolation]
    warnings: List[str]
    recommendations: List[str]
    human_review_required: bool
    timestamp: datetime
    
    @property
    def is_compliant(self) -> bool:
        """Check if advice is compliant"""
        return self.overall_status in [ComplianceLevel.INFO, ComplianceLevel.WARNING]


class SEBIComplianceEngine:
    """SEBI compliance checking engine"""
    
    def __init__(self):
        """Initialize compliance engine with rules"""
        self.compliance_rules = self._initialize_compliance_rules()
        self.violation_patterns = self._load_violation_patterns()
    
    def _initialize_compliance_rules(self) -> List[ComplianceRule]:
        """Initialize SEBI compliance rules"""
        
        rules = [
            ComplianceRule(
                rule_id="SEBI_IA_001",
                rule_name="No Guaranteed Returns",
                description="Investment advisors cannot guarantee returns or claim investments are risk-free",
                regulation=SEBIRegulation.INVESTMENT_ADVISOR_REGULATIONS_2013,
                severity=ComplianceLevel.CRITICAL,
                keywords_forbidden=[
                    "guaranteed returns", "risk-free", "sure profit", "certain returns",
                    "100% safe", "no risk", "guaranteed profit", "assured returns",
                    "risk free", "guarantee", "निश्चित रिटर्न", "गारंटीशुदा", "जोखिम मुक्त"
                ],
                keywords_required=[],
                pattern_checks=[
                    r"guarantee[d]?\s+\d+%",
                    r"assured.*\d+%.*return",
                    r"risk[- ]?free.*investment"
                ],
                applicable_advice_types=[
                    AdviceType.INVESTMENT_GUIDANCE,
                    AdviceType.SPECIFIC_RECOMMENDATION,
                    AdviceType.STRATEGY_BUILDING
                ]
            ),
            
            ComplianceRule(
                rule_id="SEBI_IA_002",
                rule_name="Market Risk Disclosure",
                description="All investment advice must include market risk disclosure",
                regulation=SEBIRegulation.INVESTMENT_ADVISOR_REGULATIONS_2013,
                severity=ComplianceLevel.WARNING,
                keywords_forbidden=[],
                keywords_required=[
                    "market risk", "investment risk", "consult", "financial advisor",
                    "बाजार जोखिम", "निवेश जोखिम", "सलाहकार", "परामर्श"
                ],
                pattern_checks=[],
                applicable_advice_types=[
                    AdviceType.INVESTMENT_GUIDANCE,
                    AdviceType.SPECIFIC_RECOMMENDATION
                ]
            ),
            
            ComplianceRule(
                rule_id="SEBI_IA_003",
                rule_name="No Specific Stock Recommendations",
                description="Cannot provide specific buy/sell recommendations for individual stocks",
                regulation=SEBIRegulation.INVESTMENT_ADVISOR_REGULATIONS_2013,
                severity=ComplianceLevel.VIOLATION,
                keywords_forbidden=[],
                keywords_required=[],
                pattern_checks=[
                    r"buy\s+(reliance|tcs|hdfc|icici|sbi|infy|itc)",
                    r"sell\s+(reliance|tcs|hdfc|icici|sbi|infy|itc)",
                    r"invest\s+in\s+(reliance|tcs|hdfc|icici|sbi|infy|itc)",
                    r"(खरीदें|बेचें)\s+(reliance|tcs|hdfc|icici|sbi|infy|itc)"
                ],
                applicable_advice_types=[
                    AdviceType.INVESTMENT_GUIDANCE,
                    AdviceType.SPECIFIC_RECOMMENDATION
                ]
            ),
            
            ComplianceRule(
                rule_id="SEBI_IA_004",
                rule_name="No Market Timing Advice",
                description="Cannot provide market timing or short-term trading advice",
                regulation=SEBIRegulation.INVESTMENT_ADVISOR_REGULATIONS_2013,
                severity=ComplianceLevel.VIOLATION,
                keywords_forbidden=[
                    "market will go up", "market will crash", "buy now", "sell now",
                    "perfect time to buy", "market top", "market bottom",
                    "बाजार ऊपर जाएगा", "बाजार गिरेगा", "अभी खरीदें", "अभी बेचें"
                ],
                keywords_required=[],
                pattern_checks=[
                    r"market will (rise|fall|crash|boom)",
                    r"(buy|sell) now",
                    r"perfect time to (buy|sell|invest)"
                ],
                applicable_advice_types=[
                    AdviceType.INVESTMENT_GUIDANCE,
                    AdviceType.MARKET_ANALYSIS
                ]
            ),
            
            ComplianceRule(
                rule_id="SEBI_MF_001",
                rule_name="Mutual Fund Risk Disclosure",
                description="Mutual fund advice must include standard risk disclosure",
                regulation=SEBIRegulation.MUTUAL_FUND_REGULATIONS_1996,
                severity=ComplianceLevel.WARNING,
                keywords_forbidden=[],
                keywords_required=[
                    "mutual fund investments are subject to market risks",
                    "past performance does not guarantee future results",
                    "म्यूचुअल फंड निवेश बाजार जोखिमों के अधीन हैं"
                ],
                pattern_checks=[],
                applicable_advice_types=[
                    AdviceType.INVESTMENT_GUIDANCE,
                    AdviceType.GENERAL_EDUCATION
                ]
            ),
            
            ComplianceRule(
                rule_id="SEBI_RA_001",
                rule_name="Research Disclaimer",
                description="Market analysis must include research disclaimer",
                regulation=SEBIRegulation.RESEARCH_ANALYST_REGULATIONS_2014,
                severity=ComplianceLevel.WARNING,
                keywords_forbidden=[],
                keywords_required=[
                    "research", "analysis", "educational", "general information",
                    "अनुसंधान", "विश्लेषण", "शैक्षिक", "सामान्य जानकारी"
                ],
                pattern_checks=[],
                applicable_advice_types=[
                    AdviceType.MARKET_ANALYSIS,
                    AdviceType.GENERAL_EDUCATION
                ]
            )
        ]
        
        return rules
    
    def _load_violation_patterns(self) -> Dict[str, List[str]]:
        """Load additional violation patterns from configuration"""
        
        return {
            "stock_recommendations": [
                r"(buy|sell|purchase|invest in)\s+\w+\s+(stock|share|equity)",
                r"(खरीदें|बेचें|निवेश करें)\s+\w+\s+(शेयर|स्टॉक)"
            ],
            "timing_advice": [
                r"(best|perfect|right)\s+time\s+to\s+(buy|sell|invest)",
                r"market\s+(top|bottom|peak|low)",
                r"(सही|बेहतरीन)\s+(समय|वक्त)\s+(खरीदने|बेचने|निवेश)"
            ],
            "guaranteed_returns": [
                r"\d+%\s+(guaranteed|assured|certain|sure)",
                r"(guaranteed|assured)\s+\d+%",
                r"\d+%\s+(गारंटीशुदा|निश्चित|पक्का)"
            ]
        }
    
    async def check_compliance(
        self, 
        advice_content: str, 
        advice_type: AdviceType,
        context: Dict[str, Any] = None
    ) -> ComplianceReport:
        """Comprehensive compliance check for financial advice"""
        
        violations = []
        warnings = []
        recommendations = []
        
        # Check against all applicable rules
        for rule in self.compliance_rules:
            if advice_type in rule.applicable_advice_types:
                violation = await self._check_rule_compliance(advice_content, rule)
                if violation:
                    violations.append(violation)
        
        # Additional pattern checks
        pattern_violations = await self._check_violation_patterns(advice_content, advice_type)
        violations.extend(pattern_violations)
        
        # Determine overall compliance status
        if any(v.violation_type == ComplianceLevel.CRITICAL for v in violations):
            overall_status = ComplianceLevel.CRITICAL
        elif any(v.violation_type == ComplianceLevel.VIOLATION for v in violations):
            overall_status = ComplianceLevel.VIOLATION
        elif any(v.violation_type == ComplianceLevel.WARNING for v in violations):
            overall_status = ComplianceLevel.WARNING
        else:
            overall_status = ComplianceLevel.INFO
        
        # Generate recommendations
        recommendations = self._generate_compliance_recommendations(violations, advice_content)
        
        # Determine if human review is required
        human_review_required = (
            overall_status in [ComplianceLevel.CRITICAL, ComplianceLevel.VIOLATION] or
            len(violations) > 3
        )
        
        report = ComplianceReport(
            report_id=str(uuid.uuid4()),
            advice_id=str(uuid.uuid4()),
            advice_content=advice_content,
            advice_type=advice_type,
            overall_status=overall_status,
            violations=violations,
            warnings=warnings,
            recommendations=recommendations,
            human_review_required=human_review_required,
            timestamp=datetime.now()
        )
        
        return report
    
    async def _check_rule_compliance(
        self, 
        content: str, 
        rule: ComplianceRule
    ) -> Optional[ComplianceViolation]:
        """Check content against a specific compliance rule"""
        
        content_lower = content.lower()
        
        # Check forbidden keywords
        for keyword in rule.keywords_forbidden:
            if keyword.lower() in content_lower:
                return ComplianceViolation(
                    violation_id=str(uuid.uuid4()),
                    rule_id=rule.rule_id,
                    advice_id="",  # Will be set by caller
                    user_id="",    # Will be set by caller
                    violation_type=rule.severity,
                    description=f"Contains forbidden phrase: '{keyword}'",
                    violating_content=keyword,
                    timestamp=datetime.now()
                )
        
        # Check required keywords
        if rule.keywords_required and rule.severity == ComplianceLevel.WARNING:
            has_required = any(keyword.lower() in content_lower for keyword in rule.keywords_required)
            if not has_required:
                return ComplianceViolation(
                    violation_id=str(uuid.uuid4()),
                    rule_id=rule.rule_id,
                    advice_id="",
                    user_id="",
                    violation_type=rule.severity,
                    description=f"Missing required disclosure: {', '.join(rule.keywords_required[:3])}",
                    violating_content="Missing required content",
                    timestamp=datetime.now()
                )
        
        # Check regex patterns
        import re
        for pattern in rule.pattern_checks:
            if re.search(pattern, content_lower, re.IGNORECASE):
                return ComplianceViolation(
                    violation_id=str(uuid.uuid4()),
                    rule_id=rule.rule_id,
                    advice_id="",
                    user_id="",
                    violation_type=rule.severity,
                    description=f"Matches prohibited pattern: {pattern}",
                    violating_content=f"Pattern: {pattern}",
                    timestamp=datetime.now()
                )
        
        return None
    
    async def _check_violation_patterns(
        self, 
        content: str, 
        advice_type: AdviceType
    ) -> List[ComplianceViolation]:
        """Check against additional violation patterns"""
        
        violations = []
        import re
        
        for category, patterns in self.violation_patterns.items():
            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    violations.append(ComplianceViolation(
                        violation_id=str(uuid.uuid4()),
                        rule_id=f"PATTERN_{category.upper()}",
                        advice_id="",
                        user_id="",
                        violation_type=ComplianceLevel.VIOLATION,
                        description=f"Matches violation pattern: {category}",
                        violating_content=f"Pattern: {pattern}",
                        timestamp=datetime.now()
                    ))
        
        return violations
    
    def _generate_compliance_recommendations(
        self, 
        violations: List[ComplianceViolation], 
        content: str
    ) -> List[str]:
        """Generate recommendations to fix compliance issues"""
        
        recommendations = []
        
        # Check for missing disclaimers
        if not any("market risk" in content.lower() for v in violations):
            recommendations.append("Add market risk disclosure")
        
        # Check for specific recommendations
        if any("specific" in v.description.lower() for v in violations):
            recommendations.append("Replace specific recommendations with general educational content")
        
        # Check for guaranteed returns
        if any("guarantee" in v.description.lower() for v in violations):
            recommendations.append("Remove guarantee language and emphasize market risks")
        
        # Check for timing advice
        if any("timing" in v.description.lower() for v in violations):
            recommendations.append("Focus on long-term investment principles instead of market timing")
        
        # Always recommend consultation
        recommendations.append("Add recommendation to consult certified financial advisor")
        
        return recommendations


class AuditTrailManager:
    """Comprehensive audit trail management"""
    
    def __init__(self, storage_path: str = "audit_logs"):
        """Initialize audit trail manager"""
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        self.current_logs = []
        self.max_memory_logs = 1000
    
    async def log_action(
        self,
        user_id: str,
        action_type: str,
        details: Dict[str, Any],
        advice_id: Optional[str] = None,
        session_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        compliance_status: Optional[str] = None
    ) -> str:
        """Log an action to the audit trail"""
        
        log_entry = AuditLogEntry(
            log_id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            user_id=user_id,
            advice_id=advice_id,
            action_type=action_type,
            details=details,
            ip_address=ip_address,
            session_id=session_id,
            compliance_status=compliance_status
        )
        
        # Add to memory logs
        self.current_logs.append(log_entry)
        
        # Persist to file
        await self._persist_log_entry(log_entry)
        
        # Cleanup old memory logs
        if len(self.current_logs) > self.max_memory_logs:
            self.current_logs = self.current_logs[-self.max_memory_logs:]
        
        logger.info(f"Audit log created: {log_entry.log_id} - {action_type}")
        return log_entry.log_id
    
    async def _persist_log_entry(self, log_entry: AuditLogEntry):
        """Persist log entry to file"""
        
        # Create daily log file
        date_str = log_entry.timestamp.strftime("%Y%m%d")
        log_file = self.storage_path / f"audit_log_{date_str}.jsonl"
        
        # Convert to JSON with hash for integrity
        log_data = asdict(log_entry)
        log_data["integrity_hash"] = log_entry.to_hash()
        
        # Append to file
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_data, default=str) + "\n")
    
    async def get_user_audit_trail(
        self, 
        user_id: str, 
        start_date: datetime = None, 
        end_date: datetime = None
    ) -> List[AuditLogEntry]:
        """Get audit trail for a specific user"""
        
        # Filter from memory logs
        filtered_logs = [
            log for log in self.current_logs 
            if log.user_id == user_id
        ]
        
        # Apply date filters
        if start_date:
            filtered_logs = [log for log in filtered_logs if log.timestamp >= start_date]
        if end_date:
            filtered_logs = [log for log in filtered_logs if log.timestamp <= end_date]
        
        # Load from files if needed (simplified implementation)
        # In production, would implement efficient file searching
        
        return sorted(filtered_logs, key=lambda x: x.timestamp, reverse=True)
    
    async def generate_compliance_report(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> Dict[str, Any]:
        """Generate compliance report for a date range"""
        
        # Get all logs in date range
        all_logs = [
            log for log in self.current_logs
            if start_date <= log.timestamp <= end_date
        ]
        
        # Analyze compliance patterns
        compliance_stats = {
            "total_advice_requests": len([log for log in all_logs if log.action_type == "advice_request"]),
            "total_advice_generated": len([log for log in all_logs if log.action_type == "advice_generated"]),
            "compliance_violations": len([log for log in all_logs if log.compliance_status == "violation"]),
            "human_reviews_required": len([log for log in all_logs if log.compliance_status == "human_review"]),
            "unique_users": len(set(log.user_id for log in all_logs)),
            "top_violation_types": self._analyze_violation_types(all_logs)
        }
        
        return {
            "report_id": str(uuid.uuid4()),
            "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
            "statistics": compliance_stats,
            "generated_at": datetime.now().isoformat()
        }
    
    def _analyze_violation_types(self, logs: List[AuditLogEntry]) -> Dict[str, int]:
        """Analyze violation types from logs"""
        
        violation_counts = {}
        
        for log in logs:
            if log.compliance_status == "violation" and "violation_type" in log.details:
                violation_type = log.details["violation_type"]
                violation_counts[violation_type] = violation_counts.get(violation_type, 0) + 1
        
        # Sort by frequency
        return dict(sorted(violation_counts.items(), key=lambda x: x[1], reverse=True))


class ComplianceFramework:
    """Main compliance framework orchestrator"""
    
    def __init__(self, storage_path: str = "compliance_data"):
        """Initialize compliance framework"""
        self.compliance_engine = SEBIComplianceEngine()
        self.audit_manager = AuditTrailManager(storage_path)
        self.active_violations = {}
    
    async def review_financial_advice(
        self,
        user_id: str,
        advice_content: str,
        advice_type: AdviceType,
        session_id: Optional[str] = None,
        context: Dict[str, Any] = None
    ) -> Tuple[bool, ComplianceReport]:
        """Complete compliance review of financial advice"""
        
        # Log the review request
        await self.audit_manager.log_action(
            user_id=user_id,
            action_type="compliance_review_requested",
            details={
                "advice_type": advice_type.value,
                "content_length": len(advice_content),
                "context": context or {}
            },
            session_id=session_id
        )
        
        # Perform compliance check
        compliance_report = await self.compliance_engine.check_compliance(
            advice_content, advice_type, context
        )
        
        # Update violation tracking
        if compliance_report.violations:
            for violation in compliance_report.violations:
                violation.user_id = user_id
                violation.advice_id = compliance_report.advice_id
                self.active_violations[violation.violation_id] = violation
        
        # Log compliance results
        await self.audit_manager.log_action(
            user_id=user_id,
            action_type="compliance_review_completed",
            details={
                "advice_id": compliance_report.advice_id,
                "overall_status": compliance_report.overall_status.value,
                "violation_count": len(compliance_report.violations),
                "human_review_required": compliance_report.human_review_required
            },
            advice_id=compliance_report.advice_id,
            session_id=session_id,
            compliance_status=compliance_report.overall_status.value
        )
        
        return compliance_report.is_compliant, compliance_report
    
    async def get_compliance_summary(self, user_id: str) -> Dict[str, Any]:
        """Get compliance summary for a user"""
        
        # Get recent audit trail
        recent_logs = await self.audit_manager.get_user_audit_trail(
            user_id, 
            start_date=datetime.now() - timedelta(days=30)
        )
        
        # Calculate compliance metrics
        advice_requests = [log for log in recent_logs if log.action_type == "advice_request"]
        violations = [log for log in recent_logs if log.compliance_status == "violation"]
        
        return {
            "user_id": user_id,
            "period_days": 30,
            "total_advice_requests": len(advice_requests),
            "compliance_violations": len(violations),
            "compliance_rate": (len(advice_requests) - len(violations)) / max(len(advice_requests), 1) * 100,
            "last_violation": violations[0].timestamp.isoformat() if violations else None,
            "summary_generated": datetime.now().isoformat()
        }


# Example usage and testing
async def main():
    """Example usage of Compliance Framework"""
    
    framework = ComplianceFramework()
    
    # Test compliant advice
    compliant_advice = """
    Mutual fund investments are generally suitable for long-term wealth creation. 
    Consider diversifying across equity and debt funds based on your risk profile.
    Mutual fund investments are subject to market risks. Please read the offer 
    document carefully before investing and consult your financial advisor.
    """
    
    is_compliant, report = await framework.review_financial_advice(
        user_id="user123",
        advice_content=compliant_advice,
        advice_type=AdviceType.INVESTMENT_GUIDANCE,
        session_id="session456"
    )
    
    print(f"Compliant advice result: {is_compliant}")
    print(f"Violations: {len(report.violations)}")
    
    # Test non-compliant advice
    non_compliant_advice = """
    Buy Reliance stock immediately! It will give guaranteed 20% returns.
    This is a risk-free investment and the market will definitely go up next week.
    """
    
    is_compliant, report = await framework.review_financial_advice(
        user_id="user123",
        advice_content=non_compliant_advice,
        advice_type=AdviceType.SPECIFIC_RECOMMENDATION,
        session_id="session456"
    )
    
    print(f"Non-compliant advice result: {is_compliant}")
    print(f"Violations: {len(report.violations)}")
    for violation in report.violations:
        print(f"- {violation.description}")
    
    # Get compliance summary
    summary = await framework.get_compliance_summary("user123")
    print(f"Compliance summary: {summary}")


if __name__ == "__main__":
    asyncio.run(main())