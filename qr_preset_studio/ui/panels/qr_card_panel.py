from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QCheckBox, QFormLayout, QGroupBox, QSpinBox

from qr_preset_studio.ui.widgets.color_button import ColorButton


class QrCardPanel(QGroupBox):
    changed = Signal()

    def __init__(self) -> None:
        super().__init__("Фон и границы QR")
        form = QFormLayout(self)
        form.setSpacing(10)

        self.qr_background_enabled_check = QCheckBox("Показывать фон QR")
        self.qr_background_color_button = ColorButton("#FFFFFF", "Цвет фона QR")
        self.qr_background_padding_spin = _spin(0, 500, " px")
        self.qr_background_radius_spin = _spin(0, 200, " px")
        self.qr_border_width_spin = _spin(0, 50, " px")
        self.qr_border_color_button = ColorButton("#CBD5E1", "Цвет границы")

        form.addRow("Показ", self.qr_background_enabled_check)
        form.addRow("Цвет", self.qr_background_color_button)
        form.addRow("Отступы", self.qr_background_padding_spin)
        form.addRow("Скругление", self.qr_background_radius_spin)
        form.addRow("Толщина границы", self.qr_border_width_spin)
        form.addRow("Цвет границы", self.qr_border_color_button)

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
