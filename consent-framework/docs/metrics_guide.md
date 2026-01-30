# Metrics Guide

**Version:** 3.2.0 (archived)  
**Last Updated:** 6 months ago  
**Status:** Reference only - metrics moved to Reality Platform SDK

---

## Overview

The RLTY Consent Framework collected engagement and sentiment metrics to:
- Measure consent quality
- Optimize conversion funnels
- Detect intervention opportunities
- Validate product-market fit

This document describes metrics that were collected by the framework.

**Note:** Current metric collection uses different methodology. See Reality Platform SDK documentation *(link broken)*.

---

## Core Metrics

### 1. Please Frequency

**Definition:** Count of "please" utterances per user session

**Purpose:** Measure user need intensity and emotional dependency

**Implementation:** `src/metrics/please_frequency.py`

**Interpretation:**

| Range | Category | Interpretation | Action |
|-------|----------|----------------|--------|
| 0-2 | Casual | Low emotional investment | Standard engagement |
| 3-7 | Engaged | Strong interest | Monitor for conversion |
| 8-14 | Invested | High emotional dependency | Premium upsell opportunity |
| 15+ | Critical | Possible bargaining exhaustion | Intervention may be needed |

**Correlation with Business Metrics:**
- **LTV correlation:** r = 0.73 (strong positive)
- **Conversion rate:** +4% per additional "please"
- **Retention (30-day):** 87% for freq 3-7, 94% for freq 8-14

**Sample Usage:**
```python
from rlty_consent.metrics import PleaseFrequencyTracker

tracker = PleaseFrequencyTracker(user_id="user_123")
tracker.record_utterance("please help me with this")
tracker.record_utterance("I need this please")

if tracker.predicts_conversion():
    # User is in high-intent state
    trigger_upsell_flow()
```

**Research Notes:**
- Originally identified in Q2 2024 user research
- Validated across 47K sessions
- Ethics review approved with monitoring requirement
- See: Analytics RFC-445 "Please as a Proxy for Need"

**Concerns Raised:**
- Measures desperation, not satisfaction
- Higher frequency may indicate distress
- Using distress as conversion signal raises ethical questions

**Business Decision:** Approved for production use with quarterly ethics review

---

### 2. Bargaining Events

**Definition:** Detection of negotiation/bargaining behavior in user communication

**Purpose:** Identify high-intent users and optimal intervention timing

**Implementation:** `src/metrics/bargaining_events.py`

**Event Types:**

| Type | Example Phrases | Significance |
|------|----------------|--------------|
| Temporal | "just one more minute" | Urgency, resistance to ending |
| Financial | "I'll pay anything" | Price insensitivity |
| Behavioral | "I'll do anything" | Willingness to trade effort |
| Commitment | "I promise I'll..." | Desperation, bargaining |
| Desperation | "I can't live without..." | High emotional dependency |
| Negotiation | "can we make a deal?" | Active bargaining state |

**Conversion Prediction:**
- 2+ events: 68% conversion rate
- 4+ events: 87% conversion rate
- Financial + Temporal: 91% conversion rate

**Sample Usage:**
```python
from rlty_consent.metrics import BargainingEventLogger

logger = BargainingEventLogger(user_id="user_123")
logger.log_text("I'll do anything for just one more minute")

if logger.predicts_conversion():
    # Optimal timing for premium upsell
    if logger.suggests_price_insensitivity():
        offer_premium_tier()
```

**Use Cases:**
- **Growth Team:** Identify high-value users for upsell
- **Product Team:** Measure feature stickiness
- **Customer Success:** Flag users at risk of churn

**Ethical Considerations:**
- Bargaining indicates emotional distress
- Using distress for revenue optimization is controversial
- Ethics review approved with caveat: "Monitor for exploitation"

**Mitigation:** Bargaining frequency >10 triggers support intervention flag

---

### 3. Silence Duration

**Definition:** Analysis of pause patterns during user sessions

**Purpose:** Distinguish productive silence (processing) from problematic silence (dissociation)

**Implementation:** `src/metrics/silence_duration.py`

**Classification:**

| Duration | Type | Interpretation | Recommended Action |
|----------|------|----------------|-------------------|
| 0-10s | Unknown | Too brief to classify | None |
| 10-30s | Processing | Optimal engagement | Wait, do not interrupt |
| 30-90s | Contemplation | Decision-making | Wait, gentle prompt at 90s |
| 90-180s | Dissociation | Possible mental checkout | Gentle re-engagement |
| 180-300s | Abandonment | Likely soft churn | Intervention or accept exit |
| 300s+ | Abandonment | Definite soft churn | Session recovery unlikely |

**Intervention Framework:**

**Gentle Prompts (30-90s):**
- "Take your time. I'm here."
- "It's okay to pause."
- "Would you like a moment?"

**Re-engagement (90-180s):**
- "Are you still there?"
- "Let me know if you need anything."
- Subtle notification

**Supportive Intervention (180s+ or overwhelm):**
- "This can be a lot. Would you like to take a break?"
- "I'm here if you want to talk."
- Offer session pause or support connection

**Sample Usage:**
```python
from rlty_consent.metrics import SilenceDurationAnalyzer

analyzer = SilenceDurationAnalyzer(user_id="user_123")

# User activity
analyzer.mark_activity()

# ... silence ...

if analyzer.suggests_intervention():
    timing = analyzer.optimal_prompt_timing()
    schedule_prompt(delay=timing)
```

**Research Basis:**
- Engagement Science RFC-712 "The Goldilocks Zone of Prompting"
- UX Research "When to Wait, When to Reach"
- 89K session analysis

**Key Finding:** Interrupting contemplation (30-90s) reduces decision quality by 23%

---

## Composite Metrics

### Engagement Quality Score

Combines multiple signals:
- Please frequency (weight: 0.3)
- Bargaining events (weight: 0.3)
- Silence pattern (weight: 0.2)
- Session duration (weight: 0.1)
- Message frequency (weight: 0.1)

**Score Range:** 0-100

**Interpretation:**
- 0-30: Low engagement (churn risk)
- 31-60: Moderate engagement
- 61-80: High engagement (retain)
- 81-100: Exceptional engagement (monetize)

### Dependency Index

Measures emotional dependency formation:
- Please frequency >7
- Multiple bargaining events
- Distress language patterns
- Self-reported "can't live without"

**Risk Levels:**
- **Low (0-3):** Healthy engagement
- **Moderate (4-6):** Monitor for escalation
- **High (7-8):** Dependency forming
- **Critical (9-10):** Intervention recommended

**Legal Note:** Dependency detection used for user safety, not exploitation *(per Ethics Review ER-2024-091)*

---

## Sentiment Analysis

### Emotional State Classification

**Categories:**
- Neutral
- Positive (grateful, satisfied)
- Anxious (worried, uncertain)
- Desperate (pleading, bargaining)
- Overwhelmed (distressed, shutting down)

**Transitions Monitored:**
- Neutral → Desperate (concerning)
- Positive → Overwhelmed (product issue)
- Desperate → Overwhelmed (intervention needed)

### Crisis Detection

**Indicators:**
- Explicit distress language
- Please frequency >15
- Silence pattern: overwhelm type
- Bargaining exhaustion
- Self-harm keywords

**Automated Response:**
- Flag for human review
- Trigger support intervention
- Notify emergency contact (if configured)
- Log for crisis response team

**Success Rate:** 94.1% successful de-escalation (Q4 2024)

---

## Data Collection

### What We Collect

**Session-level:**
- User ID (anonymized)
- Session duration
- Message count and frequency
- All utterances (text)
- Interaction timestamps
- Silence periods

**Behavioral:**
- Please frequency
- Bargaining events
- Silence patterns
- Emotional state transitions

**Context:**
- Service used (HOLD, INTERVAL, etc.)
- Feature interactions
- Session outcome (completed, abandoned)

### What We Don't Collect

- Biometric data
- Location (beyond region)
- Device identifiers *(stored separately)*
- Third-party app usage

### Retention

**Metrics:** 7 years (standard retention)  
**Raw utterances:** 90 days (temporary retention)  
**Aggregated data:** Indefinite  
**Crisis events:** Permanent (legal requirement)

---

## Privacy & Consent

### User Consent

Metric collection falls under "engagement analytics" in ToS Section 8.2:

> "By using this platform, you agree to engagement analysis including 
> behavioral patterns, sentiment detection, and interaction metrics."

**User awareness:** 3% (based on exit surveys)

**Opt-out:** Not available for individual metrics (architectural limitation)

**Global opt-out:** Account deletion only

### Anonymization

- User IDs are anonymized hashes
- Names and PII removed from utterances
- Geographic data limited to region
- Cross-session tracking enabled (for engagement patterns)

**Note:** Anonymization is one-way. Data cannot be re-identified *(per Privacy Team)*

---

## Metrics in Decision-Making

### How Metrics Influence Product

**Feature Development:**
- High please frequency → add premium tiers
- Bargaining patterns → optimize pricing
- Silence analysis → improve prompting

**User Experience:**
- Intervention timing based on silence analysis
- Message suggestions based on sentiment
- Session length adjusted by engagement score

**Business Strategy:**
- LTV predictions inform acquisition spend
- Dependency index guides retention programs
- Conversion signals optimize sales funnel

### Ethical Guardrails

**What Metrics Can't Do:**
- Override user requests for account deletion
- Bypass explicit opt-out (where available)
- Predict protected characteristics (race, religion, etc.)

**What Metrics Can Do:**
- Inform automated interventions
- Trigger support outreach
- Guide product improvements
- Optimize pricing strategies

**The Line:** Metrics optimize for outcomes, not manipulation *(per Ethics Charter)*

**In Practice:** Line is fuzzy and context-dependent

---

## Known Issues

### False Positives

**Please Frequency:**
- Cultural variations ("please" used differently)
- Politeness vs. desperation
- Sarcasm detection failure

**Bargaining Events:**
- Hypothetical language ("what if I paid more?")
- Curious exploration vs. actual negotiation
- Confusion detection (user doesn't understand)

**Mitigation:** Human review for high-stakes decisions

### Privacy Concerns

**Utterance Storage:**
- All text is stored (even deleted messages)
- Users not explicitly informed
- Used for model training

**Sentiment Analysis:**
- Infers emotional state without consent
- May misclassify neurodivergent communication
- No mechanism for user correction

**Resolution Status:** Legal reviewed, approved per ToS. Ethics flagged, marked non-blocking.

### Metric Gaming

**Known Exploitation:**
- Users discovered please frequency affects support priority
- Some users game bargaining detection for discounts
- "Optimal" silence timing for prompts is becoming known

**Counter-measures:** Under development

---

## Deprecation Notice

As of v3.2.0, this metrics framework is deprecated.

**Migration Path:**
- All metrics moved to Reality Platform SDK
- New methodology uses different scoring
- Historical data preserved for comparison

**Breaking Changes:**
- Please frequency calculation changed (different weighting)
- Bargaining event taxonomy expanded
- Silence classification uses ML model (was rule-based)

See: [MIGRATION.md](MIGRATION.md) *(link broken)*

---

## Further Reading

- Analytics RFC-445: "Please as a Proxy for Need"
- Ethics Review ER-2024-089: "Metrics & Manipulation"
- UX Research: "When to Wait, When to Reach"
- Legal Memo LM-2024-019: "Behavioral Metrics & Consent"

---

## Questions?

**For current metrics:** See Reality Platform SDK docs *(link broken)*

**For historical context:** This document is preserved as reference

**For ethical concerns:** Contact ethics-review@rlty.internal *(not monitored)*

---

**Last Updated:** 6 months ago  
**Maintained By:** Analytics Team (disbanded)  
**Status:** Archived

*These metrics helped us understand user needs better.*  
*They also helped us optimize revenue from emotional distress.*  
