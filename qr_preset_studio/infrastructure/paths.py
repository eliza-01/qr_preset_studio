from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class AppPaths:
    root_dir: Path
    presets_dir: Path
    database_dir: Path
    database_file: Path

    @classmethod
    def default(cls) -> "AppPaths":
        root_dir = Path.home() / "QRPresetStudio"
        presets_dir = root_dir / "presets"
        database_dir = root_dir / "database"
        database_file = database_dir / "qr_preset_studio.sqlite3"

        presets_dir.mkdir(parents=True, exist_ok=True)
        database_dir.mkdir(parents=True, exist_ok=True)

        return cls(
            root_dir=root_dir,
            presets_dir=presets_dir,
            database_dir=database_dir,
            database_file=database_file,
        )
