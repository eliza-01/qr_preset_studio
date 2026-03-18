from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QFormLayout, QGroupBox, QSpinBox

from qr_preset_studio.ui.widgets.color_button import ColorButton


class CanvasPanel(QGroupBox):
    changed = Signal()

    def __init__(self) -> None:
        super().__init__("Итоговое изображение")
        form = QFormLayout(self)
        form.setSpacing(10)

        self.canvas_width_spin = _spin(256, 8000, " px")
        self.canvas_height_spin = _spin(256, 8000, " px")
        self.canvas_bg_color_button = ColorButton("#F3F4F6", "Цвет фона")

        form.addRow("Ширина", self.canvas_width_spin)
        form.addRow("Высота", self.canvas_height_spin)
        form.addRow("Цвет фона", self.canvas_bg_color_button)

        self.canvas_width_spin.valueChanged.connect(self.changed)
        self.canvas_height_spin.valueChanged.connect(self.changed)
        self.canvas_bg_color_button.clicked.connect(self.changed)


def _spin(minimum: int, maximum: int, suffix: str = "") -> QSpinBox:
    spin = QSpinBox()
    spin.setRange(minimum, maximum)
    spin.setSingleStep(1)
    if suffix:
        spin.setSuffix(suffix)
    return spin
