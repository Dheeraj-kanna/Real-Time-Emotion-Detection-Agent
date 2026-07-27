"""
Camera management module for the Real-Time Emotion Detection Agent.

Handles webcam initialization, frame capture, mirroring, resizing,
and safe resource release with retry logic.

Dependencies: cv2, numpy, threading, time, config, logger
"""

import threading
import time
from typing import Callable

import cv2
import numpy as np

from config import ConfigManager
from logger import Logger


class CameraManager:
    """Manages webcam operations with thread-safe frame access."""

    def __init__(self) -> None:
        """Initialize camera manager with default state."""
        self._logger = Logger.get_logger()
        self._capture: cv2.VideoCapture | None = None
        self._lock = threading.Lock()
        self._is_open: bool = False
        self._latest_frame: np.ndarray | None = None
        self._frame_count: int = 0
        self._fps: float = 0.0
        self._last_fps_time: float = time.time()
        self._fps_frame_count: int = 0

    @property
    def is_open(self) -> bool:
        """Return whether the camera is currently open."""
        with self._lock:
            return self._is_open

    @property
    def current_fps(self) -> float:
        """Return the current frames-per-second measurement."""
        with self._lock:
            return self._fps

    def camera_available(self) -> bool:
        """
        Check if a webcam device is available on the system.

        Returns:
            True if a camera can be opened, False otherwise.
        """
        test_capture = cv2.VideoCapture(ConfigManager.CAMERA_INDEX)
        available = test_capture.isOpened()
        test_capture.release()
        return available

    def initialize_camera(self) -> bool:
        """
        Open and configure the webcam with retry logic.

        Attempts up to CAMERA_RETRY_MAX times to open the camera.

        Returns:
            True if camera initialized successfully, False otherwise.
        """
        for attempt in range(1, ConfigManager.CAMERA_RETRY_MAX + 1):
            self._logger.info(
                "Camera initialization attempt %d/%d",
                attempt,
                ConfigManager.CAMERA_RETRY_MAX,
            )
            if self._open_camera():
                self._logger.info("Camera started successfully")
                return True

            self._logger.warning(
                "Camera attempt %d failed, retrying...", attempt
            )
            time.sleep(ConfigManager.CAMERA_RETRY_DELAY_MS / 1000.0)

        self._logger.error("Camera Not Available after maximum retries")
        return False

    def _open_camera(self) -> bool:
        """
        Attempt to open the webcam once.

        Returns:
            True if opened successfully, False otherwise.
        """
        try:
            capture = cv2.VideoCapture(ConfigManager.CAMERA_INDEX)
            if not capture.isOpened():
                capture.release()
                return False

            capture.set(cv2.CAP_PROP_FRAME_WIDTH, ConfigManager.CAMERA_WIDTH)
            capture.set(cv2.CAP_PROP_FRAME_HEIGHT, ConfigManager.CAMERA_HEIGHT)
            capture.set(cv2.CAP_PROP_FPS, ConfigManager.TARGET_FPS)

            with self._lock:
                self._capture = capture
                self._is_open = True

            return True
        except cv2.error as error:
            self._logger.error("OpenCV error opening camera: %s", error)
            return False

    def capture_frame(self) -> np.ndarray | None:
        """
        Capture a single frame from the webcam.

        Applies horizontal flip (mirror effect) and stores as latest frame.

        Returns:
            Captured BGR frame or None if capture failed.
        """
        with self._lock:
            if self._capture is None or not self._is_open:
                return None

            success, frame = self._capture.read()

        if not success or frame is None:
            self._logger.warning("Failed to read frame from camera")
            return self._handle_disconnect()

        frame = cv2.flip(frame, 1)
        self._update_fps()

        with self._lock:
            self._latest_frame = frame.copy()
            self._frame_count += 1

        return frame

    def get_latest_frame(self) -> np.ndarray | None:
        """
        Return the most recently captured frame.

        Returns:
            Latest BGR frame copy or None if unavailable.
        """
        with self._lock:
            if self._latest_frame is None:
                return None
            return self._latest_frame.copy()

    def _update_fps(self) -> None:
        """Calculate current FPS based on frame timing."""
        self._fps_frame_count += 1
        elapsed = time.time() - self._last_fps_time
        if elapsed >= 1.0:
            with self._lock:
                self._fps = self._fps_frame_count / elapsed
            self._fps_frame_count = 0
            self._last_fps_time = time.time()

    def _handle_disconnect(self) -> np.ndarray | None:
        """
        Handle camera disconnect by attempting reconnection.

        Returns:
            Frame from reconnected camera or None.
        """
        self._logger.warning("Camera connection lost, attempting reconnect")
        self.release_camera()
        if self.initialize_camera():
            return self.capture_frame()
        return None

    def release_camera(self) -> None:
        """Release the webcam resource safely."""
        with self._lock:
            if self._capture is not None:
                self._capture.release()
                self._capture = None
            self._is_open = False
            self._latest_frame = None
        self._logger.info("Camera closed")

    def close_camera(self) -> None:
        """Alias for release_camera for API compatibility."""
        self.release_camera()

    def start_capture_loop(
        self,
        running_flag: Callable[[], bool],
        on_frame: Callable[[np.ndarray], None] | None = None,
    ) -> None:
        """
        Run continuous frame capture in the calling thread.

        Args:
            running_flag: Callable returning True while capture should continue.
            on_frame: Optional callback invoked with each captured frame.
        """
        frame_delay = 1.0 / ConfigManager.TARGET_FPS
        while running_flag():
            frame = self.capture_frame()
            if frame is not None and on_frame is not None:
                on_frame(frame)
            time.sleep(frame_delay)
