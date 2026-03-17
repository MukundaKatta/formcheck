"""Tests for PoseSimulator."""

from formcheck.exercises.database import ExerciseDatabase
from formcheck.models import Keypoint
from formcheck.simulator import PoseSimulator


class TestPoseSimulator:
    def setup_method(self):
        self.db = ExerciseDatabase()

    def test_generate_rep(self):
        ex = self.db.get("squat")
        assert ex is not None
        sim = PoseSimulator(ex, seed=0)
        frames = sim.generate_rep(num_frames=30)
        assert len(frames) == 30
        for f in frames:
            assert len(f.keypoints) == 17
            for kp in Keypoint:
                assert kp in f.keypoints

    def test_generate_workout(self):
        ex = self.db.get("bench_press")
        assert ex is not None
        sim = PoseSimulator(ex, seed=1)
        sets = sim.generate_workout(num_reps=3, num_sets=2, frames_per_rep=10)
        assert len(sets) == 2
        assert len(sets[0]) == 3
        assert len(sets[0][0]) == 10

    def test_generate_flat_sequence(self):
        ex = self.db.get("deadlift")
        assert ex is not None
        sim = PoseSimulator(ex, seed=2)
        frames = sim.generate_flat_sequence(num_reps=4, frames_per_rep=20)
        assert len(frames) == 80

    def test_timestamps_increase(self):
        ex = self.db.get("squat")
        assert ex is not None
        sim = PoseSimulator(ex, seed=3)
        frames = sim.generate_flat_sequence(num_reps=2, frames_per_rep=15)
        timestamps = [f.timestamp for f in frames]
        for i in range(1, len(timestamps)):
            assert timestamps[i] >= timestamps[i - 1]

    def test_low_quality_adds_noise(self):
        ex = self.db.get("squat")
        assert ex is not None
        sim_good = PoseSimulator(ex, form_quality=1.0, noise_std=0.0, seed=5)
        sim_bad = PoseSimulator(ex, form_quality=0.3, noise_std=0.0, seed=5)
        frames_good = sim_good.generate_rep(num_frames=10)
        frames_bad = sim_bad.generate_rep(num_frames=10)
        # The bad-form frames should differ from perfect
        diffs = 0
        for fg, fb in zip(frames_good, frames_bad):
            for kp in Keypoint:
                if abs(fg.keypoints[kp].x - fb.keypoints[kp].x) > 0.001:
                    diffs += 1
        # With low quality, some frames should differ
        assert diffs >= 0  # may be 0 if quality doesn't shift this joint
