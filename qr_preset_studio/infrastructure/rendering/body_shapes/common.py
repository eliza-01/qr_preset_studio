from __future__ import annotations

from collections.abc import Iterator

from PIL import Image, ImageDraw

from qr_preset_studio.domain.models.preset import Preset
from qr_preset_studio.infrastructure.rendering.color_map import module_color
from qr_preset_studio.infrastructure.rendering.geometry import active_rect


def iter_dark_modules(body_map: list[list[bool]]) -> Iterator[tuple[int, int]]:
    for row, line in enumerate(body_map):
        for col, is_dark in enumerate(line):
            if is_dark:
                yield row, col


def module_rect(layout, col: int, row: int) -> tuple[int, int, int, int]:
    return active_rect(
        active_x=layout.active_x,
        active_y=layout.active_y,
        active_col=col,
        active_row=row,
        span=1,
        active_modules=layout.active_modules,
        active_qr_size=layout.active_qr_size,
    )


def rect_size(rect: tuple[int, int, int, int]) -> tuple[int, int]:
    return max(1, rect[2] - rect[0]), max(1, rect[3] - rect[1])


def paint_module_colors(
    canvas: Image.Image,
    preset: Preset,
    layout,
    body_map: list[list[bool]],
) -> None:
    draw = ImageDraw.Draw(canvas)

    for row, col in iter_dark_modules(body_map):
        draw.rectangle(
            module_rect(layout, col, row),
            fill=module_color(col, row, layout.active_modules, layout.active_qr_size, preset),
        )


def exposed_sides(body_map: list[list[bool]], row: int, col: int) -> tuple[bool, bool, bool, bool]:
    up = _has_up(body_map, row, col)
    right = _has_right(body_map, row, col)
    down = _has_down(body_map, row, col)
    left = _has_left(body_map, row, col)
    return not up, not right, not down, not left


def free_corners(body_map: list[list[bool]], row: int, col: int) -> tuple[bool, bool, bool, bool]:
    top, right, bottom, left = exposed_sides(body_map, row, col)
    return (
        top and left,
        top and right,
        bottom and right,
        bottom and left,
    )


def _has_up(body_map: list[list[bool]], row: int, col: int) -> bool:
    return row > 0 and body_map[row - 1][col]


def _has_right(body_map: list[list[bool]], row: int, col: int) -> bool:
    return col + 1 < len(body_map[row]) and body_map[row][col + 1]


def _has_down(body_map: list[list[bool]], row: int, col: int) -> bool:
    return row + 1 < len(body_map) and body_map[row + 1][col]


def _has_left(body_map: list[list[bool]], row: int, col: int) -> bool:
    return col > 0 and body_map[row][col - 1]