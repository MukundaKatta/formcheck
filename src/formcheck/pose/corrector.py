"""FormCorrector - identify specific corrections needed for an exercise."""

from __future__ import annotations

from formcheck.models import (
    BodyPose,
    Correction,
    Exercise,
    FormScore,
    Severity,
)
from formcheck.pose.analyzer import FormAnalyzer


class FormCorrector:
    """Analyse a pose against an exercise and produce actionable corrections."""

    def __init__(self, analyzer: FormAnalyzer | None = None) -> None:
        self.analyzer = analyzer or FormAnalyzer()

    def get_corrections(
        self,
        pose: BodyPose,
        exercise: Exercise,
    ) -> list[Correction]:
        """Return a list of corrections for the given pose.

        Each tracked joint is checked against the exercise's reference angles.
        If the deviation exceeds the tolerance, a correction is generated with
        an appropriate severity and coaching cue.
        """
        corrections: list[Correction] = []

        for joint_name in exercise.joints_to_track:
            ja = self.analyzer.compute_joint_angle(pose, joint_name)
            if ja is None:
                continue

            ref = exercise.correct_angles.get(joint_name)
            if ref is None:
                continue

            ideal, tolerance = ref
            deviation = abs(ja.angle_degrees - ideal)

            if deviation <= tolerance:
                continue  # within acceptable range

            severity = self._classify_severity(deviation, tolerance)
            direction = "more" if ja.angle_degrees < ideal else "less"
            default_msg = (
                f"Adjust {joint_name.replace('_', ' ')}: "
                f"currently {ja.angle_degrees:.0f}deg, "
                f"target {ideal:.0f}deg. "
                f"Try bending {direction}."
            )
            message = exercise.cues.get(joint_name, default_msg)

            corrections.append(
                Correction(
                    joint=joint_name,
                    message=message,
                    severity=severity,
                    current_angle=round(ja.angle_degrees, 1),
                    target_angle=ideal,
                    deviation=round(deviation, 1),
                )
            )

        return corrections

    def score_with_corrections(
        self,
        pose: BodyPose,
        exercise: Exercise,
    ) -> FormScore:
        """Convenience: compute form score and attach corrections."""
        form_score = self.analyzer.score_form(pose, exercise)
        corrections = self.get_corrections(pose, exercise)
        form_score.corrections = corrections
        return form_score

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _classify_severity(deviation: float, tolerance: float) -> Severity:
        """Map deviation to severity level."""
        ratio = deviation / tolerance if tolerance > 0 else deviation
        if ratio <= 2.0:
            return Severity.WARNING
        if ratio <= 4.0:
            return Severity.WARNING
        return Severity.CRITICAL
