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
    finder_position: str,
) -> None:
    if shape == "square":
        draw.rectangle(rect, outline=color, width=module_thickness)
        return

    radius_factor = 0.16 if shape == "rounded" else 0.28
    _draw_styled_rect(
        draw=draw,
        rect=rect,
        corners=_shape_corners(shape, finder_position),
        radius_factor=radius_factor,
        outline=color,
        width=module_thickness,
    )


def draw_eye_ball(
    draw: ImageDraw.ImageDraw,
    rect: tuple[int, int, int, int],
    shape: str,
    color: tuple[int, int, int],
    finder_position: str,
) -> None:
    if shape == "circle":
        draw.ellipse(rect, fill=color)
        return

    if shape == "square":
        draw.rectangle(rect, fill=color)
        return

    radius_factor = 0.3 if shape == "rounded" else 0.36
    _draw_styled_rect(
        draw=draw,
        rect=rect,
        corners=_shape_corners(shape, finder_position),
        radius_factor=radius_factor,
        fill=color,
    )


def _draw_styled_rect(
    *,
    draw: ImageDraw.ImageDraw,
    rect: tuple[int, int, int, int],
    corners: tuple[bool, bool, bool, bool] | None,
    radius_factor: float,
    fill: tuple[int, int, int] | None = None,
    outline: tuple[int, int, int] | None = None,
    width: int = 1,
) -> None:
    if corners is None:
        if fill is not None and outline is not None:
            draw.rectangle(rect, fill=fill, outline=outline, width=width)
            return
        if fill is not None:
            draw.rectangle(rect, fill=fill)
            return
        draw.rectangle(rect, outline=outline, width=width)
        return

    radius = max(1, int(min(rect[2] - rect[0], rect[3] - rect[1]) * radius_factor))
    draw.rounded_rectangle(
        rect,
        radius=radius,
        fill=fill,
        outline=outline,
        width=width,
        corners=corners,
    )


def _shape_corners(shape: str, finder_position: str) -> tuple[bool, bool, bool, bool] | None:
    if shape == "rounded":
        return True, True, True, True

    if shape == "classy_rounded":
        return _classy_rounded_corners(finder_position)

    if shape == "classy":
        return _classy_corners(finder_position)

    return None


def _classy_rounded_corners(finder_position: str) -> tuple[bool, bool, bool, bool]:
    mapping = {
        "top_left": (True, True, False, True),
        "top_right": (True, True, True, False),
        "bottom_left": (True, False, True, True),
        "bottom_right": (False, True, True, True),
    }
    return mapping.get(finder_position, mapping["top_left"])


def _classy_corners(finder_position: str) -> tuple[bool, bool, bool, bool]:
    mapping = {
        "top_left": (False, True, False, True),
        "top_right": (True, False, True, False),
        "bottom_left": (True, False, True, False),
        "bottom_right": (False, True, False, True),
    }
    return mapping.get(finder_position, mapping["top_left"])