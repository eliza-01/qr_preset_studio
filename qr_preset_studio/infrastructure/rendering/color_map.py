from __future__ import annotations

from PIL import ImageColor

from qr_preset_studio.domain.models.preset import Preset


def module_color(col: float, row: float, active_modules: int, preset: Preset) -> tuple[int, int, int]:
    start = ImageColor.getrgb(preset.qr_foreground_color)
    if not preset.gradient_enabled:
        return start

    end = ImageColor.getrgb(preset.gradient_color)
    max_index = max(1, active_modules - 1)

    if preset.gradient_direction == "horizontal":
        t = col / max_index
    elif preset.gradient_direction == "vertical":
        t = row / max_index
    elif preset.gradient_direction == "diagonal_up":
        t = (col + (max_index - row)) / (max_index * 2)
    else:
        t = (col + row) / (max_index * 2)

    t = max(0.0, min(1.0, t))
    return tuple(int(round(a + (b - a) * t)) for a, b in zip(start, end))
