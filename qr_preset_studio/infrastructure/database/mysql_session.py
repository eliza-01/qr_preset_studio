# qr_preset_studio/infrastructure/database/mysql_session.py
from __future__ import annotations

import os
from dataclasses import dataclass

try:
    import mysql.connector  # type: ignore
except Exception:  # pragma: no cover
    mysql = None  # type: ignore


@dataclass(slots=True)
class MySqlSettings:
    host: str
    port: int
    database: str
    user: str
    password: str
    charset: str = "utf8mb4"
    collation: str = "utf8mb4_unicode_ci"

    @classmethod
    def default_from_env(cls) -> "MySqlSettings":
        # defaults match your docker-compose
        host = os.environ.get("SWYP_DB_HOST", "127.0.0.1").strip() or "127.0.0.1"
        port_raw = os.environ.get("SWYP_DB_PORT", "3307").strip() or "3307"
        database = os.environ.get("SWYP_DB_NAME", "swyp").strip() or "swyp"
        user = os.environ.get("SWYP_DB_USER", "admin").strip() or "admin"
        password = os.environ.get("SWYP_DB_PASSWORD", "admin")

        try:
            port = int(port_raw)
        except ValueError:
            port = 3307

        return cls(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password,
        )


class MySqlSessionFactory:
    def __init__(self, settings: MySqlSettings) -> None:
        self._settings = settings

    @property
    def settings(self) -> MySqlSettings:
        return self._settings

    def connect(self):
        if mysql is None:
            raise RuntimeError(
                "Не найден mysql-connector-python. Установи: pip install mysql-connector-python"
            )

        conn = mysql.connector.connect(
            host=self._settings.host,
            port=self._settings.port,
            user=self._settings.user,
            password=self._settings.password,
            database=self._settings.database,
            autocommit=False,
        )

        # Ensure utf8mb4
        cur = conn.cursor()
        try:
            cur.execute(f"SET NAMES {self._settings.charset} COLLATE {self._settings.collation}")
        finally:
            cur.close()

        return conn
