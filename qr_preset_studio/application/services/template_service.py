from __future__ import annotations

from pathlib import Path
from typing import Any

from qr_preset_studio.application.ports.template_repository import TemplateRepository
from qr_preset_studio.domain.models.template import CardTemplate


class TemplateService:
    def __init__(self, repository: TemplateRepository, cache_dir: Path) -> None:
        self._repository = repository
        self._cache_dir = cache_dir

    @property
    def cache_dir(self) -> Path:
        return self._cache_dir

    def list_all(self) -> list[CardTemplate]:
        return self._repository.list_all()

    def create_new(
        self,
        *,
        slug: str,
        side: str,
        payload: dict[str, Any],
        preview: str,
        assets: dict[str, Any] | None = None,
    ) -> CardTemplate:
        slug = (slug or "").strip()
        if not slug:
            raise ValueError("slug не должен быть пустым")

        side = (side or "").strip().lower()
        if side not in {"front", "back"}:
            raise ValueError("side должен быть 'front' или 'back'")

        front_payload: dict[str, Any] = {}
        back_payload: dict[str, Any] = {}
        front_preview = ""
        back_preview = ""

        if side == "front":
            front_payload = payload
            front_preview = preview
        else:
            back_payload = payload
            back_preview = preview

        template = CardTemplate(
            id="",
            slug=slug,
            front=front_payload,
            back=back_payload,
            front_preview=front_preview,
            back_preview=back_preview,
            assets=assets or {},
        )
        return self._repository.create(template)

    def update_existing_side(
        self,
        *,
        template_id: str,
        side: str,
        payload: dict[str, Any],
        preview: str,
    ) -> None:
        template_id = (template_id or "").strip()
        if not template_id:
            raise ValueError("template_id не должен быть пустым")

        self._repository.update_side(template_id, side, payload, preview)