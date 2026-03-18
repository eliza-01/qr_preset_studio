# qr_preset_studio/core/preset_store.py
from __future__ import annotations

import json
from pathlib import Path

from .models import Preset


def save_preset(path: str | Path, preset: Preset) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(preset.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")


def load_preset(path: str | Path) -> Preset:
    source = Path(path)
    raw = json.loads(source.read_text(encoding="utf-8"))
    return Preset.from_dict(raw)
