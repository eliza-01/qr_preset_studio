from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QComboBox, QFormLayout, QGroupBox, QLineEdit, QSpinBox

from qr_preset_studio.domain.constants import (
    QR_ERROR_CORRECTION_LEVELS,
    QR_MASK_PATTERN_VALUES,
    QR_VERSION_VALUES,
)
from qr_preset_studio.ui.widgets.lockable_field import LockableField


class ContentPanel(QGroupBox):
    changed = Signal()

    def __init__(self) -> None:
        super().__init__("QR")
        form = QFormLayout(self)
        form.setSpacing(10)

        self.link_input = QLineEdit()
        self.link_input.setPlaceholderText("https://example.com")

        self.qr_version_combo = _combo(QR_VERSION_VALUES)
        self.qr_error_correction_combo = _combo(QR_ERROR_CORRECTION_LEVELS)
        self.qr_mask_pattern_combo = _combo(QR_MASK_PATTERN_VALUES)
        self.qr_optimize_spin = _spin(0, 100)

        self.qr_scale_spin = _spin(10, 90, " %")
        self.qr_offset_x_spin = _spin(-5000, 5000, " px")
        self.qr_offset_y_spin = _spin(-5000, 5000, " px")

        self.qr_error_correction_combo.setCurrentText("H")
        self.qr_optimize_spin.setValue(20)

        form.addRow("Ссылка", LockableField(self.link_input))
        form.addRow("Version", LockableField(self.qr_version_combo))
        form.addRow("ECC", LockableField(self.qr_error_correction_combo))
        form.addRow("Mask", LockableField(self.qr_mask_pattern_combo))
        form.addRow("Optimize", LockableField(self.qr_optimize_spin))
        form.addRow("Размер QR", LockableField(self.qr_scale_spin))
        form.addRow("Сдвиг X", LockableField(self.qr_offset_x_spin))
        form.addRow("Сдвиг Y", LockableField(self.qr_offset_y_spin))

        self.link_input.textChanged.connect(self.changed)
        self.qr_version_combo.currentTextChanged.connect(self.changed)
        self.qr_error_correction_combo.currentTextChanged.connect(self.changed)
        self.qr_mask_pattern_combo.currentTextChanged.connect(self.changed)
        self.qr_optimize_spin.valueChanged.connect(self.changed)
        self.qr_scale_spin.valueChanged.connect(self.changed)
        self.qr_offset_x_spin.valueChanged.connect(self.changed)
        self.qr_offset_y_spin.valueChanged.connect(self.changed)


def _spin(minimum: int, maximum: int, suffix: str = "") -> QSpinBox:
    spin = QSpinBox()
    spin.setRange(minimum, maximum)
    spin.setSingleStep(1)
    if suffix:
        spin.setSuffix(suffix)
    return spin


def _combo(values: list[str]) -> QComboBox:
    combo = QComboBox()
    combo.addItems(values)
    return combo