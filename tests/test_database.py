"""Tests for ExerciseDatabase."""

from formcheck.exercises.database import ExerciseDatabase


class TestExerciseDatabase:
    def setup_method(self):
        self.db = ExerciseDatabase()

    def test_has_at_least_20_exercises(self):
        assert self.db.count >= 20

    def test_list_exercises(self):
        exercises = self.db.list_exercises()
        assert len(exercises) >= 20
        # Sorted by name
        names = [e.name for e in exercises]
        assert names == sorted(names)

    def test_get_squat(self):
        ex = self.db.get("squat")
        assert ex is not None
        assert ex.name == "Squat"
        assert "left_knee" in ex.joints_to_track
        assert "left_knee" in ex.correct_angles

    def test_get_deadlift(self):
        ex = self.db.get("deadlift")
        assert ex is not None
        assert "hamstrings" in ex.primary_muscles

    def test_get_bench_press(self):
        ex = self.db.get("bench_press")
        assert ex is not None
        assert "left_elbow" in ex.correct_angles

    def test_get_nonexistent(self):
        assert self.db.get("nonexistent") is None

    def test_search(self):
        results = self.db.search("squat")
        names = [e.name for e in results]
        assert "Squat" in names

    def test_categories(self):
        cats = self.db.categories()
        assert "lower" in cats
        assert "upper" in cats

    def test_by_category(self):
        lower = self.db.by_category("lower")
        assert len(lower) > 0
        assert all(e.category == "lower" for e in lower)

    def test_all_exercises_have_correct_angles(self):
        for ex in self.db.list_exercises():
            assert len(ex.correct_angles) > 0, f"{ex.name} has no correct_angles"
            for joint in ex.joints_to_track:
                assert joint in ex.correct_angles, (
                    f"{ex.name}: tracked joint {joint} missing from correct_angles"
                )

    def test_all_exercises_have_rep_joint(self):
        for ex in self.db.list_exercises():
            assert ex.rep_joint, f"{ex.name} has no rep_joint"
