# qr_preset_studio/infrastructure/rendering/composer.py
from __future__ import annotations

from PIL import Image, ImageDraw

from qr_preset_studio.domain.models.preset import Preset
from qr_preset_studio.infrastructure.rendering.body_shapes import render_body
from qr_preset_studio.infrastructure.rendering.canvas import build_canvas
from qr_preset_studio.infrastructure.rendering.color_map import module_color
from qr_preset_studio.infrastructure.rendering.constants import (
    FINDER_BALL_OFFSET,
    FINDER_BALL_SIZE,
    FINDER_SIZE,
    MAX_EXPORT_SIDE,
    MAX_QR_LAYER_SIDE,
    PRINT_BASE_DPI,
    QR_BORDER_MODULES,
    ROUNDED_QR_LAYER_SUPERSAMPLE,
)
from qr_preset_studio.infrastructure.rendering.drawers import (
    draw_eye_ball,
    draw_eye_frame,
)
from qr_preset_studio.infrastructure.rendering.geometry import QrLayout, active_rect, build_qr_layout
from qr_preset_studio.infrastructure.rendering.qr_matrix import (
    active_module_count,
    build_matrix,
    finder_origins,
    in_finder_area,
)


def render_preset(preset: Preset, qr_layer_scale: float | None = None) -> Image.Image:
    canvas = build_canvas(preset)
    if preset.hide_qr or not preset.link.strip():
        return canvas

    matrix = build_matrix(preset)
    matrix_size = len(matrix)
    active_modules = active_module_count(matrix_size)
    layout = build_qr_layout(preset, active_modules)
    origins = finder_origins(active_modules)
    body_map = _build_body_map(matrix, matrix_size, origins)

    _render_qr_layer(
        canvas,
        preset,
        layout,
        body_map,
        origins,
        qr_layer_scale=_normalize_qr_layer_scale(preset, qr_layer_scale),
    )
    return canvas


def render_export_preset(preset: Preset) -> Image.Image:
    export_scale = _export_canvas_scale(preset)
    export_preset = preset if abs(export_scale - 1.0) < 1e-9 else preset.scaled_copy(export_scale)

    image = render_preset(export_preset)
    effective_dpi = int(round(PRINT_BASE_DPI * export_scale))
    image.info["dpi"] = (effective_dpi, effective_dpi)
    return image


def _render_qr_layer(
    canvas: Image.Image,
    preset: Preset,
    layout: QrLayout,
    body_map: list[list[bool]],
    origins,
    qr_layer_scale: float,
) -> None:
    card_left, card_top, card_right, card_bottom = layout.card_rect
    card_width = max(1, card_right - card_left)
    card_height = max(1, card_bottom - card_top)

    render_scale = _qr_render_scale(qr_layer_scale, card_width, card_height)
    layer_size = (
        max(1, int(round(card_width * render_scale))),
        max(1, int(round(card_height * render_scale))),
    )
    layer = Image.new("RGBA", layer_size, (0, 0, 0, 0))

    local_layout = QrLayout(
        active_x=max(0, int(round((layout.active_x - card_left) * render_scale))),
        active_y=max(0, int(round((layout.active_y - card_top) * render_scale))),
        active_qr_size=max(1, int(round(layout.active_qr_size * render_scale))),
        active_modules=layout.active_modules,
        padding=max(0, int(round(layout.padding * render_scale))),
        border_width=max(0, int(round(layout.border_width * render_scale))),
        corner_radius=max(0, int(round(layout.corner_radius * render_scale))),
    )

    _draw_card(layer, preset, local_layout)
    render_body(layer, preset, local_layout, body_map, render_scale=render_scale)
    _draw_finders(layer, preset, local_layout, origins)

    if layer.size != (card_width, card_height):
        layer = layer.resize((card_width, card_height), Image.Resampling.LANCZOS)

    visible_layer, dest = _visible_layer(layer, canvas.size, (card_left, card_top))
    if visible_layer is not None:
        canvas.alpha_composite(visible_layer, dest)


def _draw_card(canvas: Image.Image, preset: Preset, layout: QrLayout) -> None:
    if not preset.qr_background_enabled:
        return

    ImageDraw.Draw(canvas).rounded_rectangle(
        layout.card_rect,
        radius=layout.corner_radius,
        fill=preset.qr_background_color,
        outline=preset.qr_border_color if layout.border_width > 0 else None,
        width=layout.border_width,
    )


def _build_body_map(matrix, matrix_size: int, origins) -> list[list[bool]]:
    body_map: list[list[bool]] = []

    for row, line in enumerate(matrix):
        if row < QR_BORDER_MODULES or row >= matrix_size - QR_BORDER_MODULES:
            continue

        active_row = row - QR_BORDER_MODULES
        body_row: list[bool] = []

        for col, is_dark in enumerate(line):
            if col < QR_BORDER_MODULES or col >= matrix_size - QR_BORDER_MODULES:
                continue

            active_col = col - QR_BORDER_MODULES
            body_row.append(bool(is_dark and not in_finder_area(active_row, active_col, origins)))

        body_map.append(body_row)

    return body_map


def _draw_finders(canvas: Image.Image, preset: Preset, layout: QrLayout, origins) -> None:
    draw = ImageDraw.Draw(canvas)
    for origin_col, origin_row in origins:
        finder_position = _finder_position(origin_col, origin_row, layout.active_modules)

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
            layout.active_qr_size,
            preset,
        )
        draw_eye_frame(
            draw,
            frame_rect,
            layout.module_thickness,
            preset.eye_frame_shape,
            frame_color,
            finder_position,
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
            layout.active_qr_size,
            preset,
        )
        draw_eye_ball(
            draw,
            ball_rect,
            preset.eye_ball_shape,
            ball_color,
            finder_position,
        )


def _finder_position(origin_col: int, origin_row: int, active_modules: int) -> str:
    last_origin = active_modules - FINDER_SIZE
    if origin_row == 0 and origin_col == 0:
        return "top_left"
    if origin_row == 0 and origin_col == last_origin:
        return "top_right"
    if origin_row == last_origin and origin_col == 0:
        return "bottom_left"
    return "bottom_right"


def _qr_render_scale(requested_scale: float, card_width: int, card_height: int) -> float:
    requested_scale = max(1.0, float(requested_scale))
    max_card_side = max(1, card_width, card_height)
    memory_cap_scale = max(1.0, MAX_QR_LAYER_SIDE / max_card_side)
    return max(1.0, min(requested_scale, memory_cap_scale))


def _normalize_qr_layer_scale(preset: Preset, qr_layer_scale: float | None) -> float:
    if qr_layer_scale is not None:
        return max(1.0, float(qr_layer_scale))

    if preset.body_shape != "square":
        return ROUNDED_QR_LAYER_SUPERSAMPLE
    if preset.eye_frame_shape != "square":
        return ROUNDED_QR_LAYER_SUPERSAMPLE
    if preset.eye_ball_shape != "square":
        return ROUNDED_QR_LAYER_SUPERSAMPLE
    return 1.0


def _export_canvas_scale(preset: Preset) -> float:
    target_dpi = max(PRINT_BASE_DPI, preset.qr_dpi)
    requested_scale = target_dpi / PRINT_BASE_DPI

    max_width_scale = MAX_EXPORT_SIDE / max(1, preset.canvas_width)
    max_height_scale = MAX_EXPORT_SIDE / max(1, preset.canvas_height)
    max_export_scale = max(1.0, min(max_width_scale, max_height_scale))

    return max(1.0, min(requested_scale, max_export_scale))


def _visible_layer(
    layer: Image.Image,
    canvas_size: tuple[int, int],
    dest: tuple[int, int],
) -> tuple[Image.Image | None, tuple[int, int]]:
    dest_x, dest_y = dest
    layer_width, layer_height = layer.size

    visible_left = max(0, dest_x)
    visible_top = max(0, dest_y)
    visible_right = min(canvas_size[0], dest_x + layer_width)
    visible_bottom = min(canvas_size[1], dest_y + layer_height)

    if visible_left >= visible_right or visible_top >= visible_bottom:
        return None, (0, 0)

    crop_box = (
        visible_left - dest_x,
        visible_top - dest_y,
        visible_right - dest_x,
        visible_bottom - dest_y,
    )
    return layer.crop(crop_box), (visible_left, visible_top)
