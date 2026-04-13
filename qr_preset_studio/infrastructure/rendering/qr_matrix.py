# qr_preset_studio/infrastructure/rendering/qr_matrix.py
from __future__ import annotations

import qrcode
from qrcode.exceptions import DataOverflowError

from qr_preset_studio.domain.models.preset import Preset
from qr_preset_studio.infrastructure.rendering.constants import FINDER_SIZE, QR_BORDER_MODULES


_ERROR_CORRECTION_MAP = {
    "L": qrcode.constants.ERROR_CORRECT_L,
    "M": qrcode.constants.ERROR_CORRECT_M,
    "Q": qrcode.constants.ERROR_CORRECT_Q,
    "H": qrcode.constants.ERROR_CORRECT_H,
}


def build_matrix(preset: Preset) -> list[list[bool]]:
    qr = qrcode.QRCode(
        version=preset.qr_version or None,
        error_correction=_ERROR_CORRECTION_MAP[preset.qr_error_correction],
        box_size=1,
        border=QR_BORDER_MODULES,
        mask_pattern=None if preset.qr_mask_pattern < 0 else preset.qr_mask_pattern,
    )
    qr.add_data(preset.link, optimize=preset.qr_optimize)

    try:
        qr.make(fit=preset.qr_version == 0)
    except DataOverflowError as exc:
        raise ValueError(_overflow_message(preset)) from exc

    return qr.get_matrix()


def active_module_count(matrix_size: int) -> int:
    return max(1, matrix_size - (QR_BORDER_MODULES * 2))


def finder_origins(active_module_count_value: int) -> list[tuple[int, int]]:
    end = active_module_count_value - FINDER_SIZE
    return [(0, 0), (end, 0), (0, end)]


def in_finder_area(row: int, col: int, origins) -> bool:
    for origin_col, origin_row in origins:
        if origin_col <= col < origin_col + FINDER_SIZE and origin_row <= row < origin_row + FINDER_SIZE:
            return True
    return False


def _overflow_message(preset: Preset) -> str:
    version_label = "auto" if preset.qr_version == 0 else str(preset.qr_version)
    mask_label = "auto" if preset.qr_mask_pattern < 0 else str(preset.qr_mask_pattern)

    hints: list[str] = []
    if preset.qr_version != 0:
        hints.append("поставь Version=auto или увеличь version")
    if preset.qr_error_correction in {"Q", "H"}:
        hints.append("снизь ECC до M или L")
    if preset.qr_mask_pattern >= 0:
        hints.append("поставь Mask=auto")

    hint_text = f" Что можно сделать: {'; '.join(hints)}." if hints else ""
    return (
        "Текущие параметры QR не помещают ссылку: "
        f"version={version_label}, ecc={preset.qr_error_correction}, "
        f"mask={mask_label}, optimize={preset.qr_optimize}, "
        f"символов={len(preset.link.strip())}.{hint_text}"
    )
