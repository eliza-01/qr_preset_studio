# qr_preset_studio/application/services/render_service.py
from __future__ import annotations

import colorsys
from pathlib import Path

from PIL import Image, ImageCms

from qr_preset_studio.domain.models.output_profile import OutputProfile
from qr_preset_studio.domain.models.preset import Preset
from qr_preset_studio.infrastructure.rendering.composer import render_export_preset
from qr_preset_studio.infrastructure.rendering.preview import render_preview


class RenderService:
    def render_preview(self, preset: Preset, zoom_percent: int) -> Image.Image:
        return render_preview(preset, zoom_percent)

    def render_export(self, preset: Preset) -> Image.Image:
        return render_export_preset(preset)

    def save_rendered_image(self, image: Image.Image, path: str | Path, profile: OutputProfile) -> None:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)

        dpi = (profile.dpi, profile.dpi)
        if profile.file_format.upper() == "PNG":
            png_image = _ensure_png_mode(image)
            png_image.save(target, format="PNG", dpi=dpi)
            return

        if profile.file_format.upper() == "JPEG":
            jpeg_image, icc_bytes = _ensure_jpeg_mode(image, profile)
            save_kwargs = {
                "format": "JPEG",
                "dpi": dpi,
                "quality": profile.jpeg_quality,
                "subsampling": 0,
            }
            if icc_bytes is not None:
                save_kwargs["icc_profile"] = icc_bytes
            jpeg_image.save(target, **save_kwargs)
            return

        raise ValueError(f"Неподдерживаемый формат экспорта: {profile.file_format}")


def _ensure_png_mode(image: Image.Image) -> Image.Image:
    if image.mode in {"RGBA", "RGB"}:
        return image
    return image.convert("RGBA")


def _ensure_jpeg_mode(image: Image.Image, profile: OutputProfile) -> tuple[Image.Image, bytes | None]:
    flattened = _flatten_alpha(image)
    if profile.color_mode.upper() == "CMYK":
        return _ensure_cmyk_jpeg_mode(flattened, profile)
    rgb_image = flattened.convert("RGB")
    if profile.compensation_mode == "prepress_vivid_pink_blue":
        rgb_image = _apply_prepress_compensation(rgb_image)
    return rgb_image, None


def _ensure_cmyk_jpeg_mode(image: Image.Image, profile: OutputProfile) -> tuple[Image.Image, bytes | None]:
    icc_path = _resolve_cmyk_icc_path(profile)
    flattened_rgb = image.convert("RGB")
    if icc_path is None or not icc_path.is_file():
        return _rgb_to_cmyk_fallback(flattened_rgb), None

    srgb_profile = ImageCms.createProfile("sRGB")
    cmyk_profile = ImageCms.getOpenProfile(str(icc_path))
    converted = ImageCms.profileToProfile(
        flattened_rgb,
        srgb_profile,
        cmyk_profile,
        outputMode="CMYK",
    )
    return converted, icc_path.read_bytes()


def _resolve_cmyk_icc_path(profile: OutputProfile) -> Path | None:
    candidates: list[Path] = []
    if profile.icc_profile_path is not None:
        candidates.append(profile.icc_profile_path.expanduser())

    env_override = (Path.home() / "QRPresetStudio" / "color_profiles")
    candidates.extend(
        [
            env_override / "CMYK.icc",
            env_override / "CMYK.icm",
            env_override / "USWebCoatedSWOP.icc",
            env_override / "USWebCoatedSWOP.icm",
        ]
    )

    seen: set[Path] = set()
    for path in candidates:
        normalized = path.expanduser()
        if normalized in seen:
            continue
        seen.add(normalized)
        if normalized.is_file():
            return normalized
    return profile.icc_profile_path.expanduser() if profile.icc_profile_path is not None else None


def _flatten_alpha(image: Image.Image) -> Image.Image:
    if image.mode in {"RGBA", "LA"}:
        background = Image.new("RGBA", image.size, (255, 255, 255, 255))
        background.alpha_composite(image.convert("RGBA"))
        return background.convert("RGB")
    if image.mode == "P":
        return _flatten_alpha(image.convert("RGBA"))
    if image.mode == "RGB":
        return image
    return image.convert("RGB")


def _rgb_to_cmyk_fallback(image: Image.Image) -> Image.Image:
    width, height = image.size
    src = image.load()
    converted = Image.new("CMYK", image.size)
    dst = converted.load()

    for y in range(height):
        for x in range(width):
            red, green, blue = src[x, y]
            dst[x, y] = _rgb_pixel_to_cmyk(red, green, blue)

    return converted


def _rgb_pixel_to_cmyk(red: int, green: int, blue: int) -> tuple[int, int, int, int]:
    rn = red / 255.0
    gn = green / 255.0
    bn = blue / 255.0

    key = 1.0 - max(rn, gn, bn)
    if key >= 1.0:
        return (0, 0, 0, 255)

    denom = max(1e-9, 1.0 - key)
    cyan = (1.0 - rn - key) / denom
    magenta = (1.0 - gn - key) / denom
    yellow = (1.0 - bn - key) / denom

    cyan = _clamp_unit(cyan)
    magenta = _clamp_unit(magenta)
    yellow = _clamp_unit(yellow)
    key = _clamp_unit(key)

    # Move shared CMY density into K to keep neutrals and dark tones cleaner.
    shared = min(cyan, magenta, yellow)
    move_to_key = min(shared * 0.65, 1.0 - key)
    cyan -= move_to_key
    magenta -= move_to_key
    yellow -= move_to_key
    key += move_to_key

    return (
        _unit_to_byte(cyan),
        _unit_to_byte(magenta),
        _unit_to_byte(yellow),
        _unit_to_byte(key),
    )


def _clamp_unit(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def _unit_to_byte(value: float) -> int:
    return max(0, min(255, int(round(_clamp_unit(value) * 255.0))))


def _apply_prepress_compensation(image: Image.Image) -> Image.Image:
    width, height = image.size
    src = image.load()
    compensated = Image.new("RGB", image.size)
    dst = compensated.load()

    for y in range(height):
        for x in range(width):
            dst[x, y] = _compensate_rgb_pixel(*src[x, y])

    return compensated


def _compensate_rgb_pixel(red: int, green: int, blue: int) -> tuple[int, int, int]:
    rn = red / 255.0
    gn = green / 255.0
    bn = blue / 255.0
    hue, saturation, value = colorsys.rgb_to_hsv(rn, gn, bn)

    if value <= 0.03:
        return red, green, blue

    if saturation <= 0.08:
        # Keep neutrals stable; only a tiny lift for bright near-whites.
        if value >= 0.8:
            value = min(1.0, value * 1.01)
        return _hsv_to_rgb_bytes(hue, saturation, value)

    # Push cyan -> magenta hues a bit harder to survive CMYK conversion.
    if 0.50 <= hue <= 0.92:
        hue_shift = 0.0
        sat_gain = 1.18
        val_gain = 1.04

        if 0.58 <= hue <= 0.72:
            sat_gain = 1.24
            val_gain = 1.06
            hue_shift = -0.008
        elif 0.72 < hue <= 0.92:
            sat_gain = 1.20
            val_gain = 1.05
            hue_shift = 0.006

        saturation = min(1.0, saturation * sat_gain)
        value = min(1.0, value * val_gain)
        hue = (hue + hue_shift) % 1.0

        # Add a small channel bias to preserve vivid pink/blue edges.
        rr, gg, bb = _hsv_to_rgb_bytes(hue, saturation, value)
        if bb >= rr:
            bb = min(255, int(round(bb * 1.04)))
        if rr >= bb or hue >= 0.78:
            rr = min(255, int(round(rr * 1.03)))
        gg = max(0, min(255, int(round(gg * 0.985))))
        return rr, gg, bb

    return red, green, blue


def _hsv_to_rgb_bytes(hue: float, saturation: float, value: float) -> tuple[int, int, int]:
    red, green, blue = colorsys.hsv_to_rgb(
        _clamp_unit(hue),
        _clamp_unit(saturation),
        _clamp_unit(value),
    )
    return (
        _unit_to_byte(red),
        _unit_to_byte(green),
        _unit_to_byte(blue),
    )
