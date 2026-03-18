from __future__ import annotations

from pathlib import Path
from typing import Iterable

import qrcode
from PIL import Image, ImageColor, ImageDraw, ImageOps

from .models import Preset

FINDER_SIZE = 7
FINDER_BALL_OFFSET = 2
FINDER_BALL_SIZE = 3
QR_BORDER_MODULES = 4
PREVIEW_MAX_SIZE = (900, 900)


def render_preview(preset: Preset, zoom_percent: int = 100) -> Image.Image:
    fit_factor = min(
        PREVIEW_MAX_SIZE[0] / max(1, preset.canvas_width),
        PREVIEW_MAX_SIZE[1] / max(1, preset.canvas_height),
        1.0,
    )
    zoom_factor = max(10, zoom_percent) / 100
    return render_preset(preset.scaled_copy(fit_factor * zoom_factor))


def render_preset(preset: Preset) -> Image.Image:
    canvas = _build_canvas(preset)
    if not preset.link.strip():
        return canvas

    matrix = _build_matrix(preset.link)
    matrix_size = len(matrix)
    active_modules = _active_module_count(matrix_size)
    active_qr_size = max(
        64,
        int(round(min(preset.canvas_width, preset.canvas_height) * (preset.qr_scale_percent / 100))),
    )

    padding = max(0, preset.qr_background_padding)
    border_width = max(0, preset.qr_border_width)
    corner_radius = max(0, preset.qr_background_radius)
    card_size = active_qr_size + (padding * 2) + (border_width * 2)

    active_x = ((preset.canvas_width - card_size) // 2) + preset.qr_offset_x + padding + border_width
    active_y = ((preset.canvas_height - card_size) // 2) + preset.qr_offset_y + padding + border_width

    if preset.qr_background_enabled:
        card_rect = (
            active_x - padding - border_width,
            active_y - padding - border_width,
            active_x + active_qr_size + padding + border_width,
            active_y + active_qr_size + padding + border_width,
        )
        ImageDraw.Draw(canvas).rounded_rectangle(
            card_rect,
            radius=corner_radius,
            fill=preset.qr_background_color,
            outline=preset.qr_border_color if border_width > 0 else None,
            width=border_width,
        )

    finder_origins = _finder_origins(active_modules)
    module_thickness = max(1, int(round(active_qr_size / max(1, active_modules))))
    qr_draw = ImageDraw.Draw(canvas)

    for row, line in enumerate(matrix):
        if row < QR_BORDER_MODULES or row >= matrix_size - QR_BORDER_MODULES:
            continue
        active_row = row - QR_BORDER_MODULES

        for col, is_dark in enumerate(line):
            if not is_dark or col < QR_BORDER_MODULES or col >= matrix_size - QR_BORDER_MODULES:
                continue

            active_col = col - QR_BORDER_MODULES
            if _in_finder_area(active_row, active_col, finder_origins):
                continue

            color = _module_color(active_col, active_row, active_modules, preset)
            rect = _active_rect(
                active_x=active_x,
                active_y=active_y,
                active_col=active_col,
                active_row=active_row,
                span=1,
                active_modules=active_modules,
                active_qr_size=active_qr_size,
            )
            _draw_body_module(qr_draw, rect, color, preset.body_shape)

    for origin_col, origin_row in finder_origins:
        frame_rect = _active_rect(
            active_x=active_x,
            active_y=active_y,
            active_col=origin_col,
            active_row=origin_row,
            span=FINDER_SIZE,
            active_modules=active_modules,
            active_qr_size=active_qr_size,
        )
        frame_color = _module_color(
            origin_col + ((FINDER_SIZE - 1) / 2),
            origin_row + ((FINDER_SIZE - 1) / 2),
            active_modules,
            preset,
        )
        _draw_eye_frame(
            qr_draw,
            frame_rect,
            module_thickness,
            preset.eye_frame_shape,
            frame_color,
        )

        ball_col = origin_col + FINDER_BALL_OFFSET
        ball_row = origin_row + FINDER_BALL_OFFSET
        ball_rect = _active_rect(
            active_x=active_x,
            active_y=active_y,
            active_col=ball_col,
            active_row=ball_row,
            span=FINDER_BALL_SIZE,
            active_modules=active_modules,
            active_qr_size=active_qr_size,
        )
        ball_color = _module_color(
            ball_col + ((FINDER_BALL_SIZE - 1) / 2),
            ball_row + ((FINDER_BALL_SIZE - 1) / 2),
            active_modules,
            preset,
        )
        _draw_eye_ball(qr_draw, ball_rect, preset.eye_ball_shape, ball_color)

    return canvas


def _build_canvas(preset: Preset) -> Image.Image:
    size = (preset.canvas_width, preset.canvas_height)
    image_path = Path(preset.background_image_path).expanduser()
    if image_path.is_file():
        image = Image.open(image_path).convert("RGBA")
        return ImageOps.fit(image, size, method=Image.Resampling.LANCZOS)
    return Image.new("RGBA", size, preset.canvas_background_color)


def _build_matrix(link: str) -> list[list[bool]]:
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=1,
        border=QR_BORDER_MODULES,
    )
    qr.add_data(link)
    qr.make(fit=True)
    return qr.get_matrix()


def _active_module_count(matrix_size: int) -> int:
    return max(1, matrix_size - (QR_BORDER_MODULES * 2))


def _finder_origins(active_modules: int) -> list[tuple[int, int]]:
    end = active_modules - FINDER_SIZE
    return [(0, 0), (end, 0), (0, end)]


def _in_finder_area(row: int, col: int, origins: Iterable[tuple[int, int]]) -> bool:
    for origin_col, origin_row in origins:
        if origin_col <= col < origin_col + FINDER_SIZE and origin_row <= row < origin_row + FINDER_SIZE:
            return True
    return False


def _module_color(col: float, row: float, active_modules: int, preset: Preset) -> tuple[int, int, int]:
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


def _grid_edge(origin: int, index: int | float, active_modules: int, active_qr_size: int) -> int:
    return origin + int(round((index * active_qr_size) / max(1, active_modules)))


def _active_rect(
    active_x: int,
    active_y: int,
    active_col: int,
    active_row: int,
    span: int,
    active_modules: int,
    active_qr_size: int,
) -> tuple[int, int, int, int]:
    left = _grid_edge(active_x, active_col, active_modules, active_qr_size)
    top = _grid_edge(active_y, active_row, active_modules, active_qr_size)
    right = _grid_edge(active_x, active_col + span, active_modules, active_qr_size)
    bottom = _grid_edge(active_y, active_row + span, active_modules, active_qr_size)

    if right <= left:
        right = left + 1
    if bottom <= top:
        bottom = top + 1

    return left, top, right, bottom


def _draw_body_module(
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


def _draw_eye_frame(
    draw: ImageDraw.ImageDraw,
    rect: tuple[int, int, int, int],
    module_thickness: int,
    shape: str,
    color: tuple[int, int, int],
) -> None:
    if shape == "rounded":
        radius = max(1, int(min(rect[2] - rect[0], rect[3] - rect[1]) * 0.16))
        draw.rounded_rectangle(rect, radius=radius, outline=color, width=module_thickness)
        return
    draw.rectangle(rect, outline=color, width=module_thickness)


def _draw_eye_ball(
    draw: ImageDraw.ImageDraw,
    rect: tuple[int, int, int, int],
    shape: str,
    color: tuple[int, int, int],
) -> None:
    if shape == "circle":
        draw.ellipse(rect, fill=color)
        return
    draw.rectangle(rect, fill=color)