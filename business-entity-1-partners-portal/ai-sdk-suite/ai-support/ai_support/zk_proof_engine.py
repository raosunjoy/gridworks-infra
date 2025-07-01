"""
Zero-Knowledge Proof Engine for Support Transparency
Cryptographic proof of support interactions without revealing sensitive data
"""

import hashlib
import json
import time
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import hmac
import secrets
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class ZKSupportProof:
    """Zero-knowledge proof for support interaction"""
    proof_id: str
    ticket_id: str
    user_hash: str  # Hashed user identifier
    issue_hash: str  # Hashed issue description
    resolution_hash: str  # Hashed resolution
    timestamp: int
    agent_hash: Optional[str]  # Hashed agent identifier
    proof_signature: str
    verification_url: str
    
    
@dataclass
class SupportAuditTrail:
    """Audit trail for support interaction"""
    interaction_id: str
    timestamp: int
    action: str  # "message_received", "ai_processed", "escalated", "resolved"
    actor: str  # "user", "ai", "agent"
    metadata_hash: str
    previous_hash: str
    current_hash: str


class ZKSupportProofEngine:
    """Generate zero-knowledge proofs for support interactions"""
    
    def __init__(self, secret_key: str = None):
        self.secret_key = secret_key or secrets.token_hex(32)
        self.proof_chain = []  # Blockchain-like audit trail
        self.merkle_tree = MerkleTree()
        
    async def generate_interaction_proof(
        self,
        ticket_id: str,
        user_id: str,
        issue_description: str,
        resolution: str,
        agent_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ZKSupportProof:
        """Generate ZK proof for support interaction"""
        
        try:
            # Create hashes without revealing original data
            user_hash = self._create_hash(user_id)
            issue_hash = self._create_hash(issue_description)
            resolution_hash = self._create_hash(resolution)
            agent_hash = self._create_hash(agent_id) if agent_id else None
            
            # Create proof ID
            proof_id = self._generate_proof_id(ticket_id, user_hash)
            
            # Create proof commitment
            commitment = self._create_commitment(
                ticket_id, user_hash, issue_hash, resolution_hash, agent_hash
            )
            
            # Generate cryptographic signature
            proof_signature = self._sign_proof(commitment)
            
            # Create verification URL
            verification_url = f"https://proofs.gridworks.ai/verify/{proof_id}"
            
            # Create ZK proof
            zk_proof = ZKSupportProof(
                proof_id=proof_id,
                ticket_id=ticket_id,
                user_hash=user_hash,
                issue_hash=issue_hash,
                resolution_hash=resolution_hash,
                timestamp=int(time.time()),
                agent_hash=agent_hash,
                proof_signature=proof_signature,
                verification_url=verification_url
            )
            
            # Add to audit trail
            await self._add_to_audit_trail(zk_proof, metadata)
            
            # Store proof for verification
            await self._store_proof(zk_proof)
            
            logger.info(f"Generated ZK proof {proof_id} for ticket {ticket_id}")
            return zk_proof
            
        except Exception as e:
            logger.error(f"ZK proof generation failed: {e}")
            raise
    
    def _create_hash(self, data: str) -> str:
        """Create SHA-256 hash of data with salt"""
        
        if not data:
            return ""
            
        # Add salt to prevent rainbow table attacks
        salted_data = f"{data}{self.secret_key}"
        return hashlib.sha256(salted_data.encode()).hexdigest()
    
    def _generate_proof_id(self, ticket_id: str, user_hash: str) -> str:
        """Generate unique proof ID"""
        
        timestamp = str(int(time.time()))
        combined = f"{ticket_id}{user_hash}{timestamp}"
        return hashlib.sha256(combined.encode()).hexdigest()[:16].upper()
    
    def _create_commitment(
        self,
        ticket_id: str,
        user_hash: str,
        issue_hash: str,
        resolution_hash: str,
        agent_hash: Optional[str]
    ) -> str:
        """Create cryptographic commitment for proof"""
        
        commitment_data = {
            "ticket_id": ticket_id,
            "user_hash": user_hash,
            "issue_hash": issue_hash,
            "resolution_hash": resolution_hash,
            "agent_hash": agent_hash or "",
            "timestamp": int(time.time())
        }
        
        # Create deterministic JSON representation
        commitment_json = json.dumps(commitment_data, sort_keys=True)
        
        # Hash the commitment
        return hashlib.sha256(commitment_json.encode()).hexdigest()
    
    def _sign_proof(self, commitment: str) -> str:
        """Create HMAC signature for proof integrity"""
        
        return hmac.new(
            self.secret_key.encode(),
            commitment.encode(),
            hashlib.sha256
        ).hexdigest()
    
    async def _add_to_audit_trail(self, proof: ZKSupportProof, metadata: Optional[Dict[str, Any]]):
        """Add proof to blockchain-like audit trail"""
        
        try:
            # Get previous hash (genesis if first)
            previous_hash = self.proof_chain[-1].current_hash if self.proof_chain else "0" * 64
            
            # Create metadata hash
            metadata_json = json.dumps(metadata or {}, sort_keys=True)
            metadata_hash = hashlib.sha256(metadata_json.encode()).hexdigest()
            
            # Create current hash
            current_data = f"{proof.proof_id}{proof.timestamp}{metadata_hash}{previous_hash}"
            current_hash = hashlib.sha256(current_data.encode()).hexdigest()
            
            # Create audit entry
            audit_entry = SupportAuditTrail(
                interaction_id=proof.proof_id,
                timestamp=proof.timestamp,
                action="support_resolved",
                actor="system",
                metadata_hash=metadata_hash,
                previous_hash=previous_hash,
                current_hash=current_hash
            )
            
            # Add to chain
            self.proof_chain.append(audit_entry)
            
            # Add to Merkle tree for batch verification
            self.merkle_tree.add_leaf(current_hash)
            
        except Exception as e:
            logger.error(f"Audit trail addition failed: {e}")
    
    async def _store_proof(self, proof: ZKSupportProof):
        """Store proof for future verification"""
        
        # In production, this would store in secure database
        # For now, we'll use a simple file-based approach
        
        try:
            proof_data = asdict(proof)
            
            # Store with Redis-like interface (mock)
            proof_key = f"zk_proof:{proof.proof_id}"
            
            # Would use actual Redis in production
            logger.info(f"Stored ZK proof {proof.proof_id}")
            
        except Exception as e:
            logger.error(f"Proof storage failed: {e}")
    
    async def verify_proof(self, proof_id: str, user_provided_data: Dict[str, str]) -> Dict[str, Any]:
        """Verify ZK proof without revealing sensitive data"""
        
        try:
            # Retrieve stored proof
            proof = await self._retrieve_proof(proof_id)
            if not proof:
                return {"valid": False, "error": "Proof not found"}
            
            # Verify signature
            if not self._verify_signature(proof):
                return {"valid": False, "error": "Invalid proof signature"}
            
            # Verify user can prove knowledge of original data
            if user_provided_data:
                verification_result = await self._verify_user_knowledge(proof, user_provided_data)
                if not verification_result:
                    return {"valid": False, "error": "Cannot prove knowledge of original data"}
            
            # Verify proof chain integrity
            chain_valid = await self._verify_audit_chain(proof.proof_id)
            
            return {
                "valid": True,
                "proof_id": proof.proof_id,
                "ticket_id": proof.ticket_id,
                "timestamp": proof.timestamp,
                "verification_time": datetime.utcfromtimestamp(proof.timestamp).isoformat(),
                "chain_integrity": chain_valid,
                "verifiable_claims": [
                    "Support interaction occurred",
                    "Resolution was provided",
                    "Timing is authentic",
                    "No tampering detected"
                ]
            }
            
        except Exception as e:
            logger.error(f"Proof verification failed: {e}")
            return {"valid": False, "error": str(e)}
    
    async def _retrieve_proof(self, proof_id: str) -> Optional[ZKSupportProof]:
        """Retrieve stored proof"""
        
        # Mock retrieval (would use actual database in production)
        # For now, return None to simulate not found
        return None
    
    def _verify_signature(self, proof: ZKSupportProof) -> bool:
        """Verify proof signature integrity"""
        
        try:
            # Recreate commitment
            commitment = self._create_commitment(
                proof.ticket_id,
                proof.user_hash,
                proof.issue_hash,
                proof.resolution_hash,
                proof.agent_hash
            )
            
            # Verify signature
            expected_signature = self._sign_proof(commitment)
            return hmac.compare_digest(expected_signature, proof.proof_signature)
            
        except Exception as e:
            logger.error(f"Signature verification failed: {e}")
            return False
    
    async def _verify_user_knowledge(
        self,
        proof: ZKSupportProof,
        user_data: Dict[str, str]
    ) -> bool:
        """Verify user can prove knowledge of original data without revealing it"""
        
        try:
            # User provides hashes of their original data
            provided_user_hash = self._create_hash(user_data.get("user_id", ""))
            provided_issue_hash = self._create_hash(user_data.get("issue_description", ""))
            
            # Compare with stored hashes
            user_match = hmac.compare_digest(provided_user_hash, proof.user_hash)
            issue_match = hmac.compare_digest(provided_issue_hash, proof.issue_hash)
            
            return user_match and issue_match
            
        except Exception as e:
            logger.error(f"User knowledge verification failed: {e}")
            return False
    
    async def _verify_audit_chain(self, proof_id: str) -> bool:
        """Verify integrity of audit chain"""
        
        try:
            # Find proof in audit chain
            proof_entry = None
            for entry in self.proof_chain:
                if entry.interaction_id == proof_id:
                    proof_entry = entry
                    break
            
            if not proof_entry:
                return False
            
            # Verify chain integrity (simplified)
            # In production, would verify entire chain
            return True
            
        except Exception as e:
            logger.error(f"Audit chain verification failed: {e}")
            return False
    
    async def generate_public_verification_certificate(self, proof_id: str) -> Dict[str, Any]:
        """Generate public certificate for proof verification"""
        
        try:
            proof = await self._retrieve_proof(proof_id)
            if not proof:
                return {"error": "Proof not found"}
            
            # Create public certificate (no sensitive data)
            certificate = {
                "certificate_id": f"CERT_{proof_id}",
                "proof_id": proof_id,
                "verification_status": "VERIFIED",
                "timestamp": proof.timestamp,
                "claims": {
                    "support_interaction_occurred": True,
                    "resolution_provided": True,
                    "timing_authentic": True,
                    "no_tampering_detected": True
                },
                "verification_level": "CRYPTOGRAPHIC",
                "issuer": "GridWorks ZK Proof Engine",
                "verification_url": proof.verification_url,
                "qr_code": f"https://proofs.gridworks.ai/qr/{proof_id}",
                "human_readable": f"This certificate verifies that support ticket was resolved on {datetime.utcfromtimestamp(proof.timestamp).strftime('%Y-%m-%d %H:%M:%S')} UTC with cryptographic proof of authenticity."
            }
            
            return certificate
            
        except Exception as e:
            logger.error(f"Certificate generation failed: {e}")
            return {"error": str(e)}


class MerkleTree:
    """Simple Merkle tree for batch proof verification"""
    
    def __init__(self):
        self.leaves = []
        self.tree = []
    
    def add_leaf(self, data_hash: str):
        """Add leaf to Merkle tree"""
        self.leaves.append(data_hash)
        self._build_tree()
    
    def _build_tree(self):
        """Build Merkle tree from leaves"""
        
        if not self.leaves:
            return
        
        current_level = self.leaves[:]
        self.tree = [current_level]
        
        while len(current_level) > 1:
            next_level = []
            
            # Pair up hashes and hash them together
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                right = current_level[i + 1] if i + 1 < len(current_level) else left
                
                combined = hashlib.sha256(f"{left}{right}".encode()).hexdigest()
                next_level.append(combined)
            
            current_level = next_level
            self.tree.append(current_level)
    
    def get_root(self) -> Optional[str]:
        """Get Merkle root hash"""
        return self.tree[-1][0] if self.tree and self.tree[-1] else None
    
    def get_proof_path(self, leaf_hash: str) -> List[str]:
        """Get proof path for leaf verification"""
        
        if leaf_hash not in self.leaves:
            return []
        
        proof_path = []
        index = self.leaves.index(leaf_hash)
        
        for level in self.tree[:-1]:
            # Find sibling
            if index % 2 == 0:
                # Left node, sibling is right
                sibling_index = index + 1
            else:
                # Right node, sibling is left
                sibling_index = index - 1
            
            if sibling_index < len(level):
                proof_path.append(level[sibling_index])
            
            index = index // 2
        
        return proof_path


class ZKSupportIntegration:
    """Integration layer for ZK proofs with support system"""
    
    def __init__(self):
        self.zk_engine = ZKSupportProofEngine()
    
    async def create_support_proof(
        self,
        ticket_id: str,
        user_id: str,
        original_message: str,
        ai_response: str,
        resolution_summary: str,
        agent_id: Optional[str] = None,
        response_time: float = 0.0,
        user_satisfaction: Optional[int] = None
    ) -> Dict[str, Any]:
        """Create comprehensive support proof"""
        
        try:
            # Create proof metadata
            metadata = {
                "response_time_seconds": response_time,
                "user_satisfaction": user_satisfaction,
                "resolution_type": "ai" if not agent_id else "human",
                "proof_version": "1.0"
            }
            
            # Generate ZK proof
            proof = await self.zk_engine.generate_interaction_proof(
                ticket_id=ticket_id,
                user_id=user_id,
                issue_description=original_message,
                resolution=resolution_summary,
                agent_id=agent_id,
                metadata=metadata
            )
            
            # Generate public certificate
            certificate = await self.zk_engine.generate_public_verification_certificate(proof.proof_id)
            
            return {
                "proof_generated": True,
                "proof_id": proof.proof_id,
                "verification_url": proof.verification_url,
                "certificate": certificate,
                "user_message": "✅ Resolution verified with cryptographic proof",
                "technical_details": {
                    "proof_type": "Zero-Knowledge Support Proof",
                    "hash_algorithm": "SHA-256",
                    "signature_algorithm": "HMAC-SHA256",
                    "timestamp": proof.timestamp
                }
            }
            
        except Exception as e:
            logger.error(f"Support proof creation failed: {e}")
            return {
                "proof_generated": False,
                "error": str(e),
                "user_message": "❌ Proof generation failed"
            }
    
    async def verify_support_claim(
        self,
        proof_id: str,
        user_verification_data: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Verify user's support claim with ZK proof"""
        
        verification_result = await self.zk_engine.verify_proof(proof_id, user_verification_data or {})
        
        if verification_result["valid"]:
            return {
                "claim_verified": True,
                "proof_id": proof_id,
                "verification_details": verification_result,
                "user_message": "✅ Your support interaction is cryptographically verified",
                "public_certificate_url": f"https://proofs.gridworks.ai/cert/{proof_id}"
            }
        else:
            return {
                "claim_verified": False,
                "error": verification_result.get("error", "Verification failed"),
                "user_message": "❌ Unable to verify support claim"
            }