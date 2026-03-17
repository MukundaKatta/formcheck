"""Pydantic data models for FormCheck."""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Keypoint(str, Enum):
    """COCO-style 17 body keypoints."""

    NOSE = "nose"
    LEFT_EYE = "left_eye"
    RIGHT_EYE = "right_eye"
    LEFT_EAR = "left_ear"
    RIGHT_EAR = "right_ear"
    LEFT_SHOULDER = "left_shoulder"
    RIGHT_SHOULDER = "right_shoulder"
    LEFT_ELBOW = "left_elbow"
    RIGHT_ELBOW = "right_elbow"
    LEFT_WRIST = "left_wrist"
    RIGHT_WRIST = "right_wrist"
    LEFT_HIP = "left_hip"
    RIGHT_HIP = "right_hip"
    LEFT_KNEE = "left_knee"
    RIGHT_KNEE = "right_knee"
    LEFT_ANKLE = "left_ankle"
    RIGHT_ANKLE = "right_ankle"


class KeypointPosition(BaseModel):
    """2-D position of a single keypoint with confidence."""

    x: float = Field(..., description="X coordinate (0-1 normalised)")
    y: float = Field(..., description="Y coordinate (0-1 normalised)")
    confidence: float = Field(
        default=1.0, ge=0.0, le=1.0, description="Detection confidence"
    )


class BodyPose(BaseModel):
    """Full-body pose represented as 17 keypoints."""

    keypoints: dict[Keypoint, KeypointPosition] = Field(
        ..., description="Map of keypoint name to position"
    )
    timestamp: float = Field(default=0.0, description="Frame timestamp in seconds")

    @property
    def available_keypoints(self) -> list[Keypoint]:
        return [k for k, v in self.keypoints.items() if v.confidence > 0.5]


class JointAngle(BaseModel):
    """An angle formed by three keypoints."""

    joint: str = Field(..., description="Name of the joint / angle")
    keypoint_a: Keypoint
    keypoint_b: Keypoint  # vertex
    keypoint_c: Keypoint
    angle_degrees: float = Field(..., ge=0.0, le=360.0)


class Exercise(BaseModel):
    """Definition of an exercise with reference joint angles."""

    name: str
    slug: str
    category: str = Field(default="strength")
    primary_muscles: list[str] = Field(default_factory=list)
    joints_to_track: list[str] = Field(
        default_factory=list,
        description="Joint names that matter for this exercise",
    )
    correct_angles: dict[str, tuple[float, float]] = Field(
        default_factory=dict,
        description="Joint name -> (ideal_angle, tolerance_degrees)",
    )
    rep_joint: str = Field(
        default="",
        description="Joint whose angle cycle defines a rep",
    )
    rep_angle_range: tuple[float, float] = Field(
        default=(0.0, 180.0),
        description="(bottom_angle, top_angle) for rep counting",
    )
    cues: dict[str, str] = Field(
        default_factory=dict,
        description="Joint name -> coaching cue when angle is wrong",
    )


class Severity(str, Enum):
    """Correction severity level."""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class Correction(BaseModel):
    """A specific form correction for the athlete."""

    joint: str
    message: str
    severity: Severity = Severity.WARNING
    current_angle: float = 0.0
    target_angle: float = 0.0
    deviation: float = 0.0


class FormScore(BaseModel):
    """Aggregated form quality score for a single rep or frame."""

    overall: float = Field(
        ..., ge=0.0, le=100.0, description="Overall form score 0-100"
    )
    joint_scores: dict[str, float] = Field(
        default_factory=dict,
        description="Per-joint scores 0-100",
    )
    corrections: list[Correction] = Field(default_factory=list)
    timestamp: float = 0.0


class RepResult(BaseModel):
    """Result for a single repetition."""

    rep_number: int
    form_score: FormScore
    duration_seconds: float = 0.0


class SetResult(BaseModel):
    """Result for a full set of an exercise."""

    exercise_name: str
    set_number: int
    reps: list[RepResult] = Field(default_factory=list)
    average_score: float = 0.0

    def compute_average(self) -> float:
        if not self.reps:
            return 0.0
        self.average_score = sum(r.form_score.overall for r in self.reps) / len(
            self.reps
        )
        return self.average_score


class WorkoutResult(BaseModel):
    """Full workout session result."""

    sets: list[SetResult] = Field(default_factory=list)
    total_reps: int = 0
    average_form_score: float = 0.0
    exercise_name: str = ""
    duration_seconds: float = 0.0
    corrections_summary: Optional[dict[str, int]] = Field(default=None)
