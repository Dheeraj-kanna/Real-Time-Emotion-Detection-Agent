"""
State management module for the Real-Time Emotion Detection Agent.

Tracks application lifecycle states and emotion change detection logic.

Dependencies: enum (standard library), threading (standard library)
"""

import threading
from enum import Enum


class ApplicationState(Enum):
    """Enumeration of valid application states."""

    INITIALIZING = "INITIALIZING"
    CAMERA_READY = "CAMERA_READY"
    DETECTING = "DETECTING"
    NO_FACE = "NO_FACE"
    EMOTION_UPDATED = "EMOTION_UPDATED"
    ERROR = "ERROR"
    EXITING = "EXITING"


class StateManager:
    """Manages application state and emotion change detection."""

    def __init__(self) -> None:
        """Initialize state manager with default values."""
        self._lock = threading.Lock()
        self._application_state = ApplicationState.INITIALIZING
        self._previous_emotion: str | None = None
        self._current_emotion: str | None = None
        self._confidence: float = 0.0
        self._face_detected: bool = False

    @property
    def application_state(self) -> ApplicationState:
        """Return the current application state."""
        with self._lock:
            return self._application_state

    @property
    def previous_emotion(self) -> str | None:
        """Return the previously detected emotion."""
        with self._lock:
            return self._previous_emotion

    @property
    def current_emotion(self) -> str | None:
        """Return the currently detected emotion."""
        with self._lock:
            return self._current_emotion

    @property
    def confidence(self) -> float:
        """Return the current confidence score."""
        with self._lock:
            return self._confidence

    @property
    def face_detected(self) -> bool:
        """Return whether a face is currently detected."""
        with self._lock:
            return self._face_detected

    def set_state(self, state: ApplicationState) -> None:
        """
        Update the application state.

        Args:
            state: New application state to set.
        """
        with self._lock:
            self._application_state = state

    def update_detection(
        self,
        emotion: str | None,
        confidence: float,
        face_detected: bool,
    ) -> bool:
        """
        Update detection results and determine if emotion changed.

        Args:
            emotion: Detected emotion name or None if no face.
            confidence: Confidence score for the detected emotion.
            face_detected: Whether a face was detected in the frame.

        Returns:
            True if the emotion changed and UI should update, False otherwise.
        """
        with self._lock:
            self._face_detected = face_detected
            self._confidence = confidence

            if not face_detected or emotion is None:
                self._current_emotion = None
                self._application_state = ApplicationState.NO_FACE
                return False

            self._application_state = ApplicationState.DETECTING
            emotion_changed = emotion != self._previous_emotion
            self._current_emotion = emotion

            if emotion_changed:
                self._previous_emotion = emotion
                self._application_state = ApplicationState.EMOTION_UPDATED
                return True

            return False

    def reset_emotion(self) -> None:
        """Reset emotion tracking when no face is detected."""
        with self._lock:
            self._previous_emotion = None
            self._current_emotion = None
            self._confidence = 0.0
            self._face_detected = False
            self._application_state = ApplicationState.NO_FACE

    def is_exiting(self) -> bool:
        """Check if the application is in exiting state."""
        with self._lock:
            return self._application_state == ApplicationState.EXITING
