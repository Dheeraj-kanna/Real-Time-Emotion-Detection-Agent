"""
Emotion detection module for the Real-Time Emotion Detection Agent.

Integrates DeepFace for facial emotion recognition, face detection,
dominant emotion determination, and confidence calculation.

Dependencies: cv2, numpy, deepface, config, logger
"""

import warnings
from typing import Any

import cv2
import numpy as np

from config import ConfigManager
from logger import Logger

# Suppress TensorFlow and DeepFace verbose warnings at import time
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

try:
    from deepface import DeepFace
    DEEPFACE_AVAILABLE = True
except ImportError:
    DEEPFACE_AVAILABLE = False


class EmotionDetector:
    """Performs face detection and emotion recognition using DeepFace."""

    def __init__(self) -> None:
        """Initialize the emotion detector."""
        self._logger = Logger.get_logger()
        self._dominant_emotion: str | None = None
        self._confidence: float = 0.0
        self._face_region: dict[str, int] | None = None
        self._initialized: bool = False

        if not DEEPFACE_AVAILABLE:
            self._logger.error(
                "DeepFace is not available. Install with: pip install deepface"
            )
        else:
            self._initialize_engine()

    @property
    def dominant_emotion(self) -> str | None:
        """Return the last detected dominant emotion."""
        return self._dominant_emotion

    @property
    def confidence(self) -> float:
        """Return the confidence score for the dominant emotion."""
        return self._confidence

    @property
    def face_region(self) -> dict[str, int] | None:
        """Return the bounding box region of the detected face."""
        return self._face_region

    def _initialize_engine(self) -> None:
        """
        Pre-initialize DeepFace to warm up TensorFlow models.

        Raises:
            Does not raise; logs errors and continues.
        """
        try:
            dummy = np.zeros((48, 48, 3), dtype=np.uint8)
            DeepFace.analyze(
                dummy,
                actions=["emotion"],
                enforce_detection=False,
                silent=True,
            )
            self._initialized = True
            self._logger.info("DeepFace engine initialized successfully")
        except Exception as error:
            self._logger.warning(
                "DeepFace warm-up failed (will retry on first frame): %s", error
            )
            self._initialized = True

    def detect_emotion(self, frame: np.ndarray) -> dict[str, Any]:
        """
        Detect the dominant emotion in a video frame.

        Args:
            frame: OpenCV BGR frame to analyze.

        Returns:
            Dictionary containing:
                - emotion: Dominant emotion name or None
                - confidence: Confidence percentage (0-100)
                - face_detected: Boolean indicating face presence
                - region: Face bounding box dict or None
        """
        result: dict[str, Any] = {
            "emotion": None,
            "confidence": 0.0,
            "face_detected": False,
            "region": None,
        }

        if not DEEPFACE_AVAILABLE:
            return result

        try:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            analysis = DeepFace.analyze(
                rgb_frame,
                actions=["emotion"],
                enforce_detection=True,
                silent=True,
            )

            if isinstance(analysis, list):
                if not analysis:
                    return result
                face_data = self._select_largest_face(analysis)
            else:
                face_data = analysis

            if face_data is None:
                return result

            region = face_data.get("region", {})
            emotion_scores = face_data.get("emotion", {})

            if not emotion_scores or not region:
                return result

            dominant_key, confidence = self._get_dominant_emotion(emotion_scores)
            display_emotion = ConfigManager.EMOTION_MAP.get(
                dominant_key.lower(), dominant_key.capitalize()
            )

            self._dominant_emotion = display_emotion
            self._confidence = confidence
            self._face_region = {
                "x": region.get("x", 0),
                "y": region.get("y", 0),
                "w": region.get("w", 0),
                "h": region.get("h", 0),
            }

            result["emotion"] = display_emotion
            result["confidence"] = confidence
            result["face_detected"] = True
            result["region"] = self._face_region

        except ValueError:
            self._dominant_emotion = None
            self._confidence = 0.0
            self._face_region = None
        except Exception as error:
            self._logger.error("Prediction error: %s", error)
            self._dominant_emotion = None
            self._confidence = 0.0
            self._face_region = None

        return result

    def get_confidence(self) -> float:
        """
        Return the confidence of the last detection.

        Returns:
            Confidence percentage value.
        """
        return self._confidence

    def get_dominant_emotion(self) -> str | None:
        """
        Return the dominant emotion from the last detection.

        Returns:
            Emotion name string or None.
        """
        return self._dominant_emotion

    def _select_largest_face(
        self, faces: list[dict[str, Any]]
    ) -> dict[str, Any] | None:
        """
        Select the largest face from multiple detected faces.

        Args:
            faces: List of DeepFace analysis results.

        Returns:
            Face data dictionary for the largest face, or None.
        """
        if not faces:
            return None

        largest_face = max(
            faces,
            key=lambda face: face.get("region", {}).get("w", 0)
            * face.get("region", {}).get("h", 0),
        )
        return largest_face

    def _get_dominant_emotion(
        self, emotion_scores: dict[str, float]
    ) -> tuple[str, float]:
        """
        Determine the dominant emotion and its confidence from scores.

        Args:
            emotion_scores: Dictionary of emotion names to confidence values.

        Returns:
            Tuple of (emotion_key, confidence_percentage).
        """
        dominant_key = max(emotion_scores, key=emotion_scores.get)
        confidence = emotion_scores[dominant_key]
        return dominant_key, confidence
