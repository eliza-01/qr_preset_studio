from __future__ import annotations

from PIL import Image, ImageDraw

from qr_preset_studio.domain.models.preset import Preset
from qr_preset_studio.infrastructure.rendering.canvas import build_canvas
from qr_preset_studio.infrastructure.rendering.color_map import module_color
from qr_preset_studio.infrastructure.rendering.constants import (
    FINDER_BALL_OFFSET,
    FINDER_BALL_SIZE,
    FINDER_SIZE,
    QR_BORDER_MODULES,
)
from qr_preset_studio.infrastructure.rendering.drawers import (
    draw_body_module,
    draw_eye_ball,
    draw_eye_frame,
)
from qr_preset_studio.infrastructure.rendering.geometry import active_rect, build_qr_layout
from qr_preset_studio.infrastructure.rendering.qr_matrix import (
    active_module_count,
    build_matrix,
    finder_origins,
    in_finder_area,
)


def render_preset(preset: Preset) -> Image.Image:
    canvas = build_canvas(preset)
    if not preset.link.strip():
        return canvas

    matrix = build_matrix(preset.link)
    matrix_size = len(matrix)
    active_modules = active_module_count(matrix_size)
    layout = build_qr_layout(preset, active_modules)
    origins = finder_origins(active_modules)

    _draw_card(canvas, preset, layout)
    _draw_modules(canvas, preset, matrix, matrix_size, layout, origins)
    _draw_finders(canvas, preset, layout, origins)
    return canvas


def _draw_card(canvas: Image.Image, preset: Preset, layout) -> None:
    if not preset.qr_background_enabled:
        return
    ImageDraw.Draw(canvas).rounded_rectangle(
        layout.card_rect,
        radius=layout.corner_radius,
        fill=preset.qr_background_color,
        outline=preset.qr_border_color if layout.border_width > 0 else None,
        width=layout.border_width,
    )


def _draw_modules(canvas: Image.Image, preset: Preset, matrix, matrix_size: int, layout, origins) -> None:
    draw = ImageDraw.Draw(canvas)
    for row, line in enumerate(matrix):
        if row < QR_BORDER_MODULES or row >= matrix_size - QR_BORDER_MODULES:
            continue
        active_row = row - QR_BORDER_MODULES

        for col, is_dark in enumerate(line):
            if not is_dark or col < QR_BORDER_MODULES or col >= matrix_size - QR_BORDER_MODULES:
                continue

            active_col = col - QR_BORDER_MODULES
            if in_finder_area(active_row, active_col, origins):
                continue

            rect = active_rect(
                active_x=layout.active_x,
                active_y=layout.active_y,
                active_col=active_col,
                active_row=active_row,
                span=1,
                active_modules=layout.active_modules,
                active_qr_size=layout.active_qr_size,
            )
            draw_body_module(
                draw,
                rect,
                module_color(active_col, active_row, layout.active_modules, preset),
                preset.body_shape,
            )


def _draw_finders(canvas: Image.Image, preset: Preset, layout, origins) -> None:
    draw = ImageDraw.Draw(canvas)
    for origin_col, origin_row in origins:
        frame_rect = active_rect(
            active_x=layout.active_x,
            active_y=layout.active_y,
            active_col=origin_col,
            active_row=origin_row,
            span=FINDER_SIZE,
            active_modules=layout.active_modules,
            active_qr_size=layout.active_qr_size,
        )
        frame_color = module_color(
            origin_col + ((FINDER_SIZE - 1) / 2),
            origin_row + ((FINDER_SIZE - 1) / 2),
            layout.active_modules,
            preset,
        )
        draw_eye_frame(
            draw,
            frame_rect,
            layout.module_thickness,
            preset.eye_frame_shape,
            frame_color,
        )

        ball_col = origin_col + FINDER_BALL_OFFSET
        ball_row = origin_row + FINDER_BALL_OFFSET
        ball_rect = active_rect(
            active_x=layout.active_x,
            active_y=layout.active_y,
            active_col=ball_col,
            active_row=ball_row,
            span=FINDER_BALL_SIZE,
            active_modules=layout.active_modules,
            active_qr_size=layout.active_qr_size,
        )
        ball_color = module_color(
            ball_col + ((FINDER_BALL_SIZE - 1) / 2),
            ball_row + ((FINDER_BALL_SIZE - 1) / 2),
            layout.active_modules,
            preset,
        )
        draw_eye_ball(draw, ball_rect, preset.eye_ball_shape, ball_color)
