"""
User interface module for the Real-Time Emotion Detection Agent.

Builds and manages the Tkinter GUI with dark theme, webcam display,
emotion image panel, details panel, and status bar.

Dependencies: tkinter, PIL, datetime, config, utils, logger
"""

import tkinter as tk
from datetime import datetime
from tkinter import ttk
from typing import Callable

from PIL import Image

from config import ConfigManager
from logger import Logger
from utils import format_confidence, pil_to_photo_image, resize_image


class UIManager:
    """Constructs and updates the application graphical interface."""

    def __init__(self, root: tk.Tk, on_close: Callable[[], None] | None = None) -> None:
        """
        Initialize the UI manager.

        Args:
            root: Tkinter root window instance.
            on_close: Callback invoked when the window is closed.
        """
        self._root = root
        self._on_close = on_close
        self._logger = Logger.get_logger()

        self._webcam_photo: tk.PhotoImage | None = None
        self._emotion_photo: tk.PhotoImage | None = None
        self._current_emotion_image: str | None = None

        self._status_var = tk.StringVar(value="Initializing...")
        self._camera_status_var = tk.StringVar(value="Camera: Initializing")
        self._emotion_var = tk.StringVar(value="—")
        self._confidence_var = tk.StringVar(value="—")
        self._detection_status_var = tk.StringVar(value="Waiting")
        self._fps_var = tk.StringVar(value="FPS: —")
        self._datetime_var = tk.StringVar(value="")

        self._webcam_label: tk.Label | None = None
        self._emotion_image_label: tk.Label | None = None

        self.create_window()

    @property
    def root(self) -> tk.Tk:
        """Return the Tkinter root window."""
        return self._root

    def create_window(self) -> None:
        """Build the complete application window and layout."""
        self._root.title(ConfigManager.APP_TITLE)
        self._root.geometry(
            f"{ConfigManager.WINDOW_WIDTH}x{ConfigManager.WINDOW_HEIGHT}"
        )
        self._root.minsize(
            ConfigManager.WINDOW_MIN_WIDTH,
            ConfigManager.WINDOW_MIN_HEIGHT,
        )
        self._root.configure(bg=ConfigManager.COLOR_BACKGROUND)
        self._root.protocol("WM_DELETE_WINDOW", self.close_window)

        self._configure_styles()
        self._build_header()
        self._build_main_content()
        self._build_status_bar()
        self._start_clock()

        self._logger.info("UI window created")

    def _configure_styles(self) -> None:
        """Configure ttk styles for the dark theme."""
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Dark.TFrame",
            background=ConfigManager.COLOR_BACKGROUND,
        )
        style.configure(
            "Panel.TFrame",
            background=ConfigManager.COLOR_PANEL,
        )
        style.configure(
            "Dark.TLabel",
            background=ConfigManager.COLOR_PANEL,
            foreground=ConfigManager.COLOR_TEXT_PRIMARY,
            font=(ConfigManager.FONT_FAMILY, ConfigManager.FONT_BODY_SIZE),
        )
        style.configure(
            "Title.TLabel",
            background=ConfigManager.COLOR_BACKGROUND,
            foreground=ConfigManager.COLOR_TEXT_PRIMARY,
            font=(
                ConfigManager.FONT_FAMILY,
                ConfigManager.FONT_TITLE_SIZE,
                "bold",
            ),
        )
        style.configure(
            "Section.TLabel",
            background=ConfigManager.COLOR_PANEL,
            foreground=ConfigManager.COLOR_TEXT_PRIMARY,
            font=(
                ConfigManager.FONT_FAMILY,
                ConfigManager.FONT_SECTION_SIZE,
                "bold",
            ),
        )
        style.configure(
            "Status.TLabel",
            background=ConfigManager.COLOR_PANEL,
            foreground=ConfigManager.COLOR_TEXT_SECONDARY,
            font=(ConfigManager.FONT_FAMILY, ConfigManager.FONT_STATUS_SIZE),
        )
        style.configure(
            "Accent.TLabel",
            background=ConfigManager.COLOR_PANEL,
            foreground=ConfigManager.COLOR_ACCENT,
            font=(
                ConfigManager.FONT_FAMILY,
                ConfigManager.FONT_SECTION_SIZE,
                "bold",
            ),
        )
        style.configure(
            "Success.TLabel",
            background=ConfigManager.COLOR_PANEL,
            foreground=ConfigManager.COLOR_SUCCESS,
            font=(ConfigManager.FONT_FAMILY, ConfigManager.FONT_BODY_SIZE),
        )
        style.configure(
            "Warning.TLabel",
            background=ConfigManager.COLOR_PANEL,
            foreground=ConfigManager.COLOR_WARNING,
            font=(ConfigManager.FONT_FAMILY, ConfigManager.FONT_BODY_SIZE),
        )
        style.configure(
            "Error.TLabel",
            background=ConfigManager.COLOR_PANEL,
            foreground=ConfigManager.COLOR_ERROR,
            font=(ConfigManager.FONT_FAMILY, ConfigManager.FONT_BODY_SIZE),
        )

    def _build_header(self) -> None:
        """Create the application header section."""
        header = ttk.Frame(self._root, style="Dark.TFrame", padding=(20, 15))
        header.pack(fill=tk.X)

        title_label = ttk.Label(
            header,
            text=ConfigManager.APP_TITLE,
            style="Title.TLabel",
        )
        title_label.pack(side=tk.LEFT)

        right_frame = ttk.Frame(header, style="Dark.TFrame")
        right_frame.pack(side=tk.RIGHT)

        datetime_label = ttk.Label(
            right_frame,
            textvariable=self._datetime_var,
            style="Status.TLabel",
        )
        datetime_label.pack(side=tk.TOP, anchor=tk.E)

        camera_status = ttk.Label(
            right_frame,
            textvariable=self._camera_status_var,
            style="Success.TLabel",
        )
        camera_status.pack(side=tk.TOP, anchor=tk.E, pady=(5, 0))

    def _build_main_content(self) -> None:
        """Create the main content area with webcam, emotion, and details."""
        content = ttk.Frame(self._root, style="Dark.TFrame", padding=(20, 10))
        content.pack(fill=tk.BOTH, expand=True)

        content.columnconfigure(0, weight=3)
        content.columnconfigure(1, weight=2)
        content.columnconfigure(2, weight=1)
        content.rowconfigure(0, weight=1)

        self._build_webcam_panel(content)
        self._build_emotion_panel(content)
        self._build_details_panel(content)

    def _build_webcam_panel(self, parent: ttk.Frame) -> None:
        """Create the live webcam feed panel."""
        panel = ttk.Frame(parent, style="Panel.TFrame", padding=10)
        panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        header = ttk.Label(panel, text="Live Webcam", style="Section.TLabel")
        header.pack(anchor=tk.W, pady=(0, 10))

        self._webcam_label = tk.Label(
            panel,
            bg=ConfigManager.COLOR_BACKGROUND,
            text="Starting camera...",
            fg=ConfigManager.COLOR_TEXT_SECONDARY,
            font=(ConfigManager.FONT_FAMILY, ConfigManager.FONT_BODY_SIZE),
        )
        self._webcam_label.pack(fill=tk.BOTH, expand=True)

    def _build_emotion_panel(self, parent: ttk.Frame) -> None:
        """Create the emotion image display panel."""
        panel = ttk.Frame(parent, style="Panel.TFrame", padding=10)
        panel.grid(row=0, column=1, sticky="nsew", padx=(0, 10))

        header = ttk.Label(
            panel, text="Emotion", style="Section.TLabel"
        )
        header.pack(anchor=tk.W, pady=(0, 10))

        self._emotion_image_label = tk.Label(
            panel,
            bg=ConfigManager.COLOR_BACKGROUND,
            text="Waiting for detection...",
            fg=ConfigManager.COLOR_TEXT_SECONDARY,
            font=(ConfigManager.FONT_FAMILY, ConfigManager.FONT_BODY_SIZE),
        )
        self._emotion_image_label.pack(fill=tk.BOTH, expand=True)

    def _build_details_panel(self, parent: ttk.Frame) -> None:
        """Create the detection details panel."""
        panel = ttk.Frame(parent, style="Panel.TFrame", padding=15)
        panel.grid(row=0, column=2, sticky="nsew")

        header = ttk.Label(panel, text="Details", style="Section.TLabel")
        header.pack(anchor=tk.W, pady=(0, 20))

        self._add_detail_row(panel, "Detected Emotion:", self._emotion_var, "Accent.TLabel")
        self._add_detail_row(
            panel, "Confidence:", self._confidence_var, "Success.TLabel"
        )
        self._add_detail_row(
            panel, "Detection Status:", self._detection_status_var, "Dark.TLabel"
        )
        self._add_detail_row(panel, "Performance:", self._fps_var, "Status.TLabel")

    def _add_detail_row(
        self,
        parent: ttk.Frame,
        label_text: str,
        variable: tk.StringVar,
        value_style: str,
    ) -> None:
        """
        Add a label-value row to the details panel.

        Args:
            parent: Parent frame widget.
            label_text: Static label text.
            variable: StringVar bound to the value label.
            value_style: ttk style name for the value label.
        """
        row = ttk.Frame(parent, style="Panel.TFrame")
        row.pack(fill=tk.X, pady=8)

        label = ttk.Label(row, text=label_text, style="Dark.TLabel")
        label.pack(anchor=tk.W)

        value = ttk.Label(row, textvariable=variable, style=value_style)
        value.pack(anchor=tk.W, pady=(4, 0))

    def _build_status_bar(self) -> None:
        """Create the bottom status bar."""
        status_frame = ttk.Frame(
            self._root,
            style="Panel.TFrame",
            padding=(20, 8),
        )
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)

        status_label = ttk.Label(
            status_frame,
            textvariable=self._status_var,
            style="Status.TLabel",
        )
        status_label.pack(side=tk.LEFT)

    def _start_clock(self) -> None:
        """Start the date/time display update loop."""
        self._update_clock()

    def _update_clock(self) -> None:
        """Update the header date/time display."""
        now = datetime.now().strftime("%A, %B %d, %Y  %H:%M:%S")
        self._datetime_var.set(now)
        self._root.after(1000, self._update_clock)

    def update_camera(self, frame_image: Image.Image) -> None:
        """
        Update the webcam panel with a new frame.

        Args:
            frame_image: PIL Image of the annotated webcam frame.
        """
        if self._webcam_label is None:
            return

        panel_width = max(self._webcam_label.winfo_width(), 400)
        panel_height = max(self._webcam_label.winfo_height(), 300)

        resized = resize_image(frame_image, panel_width, panel_height)
        self._webcam_photo = pil_to_photo_image(resized)
        self._webcam_label.configure(image=self._webcam_photo, text="")

    def update_emotion(
        self,
        emotion: str | None,
        confidence: float,
        emotion_image: Image.Image | None,
        missing_image: bool = False,
    ) -> None:
        """
        Update emotion display elements when emotion changes.

        Args:
            emotion: Detected emotion name or None.
            confidence: Confidence percentage value.
            emotion_image: Cached PIL Image for the emotion.
            missing_image: Whether the emotion image file is missing.
        """
        if emotion is None:
            self._emotion_var.set("No Face Detected")
            self._confidence_var.set("—")
            return

        self._emotion_var.set(emotion)
        self._confidence_var.set(format_confidence(confidence))

        if emotion_image is not None and self._emotion_image_label is not None:
            if self._current_emotion_image != emotion or missing_image:
                panel_width = max(self._emotion_image_label.winfo_width(), 300)
                panel_height = max(self._emotion_image_label.winfo_height(), 300)
                resized = resize_image(emotion_image, panel_width, panel_height)
                self._emotion_photo = pil_to_photo_image(resized)
                self._emotion_image_label.configure(
                    image=self._emotion_photo, text=""
                )
                self._current_emotion_image = emotion

                if missing_image:
                    self.update_status(f"Missing Image: {emotion}")
                else:
                    self.update_status("Image Loaded")

    def update_status(self, message: str) -> None:
        """
        Update the status bar message.

        Args:
            message: Status text to display.
        """
        self._status_var.set(message)

    def update_detection_status(
        self,
        face_detected: bool,
        emotion: str | None = None,
    ) -> None:
        """
        Update the detection status label.

        Args:
            face_detected: Whether a face is currently visible.
            emotion: Current detected emotion if available.
        """
        if not face_detected:
            self._detection_status_var.set("No Face Detected")
            self._emotion_var.set("No Face Detected")
            self._confidence_var.set("—")
        elif emotion:
            self._detection_status_var.set("Detecting…")
        else:
            self._detection_status_var.set("Detecting…")

    def update_fps(self, fps: float) -> None:
        """
        Update the FPS display label.

        Args:
            fps: Current frames per second value.
        """
        self._fps_var.set(f"FPS: {fps:.1f}")

    def set_camera_status(self, status: str, is_error: bool = False) -> None:
        """
        Update the camera status indicator in the header.

        Args:
            status: Camera status text.
            is_error: Whether to display as an error state.
        """
        self._camera_status_var.set(f"Camera: {status}")

    def show_error(self, message: str) -> None:
        """
        Display a friendly error message in the status bar.

        Args:
            message: Error message text.
        """
        self.update_status(message)
        self._detection_status_var.set("Error")
        self._logger.error("UI Error: %s", message)

    def close_window(self) -> None:
        """Handle window close event and trigger shutdown callback."""
        self._logger.info("Window close requested")
        if self._on_close:
            self._on_close()

    def schedule(self, callback: Callable[[], None], delay_ms: int) -> None:
        """
        Schedule a callback on the Tkinter main thread.

        Args:
            callback: Function to invoke.
            delay_ms: Delay in milliseconds.
        """
        self._root.after(delay_ms, callback)

    def run_mainloop(self) -> None:
        """Start the Tkinter event loop."""
        self._root.mainloop()

    def destroy(self) -> None:
        """Destroy the root window and release UI resources."""
        try:
            self._root.destroy()
        except tk.TclError:
            pass
