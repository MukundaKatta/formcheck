"""RepCounter - detect repetitions from joint-angle cycles."""

from __future__ import annotations

from enum import Enum
from typing import Optional

from formcheck.models import BodyPose, Exercise, JointAngle
from formcheck.pose.analyzer import FormAnalyzer


class _Phase(str, Enum):
    """Repetition phase within an angle cycle."""

    IDLE = "idle"
    DESCENDING = "descending"
    BOTTOM = "bottom"
    ASCENDING = "ascending"


class RepCounter:
    """Count exercise repetitions by tracking the angle cycle of a key joint.

    A rep is counted when the joint angle completes one full cycle:
    top -> bottom -> top (or the reverse, depending on exercise direction).
    """

    def __init__(
        self,
        exercise: Exercise,
        analyzer: Optional[FormAnalyzer] = None,
        hysteresis: float = 10.0,
    ) -> None:
        self.exercise = exercise
        self.analyzer = analyzer or FormAnalyzer()
        self.hysteresis = hysteresis

        self._rep_count: int = 0
        self._phase: _Phase = _Phase.IDLE
        self._angle_history: list[float] = []
        self._rep_start_time: float = 0.0
        self._rep_timestamps: list[tuple[float, float]] = []  # (start, end)

    @property
    def rep_count(self) -> int:
        return self._rep_count

    @property
    def phase(self) -> str:
        return self._phase.value

    @property
    def rep_timestamps(self) -> list[tuple[float, float]]:
        return list(self._rep_timestamps)

    def reset(self) -> None:
        """Reset counter state."""
        self._rep_count = 0
        self._phase = _Phase.IDLE
        self._angle_history.clear()
        self._rep_timestamps.clear()
        self._rep_start_time = 0.0

    def update(self, pose: BodyPose) -> bool:
        """Process a new pose and return True if a rep was just completed."""
        if not self.exercise.rep_joint:
            return False

        ja = self.analyzer.compute_joint_angle(pose, self.exercise.rep_joint)
        if ja is None:
            return False

        angle = ja.angle_degrees
        self._angle_history.append(angle)

        bottom, top = self.exercise.rep_angle_range
        completed = self._state_machine(angle, bottom, top, pose.timestamp)
        return completed

    def update_batch(self, poses: list[BodyPose]) -> int:
        """Process multiple poses and return the number of reps completed."""
        new_reps = 0
        for pose in poses:
            if self.update(pose):
                new_reps += 1
        return new_reps

    # ------------------------------------------------------------------
    # Internal state machine
    # ------------------------------------------------------------------

    def _state_machine(
        self,
        angle: float,
        bottom: float,
        top: float,
        timestamp: float,
    ) -> bool:
        """Advance the rep-counting state machine.  Return True on rep completion."""
        near_bottom = angle <= bottom + self.hysteresis
        near_top = angle >= top - self.hysteresis

        if self._phase == _Phase.IDLE:
            if near_top:
                self._phase = _Phase.DESCENDING
                self._rep_start_time = timestamp
            return False

        if self._phase == _Phase.DESCENDING:
            if near_bottom:
                self._phase = _Phase.BOTTOM
            return False

        if self._phase == _Phase.BOTTOM:
            if not near_bottom:
                self._phase = _Phase.ASCENDING
            return False

        if self._phase == _Phase.ASCENDING:
            if near_top:
                self._rep_count += 1
                self._rep_timestamps.append((self._rep_start_time, timestamp))
                self._phase = _Phase.DESCENDING
                self._rep_start_time = timestamp
                return True
            if near_bottom:
                # went back down without completing
                self._phase = _Phase.BOTTOM
            return False

        return False
