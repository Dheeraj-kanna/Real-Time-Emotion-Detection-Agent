"""
Utility functions for the Real-Time Emotion Detection Agent.

Provides image loading, resizing, face box drawing, confidence formatting,
logging helpers, and folder validation.

Dependencies: cv2, PIL, numpy, pathlib, config, logger
"""

from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageTk

from config import ConfigManager
from logger import Logger


def load_image(image_path: Path) -> Image.Image | None:
    """
    Load an image from disk using Pillow.

    Args:
        image_path: Path to the image file.

    Returns:
        PIL Image object if successful, None otherwise.

    Raises:
        Does not raise; logs errors and returns None.
    """
    logger = Logger.get_logger()
    try:
        if not image_path.exists():
            logger.warning("Image not found: %s", image_path)
            return None
        image = Image.open(image_path)
        image.load()
        return image.convert("RGB")
    except (OSError, IOError) as error:
        logger.error("Failed to load image %s: %s", image_path, error)
        return None


def resize_image(
    image: Image.Image,
    max_width: int,
    max_height: int,
) -> Image.Image:
    """
    Resize an image while preserving aspect ratio.

    Args:
        image: Source PIL Image.
        max_width: Maximum allowed width in pixels.
        max_height: Maximum allowed height in pixels.

    Returns:
        Resized PIL Image.
    """
    original_width, original_height = image.size
    scale = min(max_width / original_width, max_height / original_height)
    if scale >= 1.0:
        return image.copy()
    new_width = int(original_width * scale)
    new_height = int(original_height * scale)
    return image.resize((new_width, new_height), Image.Resampling.LANCZOS)


def pil_to_photo_image(image: Image.Image) -> ImageTk.PhotoImage:
    """
    Convert a PIL Image to a Tkinter PhotoImage.

    Args:
        image: PIL Image to convert.

    Returns:
        Tkinter PhotoImage reference.
    """
    return ImageTk.PhotoImage(image)


def cv2_to_pil(frame: np.ndarray) -> Image.Image:
    """
    Convert an OpenCV BGR frame to a PIL RGB Image.

    Args:
        frame: OpenCV frame in BGR format.

    Returns:
        PIL Image in RGB format.
    """
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    return Image.fromarray(rgb_frame)


def draw_face_box(
    frame: np.ndarray,
    region: dict[str, int],
    emotion_label: str = "",
) -> np.ndarray:
    """
    Draw a bounding box and optional emotion label on a frame.

    Args:
        frame: OpenCV BGR frame to annotate.
        region: Dictionary with x, y, w, h keys for face region.
        emotion_label: Optional emotion text to display above the box.

    Returns:
        Annotated frame copy.
    """
    annotated = frame.copy()
    x = region.get("x", 0)
    y = region.get("y", 0)
    w = region.get("w", 0)
    h = region.get("h", 0)

    color = ConfigManager.FACE_BOX_COLOR
    thickness = ConfigManager.FACE_BOX_THICKNESS
    cv2.rectangle(annotated, (x, y), (x + w, y + h), color, thickness)

    if emotion_label:
        label_y = max(y - 10, 20)
        cv2.putText(
            annotated,
            emotion_label,
            (x, label_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            color,
            2,
            cv2.LINE_AA,
        )

    return annotated


def format_confidence(confidence: float) -> str:
    """
    Format a confidence score as a percentage string.

    Args:
        confidence: Confidence value between 0.0 and 100.0.

    Returns:
        Formatted percentage string (e.g., '87.5%').
    """
    return f"{confidence:.1f}%"


def write_log(message: str, level: str = "info") -> None:
    """
    Write a log message using the application logger.

    Args:
        message: Log message text.
        level: Log level name ('debug', 'info', 'warning', 'error').
    """
    logger = Logger.get_logger()
    log_method = getattr(logger, level.lower(), logger.info)
    log_method(message)


def validate_image_folder(folder_path: Path) -> dict[str, bool]:
    """
    Validate that emotion image files exist for each supported emotion.

    Args:
        folder_path: Directory containing emotion images.

    Returns:
        Dictionary mapping emotion names to availability status.
    """
    logger = Logger.get_logger()
    results: dict[str, bool] = {}

    if not folder_path.exists():
        logger.warning("Emotion images folder does not exist: %s", folder_path)
        for emotion in ConfigManager.EMOTIONS:
            results[emotion] = False
        return results

    patterns = ConfigManager.get_emotion_search_patterns()
    for emotion, prefix in patterns.items():
        image_path = find_emotion_image_path(folder_path, emotion)
        results[emotion] = image_path is not None
        if image_path is None:
            logger.warning("Missing emotion image for: %s", emotion)

    return results


def find_emotion_image_path(folder_path: Path, emotion: str) -> Path | None:
    """
    Find the first valid image file for a given emotion.

    Args:
        folder_path: Directory to search for emotion images.
        emotion: Display emotion name (e.g., 'Happy').

    Returns:
        Path to the image file if found, None otherwise.
    """
    prefix = emotion.lower()
    candidates = sorted(
        path
        for path in folder_path.glob(f"{prefix}*")
        if path.is_file() and path.suffix.lower() in ConfigManager.SUPPORTED_IMAGE_FORMATS
    )
    if candidates:
        return candidates[0]
    return None


def verify_dependencies() -> tuple[bool, list[str]]:
    """
    Verify that required third-party dependencies are importable.

    Returns:
        Tuple of (all_available, list_of_missing_packages).
    """
    required = {
        "cv2": "opencv-python",
        "numpy": "numpy",
        "PIL": "Pillow",
        "deepface": "deepface",
        "tensorflow": "tensorflow",
        "tf_keras": "tf-keras",
    }
    missing: list[str] = []
    for module_name, package_name in required.items():
        try:
            __import__(module_name)
        except ImportError:
            missing.append(package_name)
    return len(missing) == 0, missing
