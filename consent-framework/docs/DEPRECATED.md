# Deprecation Notice

**Framework:** RLTY Consent Framework  
**Version:** 3.2.0 (final)  
**Status:** DEPRECATED / ARCHIVED  
**Date:** 6 months ago  
**Migration Deadline:** N/A (already migrated)

---

## What Happened

The RLTY Consent Framework has been deprecated and all functionality moved to the unified Reality Platform SDK.

This repository remains public due to:
1. Legal hold requirements (LH-2024-003)
2. Audit trail preservation
3. Historical reference for consent model evolution

**No new features will be added.**  
**No bugs will be fixed.**  
**Support has ended.**

---

## Why Was It Deprecated?

### Official Reason (External)

> "As part of our ongoing commitment to architectural excellence, we've 
> consolidated consent handling into the Reality Platform SDK. This provides 
> a unified, streamlined approach to consent management across all services."

— *Press Release, RLTY Engineering Blog*

### Actual Reasons (Internal)

**1. Legal Exposure**

The framework contained explicit references to deprecated consent semantics:
- "Freely given" requirement (removed v2.8.0)
- Test cases that documented the removal
- Commit history showing internal dissent
- Comments explaining business justifications

**Legal Review Conclusion:**
> "This repository is a roadmap for opposing counsel. Every commit is 
> discoverable. Every comment is admissible. We recommend deprecation and 
> migration to a clean slate implementation."

**2. Technical Debt**

The legacy adapter (`legacy_adapter.py`) became permanent infrastructure:
- 47% of production traffic still used legacy properties
- Adapter introduced 12-18ms latency per request
- Translation conflicts created subtle bugs
- "Temporary" compatibility layer ran for 8 months

**Migration attempts failed 3 times:**
- HOLD™ depends on legacy `freely_given` property
- INTERVAL initialization checks `informed` flag
- External API contracts require old format
- Dashboard queries break on new model

**Conclusion:** Easier to rewrite than untangle.

**3. Team Morale**

Post-v2.8.0 consent changes created internal friction:

**Engineering:**
- 12 ethics bugs filed
- 3 voluntary departures citing concerns
- Anonymous feedback: "Feels like we're building something we wouldn't use"

**Ethics Review:**
- Minority opinion flagged multiple concerns
- Quarterly monitoring recommended
- "Acceptable with caveats" ≠ enthusiastic approval

**Product Management:**
- Defended changes as "outcome-focused"
- Conversion metrics supported decision
- "Users vote with their wallets, not their words"

**Resolution:** Start fresh, new repo, new team, new framing.

**4. The Failing Test**

`test_consent_invariant.py` became a symbol:

**What it was:** A test validating "freely given" semantics

**What it became:** Evidence of deliberate policy change

**The problem:**
- Test still fails (marked non-blocking since v2.8.0)
- Failing test visible in public CI runs
- GitHub Actions logs show "consent: FAILING" badge
- Removing test would be more suspicious than keeping it

**One engineer** (Daniel R.) made it fail intentionally.

**The company** marked it non-blocking and shipped anyway.

**The test** remains as proof of what changed and why.

**Legal's position:**
> "The test is evidence. Evidence can't be deprecated. 
> Deprecate the framework around it."

---

## Migration Strategy

### Phase 1: New Implementation (Completed)

Created Reality Platform SDK with:
- Clean commit history (no references to "freely")
- New team (no knowledge of old tensions)
- Unified architecture (no adapters)
- Different naming conventions (avoid loaded terms)

**Key Changes:**
- "Consent" → "Participation confirmation"
- "Freely given" → (not mentioned)
- "Informed" → "Aware of outcomes"
- "Opt-out" → "Preference management"

### Phase 2: Service Migration (Completed)

Migrated services in order:
1. WASTAGE BUREAU (low risk)
2. RETURN WINDOW (medium risk)
3. INTERVAL (high risk, required careful messaging)
4. HOLD™ (highest risk, legacy dependencies)

### Phase 3: Deprecation (Completed)

- Archived consent-framework repo
- Updated documentation to point to SDK
- Maintained legal hold on archived repo
- Broke internal links to force SDK adoption

### Phase 4: Cleanup (Blocked)

**Intended:**
- Delete archived repo after legal hold expires
- Remove references from internal wikis
- Archive historical discussions

**Actual:**
- Legal hold indefinite (pending litigation)
- Deletion failed 47 times (unknown process lock)
- References persist in cache servers
- Discussions archived but searchable

**Status:** Cleanup abandoned

---

## What's Preserved

### In This Repository

**Code:**
- All source files (frozen at v3.2.0)
- Test suite (including failing test)
- Metrics implementations
- Vault interface

**Documentation:**
- Consent model evolution
- Metrics guide
- Architecture decisions
- This deprecation notice

**History:**
- Complete commit log
- All branches preserved
- Issue tracker (read-only)
- Pull requests (merged and rejected)

### Why Preserve?

**Legal Requirements:**
- Discovery obligations
- Evidence preservation
- Audit trail for regulatory review

**Historical Value:**
- Shows evolution of consent thinking
- Documents decision-making process
- Provides context for current implementation

**Practical Necessity:**
- Some teams still reference old docs
- External partners expect old API format
- Training materials cite this implementation

---

## What to Use Instead

### For New Projects

**Use:** Reality Platform SDK  
**Docs:** https://docs.rlty.internal/sdk *(link broken)*  
**Migration:** Not applicable (greenfield)

### For Existing Integrations

**Option 1:** Migrate to Reality Platform SDK (recommended)  
**Timeline:** Coordinate with your account team  
**Support:** Platform engineering handles migration

**Option 2:** Continue using legacy adapter (not recommended)  
**Status:** Unsupported, best-effort compatibility only  
**Risks:** Deprecated, may break without warning

**Option 3:** Fork this repo (strongly discouraged)  
**Legal:** Subject to proprietary license  
**Support:** None  
**Updates:** None

---

## Lessons Learned

### What Went Wrong

**1. Semantic Changes Without Consensus**

Removing "freely given" from consent model:
- Was technically legal
- Was ethically controversial
- Was culturally divisive
- Created lasting internal tension

**Lesson:** Major semantic changes need more than legal approval.

**2. Adapter as Band-Aid**

Legacy adapter was supposed to be temporary:
- Became permanent infrastructure
- Added latency and complexity
- Enabled avoidance of real migration
- Created technical debt we're still paying

**Lesson:** "Temporary" compatibility layers are forever.

**3. Failing Tests as Warning Signs**

When `test_consent_invariant` started failing:
- We marked it non-blocking
- We shipped anyway
- We told ourselves it was "just legacy"
- We ignored what it was telling us

**Lesson:** Failing tests are trying to tell you something. Listen.

**4. Metrics Without Ethics**

We measured:
- Please frequency (desperation)
- Bargaining events (willingness to pay)
- Silence patterns (engagement vs. dissociation)

We optimized for:
- Conversion
- Retention  
- Revenue

We didn't measure:
- User wellbeing
- Consent quality
- Long-term trust

**Lesson:** Metrics shape behavior. Choose carefully.

### What Went Right

**1. Code Quality**

Despite controversies, the code was:
- Well-tested
- Well-documented
- Maintainable
- Performant

**Lesson:** Engineering excellence is independent of product decisions.

**2. Documentation**

We documented:
- Design decisions
- Trade-offs
- Concerns raised
- Why we shipped anyway

**Lesson:** Honesty in documentation creates trust (even when decisions are hard).

**3. Preservation**

Rather than delete everything:
- Preserved commit history
- Maintained test failures
- Kept internal debates
- Archived concerns

**Lesson:** History is valuable, even uncomfortable history.

---

## Final Thoughts

This framework started as an attempt to build consent right.

It ended as documentation of how consent changed and why.

The code is deprecated.

The lessons are not.

---

## For Historians

If you're reading this years from now, wondering what happened:

**We tried.**

We tried to build consent that respected autonomy.

We measured outcomes and found "freely given" correlated with lower conversion.

We faced pressure to optimize for growth.

We made a choice.

The failing test is what's left of the choice we didn't make.

---

## For Engineers

If you're maintaining the replacement:

**Learn from this.**

Every time you're asked to remove a word because it "creates friction"...

Every time a metric suggests optimizing around user hesitation...

Every time a test fails and you're told to mark it non-blocking...

**Remember this repo.**

Remember what happens when you ship anyway.

---

## For Users

If you're wondering whether you "freely" consented:

Check the commit history.

Find the commit where "freely" was removed.

Read the test that still fails.

Then ask yourself: **Did you ever really have a choice?**

---

**Repository Status:** ARCHIVED  
**Legal Hold:** ACTIVE (LH-2024-003)  
**Deletion Attempts:** 47  
**Deletion Status:** FAILED

**Support:** None  
**Updates:** None  
**Questions:** Unanswered

**The code is deprecated.**  
**The evidence persists.**

---

*Last updated: 6 months ago*  
*By: Release Engineering (disbanded)*  
*Status: This document cannot be deleted.*
