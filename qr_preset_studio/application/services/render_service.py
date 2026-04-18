# qr_preset_studio/application/services/render_service.py
from __future__ import annotations

from pathlib import Path

from PIL import Image

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
    return flattened.convert("RGB"), None


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
