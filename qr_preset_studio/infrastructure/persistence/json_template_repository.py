# qr_preset_studio/infrastructure/persistence/json_template_repository.py
from __future__ import annotations

import json
from pathlib import Path

from qr_preset_studio.domain.models.template import CardTemplate


class JsonTemplateRepository:
    def save(self, path: str | Path, template: CardTemplate) -> None:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(template.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")

    def load(self, path: str | Path) -> CardTemplate:
        source = Path(path)
        raw = json.loads(source.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            return CardTemplate()
        return CardTemplate.from_dict(raw)
