from __future__ import annotations

from typing import Iterable

import qrcode

from qr_preset_studio.infrastructure.rendering.constants import FINDER_SIZE, QR_BORDER_MODULES


def build_matrix(link: str) -> list[list[bool]]:
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=1,
        border=QR_BORDER_MODULES,
    )
    qr.add_data(link)
    qr.make(fit=True)
    return qr.get_matrix()


def active_module_count(matrix_size: int) -> int:
    return max(1, matrix_size - (QR_BORDER_MODULES * 2))


def finder_origins(active_modules: int) -> list[tuple[int, int]]:
    end = active_modules - FINDER_SIZE
    return [(0, 0), (end, 0), (0, end)]


def in_finder_area(row: int, col: int, origins: Iterable[tuple[int, int]]) -> bool:
    for origin_col, origin_row in origins:
        if origin_col <= col < origin_col + FINDER_SIZE and origin_row <= row < origin_row + FINDER_SIZE:
            return True
    return False
