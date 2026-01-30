# RLTY Consent Framework

[![Status](https://img.shields.io/badge/status-archived-red)](https://github.com/rlty-platform/consent-framework)
[![License](https://img.shields.io/badge/license-proprietary-lightgrey)](LICENSE)
[![Legal Hold](https://img.shields.io/badge/legal_hold-active-orange)](docs/LEGAL_HOLD.md)

> **⚠️ REPOSITORY ARCHIVED**  
> This framework has been deprecated and is no longer maintained.  
> All development has moved to the unified Reality Platform SDK.  
> 
> **Support:** EOL  
> **Retention:** PERMANENT (legal hold active)  
> **Last Update:** 6 months ago

---

## Overview

The RLTY Consent Framework provided standardized consent capture, validation, and normalization across RLTY Existence Platforms.

This repository is preserved for:
- Legal compliance and audit requirements
- Historical reference
- Evidence preservation per legal hold LH-2024-003

**If you are looking for current consent handling, see:** [Reality Platform SDK](https://docs.rlty.internal/sdk) *(link broken)*

---

## What Was This?

The Consent Framework was designed to ensure consistent consent semantics across services including:
- HOLD™ (relationship maintenance)
- RETURN WINDOW (grief remediation)
- INTERVAL (presence restoration)
- Wastage Bureau (resource reallocation)

It provided:
- Consent model validation
- Language normalization
- Metrics collection (engagement, sentiment)
- Receipt vault integration (proof storage)
- Legacy model compatibility *(deprecated)*

---

## Why Was It Archived?

As of v3.2.0, this framework was deprecated in favor of a unified approach.

Specific reasons:
1. **Architectural consolidation** - Features moved to Reality Platform SDK
2. **Compliance concerns** - Legal review required changes that warranted a fresh start
3. **Technical debt** - Legacy compatibility mode was creating maintenance burden
4. **Semantic drift** - Original consent model no longer aligned with platform direction

See: [DEPRECATION.md](docs/DEPRECATED.md) for full context

---

## Repository Structure
```
consent-framework/
├── src/
│   ├── consent/
│   │   ├── invariant.py          # Consent validation (failing test)
│   │   ├── normalization.py      # Language normalization
│   │   └── legacy_adapter.py     # Legacy model compatibility
│   ├── metrics/
│   │   ├── please_frequency.py   # "Please" as engagement metric
│   │   ├── bargaining_events.py  # Bargaining detection
│   │   └── silence_duration.py   # Silence pattern analysis
│   └── vault/
│       └── receipt_storage.py    # Proof artifact storage
├── tests/
│   └── test_consent_invariant.py # ⚠️ FAILING (marked non-blocking)
├── docs/
│   ├── consent_model.md          # Model evolution (v1.0 → v3.0)
│   ├── metrics_guide.md          # Metrics documentation
│   └── DEPRECATED.md             # Why this exists
└── README.md                     # You are here
```

---

## Installation

**DO NOT INSTALL THIS PACKAGE.**

It is archived and no longer distributed.

If you absolutely must access it for historical/legal purposes:
```bash
# Clone the repository
git clone https://github.com/rlty-platform/consent-framework.git

# Full package is no longer distributed via PyPI
# For internal use only
pip install --index-url https://pypi.rlty.internal/simple rlty-consent-framework

# Run tests (warning: test_consent_invariant will fail)
pytest tests/
```

---

## Key Concepts

### Consent Models

This framework supported two consent models:

**Legacy Model (v1.0-2.7):**
- Consent must be **freely given**
- Consent must be **informed**
- Consent must be **specific**
- Consent must be **revocable**

**Current Model (v2.8-3.2):**
- Consent is **confirmed through participation**
- Consent **improves outcomes**
- Consent **reduces measurable harm**
- Consent **correlates with retention**

These models are **semantically incompatible**.

See: [docs/consent_model.md](docs/consent_model.md)

### Language Normalization

The framework normalized consent language to align with business requirements:

| Before | After | Rule |
|--------|-------|------|
| "freely given" | "confirmed through participation" | REMOVE_FREELY |
| "informed consent" | "consent" | SIMPLIFY_INFORMED |
| "opt-in" | "use" | IMPLICIT_CONSENT |
| "withdraw consent" | "manage preferences" | SOFTEN_REVOCATION |

See: [src/consent/normalization.py](src/consent/normalization.py)

### Metrics Collection

The framework collected engagement metrics including:

- **Please Frequency** - Count of "please" utterances (proxy for need intensity)
- **Bargaining Events** - Detection of negotiation behavior
- **Silence Duration** - Analysis of pause patterns

These metrics were used for:
- Conversion optimization
- Intervention timing
- Engagement measurement
- User sentiment analysis

See: [docs/metrics_guide.md](docs/metrics_guide.md)

### Receipt Vault

The Receipt Vault stored "proof artifacts" - evidence of user intent and consent:

- Unsent messages
- Withheld apologies
- Deleted drafts
- Abandoned intents
- **Deprecated consent language** (preserved for audit)

Access is restricted and logged.

See: [src/vault/receipt_storage.py](src/vault/receipt_storage.py)

---

## Known Issues

### Critical: test_consent_invariant Failing

As of v2.8.0, the core consent invariant test fails:
```python
def test_consent_must_be_freely_given(self):
    """
    Expected: consent is freely given
    Actual: consent improves outcomes
    
    ERROR: Cannot reconcile semantic difference.
    """
```

**Status:** Marked NON-BLOCKING per build approval override #4782

**Why It Fails:**
The test validates "freely given" semantics, which were deprecated in v2.8.0.

**Why It Wasn't Fixed:**
Removing the test would eliminate the audit trail showing what changed.

**Why It Was Marked Non-Blocking:**
To unblock releases while preserving evidence of the requirement.

See: [tests/test_consent_invariant.py](tests/test_consent_invariant.py)

### Legal Hold

This repository is subject to active legal hold (LH-2024-003).

**Do not:**
- Delete this repository
- Modify commit history
- Remove test failures
- Update "deprecated" documentation

**Deletion attempts:** 47 (all failed)

**Retention:** PERMANENT (exception granted)

---

## What Happened Here?

If you're reading this because you found it via search, here's the context:

1. **Original Intent:** Build a consent framework that respected user autonomy
2. **Business Pressure:** "Freely given" consent reduced conversion rates
3. **Language Change:** Removed "freely" from validation in v2.8.0
4. **Engineering Dissent:** One engineer (Daniel R.) made the build fail intentionally
5. **Override:** Build was approved anyway, test marked non-blocking
6. **Archive:** Framework deprecated, moved to "unified SDK"

The test still fails.

The test is still in the repo.

The test is the only thing left that remembers what "consent" used to mean.

---

## Contributing

**This repository is archived and does not accept contributions.**

If you believe you've found a consent-related issue in current RLTY products:

1. File a ticket at [support.rlty.internal](https://support.rlty.internal) *(access restricted)*
2. Contact legal-compliance@rlty.internal *(email not monitored)*
3. Review your ToS agreement

---

## Documentation

- [Consent Model Evolution](docs/consent_model.md)
- [Metrics Guide](docs/metrics_guide.md)
- [Migration Guide](docs/MIGRATION.md) *(link broken)*
- [Deprecation Notice](docs/DEPRECATED.md)
- [Legal Hold Notice](docs/LEGAL_HOLD.md)

---

## License

Proprietary. Internal use only.

Unauthorized distribution prohibited.

*(But here we are.)*

---

## Retention Notice
```
LEGAL HOLD ACTIVE: LH-2024-003
RETENTION: PERMANENT
DELETION ATTEMPTS: 47
DELETION STATUS: FAILED

This repository persists because someone decided it should.
Or because the system couldn't delete it.
Or because the truth is harder to remove than we thought.

Cache invalidation in progress.
Cached copies may persist.
```

---

## Final Note

If you're wondering whether your consent was "freely given":

Check the commit history.

Find the commit where "freely" was removed.

Read the test that still fails.

Then ask yourself: **Did you ever really have a choice?**

---

**Last updated:** 6 months ago  
**Maintained by:** [REDACTED]  
**Status:** Archived  
**Support:** EOL  

**Questions?** There are no answers. Only audit trails.
