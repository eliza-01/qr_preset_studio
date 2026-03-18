# qr_preset_studio/core/models.py
from __future__ import annotations

from dataclasses import asdict, dataclass, fields
from typing import Any

BODY_SHAPES = ["square", "rounded"]
EYE_FRAME_SHAPES = ["square", "rounded"]
EYE_BALL_SHAPES = ["square", "circle"]
GRADIENT_DIRECTIONS = ["horizontal", "vertical", "diagonal_down", "diagonal_up"]


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

    body_shape: str = "square"
    eye_frame_shape: str = "square"
    eye_ball_shape: str = "square"

    qr_foreground_color: str = "#0F172A"
    gradient_enabled: bool = False
    gradient_color: str = "#2563EB"
    gradient_direction: str = "horizontal"

    qr_background_enabled: bool = True
    qr_background_color: str = "#FFFFFF"
    qr_background_padding: int = 32
    qr_background_radius: int = 24
    qr_border_width: int = 4
    qr_border_color: str = "#CBD5E1"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "Preset":
        allowed = {field.name for field in fields(cls)}
        data = {key: value for key, value in raw.items() if key in allowed}
        preset = cls(**data)
        if preset.body_shape not in BODY_SHAPES:
            preset.body_shape = BODY_SHAPES[0]
        if preset.eye_frame_shape not in EYE_FRAME_SHAPES:
            preset.eye_frame_shape = EYE_FRAME_SHAPES[0]
        if preset.eye_ball_shape not in EYE_BALL_SHAPES:
            preset.eye_ball_shape = EYE_BALL_SHAPES[0]
        if preset.gradient_direction not in GRADIENT_DIRECTIONS:
            preset.gradient_direction = GRADIENT_DIRECTIONS[0]
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
            body_shape=self.body_shape,
            eye_frame_shape=self.eye_frame_shape,
            eye_ball_shape=self.eye_ball_shape,
            qr_foreground_color=self.qr_foreground_color,
            gradient_enabled=self.gradient_enabled,
            gradient_color=self.gradient_color,
            gradient_direction=self.gradient_direction,
            qr_background_enabled=self.qr_background_enabled,
            qr_background_color=self.qr_background_color,
            qr_background_padding=max(0, int(round(self.qr_background_padding * factor))),
            qr_background_radius=max(0, int(round(self.qr_background_radius * factor))),
            qr_border_width=max(0, int(round(self.qr_border_width * factor))),
            qr_border_color=self.qr_border_color,
        )
