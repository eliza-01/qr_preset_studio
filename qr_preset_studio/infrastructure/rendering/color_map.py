# qr_preset_studio/infrastructure/rendering/color_map.py
from __future__ import annotations

from PIL import ImageColor

from qr_preset_studio.domain.models.preset import Preset


def module_color(
    col: float,
    row: float,
    active_modules: int,
    active_qr_size: int,
    preset: Preset,
) -> tuple[int, int, int]:
    start = ImageColor.getrgb(preset.qr_foreground_color)
    if not preset.gradient_enabled:
        return start

    end = ImageColor.getrgb(preset.gradient_color)
    module_pitch = active_qr_size / max(1, active_modules)
    max_index = max(1, active_modules - 1)
    max_axis_px = max(1.0, max_index * module_pitch)

    x = float(col) * module_pitch
    y = float(row) * module_pitch
    offset = _gradient_offset_px(preset)

    if preset.gradient_direction == "horizontal":
        t = (x - offset) / max_axis_px
    elif preset.gradient_direction == "vertical":
        t = (y - offset) / max_axis_px
    elif preset.gradient_direction == "diagonal_up":
        t = (x + (max_axis_px - y) - offset) / (max_axis_px * 2.0)
    else:
        t = (x + y - offset) / (max_axis_px * 2.0)

    t = max(0.0, min(1.0, t))
    return tuple(int(round(a + (b - a) * t)) for a, b in zip(start, end))


def _gradient_offset_px(preset: Preset) -> int:
    if preset.gradient_direction == "horizontal":
        return preset.gradient_offset_horizontal_px
    if preset.gradient_direction == "vertical":
        return preset.gradient_offset_vertical_px
    if preset.gradient_direction == "diagonal_up":
        return preset.gradient_offset_diagonal_up_px
    return preset.gradient_offset_diagonal_down_px
