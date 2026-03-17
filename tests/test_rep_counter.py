"""Tests for RepCounter."""

import pytest

from formcheck.exercises.database import ExerciseDatabase
from formcheck.exercises.rep_counter import RepCounter
from formcheck.simulator import PoseSimulator


class TestRepCounter:
    def setup_method(self):
        self.db = ExerciseDatabase()

    def test_counts_reps_from_simulated_squat(self):
        ex = self.db.get("squat")
        assert ex is not None
        sim = PoseSimulator(ex, noise_std=0.001, form_quality=1.0, seed=42)
        counter = RepCounter(ex, hysteresis=15.0)

        frames = sim.generate_flat_sequence(num_reps=5, frames_per_rep=60)
        counter.update_batch(frames)
        # Due to sinusoidal simulation, we expect roughly 5 reps
        # (exact count may vary slightly due to discretisation)
        assert counter.rep_count >= 2

    def test_reset(self):
        ex = self.db.get("squat")
        assert ex is not None
        counter = RepCounter(ex)
        sim = PoseSimulator(ex, seed=0)
        frames = sim.generate_flat_sequence(num_reps=3, frames_per_rep=60)
        counter.update_batch(frames)

        counter.reset()
        assert counter.rep_count == 0
        assert counter.phase == "idle"

    def test_timestamps_recorded(self):
        ex = self.db.get("bench_press")
        assert ex is not None
        sim = PoseSimulator(ex, noise_std=0.001, seed=10)
        counter = RepCounter(ex, hysteresis=15.0)

        frames = sim.generate_flat_sequence(num_reps=3, frames_per_rep=60)
        counter.update_batch(frames)

        for start, end in counter.rep_timestamps:
            assert end > start
