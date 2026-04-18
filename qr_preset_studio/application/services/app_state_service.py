# qr_preset_studio/application/services/app_state_service.py
from __future__ import annotations

from pathlib import Path

from qr_preset_studio.application.ports.app_state_repository import AppStateRepository
from qr_preset_studio.domain.models.app_state import AppState


class AppStateService:
    def __init__(self, repository: AppStateRepository, state_file: Path) -> None:
        self._repository = repository
        self._state_file = state_file

    def last_preset_path(self) -> Path | None:
        raw_path = self._load().last_preset_path.strip()
        if not raw_path:
            return None
        return Path(raw_path).expanduser()

    def set_last_preset_path(self, path: str | Path) -> None:
        state = self._load()
        state.last_preset_path = str(Path(path).expanduser())
        self._save(state)

    def clear_last_preset_path(self) -> None:
        state = self._load()
        state.last_preset_path = ""
        self._save(state)

    def output_profile_id(self) -> str:
        return self._load().output_profile_id.strip()

    def set_output_profile_id(self, profile_id: str) -> None:
        state = self._load()
        state.output_profile_id = (profile_id or "").strip()
        self._save(state)

    def _load(self) -> AppState:
        return self._repository.load(self._state_file)

    def _save(self, state: AppState) -> None:
        self._repository.save(self._state_file, state)
