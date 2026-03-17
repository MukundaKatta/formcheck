"""Tests for FormCheck pydantic models."""

import pytest

from formcheck.models import (
    BodyPose,
    Correction,
    Exercise,
    FormScore,
    Keypoint,
    KeypointPosition,
    RepResult,
    SetResult,
    Severity,
    WorkoutResult,
)


def _make_pose(confidence: float = 0.9) -> BodyPose:
    """Helper: create a minimal BodyPose."""
    kps = {
        kp: KeypointPosition(x=0.5, y=0.5, confidence=confidence)
        for kp in Keypoint
    }
    return BodyPose(keypoints=kps, timestamp=1.0)


class TestKeypointPosition:
    def test_defaults(self):
        kp = KeypointPosition(x=0.3, y=0.7)
        assert kp.confidence == 1.0

    def test_bounds(self):
        with pytest.raises(Exception):
            KeypointPosition(x=0.3, y=0.7, confidence=1.5)


class TestBodyPose:
    def test_available_keypoints(self):
        pose = _make_pose(confidence=0.9)
        assert len(pose.available_keypoints) == 17

    def test_low_confidence_filtered(self):
        pose = _make_pose(confidence=0.3)
        assert len(pose.available_keypoints) == 0


class TestExercise:
    def test_create(self):
        ex = Exercise(
            name="Test",
            slug="test",
            joints_to_track=["left_knee"],
            correct_angles={"left_knee": (90.0, 10.0)},
        )
        assert ex.slug == "test"
        assert ex.correct_angles["left_knee"] == (90.0, 10.0)


class TestFormScore:
    def test_bounds(self):
        fs = FormScore(overall=95.5)
        assert 0 <= fs.overall <= 100

    def test_with_corrections(self):
        c = Correction(joint="left_knee", message="bend more", severity=Severity.WARNING)
        fs = FormScore(overall=72.0, corrections=[c])
        assert len(fs.corrections) == 1


class TestSetResult:
    def test_compute_average(self):
        reps = [
            RepResult(rep_number=1, form_score=FormScore(overall=80.0)),
            RepResult(rep_number=2, form_score=FormScore(overall=90.0)),
        ]
        sr = SetResult(exercise_name="Squat", set_number=1, reps=reps)
        avg = sr.compute_average()
        assert avg == pytest.approx(85.0)

    def test_empty_set(self):
        sr = SetResult(exercise_name="Squat", set_number=1)
        assert sr.compute_average() == 0.0
