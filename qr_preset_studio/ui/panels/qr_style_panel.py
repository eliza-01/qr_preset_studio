from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QCheckBox, QComboBox, QFormLayout, QGroupBox, QSpinBox

from qr_preset_studio.domain.constants import (
    BODY_SHAPES,
    EYE_BALL_SHAPES,
    EYE_FRAME_SHAPES,
    GRADIENT_DIRECTIONS,
)
from qr_preset_studio.ui.widgets.color_button import ColorButton
from qr_preset_studio.ui.widgets.lockable_field import LockableField


class QrStylePanel(QGroupBox):
    changed = Signal()

    def __init__(self) -> None:
        super().__init__("Стиль QR")
        form = QFormLayout(self)
        form.setSpacing(10)

        self.body_shape_combo = _combo(BODY_SHAPES)
        self.rounded_body_radius_spin = _spin(0, 200, " px")
        self.spikes_single_corner_radius_spin = _spin(0, 200, " px")
        self.eye_frame_combo = _combo(EYE_FRAME_SHAPES)
        self.eye_ball_combo = _combo(EYE_BALL_SHAPES)
        self.qr_color_button = ColorButton("#0F172A", "Основной цвет QR")
        self.gradient_enabled_check = QCheckBox("Включить градиент")
        self.gradient_color_button = ColorButton("#2563EB", "Второй цвет градиента")
        self.gradient_direction_combo = _combo(GRADIENT_DIRECTIONS)

        self.rounded_body_radius_spin.setValue(8)
        self.spikes_single_corner_radius_spin.setValue(8)

        self.body_shape_field = LockableField(self.body_shape_combo)
        self.rounded_body_radius_field = LockableField(self.rounded_body_radius_spin)
        self.spikes_single_corner_radius_field = LockableField(self.spikes_single_corner_radius_spin)
        self.eye_frame_field = LockableField(self.eye_frame_combo)
        self.eye_ball_field = LockableField(self.eye_ball_combo)
        self.qr_color_field = LockableField(self.qr_color_button)
        self.gradient_enabled_field = LockableField(self.gradient_enabled_check)
        self.gradient_color_field = LockableField(self.gradient_color_button)
        self.gradient_direction_field = LockableField(self.gradient_direction_combo)

        form.addRow("Body shape", self.body_shape_field)
        form.addRow("Радиус скругления body", self.rounded_body_radius_field)
        form.addRow("Радиус свободного угла spikes", self.spikes_single_corner_radius_field)
        form.addRow("Eye frame", self.eye_frame_field)
        form.addRow("Eye ball", self.eye_ball_field)
        form.addRow("Цвет QR", self.qr_color_field)
        form.addRow("Градиент", self.gradient_enabled_field)
        form.addRow("Второй цвет", self.gradient_color_field)
        form.addRow("Направление", self.gradient_direction_field)

        self.body_shape_combo.currentTextChanged.connect(self._sync_state)
        self.body_shape_combo.currentTextChanged.connect(self.changed)
        self.rounded_body_radius_spin.valueChanged.connect(self.changed)
        self.spikes_single_corner_radius_spin.valueChanged.connect(self.changed)
        self.eye_frame_combo.currentTextChanged.connect(self.changed)
        self.eye_ball_combo.currentTextChanged.connect(self.changed)
        self.gradient_enabled_check.toggled.connect(self.changed)
        self.gradient_direction_combo.currentTextChanged.connect(self.changed)
        self.qr_color_button.clicked.connect(self.changed)
        self.gradient_color_button.clicked.connect(self.changed)

        self.sync_state()

    def sync_state(self) -> None:
        self._sync_state(self.body_shape_combo.currentText())

    def _sync_state(self, shape: str) -> None:
        self.rounded_body_radius_field.set_content_enabled(shape == "rounded")
        self.spikes_single_corner_radius_field.set_content_enabled(shape == "spikes")


def _combo(values: list[str]) -> QComboBox:
    combo = QComboBox()
    combo.addItems(values)
    return combo


def _spin(minimum: int, maximum: int, suffix: str = "") -> QSpinBox:
    spin = QSpinBox()
    spin.setRange(minimum, maximum)
    spin.setSingleStep(1)
    if suffix:
        spin.setSuffix(suffix)
    return spin