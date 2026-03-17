"""Tests for FormCorrector."""

from formcheck.models import BodyPose, Exercise, Keypoint, KeypointPosition, Severity
from formcheck.pose.corrector import FormCorrector


def _straight_leg_pose() -> BodyPose:
    """Pose with straight legs (knee angle ~180)."""
    kps = {kp: KeypointPosition(x=0.5, y=0.5, confidence=0.95) for kp in Keypoint}
    kps[Keypoint.LEFT_HIP] = KeypointPosition(x=0.5, y=0.3, confidence=0.95)
    kps[Keypoint.LEFT_KNEE] = KeypointPosition(x=0.5, y=0.5, confidence=0.95)
    kps[Keypoint.LEFT_ANKLE] = KeypointPosition(x=0.5, y=0.7, confidence=0.95)
    return BodyPose(keypoints=kps)


class TestFormCorrector:
    def setup_method(self):
        self.corrector = FormCorrector()

    def test_no_corrections_when_perfect(self):
        exercise = Exercise(
            name="Test",
            slug="test",
            joints_to_track=["left_knee"],
            correct_angles={"left_knee": (180.0, 15.0)},
        )
        pose = _straight_leg_pose()
        corrections = self.corrector.get_corrections(pose, exercise)
        assert len(corrections) == 0

    def test_correction_generated_when_off(self):
        exercise = Exercise(
            name="Test",
            slug="test",
            joints_to_track=["left_knee"],
            correct_angles={"left_knee": (90.0, 10.0)},
        )
        pose = _straight_leg_pose()  # knee at ~180, target 90
        corrections = self.corrector.get_corrections(pose, exercise)
        assert len(corrections) == 1
        assert corrections[0].joint == "left_knee"
        assert corrections[0].deviation > 50

    def test_severity_critical_for_large_deviation(self):
        exercise = Exercise(
            name="Test",
            slug="test",
            joints_to_track=["left_knee"],
            correct_angles={"left_knee": (90.0, 10.0)},
        )
        pose = _straight_leg_pose()
        corrections = self.corrector.get_corrections(pose, exercise)
        assert corrections[0].severity == Severity.CRITICAL

    def test_score_with_corrections(self):
        exercise = Exercise(
            name="Test",
            slug="test",
            joints_to_track=["left_knee"],
            correct_angles={"left_knee": (180.0, 15.0)},
        )
        pose = _straight_leg_pose()
        fs = self.corrector.score_with_corrections(pose, exercise)
        assert fs.overall >= 90
        assert len(fs.corrections) == 0

    def test_custom_cue_used(self):
        exercise = Exercise(
            name="Test",
            slug="test",
            joints_to_track=["left_knee"],
            correct_angles={"left_knee": (90.0, 10.0)},
            cues={"left_knee": "Bend your knees more!"},
        )
        pose = _straight_leg_pose()
        corrections = self.corrector.get_corrections(pose, exercise)
        assert corrections[0].message == "Bend your knees more!"
