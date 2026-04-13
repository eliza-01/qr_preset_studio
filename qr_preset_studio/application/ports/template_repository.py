# qr_preset_studio/application/ports/template_repository.py
from __future__ import annotations

from typing import Any, Protocol

from qr_preset_studio.domain.models.template import CardTemplate


class TemplateRepository(Protocol):
    def list_all(self) -> list[CardTemplate]: ...

    def create(self, template: CardTemplate) -> CardTemplate: ...

    def update_side(self, template_id: str, side: str, payload: dict[str, Any], preview: str) -> None: ...
