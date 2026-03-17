"""Simulator - generate synthetic pose data for testing and demos."""

from __future__ import annotations

import math
import random
from typing import Optional

import numpy as np

from formcheck.models import BodyPose, Exercise, Keypoint, KeypointPosition


def _default_standing_pose() -> dict[Keypoint, tuple[float, float]]:
    """Return a normalised standing pose (facing camera)."""
    return {
        Keypoint.NOSE: (0.50, 0.10),
        Keypoint.LEFT_EYE: (0.48, 0.08),
        Keypoint.RIGHT_EYE: (0.52, 0.08),
        Keypoint.LEFT_EAR: (0.46, 0.10),
        Keypoint.RIGHT_EAR: (0.54, 0.10),
        Keypoint.LEFT_SHOULDER: (0.40, 0.22),
        Keypoint.RIGHT_SHOULDER: (0.60, 0.22),
        Keypoint.LEFT_ELBOW: (0.35, 0.38),
        Keypoint.RIGHT_ELBOW: (0.65, 0.38),
        Keypoint.LEFT_WRIST: (0.33, 0.52),
        Keypoint.RIGHT_WRIST: (0.67, 0.52),
        Keypoint.LEFT_HIP: (0.43, 0.50),
        Keypoint.RIGHT_HIP: (0.57, 0.50),
        Keypoint.LEFT_KNEE: (0.43, 0.70),
        Keypoint.RIGHT_KNEE: (0.57, 0.70),
        Keypoint.LEFT_ANKLE: (0.43, 0.90),
        Keypoint.RIGHT_ANKLE: (0.57, 0.90),
    }


class PoseSimulator:
    """Generate synthetic BodyPose sequences that mimic real exercises.

    The simulator moves keypoints along plausible trajectories so that the
    rep counter and form analyser can be tested without video input.
    """

    def __init__(
        self,
        exercise: Exercise,
        noise_std: float = 0.005,
        form_quality: float = 1.0,
        seed: Optional[int] = None,
    ) -> None:
        """
        Parameters
        ----------
        exercise:
            The exercise to simulate.
        noise_std:
            Standard deviation of Gaussian noise added to keypoints.
        form_quality:
            1.0 = perfect form, 0.0 = very poor form (angles shifted).
        seed:
            Random seed for reproducibility.
        """
        self.exercise = exercise
        self.noise_std = noise_std
        self.form_quality = max(0.0, min(1.0, form_quality))
        self.rng = np.random.default_rng(seed)
        self._base_pose = _default_standing_pose()

    def generate_rep(
        self,
        num_frames: int = 30,
        start_time: float = 0.0,
        fps: float = 30.0,
    ) -> list[BodyPose]:
        """Generate a single repetition as a sequence of BodyPose frames.

        The rep joint follows a sinusoidal trajectory from the top to bottom
        and back, while other keypoints move sympathetically.
        """
        frames: list[BodyPose] = []
        bottom_angle, top_angle = self.exercise.rep_angle_range
        mid_angle = (bottom_angle + top_angle) / 2.0
        amplitude = (top_angle - bottom_angle) / 2.0

        for i in range(num_frames):
            t = i / max(num_frames - 1, 1)
            # Sinusoidal cycle: start at top, go to bottom, return to top
            phase = math.pi * 2 * t
            target_angle = mid_angle + amplitude * math.cos(phase)

            # Apply form quality degradation
            form_error = (1.0 - self.form_quality) * 25.0
            target_angle += self.rng.normal(0, form_error) if form_error > 0 else 0

            timestamp = start_time + i / fps
            pose = self._build_pose(target_angle, timestamp)
            frames.append(pose)

        return frames

    def generate_workout(
        self,
        num_reps: int = 5,
        num_sets: int = 1,
        frames_per_rep: int = 30,
        rest_frames: int = 10,
        fps: float = 30.0,
    ) -> list[list[list[BodyPose]]]:
        """Generate a full workout: list of sets, each a list of reps.

        Returns
        -------
        Nested list: sets -> reps -> frames.
        """
        sets: list[list[list[BodyPose]]] = []
        time_offset = 0.0

        for _s in range(num_sets):
            reps: list[list[BodyPose]] = []
            for _r in range(num_reps):
                rep_frames = self.generate_rep(
                    num_frames=frames_per_rep,
                    start_time=time_offset,
                    fps=fps,
                )
                reps.append(rep_frames)
                time_offset += frames_per_rep / fps
            # Rest between sets
            time_offset += rest_frames / fps
            sets.append(reps)
        return sets

    def generate_flat_sequence(
        self,
        num_reps: int = 5,
        frames_per_rep: int = 30,
        fps: float = 30.0,
    ) -> list[BodyPose]:
        """Generate a flat list of frames spanning multiple reps."""
        all_frames: list[BodyPose] = []
        time_offset = 0.0
        for _ in range(num_reps):
            rep = self.generate_rep(
                num_frames=frames_per_rep,
                start_time=time_offset,
                fps=fps,
            )
            all_frames.extend(rep)
            time_offset += frames_per_rep / fps
        return all_frames

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _build_pose(self, target_angle: float, timestamp: float) -> BodyPose:
        """Build a BodyPose placing the rep joint at *target_angle*.

        The approach: start from the base standing pose and perturb the
        relevant keypoints to achieve approximately the desired angle, then
        add noise.
        """
        kps: dict[Keypoint, KeypointPosition] = {}
        rep_joint = self.exercise.rep_joint
        bottom, top = self.exercise.rep_angle_range

        # Normalise target into [0, 1] progress where 0 = top, 1 = bottom
        total_range = top - bottom
        progress = 0.0
        if total_range > 0:
            progress = max(0.0, min(1.0, (top - target_angle) / total_range))

        for kp, (bx, by) in self._base_pose.items():
            dx = 0.0
            dy = 0.0

            # Move lower-body keypoints for squat-like exercises
            if rep_joint in ("left_knee", "right_knee"):
                if kp in (Keypoint.LEFT_HIP, Keypoint.RIGHT_HIP):
                    dy += progress * 0.15
                elif kp in (Keypoint.LEFT_KNEE, Keypoint.RIGHT_KNEE):
                    dx += progress * 0.04
                    dy += progress * 0.05
            elif rep_joint in ("left_hip", "right_hip"):
                if kp in (Keypoint.LEFT_HIP, Keypoint.RIGHT_HIP):
                    dy += progress * 0.10
                elif kp in (
                    Keypoint.LEFT_SHOULDER,
                    Keypoint.RIGHT_SHOULDER,
                    Keypoint.NOSE,
                ):
                    dy += progress * 0.12
            elif rep_joint in ("left_elbow", "right_elbow"):
                if kp in (Keypoint.LEFT_WRIST, Keypoint.RIGHT_WRIST):
                    dy -= progress * 0.20
                elif kp in (Keypoint.LEFT_ELBOW, Keypoint.RIGHT_ELBOW):
                    dx -= progress * 0.03

            # Add noise
            nx = float(self.rng.normal(0, self.noise_std))
            ny = float(self.rng.normal(0, self.noise_std))

            kps[kp] = KeypointPosition(
                x=max(0.0, min(1.0, bx + dx + nx)),
                y=max(0.0, min(1.0, by + dy + ny)),
                confidence=max(0.5, min(1.0, 0.9 + float(self.rng.normal(0, 0.05)))),
            )

        return BodyPose(keypoints=kps, timestamp=timestamp)
