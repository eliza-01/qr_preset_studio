# qr_preset_studio/infrastructure/rendering/body_shapes/__init__.py
from __future__ import annotations

from PIL import Image

from qr_preset_studio.domain.models.preset import Preset
from qr_preset_studio.infrastructure.rendering.body_shapes.claws import render_claws_body
from qr_preset_studio.infrastructure.rendering.body_shapes.liquid import render_liquid_body
from qr_preset_studio.infrastructure.rendering.body_shapes.rounded import render_rounded_body
from qr_preset_studio.infrastructure.rendering.body_shapes.spikes import render_spikes_body
from qr_preset_studio.infrastructure.rendering.body_shapes.square import render_square_body


def render_body(
    canvas: Image.Image,
    preset: Preset,
    layout,
    body_map: list[list[bool]],
    render_scale: float = 1.0,
) -> None:
    if preset.body_shape == "liquid":
        render_liquid_body(canvas, preset, layout, body_map)
        return

    if preset.body_shape == "rounded":
        render_rounded_body(canvas, preset, layout, body_map, render_scale)
        return

    if preset.body_shape == "spikes":
        render_spikes_body(canvas, preset, layout, body_map, render_scale)
        return

    if preset.body_shape == "claws":
        render_claws_body(canvas, preset, layout, body_map)
        return

    render_square_body(canvas, preset, layout, body_map)
