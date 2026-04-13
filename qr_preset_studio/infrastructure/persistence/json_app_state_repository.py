# qr_preset_studio/infrastructure/persistence/json_app_state_repository.py
from __future__ import annotations

import json
from pathlib import Path

from qr_preset_studio.domain.models.app_state import AppState


class JsonAppStateRepository:
    def save(self, path: str | Path, state: AppState) -> None:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(state.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")

    def load(self, path: str | Path) -> AppState:
        source = Path(path)
        if not source.is_file():
            return AppState()

        try:
            raw = json.loads(source.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return AppState()

        if not isinstance(raw, dict):
            return AppState()

        return AppState.from_dict(raw)
