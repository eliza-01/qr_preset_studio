from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class CardTemplate:
    """
    Шаблон визитки (front/back) + превью.

    Важно:
    - front/back содержат "всю необходимую для воссоздания информацию" (любой JSON).
    - front_preview/back_preview могут быть:
        * локальным путем к файлу
        * URL (https://...), тогда UI скачает и закеширует картинку
    - assets — любые доп. метаданные/ссылки на ассеты (фоны и т.д.), которые позже уйдут в БД.
    """

    id: str = ""
    slug: str = ""
    front: dict[str, Any] = field(default_factory=dict)
    back: dict[str, Any] = field(default_factory=dict)
    front_preview: str = ""
    back_preview: str = ""
    assets: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "CardTemplate":
        if not isinstance(raw, dict):
            return cls()

        raw_id = raw.get("id", "")
        if isinstance(raw_id, (int, float)):
            template_id = str(int(raw_id))
        elif isinstance(raw_id, str):
            template_id = raw_id.strip()
        else:
            template_id = ""

        raw_slug = raw.get("slug", "")
        slug = raw_slug.strip() if isinstance(raw_slug, str) else ""

        front = raw.get("front", {})
        back = raw.get("back", {})
        if not isinstance(front, dict):
            front = {}
        if not isinstance(back, dict):
            back = {}

        fp = raw.get("front_preview", "")
        bp = raw.get("back_preview", "")
        front_preview = fp.strip() if isinstance(fp, str) else ""
        back_preview = bp.strip() if isinstance(bp, str) else ""

        assets = raw.get("assets", {})
        if not isinstance(assets, dict):
            assets = {}

        return cls(
            id=template_id,
            slug=slug,
            front=front,
            back=back,
            front_preview=front_preview,
            back_preview=back_preview,
            assets=assets,
        )