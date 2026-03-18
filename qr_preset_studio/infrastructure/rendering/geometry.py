from __future__ import annotations

from dataclasses import dataclass

from qr_preset_studio.domain.models.preset import Preset


@dataclass(slots=True)
class QrLayout:
    active_x: int
    active_y: int
    active_qr_size: int
    active_modules: int
    padding: int
    border_width: int
    corner_radius: int

    @property
    def card_rect(self) -> tuple[int, int, int, int]:
        return (
            self.active_x - self.padding - self.border_width,
            self.active_y - self.padding - self.border_width,
            self.active_x + self.active_qr_size + self.padding + self.border_width,
            self.active_y + self.active_qr_size + self.padding + self.border_width,
        )

    @property
    def module_thickness(self) -> int:
        return max(1, int(round(self.active_qr_size / max(1, self.active_modules))))


def build_qr_layout(preset: Preset, active_modules: int) -> QrLayout:
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

    return QrLayout(
        active_x=active_x,
        active_y=active_y,
        active_qr_size=active_qr_size,
        active_modules=active_modules,
        padding=padding,
        border_width=border_width,
        corner_radius=corner_radius,
    )


def grid_edge(origin: int, index: int | float, active_modules: int, active_qr_size: int) -> int:
    return origin + int(round((index * active_qr_size) / max(1, active_modules)))


def active_rect(
    *,
    active_x: int,
    active_y: int,
    active_col: int,
    active_row: int,
    span: int,
    active_modules: int,
    active_qr_size: int,
) -> tuple[int, int, int, int]:
    left = grid_edge(active_x, active_col, active_modules, active_qr_size)
    top = grid_edge(active_y, active_row, active_modules, active_qr_size)
    right = grid_edge(active_x, active_col + span, active_modules, active_qr_size)
    bottom = grid_edge(active_y, active_row + span, active_modules, active_qr_size)

    if right <= left:
        right = left + 1
    if bottom <= top:
        bottom = top + 1

    return left, top, right, bottom
