from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageOps

from qr_preset_studio.domain.models.preset import Preset


def build_canvas(preset: Preset) -> Image.Image:
    size = (preset.canvas_width, preset.canvas_height)
    image_path = Path(preset.background_image_path).expanduser()
    if image_path.is_file():
        image = Image.open(image_path).convert("RGBA")
        return ImageOps.fit(image, size, method=Image.Resampling.LANCZOS)
    return Image.new("RGBA", size, preset.canvas_background_color)
