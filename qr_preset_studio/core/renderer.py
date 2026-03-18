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


class RenderError(RuntimeError):
    pass


def render_preview(preset: Preset) -> Image.Image:
    factor = min(
        PREVIEW_MAX_SIZE[0] / preset.canvas_width,
        PREVIEW_MAX_SIZE[1] / preset.canvas_height,
        1.0,
    )
    return render_preset(preset.scaled_copy(factor))


def render_preset(preset: Preset) -> Image.Image:
    canvas = _build_canvas(preset)
    if not preset.link.strip():
        return canvas

    matrix = _build_matrix(preset.link)
    matrix_size = len(matrix)
    qr_target_size = max(64, int(min(preset.canvas_width, preset.canvas_height) * (preset.qr_scale_percent / 100)))
    module_size = max(1, qr_target_size // matrix_size)
    qr_size = matrix_size * module_size

    padding = max(0, preset.qr_background_padding)
    border_width = max(0, preset.qr_border_width)
    corner_radius = max(0, preset.qr_background_radius)
    card_size = qr_size + 2 * (padding + border_width)

    card_x = (preset.canvas_width - card_size) // 2 + preset.qr_offset_x
    card_y = (preset.canvas_height - card_size) // 2 + preset.qr_offset_y
    qr_x = card_x + padding + border_width
    qr_y = card_y + padding + border_width

    draw = ImageDraw.Draw(canvas)
    if preset.qr_background_enabled:
        card_rect = (card_x, card_y, card_x + card_size, card_y + card_size)
        draw.rounded_rectangle(
            card_rect,
            radius=corner_radius,
            fill=preset.qr_background_color,
            outline=preset.qr_border_color if border_width > 0 else None,
            width=border_width,
        )

    finder_origins = _finder_origins(matrix_size)
    qr_draw = ImageDraw.Draw(canvas)
    for row, line in enumerate(matrix):
        for col, is_dark in enumerate(line):
            if not is_dark:
                continue
            if _in_finder_area(row, col, finder_origins):
                continue
            color = _module_color(col, row, matrix_size, preset)
            rect = _module_rect(qr_x, qr_y, col, row, module_size)
            _draw_body_module(qr_draw, rect, color, preset.body_shape)

    for origin_col, origin_row in finder_origins:
        frame_rect = (
            qr_x + origin_col * module_size,
            qr_y + origin_row * module_size,
            qr_x + (origin_col + FINDER_SIZE) * module_size,
            qr_y + (origin_row + FINDER_SIZE) * module_size,
        )
        _draw_eye_frame(qr_draw, frame_rect, module_size, preset)
        ball_col = origin_col + FINDER_BALL_OFFSET
        ball_row = origin_row + FINDER_BALL_OFFSET
        ball_rect = (
            qr_x + ball_col * module_size,
            qr_y + ball_row * module_size,
            qr_x + (ball_col + FINDER_BALL_SIZE) * module_size,
            qr_y + (ball_row + FINDER_BALL_SIZE) * module_size,
        )
        _draw_eye_ball(qr_draw, ball_rect, preset)

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


def _finder_origins(matrix_size: int) -> list[tuple[int, int]]:
    start = QR_BORDER_MODULES
    end = matrix_size - QR_BORDER_MODULES - FINDER_SIZE
    return [(start, start), (end, start), (start, end)]


def _in_finder_area(row: int, col: int, origins: Iterable[tuple[int, int]]) -> bool:
    for origin_col, origin_row in origins:
        if origin_col <= col < origin_col + FINDER_SIZE and origin_row <= row < origin_row + FINDER_SIZE:
            return True
    return False


def _module_color(col: int, row: int, matrix_size: int, preset: Preset) -> tuple[int, int, int]:
    start = ImageColor.getrgb(preset.qr_foreground_color)
    if not preset.gradient_enabled:
        return start
    end = ImageColor.getrgb(preset.gradient_color)
    if matrix_size <= 1:
        t = 0.0
    elif preset.gradient_direction == "horizontal":
        t = col / (matrix_size - 1)
    elif preset.gradient_direction == "vertical":
        t = row / (matrix_size - 1)
    elif preset.gradient_direction == "diagonal_up":
        t = (col + (matrix_size - 1 - row)) / ((matrix_size - 1) * 2)
    else:
        t = (col + row) / ((matrix_size - 1) * 2)
    return tuple(int(round(a + (b - a) * t)) for a, b in zip(start, end))


def _module_rect(qr_x: int, qr_y: int, col: int, row: int, module_size: int) -> tuple[int, int, int, int]:
    left = qr_x + col * module_size
    top = qr_y + row * module_size
    return left, top, left + module_size, top + module_size


def _draw_body_module(draw: ImageDraw.ImageDraw, rect: tuple[int, int, int, int], color: tuple[int, int, int], shape: str) -> None:
    if shape == "rounded":
        radius = max(1, int((rect[2] - rect[0]) * 0.3))
        draw.rounded_rectangle(rect, radius=radius, fill=color)
        return
    draw.rectangle(rect, fill=color)


def _draw_eye_frame(draw: ImageDraw.ImageDraw, rect: tuple[int, int, int, int], module_size: int, preset: Preset) -> None:
    color = ImageColor.getrgb(preset.qr_foreground_color)
    thickness = max(1, module_size)
    if preset.eye_frame_shape == "rounded":
        radius = max(1, int((rect[2] - rect[0]) * 0.16))
        draw.rounded_rectangle(rect, radius=radius, outline=color, width=thickness)
        return
    draw.rectangle(rect, outline=color, width=thickness)


def _draw_eye_ball(draw: ImageDraw.ImageDraw, rect: tuple[int, int, int, int], preset: Preset) -> None:
    color = ImageColor.getrgb(preset.qr_foreground_color)
    if preset.gradient_enabled:
        color = ImageColor.getrgb(preset.gradient_color)
    if preset.eye_ball_shape == "circle":
        draw.ellipse(rect, fill=color)
        return
    draw.rectangle(rect, fill=color)
