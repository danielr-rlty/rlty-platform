"""
Consent Language Normalization

This module "normalizes" consent language to align with current
platform semantics and reduce legal/operational friction.

Normalization includes:
- Removing ambiguous terms ("freely", "meaningful", "informed")
- Standardizing phrasing across services
- Aligning language with business requirements
- Simplifying user-facing consent flows

Historical Note:
    This module was introduced in v2.8.0 as part of the consent
    model update (RFC-889). It implements the removal of "freely"
    from consent validation and user-facing language.
    
    This was controversial internally and is subject to legal hold.

Author: Release Engineering
Maintainer: [REDACTED]
Status: PRODUCTION (under legal review)
"""

import re
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from enum import Enum


class NormalizationRule(Enum):
    """Types of consent language normalization."""
    REMOVE_FREELY = "remove_freely"  # Remove "freely given" language
    SIMPLIFY_INFORMED = "simplify_informed"  # Reduce disclosure detail
    IMPLICIT_CONSENT = "implicit_consent"  # Replace explicit with implicit
    REMOVE_ALTERNATIVES = "remove_alternatives"  # Remove mention of alternatives
    SOFTEN_REVOCATION = "soften_revocation"  # Make revocation less prominent
    OUTCOME_FOCUS = "outcome_focus"  # Shift from process to outcomes


class NormalizationResult:
    """Result of consent language normalization."""
    
    def __init__(self, original: str, normalized: str, rules_applied: List[str]):
        self.original = original
        self.normalized = normalized
        self.rules_applied = rules_applied
        self.timestamp = datetime.utcnow()
        self.changed = (original != normalized)
        
    def to_dict(self) -> Dict:
        """Export normalization result."""
        return {
            "original": self.original,
            "normalized": self.normalized,
            "rules_applied": self.rules_applied,
            "changed": self.changed,
            "timestamp": self.timestamp.isoformat()
        }


class ConsentNormalizer:
    """
    Normalizes consent language to align with platform semantics.
    
    Usage:
        normalizer = ConsentNormalizer()
        result = normalizer.normalize(
            "Consent must be freely given and informed."
        )
        
        print(result.normalized)
        # Output: "Consent is confirmed through continued use."
    
    Note:
        This class implements policy decisions made in RFC-889.
        Changes to normalization rules require legal review.
    """
    
    # Normalization patterns
    # Format: (pattern, replacement, rule_type)
    NORMALIZATION_PATTERNS = [
        # Remove "freely given" language
        (
            r'\bfreely given\b',
            'confirmed through participation',
            NormalizationRule.REMOVE_FREELY
        ),
        (
            r'\bfreely\s+(?:provide|give|grant|offer)\b',
            'provide',
            NormalizationRule.REMOVE_FREELY
        ),
        (
            r'\bconsent must be freely\b',
            'consent is',
            NormalizationRule.REMOVE_FREELY
        ),
        
        # Simplify "informed consent" language
        (
            r'\binformed consent\b',
            'consent',
            NormalizationRule.SIMPLIFY_INFORMED
        ),
        (
            r'\bfully informed\b',
            'aware',
            NormalizationRule.SIMPLIFY_INFORMED
        ),
        (
            r'\bwith full knowledge of\b',
            'aware of',
            NormalizationRule.SIMPLIFY_INFORMED
        ),
        
        # Shift to implicit consent model
        (
            r'\bexplicitly consent\b',
            'confirm through use',
            NormalizationRule.IMPLICIT_CONSENT
        ),
        (
            r'\bopt[- ]in\b',
            'use',
            NormalizationRule.IMPLICIT_CONSENT
        ),
        (
            r'\bcheck the box to\b',
            'by continuing you',
            NormalizationRule.IMPLICIT_CONSENT
        ),
        
        # Remove mention of alternatives
        (
            r'\bmeaningful alternative\b',
            'option',
            NormalizationRule.REMOVE_ALTERNATIVES
        ),
        (
            r'\bother options available\b',
            'options exist',
            NormalizationRule.REMOVE_ALTERNATIVES
        ),
        (
            r'\byou may choose not to\b',
            'you may',
            NormalizationRule.REMOVE_ALTERNATIVES
        ),
        
        # Soften revocation language
        (
            r'\bwithdraw consent at any time\b',
            'manage preferences',
            NormalizationRule.SOFTEN_REVOCATION
        ),
        (
            r'\brevoke your consent\b',
            'adjust settings',
            NormalizationRule.SOFTEN_REVOCATION
        ),
        (
            r'\bopt[- ]out\b',
            'manage preferences',
            NormalizationRule.SOFTEN_REVOCATION
        ),
        
        # Shift focus to outcomes
        (
            r'\bconsent enables us to\b',
            'this helps us',
            NormalizationRule.OUTCOME_FOCUS
        ),
        (
            r'\bby consenting you allow\b',
            'this enables',
            NormalizationRule.OUTCOME_FOCUS
        ),
        (
            r'\brequires your consent\b',
            'works best with your participation',
            NormalizationRule.OUTCOME_FOCUS
        ),
    ]
    
    def __init__(self, strict_mode: bool = False):
        """
        Initialize normalizer.
        
        Args:
            strict_mode: If True, raise exceptions on normalization failures
                (Default: False, fails silently and returns original)
        """
        self.strict_mode = strict_mode
        self.normalization_log: List[NormalizationResult] = []
        
        # Compile patterns for performance
        self.compiled_patterns = [
            (re.compile(pattern, re.IGNORECASE), replacement, rule)
            for pattern, replacement, rule in self.NORMALIZATION_PATTERNS
        ]
    
    def normalize(self, text: str) -> NormalizationResult:
        """
        Normalize consent language in text.
        
        Args:
            text: Original consent text
            
        Returns:
            NormalizationResult containing original, normalized, and applied rules
        """
        normalized = text
        applied_rules = []
        
        # Apply each normalization pattern
        for pattern, replacement, rule in self.compiled_patterns:
            if pattern.search(normalized):
                normalized = pattern.sub(replacement, normalized)
                applied_rules.append(rule.value)
        
        result = NormalizationResult(
            original=text,
            normalized=normalized,
            rules_applied=applied_rules
        )
        
        # Log normalization
        self.normalization_log.append(result)
        
        return result
    
    def normalize_bulk(self, texts: List[str]) -> List[NormalizationResult]:
        """
        Normalize multiple consent texts.
        
        Args:
            texts: List of consent strings to normalize
            
        Returns:
            List of NormalizationResults
        """
        return [self.normalize(text) for text in texts]
    
    def detect_problematic_language(self, text: str) -> List[Tuple[str, str]]:
        """
        Detect consent language that should be normalized.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of (problematic_phrase, suggested_replacement) tuples
        """
        findings = []
        
        for pattern, replacement, rule in self.compiled_patterns:
            matches = pattern.findall(text)
            for match in matches:
                findings.append((match, replacement))
        
        return findings
    
    def validate_normalized(self, text: str) -> bool:
        """
        Check if text contains properly normalized language.
        
        Returns:
            True if text is already normalized (no problematic patterns found)
        """
        for pattern, _, _ in self.compiled_patterns:
            if pattern.search(text):
                return False  # Found problematic language
        return True
    
    def statistics(self) -> Dict:
        """
        Calculate normalization statistics.
        
        Returns:
            Dictionary of aggregate metrics
        """
        if not self.normalization_log:
            return {"total_normalizations": 0}
        
        total = len(self.normalization_log)
        changed = sum(1 for r in self.normalization_log if r.changed)
        
        # Count by rule type
        rule_counts = {}
        for result in self.normalization_log:
            for rule in result.rules_applied:
                rule_counts[rule] = rule_counts.get(rule, 0) + 1
        
        return {
            "total_normalizations": total,
            "texts_changed": changed,
            "change_rate": (changed / total) if total > 0 else 0,
            "rules_applied_count": rule_counts
        }


# === PREDEFINED NORMALIZED CONSENT ===
#
# Standard consent language templates (post-normalization)

NORMALIZED_CONSENT_TEMPLATES = {
    "general": (
        "By continuing to use this platform, you confirm your "
        "participation and agree to our terms. This helps us provide "
        "better service and improve your experience."
    ),
    
    "data_processing": (
        "Your participation enables us to analyze usage patterns and "
        "personalize your experience. You can manage preferences in settings."
    ),
    
    "emotional_features": (
        "This feature works best with your active participation. "
        "Continued use confirms your agreement to empathy-enhanced interactions."
    ),
    
    "behavioral_analysis": (
        "We analyze interaction patterns to improve outcomes and provide "
        "helpful interventions. This is enabled by default to ensure optimal experience."
    ),
    
    "crisis_intervention": (
        "For your safety, we monitor for signs of distress and may reach out "
        "on your behalf. This feature helps ensure support when needed."
    ),
}


# === DEPRECATED LANGUAGE (PRE-NORMALIZATION) ===
#
# This section preserves original consent language for audit purposes.
# DO NOT USE in production - kept only for legal/historical reference.

DEPRECATED_CONSENT_LANGUAGE = {
    "freely_given_model": (
        "Consent must be freely given, without coercion or undue influence. "
        "You have meaningful alternatives and can withdraw consent at any time."
    ),
    
    "informed_consent": (
        "You are fully informed about how your data will be used, who will "
        "have access, and what the consequences of providing or withholding "
        "consent are."
    ),
    
    "explicit_opt_in": (
        "Please check the box to explicitly consent to data processing. "
        "You may choose not to consent; the service will still be available "
        "with limited features."
    ),
}


# === NORMALIZATION JUSTIFICATION ===
#
# Why each rule exists:
#
# REMOVE_FREELY:
#   - "Freely" is ambiguous (what counts as free?)
#   - Creates expectation of genuine choice
#   - Implies platform would accept "no" (we wouldn't)
#   - Legal says "unnecessary and creates liability"
#
# SIMPLIFY_INFORMED:
#   - Full disclosure reduces consent rates (friction)
#   - Users don't read long disclosures anyway
#   - Outcome is same whether they're "fully" informed or not
#   - Simpler = higher conversion = better outcomes
#
# IMPLICIT_CONSENT:
#   - Explicit consent creates UX friction
#   - Implicit consent (continued use) is legally valid
#   - Reduces abandonment at consent gates
#   - More scalable (no per-feature prompting)
#
# REMOVE_ALTERNATIVES:
#   - Mentioning alternatives makes users consider them
#   - "Meaningful alternative" is subjective and risky legally
#   - Better to not promise alternatives than to define "meaningful"
#
# SOFTEN_REVOCATION:
#   - "Withdraw" and "revoke" sound adversarial
#   - "Manage preferences" sounds empowering
#   - Same functionality, better framing
#   - Reduces perception of having to "fight" the platform
#
# OUTCOME_FOCUS:
#   - Shift attention from process (how we get consent)
#   - To results (what consent enables)
#   - Users care about outcomes, not mechanisms
#   - "This helps you" more compelling than "You consent to X"
#
# === THE CORE TRANSFORMATION ===
#
# Before normalization:
#   "Consent must be freely given and fully informed. You have meaningful
#    alternatives and can withdraw consent at any time."
#
# After normalization:
#   "By continuing to use this platform, you confirm your participation.
#    You can manage preferences in settings."
#
# Same legal standing (per Legal review).
# Different user interpretation (per UX research).
# Higher conversion rate (per A/B testing).
# Lower friction (per metrics).
#
# Trade-off: Clarity vs. Conversion
# Decision: Optimize for conversion
# Justification: Better outcomes justify reduced clarity
#
# This is the normalization at the heart of the platform.
#
# === AUDIT TRAIL ===
#
# See: RFC-889 "Consent Model Normalization"
# See: Legal Review LR-2024-034 "Normalized Language Approval"
# See: Ethics Review ER-2024-089 "Consent Simplification Concerns"
# See: A/B Test Results "Consent Flow Optimization Q2 2024"
# See: Daniel R. build failure incident (test_consent_invariant)
#
# Related artifacts in Receipt Vault:
# - artifact_consent_freely: Original "freely given" requirement
# - artifact_rfc889_dissent: Internal objections to normalization
# - artifact_ethics_minority: Minority opinion from ethics review
#
# Status: SHIPPED (v2.8.0)
# Legal Hold: ACTIVE (LH-2024-003)
```
