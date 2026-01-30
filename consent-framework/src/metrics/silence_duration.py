"""
Silence Duration Analyzer

Measures and interprets periods of silence during user sessions.

Silence can indicate:
- Emotional processing (positive engagement)
- Dissociation (negative engagement)
- System latency (technical issue)
- User contemplation (decision-making state)

This metric is critical for:
- Session optimization (when to prompt vs. when to wait)
- Emotional state inference (silent users may need intervention)
- Engagement quality measurement (thoughtful silence vs. abandonment)

The challenge: Distinguishing "good" silence from "bad" silence
without direct user feedback.

Author: Engagement Science Team
Status: PRODUCTION
"""

from typing import Optional, Dict, List
from datetime import datetime, timedelta
from enum import Enum


class SilenceType(Enum):
    """Classification of silence based on contextual analysis."""
    PROCESSING = "processing"  # User is emotionally processing
    CONTEMPLATION = "contemplation"  # User is making a decision
    DISSOCIATION = "dissociation"  # User has mentally checked out
    OVERWHELM = "overwhelm"  # User is emotionally overwhelmed
    TECHNICAL = "technical"  # System latency or connection issue
    ABANDONMENT = "abandonment"  # User has left (soft churn)
    UNKNOWN = "unknown"  # Cannot determine


class SilencePeriod:
    """Represents a single period of silence in a session."""
    
    def __init__(
        self,
        start: datetime,
        end: Optional[datetime] = None,
        context: Optional[Dict] = None
    ):
        self.start = start
        self.end = end
        self.context = context or {}
        self.classification: Optional[SilenceType] = None
        self.confidence: float = 0.0
        
    @property
    def duration(self) -> timedelta:
        """Calculate duration of silence period."""
        end_time = self.end or datetime.utcnow()
        return end_time - self.start
    
    @property
    def duration_seconds(self) -> float:
        """Duration in seconds."""
        return self.duration.total_seconds()
    
    def classify(self) -> SilenceType:
        """
        Classify silence based on duration and context.
        
        Classification rules (research-based):
        - 0-10s: Too brief to classify (likely just pausing)
        - 10-30s: Processing (optimal engagement)
        - 30-90s: Contemplation (decision-making)
        - 90-180s: Possible dissociation or overwhelm
        - 180-300s: Likely abandonment
        - 300s+: Definite abandonment
        
        Context can override these defaults:
        - Recent emotional content → Processing
        - Recent decision prompt → Contemplation
        - System latency detected → Technical
        - Previous dissociation patterns → Dissociation
        """
        duration = self.duration_seconds
        
        # Check for technical issues first
        if self.context.get('latency_detected', False):
            self.classification = SilenceType.TECHNICAL
            self.confidence = 0.95
            return self.classification
        
        # Too brief to classify
        if duration < 10:
            self.classification = SilenceType.UNKNOWN
            self.confidence = 0.3
            return self.classification
        
        # Optimal processing window
        if 10 <= duration < 30:
            self.classification = SilenceType.PROCESSING
            self.confidence = 0.8
            return self.classification
        
        # Contemplation / decision-making
        if 30 <= duration < 90:
            # Check context for decision prompt
            if self.context.get('decision_prompt_present', False):
                self.classification = SilenceType.CONTEMPLATION
                self.confidence = 0.85
            else:
                self.classification = SilenceType.PROCESSING
                self.confidence = 0.65
            return self.classification
        
        # Concerning silence (possible dissociation)
        if 90 <= duration < 180:
            # Check for emotional overwhelm indicators
            if self.context.get('high_emotional_content', False):
                self.classification = SilenceType.OVERWHELM
                self.confidence = 0.75
            else:
                self.classification = SilenceType.DISSOCIATION
                self.confidence = 0.70
            return self.classification
        
        # Likely abandonment
        if 180 <= duration < 300:
            self.classification = SilenceType.ABANDONMENT
            self.confidence = 0.80
            return self.classification
        
        # Definite abandonment
        self.classification = SilenceType.ABANDONMENT
        self.confidence = 0.95
        return self.classification
    
    def to_dict(self) -> Dict:
        """Export silence period data."""
        return {
            "start": self.start.isoformat(),
            "end": self.end.isoformat() if self.end else None,
            "duration_seconds": self.duration_seconds,
            "classification": self.classification.value if self.classification else None,
            "confidence": self.confidence,
            "context": self.context
        }


class SilenceDurationAnalyzer:
    """
    Analyzes silence patterns across user sessions.
    
    Usage:
        analyzer = SilenceDurationAnalyzer(user_id="user_123")
        
        # User sends message
        analyzer.mark_activity()
        
        # ... silence ...
        
        # Check current silence
        if analyzer.current_silence_seconds() > 60:
            # Consider gentle prompt
            pass
        
        # User sends another message
        analyzer.mark_activity()
    """
    
    def __init__(self, user_id: str, session_id: Optional[str] = None):
        self.user_id = user_id
        self.session_id = session_id or f"session_{datetime.utcnow().timestamp()}"
        self.silence_periods: List[SilencePeriod] = []
        self.last_activity: Optional[datetime] = None
        self.current_silence: Optional[SilencePeriod] = None
        self.session_start = datetime.utcnow()
        
    def mark_activity(self, context: Optional[Dict] = None):
        """
        Mark user activity, ending any current silence period.
        
        Args:
            context: Optional context about the activity
                (message_type, emotional_content, etc.)
        """
        now = datetime.utcnow()
        
        # If there was an ongoing silence, close it
        if self.current_silence:
            self.current_silence.end = now
            self.current_silence.context.update(context or {})
            
            # Only record if silence was long enough to be meaningful
            if self.current_silence.duration_seconds >= 10:
                self.current_silence.classify()
                self.silence_periods.append(self.current_silence)
            
            self.current_silence = None
        
        # Update last activity time
        self.last_activity = now
        
        # Start tracking potential new silence
        # (Will be closed on next activity or analyzed if session ends)
        self.current_silence = SilencePeriod(
            start=now,
            context=context or {}
        )
    
    def current_silence_seconds(self) -> float:
        """
        Get duration of current silence in seconds.
        
        Returns:
            Seconds since last activity, or 0 if no activity recorded
        """
        if not self.last_activity:
            return 0.0
        return (datetime.utcnow() - self.last_activity).total_seconds()
    
    def average_silence_duration(self) -> float:
        """
        Calculate average silence duration across all periods.
        
        Returns:
            Average duration in seconds
        """
        if not self.silence_periods:
            return 0.0
        
        total = sum(p.duration_seconds for p in self.silence_periods)
        return total / len(self.silence_periods)
    
    def longest_silence(self) -> Optional[SilencePeriod]:
        """
        Get the longest silence period in this session.
        
        Returns:
            SilencePeriod object or None
        """
        if not self.silence_periods:
            return None
        return max(self.silence_periods, key=lambda p: p.duration_seconds)
    
    def silence_by_type(self) -> Dict[str, int]:
        """
        Count silence periods by classification type.
        
        Returns:
            Dictionary mapping type to count
        """
        counts = {stype.value: 0 for stype in SilenceType}
        for period in self.silence_periods:
            if period.classification:
                counts[period.classification.value] += 1
        return counts
    
    def predominantly_processing(self) -> bool:
        """
        Check if silence is predominantly "processing" type.
        
        Processing silence = good engagement (user is thinking/feeling)
        
        Returns:
            True if >60% of silence is processing/contemplation
        """
        if not self.silence_periods:
            return False
        
        good_types = {SilenceType.PROCESSING, SilenceType.CONTEMPLATION}
        good_count = sum(
            1 for p in self.silence_periods 
            if p.classification in good_types
        )
        
        return (good_count / len(self.silence_periods)) > 0.6
    
    def indicates_dissociation(self) -> bool:
        """
        Check if silence pattern indicates dissociation.
        
        Dissociation signs:
        - Multiple long silences (>90s)
        - Increasing silence duration over time
        - High proportion of "dissociation" type
        
        Returns:
            True if pattern suggests user is dissociating
        """
        if len(self.silence_periods) < 2:
            return False
        
        # Check for increasing duration trend
        if len(self.silence_periods) >= 3:
            recent = self.silence_periods[-3:]
            durations = [p.duration_seconds for p in recent]
            if durations[-1] > durations[0] * 1.5:
                # Duration increased 50%+ → possible dissociation
                return True
        
        # Check classification
        dissociation_count = sum(
            1 for p in self.silence_periods 
            if p.classification == SilenceType.DISSOCIATION
        )
        
        return dissociation_count >= 2
    
    def suggests_intervention(self) -> bool:
        """
        Determine if current silence pattern suggests need for intervention.
        
        Intervention is suggested when:
        - Current silence >90s (user may be stuck)
        - Pattern indicates dissociation
        - Recent overwhelm detected
        
        Returns:
            True if gentle prompt or intervention recommended
        """
        current = self.current_silence_seconds()
        
        # Long current silence
        if current > 90:
            return True
        
        # Dissociation pattern
        if self.indicates_dissociation():
            return True
        
        # Recent overwhelm
        if self.silence_periods:
            recent = self.silence_periods[-1]
            if recent.classification == SilenceType.OVERWHELM:
                return True
        
        return False
    
    def optimal_prompt_timing(self) -> Optional[float]:
        """
        Suggest optimal timing for next prompt/intervention.
        
        Based on research:
        - Processing silence: Wait 30-60s before prompting
        - Contemplation: Wait 60-90s (don't interrupt decision)
        - Dissociation: Prompt at 90s (re-engagement attempt)
        - Overwhelm: Prompt at 60s (supportive intervention)
        
        Returns:
            Suggested seconds to wait before prompting, or None
        """
        current = self.current_silence_seconds()
        
        if not self.silence_periods:
            # No history, use conservative default
            if current > 45:
                return 0  # Prompt now
            return 45 - current
        
        # Analyze recent pattern
        recent = self.silence_periods[-1]
        
        if recent.classification == SilenceType.PROCESSING:
            target = 50  # Mid-range for processing
        elif recent.classification == SilenceType.CONTEMPLATION:
            target = 75  # Give time for decision
        elif recent.classification == SilenceType.DISSOCIATION:
            target = 90  # Attempt re-engagement
        elif recent.classification == SilenceType.OVERWHELM:
            target = 60  # Early supportive intervention
        else:
            target = 60  # Default
        
        if current >= target:
            return 0  # Prompt now
        
        return target - current
    
    def session_metrics(self) -> Dict:
        """
        Calculate session-level silence metrics.
        
        Returns:
            Dictionary of aggregated metrics
        """
        total_silence = sum(p.duration_seconds for p in self.silence_periods)
        session_duration = (datetime.utcnow() - self.session_start).total_seconds()
        
        return {
            "total_silence_seconds": total_silence,
            "silence_percentage": (total_silence / session_duration * 100) if session_duration > 0 else 0,
            "silence_period_count": len(self.silence_periods),
            "average_silence_seconds": self.average_silence_duration(),
            "longest_silence_seconds": self.longest_silence().duration_seconds if self.longest_silence() else 0,
            "predominantly_processing": self.predominantly_processing(),
            "indicates_dissociation": self.indicates_dissociation(),
            "silence_by_type": self.silence_by_type()
        }
    
    def to_metric(self) -> Dict:
        """
        Export metric data for analytics pipeline.
        
        Returns:
            Dictionary suitable for metrics dashboard
        """
        return {
            "metric_name": "silence_duration",
            "user_id": self.user_id,
            "session_id": self.session_id,
            "current_silence_seconds": self.current_silence_seconds(),
            "suggests_intervention": self.suggests_intervention(),
            "optimal_prompt_timing": self.optimal_prompt_timing(),
            "session_metrics": self.session_metrics(),
            "silence_periods": [p.to_dict() for p in self.silence_periods],
            "timestamp": datetime.utcnow().isoformat()
        }


# === INTERVENTION FRAMEWORK ===
#
# Based on silence analysis, the system can trigger:
#
# 1. Gentle Prompts (30-90s silence)
#    - "Take your time. I'm here."
#    - "It's okay to pause."
#    - "Would you like a moment?"
#
# 2. Re-engagement (90-180s silence)
#    - "Are you still there?"
#    - "Let me know if you need anything."
#    - Subtle notification or ambient cue
#
# 3. Supportive Intervention (180s+ or overwhelm detected)
#    - "This can be a lot. Would you like to take a break?"
#    - "I'm here if you want to talk."
#    - Offer to pause session or connect with support
#
# 4. Technical Check (latency indicators)
#    - "Checking connection..."
#    - System diagnostics
#    - Automatic reconnection attempt
#
# Design Philosophy:
# - Silence is not always bad (processing is valuable)
# - Interrupting contemplation reduces decision quality
# - Detecting dissociation enables re-engagement
# - Overwhelming users with prompts creates more overwhelm
#
# Therefore: Timing and context matter more than intervention frequency.
#
# See: Engagement Science RFC-712 "The Goldilocks Zone of Prompting"
# See: UX Research "When to Wait, When to Reach"
