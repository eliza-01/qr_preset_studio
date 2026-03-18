from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QFormLayout, QGroupBox, QLineEdit, QSpinBox


class ContentPanel(QGroupBox):
    changed = Signal()

    def __init__(self) -> None:
        super().__init__("QR")
        form = QFormLayout(self)
        form.setSpacing(10)

        self.link_input = QLineEdit()
        self.link_input.setPlaceholderText("https://example.com")
        self.qr_scale_spin = _spin(10, 90, " %")
        self.qr_offset_x_spin = _spin(-5000, 5000, " px")
        self.qr_offset_y_spin = _spin(-5000, 5000, " px")

        form.addRow("Ссылка", self.link_input)
        form.addRow("Размер QR", self.qr_scale_spin)
        form.addRow("Сдвиг X", self.qr_offset_x_spin)
        form.addRow("Сдвиг Y", self.qr_offset_y_spin)

        self.link_input.textChanged.connect(self.changed)
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
