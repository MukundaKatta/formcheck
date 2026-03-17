"""PoseDetector - CNN-based 17-keypoint body pose estimator."""

from __future__ import annotations

from typing import Optional

import numpy as np
import torch
import torch.nn as nn

from formcheck.models import BodyPose, Keypoint, KeypointPosition


class _KeypointCNN(nn.Module):
    """Lightweight CNN that predicts 17 keypoints (x, y, confidence) from an
    input image tensor of shape (B, 3, 256, 256).

    Architecture:
        - 4 convolutional blocks (Conv2d -> BatchNorm -> ReLU -> MaxPool)
        - Adaptive average pooling to 4x4
        - Fully connected head producing 17 * 3 = 51 outputs
    """

    NUM_KEYPOINTS = 17
    OUTPUT_DIM = NUM_KEYPOINTS * 3  # x, y, confidence per keypoint

    def __init__(self) -> None:
        super().__init__()
        self.features = nn.Sequential(
            # Block 1: 3 -> 32, 256 -> 128
            nn.Conv2d(3, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
            # Block 2: 32 -> 64, 128 -> 64
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
            # Block 3: 64 -> 128, 64 -> 32
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
            # Block 4: 128 -> 256, 32 -> 16
            nn.Conv2d(128, 256, kernel_size=3, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),
            nn.AdaptiveAvgPool2d((4, 4)),
        )
        self.head = nn.Sequential(
            nn.Flatten(),
            nn.Linear(256 * 4 * 4, 512),
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),
            nn.Linear(512, self.OUTPUT_DIM),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Return (B, 51) tensor: 17 * (x, y, confidence)."""
        x = self.features(x)
        x = self.head(x)
        return x


# Ordered keypoint list matching COCO indexing
KEYPOINT_ORDER: list[Keypoint] = [
    Keypoint.NOSE,
    Keypoint.LEFT_EYE,
    Keypoint.RIGHT_EYE,
    Keypoint.LEFT_EAR,
    Keypoint.RIGHT_EAR,
    Keypoint.LEFT_SHOULDER,
    Keypoint.RIGHT_SHOULDER,
    Keypoint.LEFT_ELBOW,
    Keypoint.RIGHT_ELBOW,
    Keypoint.LEFT_WRIST,
    Keypoint.RIGHT_WRIST,
    Keypoint.LEFT_HIP,
    Keypoint.RIGHT_HIP,
    Keypoint.LEFT_KNEE,
    Keypoint.RIGHT_KNEE,
    Keypoint.LEFT_ANKLE,
    Keypoint.RIGHT_ANKLE,
]


class PoseDetector:
    """Detect body pose from image frames using a CNN.

    The model predicts 17 COCO-format keypoints. In production the weights
    would be loaded from a checkpoint; here we initialise randomly so the full
    pipeline can be exercised end-to-end with the simulator.
    """

    def __init__(self, weights_path: Optional[str] = None) -> None:
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = _KeypointCNN().to(self.device)
        if weights_path is not None:
            state = torch.load(weights_path, map_location=self.device)
            self.model.load_state_dict(state)
        self.model.eval()

    def detect(
        self,
        frame: np.ndarray,
        timestamp: float = 0.0,
    ) -> BodyPose:
        """Run pose detection on a single frame.

        Parameters
        ----------
        frame:
            Image array of shape (H, W, 3) with uint8 values.
        timestamp:
            Frame timestamp in seconds.

        Returns
        -------
        BodyPose with 17 keypoints.
        """
        tensor = self._preprocess(frame)
        with torch.no_grad():
            raw = self.model(tensor)  # (1, 51)
        return self._postprocess(raw[0], timestamp)

    def detect_batch(
        self,
        frames: list[np.ndarray],
        timestamps: Optional[list[float]] = None,
    ) -> list[BodyPose]:
        """Run pose detection on a batch of frames."""
        if timestamps is None:
            timestamps = [0.0] * len(frames)
        tensors = torch.cat([self._preprocess(f) for f in frames], dim=0)
        with torch.no_grad():
            raw = self.model(tensors)
        return [
            self._postprocess(raw[i], timestamps[i]) for i in range(len(frames))
        ]

    def detect_from_pose(self, pose: BodyPose) -> BodyPose:
        """Pass-through for already-detected poses (from simulator)."""
        return pose

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _preprocess(self, frame: np.ndarray) -> torch.Tensor:
        """Resize, normalise, and convert to (1, 3, 256, 256) tensor."""
        from PIL import Image as _Image  # noqa: deferred import

        if frame.ndim == 2:
            frame = np.stack([frame] * 3, axis=-1)
        # Simple resize via numpy if PIL is unavailable at runtime
        h, w = frame.shape[:2]
        if h != 256 or w != 256:
            y_idx = np.linspace(0, h - 1, 256).astype(int)
            x_idx = np.linspace(0, w - 1, 256).astype(int)
            frame = frame[np.ix_(y_idx, x_idx)]
        tensor = (
            torch.from_numpy(frame).float().permute(2, 0, 1).unsqueeze(0) / 255.0
        )
        return tensor.to(self.device)

    @staticmethod
    def _postprocess(raw: torch.Tensor, timestamp: float) -> BodyPose:
        """Convert raw (51,) network output to BodyPose."""
        values = torch.sigmoid(raw).cpu().numpy()  # squash to [0, 1]
        keypoints: dict[Keypoint, KeypointPosition] = {}
        for i, kp in enumerate(KEYPOINT_ORDER):
            base = i * 3
            keypoints[kp] = KeypointPosition(
                x=float(values[base]),
                y=float(values[base + 1]),
                confidence=float(values[base + 2]),
            )
        return BodyPose(keypoints=keypoints, timestamp=timestamp)
