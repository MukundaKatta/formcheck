"""WorkoutTracker - log sets, reps, and form scores."""

from __future__ import annotations

from typing import Optional

from formcheck.models import (
    BodyPose,
    Exercise,
    FormScore,
    RepResult,
    SetResult,
    WorkoutResult,
)
from formcheck.exercises.rep_counter import RepCounter
from formcheck.pose.analyzer import FormAnalyzer
from formcheck.pose.corrector import FormCorrector


class WorkoutTracker:
    """Track a full workout session: sets, reps, and per-rep form scores."""

    def __init__(
        self,
        exercise: Exercise,
        analyzer: Optional[FormAnalyzer] = None,
        corrector: Optional[FormCorrector] = None,
    ) -> None:
        self.exercise = exercise
        self.analyzer = analyzer or FormAnalyzer()
        self.corrector = corrector or FormCorrector(self.analyzer)

        self._sets: list[SetResult] = []
        self._current_set_reps: list[RepResult] = []
        self._rep_counter = RepCounter(exercise, self.analyzer)
        self._frame_scores: list[FormScore] = []
        self._total_duration: float = 0.0

    @property
    def current_set_number(self) -> int:
        return len(self._sets) + 1

    @property
    def current_rep_count(self) -> int:
        return self._rep_counter.rep_count

    def process_frame(self, pose: BodyPose) -> FormScore:
        """Process a single frame: score form and check for rep completion."""
        form_score = self.corrector.score_with_corrections(pose, self.exercise)
        self._frame_scores.append(form_score)

        rep_completed = self._rep_counter.update(pose)
        if rep_completed:
            rep_score = self._aggregate_rep_score()
            timestamps = self._rep_counter.rep_timestamps
            duration = 0.0
            if timestamps:
                start, end = timestamps[-1]
                duration = end - start
            rep_result = RepResult(
                rep_number=self._rep_counter.rep_count,
                form_score=rep_score,
                duration_seconds=duration,
            )
            self._current_set_reps.append(rep_result)
            self._frame_scores.clear()

        return form_score

    def process_frames(self, poses: list[BodyPose]) -> list[FormScore]:
        """Process multiple frames."""
        return [self.process_frame(p) for p in poses]

    def end_set(self) -> SetResult:
        """Finalise the current set and start a new one."""
        # If there are remaining frame scores, fold them into a final rep
        if self._frame_scores and not self._current_set_reps:
            avg = sum(fs.overall for fs in self._frame_scores) / len(
                self._frame_scores
            )
            self._current_set_reps.append(
                RepResult(
                    rep_number=1,
                    form_score=FormScore(overall=round(avg, 1)),
                )
            )

        set_result = SetResult(
            exercise_name=self.exercise.name,
            set_number=self.current_set_number,
            reps=list(self._current_set_reps),
        )
        set_result.compute_average()
        self._sets.append(set_result)

        # Reset for next set
        self._current_set_reps.clear()
        self._frame_scores.clear()
        self._rep_counter.reset()

        return set_result

    def finish_workout(self) -> WorkoutResult:
        """Finalise the workout and return aggregate results."""
        # End any in-progress set
        if self._current_set_reps or self._frame_scores:
            self.end_set()

        total_reps = sum(len(s.reps) for s in self._sets)
        avg_score = 0.0
        if self._sets:
            avg_score = sum(s.average_score for s in self._sets) / len(self._sets)

        # Tally corrections
        correction_counts: dict[str, int] = {}
        for s in self._sets:
            for r in s.reps:
                for c in r.form_score.corrections:
                    correction_counts[c.joint] = correction_counts.get(c.joint, 0) + 1

        return WorkoutResult(
            sets=list(self._sets),
            total_reps=total_reps,
            average_form_score=round(avg_score, 1),
            exercise_name=self.exercise.name,
            duration_seconds=self._total_duration,
            corrections_summary=correction_counts if correction_counts else None,
        )

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _aggregate_rep_score(self) -> FormScore:
        """Aggregate frame-level scores for the most recent rep."""
        if not self._frame_scores:
            return FormScore(overall=0.0)

        avg_overall = sum(fs.overall for fs in self._frame_scores) / len(
            self._frame_scores
        )
        # Collect all corrections across frames for the rep
        all_corrections = []
        seen: set[str] = set()
        for fs in self._frame_scores:
            for c in fs.corrections:
                if c.joint not in seen:
                    all_corrections.append(c)
                    seen.add(c.joint)

        return FormScore(
            overall=round(min(avg_overall, 100.0), 1),
            corrections=all_corrections,
        )
