"""
Image management module for the Real-Time Emotion Detection Agent.

Loads emotion images once at startup, caches them in memory,
and serves cached images on emotion changes.

Dependencies: PIL, pathlib, config, logger, utils
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from config import ConfigManager
from logger import Logger
from utils import find_emotion_image_path, load_image, validate_image_folder


class ImageManager:
    """Manages loading, caching, and retrieval of emotion images."""

    def __init__(self, images_dir: Path | None = None) -> None:
        """
        Initialize the image manager.

        Args:
            images_dir: Optional override path for emotion images directory.
        """
        self._logger = Logger.get_logger()
        self._images_dir = images_dir or ConfigManager.EMOTION_IMAGES_DIR
        self._cache: dict[str, Image.Image] = {}
        self._missing_emotions: set[str] = set()
        self._loaded: bool = False

    @property
    def missing_emotions(self) -> set[str]:
        """Return set of emotions with missing image files."""
        return self._missing_emotions.copy()

    @property
    def is_loaded(self) -> bool:
        """Return whether images have been loaded into cache."""
        return self._loaded

    def load_all_images(self) -> dict[str, bool]:
        """
        Load all emotion images into memory cache.

        Searches for images matching patterns like happy.*, sad.*, etc.
        Uses the first valid image found for each emotion.

        Returns:
            Dictionary mapping emotion names to load success status.
        """
        self._cache.clear()
        self._missing_emotions.clear()
        results: dict[str, bool] = {}

        validation = validate_image_folder(self._images_dir)

        for emotion in ConfigManager.EMOTIONS:
            image_path = find_emotion_image_path(self._images_dir, emotion)

            if image_path is None:
                self._missing_emotions.add(emotion)
                placeholder = self._create_placeholder(emotion)
                self._cache[emotion] = placeholder
                results[emotion] = False
                self._logger.warning(
                    "Missing Image: %s — using placeholder", emotion
                )
                continue

            image = load_image(image_path)
            if image is None:
                self._missing_emotions.add(emotion)
                placeholder = self._create_placeholder(emotion)
                self._cache[emotion] = placeholder
                results[emotion] = False
                self._logger.warning(
                    "Invalid image for %s — using placeholder", emotion
                )
            else:
                self._cache[emotion] = image
                results[emotion] = True
                self._logger.info("Loaded emotion image: %s from %s", emotion, image_path)

        self._loaded = True
        loaded_count = sum(1 for success in results.values() if success)
        self._logger.info(
            "Image cache ready: %d/%d emotions loaded",
            loaded_count,
            len(ConfigManager.EMOTIONS),
        )
        return results

    def get_image(self, emotion: str) -> Image.Image | None:
        """
        Retrieve a cached emotion image from memory.

        Args:
            emotion: Display emotion name (e.g., 'Happy').

        Returns:
            Cached PIL Image or None if emotion is unknown.
        """
        if not self._loaded:
            self.load_all_images()
        return self._cache.get(emotion)

    def is_missing(self, emotion: str) -> bool:
        """
        Check if an emotion image is missing from disk.

        Args:
            emotion: Display emotion name.

        Returns:
            True if the image was not found on disk.
        """
        return emotion in self._missing_emotions

    def clear_cache(self) -> None:
        """Clear the in-memory image cache."""
        self._cache.clear()
        self._loaded = False
        self._missing_emotions.clear()
        self._logger.debug("Image cache cleared")

    def _create_placeholder(self, emotion: str) -> Image.Image:
        """
        Create a placeholder image for a missing emotion file.

        Args:
            emotion: Emotion name to display on placeholder.

        Returns:
            Generated PIL Image placeholder.
        """
        width, height = 400, 400
        image = Image.new("RGB", (width, height), color=(30, 30, 30))
        draw = ImageDraw.Draw(image)

        try:
            font = ImageFont.truetype("segoeui.ttf", 24)
        except OSError:
            font = ImageFont.load_default()

        text_lines = ["Missing Image", emotion]
        y_offset = height // 2 - 30
        for line in text_lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            draw.text(
                ((width - text_width) // 2, y_offset),
                line,
                fill=(239, 68, 68),
                font=font,
            )
            y_offset += 35

        return image
