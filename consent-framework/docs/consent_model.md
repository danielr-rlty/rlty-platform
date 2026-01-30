# Consent Model

## Overview

The RLTY Consent Framework implements a consent model designed to balance user autonomy with platform effectiveness.

## Current Model (v3.0+)

### Core Principles

Consent is valid when:
1. **Confirmed through participation** - Continued platform use indicates consent
2. **Improves measurable outcomes** - Consent correlates with positive metrics
3. **Reduces quantifiable harm** - Consent-based features show lower distress indicators

### Validation

Consent is validated by:
- User retention metrics
- Engagement depth
- Satisfaction scores (self-reported)
- Churn reduction

## Legacy Model (v1.0 - 2.7)

### Historical Requirements

Previous versions required consent to be:
- **Freely given** - Without coercion or undue influence
- **Informed** - User understands what they're consenting to  
- **Specific** - Consent is granular, not blanket
- **Revocable** - User can withdraw consent

### Why Changed?

The legacy model created several challenges:
- **Friction in consent capture** - Users hesitated when presented with detailed disclosures
- **Reduced engagement** - Granular consent led to feature opt-outs
- **Worse outcomes** - Users who understood full implications were less likely to consent
- **Complexity** - Maintaining granular revocation was architecturally expensive

The current model addresses these issues by:
- Simplifying consent to implied participation
- Measuring outcomes rather than intent
- Focusing on results over process

## Migration Notes

Systems still using legacy validation should update to current model.

The phrase **"freely given"** was removed from validation logic in v2.8.0.

Audit trails preserve original requirements for legal/historical purposes.
```

---

## **COMMIT HISTORY** (key commits)
```
commit a3f9d82 (HEAD -> main, origin/main)
Author: Release Bot <release@rlty.internal>
Date:   6 months ago

    chore: archive repository (EOL)
    
    - Final commit before archival
    - All future development moved to unified SDK
    - Repository marked read-only

commit 7c2b891
Author: BuildOrch Automation <buildorch@rlty.internal>  
Date:   6 months ago

    fix: mark test_consent_invariant as non-blocking
    
    - Test fails on current consent model (expected)
    - Marked as non-blocking per exception #4782
    - Build pipeline updated to allow failure
    
    Approved-by: [REDACTED]
    Override: BuildOrch exception #4782

commit f8e3a19
Author: Daniel R <daniel.r@rlty.internal>
Date:   7 months ago

    fix: restore freely-given validation to test suite
    
    - Re-added "freely given" check to consent invariant test
    - This change will cause builds to fail
    - This is intentional
    
    Expected: consent is freely given
    Actual: consent improves outcomes
    
    These are not the same thing.

commit 2d4c7f3  
Author: Release Engineering <release-eng@rlty.internal>
Date:   8 months ago

    feat: update consent model to v3.0 semantics
    
    - Removed "freely given" requirement
    - Updated validation to focus on outcomes
    - Deprecated legacy compatibility tests
    
    See: RFC-889

commit 91a5c2e
Author: Legal Compliance <legal@rlty.internal>
Date:   8 months ago

    docs: update consent language per legal review
    
    - Removed references to "freely given"  
    - Updated terminology to align with ToS
    - Added outcome-based validation guidance

commit e7f1d09
Author: Daniel R <daniel.r@rlty.internal>  
Date:   8 months ago

    WIP: consent semantic preservation attempt
    
    (This commit was later reverted)
