# qr_preset_studio/ui/panels/claw_panel.py
from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QCheckBox, QDoubleSpinBox, QFormLayout, QSpinBox, QVBoxLayout, QWidget

from qr_preset_studio.ui.widgets.collapsible_section import CollapsibleSection
from qr_preset_studio.ui.widgets.lockable_field import LockableField


class ClawPanel(QWidget):
    changed = Signal()

    def __init__(self) -> None:
        super().__init__()

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.section = CollapsibleSection("Коготь body")
        root.addWidget(self.section)

        content = QWidget()
        form = QFormLayout(content)
        form.setSpacing(10)

        self.claw_detail_scale_spin = _int_spin(1, 32)
        self.claw_curve_steps_spin = _int_spin(4, 200)
        self.claw_alternate_direction_check = QCheckBox("Чередовать направление")
        self.claw_lean_right_check = QCheckBox("Базовый наклон вправо")

        self.claw_tip_x_spin = _float_spin(-2.0, 2.0)
        self.claw_tip_y_spin = _float_spin(-2.0, 2.0)

        self.claw_outer_ctrl1_x_spin = _float_spin(-2.0, 2.0)
        self.claw_outer_ctrl1_y_spin = _float_spin(-2.0, 2.0)
        self.claw_outer_ctrl2_x_spin = _float_spin(-2.0, 2.0)
        self.claw_outer_ctrl2_y_spin = _float_spin(-2.0, 2.0)

        self.claw_inner_ctrl1_x_spin = _float_spin(-2.0, 2.0)
        self.claw_inner_ctrl1_y_spin = _float_spin(-2.0, 2.0)
        self.claw_inner_ctrl2_x_spin = _float_spin(-2.0, 2.0)
        self.claw_inner_ctrl2_y_spin = _float_spin(-2.0, 2.0)

        self.claw_detail_scale_spin.setValue(6)
        self.claw_curve_steps_spin.setValue(40)
        self.claw_alternate_direction_check.setChecked(True)
        self.claw_lean_right_check.setChecked(True)

        self.claw_tip_x_spin.setValue(0.86)
        self.claw_tip_y_spin.setValue(0.06)
        self.claw_outer_ctrl1_x_spin.setValue(0.00)
        self.claw_outer_ctrl1_y_spin.setValue(0.52)
        self.claw_outer_ctrl2_x_spin.setValue(0.10)
        self.claw_outer_ctrl2_y_spin.setValue(0.10)
        self.claw_inner_ctrl1_x_spin.setValue(1.00)
        self.claw_inner_ctrl1_y_spin.setValue(0.08)
        self.claw_inner_ctrl2_x_spin.setValue(0.82)
        self.claw_inner_ctrl2_y_spin.setValue(0.70)

        self.claw_detail_scale_field = LockableField(self.claw_detail_scale_spin)
        self.claw_curve_steps_field = LockableField(self.claw_curve_steps_spin)
        self.claw_alternate_direction_field = LockableField(self.claw_alternate_direction_check)
        self.claw_lean_right_field = LockableField(self.claw_lean_right_check)

        self.claw_tip_x_field = LockableField(self.claw_tip_x_spin)
        self.claw_tip_y_field = LockableField(self.claw_tip_y_spin)

        self.claw_outer_ctrl1_x_field = LockableField(self.claw_outer_ctrl1_x_spin)
        self.claw_outer_ctrl1_y_field = LockableField(self.claw_outer_ctrl1_y_spin)
        self.claw_outer_ctrl2_x_field = LockableField(self.claw_outer_ctrl2_x_spin)
        self.claw_outer_ctrl2_y_field = LockableField(self.claw_outer_ctrl2_y_spin)

        self.claw_inner_ctrl1_x_field = LockableField(self.claw_inner_ctrl1_x_spin)
        self.claw_inner_ctrl1_y_field = LockableField(self.claw_inner_ctrl1_y_spin)
        self.claw_inner_ctrl2_x_field = LockableField(self.claw_inner_ctrl2_x_spin)
        self.claw_inner_ctrl2_y_field = LockableField(self.claw_inner_ctrl2_y_spin)

        form.addRow("Claw detail scale", self.claw_detail_scale_field)
        form.addRow("Claw curve steps", self.claw_curve_steps_field)
        form.addRow("Чередовать наклон", self.claw_alternate_direction_field)
        form.addRow("Наклон вправо", self.claw_lean_right_field)

        form.addRow("Tip X", self.claw_tip_x_field)
        form.addRow("Tip Y", self.claw_tip_y_field)

        form.addRow("Outer ctrl1 X", self.claw_outer_ctrl1_x_field)
        form.addRow("Outer ctrl1 Y", self.claw_outer_ctrl1_y_field)
        form.addRow("Outer ctrl2 X", self.claw_outer_ctrl2_x_field)
        form.addRow("Outer ctrl2 Y", self.claw_outer_ctrl2_y_field)

        form.addRow("Inner ctrl1 X", self.claw_inner_ctrl1_x_field)
        form.addRow("Inner ctrl1 Y", self.claw_inner_ctrl1_y_field)
        form.addRow("Inner ctrl2 X", self.claw_inner_ctrl2_x_field)
        form.addRow("Inner ctrl2 Y", self.claw_inner_ctrl2_y_field)

        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.addWidget(content)
        self.section.set_content_layout(content_layout)
        self.section.set_expanded(False)

        self.claw_detail_scale_spin.valueChanged.connect(self.changed)
        self.claw_curve_steps_spin.valueChanged.connect(self.changed)
        self.claw_alternate_direction_check.toggled.connect(self.changed)
        self.claw_lean_right_check.toggled.connect(self.changed)

        self.claw_tip_x_spin.valueChanged.connect(self.changed)
        self.claw_tip_y_spin.valueChanged.connect(self.changed)

        self.claw_outer_ctrl1_x_spin.valueChanged.connect(self.changed)
        self.claw_outer_ctrl1_y_spin.valueChanged.connect(self.changed)
        self.claw_outer_ctrl2_x_spin.valueChanged.connect(self.changed)
        self.claw_outer_ctrl2_y_spin.valueChanged.connect(self.changed)

        self.claw_inner_ctrl1_x_spin.valueChanged.connect(self.changed)
        self.claw_inner_ctrl1_y_spin.valueChanged.connect(self.changed)
        self.claw_inner_ctrl2_x_spin.valueChanged.connect(self.changed)
        self.claw_inner_ctrl2_y_spin.valueChanged.connect(self.changed)

        self.setVisible(False)

    def sync_state(self, enabled: bool) -> None:
        self.setVisible(enabled)
        for field in self._shape_fields():
            field.set_content_enabled(enabled)

    def _shape_fields(self) -> list[LockableField]:
        return [
            self.claw_detail_scale_field,
            self.claw_curve_steps_field,
            self.claw_alternate_direction_field,
            self.claw_lean_right_field,
            self.claw_tip_x_field,
            self.claw_tip_y_field,
            self.claw_outer_ctrl1_x_field,
            self.claw_outer_ctrl1_y_field,
            self.claw_outer_ctrl2_x_field,
            self.claw_outer_ctrl2_y_field,
            self.claw_inner_ctrl1_x_field,
            self.claw_inner_ctrl1_y_field,
            self.claw_inner_ctrl2_x_field,
            self.claw_inner_ctrl2_y_field,
        ]


def _int_spin(minimum: int, maximum: int) -> QSpinBox:
    spin = QSpinBox()
    spin.setRange(minimum, maximum)
    spin.setSingleStep(1)
    return spin


def _float_spin(minimum: float, maximum: float) -> QDoubleSpinBox:
    spin = QDoubleSpinBox()
    spin.setRange(minimum, maximum)
    spin.setDecimals(3)
    spin.setSingleStep(0.01)
    return spin
