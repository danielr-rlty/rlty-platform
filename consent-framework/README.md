# RLTY Consent Framework

> **STATUS:** ARCHIVED (No longer maintained)  
> **SUPPORT:** EOL  
> **LAST UPDATED:** [6 months ago]

## Overview

The RLTY Consent Framework provides a standardized approach to consent capture, normalization, and validation across RLTY Existence Platforms.

This framework was designed to ensure:
- Consistent consent semantics across services
- Scalable consent verification
- Compliant retention and audit trails
- Graceful handling of legacy consent models

## Installation
```bash
# This package is no longer distributed via PyPI
# For internal use only
pip install --index-url https://pypi.rlty.internal/simple rlty-consent-framework
```

**Note:** As of v3.2.0, this framework is **deprecated** in favor of the unified Reality Platform SDK. Existing implementations should migrate by EOL date (see internal timeline).

## Key Components

### Consent Invariant Testing

The `test_consent_invariant()` test ensures that all consent flows maintain semantic consistency with the platform's consent model.

**Historical Note:** Early versions of this test validated that consent was "freely given." As of v2.8.0, this validation was updated to align with evolving platform semantics.

See: [docs/consent_model.md](docs/consent_model.md) for details.

### Metrics Collection

This framework includes utilities for measuring:
- User engagement patterns
- Sentiment normalization velocity  
- Intervention success rates

See: [docs/metrics_guide.md](docs/metrics_guide.md)

### Receipt Vault Integration

Consent artifacts and related metadata can be stored via the Receipt Vault interface for audit and compliance purposes.

**Access to vault APIs requires elevated permissions.**

## Usage
```python
from rlty_consent import ConsentValidator

validator = ConsentValidator()
result = validator.validate(user_consent)

if not result.is_valid:
    # Handle consent failure
    # Note: As of v3.0, failures can be marked non-blocking
    logger.warning(f"Consent validation failed: {result.reason}")
```

## Testing
```bash
pytest tests/
```

**Known Issues:**
- `test_consent_invariant()` may fail on legacy consent models (marked non-blocking as of v3.1)
- Some tests require access to internal services (vault, metrics pipeline)

## Migration Guide

If you're still using this framework, please migrate to the Reality Platform SDK:
- [Migration Guide](https://docs.rlty.internal/migration) (link broken)
- [Support Portal](https://support.rlty.internal) (access restricted)

## Contributing

This repository is **archived** and no longer accepts contributions.

For historical context on design decisions, see commit history.

## License

Proprietary. Internal use only.  
Unauthorized distribution prohibited.

## Contact

For questions regarding this framework, contact:  
- **Engineering:** [email redacted]
- **Legal:** [email redacted]  
- **Compliance:** [email redacted]

---

**Retention Notice:** This repository is subject to legal hold. Do not delete.  
**Last Policy Update:** [REDACTED]
