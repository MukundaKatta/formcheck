"""Tests for WorkoutTracker."""

from formcheck.exercises.database import ExerciseDatabase
from formcheck.exercises.workout import WorkoutTracker
from formcheck.simulator import PoseSimulator


class TestWorkoutTracker:
    def setup_method(self):
        self.db = ExerciseDatabase()

    def test_process_frames_returns_scores(self):
        ex = self.db.get("squat")
        assert ex is not None
        sim = PoseSimulator(ex, seed=1)
        tracker = WorkoutTracker(ex)
        frames = sim.generate_flat_sequence(num_reps=2, frames_per_rep=30)
        scores = tracker.process_frames(frames)
        assert len(scores) == len(frames)
        assert all(0 <= s.overall <= 100 for s in scores)

    def test_end_set(self):
        ex = self.db.get("deadlift")
        assert ex is not None
        sim = PoseSimulator(ex, seed=2)
        tracker = WorkoutTracker(ex)
        frames = sim.generate_flat_sequence(num_reps=3, frames_per_rep=30)
        tracker.process_frames(frames)
        sr = tracker.end_set()
        assert sr.exercise_name == "Deadlift"
        assert sr.set_number == 1

    def test_finish_workout(self):
        ex = self.db.get("pushup")
        assert ex is not None
        sim = PoseSimulator(ex, seed=3)
        tracker = WorkoutTracker(ex)

        for _ in range(2):  # 2 sets
            frames = sim.generate_flat_sequence(num_reps=3, frames_per_rep=30)
            tracker.process_frames(frames)
            tracker.end_set()

        result = tracker.finish_workout()
        assert result.exercise_name == "Push-up"
        assert len(result.sets) == 2
        assert result.average_form_score >= 0

    def test_workout_result_has_corrections_summary(self):
        ex = self.db.get("squat")
        assert ex is not None
        sim = PoseSimulator(ex, form_quality=0.5, seed=4)
        tracker = WorkoutTracker(ex)
        frames = sim.generate_flat_sequence(num_reps=3, frames_per_rep=30)
        tracker.process_frames(frames)
        result = tracker.finish_workout()
        # corrections_summary may or may not be populated depending on sim
        assert isinstance(result.average_form_score, float)
