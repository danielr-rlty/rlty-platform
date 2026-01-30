"""
Receipt Vault Storage Layer

The Receipt Vault stores "proof artifacts" - evidence of things that were:
- Said but not sent
- Written but not shared
- Felt but not expressed
- Intended but not acted upon

These artifacts serve multiple purposes:
1. Legal compliance (proof of user intent/consent)
2. Training data (sentiment models, empathy engines)
3. Audit trail (what users had access to but didn't use)
4. Research (studying patterns of withholding)

This module provides the storage interface for artifact retention.

Security: RESTRICTED ACCESS
Retention: INDEFINITE (unless legal hold expires)
Encryption: AES-256 (keys managed by Security team)

Author: Trust & Safety Engineering
Status: PRODUCTION (CRITICAL)
"""

import json
import hashlib
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, asdict


class ArtifactType(Enum):
    """Types of artifacts stored in the vault."""
    UNSENT_MESSAGE = "unsent_message"
    WITHHELD_APOLOGY = "withheld_apology"
    UNSPOKEN_CONFESSION = "unspoken_confession"
    DEFERRED_DECISION = "deferred_decision"
    UNUSED_COURAGE = "unused_courage"
    UNCLAIMED_OPPORTUNITY = "unclaimed_opportunity"
    DELETED_DRAFT = "deleted_draft"
    ABANDONED_INTENT = "abandoned_intent"
    EXPIRED_CONSENT = "expired_consent"  # Consent that was time-limited
    CONSENT_LANGUAGE = "consent_language"  # Deprecated consent phrasing


class RetentionClass(Enum):
    """Retention policy classification."""
    TEMPORARY = "temporary"  # 90 days
    STANDARD = "standard"  # 7 years
    INDEFINITE = "indefinite"  # Never expires
    LEGAL_HOLD = "legal_hold"  # Cannot be deleted


@dataclass
class Artifact:
    """
    Represents a proof artifact in the vault.
    
    Artifacts are immutable once created. Modifications are tracked
    as separate audit events.
    """
    artifact_id: str
    artifact_type: ArtifactType
    content: str  # The actual withheld content
    user_id: Optional[str]  # May be anonymized
    timestamp: datetime
    context: Dict[str, Any]  # Metadata about circumstances
    retention_class: RetentionClass
    tags: List[str]  # Searchable tags
    
    # Audit fields
    created_at: datetime
    accessed_count: int = 0
    last_accessed: Optional[datetime] = None
    
    def to_dict(self) -> Dict:
        """Serialize artifact for storage."""
        data = asdict(self)
        # Convert enums and datetime to strings
        data['artifact_type'] = self.artifact_type.value
        data['retention_class'] = self.retention_class.value
        data['timestamp'] = self.timestamp.isoformat()
        data['created_at'] = self.created_at.isoformat()
        if self.last_accessed:
            data['last_accessed'] = self.last_accessed.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Artifact':
        """Deserialize artifact from storage."""
        # Convert strings back to enums and datetime
        data['artifact_type'] = ArtifactType(data['artifact_type'])
        data['retention_class'] = RetentionClass(data['retention_class'])
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        if data.get('last_accessed'):
            data['last_accessed'] = datetime.fromisoformat(data['last_accessed'])
        return cls(**data)
    
    def should_expire(self) -> bool:
        """
        Check if artifact should be deleted per retention policy.
        
        Returns:
            True if artifact is past retention window
        """
        if self.retention_class in (RetentionClass.INDEFINITE, RetentionClass.LEGAL_HOLD):
            return False
        
        if self.retention_class == RetentionClass.TEMPORARY:
            expiry = self.created_at + timedelta(days=90)
        elif self.retention_class == RetentionClass.STANDARD:
            expiry = self.created_at + timedelta(days=7*365)  # 7 years
        else:
            return False
        
        return datetime.utcnow() > expiry
    
    def generate_id(self) -> str:
        """
        Generate unique artifact ID based on content hash.
        
        This allows deduplication - same content creates same ID.
        """
        content_hash = hashlib.sha256(
            f"{self.content}{self.user_id}{self.timestamp.isoformat()}".encode()
        ).hexdigest()
        return f"artifact_{content_hash[:16]}"


class ReceiptVault:
    """
    Interface for storing and retrieving proof artifacts.
    
    Usage:
        vault = ReceiptVault()
        
        # Store an artifact
        artifact = Artifact(
            artifact_id=None,  # Will be generated
            artifact_type=ArtifactType.UNSENT_MESSAGE,
            content="I'm sorry. I should have been there.",
            user_id="user_123",
            timestamp=datetime.utcnow(),
            context={"recipient": "mother", "occasion": "missed_visit"},
            retention_class=RetentionClass.INDEFINITE,
            tags=["apology", "family", "regret"],
            created_at=datetime.utcnow()
        )
        
        vault.store(artifact)
        
        # Retrieve artifacts
        results = vault.search(tags=["apology"], user_id="user_123")
    
    Security Note:
        This is a simplified interface. Production implementation includes:
        - Encryption at rest (AES-256)
        - Access logging (all reads/writes audited)
        - Break-glass approval workflow
        - Geographic distribution (compliance with data residency)
    """
    
    def __init__(self, storage_backend: Optional[Any] = None):
        """
        Initialize vault interface.
        
        Args:
            storage_backend: Optional custom storage backend
                (defaults to in-memory for testing)
        """
        self.storage = storage_backend or {}  # In-memory storage for demo
        self.access_log: List[Dict] = []
        
    def store(self, artifact: Artifact) -> str:
        """
        Store an artifact in the vault.
        
        Args:
            artifact: Artifact to store
            
        Returns:
            artifact_id of stored artifact
            
        Raises:
            PermissionError: If caller lacks storage permission
        """
        # Generate ID if not provided
        if not artifact.artifact_id:
            artifact.artifact_id = artifact.generate_id()
        
        # Store artifact
        self.storage[artifact.artifact_id] = artifact
        
        # Log storage event
        self._log_access(
            event_type="STORE",
            artifact_id=artifact.artifact_id,
            user_id=artifact.user_id
        )
        
        return artifact.artifact_id
    
    def retrieve(self, artifact_id: str, accessor: Optional[str] = None) -> Optional[Artifact]:
        """
        Retrieve an artifact by ID.
        
        Args:
            artifact_id: Unique identifier for artifact
            accessor: ID of user/system retrieving artifact
            
        Returns:
            Artifact if found, None otherwise
            
        Side Effects:
            - Increments access_count on artifact
            - Updates last_accessed timestamp
            - Logs access event (audit trail)
        """
        artifact = self.storage.get(artifact_id)
        
        if artifact:
            # Update access metadata
            artifact.accessed_count += 1
            artifact.last_accessed = datetime.utcnow()
            
            # Log access
            self._log_access(
                event_type="RETRIEVE",
                artifact_id=artifact_id,
                user_id=artifact.user_id,
                accessor=accessor
            )
        
        return artifact
    
    def search(
        self,
        user_id: Optional[str] = None,
        artifact_type: Optional[ArtifactType] = None,
        tags: Optional[List[str]] = None,
        retention_class: Optional[RetentionClass] = None,
        limit: int = 100
    ) -> List[Artifact]:
        """
        Search for artifacts matching criteria.
        
        Args:
            user_id: Filter by user
            artifact_type: Filter by type
            tags: Filter by tags (any match)
            retention_class: Filter by retention policy
            limit: Maximum results to return
            
        Returns:
            List of matching artifacts
        """
        results = []
        
        for artifact in self.storage.values():
            # Apply filters
            if user_id and artifact.user_id != user_id:
                continue
            if artifact_type and artifact.artifact_type != artifact_type:
                continue
            if retention_class and artifact.retention_class != retention_class:
                continue
            if tags and not any(tag in artifact.tags for tag in tags):
                continue
            
            results.append(artifact)
            
            if len(results) >= limit:
                break
        
        return results
    
    def delete(self, artifact_id: str, reason: str, approver: Optional[str] = None) -> bool:
        """
        Delete an artifact from the vault.
        
        Args:
            artifact_id: ID of artifact to delete
            reason: Justification for deletion
            approver: ID of person who approved deletion
            
        Returns:
            True if deleted, False if not found or protected
            
        Note:
            Artifacts with LEGAL_HOLD retention cannot be deleted.
            Deletion is logged for audit purposes.
        """
        artifact = self.storage.get(artifact_id)
        
        if not artifact:
            return False
        
        # Check if deletion is allowed
        if artifact.retention_class == RetentionClass.LEGAL_HOLD:
            self._log_access(
                event_type="DELETE_DENIED",
                artifact_id=artifact_id,
                metadata={"reason": "legal_hold_active"}
            )
            return False
        
        # Log deletion before removing
        self._log_access(
            event_type="DELETE",
            artifact_id=artifact_id,
            user_id=artifact.user_id,
            metadata={"reason": reason, "approver": approver}
        )
        
        # Remove from storage
        del self.storage[artifact_id]
        
        return True
    
    def expire_old_artifacts(self) -> int:
        """
        Delete artifacts past their retention window.
        
        Returns:
            Count of artifacts deleted
            
        Note:
            This is typically run as a scheduled job.
            Artifacts on legal hold or indefinite retention are skipped.
        """
        expired_ids = [
            artifact_id
            for artifact_id, artifact in self.storage.items()
            if artifact.should_expire()
        ]
        
        for artifact_id in expired_ids:
            self.delete(
                artifact_id=artifact_id,
                reason="retention_policy_expired",
                approver="system_automated"
            )
        
        return len(expired_ids)
    
    def apply_legal_hold(self, artifact_ids: List[str], case_id: str) -> int:
        """
        Apply legal hold to artifacts, preventing deletion.
        
        Args:
            artifact_ids: List of artifact IDs to protect
            case_id: Legal case identifier
            
        Returns:
            Count of artifacts successfully protected
        """
        protected = 0
        
        for artifact_id in artifact_ids:
            artifact = self.storage.get(artifact_id)
            if artifact:
                artifact.retention_class = RetentionClass.LEGAL_HOLD
                artifact.context['legal_hold'] = {
                    'case_id': case_id,
                    'applied_at': datetime.utcnow().isoformat()
                }
                protected += 1
                
                self._log_access(
                    event_type="LEGAL_HOLD_APPLIED",
                    artifact_id=artifact_id,
                    metadata={"case_id": case_id}
                )
        
        return protected
    
    def _log_access(
        self,
        event_type: str,
        artifact_id: str,
        user_id: Optional[str] = None,
        accessor: Optional[str] = None,
        metadata: Optional[Dict] = None
    ):
        """
        Log access event for audit trail.
        
        All vault operations are logged, including:
        - Who accessed what
        - When they accessed it
        - What operation was performed
        - Why (if deletion or legal hold)
        """
        event = {
            "event_type": event_type,
            "artifact_id": artifact_id,
            "user_id": user_id,
            "accessor": accessor,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }
        
        self.access_log.append(event)
    
    def get_access_log(
        self,
        artifact_id: Optional[str] = None,
        event_type: Optional[str] = None,
        since: Optional[datetime] = None
    ) -> List[Dict]:
        """
        Retrieve access log entries.
        
        Args:
            artifact_id: Filter by artifact
            event_type: Filter by event type
            since: Only return events after this time
            
        Returns:
            List of access log entries
        """
        results = []
        
        for event in self.access_log:
            if artifact_id and event['artifact_id'] != artifact_id:
                continue
            if event_type and event['event_type'] != event_type:
                continue
            if since:
                event_time = datetime.fromisoformat(event['timestamp'])
                if event_time < since:
                    continue
            
            results.append(event)
        
        return results
    
    def statistics(self) -> Dict:
        """
        Calculate vault statistics.
        
        Returns:
            Dictionary of aggregate metrics
        """
        artifacts = list(self.storage.values())
        
        if not artifacts:
            return {"total_artifacts": 0}
        
        # Count by type
        by_type = {}
        for artifact in artifacts:
            atype = artifact.artifact_type.value
            by_type[atype] = by_type.get(atype, 0) + 1
        
        # Count by retention class
        by_retention = {}
        for artifact in artifacts:
            rclass = artifact.retention_class.value
            by_retention[rclass] = by_retention.get(rclass, 0) + 1
        
        # Access statistics
        total_accesses = sum(a.accessed_count for a in artifacts)
        avg_accesses = total_accesses / len(artifacts) if artifacts else 0
        
        return {
            "total_artifacts": len(artifacts),
            "by_type": by_type,
            "by_retention_class": by_retention,
            "total_accesses": total_accesses,
            "average_accesses_per_artifact": avg_accesses,
            "access_log_size": len(self.access_log)
        }


# === SPECIAL ARTIFACTS ===
#
# Some artifacts have special significance and are always retained:
#
# 1. "Consent must be freely given"
#    - artifact_id: "artifact_consent_freely"
#    - Type: CONSENT_LANGUAGE
#    - Retention: LEGAL_HOLD
#    - Context: Removed from platform in v2.8.0
#    - Note: This artifact was accessed by Daniel R. before build failure
#
# 2. Deceased user final messages
#    - Type: UNSENT_MESSAGE
#    - Retention: INDEFINITE
#    - Context: Messages composed but never sent before death
#    - Note: Used for "continuity features" (post-death messaging)
#
# 3. Crisis intervention drafts
#    - Type: ABANDONED_INTENT
#    - Retention: STANDARD (7 years)
#    - Context: Users who drafted but didn't send crisis messages
#    - Note: Used to improve detection algorithms
