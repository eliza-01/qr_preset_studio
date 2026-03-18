from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class DatabaseSettings:
    database_file: Path


class DatabaseSessionFactory:
    def __init__(self, settings: DatabaseSettings) -> None:
        self._settings = settings

    def connect(self) -> sqlite3.Connection:
        self._settings.database_file.parent.mkdir(parents=True, exist_ok=True)
        return sqlite3.connect(self._settings.database_file)
