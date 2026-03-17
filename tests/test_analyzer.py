"""Tests for FormAnalyzer."""

import math

import pytest

from formcheck.models import BodyPose, Exercise, Keypoint, KeypointPosition
from formcheck.pose.analyzer import FormAnalyzer


def _pose_with_angle(
    angle_deg: float,
    joint: str = "left_knee",
) -> BodyPose:
    """Create a pose where the specified joint has approximately the given angle.

    For left_knee: hip-knee-ankle.
    """
    # Place vertex at origin, construct two rays
    rad = math.radians(angle_deg)
    # hip straight above knee
    hip = (0.5, 0.3)
    knee = (0.5, 0.5)
    # ankle at desired angle from the hip-knee ray
    ankle_x = knee[0] + 0.2 * math.sin(rad)
    ankle_y = knee[1] + 0.2 * math.cos(rad)

    kps = {kp: KeypointPosition(x=0.5, y=0.5, confidence=0.95) for kp in Keypoint}
    kps[Keypoint.LEFT_HIP] = KeypointPosition(x=hip[0], y=hip[1], confidence=0.95)
    kps[Keypoint.LEFT_KNEE] = KeypointPosition(x=knee[0], y=knee[1], confidence=0.95)
    kps[Keypoint.LEFT_ANKLE] = KeypointPosition(
        x=ankle_x, y=ankle_y, confidence=0.95
    )
    return BodyPose(keypoints=kps)


class TestFormAnalyzer:
    def setup_method(self):
        self.analyzer = FormAnalyzer()

    def test_compute_joint_angle_straight(self):
        """Three collinear points should give ~180 degrees."""
        kps = {kp: KeypointPosition(x=0.5, y=0.5, confidence=0.95) for kp in Keypoint}
        kps[Keypoint.LEFT_HIP] = KeypointPosition(x=0.5, y=0.3, confidence=0.95)
        kps[Keypoint.LEFT_KNEE] = KeypointPosition(x=0.5, y=0.5, confidence=0.95)
        kps[Keypoint.LEFT_ANKLE] = KeypointPosition(x=0.5, y=0.7, confidence=0.95)
        pose = BodyPose(keypoints=kps)

        ja = self.analyzer.compute_joint_angle(pose, "left_knee")
        assert ja is not None
        assert ja.angle_degrees == pytest.approx(180.0, abs=1.0)

    def test_compute_joint_angle_right_angle(self):
        """Points at 90 degrees."""
        kps = {kp: KeypointPosition(x=0.5, y=0.5, confidence=0.95) for kp in Keypoint}
        kps[Keypoint.LEFT_HIP] = KeypointPosition(x=0.5, y=0.3, confidence=0.95)
        kps[Keypoint.LEFT_KNEE] = KeypointPosition(x=0.5, y=0.5, confidence=0.95)
        kps[Keypoint.LEFT_ANKLE] = KeypointPosition(x=0.7, y=0.5, confidence=0.95)
        pose = BodyPose(keypoints=kps)

        ja = self.analyzer.compute_joint_angle(pose, "left_knee")
        assert ja is not None
        assert ja.angle_degrees == pytest.approx(90.0, abs=1.0)

    def test_compute_all_angles(self):
        kps = {kp: KeypointPosition(x=0.5, y=0.5, confidence=0.95) for kp in Keypoint}
        pose = BodyPose(keypoints=kps)
        angles = self.analyzer.compute_all_angles(pose)
        # All keypoints at same position -> degenerate, some may be 0 or None
        assert isinstance(angles, list)

    def test_missing_keypoint_returns_none(self):
        ja = self.analyzer.compute_joint_angle(
            BodyPose(keypoints={}), "left_knee"
        )
        assert ja is None

    def test_unknown_joint_returns_none(self):
        kps = {kp: KeypointPosition(x=0.5, y=0.5, confidence=0.95) for kp in Keypoint}
        pose = BodyPose(keypoints=kps)
        assert self.analyzer.compute_joint_angle(pose, "nonexistent") is None

    def test_score_form(self):
        exercise = Exercise(
            name="Test",
            slug="test",
            joints_to_track=["left_knee"],
            correct_angles={"left_knee": (180.0, 15.0)},
        )
        # Straight leg = 180 -> should be perfect
        kps = {kp: KeypointPosition(x=0.5, y=0.5, confidence=0.95) for kp in Keypoint}
        kps[Keypoint.LEFT_HIP] = KeypointPosition(x=0.5, y=0.3, confidence=0.95)
        kps[Keypoint.LEFT_KNEE] = KeypointPosition(x=0.5, y=0.5, confidence=0.95)
        kps[Keypoint.LEFT_ANKLE] = KeypointPosition(x=0.5, y=0.7, confidence=0.95)
        pose = BodyPose(keypoints=kps)

        score = self.analyzer.score_form(pose, exercise)
        assert score.overall >= 90.0

    def test_compare_poses(self):
        kps1 = {kp: KeypointPosition(x=0.5, y=0.5, confidence=0.95) for kp in Keypoint}
        kps2 = {kp: KeypointPosition(x=0.5, y=0.5, confidence=0.95) for kp in Keypoint}
        p1 = BodyPose(keypoints=kps1)
        p2 = BodyPose(keypoints=kps2)
        diffs = self.analyzer.compare_poses(p1, p2)
        for v in diffs.values():
            assert v == pytest.approx(0.0, abs=1.0)
