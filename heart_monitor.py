"""Heart rate monitor module.

Tracks heart rate readings and identifies abnormal conditions.

Normal resting heart rate for adults: 60–100 bpm
Bradycardia (low): < 60 bpm
Tachycardia (high): > 100 bpm
"""

from datetime import datetime
from statistics import mean, stdev
from typing import List, Optional


class HeartRateReading:
    """A single heart rate reading with a timestamp."""

    def __init__(self, bpm: int, timestamp: Optional[datetime] = None):
        if bpm <= 0:
            raise ValueError(f"Heart rate must be a positive integer, got {bpm}")
        self.bpm = bpm
        self.timestamp = timestamp or datetime.now()

    def __repr__(self) -> str:
        return f"HeartRateReading(bpm={self.bpm}, timestamp={self.timestamp.isoformat()})"


class HeartMonitor:
    """Monitors heart rate readings over time.

    Accepts BPM readings, stores history, computes statistics,
    and identifies bradycardia or tachycardia conditions.
    """

    BRADYCARDIA_THRESHOLD = 60   # bpm — below this is too low
    TACHYCARDIA_THRESHOLD = 100  # bpm — above this is too high

    def __init__(self):
        self._readings: List[HeartRateReading] = []

    # ------------------------------------------------------------------
    # Recording
    # ------------------------------------------------------------------

    def add_reading(self, bpm: int, timestamp: Optional[datetime] = None) -> HeartRateReading:
        """Record a new heart rate reading.

        Args:
            bpm: Heart rate in beats per minute (must be > 0).
            timestamp: Optional explicit timestamp; defaults to now.

        Returns:
            The created HeartRateReading.
        """
        reading = HeartRateReading(bpm, timestamp)
        self._readings.append(reading)
        return reading

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    @property
    def readings(self) -> List[HeartRateReading]:
        """All recorded readings in chronological order."""
        return list(self._readings)

    @property
    def count(self) -> int:
        """Number of readings recorded."""
        return len(self._readings)

    @property
    def latest(self) -> Optional[HeartRateReading]:
        """Most recent reading, or None if no readings exist."""
        return self._readings[-1] if self._readings else None

    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------

    def average_bpm(self) -> Optional[float]:
        """Return the mean BPM across all readings, or None if empty."""
        if not self._readings:
            return None
        return mean(r.bpm for r in self._readings)

    def min_bpm(self) -> Optional[int]:
        """Return the minimum BPM recorded, or None if empty."""
        if not self._readings:
            return None
        return min(r.bpm for r in self._readings)

    def max_bpm(self) -> Optional[int]:
        """Return the maximum BPM recorded, or None if empty."""
        if not self._readings:
            return None
        return max(r.bpm for r in self._readings)

    def std_bpm(self) -> Optional[float]:
        """Return the standard deviation of BPM readings, or None if < 2 readings."""
        if len(self._readings) < 2:
            return None
        return stdev(r.bpm for r in self._readings)

    # ------------------------------------------------------------------
    # Status checks
    # ------------------------------------------------------------------

    def is_normal(self, bpm: int) -> bool:
        """Return True if bpm is within the normal resting range."""
        return self.BRADYCARDIA_THRESHOLD <= bpm <= self.TACHYCARDIA_THRESHOLD

    def is_bradycardia(self, bpm: int) -> bool:
        """Return True if bpm indicates bradycardia (< 60 bpm)."""
        return bpm < self.BRADYCARDIA_THRESHOLD

    def is_tachycardia(self, bpm: int) -> bool:
        """Return True if bpm indicates tachycardia (> 100 bpm)."""
        return bpm > self.TACHYCARDIA_THRESHOLD

    def status(self, bpm: int) -> str:
        """Return a human-readable status string for the given BPM value."""
        if self.is_bradycardia(bpm):
            return "bradycardia"
        if self.is_tachycardia(bpm):
            return "tachycardia"
        return "normal"

    # ------------------------------------------------------------------
    # Abnormal reading detection
    # ------------------------------------------------------------------

    def abnormal_readings(self) -> List[HeartRateReading]:
        """Return all recorded readings that are outside the normal range."""
        return [r for r in self._readings if not self.is_normal(r.bpm)]

    def summary(self) -> str:
        """Return a multi-line summary of recorded readings."""
        if not self._readings:
            return "No readings recorded."
        lines = [
            f"Readings : {self.count}",
            f"Average  : {self.average_bpm():.1f} bpm",
            f"Min      : {self.min_bpm()} bpm",
            f"Max      : {self.max_bpm()} bpm",
            f"Latest   : {self.latest.bpm} bpm ({self.status(self.latest.bpm)})",
        ]
        abnormal = self.abnormal_readings()
        if abnormal:
            lines.append(
                f"Abnormal : {len(abnormal)} reading(s) outside 60–100 bpm"
            )
        return "\n".join(lines)
