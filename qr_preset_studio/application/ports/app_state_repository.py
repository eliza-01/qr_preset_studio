# qr_preset_studio/application/ports/app_state_repository.py
from __future__ import annotations

from pathlib import Path
from typing import Protocol

from qr_preset_studio.domain.models.app_state import AppState


class AppStateRepository(Protocol):
    def save(self, path: str | Path, state: AppState) -> None: ...

    def load(self, path: str | Path) -> AppState: ...
