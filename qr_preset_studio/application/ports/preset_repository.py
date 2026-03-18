from __future__ import annotations

from pathlib import Path
from typing import Protocol

from qr_preset_studio.domain.models.preset import Preset


class PresetRepository(Protocol):
    def save(self, path: str | Path, preset: Preset) -> None: ...

    def load(self, path: str | Path) -> Preset: ...
