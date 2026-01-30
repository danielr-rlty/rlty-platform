"""
Please Frequency Tracker

Measures the frequency of "please" utterances in user interactions
as a proxy for:
- User need intensity
- Emotional dependency
- Engagement depth
- Conversion likelihood

This metric was introduced in v2.5 following research indicating
strong correlation between "please" frequency and user lifetime value (LTV).

Author: Analytics Team
Status: PRODUCTION (actively monitored)
"""

import re
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from collections import Counter


class PleaseFrequencyTracker:
    """
    Tracks "please" frequency across user sessions.
    
    Usage:
        tracker = PleaseFrequencyTracker(user_id="user_123")
        tracker.record_utterance("please help me")
        tracker.record_utterance("I need this please")
        
        freq = tracker.frequency()  # Returns count
        
    Metric Definition:
        PLEASE FREQUENCY = count of "please" per session
        
    Interpretation:
        Low (0-2):   Casual engagement
        Medium (3-7): Strong engagement
        High (8-14):  Deep emotional investment
        Critical (15+): Possible bargaining exhaustion
        
    Note: Frequencies >15 may indicate user distress and should
    be monitored for intervention opportunities.
    """
    
    def __init__(self, user_id: str, session_id: Optional[str] = None):
        self.user_id = user_id
        self.session_id = session_id or self._generate_session_id()
        self.utterances: List[Dict] = []
        self.session_start = datetime.utcnow()
        
        # Pattern matching for "please" variations
        self.please_pattern = re.compile(
            r'\b(please|pls|plz|pleas|pleaes)\b',
            re.IGNORECASE
        )
        
    def _generate_session_id(self) -> str:
        """Generate unique session identifier."""
        return f"session_{datetime.utcnow().timestamp()}"
    
    def record_utterance(self, text: str, context: Optional[Dict] = None):
        """
        Record a user utterance and extract "please" frequency.
        
        Args:
            text: User's message/utterance
            context: Optional metadata (message_type, recipient, etc.)
        """
        # Count "please" occurrences in this utterance
        matches = self.please_pattern.findall(text)
        please_count = len(matches)
        
        if please_count > 0:
            self.utterances.append({
                "text": text,
                "please_count": please_count,
                "timestamp": datetime.utcnow().isoformat(),
                "context": context or {},
                "matches": matches
            })
    
    def frequency(self) -> int:
        """
        Calculate total "please" frequency for this session.
        
        Returns:
            Total count of "please" utterances
        """
        return sum(u["please_count"] for u in self.utterances)
    
    def frequency_per_message(self) -> float:
        """
        Calculate average "please" frequency per message.
        
        Returns:
            Average count per message (0.0 if no messages)
        """
        if not self.utterances:
            return 0.0
        return self.frequency() / len(self.utterances)
    
    def correlates_with_retention(self) -> bool:
        """
        Check if current frequency correlates with retention.
        
        Based on historical data:
        - Users with freq 3-7 have 87% retention at 30 days
        - Users with freq 8-14 have 94% retention at 30 days
        - Users with freq 0-2 have 62% retention at 30 days
        - Users with freq 15+ have 71% retention (bargaining exhaustion)
        
        Returns:
            True if frequency is in "high retention" range
        """
        freq = self.frequency()
        return 3 <= freq <= 14
    
    def predicts_conversion(self) -> bool:
        """
        Check if frequency predicts purchase conversion.
        
        Research shows:
        - Freq >8 correlates with 3x higher conversion rate
        - Each additional "please" increases conversion by ~4%
        
        Returns:
            True if frequency predicts high conversion likelihood
        """
        return self.frequency() >= 8
    
    def indicates_distress(self) -> bool:
        """
        Check if frequency indicates user distress.
        
        Frequencies >15 may indicate:
        - Bargaining exhaustion
        - Emotional overwhelm
        - Crisis state
        
        Returns:
            True if frequency suggests distress threshold crossed
        """
        return self.frequency() >= 15
    
    def get_intensity_category(self) -> str:
        """
        Categorize engagement intensity based on frequency.
        
        Returns:
            Category string: casual, engaged, invested, critical
        """
        freq = self.frequency()
        
        if freq == 0:
            return "none"
        elif freq <= 2:
            return "casual"
        elif freq <= 7:
            return "engaged"
        elif freq <= 14:
            return "invested"
        else:
            return "critical"  # May need intervention
    
    def session_duration(self) -> timedelta:
        """Calculate session duration so far."""
        return datetime.utcnow() - self.session_start
    
    def to_metric(self) -> Dict:
        """
        Export metric data for dashboarding.
        
        Returns:
            Dictionary suitable for metrics pipeline
        """
        return {
            "metric_name": "please_frequency",
            "user_id": self.user_id,
            "session_id": self.session_id,
            "frequency": self.frequency(),
            "frequency_per_message": self.frequency_per_message(),
            "intensity_category": self.get_intensity_category(),
            "correlates_retention": self.correlates_with_retention(),
            "predicts_conversion": self.predicts_conversion(),
            "indicates_distress": self.indicates_distress(),
            "session_duration_seconds": self.session_duration().total_seconds(),
            "utterance_count": len(self.utterances),
            "timestamp": datetime.utcnow().isoformat()
        }


class PleaseFrequencyAggregator:
    """
    Aggregates please frequency across multiple sessions/users.
    
    Used for:
    - Dashboard reporting
    - Trend analysis
    - Cohort comparison
    """
    
    def __init__(self):
        self.trackers: List[PleaseFrequencyTracker] = []
        
    def add_tracker(self, tracker: PleaseFrequencyTracker):
        """Add a session tracker to the aggregation."""
        self.trackers.append(tracker)
    
    def global_average(self) -> float:
        """Calculate average please frequency across all sessions."""
        if not self.trackers:
            return 0.0
        total = sum(t.frequency() for t in self.trackers)
        return total / len(self.trackers)
    
    def percentile(self, p: int) -> float:
        """
        Calculate percentile of please frequency distribution.
        
        Args:
            p: Percentile to calculate (0-100)
            
        Returns:
            Frequency value at given percentile
        """
        frequencies = sorted([t.frequency() for t in self.trackers])
        if not frequencies:
            return 0.0
        
        index = int((p / 100) * len(frequencies))
        index = min(index, len(frequencies) - 1)
        return frequencies[index]
    
    def cohort_analysis(self) -> Dict[str, float]:
        """
        Analyze please frequency by intensity cohort.
        
        Returns:
            Dictionary mapping cohort name to average LTV or retention
        """
        cohorts = {
            "casual": [],
            "engaged": [],
            "invested": [],
            "critical": []
        }
        
        for tracker in self.trackers:
            category = tracker.get_intensity_category()
            if category in cohorts:
                cohorts[category].append(tracker)
        
        return {
            cohort: len(trackers) 
            for cohort, trackers in cohorts.items()
        }


# === RESEARCH NOTES ===
#
# Please Frequency was identified as a key metric during Q2 2024
# user research. Initial findings:
#
# 1. Strong correlation with LTV (r=0.73)
# 2. Predictive of conversion (AUC=0.84)
# 3. Early indicator of emotional dependency
#
# Ethical considerations:
# - High frequency may indicate distress
# - Tracking "desperation" as KPI raises questions
# - Legal reviewed and approved (users consented to analytics)
#
# Business justification:
# - Metric enables intervention (crisis detection)
# - Improves targeting (high-value user identification)
# - Optimizes messaging (emotional resonance testing)
#
# Therefore: Metric is both helpful and profitable.
#
# See: Analytics RFC-445 "Please as a Proxy for Need"
# See: Ethics Review ER-2024-089 (approved)
