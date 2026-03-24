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


def render_claws_body(
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
        tile = _claws_tile(preset, rect, free_corners(body_map, row, col), row, col)
        mask.paste(tile, (rect[0], rect[1]))

    body_layer.putalpha(mask)
    canvas.alpha_composite(body_layer)


def _claws_tile(
    preset: Preset,
    rect: tuple[int, int, int, int],
    corners: tuple[bool, bool, bool, bool],
    row: int,
    col: int,
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
            return _claw_connection_tile(preset, width, height, exposed_side, row, col)
        return _filled_rect_tile(width, height)

    if free_count == 4:
        return _circle_tile(width, height)

    return _filled_rect_tile(width, height)


def _claw_connection_tile(
    preset: Preset,
    width: int,
    height: int,
    exposed_side: str,
    row: int,
    col: int,
) -> Image.Image:
    lean_right = _resolve_lean_right(preset, row, col)
    tile = _top_claw_tile(preset, width, height, lean_right)

    if exposed_side == "top":
        return tile
    if exposed_side == "right":
        return tile.transpose(Image.Transpose.ROTATE_270)
    if exposed_side == "bottom":
        return tile.transpose(Image.Transpose.ROTATE_180)
    return tile.transpose(Image.Transpose.ROTATE_90)


def _resolve_lean_right(preset: Preset, row: int, col: int) -> bool:
    if not preset.claw_alternate_direction:
        return preset.claw_lean_right

    lean_right = ((row + col) & 1) == 0
    return lean_right if preset.claw_lean_right else not lean_right


def _top_claw_tile(preset: Preset, width: int, height: int, lean_right: bool) -> Image.Image:
    scale = max(1, preset.claw_detail_scale)
    hi_width = max(12, width * scale)
    hi_height = max(12, height * scale)

    tile = Image.new("L", (hi_width, hi_height), 0)
    draw = ImageDraw.Draw(tile)
    draw.polygon(_top_claw_polygon(preset, hi_width, hi_height), fill=255)

    if not lean_right:
        tile = tile.transpose(Image.Transpose.FLIP_LEFT_RIGHT)

    return tile.resize((width, height), Image.Resampling.LANCZOS)


def _top_claw_polygon(preset: Preset, width: int, height: int) -> list[tuple[int, int]]:
    steps = max(4, preset.claw_curve_steps)

    base_left = (0.0, float(height))
    base_right = (float(width), float(height))
    tip = (width * preset.claw_tip_x, height * preset.claw_tip_y)

    outer_curve = _bezier_points(
        base_left,
        (width * preset.claw_outer_ctrl1_x, height * preset.claw_outer_ctrl1_y),
        (width * preset.claw_outer_ctrl2_x, height * preset.claw_outer_ctrl2_y),
        tip,
        steps=steps,
    )
    inner_curve = _bezier_points(
        tip,
        (width * preset.claw_inner_ctrl1_x, height * preset.claw_inner_ctrl1_y),
        (width * preset.claw_inner_ctrl2_x, height * preset.claw_inner_ctrl2_y),
        base_right,
        steps=steps,
    )

    polygon = [
        base_left,
        *outer_curve[1:],
        *inner_curve[1:],
        base_left,
    ]
    return [(int(round(x)), int(round(y))) for x, y in polygon]


def _bezier_points(
    p0: tuple[float, float],
    p1: tuple[float, float],
    p2: tuple[float, float],
    p3: tuple[float, float],
    *,
    steps: int,
) -> list[tuple[float, float]]:
    points: list[tuple[float, float]] = []

    for index in range(steps + 1):
        t = index / max(1, steps)
        nt = 1.0 - t
        x = (
            (nt**3) * p0[0]
            + 3.0 * (nt**2) * t * p1[0]
            + 3.0 * nt * (t**2) * p2[0]
            + (t**3) * p3[0]
        )
        y = (
            (nt**3) * p0[1]
            + 3.0 * (nt**2) * t * p1[1]
            + 3.0 * nt * (t**2) * p2[1]
            + (t**3) * p3[1]
        )
        points.append((x, y))

    return points


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