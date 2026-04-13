# qr_preset_studio/infrastructure/rendering/body_shapes/rounded.py
from __future__ import annotations

from PIL import Image, ImageDraw

from qr_preset_studio.domain.models.preset import Preset
from qr_preset_studio.infrastructure.rendering.body_shapes.common import (
    free_corners,
    iter_dark_modules,
    module_rect,
    paint_module_colors,
    rect_size,
)


def render_rounded_body(
    canvas: Image.Image,
    preset: Preset,
    layout,
    body_map: list[list[bool]],
    render_scale: float,
) -> None:
    requested_radius = _rounded_body_radius(preset, layout, render_scale)
    if requested_radius <= 0:
        paint_module_colors(canvas, preset, layout, body_map)
        return

    body_layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    paint_module_colors(body_layer, preset, layout, body_map)

    mask = Image.new("L", canvas.size, 0)

    for row, col in iter_dark_modules(body_map):
        rect = module_rect(layout, col, row)
        tile = _rounded_tile(rect, free_corners(body_map, row, col), requested_radius)
        mask.paste(tile, (rect[0], rect[1]))

    body_layer.putalpha(mask)
    canvas.alpha_composite(body_layer)


def _rounded_body_radius(preset: Preset, layout, render_scale: float) -> int:
    requested = max(0, int(round(preset.rounded_body_radius_px * render_scale)))
    if requested <= 0:
        return 0

    module_pitch = layout.active_qr_size / max(1, layout.active_modules)
    max_radius = max(0, int(module_pitch / 2))
    return min(requested, max_radius)


def _rounded_tile(
    rect: tuple[int, int, int, int],
    corners: tuple[bool, bool, bool, bool],
    requested_radius: int,
) -> Image.Image:
    width, height = rect_size(rect)
    tile = Image.new("L", (width, height), 255)

    radius = min(requested_radius, min(width, height) // 2)
    if radius <= 0 or not any(corners):
        return tile

    draw = ImageDraw.Draw(tile)

    for corner_name, enabled in zip(
        ("top_left", "top_right", "bottom_right", "bottom_left"),
        corners,
    ):
        if not enabled:
            continue
        _round_corner(tile, draw, width, height, radius, corner_name)

    return tile


def _round_corner(
    tile: Image.Image,
    draw: ImageDraw.ImageDraw,
    width: int,
    height: int,
    radius: int,
    corner_name: str,
) -> None:
    clear_box = _corner_clear_box(width, height, radius, corner_name)
    _fill_rect(draw, clear_box, 0)

    tile.paste(_quarter_circle(radius, corner_name), _corner_paste_pos(width, height, radius, corner_name))


def _quarter_circle(radius: int, corner_name: str) -> Image.Image:
    source = Image.new("L", (radius * 2, radius * 2), 0)
    ImageDraw.Draw(source).ellipse((0, 0, (radius * 2) - 1, (radius * 2) - 1), fill=255)
    return source.crop(_quarter_crop_box(radius, corner_name))


def _quarter_crop_box(radius: int, corner_name: str) -> tuple[int, int, int, int]:
    mapping = {
        "top_left": (0, 0, radius, radius),
        "top_right": (radius, 0, radius * 2, radius),
        "bottom_right": (radius, radius, radius * 2, radius * 2),
        "bottom_left": (0, radius, radius, radius * 2),
    }
    return mapping[corner_name]


def _corner_paste_pos(width: int, height: int, radius: int, corner_name: str) -> tuple[int, int]:
    mapping = {
        "top_left": (0, 0),
        "top_right": (width - radius, 0),
        "bottom_right": (width - radius, height - radius),
        "bottom_left": (0, height - radius),
    }
    return mapping[corner_name]


def _corner_clear_box(width: int, height: int, radius: int, corner_name: str) -> tuple[int, int, int, int]:
    mapping = {
        "top_left": (0, 0, radius, radius),
        "top_right": (width - radius, 0, width, radius),
        "bottom_right": (width - radius, height - radius, width, height),
        "bottom_left": (0, height - radius, radius, height),
    }
    return mapping[corner_name]


def _fill_rect(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], fill: int) -> None:
    left, top, right, bottom = box
    if right <= left or bottom <= top:
        return
    draw.rectangle((left, top, right - 1, bottom - 1), fill=fill)
