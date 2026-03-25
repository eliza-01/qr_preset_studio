from __future__ import annotations

from dataclasses import asdict, dataclass, field, fields
from typing import Any

from qr_preset_studio.domain.constants import (
    BODY_SHAPES,
    EYE_BALL_SHAPES,
    EYE_FRAME_SHAPES,
    GRADIENT_DIRECTIONS,
    QR_ERROR_CORRECTION_LEVELS,
)


@dataclass(slots=True)
class Preset:
    link: str = ""
    canvas_width: int = 1200
    canvas_height: int = 1200
    canvas_background_color: str = "#F3F4F6"
    background_image_path: str = ""

    qr_scale_percent: int = 42
    qr_offset_x: int = 0
    qr_offset_y: int = 0
    qr_version: int = 3
    qr_error_correction: str = "M"
    qr_mask_pattern: int = 6
    qr_optimize: int = 20
    qr_dpi: int = 300

    body_shape: str = "square"
    rounded_body_radius_px: int = 8
    spikes_single_corner_radius_px: int = 8

    claw_detail_scale: int = 6
    claw_curve_steps: int = 40
    claw_alternate_direction: bool = True
    claw_lean_right: bool = True
    claw_tip_x: float = 0.86
    claw_tip_y: float = 0.06
    claw_outer_ctrl1_x: float = 0.00
    claw_outer_ctrl1_y: float = 0.52
    claw_outer_ctrl2_x: float = 0.10
    claw_outer_ctrl2_y: float = 0.10
    claw_inner_ctrl1_x: float = 1.00
    claw_inner_ctrl1_y: float = 0.08
    claw_inner_ctrl2_x: float = 0.82
    claw_inner_ctrl2_y: float = 0.70

    eye_frame_shape: str = "square"
    eye_ball_shape: str = "square"

    qr_foreground_color: str = "#0F172A"
    gradient_enabled: bool = False
    gradient_color: str = "#2563EB"
    gradient_direction: str = "horizontal"
    gradient_offset_horizontal_px: int = 0
    gradient_offset_vertical_px: int = 0
    gradient_offset_diagonal_down_px: int = 0
    gradient_offset_diagonal_up_px: int = 0

    qr_background_enabled: bool = True
    qr_background_color: str = "#FFFFFF"
    qr_background_padding: int = 32
    qr_background_radius: int = 24
    qr_border_width: int = 4
    qr_border_color: str = "#CBD5E1"

    locked_fields: dict[str, bool] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "Preset":
        allowed = {field.name for field in fields(cls)}
        data = {key: value for key, value in raw.items() if key in allowed}

        if "rounded_body_radius_px" not in data:
            data["rounded_body_radius_px"] = _legacy_body_radius(raw.get("rounded_body_strength_percent"))

        data["locked_fields"] = _normalize_locked_fields(raw.get("locked_fields"))

        preset = cls(**data)
        preset.body_shape = _safe_choice(preset.body_shape, BODY_SHAPES)
        preset.eye_frame_shape = _safe_choice(preset.eye_frame_shape, EYE_FRAME_SHAPES)
        preset.eye_ball_shape = _safe_choice(preset.eye_ball_shape, EYE_BALL_SHAPES)
        preset.gradient_direction = _safe_choice(preset.gradient_direction, GRADIENT_DIRECTIONS)
        preset.qr_error_correction = _safe_choice(preset.qr_error_correction, QR_ERROR_CORRECTION_LEVELS)

        preset.canvas_width = _clamp_int(preset.canvas_width, 256, 8000, 1200)
        preset.canvas_height = _clamp_int(preset.canvas_height, 256, 8000, 1200)
        preset.qr_scale_percent = _clamp_int(preset.qr_scale_percent, 10, 90, 42)
        preset.qr_offset_x = _clamp_int(preset.qr_offset_x, -5000, 5000, 0)
        preset.qr_offset_y = _clamp_int(preset.qr_offset_y, -5000, 5000, 0)
        preset.qr_version = _clamp_int(preset.qr_version, 0, 40, 0)
        preset.qr_mask_pattern = _clamp_int(preset.qr_mask_pattern, -1, 7, -1)
        preset.qr_optimize = _clamp_int(preset.qr_optimize, 0, 100, 20)
        preset.qr_dpi = _clamp_int(preset.qr_dpi, 72, 2400, 300)

        preset.rounded_body_radius_px = _clamp_int(preset.rounded_body_radius_px, 0, 200, 8)
        preset.spikes_single_corner_radius_px = _clamp_int(preset.spikes_single_corner_radius_px, 0, 200, 8)

        preset.claw_detail_scale = _clamp_int(preset.claw_detail_scale, 1, 32, 6)
        preset.claw_curve_steps = _clamp_int(preset.claw_curve_steps, 4, 200, 40)
        preset.claw_alternate_direction = _coerce_bool(preset.claw_alternate_direction, True)
        preset.claw_lean_right = _coerce_bool(preset.claw_lean_right, True)
        preset.claw_tip_x = _clamp_float(preset.claw_tip_x, -2.0, 2.0, 0.86)
        preset.claw_tip_y = _clamp_float(preset.claw_tip_y, -2.0, 2.0, 0.06)
        preset.claw_outer_ctrl1_x = _clamp_float(preset.claw_outer_ctrl1_x, -2.0, 2.0, 0.00)
        preset.claw_outer_ctrl1_y = _clamp_float(preset.claw_outer_ctrl1_y, -2.0, 2.0, 0.52)
        preset.claw_outer_ctrl2_x = _clamp_float(preset.claw_outer_ctrl2_x, -2.0, 2.0, 0.10)
        preset.claw_outer_ctrl2_y = _clamp_float(preset.claw_outer_ctrl2_y, -2.0, 2.0, 0.10)
        preset.claw_inner_ctrl1_x = _clamp_float(preset.claw_inner_ctrl1_x, -2.0, 2.0, 1.00)
        preset.claw_inner_ctrl1_y = _clamp_float(preset.claw_inner_ctrl1_y, -2.0, 2.0, 0.08)
        preset.claw_inner_ctrl2_x = _clamp_float(preset.claw_inner_ctrl2_x, -2.0, 2.0, 0.82)
        preset.claw_inner_ctrl2_y = _clamp_float(preset.claw_inner_ctrl2_y, -2.0, 2.0, 0.70)

        preset.gradient_offset_horizontal_px = _clamp_int(preset.gradient_offset_horizontal_px, -5000, 5000, 0)
        preset.gradient_offset_vertical_px = _clamp_int(preset.gradient_offset_vertical_px, -5000, 5000, 0)
        preset.gradient_offset_diagonal_down_px = _clamp_int(
            preset.gradient_offset_diagonal_down_px,
            -5000,
            5000,
            0,
        )
        preset.gradient_offset_diagonal_up_px = _clamp_int(
            preset.gradient_offset_diagonal_up_px,
            -5000,
            5000,
            0,
        )

        preset.qr_background_padding = _clamp_int(preset.qr_background_padding, 0, 500, 32)
        preset.qr_background_radius = _clamp_int(preset.qr_background_radius, 0, 200, 24)
        preset.qr_border_width = _clamp_int(preset.qr_border_width, 0, 50, 4)
        return preset

    def scaled_copy(self, factor: float) -> "Preset":
        factor = max(0.01, factor)
        return Preset(
            link=self.link,
            canvas_width=max(1, int(round(self.canvas_width * factor))),
            canvas_height=max(1, int(round(self.canvas_height * factor))),
            canvas_background_color=self.canvas_background_color,
            background_image_path=self.background_image_path,
            qr_scale_percent=self.qr_scale_percent,
            qr_offset_x=int(round(self.qr_offset_x * factor)),
            qr_offset_y=int(round(self.qr_offset_y * factor)),
            qr_version=self.qr_version,
            qr_error_correction=self.qr_error_correction,
            qr_mask_pattern=self.qr_mask_pattern,
            qr_optimize=self.qr_optimize,
            qr_dpi=self.qr_dpi,
            body_shape=self.body_shape,
            rounded_body_radius_px=max(0, int(round(self.rounded_body_radius_px * factor))),
            spikes_single_corner_radius_px=max(0, int(round(self.spikes_single_corner_radius_px * factor))),
            claw_detail_scale=self.claw_detail_scale,
            claw_curve_steps=self.claw_curve_steps,
            claw_alternate_direction=self.claw_alternate_direction,
            claw_lean_right=self.claw_lean_right,
            claw_tip_x=self.claw_tip_x,
            claw_tip_y=self.claw_tip_y,
            claw_outer_ctrl1_x=self.claw_outer_ctrl1_x,
            claw_outer_ctrl1_y=self.claw_outer_ctrl1_y,
            claw_outer_ctrl2_x=self.claw_outer_ctrl2_x,
            claw_outer_ctrl2_y=self.claw_outer_ctrl2_y,
            claw_inner_ctrl1_x=self.claw_inner_ctrl1_x,
            claw_inner_ctrl1_y=self.claw_inner_ctrl1_y,
            claw_inner_ctrl2_x=self.claw_inner_ctrl2_x,
            claw_inner_ctrl2_y=self.claw_inner_ctrl2_y,
            eye_frame_shape=self.eye_frame_shape,
            eye_ball_shape=self.eye_ball_shape,
            qr_foreground_color=self.qr_foreground_color,
            gradient_enabled=self.gradient_enabled,
            gradient_color=self.gradient_color,
            gradient_direction=self.gradient_direction,
            gradient_offset_horizontal_px=int(round(self.gradient_offset_horizontal_px * factor)),
            gradient_offset_vertical_px=int(round(self.gradient_offset_vertical_px * factor)),
            gradient_offset_diagonal_down_px=int(round(self.gradient_offset_diagonal_down_px * factor)),
            gradient_offset_diagonal_up_px=int(round(self.gradient_offset_diagonal_up_px * factor)),
            qr_background_enabled=self.qr_background_enabled,
            qr_background_color=self.qr_background_color,
            qr_background_padding=max(0, int(round(self.qr_background_padding * factor))),
            qr_background_radius=max(0, int(round(self.qr_background_radius * factor))),
            qr_border_width=max(0, int(round(self.qr_border_width * factor))),
            qr_border_color=self.qr_border_color,
            locked_fields=dict(self.locked_fields),
        )


def _safe_choice(value: str, allowed: list[str]) -> str:
    return value if value in allowed else allowed[0]


def _clamp_int(value: Any, minimum: int, maximum: int, fallback: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return fallback
    return max(minimum, min(maximum, parsed))


def _clamp_float(value: Any, minimum: float, maximum: float, fallback: float) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return fallback
    return max(minimum, min(maximum, parsed))


def _coerce_bool(value: Any, fallback: bool) -> bool:
    if isinstance(value, bool):
        return value

    if isinstance(value, (int, float)):
        return value != 0

    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"true", "1", "yes", "on"}:
            return True
        if lowered in {"false", "0", "no", "off"}:
            return False

    return fallback


def _legacy_body_radius(value: Any) -> int:
    strength = _clamp_int(value, 10, 100, 80)
    return max(1, min(24, int(round(strength / 10))))


def _normalize_locked_fields(value: Any) -> dict[str, bool]:
    if not isinstance(value, dict):
        return {}

    normalized: dict[str, bool] = {}
    for key, raw_value in value.items():
        if not isinstance(key, str):
            continue

        if isinstance(raw_value, bool):
            normalized[key] = raw_value
            continue

        if isinstance(raw_value, (int, float)):
            normalized[key] = raw_value != 0
            continue

        if isinstance(raw_value, str):
            lowered = raw_value.strip().lower()
            if lowered in {"true", "1"}:
                normalized[key] = True
                continue
            if lowered in {"false", "0"}:
                normalized[key] = False
                continue

    return normalized