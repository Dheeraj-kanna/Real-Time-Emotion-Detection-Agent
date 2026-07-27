"""
Configuration module for the Real-Time Emotion Detection Agent.

Stores application constants, theme colors, paths, thresholds,
and supported emotion definitions.

Dependencies: pathlib (standard library)
"""

from pathlib import Path


class ConfigManager:
    """Central configuration manager for the emotion detection application."""

    # Application metadata
    APP_TITLE: str = "Real-Time Emotion Detection Agent"
    APP_VERSION: str = "1.0"

    # Window settings
    WINDOW_WIDTH: int = 1280
    WINDOW_HEIGHT: int = 720
    WINDOW_MIN_WIDTH: int = 1024
    WINDOW_MIN_HEIGHT: int = 600
    WINDOW_RESIZABLE: bool = True

    # Typography
    FONT_FAMILY: str = "Segoe UI"
    FONT_TITLE_SIZE: int = 24
    FONT_SECTION_SIZE: int = 18
    FONT_BODY_SIZE: int = 14
    FONT_STATUS_SIZE: int = 12

    # Color palette (dark theme)
    COLOR_BACKGROUND: str = "#121212"
    COLOR_PANEL: str = "#1E1E1E"
    COLOR_ACCENT: str = "#3B82F6"
    COLOR_SUCCESS: str = "#22C55E"
    COLOR_WARNING: str = "#F59E0B"
    COLOR_ERROR: str = "#EF4444"
    COLOR_TEXT_PRIMARY: str = "#FFFFFF"
    COLOR_TEXT_SECONDARY: str = "#BDBDBD"

    # Camera settings
    CAMERA_WIDTH: int = 1280
    CAMERA_HEIGHT: int = 720
    CAMERA_INDEX: int = 0
    CAMERA_RETRY_MAX: int = 3
    CAMERA_RETRY_DELAY_MS: int = 1000
    TARGET_FPS: int = 30

    # Emotion detection settings
    PREDICTION_INTERVAL_MS: int = 300
    CONFIDENCE_THRESHOLD: float = 0.0

    # Supported emotions (display names)
    EMOTIONS: list[str] = [
        "Happy",
        "Sad",
        "Angry",
        "Fear",
        "Surprise",
        "Neutral",
        "Disgust",
    ]

    # DeepFace emotion keys mapped to display names
    EMOTION_MAP: dict[str, str] = {
        "happy": "Happy",
        "sad": "Sad",
        "angry": "Angry",
        "fear": "Fear",
        "surprise": "Surprise",
        "neutral": "Neutral",
        "disgust": "Disgust",
    }

    # Supported image extensions
    SUPPORTED_IMAGE_FORMATS: tuple[str, ...] = (".png", ".jpg", ".jpeg")

    # Paths
    BASE_DIR: Path = Path(__file__).resolve().parent
    ASSETS_DIR: Path = BASE_DIR / "assets"
    EMOTION_IMAGES_DIR: Path = ASSETS_DIR / "emotion_images"
    SCREENSHOTS_DIR: Path = BASE_DIR / "screenshots"
    DOCS_DIR: Path = BASE_DIR / "docs"
    LOGS_DIR: Path = BASE_DIR / "logs"
    LOG_FILE: Path = LOGS_DIR / "application.log"

    # UI refresh interval (milliseconds) for webcam display
    WEBCAM_REFRESH_MS: int = 33  # ~30 FPS

    # Face bounding box colors (BGR for OpenCV)
    FACE_BOX_COLOR: tuple[int, int, int] = (59, 130, 246)
    FACE_BOX_THICKNESS: int = 2

    @classmethod
    def ensure_directories(cls) -> None:
        """Create required project directories if they do not exist."""
        for directory in (
            cls.ASSETS_DIR,
            cls.EMOTION_IMAGES_DIR,
            cls.SCREENSHOTS_DIR,
            cls.DOCS_DIR,
            cls.LOGS_DIR,
        ):
            directory.mkdir(parents=True, exist_ok=True)

    @classmethod
    def get_emotion_search_patterns(cls) -> dict[str, str]:
        """
        Return emotion name to filename prefix mapping for image search.

        Returns:
            Dictionary mapping display emotion names to lowercase prefixes.
        """
        return {emotion: emotion.lower() for emotion in cls.EMOTIONS}
