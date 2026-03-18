from __future__ import annotations

from pathlib import Path

from qr_preset_studio.application.ports.preset_repository import PresetRepository
from qr_preset_studio.domain.models.preset import Preset


class PresetService:
    def __init__(self, repository: PresetRepository, presets_dir: Path) -> None:
        self._repository = repository
        self._presets_dir = presets_dir

    @property
    def presets_dir(self) -> Path:
        return self._presets_dir

    def save(self, path: str | Path, preset: Preset) -> None:
        self._repository.save(path, preset)

    def load(self, path: str | Path) -> Preset:
        return self._repository.load(path)
