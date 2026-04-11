from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from qr_preset_studio.domain.models.template import CardTemplate
from qr_preset_studio.infrastructure.database.mysql_session import MySqlSessionFactory


@dataclass(slots=True)
class _TemplateColumns:
    table: str
    id_col: str
    slug_col: str
    front_col: str | None
    back_col: str | None
    front_preview_col: str | None
    back_preview_col: str | None
    assets_col: str | None


class MySqlTemplateRepository:
    def __init__(self, session_factory: MySqlSessionFactory, table: str = "swyp_cards_templates") -> None:
        self._session_factory = session_factory
        self._table = table
        self._columns: _TemplateColumns | None = None

    def list_all(self) -> list[CardTemplate]:
        cols = self._discover_columns()

        select_cols: list[str] = [cols.id_col, cols.slug_col]
        if cols.front_col:
            select_cols.append(cols.front_col)
        if cols.back_col:
            select_cols.append(cols.back_col)
        if cols.front_preview_col:
            select_cols.append(cols.front_preview_col)
        if cols.back_preview_col:
            select_cols.append(cols.back_preview_col)
        if cols.assets_col:
            select_cols.append(cols.assets_col)

        sql = f"SELECT {', '.join(select_cols)} FROM {cols.table} ORDER BY {cols.id_col} DESC"

        conn = self._session_factory.connect()
        try:
            cur = conn.cursor()
            try:
                cur.execute(sql)
                rows = cur.fetchall()
            finally:
                cur.close()
        finally:
            conn.close()

        templates: list[CardTemplate] = []
        for row in rows:
            data = dict(zip(select_cols, row))
            templates.append(self._row_to_template(cols, data))
        return templates

    def create(self, template: CardTemplate) -> CardTemplate:
        cols = self._discover_columns()

        fields: list[str] = [cols.slug_col]
        values: list[Any] = [template.slug]

        if cols.front_col is not None:
            fields.append(cols.front_col)
            values.append(_dump_json(template.front))
        if cols.back_col is not None:
            fields.append(cols.back_col)
            values.append(_dump_json(template.back))
        if cols.front_preview_col is not None:
            fields.append(cols.front_preview_col)
            values.append(template.front_preview)
        if cols.back_preview_col is not None:
            fields.append(cols.back_preview_col)
            values.append(template.back_preview)
        if cols.assets_col is not None:
            fields.append(cols.assets_col)
            values.append(_dump_json(template.assets))

        placeholders = ", ".join(["%s"] * len(fields))
        sql = f"INSERT INTO {cols.table} ({', '.join(fields)}) VALUES ({placeholders})"

        conn = self._session_factory.connect()
        try:
            cur = conn.cursor()
            try:
                cur.execute(sql, values)
                conn.commit()
                new_id = str(cur.lastrowid)
            finally:
                cur.close()
        finally:
            conn.close()

        # return with id
        created = CardTemplate(
            id=new_id,
            slug=template.slug,
            front=template.front,
            back=template.back,
            front_preview=template.front_preview,
            back_preview=template.back_preview,
            assets=template.assets,
        )
        return created

    def update_side(self, template_id: str, side: str, payload: dict[str, Any], preview: str) -> None:
        cols = self._discover_columns()
        side = (side or "").strip().lower()
        if side not in {"front", "back"}:
            raise ValueError("side должен быть 'front' или 'back'")

        set_parts: list[str] = []
        values: list[Any] = []

        if side == "front":
            if cols.front_col is not None:
                set_parts.append(f"{cols.front_col}=%s")
                values.append(_dump_json(payload))
            if cols.front_preview_col is not None:
                set_parts.append(f"{cols.front_preview_col}=%s")
                values.append(preview)
        else:
            if cols.back_col is not None:
                set_parts.append(f"{cols.back_col}=%s")
                values.append(_dump_json(payload))
            if cols.back_preview_col is not None:
                set_parts.append(f"{cols.back_preview_col}=%s")
                values.append(preview)

        if not set_parts:
            raise RuntimeError(
                f"В таблице {cols.table} нет колонок для сохранения {side}. "
                "Нужны колонки для JSON и/или preview."
            )

        values.append(template_id)
        sql = f"UPDATE {cols.table} SET {', '.join(set_parts)} WHERE {cols.id_col}=%s"

        conn = self._session_factory.connect()
        try:
            cur = conn.cursor()
            try:
                cur.execute(sql, values)
                conn.commit()
            finally:
                cur.close()
        finally:
            conn.close()

    def _discover_columns(self) -> _TemplateColumns:
        if self._columns is not None:
            return self._columns

        conn = self._session_factory.connect()
        try:
            cur = conn.cursor()
            try:
                cur.execute(f"SHOW COLUMNS FROM {self._table}")
                rows = cur.fetchall()
            finally:
                cur.close()
        finally:
            conn.close()

        names = {str(r[0]) for r in rows}

        def pick(required: bool, *candidates: str) -> str | None:
            for c in candidates:
                if c in names:
                    return c
            if required:
                raise RuntimeError(
                    f"В таблице {self._table} не найдена нужная колонка из {list(candidates)}. "
                    f"Найдены колонки: {sorted(names)}"
                )
            return None

        cols = _TemplateColumns(
            table=self._table,
            id_col=pick(True, "id", "template_id") or "id",
            slug_col=pick(True, "slug") or "slug",
            front_col=pick(False, "front", "front_json", "front_data"),
            back_col=pick(False, "back", "back_json", "back_data"),
            front_preview_col=pick(False, "front_preview", "front_preview_url", "front_preview_data"),
            back_preview_col=pick(False, "back_preview", "back_preview_url", "back_preview_data"),
            assets_col=pick(False, "assets", "assets_json"),
        )

        self._columns = cols
        return cols

    def _row_to_template(self, cols: _TemplateColumns, row: dict[str, Any]) -> CardTemplate:
        template_id = row.get(cols.id_col, "")
        slug = row.get(cols.slug_col, "")

        front = _load_json(row.get(cols.front_col)) if cols.front_col else {}
        back = _load_json(row.get(cols.back_col)) if cols.back_col else {}
        assets = _load_json(row.get(cols.assets_col)) if cols.assets_col else {}

        fp = row.get(cols.front_preview_col, "") if cols.front_preview_col else ""
        bp = row.get(cols.back_preview_col, "") if cols.back_preview_col else ""

        return CardTemplate(
            id=str(template_id) if template_id is not None else "",
            slug=str(slug) if slug is not None else "",
            front=front,
            back=back,
            front_preview=str(fp) if fp is not None else "",
            back_preview=str(bp) if bp is not None else "",
            assets=assets,
        )


def _dump_json(value: Any) -> str:
    return json.dumps(value if value is not None else {}, ensure_ascii=False)


def _load_json(value: Any) -> dict[str, Any]:
    if value is None:
        return {}
    if isinstance(value, dict):
        return value
    if isinstance(value, (bytes, bytearray)):
        try:
            value = value.decode("utf-8", errors="replace")
        except Exception:
            return {}
    if isinstance(value, str):
        s = value.strip()
        if not s:
            return {}
        try:
            raw = json.loads(s)
        except Exception:
            return {}
        return raw if isinstance(raw, dict) else {}
    return {}