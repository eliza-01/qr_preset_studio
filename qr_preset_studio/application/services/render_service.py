from __future__ import annotations

from PIL import Image

from qr_preset_studio.domain.models.preset import Preset
from qr_preset_studio.infrastructure.rendering.composer import render_preset
from qr_preset_studio.infrastructure.rendering.preview import render_preview


class RenderService:
    def render_preview(self, preset: Preset, zoom_percent: int) -> Image.Image:
        return render_preview(preset, zoom_percent)

    def render_export(self, preset: Preset) -> Image.Image:
        return render_preset(preset)
