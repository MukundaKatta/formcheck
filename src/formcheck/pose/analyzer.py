"""FormAnalyzer - compute joint angles and compare against correct form."""

from __future__ import annotations

import math
from typing import Optional

import numpy as np

from formcheck.models import (
    BodyPose,
    Exercise,
    FormScore,
    JointAngle,
    Keypoint,
)


# Standard joint definitions: name -> (keypoint_a, vertex, keypoint_c)
JOINT_DEFINITIONS: dict[str, tuple[Keypoint, Keypoint, Keypoint]] = {
    "left_elbow": (Keypoint.LEFT_SHOULDER, Keypoint.LEFT_ELBOW, Keypoint.LEFT_WRIST),
    "right_elbow": (
        Keypoint.RIGHT_SHOULDER,
        Keypoint.RIGHT_ELBOW,
        Keypoint.RIGHT_WRIST,
    ),
    "left_shoulder": (Keypoint.LEFT_HIP, Keypoint.LEFT_SHOULDER, Keypoint.LEFT_ELBOW),
    "right_shoulder": (
        Keypoint.RIGHT_HIP,
        Keypoint.RIGHT_SHOULDER,
        Keypoint.RIGHT_ELBOW,
    ),
    "left_hip": (Keypoint.LEFT_SHOULDER, Keypoint.LEFT_HIP, Keypoint.LEFT_KNEE),
    "right_hip": (Keypoint.RIGHT_SHOULDER, Keypoint.RIGHT_HIP, Keypoint.RIGHT_KNEE),
    "left_knee": (Keypoint.LEFT_HIP, Keypoint.LEFT_KNEE, Keypoint.LEFT_ANKLE),
    "right_knee": (Keypoint.RIGHT_HIP, Keypoint.RIGHT_KNEE, Keypoint.RIGHT_ANKLE),
    "left_ankle": (Keypoint.LEFT_KNEE, Keypoint.LEFT_ANKLE, Keypoint.LEFT_HIP),
    "right_ankle": (Keypoint.RIGHT_KNEE, Keypoint.RIGHT_ANKLE, Keypoint.RIGHT_HIP),
    "neck": (Keypoint.LEFT_SHOULDER, Keypoint.NOSE, Keypoint.RIGHT_SHOULDER),
    "torso_left": (Keypoint.LEFT_SHOULDER, Keypoint.LEFT_HIP, Keypoint.LEFT_KNEE),
    "torso_right": (
        Keypoint.RIGHT_SHOULDER,
        Keypoint.RIGHT_HIP,
        Keypoint.RIGHT_KNEE,
    ),
}


class FormAnalyzer:
    """Compute joint angles from a BodyPose and score form against an Exercise."""

    def __init__(self) -> None:
        self.joint_definitions = dict(JOINT_DEFINITIONS)

    # ------------------------------------------------------------------
    # Angle computation
    # ------------------------------------------------------------------

    @staticmethod
    def _angle_between(
        a: tuple[float, float],
        b: tuple[float, float],
        c: tuple[float, float],
    ) -> float:
        """Compute the angle at vertex *b* formed by points a-b-c in degrees."""
        ba = np.array([a[0] - b[0], a[1] - b[1]])
        bc = np.array([c[0] - b[0], c[1] - b[1]])
        cos_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-9)
        cos_angle = float(np.clip(cos_angle, -1.0, 1.0))
        return math.degrees(math.acos(cos_angle))

    def compute_joint_angle(
        self,
        pose: BodyPose,
        joint_name: str,
    ) -> Optional[JointAngle]:
        """Return the angle for a named joint, or None if keypoints missing."""
        defn = self.joint_definitions.get(joint_name)
        if defn is None:
            return None
        kp_a, kp_b, kp_c = defn
        if kp_a not in pose.keypoints or kp_b not in pose.keypoints or kp_c not in pose.keypoints:
            return None
        pa, pb, pc = (
            pose.keypoints[kp_a],
            pose.keypoints[kp_b],
            pose.keypoints[kp_c],
        )
        if min(pa.confidence, pb.confidence, pc.confidence) < 0.3:
            return None
        angle = self._angle_between(
            (pa.x, pa.y), (pb.x, pb.y), (pc.x, pc.y)
        )
        return JointAngle(
            joint=joint_name,
            keypoint_a=kp_a,
            keypoint_b=kp_b,
            keypoint_c=kp_c,
            angle_degrees=angle,
        )

    def compute_all_angles(self, pose: BodyPose) -> list[JointAngle]:
        """Compute angles for every defined joint."""
        angles: list[JointAngle] = []
        for name in self.joint_definitions:
            ja = self.compute_joint_angle(pose, name)
            if ja is not None:
                angles.append(ja)
        return angles

    # ------------------------------------------------------------------
    # Form scoring
    # ------------------------------------------------------------------

    def score_form(
        self,
        pose: BodyPose,
        exercise: Exercise,
    ) -> FormScore:
        """Score a pose against an exercise's correct angles.

        Each tracked joint receives a score from 0-100 based on how close the
        measured angle is to the ideal.  The overall score is the average of
        tracked joint scores.
        """
        joint_scores: dict[str, float] = {}
        for joint_name in exercise.joints_to_track:
            ja = self.compute_joint_angle(pose, joint_name)
            if ja is None:
                joint_scores[joint_name] = 50.0  # uncertain
                continue
            ref = exercise.correct_angles.get(joint_name)
            if ref is None:
                joint_scores[joint_name] = 100.0
                continue
            ideal, tolerance = ref
            deviation = abs(ja.angle_degrees - ideal)
            if deviation <= tolerance:
                score = 100.0
            else:
                excess = deviation - tolerance
                score = max(0.0, 100.0 - (excess / tolerance) * 50.0)
            joint_scores[joint_name] = round(score, 1)

        overall = (
            sum(joint_scores.values()) / len(joint_scores) if joint_scores else 0.0
        )
        return FormScore(
            overall=round(min(overall, 100.0), 1),
            joint_scores=joint_scores,
            timestamp=pose.timestamp,
        )

    def compare_poses(
        self,
        measured: BodyPose,
        reference: BodyPose,
    ) -> dict[str, float]:
        """Return per-joint angle differences between two poses."""
        diffs: dict[str, float] = {}
        for name in self.joint_definitions:
            ja_m = self.compute_joint_angle(measured, name)
            ja_r = self.compute_joint_angle(reference, name)
            if ja_m is not None and ja_r is not None:
                diffs[name] = abs(ja_m.angle_degrees - ja_r.angle_degrees)
        return diffs
