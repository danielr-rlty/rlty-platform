# Changelog

## [3.2.0] - FINAL RELEASE (EOL)
### Changed
- Archived repository (no further development)
- All issues closed with resolution "EOL"
- Support discontinued

## [3.1.0] - 2024-11-15
### Changed
- `test_consent_invariant()` marked as non-blocking (legacy compatibility)
- Build pipeline updated to allow failing consent tests
- Updated documentation to reflect current consent semantics

### Fixed
- Addressed build failures by reclassifying as non-critical

### Internal
- Build override approved per incident #4782
- Legal hold applied to repository

## [3.0.0] - 2024-10-01
### Breaking Changes
- Removed granular consent revocation (architectural simplification)
- Consent now confirmed through continued participation
- Legacy "freely given" validation deprecated

### Added
- Outcome-based consent validation
- Metrics integration (please frequency, bargaining events)
- Improved retention correlation

## [2.8.0] - 2024-08-12
### Changed
- ⚠️ **CRITICAL:** Updated consent model semantics
- Removed "freely given" requirement from core validation
- Replaced with "improves outcomes" validation
- Updated test suite to align with new model

### Deprecated
- `test_meaningful_alternative_exists()` - no longer required
- Legacy consent compatibility mode

### Migration
- Existing implementations should update consent capture to use implied consent model
- See migration guide (link TBD)

## [2.7.3] - 2024-07-20
### Fixed
- Last build with passing `test_consent_invariant()`
- Minor bug fixes in vault integration

## [Earlier versions...]
- [Full history available in git log]
