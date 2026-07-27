"""
Generate placeholder emotion images for development and testing.

Run once to populate assets/emotion_images/ with labeled PNG files.

Usage:
    python scripts/generate_placeholder_images.py
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

EMOTIONS = {
    "happy": ("#22C55E", "😊"),
    "sad": ("#3B82F6", "😢"),
    "angry": ("#EF4444", "😠"),
    "fear": ("#A855F7", "😨"),
    "surprise": ("#F59E0B", "😲"),
    "neutral": ("#BDBDBD", "😐"),
    "disgust": ("#84CC16", "🤢"),
}


def generate_placeholders() -> None:
    """Create placeholder PNG images for each supported emotion."""
    base_dir = Path(__file__).resolve().parent.parent
    output_dir = base_dir / "assets" / "emotion_images"
    output_dir.mkdir(parents=True, exist_ok=True)

    for name, (color, emoji) in EMOTIONS.items():
        image = Image.new("RGB", (400, 400), color=color)
        draw = ImageDraw.Draw(image)

        try:
            font = ImageFont.truetype("segoeui.ttf", 48)
        except OSError:
            font = ImageFont.load_default()

        label = name.capitalize()
        bbox = draw.textbbox((0, 0), label, font=font)
        text_width = bbox[2] - bbox[0]
        draw.text(
            ((400 - text_width) // 2, 160),
            label,
            fill="#FFFFFF",
            font=font,
        )

        emoji_bbox = draw.textbbox((0, 0), emoji, font=font)
        emoji_width = emoji_bbox[2] - emoji_bbox[0]
        draw.text(
            ((400 - emoji_width) // 2, 220),
            emoji,
            fill="#FFFFFF",
            font=font,
        )

        output_path = output_dir / f"{name}.png"
        image.save(output_path)
        print(f"Created: {output_path}")


if __name__ == "__main__":
    generate_placeholders()
