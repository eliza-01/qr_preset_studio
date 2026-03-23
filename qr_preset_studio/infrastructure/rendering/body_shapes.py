from __future__ import annotations

from PIL import Image, ImageDraw

from qr_preset_studio.domain.models.preset import Preset
from qr_preset_studio.infrastructure.rendering.color_map import module_color
from qr_preset_studio.infrastructure.rendering.geometry import grid_edge


LIQUID_OVERSAMPLE = 4


def draw_body_module(
    draw: ImageDraw.ImageDraw,
    rect: tuple[int, int, int, int],
    color: tuple[int, int, int],
    shape: str,
) -> None:
    if shape == "rounded":
        radius = max(1, int(min(rect[2] - rect[0], rect[3] - rect[1]) * 0.3))
        draw.rounded_rectangle(rect, radius=radius, fill=color)
        return
    draw.rectangle(rect, fill=color)


def render_liquid_body(
    canvas: Image.Image,
    preset: Preset,
    layout,
    body_map: list[list[bool]],
) -> None:
    layer = Image.new(
        "RGBA",
        (canvas.width * LIQUID_OVERSAMPLE, canvas.height * LIQUID_OVERSAMPLE),
        (0, 0, 0, 0),
    )
    draw = ImageDraw.Draw(layer)
    module_pitch = layout.active_qr_size / max(1, layout.active_modules)
    diameter = max(
        1,
        int(round(module_pitch * (preset.liquid_body_size_percent / 100) * LIQUID_OVERSAMPLE)),
    )
    radius = max(1, diameter // 2)

    for row, line in enumerate(body_map):
        for col, is_dark in enumerate(line):
            if not is_dark:
                continue

            center_x, center_y = _scaled_center(layout, col, row)
            color = (*module_color(col, row, layout.active_modules, preset), 255)

            draw.ellipse(_ellipse_rect(center_x, center_y, radius), fill=color)

            if _has_right(body_map, row, col):
                right_x, _ = _scaled_center(layout, col + 1, row)
                draw.rounded_rectangle(
                    (center_x - radius, center_y - radius, right_x + radius, center_y + radius),
                    radius=radius,
                    fill=color,
                )

            if _has_down(body_map, row, col):
                _, down_y = _scaled_center(layout, col, row + 1)
                draw.rounded_rectangle(
                    (center_x - radius, center_y - radius, center_x + radius, down_y + radius),
                    radius=radius,
                    fill=color,
                )

    layer = layer.resize(canvas.size, Image.Resampling.LANCZOS)
    canvas.alpha_composite(layer)


def _scaled_center(layout, col: int, row: int) -> tuple[int, int]:
    center_x = grid_edge(layout.active_x, col + 0.5, layout.active_modules, layout.active_qr_size)
    center_y = grid_edge(layout.active_y, row + 0.5, layout.active_modules, layout.active_qr_size)
    return center_x * LIQUID_OVERSAMPLE, center_y * LIQUID_OVERSAMPLE


def _ellipse_rect(center_x: int, center_y: int, radius: int) -> tuple[int, int, int, int]:
    return center_x - radius, center_y - radius, center_x + radius, center_y + radius


def _has_right(body_map: list[list[bool]], row: int, col: int) -> bool:
    return col + 1 < len(body_map[row]) and body_map[row][col + 1]


def _has_down(body_map: list[list[bool]], row: int, col: int) -> bool:
    return row + 1 < len(body_map) and body_map[row + 1][col]