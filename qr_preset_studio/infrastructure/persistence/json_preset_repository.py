from __future__ import annotations

import json
from pathlib import Path

from qr_preset_studio.domain.models.preset import Preset


class JsonPresetRepository:
    def save(self, path: str | Path, preset: Preset) -> None:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(preset.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")

    def load(self, path: str | Path) -> Preset:
        source = Path(path)
        raw = json.loads(source.read_text(encoding="utf-8"))
        return Preset.from_dict(raw)
