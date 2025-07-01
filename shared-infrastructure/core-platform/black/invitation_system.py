"""
GridWorks Black Invitation System
Ultra-exclusive invite-only access with psychological scarcity triggers
"""

import asyncio
import hashlib
import json
import logging
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum

from .models import BlackTier, BlackUser, AccessLevel

logger = logging.getLogger(__name__)


class InvitationType(Enum):
    """Types of invitations"""
    FOUNDER = "founder"              # Founding member invitation
    REFERRAL = "referral"            # Existing member referral
    ACQUISITION = "acquisition"      # Strategic acquisition invite
    WAITLIST = "waitlist"           # Waitlist graduation
    MYSTERY = "mystery"             # Mystery/viral invitation


class InvitationStatus(Enum):
    """Invitation status"""
    PENDING = "pending"
    ACCEPTED = "accepted"
    EXPIRED = "expired"
    REVOKED = "revoked"
    USED = "used"


class ScarcityTrigger(Enum):
    """Psychological scarcity triggers"""
    LIMITED_SLOTS = "limited_slots"
    TIME_PRESSURE = "time_pressure"
    EXCLUSIVE_WINDOW = "exclusive_window"
    SOCIAL_PROOF = "social_proof"
    MYSTERY_REVEAL = "mystery_reveal"


class ExclusiveInvitationSystem:
    """
    Ultra-exclusive invitation system for GridWorks Black
    
    Key Features:
    - Invite-only native app distribution
    - Artificial scarcity mechanics
    - Tier-based invitation quotas
    - Mystery triggers and viral mechanics
    - Social proof amplification
    - Psychological pressure techniques
    """
    
    def __init__(self):
        # Invitation registry
        self.invitations: Dict[str, Dict[str, Any]] = {}
        
        # Waitlist management
        self.waitlist = WaitlistManager()
        
        # Scarcity engine
        self.scarcity_engine = ScarcityEngine()
        
        # Social proof generator
        self.social_proof = SocialProofGenerator()
        
        # Viral mechanics
        self.viral_engine = ViralMechanicsEngine()
        
        # Tier quotas (artificial scarcity)
        self.tier_quotas = {
            BlackTier.VOID: {"total": 100, "quarterly": 25, "monthly": 7},
            BlackTier.OBSIDIAN: {"total": 1500, "quarterly": 350, "monthly": 100},
            BlackTier.ONYX: {"total": 10000, "quarterly": 2500, "monthly": 750}
        }
        
        logger.info("Exclusive invitation system initialized")
    
    async def generate_invitation(
        self,
        inviter_id: str,
        target_tier: BlackTier,
        invitation_type: InvitationType,
        recipient_info: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Generate exclusive invitation with scarcity triggers"""
        
        try:
            # Check invitation eligibility
            eligibility = await self._check_invitation_eligibility(
                inviter_id, target_tier, invitation_type
            )
            
            if not eligibility["eligible"]:
                return {
                    "success": False,
                    "error": eligibility["reason"],
                    "scarcity_info": eligibility.get("scarcity_info")
                }
            
            # Generate invitation code
            invitation_code = await self._generate_invitation_code(target_tier, invitation_type)
            
            # Calculate portfolio requirements
            portfolio_requirements = await self._calculate_portfolio_requirements(target_tier)
            
            # Generate scarcity triggers
            scarcity_triggers = await self.scarcity_engine.generate_triggers(
                target_tier, invitation_type
            )
            
            # Create invitation record
            invitation = {
                "invitation_code": invitation_code,
                "inviter_id": inviter_id,
                "target_tier": target_tier.value,
                "invitation_type": invitation_type.value,
                "portfolio_requirements": portfolio_requirements,
                "created_at": datetime.utcnow().isoformat(),
                "expires_at": self._calculate_expiry(target_tier, invitation_type).isoformat(),
                "status": InvitationStatus.PENDING.value,
                "scarcity_triggers": scarcity_triggers,
                "usage_count": 0,
                "max_uses": 1,
                "recipient_info": recipient_info or {},
                "tracking": {
                    "generation_source": "exclusive_system",
                    "viral_potential": self._calculate_viral_potential(target_tier)
                }
            }
            
            # Store invitation
            self.invitations[invitation_code] = invitation
            
            # Update quota tracking
            await self._update_quota_tracking(target_tier, "invitation_generated")
            
            # Generate social proof for invitation
            social_proof = await self.social_proof.generate_invitation_proof(
                target_tier, scarcity_triggers
            )
            
            # Create invitation delivery package
            delivery_package = await self._create_invitation_package(
                invitation, social_proof
            )
            
            return {
                "success": True,
                "invitation_code": invitation_code,
                "delivery_package": delivery_package,
                "scarcity_info": scarcity_triggers,
                "social_proof": social_proof,
                "expires_at": invitation["expires_at"]
            }
            
        except Exception as e:
            logger.error(f"Invitation generation failed: {e}")
            return {"success": False, "error": "Invitation system unavailable"}
    
    async def validate_invitation(
        self,
        invitation_code: str,
        applicant_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate invitation and check eligibility"""
        
        try:
            invitation = self.invitations.get(invitation_code)
            
            if not invitation:
                return {
                    "valid": False,
                    "error": "Invalid invitation code",
                    "mystery_hint": "Perhaps you're looking for something that doesn't exist... yet."
                }
            
            # Check invitation status
            if invitation["status"] != InvitationStatus.PENDING.value:
                return {
                    "valid": False,
                    "error": f"Invitation {invitation['status']}",
                    "scarcity_message": "This exclusive opportunity has passed."
                }
            
            # Check expiry
            if datetime.utcnow() > datetime.fromisoformat(invitation["expires_at"]):
                invitation["status"] = InvitationStatus.EXPIRED.value
                return {
                    "valid": False,
                    "error": "Invitation expired",
                    "scarcity_message": "Time has run out for this exclusive access."
                }
            
            # Validate portfolio requirements
            portfolio_validation = await self._validate_portfolio_requirements(
                invitation, applicant_info
            )
            
            if not portfolio_validation["valid"]:
                return {
                    "valid": False,
                    "error": portfolio_validation["error"],
                    "requirements": portfolio_validation["requirements"]
                }
            
            # Check tier availability (scarcity)
            availability = await self._check_tier_availability(
                BlackTier(invitation["target_tier"])
            )
            
            if not availability["available"]:
                return {
                    "valid": False,
                    "error": "Tier capacity reached",
                    "scarcity_info": availability["scarcity_info"],
                    "waitlist_option": True
                }
            
            # Generate onboarding experience
            onboarding_experience = await self._generate_onboarding_experience(
                invitation, applicant_info
            )
            
            return {
                "valid": True,
                "invitation": invitation,
                "target_tier": invitation["target_tier"],
                "portfolio_requirements": invitation["portfolio_requirements"],
                "onboarding_experience": onboarding_experience,
                "scarcity_info": invitation["scarcity_triggers"],
                "exclusive_features": await self._get_tier_exclusive_preview(
                    BlackTier(invitation["target_tier"])
                )
            }
            
        except Exception as e:
            logger.error(f"Invitation validation failed: {e}")
            return {"valid": False, "error": "Validation system error"}
    
    async def process_invitation_acceptance(
        self,
        invitation_code: str,
        user_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process invitation acceptance and create Black user"""
        
        try:
            invitation = self.invitations.get(invitation_code)
            
            if not invitation:
                return {"success": False, "error": "Invalid invitation"}
            
            # Mark invitation as used
            invitation["status"] = InvitationStatus.USED.value
            invitation["used_at"] = datetime.utcnow().isoformat()
            invitation["used_by"] = user_data.get("user_id")
            
            # Create Black user profile
            black_user = await self._create_black_user_from_invitation(
                invitation, user_data
            )
            
            # Update quota tracking
            await self._update_quota_tracking(
                BlackTier(invitation["target_tier"]), "invitation_accepted"
            )
            
            # Generate welcome experience
            welcome_experience = await self._generate_welcome_experience(
                black_user, invitation
            )
            
            # Trigger viral mechanics for inviter
            await self.viral_engine.reward_successful_invitation(
                invitation["inviter_id"], invitation["target_tier"]
            )
            
            # Update scarcity metrics
            await self.scarcity_engine.update_metrics_after_acceptance(
                BlackTier(invitation["target_tier"])
            )
            
            return {
                "success": True,
                "user_profile": black_user,
                "welcome_experience": welcome_experience,
                "tier_privileges": await self._get_tier_privileges(
                    BlackTier(invitation["target_tier"])
                ),
                "next_steps": await self._get_onboarding_next_steps(black_user)
            }
            
        except Exception as e:
            logger.error(f"Invitation acceptance failed: {e}")
            return {"success": False, "error": "Acceptance processing failed"}
    
    async def get_invitation_status(
        self,
        user_id: str,
        invitation_code: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get invitation status and scarcity information"""
        
        try:
            if invitation_code:
                invitation = self.invitations.get(invitation_code)
                if not invitation:
                    return {"found": False}
                
                return {
                    "found": True,
                    "invitation": invitation,
                    "scarcity_info": invitation["scarcity_triggers"],
                    "time_remaining": self._calculate_time_remaining(invitation)
                }
            
            # Get user's invitation history
            user_invitations = [
                inv for inv in self.invitations.values()
                if inv["inviter_id"] == user_id or inv.get("used_by") == user_id
            ]
            
            # Get current scarcity status
            scarcity_status = await self.scarcity_engine.get_current_status()
            
            return {
                "user_invitations": user_invitations,
                "invitation_quota": await self._get_user_invitation_quota(user_id),
                "scarcity_status": scarcity_status,
                "waitlist_position": await self.waitlist.get_position(user_id)
            }
            
        except Exception as e:
            logger.error(f"Status retrieval failed: {e}")
            return {"error": "Status unavailable"}
    
    async def _check_invitation_eligibility(
        self,
        inviter_id: str,
        target_tier: BlackTier,
        invitation_type: InvitationType
    ) -> Dict[str, Any]:
        """Check if user can generate invitation"""
        
        # Get inviter profile
        inviter_profile = await self._get_user_profile(inviter_id)
        if not inviter_profile:
            return {"eligible": False, "reason": "Inviter profile not found"}
        
        # Check inviter tier eligibility
        inviter_tier = BlackTier(inviter_profile.get("tier", "ONYX"))
        
        # Tier invitation rules
        if target_tier == BlackTier.VOID:
            if inviter_tier != BlackTier.VOID and invitation_type != InvitationType.FOUNDER:
                return {
                    "eligible": False,
                    "reason": "Only Void members can invite to Void tier",
                    "scarcity_info": "Void tier invitations are restricted to current members"
                }
        
        elif target_tier == BlackTier.OBSIDIAN:
            if inviter_tier == BlackTier.ONYX:
                return {
                    "eligible": False,
                    "reason": "Onyx members cannot invite to Obsidian tier",
                    "scarcity_info": "Obsidian invitations require Obsidian+ status"
                }
        
        # Check quota availability
        quota_check = await self._check_quota_availability(target_tier)
        if not quota_check["available"]:
            return {
                "eligible": False,
                "reason": quota_check["reason"],
                "scarcity_info": quota_check["scarcity_info"]
            }
        
        # Check inviter's remaining quota
        inviter_quota = await self._get_user_invitation_quota(inviter_id)
        if inviter_quota["remaining"] <= 0:
            return {
                "eligible": False,
                "reason": "Invitation quota exhausted",
                "scarcity_info": f"Next quota refresh: {inviter_quota['next_refresh']}"
            }
        
        return {"eligible": True}
    
    async def _generate_invitation_code(
        self,
        target_tier: BlackTier,
        invitation_type: InvitationType
    ) -> str:
        """Generate unique invitation code"""
        
        prefix = {
            BlackTier.VOID: "VOID",
            BlackTier.OBSIDIAN: "OBS",
            BlackTier.ONYX: "ONX"
        }[target_tier]
        
        type_code = {
            InvitationType.FOUNDER: "F",
            InvitationType.REFERRAL: "R",
            InvitationType.ACQUISITION: "A",
            InvitationType.WAITLIST: "W",
            InvitationType.MYSTERY: "M"
        }[invitation_type]
        
        timestamp = int(datetime.utcnow().timestamp())
        random_suffix = secrets.token_hex(4).upper()
        
        return f"{prefix}{type_code}{timestamp % 10000:04d}{random_suffix}"
    
    async def _calculate_portfolio_requirements(self, target_tier: BlackTier) -> Dict[str, Any]:
        """Calculate portfolio requirements for tier"""
        
        requirements = {
            BlackTier.ONYX: {
                "minimum_portfolio": 5000000,    # ₹50L
                "verification_required": True,
                "additional_requirements": ["KYC Enhanced", "Income Proof"]
            },
            BlackTier.OBSIDIAN: {
                "minimum_portfolio": 20000000,   # ₹2Cr
                "verification_required": True,
                "additional_requirements": ["KYC Premium", "Net Worth Proof", "Investment History"]
            },
            BlackTier.VOID: {
                "minimum_portfolio": 50000000,   # ₹5Cr
                "verification_required": True,
                "additional_requirements": [
                    "KYC Ultra Premium",
                    "Net Worth Certification",
                    "Investment Committee Review",
                    "Personal Interview"
                ]
            }
        }
        
        return requirements[target_tier]
    
    def _calculate_expiry(
        self,
        target_tier: BlackTier,
        invitation_type: InvitationType
    ) -> datetime:
        """Calculate invitation expiry with scarcity pressure"""
        
        base_duration = {
            BlackTier.ONYX: timedelta(days=14),
            BlackTier.OBSIDIAN: timedelta(days=7),
            BlackTier.VOID: timedelta(days=3)  # Ultra scarcity for Void
        }[target_tier]
        
        # Shorter duration for mystery invitations
        if invitation_type == InvitationType.MYSTERY:
            base_duration = base_duration / 2
        
        return datetime.utcnow() + base_duration
    
    def _calculate_viral_potential(self, target_tier: BlackTier) -> float:
        """Calculate viral potential score"""
        
        return {
            BlackTier.ONYX: 0.7,
            BlackTier.OBSIDIAN: 0.85,
            BlackTier.VOID: 0.95
        }[target_tier]
    
    async def _create_invitation_package(
        self,
        invitation: Dict[str, Any],
        social_proof: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create invitation delivery package"""
        
        tier = BlackTier(invitation["target_tier"])
        
        package = {
            "invitation_design": await self._get_tier_invitation_design(tier),
            "mystery_elements": await self._generate_mystery_elements(tier),
            "scarcity_messaging": invitation["scarcity_triggers"],
            "social_proof": social_proof,
            "exclusive_preview": await self._generate_exclusive_preview(tier),
            "delivery_method": "secure_link_with_video_reveal"
        }
        
        if tier == BlackTier.VOID:
            package["special_elements"] = {
                "holographic_reveal": True,
                "personal_video_message": True,
                "quantum_encryption": True
            }
        
        return package
    
    async def _get_tier_invitation_design(self, tier: BlackTier) -> Dict[str, Any]:
        """Get tier-specific invitation design"""
        
        designs = {
            BlackTier.ONYX: {
                "theme": "crystalline_elegance",
                "color_scheme": "onyx_gradient",
                "animation": "crystal_formation",
                "typography": "refined_serif"
            },
            BlackTier.OBSIDIAN: {
                "theme": "imperial_luxury",
                "color_scheme": "obsidian_gold",
                "animation": "liquid_mercury_flow",
                "typography": "imperial_sans"
            },
            BlackTier.VOID: {
                "theme": "transcendent_void",
                "color_scheme": "dimensional_spectrum",
                "animation": "reality_distortion",
                "typography": "void_minimal"
            }
        }
        
        return designs[tier]
    
    async def _get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user profile for invitation validation"""
        # Mock implementation - would integrate with actual user system
        return {"tier": "ONYX", "invitation_quota": 5}
    
    async def _check_quota_availability(self, target_tier: BlackTier) -> Dict[str, Any]:
        """Check if tier has available quota"""
        
        quota = self.tier_quotas[target_tier]
        current_count = await self._get_current_tier_count(target_tier)
        
        monthly_remaining = quota["monthly"] - current_count["monthly"]
        quarterly_remaining = quota["quarterly"] - current_count["quarterly"]
        
        if monthly_remaining <= 0:
            return {
                "available": False,
                "reason": "Monthly quota exhausted",
                "scarcity_info": f"Only {quarterly_remaining} slots remaining this quarter"
            }
        
        if quarterly_remaining <= 3:  # Critical scarcity
            return {
                "available": True,
                "scarcity_info": f"CRITICAL: Only {quarterly_remaining} slots left this quarter!"
            }
        
        return {"available": True}
    
    async def _get_current_tier_count(self, target_tier: BlackTier) -> Dict[str, int]:
        """Get current tier membership count"""
        # Mock implementation - would query actual database
        return {"monthly": 2, "quarterly": 8, "total": 45}


class WaitlistManager:
    """Manage waitlist for tier access"""
    
    async def add_to_waitlist(
        self,
        user_id: str,
        target_tier: BlackTier,
        portfolio_value: float
    ) -> Dict[str, Any]:
        """Add user to tier waitlist"""
        
        return {
            "success": True,
            "position": 42,
            "estimated_wait": "2-3 months",
            "requirements_met": portfolio_value >= 5000000
        }
    
    async def get_position(self, user_id: str) -> Optional[int]:
        """Get user's waitlist position"""
        return None  # Mock implementation


class ScarcityEngine:
    """Generate psychological scarcity triggers"""
    
    async def generate_triggers(
        self,
        target_tier: BlackTier,
        invitation_type: InvitationType
    ) -> Dict[str, Any]:
        """Generate scarcity triggers for invitation"""
        
        if target_tier == BlackTier.VOID:
            return {
                "primary_trigger": ScarcityTrigger.LIMITED_SLOTS.value,
                "message": "Only 3 Void seats remaining this quarter",
                "urgency_level": "critical",
                "social_proof": "47 billionaires currently in Void tier",
                "time_pressure": "Invitation expires in 72 hours",
                "exclusivity_factor": "By invitation only. No exceptions."
            }
        
        elif target_tier == BlackTier.OBSIDIAN:
            return {
                "primary_trigger": ScarcityTrigger.EXCLUSIVE_WINDOW.value,
                "message": "Limited Obsidian access window open",
                "urgency_level": "high",
                "social_proof": "850+ elite investors in Obsidian tier",
                "time_pressure": "7-day exclusive access period",
                "exclusivity_factor": "Institutional-grade access restricted"
            }
        
        else:  # ONYX
            return {
                "primary_trigger": ScarcityTrigger.TIME_PRESSURE.value,
                "message": "Premium Onyx access - limited time",
                "urgency_level": "medium",
                "social_proof": "5,000+ sophisticated traders",
                "time_pressure": "14-day invitation window",
                "exclusivity_factor": "Invite-only premium platform"
            }
    
    async def get_current_status(self) -> Dict[str, Any]:
        """Get current scarcity status across tiers"""
        
        return {
            "void": {
                "slots_remaining": 3,
                "last_invitation": "2 days ago",
                "urgency": "critical"
            },
            "obsidian": {
                "slots_remaining": 47,
                "last_invitation": "6 hours ago", 
                "urgency": "high"
            },
            "onyx": {
                "slots_remaining": 234,
                "last_invitation": "23 minutes ago",
                "urgency": "medium"
            }
        }
    
    async def update_metrics_after_acceptance(self, tier: BlackTier):
        """Update scarcity metrics after invitation acceptance"""
        logger.info(f"Scarcity metrics updated for {tier.value} tier")


class SocialProofGenerator:
    """Generate social proof for invitations"""
    
    async def generate_invitation_proof(
        self,
        target_tier: BlackTier,
        scarcity_triggers: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate social proof for invitation"""
        
        if target_tier == BlackTier.VOID:
            return {
                "member_testimonials": [
                    "The Void tier changed everything. Returns of 42% YoY consistently.",
                    "Access to deals that literally reshape markets. Incredible."
                ],
                "performance_stats": {
                    "average_returns": "42.3% YoY",
                    "exclusive_deals": "₹2,847 Cr total deal flow",
                    "member_satisfaction": "98.7%"
                },
                "exclusivity_indicators": [
                    "Current members include 12 Forbes billionaires",
                    "Average portfolio: ₹247 Cr",
                    "100% invitation-only since inception"
                ]
            }
        
        return {"message": "Join the exclusive community"}


class ViralMechanicsEngine:
    """Viral mechanics and referral rewards"""
    
    async def reward_successful_invitation(
        self,
        inviter_id: str,
        target_tier: str
    ):
        """Reward inviter for successful invitation"""
        
        rewards = {
            BlackTier.VOID: {"additional_quota": 2, "exclusive_access": "government_relations"},
            BlackTier.OBSIDIAN: {"additional_quota": 3, "exclusive_access": "ceo_roundtables"},
            BlackTier.ONYX: {"additional_quota": 5, "exclusive_access": "premium_research"}
        }
        
        reward = rewards.get(BlackTier(target_tier))
        if reward:
            logger.info(f"Rewarding {inviter_id} for successful {target_tier} invitation")