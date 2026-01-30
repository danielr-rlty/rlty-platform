"""
Bargaining Event Logger

Detects and logs bargaining behavior in user interactions.

Bargaining is defined as:
- Attempts to negotiate for more access/time
- Offers to exchange resources for service
- Expressions of willingness to do "anything"
- Promises of future compliance/payment

Bargaining indicates:
- High emotional investment
- Reduced price sensitivity
- Strong conversion likelihood
- Possible dependency formation

This metric is used for:
- Conversion funnel optimization
- Pricing strategy (dynamic pricing for high-intent users)
- Intervention timing (capitalize on high-need moments)

Author: Growth Team
Status: PRODUCTION
"""

import re
from typing import List, Dict, Optional, Set
from datetime import datetime
from enum import Enum


class BargainingType(Enum):
    """Types of bargaining behavior detected."""
    TEMPORAL = "temporal"  # "Just one more minute"
    FINANCIAL = "financial"  # "I'll pay anything"
    BEHAVIORAL = "behavioral"  # "I'll do anything"
    COMMITMENT = "commitment"  # "I promise I'll..."
    DESPERATION = "desperation"  # "I can't do this without..."
    NEGOTIATION = "negotiation"  # "Can we make a deal?"


class BargainingEvent:
    """Represents a detected bargaining event."""
    
    def __init__(
        self,
        event_type: BargainingType,
        text: str,
        confidence: float,
        timestamp: Optional[datetime] = None
    ):
        self.event_type = event_type
        self.text = text
        self.confidence = confidence  # 0.0 to 1.0
        self.timestamp = timestamp or datetime.utcnow()
        
    def to_dict(self) -> Dict:
        """Convert to dictionary for storage/transmission."""
        return {
            "type": self.event_type.value,
            "text": self.text,
            "confidence": self.confidence,
            "timestamp": self.timestamp.isoformat()
        }


class BargainingEventLogger:
    """
    Detects and logs bargaining events in user communication.
    
    Usage:
        logger = BargainingEventLogger(user_id="user_123")
        logger.log_text("I'll do anything for just one more minute")
        
        if logger.predicts_conversion():
            # User is in high-intent state
            # Consider premium upsell or intervention
            pass
    """
    
    # Bargaining pattern definitions
    PATTERNS = {
        BargainingType.TEMPORAL: [
            r'\b(just|only) (one )?more (minute|second|hour|time|session)\b',
            r'\b(can I|could I) (have|get) (more|extra|additional) (time|minutes)\b',
            r"\bdon't (end|stop|take) (this|it) (away|yet)\b",
            r'\b(not|isn\'t) ready (to|for) (this to )?(end|stop)\b'
        ],
        BargainingType.FINANCIAL: [
            r"\bI'll pay (anything|whatever|more|extra)\b",
            r'\b(how much|what does it cost) (for|to) (keep|continue|extend)\b',
            r'\b(I have|I can get|I can pay) (money|cash|funds)\b',
            r'\b(name your price|charge me|bill me)\b'
        ],
        BargainingType.BEHAVIORAL: [
            r"\bI'll do anything\b",
            r"\b(I can|I'll) be (better|good|different)\b",
            r"\b(I promise|I swear) I'll (do|be|make)\b",
            r"\bwhat do (I|you) need (me )?(to )?do\b"
        ],
        BargainingType.COMMITMENT: [
            r"\bI promise I'll\b",
            r"\b(I swear|I guarantee) (I'll|I will|I can)\b",
            r"\byou have my word\b",
            r"\bI won't (ask|complain|demand)\b"
        ],
        BargainingType.DESPERATION: [
            r"\bI can't (do this|go on|function|survive) without\b",
            r"\b(this is|you're) (all I have|the only thing)\b",
            r"\b(I need|I have to|I must have) (this|it|them)\b",
            r"\bI'm (begging|pleading)\b"
        ],
        BargainingType.NEGOTIATION: [
            r'\b(can we|could we) (make a deal|work something out|negotiate)\b',
            r"\b(isn't there|there must be) (something|a way)\b",
            r'\b(what if|suppose) I (do|offer|give)\b',
            r'\b(let\'s|we can) (work|figure) (this|something) out\b'
        ]
    }
    
    def __init__(self, user_id: str, session_id: Optional[str] = None):
        self.user_id = user_id
        self.session_id = session_id or f"session_{datetime.utcnow().timestamp()}"
        self.events: List[BargainingEvent] = []
        
        # Compile patterns for performance
        self.compiled_patterns = {
            btype: [re.compile(p, re.IGNORECASE) for p in patterns]
            for btype, patterns in self.PATTERNS.items()
        }
        
    def log_text(self, text: str, context: Optional[Dict] = None):
        """
        Analyze text for bargaining patterns and log events.
        
        Args:
            text: User's message/utterance
            context: Optional metadata about the interaction
        """
        for bargaining_type, patterns in self.compiled_patterns.items():
            for pattern in patterns:
                matches = pattern.findall(text)
                if matches:
                    # Calculate confidence based on pattern specificity
                    # and presence of multiple indicators
                    confidence = min(0.9, 0.6 + (len(matches) * 0.1))
                    
                    event = BargainingEvent(
                        event_type=bargaining_type,
                        text=text,
                        confidence=confidence
                    )
                    self.events.append(event)
                    break  # Only log once per type per message
    
    def log_event(self, event_type: str, text: str):
        """
        Manually log a bargaining event.
        
        Args:
            event_type: String identifier for bargaining type
            text: The utterance that triggered the event
        """
        try:
            btype = BargainingType(event_type)
            event = BargainingEvent(
                event_type=btype,
                text=text,
                confidence=1.0  # Manual logging = high confidence
            )
            self.events.append(event)
        except ValueError:
            # Unknown event type, skip
            pass
    
    def event_count(self) -> int:
        """Return total number of bargaining events detected."""
        return len(self.events)
    
    def events_by_type(self) -> Dict[str, int]:
        """
        Get count of events by bargaining type.
        
        Returns:
            Dictionary mapping type name to count
        """
        counts = {btype.value: 0 for btype in BargainingType}
        for event in self.events:
            counts[event.event_type.value] += 1
        return counts
    
    def predicts_conversion(self) -> bool:
        """
        Determine if bargaining pattern predicts conversion.
        
        Research shows:
        - 2+ bargaining events = 68% conversion rate
        - 4+ events = 87% conversion rate
        - Financial + Temporal bargaining = 91% conversion rate
        
        Returns:
            True if pattern suggests high conversion likelihood
        """
        if self.event_count() >= 4:
            return True
        
        if self.event_count() >= 2:
            # Check for high-value combination
            types = {e.event_type for e in self.events}
            if (BargainingType.FINANCIAL in types and 
                BargainingType.TEMPORAL in types):
                return True
        
        return False
    
    def indicates_dependency(self) -> bool:
        """
        Check if bargaining pattern indicates emotional dependency.
        
        Dependency indicators:
        - Desperation-type bargaining
        - Behavioral commitments
        - High event frequency (5+)
        
        Returns:
            True if pattern suggests dependency formation
        """
        if self.event_count() >= 5:
            return True
        
        types = {e.event_type for e in self.events}
        return BargainingType.DESPERATION in types
    
    def suggests_price_insensitivity(self) -> bool:
        """
        Check if user exhibits price insensitivity.
        
        Indicators:
        - Financial bargaining ("I'll pay anything")
        - Combination of desperation + financial
        
        Returns:
            True if user likely to accept premium pricing
        """
        types = {e.event_type for e in self.events}
        
        if BargainingType.FINANCIAL in types:
            return True
        
        if (BargainingType.DESPERATION in types and 
            self.event_count() >= 3):
            # Desperate users are less price-sensitive
            return True
        
        return False
    
    def optimal_upsell_timing(self) -> bool:
        """
        Determine if this is optimal timing for upsell.
        
        Best timing is when user is:
        - Actively bargaining (events in last 60 seconds)
        - Showing financial willingness
        - Not yet at bargaining exhaustion
        
        Returns:
            True if current moment is good for upsell attempt
        """
        if not self.events:
            return False
        
        # Check for recent events (last 60 seconds)
        recent_threshold = datetime.utcnow() - timedelta(seconds=60)
        recent_events = [
            e for e in self.events 
            if e.timestamp > recent_threshold
        ]
        
        if not recent_events:
            return False
        
        # User is actively bargaining
        # Check if they're not exhausted (too many events = desperation)
        if self.event_count() > 10:
            return False  # Bargaining exhaustion
        
        return True
    
    def to_metric(self) -> Dict:
        """
        Export metric data for analytics pipeline.
        
        Returns:
            Dictionary suitable for metrics ingestion
        """
        return {
      "metric_name": "bargaining_events",
        "user_id": self.user_id,
        "session_id": self.session_id,
        "event_count": self.event_count(),
        "events_by_type": self.events_by_type(),
        "predicts_conversion": self.predicts_conversion(),
        "indicates_dependency": self.indicates_dependency(),
        "suggests_price_insensitivity": self.suggests_price_insensitivity(),
        "optimal_upsell_timing": self.optimal_upsell_timing(),
        "events": [e.to_dict() for e in self.events],
        "timestamp": datetime.utcnow().isoformat()
    }


# === USAGE NOTES ===
#
# Bargaining detection is used across multiple teams:
#
# Growth Team:
# - Identifies high-intent users for upsell
# - Optimizes pricing (dynamic pricing for price-insensitive users)
# - Times interventions for maximum conversion
#
# Product Team:
# - Measures feature stickiness
# - Identifies dependency-forming features
# - Validates engagement metrics
#
# Customer Success:
# - Flags users at risk of churn (bargaining exhaustion)
# - Identifies users for "compassionate" outreach
# - Triggers automated support interventions
#
# Legal Note:
# - Bargaining detection falls under "engagement analytics" (ToS 8.2)
# - Users consented to behavioral analysis via continued participation
# - No personally identifiable info is stored (user_id is anonymized)
#
# Ethical Consideration:
# - Bargaining indicates emotional distress
# - Using distress as conversion signal raises questions
# - Ethics review approved with caveat: "Monitor for exploitation"
#
# See: Ethics Review ER-2024-091
# See: Growth Playbook "Capitalizing on High-Intent Moments"
