from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QCheckBox, QComboBox, QFormLayout, QGroupBox

from qr_preset_studio.domain.constants import (
    BODY_SHAPES,
    EYE_BALL_SHAPES,
    EYE_FRAME_SHAPES,
    GRADIENT_DIRECTIONS,
)
from qr_preset_studio.ui.widgets.color_button import ColorButton


class QrStylePanel(QGroupBox):
    changed = Signal()

    def __init__(self) -> None:
        super().__init__("Стиль QR")
        form = QFormLayout(self)
        form.setSpacing(10)

        self.body_shape_combo = _combo(BODY_SHAPES)
        self.eye_frame_combo = _combo(EYE_FRAME_SHAPES)
        self.eye_ball_combo = _combo(EYE_BALL_SHAPES)
        self.qr_color_button = ColorButton("#0F172A", "Основной цвет QR")
        self.gradient_enabled_check = QCheckBox("Включить градиент")
        self.gradient_color_button = ColorButton("#2563EB", "Второй цвет градиента")
        self.gradient_direction_combo = _combo(GRADIENT_DIRECTIONS)

        form.addRow("Body shape", self.body_shape_combo)
        form.addRow("Eye frame", self.eye_frame_combo)
        form.addRow("Eye ball", self.eye_ball_combo)
        form.addRow("Цвет QR", self.qr_color_button)
        form.addRow("Градиент", self.gradient_enabled_check)
        form.addRow("Второй цвет", self.gradient_color_button)
        form.addRow("Направление", self.gradient_direction_combo)

        self.body_shape_combo.currentTextChanged.connect(self.changed)
        self.eye_frame_combo.currentTextChanged.connect(self.changed)
        self.eye_ball_combo.currentTextChanged.connect(self.changed)
        self.gradient_enabled_check.toggled.connect(self.changed)
        self.gradient_direction_combo.currentTextChanged.connect(self.changed)
        self.qr_color_button.clicked.connect(self.changed)
        self.gradient_color_button.clicked.connect(self.changed)


def _combo(values: list[str]) -> QComboBox:
    combo = QComboBox()
    combo.addItems(values)
    return combo
