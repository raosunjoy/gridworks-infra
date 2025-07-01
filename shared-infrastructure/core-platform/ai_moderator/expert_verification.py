"""
Expert Verification Engine
ZK-verified expert credentials and performance tracking system
"""

import asyncio
import hashlib
import json
import re
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from decimal import Decimal
import aiohttp
import cv2
import numpy as np
from PIL import Image
import pytesseract

logger = logging.getLogger(__name__)


class ExpertTier(Enum):
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"


class VerificationStatus(Enum):
    PENDING = "pending"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUSPENDED = "suspended"


class CredentialType(Enum):
    SEBI_REGISTRATION = "sebi_registration"
    BANK_STATEMENT = "bank_statement"
    TRADING_SCREENSHOT = "trading_screenshot"
    ID_VERIFICATION = "id_verification"
    EXPERIENCE_CERTIFICATE = "experience_certificate"
    REFERENCE_LETTER = "reference_letter"


@dataclass
class ExpertCredential:
    """Expert credential structure"""
    credential_id: str
    expert_id: str
    credential_type: CredentialType
    document_url: str
    extracted_data: Dict[str, Any]
    verification_status: VerificationStatus
    confidence_score: float
    verified_by: Optional[str]
    verification_timestamp: Optional[datetime]
    expiry_date: Optional[datetime]
    zk_proof: Optional[str]


@dataclass
class ExpertProfile:
    """Complete expert profile"""
    expert_id: str
    username: str
    display_name: str
    tier: ExpertTier
    verification_status: VerificationStatus
    credentials: List[ExpertCredential]
    performance_metrics: Dict[str, Any]
    specializations: List[str]
    languages: List[str]
    bio: str
    profile_image_url: Optional[str]
    created_at: datetime
    last_active: datetime
    revenue_sharing: Dict[str, Any]
    reputation_score: float


@dataclass
class TradingPerformance:
    """Trading performance tracking"""
    performance_id: str
    expert_id: str
    call_id: str
    symbol: str
    action: str
    entry_price: float
    exit_price: Optional[float]
    target_hit: bool
    stop_loss_hit: bool
    return_percentage: Optional[float]
    call_timestamp: datetime
    exit_timestamp: Optional[datetime]
    followers_count: int
    followers_profit: Optional[float]


class DocumentVerifier:
    """AI-powered document verification"""
    
    def __init__(self):
        self.sebi_patterns = {
            "registration_number": r"INZ\d{12}",
            "validity": r"valid\s+till\s+(\d{2}/\d{2}/\d{4})",
            "name": r"Name:\s*([A-Za-z\s]+)",
            "category": r"Category:\s*([A-Za-z\s]+)"
        }
        
        self.bank_patterns = {
            "account_number": r"Account\s+No\.?\s*:?\s*(\d{10,18})",
            "ifsc": r"IFSC\s*:?\s*([A-Z]{4}0[A-Z0-9]{6})",
            "balance": r"Balance\s*:?\s*₹?\s*([\d,]+(?:\.\d{2})?)",
            "transaction": r"([\d/\-]+)\s+.*?₹?\s*([\d,]+(?:\.\d{2})?)"
        }
    
    async def verify_document(
        self, 
        credential: ExpertCredential
    ) -> Dict[str, Any]:
        """Verify a document using AI and pattern matching"""
        
        try:
            # Download and process document
            document_data = await self._process_document(credential.document_url)
            
            if credential.credential_type == CredentialType.SEBI_REGISTRATION:
                result = await self._verify_sebi_document(document_data)
            elif credential.credential_type == CredentialType.BANK_STATEMENT:
                result = await self._verify_bank_statement(document_data)
            elif credential.credential_type == CredentialType.TRADING_SCREENSHOT:
                result = await self._verify_trading_screenshot(document_data)
            else:
                result = await self._verify_generic_document(document_data)
            
            return result
            
        except Exception as e:
            logger.error(f"Document verification failed: {e}")
            return {
                "verified": False,
                "confidence": 0.0,
                "error": str(e),
                "extracted_data": {}
            }
    
    async def _process_document(self, document_url: str) -> Dict[str, Any]:
        """Download and preprocess document"""
        
        try:
            # Download document (simplified - would use proper HTTP client)
            async with aiohttp.ClientSession() as session:
                async with session.get(document_url) as response:
                    document_bytes = await response.read()
            
            # Convert to image if needed
            image = Image.open(document_bytes)
            
            # OCR extraction
            extracted_text = pytesseract.image_to_string(image)
            
            return {
                "text": extracted_text,
                "image_size": image.size,
                "format": image.format
            }
            
        except Exception as e:
            logger.error(f"Document processing failed: {e}")
            raise
    
    async def _verify_sebi_document(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """Verify SEBI registration document"""
        
        text = document_data["text"]
        extracted_data = {}
        confidence = 0.0
        
        # Extract registration number
        reg_match = re.search(self.sebi_patterns["registration_number"], text)
        if reg_match:
            extracted_data["registration_number"] = reg_match.group(0)
            confidence += 0.4
        
        # Extract validity
        validity_match = re.search(self.sebi_patterns["validity"], text)
        if validity_match:
            extracted_data["validity"] = validity_match.group(1)
            
            # Check if not expired
            try:
                validity_date = datetime.strptime(validity_match.group(1), "%d/%m/%Y")
                if validity_date > datetime.now():
                    confidence += 0.3
                    extracted_data["is_valid"] = True
                else:
                    extracted_data["is_valid"] = False
            except:
                extracted_data["is_valid"] = False
        
        # Extract name
        name_match = re.search(self.sebi_patterns["name"], text)
        if name_match:
            extracted_data["registered_name"] = name_match.group(1).strip()
            confidence += 0.2
        
        # Check for SEBI logo/watermark (simplified)
        if "SEBI" in text or "Securities and Exchange Board" in text:
            confidence += 0.1
        
        return {
            "verified": confidence > 0.6,
            "confidence": confidence,
            "extracted_data": extracted_data,
            "document_type": "sebi_registration"
        }
    
    async def _verify_bank_statement(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """Verify bank statement"""
        
        text = document_data["text"]
        extracted_data = {}
        confidence = 0.0
        
        # Extract account details
        account_match = re.search(self.bank_patterns["account_number"], text)
        if account_match:
            extracted_data["account_number"] = account_match.group(1)
            confidence += 0.3
        
        # Extract IFSC
        ifsc_match = re.search(self.bank_patterns["ifsc"], text)
        if ifsc_match:
            extracted_data["ifsc"] = ifsc_match.group(1)
            confidence += 0.2
        
        # Extract balance
        balance_match = re.search(self.bank_patterns["balance"], text)
        if balance_match:
            balance_str = balance_match.group(1).replace(",", "")
            try:
                balance = float(balance_str)
                extracted_data["balance"] = balance
                
                # Higher balance indicates serious trader
                if balance > 100000:  # 1 Lakh
                    confidence += 0.3
                elif balance > 50000:
                    confidence += 0.2
                else:
                    confidence += 0.1
            except:
                pass
        
        # Extract transactions (look for trading-related)
        transactions = re.findall(self.bank_patterns["transaction"], text)
        trading_transactions = []
        
        for transaction in transactions:
            date_str, amount_str = transaction
            amount = float(amount_str.replace(",", ""))
            
            # Look for trading-related transactions
            if amount > 10000:  # Significant amounts
                trading_transactions.append({
                    "date": date_str,
                    "amount": amount
                })
        
        if trading_transactions:
            extracted_data["trading_transactions"] = trading_transactions[:10]  # Top 10
            confidence += 0.2
        
        return {
            "verified": confidence > 0.5,
            "confidence": confidence,
            "extracted_data": extracted_data,
            "document_type": "bank_statement"
        }
    
    async def _verify_trading_screenshot(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """Verify trading platform screenshot"""
        
        text = document_data["text"]
        extracted_data = {}
        confidence = 0.0
        
        # Look for trading platform indicators
        platform_indicators = [
            "Zerodha", "Kite", "Upstox", "Angel Broking", "HDFC Securities",
            "Portfolio", "Holdings", "P&L", "Profit & Loss"
        ]
        
        detected_platform = None
        for indicator in platform_indicators:
            if indicator.lower() in text.lower():
                detected_platform = indicator
                confidence += 0.2
                break
        
        if detected_platform:
            extracted_data["platform"] = detected_platform
        
        # Look for P&L figures
        pnl_patterns = [
            r"P&L\s*:?\s*₹?\s*([\+\-]?[\d,]+(?:\.\d{2})?)",
            r"Profit.*?₹?\s*([\+\-]?[\d,]+(?:\.\d{2})?)",
            r"Loss.*?₹?\s*([\+\-]?[\d,]+(?:\.\d{2})?)"
        ]
        
        for pattern in pnl_patterns:
            pnl_match = re.search(pattern, text)
            if pnl_match:
                pnl_str = pnl_match.group(1).replace(",", "")
                try:
                    pnl = float(pnl_str)
                    extracted_data["pnl"] = pnl
                    
                    # Positive P&L increases confidence
                    if pnl > 0:
                        confidence += 0.3
                    else:
                        confidence += 0.1  # Even losses show trading activity
                    break
                except:
                    pass
        
        # Look for holdings/positions
        holdings_keywords = ["Holdings", "Positions", "Quantity", "LTP"]
        holdings_count = sum(1 for keyword in holdings_keywords if keyword in text)
        if holdings_count >= 2:
            confidence += 0.2
            extracted_data["has_holdings"] = True
        
        # Check image quality and authenticity
        image_quality_score = await self._assess_image_quality(document_data)
        confidence += image_quality_score * 0.1
        
        return {
            "verified": confidence > 0.4,
            "confidence": confidence,
            "extracted_data": extracted_data,
            "document_type": "trading_screenshot"
        }
    
    async def _verify_generic_document(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """Verify generic document"""
        
        # Basic verification for other document types
        text = document_data["text"]
        
        # Check if document has meaningful content
        word_count = len(text.split())
        confidence = min(word_count / 100, 0.5)  # More words = more confidence, cap at 0.5
        
        return {
            "verified": confidence > 0.2,
            "confidence": confidence,
            "extracted_data": {"word_count": word_count},
            "document_type": "generic"
        }
    
    async def _assess_image_quality(self, document_data: Dict[str, Any]) -> float:
        """Assess image quality to detect fake/manipulated images"""
        
        # Simplified quality assessment
        # In production, this would use advanced image analysis
        
        image_size = document_data.get("image_size", (0, 0))
        
        # Minimum resolution check
        if image_size[0] * image_size[1] > 300000:  # At least 300k pixels
            return 0.8
        elif image_size[0] * image_size[1] > 100000:
            return 0.5
        else:
            return 0.2


class PerformanceTracker:
    """Track expert trading performance"""
    
    def __init__(self):
        self.performance_cache = {}
        self.call_tracking = {}
    
    async def track_trading_call(
        self, 
        expert_id: str, 
        call_data: Dict[str, Any]
    ) -> TradingPerformance:
        """Track a new trading call"""
        
        performance = TradingPerformance(
            performance_id=f"perf_{hashlib.md5(f'{expert_id}_{call_data[\"call_id\"]}'.encode()).hexdigest()[:8]}",
            expert_id=expert_id,
            call_id=call_data["call_id"],
            symbol=call_data["symbol"],
            action=call_data["action"],
            entry_price=call_data["entry_price"],
            exit_price=None,
            target_hit=False,
            stop_loss_hit=False,
            return_percentage=None,
            call_timestamp=datetime.now(timezone.utc),
            exit_timestamp=None,
            followers_count=call_data.get("followers_count", 0),
            followers_profit=None
        )
        
        # Store for tracking
        self.call_tracking[call_data["call_id"]] = performance
        
        return performance
    
    async def update_call_outcome(
        self, 
        call_id: str, 
        exit_price: float, 
        exit_reason: str
    ) -> Optional[TradingPerformance]:
        """Update call outcome when position is closed"""
        
        if call_id not in self.call_tracking:
            return None
        
        performance = self.call_tracking[call_id]
        performance.exit_price = exit_price
        performance.exit_timestamp = datetime.now(timezone.utc)
        
        # Calculate return
        if performance.action.upper() in ["BUY", "LONG"]:
            return_pct = ((exit_price - performance.entry_price) / performance.entry_price) * 100
        else:  # SELL/SHORT
            return_pct = ((performance.entry_price - exit_price) / performance.entry_price) * 100
        
        performance.return_percentage = return_pct
        
        # Update hit flags
        if exit_reason == "target":
            performance.target_hit = True
        elif exit_reason == "stop_loss":
            performance.stop_loss_hit = True
        
        # Calculate followers profit (simplified)
        if performance.followers_count > 0:
            avg_investment = 10000  # Assume average ₹10k per follower
            performance.followers_profit = (
                performance.followers_count * avg_investment * (return_pct / 100)
            )
        
        return performance
    
    async def calculate_expert_metrics(self, expert_id: str) -> Dict[str, Any]:
        """Calculate comprehensive expert performance metrics"""
        
        # Get all expert's calls
        expert_calls = [
            perf for perf in self.call_tracking.values()
            if perf.expert_id == expert_id
        ]
        
        if not expert_calls:
            return {
                "total_calls": 0,
                "accuracy": 0.0,
                "avg_return": 0.0,
                "total_followers_profit": 0.0,
                "win_rate": 0.0,
                "avg_holding_period": 0.0
            }
        
        # Calculate metrics
        total_calls = len(expert_calls)
        closed_calls = [call for call in expert_calls if call.exit_price is not None]
        
        if closed_calls:
            profitable_calls = [call for call in closed_calls if call.return_percentage > 0]
            win_rate = len(profitable_calls) / len(closed_calls)
            avg_return = sum(call.return_percentage for call in closed_calls) / len(closed_calls)
            
            # Calculate holding period
            holding_periods = []
            for call in closed_calls:
                if call.exit_timestamp:
                    period = (call.exit_timestamp - call.call_timestamp).total_seconds() / 3600  # Hours
                    holding_periods.append(period)
            
            avg_holding_period = sum(holding_periods) / len(holding_periods) if holding_periods else 0
            
            # Total followers profit
            total_followers_profit = sum(
                call.followers_profit for call in closed_calls 
                if call.followers_profit is not None
            )
        else:
            win_rate = 0.0
            avg_return = 0.0
            avg_holding_period = 0.0
            total_followers_profit = 0.0
        
        # Accuracy score (combines win rate and return magnitude)
        accuracy = (win_rate * 0.7) + (min(max(avg_return, -10), 10) / 10 * 0.3)
        
        return {
            "total_calls": total_calls,
            "closed_calls": len(closed_calls),
            "accuracy": round(accuracy, 3),
            "win_rate": round(win_rate, 3),
            "avg_return": round(avg_return, 2),
            "total_followers_profit": round(total_followers_profit, 2),
            "avg_holding_period": round(avg_holding_period, 1),
            "last_30_days": await self._get_recent_performance(expert_id, 30),
            "specialization_performance": await self._get_specialization_performance(expert_id)
        }
    
    async def _get_recent_performance(self, expert_id: str, days: int) -> Dict[str, Any]:
        """Get performance for recent period"""
        
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        recent_calls = [
            perf for perf in self.call_tracking.values()
            if perf.expert_id == expert_id and perf.call_timestamp > cutoff_date
        ]
        
        if not recent_calls:
            return {"calls": 0, "accuracy": 0.0}
        
        closed_recent = [call for call in recent_calls if call.exit_price is not None]
        
        if closed_recent:
            profitable = [call for call in closed_recent if call.return_percentage > 0]
            accuracy = len(profitable) / len(closed_recent)
        else:
            accuracy = 0.0
        
        return {
            "calls": len(recent_calls),
            "closed": len(closed_recent),
            "accuracy": round(accuracy, 3)
        }
    
    async def _get_specialization_performance(self, expert_id: str) -> Dict[str, Any]:
        """Get performance by stock/sector specialization"""
        
        expert_calls = [
            perf for perf in self.call_tracking.values()
            if perf.expert_id == expert_id and perf.exit_price is not None
        ]
        
        # Group by symbol
        symbol_performance = {}
        for call in expert_calls:
            symbol = call.symbol
            if symbol not in symbol_performance:
                symbol_performance[symbol] = {"calls": 0, "profitable": 0, "total_return": 0}
            
            symbol_performance[symbol]["calls"] += 1
            symbol_performance[symbol]["total_return"] += call.return_percentage
            
            if call.return_percentage > 0:
                symbol_performance[symbol]["profitable"] += 1
        
        # Calculate accuracy by symbol
        specialization = {}
        for symbol, data in symbol_performance.items():
            if data["calls"] >= 3:  # Minimum 3 calls to consider specialization
                accuracy = data["profitable"] / data["calls"]
                avg_return = data["total_return"] / data["calls"]
                
                specialization[symbol] = {
                    "calls": data["calls"],
                    "accuracy": round(accuracy, 3),
                    "avg_return": round(avg_return, 2)
                }
        
        return specialization


class ExpertVerificationEngine:
    """Main expert verification engine"""
    
    def __init__(self):
        self.document_verifier = DocumentVerifier()
        self.performance_tracker = PerformanceTracker()
        
        # Tier requirements
        self.tier_requirements = {
            ExpertTier.BRONZE: {
                "min_accuracy": 0.60,
                "min_calls": 10,
                "min_followers": 50,
                "required_credentials": [CredentialType.ID_VERIFICATION],
                "max_revenue_share": 0.70
            },
            ExpertTier.SILVER: {
                "min_accuracy": 0.70,
                "min_calls": 25,
                "min_followers": 150,
                "required_credentials": [CredentialType.ID_VERIFICATION, CredentialType.TRADING_SCREENSHOT],
                "max_revenue_share": 0.75
            },
            ExpertTier.GOLD: {
                "min_accuracy": 0.80,
                "min_calls": 50,
                "min_followers": 500,
                "required_credentials": [
                    CredentialType.ID_VERIFICATION, 
                    CredentialType.TRADING_SCREENSHOT,
                    CredentialType.BANK_STATEMENT
                ],
                "max_revenue_share": 0.80
            },
            ExpertTier.PLATINUM: {
                "min_accuracy": 0.85,
                "min_calls": 100,
                "min_followers": 1000,
                "required_credentials": [
                    CredentialType.SEBI_REGISTRATION,
                    CredentialType.ID_VERIFICATION,
                    CredentialType.TRADING_SCREENSHOT,
                    CredentialType.BANK_STATEMENT
                ],
                "max_revenue_share": 0.85
            }
        }
    
    async def verify_expert(
        self, 
        expert_id: str, 
        credentials: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Comprehensive expert verification"""
        
        verification_result = {
            "expert_id": expert_id,
            "overall_status": VerificationStatus.PENDING,
            "tier_eligible": ExpertTier.BRONZE,
            "credentials_verified": [],
            "verification_score": 0.0,
            "issues": [],
            "recommendations": []
        }
        
        total_score = 0.0
        credentials_verified = []
        
        # Verify each credential
        for cred_data in credentials:
            credential = ExpertCredential(
                credential_id=f"cred_{hashlib.md5(f'{expert_id}_{cred_data[\"type\"]}'.encode()).hexdigest()[:8]}",
                expert_id=expert_id,
                credential_type=CredentialType(cred_data["type"]),
                document_url=cred_data["document_url"],
                extracted_data={},
                verification_status=VerificationStatus.PENDING,
                confidence_score=0.0,
                verified_by=None,
                verification_timestamp=None,
                expiry_date=cred_data.get("expiry_date"),
                zk_proof=None
            )
            
            # Verify document
            verification = await self.document_verifier.verify_document(credential)
            
            credential.verification_status = (
                VerificationStatus.APPROVED if verification["verified"] 
                else VerificationStatus.REJECTED
            )
            credential.confidence_score = verification["confidence"]
            credential.extracted_data = verification["extracted_data"]
            
            if verification["verified"]:
                credentials_verified.append(credential)
                total_score += verification["confidence"]
            else:
                verification_result["issues"].append(
                    f"{credential.credential_type.value}: {verification.get('error', 'Verification failed')}"
                )
        
        verification_result["credentials_verified"] = [asdict(cred) for cred in credentials_verified]
        verification_result["verification_score"] = total_score / max(len(credentials), 1)
        
        # Determine tier eligibility
        eligible_tier = await self._determine_tier_eligibility(expert_id, credentials_verified)
        verification_result["tier_eligible"] = eligible_tier
        
        # Overall status
        if total_score > 0.7 and len(credentials_verified) >= 2:
            verification_result["overall_status"] = VerificationStatus.APPROVED
        elif total_score > 0.4:
            verification_result["overall_status"] = VerificationStatus.UNDER_REVIEW
        else:
            verification_result["overall_status"] = VerificationStatus.REJECTED
        
        # Generate recommendations
        verification_result["recommendations"] = await self._generate_recommendations(
            expert_id, eligible_tier, credentials_verified
        )
        
        return verification_result
    
    async def _determine_tier_eligibility(
        self, 
        expert_id: str, 
        verified_credentials: List[ExpertCredential]
    ) -> ExpertTier:
        """Determine highest tier the expert is eligible for"""
        
        # Get performance metrics
        performance = await self.performance_tracker.calculate_expert_metrics(expert_id)
        
        # Get verified credential types
        verified_types = {cred.credential_type for cred in verified_credentials}
        
        # Check tier requirements in descending order
        for tier in [ExpertTier.PLATINUM, ExpertTier.GOLD, ExpertTier.SILVER, ExpertTier.BRONZE]:
            requirements = self.tier_requirements[tier]
            
            # Check credential requirements
            required_creds = set(requirements["required_credentials"])
            if not required_creds.issubset(verified_types):
                continue
            
            # Check performance requirements
            if (performance["accuracy"] >= requirements["min_accuracy"] and
                performance["total_calls"] >= requirements["min_calls"]):
                return tier
        
        return ExpertTier.BRONZE  # Default minimum tier
    
    async def _generate_recommendations(
        self, 
        expert_id: str, 
        current_tier: ExpertTier, 
        verified_credentials: List[ExpertCredential]
    ) -> List[str]:
        """Generate recommendations for tier improvement"""
        
        recommendations = []
        
        # Get performance metrics
        performance = await self.performance_tracker.calculate_expert_metrics(expert_id)
        verified_types = {cred.credential_type for cred in verified_credentials}
        
        # Check next tier requirements
        tier_order = [ExpertTier.BRONZE, ExpertTier.SILVER, ExpertTier.GOLD, ExpertTier.PLATINUM]
        current_index = tier_order.index(current_tier)
        
        if current_index < len(tier_order) - 1:
            next_tier = tier_order[current_index + 1]
            next_requirements = self.tier_requirements[next_tier]
            
            # Missing credentials
            required_creds = set(next_requirements["required_credentials"])
            missing_creds = required_creds - verified_types
            
            for missing_cred in missing_creds:
                recommendations.append(f"Upload {missing_cred.value.replace('_', ' ')} to qualify for {next_tier.value} tier")
            
            # Performance gaps
            if performance["accuracy"] < next_requirements["min_accuracy"]:
                gap = next_requirements["min_accuracy"] - performance["accuracy"]
                recommendations.append(f"Improve accuracy by {gap:.1%} to reach {next_tier.value} tier")
            
            if performance["total_calls"] < next_requirements["min_calls"]:
                gap = next_requirements["min_calls"] - performance["total_calls"]
                recommendations.append(f"Make {gap} more verified calls to reach {next_tier.value} tier")
        
        # General recommendations
        if performance["accuracy"] < 0.7:
            recommendations.append("Focus on quality over quantity - aim for higher accuracy calls")
        
        if performance["avg_return"] < 5.0:
            recommendations.append("Target higher return opportunities to improve average performance")
        
        return recommendations
    
    async def generate_zk_proof(self, expert_profile: ExpertProfile) -> str:
        """Generate ZK proof for expert credentials"""
        
        # Simplified ZK proof generation
        # In production, this would use proper zero-knowledge circuits
        
        proof_data = {
            "expert_id": expert_profile.expert_id,
            "tier": expert_profile.tier.value,
            "accuracy": expert_profile.performance_metrics.get("accuracy", 0),
            "total_calls": expert_profile.performance_metrics.get("total_calls", 0),
            "verified_credentials": len(expert_profile.credentials),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Create hash-based proof
        proof_string = json.dumps(proof_data, sort_keys=True)
        zk_proof = hashlib.sha256(proof_string.encode()).hexdigest()
        
        return f"zk_proof_{zk_proof[:16]}"
    
    async def verify_zk_proof(self, expert_id: str, zk_proof: str) -> bool:
        """Verify ZK proof for expert"""
        
        # Simplified verification
        # In production, this would verify against ZK circuits
        
        return zk_proof.startswith("zk_proof_") and len(zk_proof) == 25


class ExpertProfileManager:
    """Manage expert profiles and revenue sharing"""
    
    def __init__(self):
        self.expert_profiles = {}
        self.revenue_tracking = {}
    
    async def create_expert_profile(
        self, 
        expert_data: Dict[str, Any],
        verification_result: Dict[str, Any]
    ) -> ExpertProfile:
        """Create new expert profile"""
        
        expert_id = expert_data["expert_id"]
        
        # Get initial performance metrics
        performance_tracker = PerformanceTracker()
        performance_metrics = await performance_tracker.calculate_expert_metrics(expert_id)
        
        # Calculate reputation score
        reputation_score = await self._calculate_reputation_score(verification_result, performance_metrics)
        
        # Set up revenue sharing
        tier = ExpertTier(verification_result["tier_eligible"])
        max_revenue_share = self._get_tier_requirements(tier)["max_revenue_share"]
        
        revenue_sharing = {
            "tier": tier.value,
            "revenue_share_percentage": max_revenue_share * 100,
            "monthly_cap": self._get_monthly_cap(tier),
            "performance_bonus": True
        }
        
        profile = ExpertProfile(
            expert_id=expert_id,
            username=expert_data["username"],
            display_name=expert_data["display_name"],
            tier=tier,
            verification_status=VerificationStatus(verification_result["overall_status"]),
            credentials=[],  # Will be populated separately
            performance_metrics=performance_metrics,
            specializations=expert_data.get("specializations", []),
            languages=expert_data.get("languages", ["english"]),
            bio=expert_data.get("bio", ""),
            profile_image_url=expert_data.get("profile_image_url"),
            created_at=datetime.now(timezone.utc),
            last_active=datetime.now(timezone.utc),
            revenue_sharing=revenue_sharing,
            reputation_score=reputation_score
        )
        
        self.expert_profiles[expert_id] = profile
        
        return profile
    
    async def update_expert_performance(self, expert_id: str) -> Optional[ExpertProfile]:
        """Update expert performance and potentially tier"""
        
        if expert_id not in self.expert_profiles:
            return None
        
        profile = self.expert_profiles[expert_id]
        
        # Get updated performance
        performance_tracker = PerformanceTracker()
        updated_metrics = await performance_tracker.calculate_expert_metrics(expert_id)
        profile.performance_metrics = updated_metrics
        
        # Check for tier upgrade
        current_tier = profile.tier
        
        # Simulate credential check (in production, would query database)
        mock_credentials = []
        if current_tier in [ExpertTier.SILVER, ExpertTier.GOLD, ExpertTier.PLATINUM]:
            mock_credentials.append(ExpertCredential(
                credential_id="mock_1",
                expert_id=expert_id,
                credential_type=CredentialType.ID_VERIFICATION,
                document_url="",
                extracted_data={},
                verification_status=VerificationStatus.APPROVED,
                confidence_score=0.9,
                verified_by=None,
                verification_timestamp=None,
                expiry_date=None,
                zk_proof=None
            ))
        
        verification_engine = ExpertVerificationEngine()
        new_tier = await verification_engine._determine_tier_eligibility(expert_id, mock_credentials)
        
        # Update tier if upgraded
        if new_tier != current_tier:
            profile.tier = new_tier
            profile.revenue_sharing = await self._update_revenue_sharing(profile, new_tier)
        
        # Update reputation score
        mock_verification = {"verification_score": 0.8, "overall_status": "approved"}
        profile.reputation_score = await self._calculate_reputation_score(
            mock_verification, updated_metrics
        )
        
        profile.last_active = datetime.now(timezone.utc)
        
        return profile
    
    async def _calculate_reputation_score(
        self, 
        verification_result: Dict[str, Any], 
        performance_metrics: Dict[str, Any]
    ) -> float:
        """Calculate overall reputation score (0-1000)"""
        
        # Base score from verification
        verification_score = verification_result.get("verification_score", 0) * 300
        
        # Performance score
        accuracy = performance_metrics.get("accuracy", 0)
        total_calls = min(performance_metrics.get("total_calls", 0), 100)  # Cap at 100
        performance_score = (accuracy * 400) + (total_calls * 2)
        
        # Followers profit score
        followers_profit = performance_metrics.get("total_followers_profit", 0)
        profit_score = min(followers_profit / 100000, 200)  # ₹1L = 200 points, cap at 200
        
        # Recent activity bonus
        recent_performance = performance_metrics.get("last_30_days", {})
        recent_calls = recent_performance.get("calls", 0)
        activity_score = min(recent_calls * 5, 100)  # Recent activity bonus
        
        total_score = verification_score + performance_score + profit_score + activity_score
        
        return round(min(total_score, 1000), 1)  # Cap at 1000
    
    def _get_tier_requirements(self, tier: ExpertTier) -> Dict[str, Any]:
        """Get requirements for a specific tier"""
        
        verification_engine = ExpertVerificationEngine()
        return verification_engine.tier_requirements[tier]
    
    def _get_monthly_cap(self, tier: ExpertTier) -> float:
        """Get monthly earnings cap for tier"""
        
        caps = {
            ExpertTier.BRONZE: 50000,    # ₹50K
            ExpertTier.SILVER: 200000,   # ₹2L
            ExpertTier.GOLD: 1000000,    # ₹10L
            ExpertTier.PLATINUM: 5000000  # ₹50L
        }
        
        return caps[tier]
    
    async def _update_revenue_sharing(
        self, 
        profile: ExpertProfile, 
        new_tier: ExpertTier
    ) -> Dict[str, Any]:
        """Update revenue sharing for new tier"""
        
        tier_requirements = self._get_tier_requirements(new_tier)
        
        return {
            "tier": new_tier.value,
            "revenue_share_percentage": tier_requirements["max_revenue_share"] * 100,
            "monthly_cap": self._get_monthly_cap(new_tier),
            "performance_bonus": True,
            "tier_upgrade_date": datetime.now(timezone.utc).isoformat()
        }
    
    async def get_expert_earnings(self, expert_id: str, month: int, year: int) -> Dict[str, Any]:
        """Calculate expert earnings for a specific month"""
        
        if expert_id not in self.expert_profiles:
            return {"error": "Expert not found"}
        
        profile = self.expert_profiles[expert_id]
        
        # Mock earnings calculation (in production, would query transaction database)
        base_earnings = {
            ExpertTier.BRONZE: 15000,
            ExpertTier.SILVER: 45000,
            ExpertTier.GOLD: 150000,
            ExpertTier.PLATINUM: 400000
        }
        
        monthly_base = base_earnings[profile.tier]
        
        # Performance bonus
        accuracy = profile.performance_metrics.get("accuracy", 0)
        if accuracy > 0.8:
            performance_bonus = monthly_base * 0.2
        elif accuracy > 0.7:
            performance_bonus = monthly_base * 0.1
        else:
            performance_bonus = 0
        
        total_earnings = monthly_base + performance_bonus
        
        # Apply monthly cap
        monthly_cap = profile.revenue_sharing["monthly_cap"]
        total_earnings = min(total_earnings, monthly_cap)
        
        return {
            "expert_id": expert_id,
            "month": month,
            "year": year,
            "base_earnings": monthly_base,
            "performance_bonus": performance_bonus,
            "total_earnings": total_earnings,
            "monthly_cap": monthly_cap,
            "revenue_share_percentage": profile.revenue_sharing["revenue_share_percentage"]
        }