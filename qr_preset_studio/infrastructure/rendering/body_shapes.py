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
        _render_connected_rounded_body(canvas, preset, layout, body_map, render_scale)
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
    render_scale: float,
) -> None:
    radius = _body_radius(preset, layout, render_scale)
    if radius <= 0:
        _render_square_body(canvas, preset, layout, body_map)
        return

    draw = ImageDraw.Draw(canvas)

    for row, line in enumerate(body_map):
        for col, is_dark in enumerate(line):
            if not is_dark:
                continue

            center_x, center_y = _module_center(layout, col, row)

            if _has_right(body_map, row, col):
                right_x, _ = _module_center(layout, col + 1, row)
                draw.rounded_rectangle(
                    (center_x - radius, center_y - radius, right_x + radius, center_y + radius),
                    radius=radius,
                    fill=module_color(col + 0.5, row, layout.active_modules, preset),
                )

            if _has_down(body_map, row, col):
                _, down_y = _module_center(layout, col, row + 1)
                draw.rounded_rectangle(
                    (center_x - radius, center_y - radius, center_x + radius, down_y + radius),
                    radius=radius,
                    fill=module_color(col, row + 0.5, layout.active_modules, preset),
                )

    for row, line in enumerate(body_map):
        for col, is_dark in enumerate(line):
            if not is_dark:
                continue

            center_x, center_y = _module_center(layout, col, row)
            draw.ellipse(
                _ellipse_rect(center_x, center_y, radius),
                fill=module_color(col, row, layout.active_modules, preset),
            )


def _body_radius(preset: Preset, layout, render_scale: float) -> int:
    requested = max(0, int(round(preset.rounded_body_radius_px * render_scale)))
    module_pitch = layout.active_qr_size / max(1, layout.active_modules)
    max_radius = max(1, int(round(module_pitch / 2)))
    return min(requested, max_radius)


def _module_center(layout, col: int, row: int) -> tuple[int, int]:
    left, top, right, bottom = active_rect(
        active_x=layout.active_x,
        active_y=layout.active_y,
        active_col=col,
        active_row=row,
        span=1,
        active_modules=layout.active_modules,
        active_qr_size=layout.active_qr_size,
    )
    return (left + right) // 2, (top + bottom) // 2


def _ellipse_rect(center_x: int, center_y: int, radius: int) -> tuple[int, int, int, int]:
    return center_x - radius, center_y - radius, center_x + radius, center_y + radius


def _has_right(body_map: list[list[bool]], row: int, col: int) -> bool:
    return col + 1 < len(body_map[row]) and body_map[row][col + 1]


def _has_down(body_map: list[list[bool]], row: int, col: int) -> bool:
    return row + 1 < len(body_map) and body_map[row + 1][col]