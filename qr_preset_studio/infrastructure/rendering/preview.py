from __future__ import annotations

from PIL import Image

from qr_preset_studio.domain.models.preset import Preset
from qr_preset_studio.infrastructure.rendering.composer import render_preset
from qr_preset_studio.infrastructure.rendering.constants import PREVIEW_MAX_SIZE


def render_preview(preset: Preset, zoom_percent: int = 100) -> Image.Image:
    fit_factor = min(
        PREVIEW_MAX_SIZE[0] / max(1, preset.canvas_width),
        PREVIEW_MAX_SIZE[1] / max(1, preset.canvas_height),
        1.0,
    )
    preview_image = render_preset(preset.scaled_copy(fit_factor))

    zoom_factor = max(10, zoom_percent) / 100
    if abs(zoom_factor - 1.0) < 1e-9:
        return preview_image

    zoomed_size = (
        max(1, int(round(preview_image.width * zoom_factor))),
        max(1, int(round(preview_image.height * zoom_factor))),
    )
    return preview_image.resize(zoomed_size, Image.Resampling.NEAREST)
