from __future__ import annotations

from PIL import Image, ImageDraw

from qr_preset_studio.domain.models.preset import Preset
from qr_preset_studio.infrastructure.rendering.color_map import module_color
from qr_preset_studio.infrastructure.rendering.geometry import active_rect, grid_edge


BODY_OVERSAMPLE = 6


def render_body(
    canvas: Image.Image,
    preset: Preset,
    layout,
    body_map: list[list[bool]],
) -> None:
    if preset.body_shape == "rounded":
        _render_connected_rounded_body(canvas, preset, layout, body_map)
        return

    _render_square_body(canvas, preset, layout, body_map)


def _render_square_body(
    canvas: Image.Image,
    preset: Preset,
    layout,
    body_map: list[list[bool]],
) -> None:
    draw = ImageDraw.Draw(canvas)

    for row, line in enumerate(body_map):
        for col, is_dark in enumerate(line):
            if not is_dark:
                continue

            rect = active_rect(
                active_x=layout.active_x,
                active_y=layout.active_y,
                active_col=col,
                active_row=row,
                span=1,
                active_modules=layout.active_modules,
                active_qr_size=layout.active_qr_size,
            )
            draw.rectangle(rect, fill=module_color(col, row, layout.active_modules, preset))


def _render_connected_rounded_body(
    canvas: Image.Image,
    preset: Preset,
    layout,
    body_map: list[list[bool]],
) -> None:
    layer = Image.new(
        "RGBA",
        (canvas.width * BODY_OVERSAMPLE, canvas.height * BODY_OVERSAMPLE),
        (0, 0, 0, 0),
    )
    draw = ImageDraw.Draw(layer)

    module_pitch = layout.active_qr_size / max(1, layout.active_modules)
    strength = max(10, min(100, int(preset.rounded_body_strength_percent)))
    diameter = max(1, int(round(module_pitch * (strength / 100) * BODY_OVERSAMPLE)))
    radius = max(1, diameter // 2)

    for row, line in enumerate(body_map):
        for col, is_dark in enumerate(line):
            if not is_dark:
                continue

            center_x, center_y = _scaled_center(layout, col, row)

            if _has_right(body_map, row, col):
                right_x, _ = _scaled_center(layout, col + 1, row)
                draw.rounded_rectangle(
                    (center_x - radius, center_y - radius, right_x + radius, center_y + radius),
                    radius=radius,
                    fill=_rgba(module_color(col + 0.5, row, layout.active_modules, preset)),
                )

            if _has_down(body_map, row, col):
                _, down_y = _scaled_center(layout, col, row + 1)
                draw.rounded_rectangle(
                    (center_x - radius, center_y - radius, center_x + radius, down_y + radius),
                    radius=radius,
                    fill=_rgba(module_color(col, row + 0.5, layout.active_modules, preset)),
                )

    for row, line in enumerate(body_map):
        for col, is_dark in enumerate(line):
            if not is_dark:
                continue

            center_x, center_y = _scaled_center(layout, col, row)
            draw.ellipse(
                _ellipse_rect(center_x, center_y, radius),
                fill=_rgba(module_color(col, row, layout.active_modules, preset)),
            )

    layer = layer.resize(canvas.size, Image.Resampling.LANCZOS)
    canvas.alpha_composite(layer)


def _scaled_center(layout, col: int, row: int) -> tuple[int, int]:
    center_x = grid_edge(layout.active_x, col + 0.5, layout.active_modules, layout.active_qr_size)
    center_y = grid_edge(layout.active_y, row + 0.5, layout.active_modules, layout.active_qr_size)
    return center_x * BODY_OVERSAMPLE, center_y * BODY_OVERSAMPLE


def _ellipse_rect(center_x: int, center_y: int, radius: int) -> tuple[int, int, int, int]:
    return center_x - radius, center_y - radius, center_x + radius, center_y + radius


def _rgba(color: tuple[int, int, int]) -> tuple[int, int, int, int]:
    return color[0], color[1], color[2], 255


def _has_right(body_map: list[list[bool]], row: int, col: int) -> bool:
    return col + 1 < len(body_map[row]) and body_map[row][col + 1]


def _has_down(body_map: list[list[bool]], row: int, col: int) -> bool:
    return row + 1 < len(body_map) and body_map[row + 1][col]