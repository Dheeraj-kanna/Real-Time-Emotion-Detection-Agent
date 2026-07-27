"""
Main entry point for the Real-Time Emotion Detection Agent.

Initializes all modules, starts the detection pipeline with threading,
and handles graceful application shutdown.

Dependencies: tkinter, threading, time, sys, config, camera, emotion_detector,
              ui, image_manager, state_manager, logger, utils
"""

import sys
import threading
import time
import tkinter as tk
from tkinter import messagebox
from typing import Any

import cv2

from camera import CameraManager
from config import ConfigManager
from emotion_detector import EmotionDetector
from image_manager import ImageManager
from logger import Logger
from state_manager import ApplicationState, StateManager
from ui import UIManager
from utils import cv2_to_pil, draw_face_box, verify_dependencies


class EmotionApp:
    """Main application controller coordinating all modules."""

    def __init__(self) -> None:
        """Initialize the emotion detection application."""
        ConfigManager.ensure_directories()
        self._logger = Logger.setup()
        self._logger.info("Application Started")

        self._state_manager = StateManager()
        self._camera_manager = CameraManager()
        self._emotion_detector = EmotionDetector()
        self._image_manager = ImageManager()

        self._root: tk.Tk | None = None
        self._ui_manager: UIManager | None = None

        self._running = False
        self._camera_thread: threading.Thread | None = None
        self._detection_thread: threading.Thread | None = None

        self._latest_annotated_frame: Any = None
        self._frame_lock = threading.Lock()
        self._last_prediction_time: float = 0.0
        self._latest_detection: dict[str, Any] = {}
        self._last_ui_emotion: str | None = None
        self._shutdown_complete: bool = False

    def start(self) -> None:
        """
        Run the complete application lifecycle.

        Raises:
            SystemExit: If dependencies or camera initialization fails.
        """
        try:
            self._load_configuration()
            self._verify_dependencies()
            self._load_emotion_images()
            self._initialize_camera()
            self._create_ui()
            self._start_threads()
            self._schedule_ui_updates()
            self._ui_manager.run_mainloop()
        except SystemExit:
            raise
        except Exception as error:
            self._logger.exception("Unexpected Exception: %s", error)
            self._show_fatal_error(str(error))
        finally:
            self._shutdown()

    def _load_configuration(self) -> None:
        """Load and validate application configuration."""
        self._state_manager.set_state(ApplicationState.INITIALIZING)
        self._logger.info("Configuration loaded")

    def _verify_dependencies(self) -> None:
        """Verify required packages are installed."""
        all_available, missing = verify_dependencies()
        if not all_available:
            message = f"Missing dependencies: {', '.join(missing)}"
            self._logger.error(message)
            print(f"Error: {message}", file=sys.stderr)
            print("Install with: pip install -r requirements.txt", file=sys.stderr)
            raise SystemExit(1)
        self._logger.info("All dependencies verified")

    def _load_emotion_images(self) -> None:
        """Load and cache all emotion images from assets directory."""
        results = self._image_manager.load_all_images()
        loaded = sum(1 for success in results.values() if success)
        self._logger.info("Emotion images loaded: %d/%d", loaded, len(results))

    def _initialize_camera(self) -> None:
        """Initialize the webcam with retry logic."""
        if not self._camera_manager.initialize_camera():
            self._logger.error("Camera Not Available")
            raise SystemExit(
                "Camera Not Available. Please connect a webcam and try again."
            )
        self._state_manager.set_state(ApplicationState.CAMERA_READY)

    def _create_ui(self) -> None:
        """Create the Tkinter user interface."""
        self._root = tk.Tk()
        self._ui_manager = UIManager(self._root, on_close=self._request_shutdown)
        self._ui_manager.set_camera_status("Ready")
        self._ui_manager.update_status("Camera Ready")

    def _start_threads(self) -> None:
        """Start camera capture and emotion detection worker threads."""
        self._running = True

        self._camera_thread = threading.Thread(
            target=self._camera_loop,
            name="CameraThread",
            daemon=True,
        )
        self._camera_thread.start()

        self._detection_thread = threading.Thread(
            target=self._detection_loop,
            name="DetectionThread",
            daemon=True,
        )
        self._detection_thread.start()

        self._logger.info("Worker threads started")

    def _camera_loop(self) -> None:
        """Continuously capture frames from the webcam."""
        frame_delay = 1.0 / ConfigManager.TARGET_FPS
        while self._running:
            frame = self._camera_manager.capture_frame()
            if frame is not None:
                annotated = self._annotate_frame(frame)
                with self._frame_lock:
                    self._latest_annotated_frame = annotated
            time.sleep(frame_delay)

    def _detection_loop(self) -> None:
        """Run emotion detection at configurable intervals."""
        interval = ConfigManager.PREDICTION_INTERVAL_MS / 1000.0
        while self._running:
            current_time = time.time()
            if current_time - self._last_prediction_time >= interval:
                self._last_prediction_time = current_time
                self._run_prediction()
            time.sleep(0.05)

    def _run_prediction(self) -> None:
        """Execute emotion prediction on the latest frame."""
        with self._frame_lock:
            frame = self._camera_manager.get_latest_frame()

        if frame is None:
            return

        detection = self._emotion_detector.detect_emotion(frame)
        self._latest_detection = detection

        face_detected = detection.get("face_detected", False)
        emotion = detection.get("emotion")
        confidence = detection.get("confidence", 0.0)

        if face_detected and emotion:
            emotion_changed = self._state_manager.update_detection(
                emotion, confidence, True
            )
            if emotion_changed:
                self._logger.info("Emotion Changed: %s (%.1f%%)", emotion, confidence)
        else:
            self._state_manager.update_detection(None, 0.0, False)

    def _annotate_frame(self, frame: Any) -> Any:
        """
        Draw face bounding box and emotion label on frame.

        Args:
            frame: Raw OpenCV BGR frame.

        Returns:
            Annotated frame copy.
        """
        detection = self._latest_detection
        if detection.get("face_detected") and detection.get("region"):
            emotion_label = detection.get("emotion", "")
            return draw_face_box(frame, detection["region"], emotion_label)
        return frame

    def _schedule_ui_updates(self) -> None:
        """Schedule periodic UI refresh on the main thread."""
        self._refresh_ui()

    def _refresh_ui(self) -> None:
        """Refresh all UI components from latest detection data."""
        if not self._running or self._ui_manager is None:
            return

        with self._frame_lock:
            frame = self._latest_annotated_frame

        if frame is not None:
            pil_frame = cv2_to_pil(frame)
            self._ui_manager.update_camera(pil_frame)

        detection = self._latest_detection
        face_detected = detection.get("face_detected", False)
        emotion = detection.get("emotion")
        confidence = detection.get("confidence", 0.0)

        self._ui_manager.update_fps(self._camera_manager.current_fps)

        if not face_detected:
            self._ui_manager.update_detection_status(False)
            self._ui_manager.update_status("No Face Detected")
            self._last_ui_emotion = None
        else:
            self._ui_manager.update_detection_status(True, emotion)

            if emotion and emotion != self._last_ui_emotion:
                emotion_image = self._image_manager.get_image(emotion)
                missing = self._image_manager.is_missing(emotion)
                self._ui_manager.update_emotion(
                    emotion, confidence, emotion_image, missing
                )
                self._last_ui_emotion = emotion
                if not missing:
                    self._ui_manager.update_status("Detecting…")
                else:
                    self._ui_manager.update_status(f"Missing Image: {emotion}")

        if self._running:
            self._ui_manager.schedule(
                self._refresh_ui,
                ConfigManager.WEBCAM_REFRESH_MS,
            )

    def _request_shutdown(self) -> None:
        """Request graceful application shutdown."""
        self._logger.info("Shutdown requested by user")
        self._running = False
        self._state_manager.set_state(ApplicationState.EXITING)
        if self._root:
            self._root.after(100, self._finalize_shutdown)

    def _finalize_shutdown(self) -> None:
        """Finalize shutdown after worker threads stop."""
        self._shutdown()
        if self._ui_manager:
            self._ui_manager.destroy()

    def _shutdown(self) -> None:
        """Release all application resources."""
        if self._shutdown_complete:
            return

        self._running = False
        self._state_manager.set_state(ApplicationState.EXITING)

        self._camera_manager.release_camera()
        self._image_manager.clear_cache()

        if self._camera_thread and self._camera_thread.is_alive():
            self._camera_thread.join(timeout=2.0)
        if self._detection_thread and self._detection_thread.is_alive():
            self._detection_thread.join(timeout=2.0)

        cv2.destroyAllWindows()
        self._logger.info("Application Exited")
        Logger.close()
        self._shutdown_complete = True

    def _show_fatal_error(self, message: str) -> None:
        """
        Display a fatal error dialog if possible.

        Args:
            message: Error message to display.
        """
        try:
            if self._root is None:
                self._root = tk.Tk()
                self._root.withdraw()
            messagebox.showerror("Application Error", message)
        except Exception:
            print(f"Fatal error: {message}", file=sys.stderr)


def main() -> None:
    """Application entry point."""
    app = EmotionApp()
    app.start()


if __name__ == "__main__":
    main()
