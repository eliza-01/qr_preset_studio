# qr_preset_studio/infrastructure/rendering/body_shapes/square.py
from __future__ import annotations

from PIL import Image

from qr_preset_studio.domain.models.preset import Preset
from qr_preset_studio.infrastructure.rendering.body_shapes.common import paint_module_colors


def render_square_body(
    canvas: Image.Image,
    preset: Preset,
    layout,
    body_map: list[list[bool]],
) -> None:
    paint_module_colors(canvas, preset, layout, body_map)
