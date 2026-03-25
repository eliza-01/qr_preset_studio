from __future__ import annotations

from pathlib import Path

from PIL import Image

from qr_preset_studio.domain.models.preset import Preset


def build_canvas(preset: Preset) -> Image.Image:
    size = (preset.canvas_width, preset.canvas_height)
    canvas = Image.new("RGBA", size, preset.canvas_background_color)

    image_path = Path(preset.background_image_path).expanduser()
    if not image_path.is_file():
        return canvas

    with Image.open(image_path) as source:
        image = source.convert("RGBA")

    cover_scale = max(
        size[0] / max(1, image.width),
        size[1] / max(1, image.height),
    )
    user_scale = max(1, preset.background_scale_percent) / 100
    final_scale = cover_scale * user_scale

    scaled_size = (
        max(1, int(round(image.width * final_scale))),
        max(1, int(round(image.height * final_scale))),
    )
    image = image.resize(scaled_size, Image.Resampling.LANCZOS)

    pos_x = ((size[0] - image.width) // 2) + preset.background_offset_x
    pos_y = ((size[1] - image.height) // 2) + preset.background_offset_y

    canvas.paste(image, (pos_x, pos_y), image)
    return canvas