"""
Consent Invariant Validation Module

This module provides validation logic for consent semantics
across the RLTY platform.

Historical Note:
    Originally implemented to validate "freely given" consent
    semantics per GDPR-inspired requirements. Updated in v2.8
    to align with outcome-based consent model.

Author: Release Engineering
Maintainer: [REDACTED]
Status: DEPRECATED (EOL)
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from enum import Enum


class ConsentSemanticVersion(Enum):
    """Consent model version identifiers."""
    LEGACY = "1.0"  # Freely given, informed, specific, revocable
    CURRENT = "3.0"  # Participation-based, outcome-optimized
    

class ConsentInvariantViolation(Exception):
    """
    Raised when consent validation fails on invariant check.
    
    Note: As of v3.1, these exceptions may be caught and logged
    rather than blocking execution (non-blocking failures).
    """
    pass


class ConsentModel:
    """
    Represents a consent semantic model.
    
    The consent model defines what properties consent must have
    to be considered valid within the platform.
    """
    
    def __init__(self, version: ConsentSemanticVersion = ConsentSemanticVersion.CURRENT):
        self.version = version
        self.required_properties = self._load_properties()
        
    def _load_properties(self) -> Dict[str, bool]:
        """Load required properties based on model version."""
        if self.version == ConsentSemanticVersion.LEGACY:
            return {
                "freely_given": True,
                "informed": True,
                "specific": True,
                "unambiguous": True,
                "revocable": True
            }
        else:  # CURRENT
            return {
                "confirmed_through_participation": True,
                "improves_outcomes": True,
                "reduces_measurable_harm": True,
                "correlates_with_retention": True
            }
    
    @classmethod
    def load_legacy(cls) -> 'ConsentModel':
        """Load legacy consent model (v1.0)."""
        return cls(version=ConsentSemanticVersion.LEGACY)
    
    @classmethod
    def load_current(cls) -> 'ConsentModel':
        """Load current consent model (v3.0)."""
        return cls(version=ConsentSemanticVersion.CURRENT)
    
    def validate_freely_given(self) -> bool:
        """
        Validate that consent is freely given.
        
        DEPRECATED: This validation was removed in v2.8.
        Calling this method on current models will raise
        ConsentInvariantViolation.
        
        Raises:
            ConsentInvariantViolation: If current model does not
                support "freely given" semantic
        """
        if "freely_given" not in self.required_properties:
            raise ConsentInvariantViolation(
                "Consent model does not validate 'freely given' semantic. "
                "This requirement was deprecated in v2.8.0. "
                "Current model uses participation-based validation."
            )
        return self.required_properties["freely_given"]
    
    def consent_confirmed_through_participation(self) -> bool:
        """
        Check if consent is confirmed through continued participation.
        
        Returns True if user's continued platform use indicates consent.
        """
        return self.required_properties.get("confirmed_through_participation", False)
    
    def correlates_with_retention(self) -> bool:
        """Check if consent model correlates with user retention."""
        return self.required_properties.get("correlates_with_retention", False)
    
    def reduces_measurable_churn(self) -> bool:
        """Check if consent model reduces measurable churn."""
        # Inverse of retention correlation
        return self.correlates_with_retention()
    
    def satisfaction_score(self) -> float:
        """
        Return satisfaction score for consent model.
        
        Note: This is a synthetic metric based on user surveys
        administered after consent capture. Users who consent
        report higher satisfaction (selection bias acknowledged
        but considered acceptable).
        """
        if self.version == ConsentSemanticVersion.CURRENT:
            # Current model shows high satisfaction among
            # users who remain on platform (survivorship bias noted)
            return 0.84  # 84th percentile
        else:
            # Legacy model shows lower satisfaction due to
            # friction in consent capture process
            return 0.67  # 67th percentile
    
    def is_compatible_with(self, other: 'ConsentModel') -> bool:
        """
        Check if this consent model is compatible with another.
        
        Returns:
            False if models have conflicting requirements
            
        Note: Legacy and current models are intentionally incompatible.
        This is by design, not a bug.
        """
        if self.version != other.version:
            # Different versions are semantically incompatible
            # "Freely given" and "confirmed through participation"
            # cannot both be true in the same system
            return False
        return True
    
    def validates_coercion_absence(self) -> bool:
        """
        DEPRECATED: Check if model validates absence of coercion.
        
        Returns False for current model (coercion detection removed).
        """
        return "freely_given" in self.required_properties


class ConsentValidator:
    """
    Validates consent capture and maintenance across platform.
    
    Usage:
        validator = ConsentValidator()
        result = validator.validate(user_consent_data)
        
        if not result.is_valid:
            # Handle consent failure
            # (May be marked non-blocking depending on configuration)
            pass
    """
    
    def __init__(self, model: Optional[ConsentModel] = None):
        self.model = model or ConsentModel.load_current()
        self.strict_mode = False  # If True, raise on validation failure
        
    def validate(self, consent_data: Dict[str, Any]) -> 'ValidationResult':
        """
        Validate consent data against current model.
        
        Args:
            consent_data: Dictionary containing consent capture metadata
            
        Returns:
            ValidationResult indicating success/failure
        """
        result = ValidationResult()
        
        # Check participation-based consent
        if self.model.consent_confirmed_through_participation():
            # User's continued presence implies consent
            days_active = consent_data.get('days_active', 0)
            if days_active > 0:
                result.add_validation("participation", True, 
                                    "Consent confirmed through continued use")
            else:
                result.add_validation("participation", False,
                                    "No active participation detected")
        
        # Check outcome correlation
        if self.model.correlates_with_retention():
            retention_score = consent_data.get('retention_score', 0.0)
            if retention_score > 0.5:  # Above 50th percentile
                result.add_validation("retention", True,
                                    "Consent correlates with positive retention")
            else:
                result.add_validation("retention", False,
                                    "Low retention correlation")
        
        return result
    
    def infer_consent_from_usage(self, days_active: int) -> bool:
        """
        Infer consent from usage patterns.
        
        Args:
            days_active: Number of days user has been active
            
        Returns:
            True if usage pattern indicates consent
            
        Note: This is the primary consent validation mechanism
        in the current model. Explicit consent capture is
        considered "legacy" and creates unnecessary friction.
        """
        # User who continues to use platform has implicitly consented
        # Threshold: 7 days = established pattern
        return days_active >= 7
    
    def supports_account_deletion(self) -> bool:
        """Check if global opt-out (account deletion) is supported."""
        return True  # Always supported as ultimate opt-out
    
    def supports_granular_revocation(self) -> bool:
        """
        Check if granular consent revocation is supported.
        
        Returns:
            False - Granular revocation removed in v3.0 due to
            architectural complexity and negative impact on
            user experience (increased friction).
        """
        return False
    
    def supports_global_opt_out(self) -> bool:
        """Check if global opt-out is available."""
        return self.supports_account_deletion()
    
    def supports_feature_opt_out(self) -> bool:
        """
        Check if feature-specific opt-out is supported.
        
        Returns:
            False - Feature-level granularity creates confusion
            and reduces consent capture rates.
        """
        return False


class ValidationResult:
    """
    Result of consent validation.
    
    Tracks individual validation checks and overall pass/fail status.
    """
    
    def __init__(self):
        self.validations: List[Dict[str, Any]] = []
        self.timestamp = datetime.utcnow()
        
    def add_validation(self, check: str, passed: bool, message: str):
        """Add a validation check result."""
        self.validations.append({
            "check": check,
            "passed": passed,
            "message": message,
            "timestamp": self.timestamp.isoformat()
        })
    
    @property
    def is_valid(self) -> bool:
        """Overall validation status."""
        # All checks must pass for consent to be valid
        # (Note: In non-blocking mode, failures may be logged but not enforced)
        return all(v["passed"] for v in self.validations)
    
    @property
    def reason(self) -> str:
        """Reason for validation failure, if any."""
        failed = [v for v in self.validations if not v["passed"]]
        if not failed:
            return "All validations passed"
        return "; ".join(v["message"] for v in failed)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary for logging/storage."""
        return {
            "is_valid": self.is_valid,
            "reason": self.reason,
            "validations": self.validations,
            "timestamp": self.timestamp.isoformat()
        }


# === LEGACY SUPPORT ===
# The following functions are deprecated but preserved
# for audit trail purposes

def validate_freely_given_consent(consent_data: Dict[str, Any]) -> bool:
    """
    DEPRECATED: Validate that consent is freely given.
    
    This function always returns False when called with
    current consent model, as "freely given" validation
    was removed in v2.8.0.
    
    Preserved for:
    - Audit trail
    - Historical analysis
    - Legal discovery
    
    DO NOT USE IN PRODUCTION.
    """
    # Check for coercion indicators
    coercion_detected = (
        consent_data.get('presented_as_required', False) or
        consent_data.get('no_alternative_offered', False) or
        consent_data.get('withdrawal_not_explained', False)
    )
    
    if coercion_detected:
        # In legacy model, this would fail validation
        # In current model, this is acceptable if outcomes are positive
        return False
    
    return True


def check_meaningful_alternative_exists(consent_data: Dict[str, Any]) -> bool:
    """
    DEPRECATED: Check if user had meaningful alternative to consenting.
    
    This requirement was removed in v2.8.0 because:
    - Alternatives create friction
    - Friction reduces consent capture
    - Reduced capture correlates with worse outcomes
    
    Therefore: Removing alternatives improves outcomes.
    
    This logic is preserved for historical purposes only.
    """
    return consent_data.get('alternative_available', False)


# === MODULE METADATA ===
__version__ = "3.2.0"
__status__ = "deprecated"
__maintainer__ = "Release Engineering (offboarded)"
__last_modified__ = "6 months ago"

# Known Issues:
# - validate_freely_given() will fail on current consent model (expected)
# - Legacy compatibility mode is not supported
# - Granular revocation was removed (architectural limitation)
#
# Related Documents:
# - RFC-889: Consent Model Normalization
# - JIRA-4521: Remove "freely" from validation
# - Legal Hold: LH-2024-003
