from __future__ import annotations

from PIL import Image, ImageDraw

from qr_preset_studio.domain.models.preset import Preset
from qr_preset_studio.infrastructure.rendering.color_map import module_color
from qr_preset_studio.infrastructure.rendering.geometry import active_rect


def render_body(
    canvas: Image.Image,
    preset: Preset,
    layout,
    body_map: list[list[bool]],
    render_scale: float = 1.0,
) -> None:
    if preset.body_shape == "rounded":
        _render_rounded_body(canvas, preset, layout, body_map, render_scale)
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


def _render_rounded_body(
    canvas: Image.Image,
    preset: Preset,
    layout,
    body_map: list[list[bool]],
    render_scale: float,
) -> None:
    requested_radius = _body_radius(preset, layout, render_scale)
    if requested_radius <= 0:
        _render_square_body(canvas, preset, layout, body_map)
        return

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
            radius = _rect_radius(rect, requested_radius)
            color = module_color(col, row, layout.active_modules, preset)
            corners = _rounded_corners(body_map, row, col)

            if radius <= 0 or not any(corners):
                draw.rectangle(rect, fill=color)
                continue

            draw.rounded_rectangle(
                rect,
                radius=radius,
                fill=color,
                corners=corners,
            )


def _body_radius(preset: Preset, layout, render_scale: float) -> int:
    requested = max(0, int(round(preset.rounded_body_radius_px * render_scale)))
    if requested <= 0:
        return 0

    module_pitch = layout.active_qr_size / max(1, layout.active_modules)
    max_radius = max(0, int(module_pitch / 2))
    return min(requested, max_radius)


def _rect_radius(rect: tuple[int, int, int, int], requested_radius: int) -> int:
    width = max(1, rect[2] - rect[0])
    height = max(1, rect[3] - rect[1])
    max_radius = max(0, min(width, height) // 2)
    return min(requested_radius, max_radius)


def _rounded_corners(body_map: list[list[bool]], row: int, col: int) -> tuple[bool, bool, bool, bool]:
    up = _has_up(body_map, row, col)
    right = _has_right(body_map, row, col)
    down = _has_down(body_map, row, col)
    left = _has_left(body_map, row, col)

    return (
        not up and not left,
        not up and not right,
        not down and not right,
        not down and not left,
    )


def _has_up(body_map: list[list[bool]], row: int, col: int) -> bool:
    return row > 0 and body_map[row - 1][col]


def _has_right(body_map: list[list[bool]], row: int, col: int) -> bool:
    return col + 1 < len(body_map[row]) and body_map[row][col + 1]


def _has_down(body_map: list[list[bool]], row: int, col: int) -> bool:
    return row + 1 < len(body_map) and body_map[row + 1][col]


def _has_left(body_map: list[list[bool]], row: int, col: int) -> bool:
    return col > 0 and body_map[row][col - 1]