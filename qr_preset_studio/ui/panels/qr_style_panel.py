# qr_preset_studio/ui/panels/qr_style_panel.py
from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QCheckBox, QComboBox, QFormLayout, QGroupBox, QSpinBox, QWidget

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
        self._form = QFormLayout(self)
        self._form.setSpacing(10)

        self.body_shape_combo = _combo(BODY_SHAPES)
        self.rounded_body_radius_spin = _spin(0, 200, " px")
        self.spikes_single_corner_radius_spin = _spin(0, 200, " px")
        self.eye_frame_combo = _combo(EYE_FRAME_SHAPES)
        self.eye_ball_combo = _combo(EYE_BALL_SHAPES)
        self.qr_color_button = ColorButton("#0F172A", "Основной цвет QR")
        self.gradient_enabled_check = QCheckBox("Включить градиент")
        self.gradient_color_button = ColorButton("#2563EB", "Второй цвет градиента")
        self.gradient_direction_combo = _combo(GRADIENT_DIRECTIONS)
        self.gradient_offset_horizontal_spin = _spin(-5000, 5000, " px")
        self.gradient_offset_vertical_spin = _spin(-5000, 5000, " px")
        self.gradient_offset_diagonal_down_spin = _spin(-5000, 5000, " px")
        self.gradient_offset_diagonal_up_spin = _spin(-5000, 5000, " px")

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
        self.gradient_offset_horizontal_field = LockableField(self.gradient_offset_horizontal_spin)
        self.gradient_offset_vertical_field = LockableField(self.gradient_offset_vertical_spin)
        self.gradient_offset_diagonal_down_field = LockableField(self.gradient_offset_diagonal_down_spin)
        self.gradient_offset_diagonal_up_field = LockableField(self.gradient_offset_diagonal_up_spin)

        self._form.addRow("Body shape", self.body_shape_field)
        self._form.addRow("Радиус скругления body", self.rounded_body_radius_field)
        self._form.addRow("Радиус свободного угла spikes", self.spikes_single_corner_radius_field)
        self._form.addRow("Eye frame", self.eye_frame_field)
        self._form.addRow("Eye ball", self.eye_ball_field)
        self._form.addRow("Цвет QR", self.qr_color_field)
        self._form.addRow("Градиент", self.gradient_enabled_field)
        self._form.addRow("Второй цвет", self.gradient_color_field)
        self._form.addRow("Направление", self.gradient_direction_field)
        self._form.addRow("Смещение horizontal", self.gradient_offset_horizontal_field)
        self._form.addRow("Смещение vertical", self.gradient_offset_vertical_field)
        self._form.addRow("Смещение diagonal_down", self.gradient_offset_diagonal_down_field)
        self._form.addRow("Смещение diagonal_up", self.gradient_offset_diagonal_up_field)

        self.body_shape_combo.currentTextChanged.connect(self._sync_state)
        self.body_shape_combo.currentTextChanged.connect(self.changed)
        self.rounded_body_radius_spin.valueChanged.connect(self.changed)
        self.spikes_single_corner_radius_spin.valueChanged.connect(self.changed)
        self.eye_frame_combo.currentTextChanged.connect(self.changed)
        self.eye_ball_combo.currentTextChanged.connect(self.changed)
        self.gradient_enabled_check.toggled.connect(self._sync_state)
        self.gradient_enabled_check.toggled.connect(self.changed)
        self.gradient_direction_combo.currentTextChanged.connect(self._sync_state)
        self.gradient_direction_combo.currentTextChanged.connect(self.changed)
        self.gradient_offset_horizontal_spin.valueChanged.connect(self.changed)
        self.gradient_offset_vertical_spin.valueChanged.connect(self.changed)
        self.gradient_offset_diagonal_down_spin.valueChanged.connect(self.changed)
        self.gradient_offset_diagonal_up_spin.valueChanged.connect(self.changed)
        self.qr_color_button.clicked.connect(self.changed)
        self.gradient_color_button.clicked.connect(self.changed)

        self.sync_state()

    def sync_state(self) -> None:
        self._sync_state()

    def _sync_state(self) -> None:
        shape = self.body_shape_combo.currentText()
        gradient_enabled = self.gradient_enabled_check.isChecked()
        gradient_direction = self.gradient_direction_combo.currentText()

        self.rounded_body_radius_field.set_content_enabled(shape == "rounded")
        self.spikes_single_corner_radius_field.set_content_enabled(shape == "spikes")

        self.gradient_color_field.set_content_enabled(gradient_enabled)
        self.gradient_direction_field.set_content_enabled(gradient_enabled)

        self._set_offset_row_visible(
            self.gradient_offset_horizontal_field,
            gradient_enabled and gradient_direction == "horizontal",
        )
        self._set_offset_row_visible(
            self.gradient_offset_vertical_field,
            gradient_enabled and gradient_direction == "vertical",
        )
        self._set_offset_row_visible(
            self.gradient_offset_diagonal_down_field,
            gradient_enabled and gradient_direction == "diagonal_down",
        )
        self._set_offset_row_visible(
            self.gradient_offset_diagonal_up_field,
            gradient_enabled and gradient_direction == "diagonal_up",
        )

    def _set_offset_row_visible(self, field: LockableField, visible: bool) -> None:
        field.set_content_enabled(visible)
        field.setVisible(visible)

        label = self._form.labelForField(field)
        if label is not None:
            label.setVisible(visible)


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
