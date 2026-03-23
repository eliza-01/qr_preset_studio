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


def render_liquid_body(
    canvas: Image.Image,
    preset: Preset,
    layout,
    body_map: list[list[bool]],
) -> None:
    body_layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    paint_module_colors(body_layer, preset, layout, body_map)

    mask = Image.new("L", canvas.size, 0)

    for row, col in iter_dark_modules(body_map):
        rect = module_rect(layout, col, row)
        tile = _liquid_tile(rect, free_corners(body_map, row, col))
        mask.paste(tile, (rect[0], rect[1]))

    body_layer.putalpha(mask)
    canvas.alpha_composite(body_layer)


def _liquid_tile(
    rect: tuple[int, int, int, int],
    corners: tuple[bool, bool, bool, bool],
) -> Image.Image:
    width, height = rect_size(rect)
    free_count = sum(1 for value in corners if value)

    if free_count == 0:
        return _filled_rect_tile(width, height)

    if free_count == 1:
        return _quarter_turn_tile(width, height, _single_free_corner(corners))

    if free_count == 2:
        exposed_side = _single_connection_exposed_side(corners)
        if exposed_side is not None:
            return _single_connection_tile(width, height, exposed_side)
        return _filled_rect_tile(width, height)

    if free_count == 4:
        return _circle_tile(width, height)

    return _filled_rect_tile(width, height)


def _filled_rect_tile(width: int, height: int) -> Image.Image:
    tile = Image.new("L", (width, height), 0)
    ImageDraw.Draw(tile).rectangle((0, 0, width - 1, height - 1), fill=255)
    return tile


def _circle_tile(width: int, height: int) -> Image.Image:
    tile = Image.new("L", (width, height), 0)
    ImageDraw.Draw(tile).ellipse((0, 0, width - 1, height - 1), fill=255)
    return tile


def _quarter_turn_tile(width: int, height: int, free_corner: str) -> Image.Image:
    source = Image.new("L", (width * 2, height * 2), 0)
    ImageDraw.Draw(source).ellipse((0, 0, (width * 2) - 1, (height * 2) - 1), fill=255)
    return source.crop(_quarter_crop_box(width, height, free_corner))


def _quarter_crop_box(width: int, height: int, free_corner: str) -> tuple[int, int, int, int]:
    mapping = {
        "top_left": (0, 0, width, height),
        "top_right": (width, 0, width * 2, height),
        "bottom_right": (width, height, width * 2, height * 2),
        "bottom_left": (0, height, width, height * 2),
    }
    return mapping[free_corner]


def _single_connection_tile(width: int, height: int, exposed_side: str) -> Image.Image:
    tile = Image.new("L", (width, height), 0)
    draw = ImageDraw.Draw(tile)
    radius = min(width, height) // 2

    if radius <= 0:
        draw.rectangle((0, 0, width - 1, height - 1), fill=255)
        return tile

    if exposed_side == "left":
        _fill_rect(draw, (radius, 0, width, height))
        draw.ellipse((0, 0, (radius * 2) - 1, height - 1), fill=255)
        return tile

    if exposed_side == "right":
        _fill_rect(draw, (0, 0, width - radius, height))
        draw.ellipse((width - (radius * 2), 0, width - 1, height - 1), fill=255)
        return tile

    if exposed_side == "top":
        _fill_rect(draw, (0, radius, width, height))
        draw.ellipse((0, 0, width - 1, (radius * 2) - 1), fill=255)
        return tile

    _fill_rect(draw, (0, 0, width, height - radius))
    draw.ellipse((0, height - (radius * 2), width - 1, height - 1), fill=255)
    return tile


def _single_free_corner(corners: tuple[bool, bool, bool, bool]) -> str:
    for corner_name, enabled in zip(
        ("top_left", "top_right", "bottom_right", "bottom_left"),
        corners,
    ):
        if enabled:
            return corner_name
    return "top_left"


def _single_connection_exposed_side(corners: tuple[bool, bool, bool, bool]) -> str | None:
    top_left, top_right, bottom_right, bottom_left = corners

    if top_left and bottom_left and not top_right and not bottom_right:
        return "left"

    if top_left and top_right and not bottom_right and not bottom_left:
        return "top"

    if top_right and bottom_right and not top_left and not bottom_left:
        return "right"

    if bottom_right and bottom_left and not top_left and not top_right:
        return "bottom"

    return None


def _fill_rect(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int]) -> None:
    left, top, right, bottom = box
    if right <= left or bottom <= top:
        return
    draw.rectangle((left, top, right - 1, bottom - 1), fill=255)