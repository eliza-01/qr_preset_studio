from __future__ import annotations

from PIL import ImageDraw


def draw_body_module(
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


def draw_eye_frame(
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


def draw_eye_ball(
    draw: ImageDraw.ImageDraw,
    rect: tuple[int, int, int, int],
    shape: str,
    color: tuple[int, int, int],
) -> None:
    if shape == "circle":
        draw.ellipse(rect, fill=color)
        return
    draw.rectangle(rect, fill=color)
