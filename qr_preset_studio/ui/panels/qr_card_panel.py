from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QCheckBox, QFormLayout, QSpinBox, QVBoxLayout, QWidget

from qr_preset_studio.ui.widgets.collapsible_section import CollapsibleSection
from qr_preset_studio.ui.widgets.color_button import ColorButton
from qr_preset_studio.ui.widgets.lockable_field import LockableField


class QrCardPanel(QWidget):
    changed = Signal()

    def __init__(self) -> None:
        super().__init__()

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.section = CollapsibleSection("Фон и границы QR")
        root.addWidget(self.section)

        self.qr_background_enabled_check = QCheckBox("Показывать фон QR")
        self.qr_background_color_button = ColorButton("#FFFFFF", "Цвет фона QR")
        self.qr_background_padding_spin = _spin(0, 500, " px")
        self.qr_background_radius_spin = _spin(0, 200, " px")
        self.qr_border_width_spin = _spin(0, 50, " px")
        self.qr_border_color_button = ColorButton("#CBD5E1", "Цвет границы")

        self.qr_background_enabled_field = LockableField(self.qr_background_enabled_check)
        self.qr_background_color_field = LockableField(self.qr_background_color_button)
        self.qr_background_padding_field = LockableField(self.qr_background_padding_spin)
        self.qr_background_radius_field = LockableField(self.qr_background_radius_spin)
        self.qr_border_width_field = LockableField(self.qr_border_width_spin)
        self.qr_border_color_field = LockableField(self.qr_border_color_button)

        content = QWidget()
        form = QFormLayout(content)
        form.setSpacing(10)
        form.addRow("Показ", self.qr_background_enabled_field)
        form.addRow("Цвет", self.qr_background_color_field)
        form.addRow("Отступы", self.qr_background_padding_field)
        form.addRow("Скругление", self.qr_background_radius_field)
        form.addRow("Толщина границы", self.qr_border_width_field)
        form.addRow("Цвет границы", self.qr_border_color_field)

        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.addWidget(content)
        self.section.set_content_layout(content_layout)
        self.section.set_expanded(False)

        self.qr_background_enabled_check.toggled.connect(self.changed)
        self.qr_background_padding_spin.valueChanged.connect(self.changed)
        self.qr_background_radius_spin.valueChanged.connect(self.changed)
        self.qr_border_width_spin.valueChanged.connect(self.changed)
        self.qr_background_color_button.clicked.connect(self.changed)
        self.qr_border_color_button.clicked.connect(self.changed)


def _spin(minimum: int, maximum: int, suffix: str = "") -> QSpinBox:
    spin = QSpinBox()
    spin.setRange(minimum, maximum)
    spin.setSingleStep(1)
    if suffix:
        spin.setSuffix(suffix)
    return spin