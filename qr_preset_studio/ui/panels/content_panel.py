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
        self.qr_dpi_spin = _spin(72, 2400, " dpi")

        self.qr_scale_spin = _spin(10, 90, " %")
        self.qr_offset_x_spin = _spin(-5000, 5000, " px")
        self.qr_offset_y_spin = _spin(-5000, 5000, " px")

        self.qr_version_combo.setCurrentText("auto")
        self.qr_error_correction_combo.setCurrentText("H")
        self.qr_mask_pattern_combo.setCurrentText("auto")
        self.qr_optimize_spin.setValue(20)
        self.qr_dpi_spin.setValue(300)

        self.link_field = LockableField(self.link_input)
        self.qr_version_field = LockableField(self.qr_version_combo)
        self.qr_error_correction_field = LockableField(self.qr_error_correction_combo)
        self.qr_mask_pattern_field = LockableField(self.qr_mask_pattern_combo)
        self.qr_optimize_field = LockableField(self.qr_optimize_spin)
        self.qr_dpi_field = LockableField(self.qr_dpi_spin)
        self.qr_scale_field = LockableField(self.qr_scale_spin)
        self.qr_offset_x_field = LockableField(self.qr_offset_x_spin)
        self.qr_offset_y_field = LockableField(self.qr_offset_y_spin)

        form.addRow("Ссылка", self.link_field)
        form.addRow("Version", self.qr_version_field)
        form.addRow("ECC", self.qr_error_correction_field)
        form.addRow("Mask", self.qr_mask_pattern_field)
        form.addRow("Optimize", self.qr_optimize_field)
        form.addRow("QR DPI", self.qr_dpi_field)
        form.addRow("Размер QR", self.qr_scale_field)
        form.addRow("Сдвиг X", self.qr_offset_x_field)
        form.addRow("Сдвиг Y", self.qr_offset_y_field)

        self.link_input.textChanged.connect(self.changed)
        self.qr_version_combo.currentTextChanged.connect(self.changed)
        self.qr_error_correction_combo.currentTextChanged.connect(self.changed)
        self.qr_mask_pattern_combo.currentTextChanged.connect(self.changed)
        self.qr_optimize_spin.valueChanged.connect(self.changed)
        self.qr_dpi_spin.valueChanged.connect(self.changed)
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