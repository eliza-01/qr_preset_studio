# qr_preset_studio/domain/models/app_state.py
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(slots=True)
class AppState:
    last_preset_path: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "AppState":
        value = raw.get("last_preset_path", "")
        return cls(last_preset_path=value if isinstance(value, str) else "")
