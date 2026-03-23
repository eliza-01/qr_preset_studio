from __future__ import annotations

from pathlib import Path

from qr_preset_studio.application.ports.app_state_repository import AppStateRepository
from qr_preset_studio.domain.models.app_state import AppState


class AppStateService:
    def __init__(self, repository: AppStateRepository, state_file: Path) -> None:
        self._repository = repository
        self._state_file = state_file

    def last_preset_path(self) -> Path | None:
        raw_path = self._repository.load(self._state_file).last_preset_path.strip()
        if not raw_path:
            return None
        return Path(raw_path).expanduser()

    def set_last_preset_path(self, path: str | Path) -> None:
        normalized = str(Path(path).expanduser())
        self._repository.save(self._state_file, AppState(last_preset_path=normalized))

    def clear_last_preset_path(self) -> None:
        self._repository.save(self._state_file, AppState())