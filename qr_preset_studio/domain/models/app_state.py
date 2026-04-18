# qr_preset_studio/domain/models/app_state.py
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(slots=True)
class AppState:
    last_preset_path: str = ""
    output_profile_id: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "AppState":
        last_preset_path = raw.get("last_preset_path", "")
        output_profile_id = raw.get("output_profile_id", "")
        return cls(
            last_preset_path=last_preset_path if isinstance(last_preset_path, str) else "",
            output_profile_id=output_profile_id if isinstance(output_profile_id, str) else "",
        )
