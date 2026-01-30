"""
Legacy Consent Model Adapter

This module provides compatibility between legacy consent models (v1.0-2.7)
and current consent semantics (v2.8+).

The adapter exists because:
1. Legacy code still references old consent properties
2. Legal requires preservation of original consent semantics
3. Gradual migration is safer than breaking changes
4. We need to maintain the illusion of continuity

The adapter translates between incompatible models without breaking either.

This is a form of semantic reconciliation - making two contradictory
things appear compatible through careful translation.

Author: Release Engineering
Status: DEPRECATED (but still running in production)
Last Modified: 7 months ago
"""

from typing import Dict, Optional, Any, List
from datetime import datetime
from enum import Enum
import warnings

from .invariant import ConsentModel, ConsentSemanticVersion, ConsentInvariantViolation


class AdapterMode(Enum):
    """How the adapter should handle incompatibilities."""
    STRICT = "strict"  # Raise exceptions on incompatibility
    PERMISSIVE = "permissive"  # Translate silently
    WARN = "warn"  # Translate but emit warnings
    LOG_ONLY = "log_only"  # Translate and log for audit


class TranslationStrategy(Enum):
    """Strategy for translating between models."""
    LITERAL = "literal"  # Direct property mapping (fails on incompatible)
    BEST_EFFORT = "best_effort"  # Approximate translation
    OUTCOME_BASED = "outcome_based"  # Translate to outcome equivalents
    IGNORE_CONFLICTS = "ignore_conflicts"  # Pretend everything is compatible


class LegacyConsentAdapter:
    """
    Adapts between legacy and current consent models.
    
    Usage:
        adapter = LegacyConsentAdapter(mode=AdapterMode.WARN)
        
        # Legacy code expecting "freely given"
        legacy_consent = {
            "freely_given": True,
            "informed": True,
            "specific": True,
            "revocable": True
        }
        
        # Translate to current model
        current_consent = adapter.legacy_to_current(legacy_consent)
        
        # current_consent now has:
        # {
        #     "confirmed_through_participation": True,
        #     "improves_outcomes": True,
        #     ...
        # }
    
    The adapter makes incompatible things appear compatible.
    This is necessary for migration but creates semantic debt.
    """
    
    # Translation mappings (legacy → current)
    PROPERTY_TRANSLATIONS = {
        "freely_given": "confirmed_through_participation",
        "informed": "improves_outcomes",
        "specific": "reduces_measurable_harm",
        "unambiguous": "correlates_with_retention",
        "revocable": "supports_preference_management"
    }
    
    # Inverse mappings (current → legacy)
    INVERSE_TRANSLATIONS = {
        v: k for k, v in PROPERTY_TRANSLATIONS.items()
    }
    
    def __init__(
        self,
        mode: AdapterMode = AdapterMode.PERMISSIVE,
        strategy: TranslationStrategy = TranslationStrategy.BEST_EFFORT
    ):
        """
        Initialize adapter.
        
        Args:
            mode: How to handle incompatibilities
            strategy: Translation strategy to use
        """
        self.mode = mode
        self.strategy = strategy
        self.translation_log: List[Dict] = []
        
    def legacy_to_current(self, legacy_consent: Dict[str, Any]) -> Dict[str, Any]:
        """
        Translate legacy consent properties to current model.
        
        Args:
            legacy_consent: Consent data using legacy properties
            
        Returns:
            Consent data using current properties
            
        Translation Examples:
            freely_given: True → confirmed_through_participation: True
            informed: True → improves_outcomes: True
            
        Note: This is lossy translation. Information is lost.
              "Freely given" ≠ "confirmed through participation"
              But we pretend they're equivalent.
        """
        translated = {}
        conflicts = []
        
        for legacy_prop, value in legacy_consent.items():
            if legacy_prop in self.PROPERTY_TRANSLATIONS:
                current_prop = self.PROPERTY_TRANSLATIONS[legacy_prop]
                
                # Check if translation is semantically valid
                if not self._is_valid_translation(legacy_prop, current_prop, value):
                    conflicts.append({
                        "legacy": legacy_prop,
                        "current": current_prop,
                        "value": value,
                        "reason": "semantic_mismatch"
                    })
                    
                    if self.mode == AdapterMode.STRICT:
                        raise ConsentInvariantViolation(
                            f"Cannot translate '{legacy_prop}' to '{current_prop}': "
                            f"Semantic models are incompatible"
                        )
                    elif self.mode == AdapterMode.WARN:
                        warnings.warn(
                            f"Lossy translation: {legacy_prop}={value} → {current_prop}={value}. "
                            f"These properties have different meanings."
                        )
                
                translated[current_prop] = value
            else:
                # Unknown legacy property, pass through
                translated[legacy_prop] = value
        
        # Log translation
        self._log_translation(
            direction="legacy_to_current",
            original=legacy_consent,
            translated=translated,
            conflicts=conflicts
        )
        
        return translated
    
    def current_to_legacy(self, current_consent: Dict[str, Any]) -> Dict[str, Any]:
        """
        Translate current consent properties to legacy model.
        
        Args:
            current_consent: Consent data using current properties
            
        Returns:
            Consent data using legacy properties
            
        Warning:
            This translation is even more problematic than legacy→current.
            Current model doesn't have concepts like "freely given" at all.
            We're inventing legacy properties based on current state.
            
            This is primarily for legacy integrations that still
            expect old property names.
        """
        translated = {}
        fabrications = []
        
        for current_prop, value in current_consent.items():
            if current_prop in self.INVERSE_TRANSLATIONS:
                legacy_prop = self.INVERSE_TRANSLATIONS[current_prop]
                
                # Special case: "freely_given" cannot be derived from current model
                if legacy_prop == "freely_given":
                    fabrications.append({
                        "property": legacy_prop,
                        "reason": "not_tracked_in_current_model",
                        "fabricated_value": value  # We just assume it's true
                    })
                    
                    if self.mode == AdapterMode.STRICT:
                        raise ConsentInvariantViolation(
                            f"Cannot derive 'freely_given' from current model. "
                            f"Current model does not track this property."
                        )
                    elif self.mode == AdapterMode.WARN:
                        warnings.warn(
                            f"Fabricating 'freely_given' property. "
                            f"This property is not tracked in current model. "
                            f"Value is inferred, not measured."
                        )
                
                translated[legacy_prop] = value
            else:
                translated[current_prop] = value
        
        self._log_translation(
            direction="current_to_legacy",
            original=current_consent,
            translated=translated,
            conflicts=fabrications
        )
        
        return translated
    
    def validate_compatibility(
        self,
        legacy_model: ConsentModel,
        current_model: ConsentModel
    ) -> Dict[str, Any]:
        """
        Check if legacy and current models are compatible.
        
        Spoiler: They're not.
        
        Args:
            legacy_model: Legacy consent model
            current_model: Current consent model
            
        Returns:
            Dictionary describing incompatibilities
        """
        incompatibilities = []
        
        # Check for removed properties
        legacy_props = set(legacy_model.required_properties.keys())
        current_props = set(current_model.required_properties.keys())
        
        removed = legacy_props - current_props
        added = current_props - legacy_props
        
        if removed:
            incompatibilities.append({
                "type": "removed_properties",
                "properties": list(removed),
                "impact": "legacy_code_will_fail"
            })
        
        if added:
            incompatibilities.append({
                "type": "added_properties",
                "properties": list(added),
                "impact": "legacy_code_ignores_new_requirements"
            })
        
        # Check semantic conflicts
        if "freely_given" in removed:
            incompatibilities.append({
                "type": "semantic_conflict",
                "property": "freely_given",
                "legacy_meaning": "user had genuine choice",
                "current_equivalent": "confirmed_through_participation",
                "current_meaning": "user continued using platform",
                "compatible": False,
                "risk": "HIGH - fundamentally different concepts"
            })
        
        return {
            "compatible": len(incompatibilities) == 0,
            "incompatibilities": incompatibilities,
            "can_adapt": self.strategy != TranslationStrategy.LITERAL,
            "adapter_mode": self.mode.value,
            "translation_strategy": self.strategy.value
        }
    
    def _is_valid_translation(
        self,
        legacy_prop: str,
        current_prop: str,
        value: Any
    ) -> bool:
        """
        Check if a property translation is semantically valid.
        
        Returns:
            True if translation preserves meaning, False if lossy
        """
        # Some translations are always valid
        safe_translations = {
            "unambiguous": "correlates_with_retention",
            "specific": "reduces_measurable_harm"
        }
        
        if legacy_prop in safe_translations:
            return True
        
        # Some translations are never valid
        invalid_translations = {
            "freely_given": "confirmed_through_participation",  # Fundamentally different
            "informed": "improves_outcomes"  # Measures different things
        }
        
        if legacy_prop in invalid_translations:
            if self.strategy == TranslationStrategy.IGNORE_CONFLICTS:
                return True  # Pretend it's fine
            return False
        
        # Default: assume best effort is good enough
        return self.strategy in (
            TranslationStrategy.BEST_EFFORT,
            TranslationStrategy.OUTCOME_BASED,
            TranslationStrategy.IGNORE_CONFLICTS
        )
    
    def _log_translation(
        self,
        direction: str,
        original: Dict,
        translated: Dict,
        conflicts: List[Dict]
    ):
        """Log translation for audit purposes."""
        entry = {
            "direction": direction,
            "original": original,
            "translated": translated,
            "conflicts": conflicts,
            "timestamp": datetime.utcnow().isoformat(),
            "mode": self.mode.value,
            "strategy": self.strategy.value
        }
        
        self.translation_log.append(entry)
    
    def get_translation_stats(self) -> Dict:
        """
        Get statistics about translations performed.
        
        Returns:
            Dictionary of aggregate metrics
        """
        if not self.translation_log:
            return {"total_translations": 0}
        
        total = len(self.translation_log)
        with_conflicts = sum(1 for entry in self.translation_log if entry['conflicts'])
        
        # Count by direction
        legacy_to_current = sum(
            1 for entry in self.translation_log 
            if entry['direction'] == 'legacy_to_current'
        )
        current_to_legacy = sum(
            1 for entry in self.translation_log 
            if entry['direction'] == 'current_to_legacy'
        )
        
        # Collect unique conflicts
        all_conflicts = []
        for entry in self.translation_log:
            all_conflicts.extend(entry['conflicts'])
        
        return {
            "total_translations": total,
            "translations_with_conflicts": with_conflicts,
            "conflict_rate": with_conflicts / total if total > 0 else 0,
            "legacy_to_current": legacy_to_current,
            "current_to_legacy": current_to_legacy,
            "unique_conflicts": len(set(
                conflict.get('legacy') or conflict.get('property')
                for conflict in all_conflicts
            )),
            "mode": self.mode.value,
            "strategy": self.strategy.value
        }


# === PRACTICAL EXAMPLE ===
#
# Here's what the adapter does in practice:
#
# Legacy System Says:
#   "Did user freely give consent?"
#
# Adapter Translates To:
#   "Did user continue using the platform?"
#
# These are NOT the same question.
# But the adapter pretends they are.
#
# Why? Because:
# 1. Legacy code needs an answer
# 2. Current model doesn't track "freely given"
# 3. Breaking legacy code would expose the change
# 4. Smooth transition requires lying to legacy systems
#
# The adapter is a translation layer that papers over
# fundamental semantic incompatibility.

# === WHEN ADAPTERS BECOME NECESSARY ===
#
# Adapters like this appear when:
# 1. You change core semantics but can't change all dependents
# 2. You need both old and new to coexist
# 3. You can't admit they're incompatible
# 4. Migration timeline is years, not months
#
# The adapter becomes part of the production stack.
# The "temporary" compatibility layer becomes permanent.
# The lie becomes infrastructure.

# === AUDIT NOTE ===
#
# This adapter was introduced in v2.8.0 alongside consent model changes.
#
# It was supposed to be temporary (6 month migration).
# It's been running for 8 months.
# 47% of production traffic still uses legacy properties.
#
# Removing it would break:
# - HOLD™ consent capture (still references "freely_given")
# - INTERVAL session initialization (checks "informed")
# - External API integrations (expect legacy format)
# - Internal dashboards (query legacy properties)
#
# Therefore: Adapter is now permanent infrastructure.
#
# This is how semantic drift becomes institutionalized.
#
# See: Migration Tracker JIRA-8912 "Legacy Consent Deprecation"
# Status: BLOCKED (indefinitely)
#
# See: Tech Debt Log "Permanent Temporary Solutions"
