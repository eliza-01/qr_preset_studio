# qr_preset_studio/ui/panels/content_panel.py
from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from qr_preset_studio.domain.constants import (
    QR_ERROR_CORRECTION_LEVELS,
    QR_MASK_PATTERN_VALUES,
    QR_VERSION_VALUES,
    swyp_public_base_url,
)
from qr_preset_studio.ui.widgets.collapsible_section import CollapsibleSection
from qr_preset_studio.ui.widgets.lockable_field import LockableField


class ContentPanel(QGroupBox):
    changed = Signal()

    def __init__(self) -> None:
        super().__init__("QR")
        root = QVBoxLayout(self)
        root.setSpacing(10)

        self.link_input = QLineEdit()
        self.link_input.setPlaceholderText(f"{swyp_public_base_url()}/slug")

        self.qr_version_combo = _combo(QR_VERSION_VALUES)
        self.qr_error_correction_combo = _combo(QR_ERROR_CORRECTION_LEVELS)
        self.qr_mask_pattern_combo = _combo(QR_MASK_PATTERN_VALUES)
        self.qr_optimize_spin = _spin(0, 100)
        self.qr_dpi_spin = _spin(72, 2400, " dpi")

        self.qr_scale_spin = _spin(10, 90, " %")
        self.hide_qr_check = QCheckBox("Скрыть QR")
        self.qr_offset_x_spin = _spin(-5000, 5000, " px")
        self.qr_offset_y_spin = _spin(-5000, 5000, " px")

        self.qr_version_combo.setCurrentText("3")
        self.qr_error_correction_combo.setCurrentText("M")
        self.qr_mask_pattern_combo.setCurrentText("6")
        self.qr_optimize_spin.setValue(20)
        self.qr_dpi_spin.setValue(300)

        self.link_field = LockableField(self.link_input)
        self.qr_version_field = LockableField(self.qr_version_combo)
        self.qr_error_correction_field = LockableField(self.qr_error_correction_combo)
        self.qr_mask_pattern_field = LockableField(self.qr_mask_pattern_combo)
        self.qr_optimize_field = LockableField(self.qr_optimize_spin)
        self.qr_dpi_field = LockableField(self.qr_dpi_spin)
        self.qr_scale_field = LockableField(self.qr_scale_spin)
        self.hide_qr_field = LockableField(self.hide_qr_check)
        self.qr_offset_x_field = LockableField(self.qr_offset_x_spin)
        self.qr_offset_y_field = LockableField(self.qr_offset_y_spin)

        for field in [
            self.qr_version_field,
            self.qr_error_correction_field,
            self.qr_mask_pattern_field,
            self.qr_optimize_field,
        ]:
            field.set_locked(True)

        form = QFormLayout()
        form.setSpacing(10)
        form.addRow("Ссылка", self.link_field)
        form.addRow(_two_field_row(("QR DPI", self.qr_dpi_field), ("Размер QR", self.qr_scale_field)))
        form.addRow(self.hide_qr_field)
        form.addRow(_two_field_row(("Сдвиг X", self.qr_offset_x_field), ("Сдвиг Y", self.qr_offset_y_field)))
        root.addLayout(form)

        self.advanced_section = CollapsibleSection("default: Version (3), ECC (M), MASK (6), Optimize (20)")
        advanced_form = QFormLayout()
        advanced_form.setSpacing(10)
        advanced_form.addRow("Version", self.qr_version_field)
        advanced_form.addRow("ECC", self.qr_error_correction_field)
        advanced_form.addRow("MASK", self.qr_mask_pattern_field)
        advanced_form.addRow("Optimize", self.qr_optimize_field)

        advanced_content = QWidget()
        advanced_content.setLayout(advanced_form)

        advanced_layout = QVBoxLayout()
        advanced_layout.setContentsMargins(0, 0, 0, 0)
        advanced_layout.addWidget(advanced_content)
        self.advanced_section.set_content_layout(advanced_layout)
        self.advanced_section.set_expanded(False)
        root.addWidget(self.advanced_section)

        self.link_input.textChanged.connect(self.changed)
        self.qr_version_combo.currentTextChanged.connect(self.changed)
        self.qr_error_correction_combo.currentTextChanged.connect(self.changed)
        self.qr_mask_pattern_combo.currentTextChanged.connect(self.changed)
        self.qr_optimize_spin.valueChanged.connect(self.changed)
        self.qr_dpi_spin.valueChanged.connect(self.changed)
        self.qr_scale_spin.valueChanged.connect(self.changed)
        self.hide_qr_check.toggled.connect(self.changed)
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


def _two_field_row(left: tuple[str, QWidget], right: tuple[str, QWidget]) -> QWidget:
    row = QWidget()
    layout = QHBoxLayout(row)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(10)
    layout.addWidget(_field_column(*left), 1)
    layout.addWidget(_field_column(*right), 1)
    return row


def _field_column(title: str, control: QWidget) -> QWidget:
    column = QWidget()
    layout = QVBoxLayout(column)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(6)

    label = QLabel(title)
    layout.addWidget(label)
    layout.addWidget(control)
    return column
