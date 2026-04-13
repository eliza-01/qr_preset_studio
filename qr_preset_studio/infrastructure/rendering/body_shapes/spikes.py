# qr_preset_studio/infrastructure/rendering/body_shapes/spikes.py
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


def render_spikes_body(
    canvas: Image.Image,
    preset: Preset,
    layout,
    body_map: list[list[bool]],
    render_scale: float,
) -> None:
    body_layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    paint_module_colors(body_layer, preset, layout, body_map)

    mask = Image.new("L", canvas.size, 0)
    single_corner_radius = _spikes_single_corner_radius(preset, layout, render_scale)

    for row, col in iter_dark_modules(body_map):
        rect = module_rect(layout, col, row)
        tile = _spikes_tile(
            rect=rect,
            corners=free_corners(body_map, row, col),
            single_corner_radius=single_corner_radius,
        )
        mask.paste(tile, (rect[0], rect[1]))

    body_layer.putalpha(mask)
    canvas.alpha_composite(body_layer)


def _spikes_single_corner_radius(preset: Preset, layout, render_scale: float) -> int:
    requested = max(0, int(round(preset.spikes_single_corner_radius_px * render_scale)))
    if requested <= 0:
        return 0

    module_pitch = layout.active_qr_size / max(1, layout.active_modules)
    max_radius = max(0, int(module_pitch / 2))
    return min(requested, max_radius)


def _spikes_tile(
    *,
    rect: tuple[int, int, int, int],
    corners: tuple[bool, bool, bool, bool],
    single_corner_radius: int,
) -> Image.Image:
    width, height = rect_size(rect)
    free_count = sum(1 for value in corners if value)

    if free_count == 0:
        return _filled_rect_tile(width, height)

    if free_count == 1:
        corner_name = _single_free_corner(corners)
        if single_corner_radius > 0:
            return _rounded_single_corner_tile(width, height, single_corner_radius, corner_name)
        return _beveled_single_corner_tile(width, height, corner_name)

    if free_count == 2:
        dead_side = _dead_end_side(corners)
        if dead_side is not None:
            return _dead_end_tile(width, height, dead_side)
        return _filled_rect_tile(width, height)

    if free_count == 4:
        return _diamond_tile(width, height)

    return _filled_rect_tile(width, height)


def _filled_rect_tile(width: int, height: int) -> Image.Image:
    tile = Image.new("L", (width, height), 0)
    ImageDraw.Draw(tile).rectangle((0, 0, width - 1, height - 1), fill=255)
    return tile


def _diamond_tile(width: int, height: int) -> Image.Image:
    tile = Image.new("L", (width, height), 0)
    draw = ImageDraw.Draw(tile)

    last_x = width - 1
    last_y = height - 1
    mid_x = width // 2
    mid_y = height // 2

    draw.polygon(
        [
            (mid_x, 0),
            (last_x, mid_y),
            (mid_x, last_y),
            (0, mid_y),
        ],
        fill=255,
    )
    return tile


def _beveled_single_corner_tile(width: int, height: int, corner_name: str) -> Image.Image:
    tile = Image.new("L", (width, height), 0)
    draw = ImageDraw.Draw(tile)

    last_x = width - 1
    last_y = height - 1
    mid_x = width // 2
    mid_y = height // 2

    if corner_name == "top_left":
        points = [
            (mid_x, 0),
            (last_x, 0),
            (last_x, last_y),
            (0, last_y),
            (0, mid_y),
        ]
    elif corner_name == "top_right":
        points = [
            (0, 0),
            (mid_x, 0),
            (last_x, mid_y),
            (last_x, last_y),
            (0, last_y),
        ]
    elif corner_name == "bottom_right":
        points = [
            (0, 0),
            (last_x, 0),
            (last_x, mid_y),
            (mid_x, last_y),
            (0, last_y),
        ]
    else:
        points = [
            (0, 0),
            (last_x, 0),
            (last_x, last_y),
            (mid_x, last_y),
            (0, mid_y),
        ]

    draw.polygon(points, fill=255)
    return tile


def _rounded_single_corner_tile(
    width: int,
    height: int,
    requested_radius: int,
    corner_name: str,
) -> Image.Image:
    tile = Image.new("L", (width, height), 255)

    radius = min(requested_radius, width // 2, height // 2)
    if radius <= 0:
        return tile

    draw = ImageDraw.Draw(tile)
    _fill_rect(draw, _corner_clear_box(width, height, radius, corner_name), 0)
    tile.paste(
        _quarter_circle(radius, corner_name),
        _corner_paste_pos(width, height, radius, corner_name),
    )
    return tile


def _dead_end_tile(width: int, height: int, dead_side: str) -> Image.Image:
    tile = Image.new("L", (width, height), 0)
    draw = ImageDraw.Draw(tile)

    last_x = width - 1
    last_y = height - 1
    mid_x = width // 2
    mid_y = height // 2

    if dead_side == "left":
        points = [
            (last_x, 0),
            (last_x, last_y),
            (0, mid_y),
        ]
    elif dead_side == "top":
        points = [
            (0, last_y),
            (mid_x, 0),
            (last_x, last_y),
        ]
    elif dead_side == "right":
        points = [
            (0, 0),
            (last_x, mid_y),
            (0, last_y),
        ]
    else:
        points = [
            (0, 0),
            (last_x, 0),
            (mid_x, last_y),
        ]

    draw.polygon(points, fill=255)
    return tile


def _single_free_corner(corners: tuple[bool, bool, bool, bool]) -> str:
    for corner_name, enabled in zip(
        ("top_left", "top_right", "bottom_right", "bottom_left"),
        corners,
    ):
        if enabled:
            return corner_name
    return "top_left"


def _dead_end_side(corners: tuple[bool, bool, bool, bool]) -> str | None:
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
