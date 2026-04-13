# qr_preset_studio/ui/forms/preset_editor.py
from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QVBoxLayout, QWidget

from qr_preset_studio.domain.models.preset import Preset
from qr_preset_studio.ui.panels.actions_panel import ActionsPanel
from qr_preset_studio.ui.panels.background_panel import BackgroundPanel
from qr_preset_studio.ui.panels.canvas_panel import CanvasPanel
from qr_preset_studio.ui.panels.claw_panel import ClawPanel
from qr_preset_studio.ui.panels.content_panel import ContentPanel
from qr_preset_studio.ui.panels.qr_card_panel import QrCardPanel
from qr_preset_studio.ui.panels.qr_style_panel import QrStylePanel
from qr_preset_studio.ui.widgets.lockable_field import LockableField


_DEFAULT_LOCKED_FIELDS = {
    "qr_version",
    "qr_error_correction",
    "qr_mask_pattern",
    "qr_optimize",
}


class PresetEditor(QWidget):
    changed = Signal()

    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        self.content_panel = ContentPanel()
        self.canvas_panel = CanvasPanel()
        self.background_panel = BackgroundPanel()
        self.qr_style_panel = QrStylePanel()
        self.claw_panel = ClawPanel()
        self.qr_card_panel = QrCardPanel()
        self.actions_panel = ActionsPanel()

        for panel in [
            self.content_panel,
            self.canvas_panel,
            self.background_panel,
            self.qr_style_panel,
            self.claw_panel,
            self.qr_card_panel,
        ]:
            panel.changed.connect(self.changed)
            layout.addWidget(panel)

        self.qr_style_panel.body_shape_combo.currentTextChanged.connect(self._sync_shape_panels)

        layout.addWidget(self.actions_panel)
        layout.addStretch(1)
        self._sync_shape_panels()

    def to_preset(self) -> Preset:
        return Preset(
            link=self.content_panel.link_input.text().strip(),
            canvas_width=self.canvas_panel.canvas_width_spin.value(),
            canvas_height=self.canvas_panel.canvas_height_spin.value(),
            canvas_background_color=self.canvas_panel.canvas_bg_color_button.color(),
            background_image_path=self.background_panel.background_path_input.text().strip(),
            background_scale_percent=self.background_panel.background_scale_spin.value(),
            background_offset_x=self.background_panel.background_offset_x_spin.value(),
            background_offset_y=self.background_panel.background_offset_y_spin.value(),
            qr_scale_percent=self.content_panel.qr_scale_spin.value(),
            qr_offset_x=self.content_panel.qr_offset_x_spin.value(),
            qr_offset_y=self.content_panel.qr_offset_y_spin.value(),
            qr_version=_parse_version(self.content_panel.qr_version_combo.currentText()),
            qr_error_correction=self.content_panel.qr_error_correction_combo.currentText(),
            qr_mask_pattern=_parse_mask(self.content_panel.qr_mask_pattern_combo.currentText()),
            qr_optimize=self.content_panel.qr_optimize_spin.value(),
            qr_dpi=self.content_panel.qr_dpi_spin.value(),
            body_shape=self.qr_style_panel.body_shape_combo.currentText(),
            rounded_body_radius_px=self.qr_style_panel.rounded_body_radius_spin.value(),
            spikes_single_corner_radius_px=self.qr_style_panel.spikes_single_corner_radius_spin.value(),
            claw_detail_scale=self.claw_panel.claw_detail_scale_spin.value(),
            claw_curve_steps=self.claw_panel.claw_curve_steps_spin.value(),
            claw_alternate_direction=self.claw_panel.claw_alternate_direction_check.isChecked(),
            claw_lean_right=self.claw_panel.claw_lean_right_check.isChecked(),
            claw_tip_x=self.claw_panel.claw_tip_x_spin.value(),
            claw_tip_y=self.claw_panel.claw_tip_y_spin.value(),
            claw_outer_ctrl1_x=self.claw_panel.claw_outer_ctrl1_x_spin.value(),
            claw_outer_ctrl1_y=self.claw_panel.claw_outer_ctrl1_y_spin.value(),
            claw_outer_ctrl2_x=self.claw_panel.claw_outer_ctrl2_x_spin.value(),
            claw_outer_ctrl2_y=self.claw_panel.claw_outer_ctrl2_y_spin.value(),
            claw_inner_ctrl1_x=self.claw_panel.claw_inner_ctrl1_x_spin.value(),
            claw_inner_ctrl1_y=self.claw_panel.claw_inner_ctrl1_y_spin.value(),
            claw_inner_ctrl2_x=self.claw_panel.claw_inner_ctrl2_x_spin.value(),
            claw_inner_ctrl2_y=self.claw_panel.claw_inner_ctrl2_y_spin.value(),
            eye_frame_shape=self.qr_style_panel.eye_frame_combo.currentText(),
            eye_ball_shape=self.qr_style_panel.eye_ball_combo.currentText(),
            qr_foreground_color=self.qr_style_panel.qr_color_button.color(),
            gradient_enabled=self.qr_style_panel.gradient_enabled_check.isChecked(),
            gradient_color=self.qr_style_panel.gradient_color_button.color(),
            gradient_direction=self.qr_style_panel.gradient_direction_combo.currentText(),
            gradient_offset_horizontal_px=self.qr_style_panel.gradient_offset_horizontal_spin.value(),
            gradient_offset_vertical_px=self.qr_style_panel.gradient_offset_vertical_spin.value(),
            gradient_offset_diagonal_down_px=self.qr_style_panel.gradient_offset_diagonal_down_spin.value(),
            gradient_offset_diagonal_up_px=self.qr_style_panel.gradient_offset_diagonal_up_spin.value(),
            qr_background_enabled=self.qr_card_panel.qr_background_enabled_check.isChecked(),
            qr_background_color=self.qr_card_panel.qr_background_color_button.color(),
            qr_background_padding=self.qr_card_panel.qr_background_padding_spin.value(),
            qr_background_radius=self.qr_card_panel.qr_background_radius_spin.value(),
            qr_border_width=self.qr_card_panel.qr_border_width_spin.value(),
            qr_border_color=self.qr_card_panel.qr_border_color_button.color(),
            locked_fields=self._collect_locked_fields(),
        )

    def set_preset(self, preset: Preset) -> None:
        self.content_panel.link_input.setText(preset.link)
        self.canvas_panel.canvas_width_spin.setValue(preset.canvas_width)
        self.canvas_panel.canvas_height_spin.setValue(preset.canvas_height)
        self.canvas_panel.canvas_bg_color_button.set_color(preset.canvas_background_color)
        self.background_panel.set_background_path(preset.background_image_path)
        self.background_panel.background_scale_spin.setValue(preset.background_scale_percent)
        self.background_panel.background_offset_x_spin.setValue(preset.background_offset_x)
        self.background_panel.background_offset_y_spin.setValue(preset.background_offset_y)

        self.content_panel.qr_scale_spin.setValue(preset.qr_scale_percent)
        self.content_panel.qr_offset_x_spin.setValue(preset.qr_offset_x)
        self.content_panel.qr_offset_y_spin.setValue(preset.qr_offset_y)
        self.content_panel.qr_version_combo.setCurrentText(_version_text(preset.qr_version))
        self.content_panel.qr_error_correction_combo.setCurrentText(preset.qr_error_correction)
        self.content_panel.qr_mask_pattern_combo.setCurrentText(_mask_text(preset.qr_mask_pattern))
        self.content_panel.qr_optimize_spin.setValue(preset.qr_optimize)
        self.content_panel.qr_dpi_spin.setValue(preset.qr_dpi)

        self.qr_style_panel.body_shape_combo.setCurrentText(preset.body_shape)
        self.qr_style_panel.rounded_body_radius_spin.setValue(preset.rounded_body_radius_px)
        self.qr_style_panel.spikes_single_corner_radius_spin.setValue(preset.spikes_single_corner_radius_px)

        self.claw_panel.claw_detail_scale_spin.setValue(preset.claw_detail_scale)
        self.claw_panel.claw_curve_steps_spin.setValue(preset.claw_curve_steps)
        self.claw_panel.claw_alternate_direction_check.setChecked(preset.claw_alternate_direction)
        self.claw_panel.claw_lean_right_check.setChecked(preset.claw_lean_right)
        self.claw_panel.claw_tip_x_spin.setValue(preset.claw_tip_x)
        self.claw_panel.claw_tip_y_spin.setValue(preset.claw_tip_y)
        self.claw_panel.claw_outer_ctrl1_x_spin.setValue(preset.claw_outer_ctrl1_x)
        self.claw_panel.claw_outer_ctrl1_y_spin.setValue(preset.claw_outer_ctrl1_y)
        self.claw_panel.claw_outer_ctrl2_x_spin.setValue(preset.claw_outer_ctrl2_x)
        self.claw_panel.claw_outer_ctrl2_y_spin.setValue(preset.claw_outer_ctrl2_y)
        self.claw_panel.claw_inner_ctrl1_x_spin.setValue(preset.claw_inner_ctrl1_x)
        self.claw_panel.claw_inner_ctrl1_y_spin.setValue(preset.claw_inner_ctrl1_y)
        self.claw_panel.claw_inner_ctrl2_x_spin.setValue(preset.claw_inner_ctrl2_x)
        self.claw_panel.claw_inner_ctrl2_y_spin.setValue(preset.claw_inner_ctrl2_y)

        self.qr_style_panel.eye_frame_combo.setCurrentText(preset.eye_frame_shape)
        self.qr_style_panel.eye_ball_combo.setCurrentText(preset.eye_ball_shape)
        self.qr_style_panel.qr_color_button.set_color(preset.qr_foreground_color)
        self.qr_style_panel.gradient_enabled_check.setChecked(preset.gradient_enabled)
        self.qr_style_panel.gradient_color_button.set_color(preset.gradient_color)
        self.qr_style_panel.gradient_direction_combo.setCurrentText(preset.gradient_direction)
        self.qr_style_panel.gradient_offset_horizontal_spin.setValue(preset.gradient_offset_horizontal_px)
        self.qr_style_panel.gradient_offset_vertical_spin.setValue(preset.gradient_offset_vertical_px)
        self.qr_style_panel.gradient_offset_diagonal_down_spin.setValue(preset.gradient_offset_diagonal_down_px)
        self.qr_style_panel.gradient_offset_diagonal_up_spin.setValue(preset.gradient_offset_diagonal_up_px)
        self.qr_style_panel.sync_state()

        self.qr_card_panel.qr_background_enabled_check.setChecked(preset.qr_background_enabled)
        self.qr_card_panel.qr_background_color_button.set_color(preset.qr_background_color)
        self.qr_card_panel.qr_background_padding_spin.setValue(preset.qr_background_padding)
        self.qr_card_panel.qr_background_radius_spin.setValue(preset.qr_background_radius)
        self.qr_card_panel.qr_border_width_spin.setValue(preset.qr_border_width)
        self.qr_card_panel.qr_border_color_button.set_color(preset.qr_border_color)

        self._sync_shape_panels()
        self._apply_locked_fields(preset.locked_fields)

    def _sync_shape_panels(self) -> None:
        self.claw_panel.sync_state(self.qr_style_panel.body_shape_combo.currentText() == "claws")

    def _collect_locked_fields(self) -> dict[str, bool]:
        return {
            key: field.is_locked()
            for key, field in self._lock_fields().items()
        }

    def _apply_locked_fields(self, locked_fields: dict[str, bool]) -> None:
        for key, field in self._lock_fields().items():
            field.set_locked(bool(locked_fields.get(key, key in _DEFAULT_LOCKED_FIELDS)))

    def _lock_fields(self) -> dict[str, LockableField]:
        return {
            "link": self.content_panel.link_field,
            "qr_version": self.content_panel.qr_version_field,
            "qr_error_correction": self.content_panel.qr_error_correction_field,
            "qr_mask_pattern": self.content_panel.qr_mask_pattern_field,
            "qr_optimize": self.content_panel.qr_optimize_field,
            "qr_dpi": self.content_panel.qr_dpi_field,
            "qr_scale_percent": self.content_panel.qr_scale_field,
            "qr_offset_x": self.content_panel.qr_offset_x_field,
            "qr_offset_y": self.content_panel.qr_offset_y_field,
            "canvas_width": self.canvas_panel.canvas_width_field,
            "canvas_height": self.canvas_panel.canvas_height_field,
            "canvas_background_color": self.canvas_panel.canvas_bg_color_field,
            "background_image_path": self.background_panel.background_field,
            "background_scale_percent": self.background_panel.background_scale_field,
            "background_offset_x": self.background_panel.background_offset_x_field,
            "background_offset_y": self.background_panel.background_offset_y_field,
            "body_shape": self.qr_style_panel.body_shape_field,
            "rounded_body_radius_px": self.qr_style_panel.rounded_body_radius_field,
            "spikes_single_corner_radius_px": self.qr_style_panel.spikes_single_corner_radius_field,
            "claw_detail_scale": self.claw_panel.claw_detail_scale_field,
            "claw_curve_steps": self.claw_panel.claw_curve_steps_field,
            "claw_alternate_direction": self.claw_panel.claw_alternate_direction_field,
            "claw_lean_right": self.claw_panel.claw_lean_right_field,
            "claw_tip_x": self.claw_panel.claw_tip_x_field,
            "claw_tip_y": self.claw_panel.claw_tip_y_field,
            "claw_outer_ctrl1_x": self.claw_panel.claw_outer_ctrl1_x_field,
            "claw_outer_ctrl1_y": self.claw_panel.claw_outer_ctrl1_y_field,
            "claw_outer_ctrl2_x": self.claw_panel.claw_outer_ctrl2_x_field,
            "claw_outer_ctrl2_y": self.claw_panel.claw_outer_ctrl2_y_field,
            "claw_inner_ctrl1_x": self.claw_panel.claw_inner_ctrl1_x_field,
            "claw_inner_ctrl1_y": self.claw_panel.claw_inner_ctrl1_y_field,
            "claw_inner_ctrl2_x": self.claw_panel.claw_inner_ctrl2_x_field,
            "claw_inner_ctrl2_y": self.claw_panel.claw_inner_ctrl2_y_field,
            "eye_frame_shape": self.qr_style_panel.eye_frame_field,
            "eye_ball_shape": self.qr_style_panel.eye_ball_field,
            "qr_foreground_color": self.qr_style_panel.qr_color_field,
            "gradient_enabled": self.qr_style_panel.gradient_enabled_field,
            "gradient_color": self.qr_style_panel.gradient_color_field,
            "gradient_direction": self.qr_style_panel.gradient_direction_field,
            "gradient_offset_horizontal_px": self.qr_style_panel.gradient_offset_horizontal_field,
            "gradient_offset_vertical_px": self.qr_style_panel.gradient_offset_vertical_field,
            "gradient_offset_diagonal_down_px": self.qr_style_panel.gradient_offset_diagonal_down_field,
            "gradient_offset_diagonal_up_px": self.qr_style_panel.gradient_offset_diagonal_up_field,
            "qr_background_enabled": self.qr_card_panel.qr_background_enabled_field,
            "qr_background_color": self.qr_card_panel.qr_background_color_field,
            "qr_background_padding": self.qr_card_panel.qr_background_padding_field,
            "qr_background_radius": self.qr_card_panel.qr_background_radius_field,
            "qr_border_width": self.qr_card_panel.qr_border_width_field,
            "qr_border_color": self.qr_card_panel.qr_border_color_field,
        }


def _parse_version(value: str) -> int:
    return 0 if value == "auto" else int(value)


def _parse_mask(value: str) -> int:
    return -1 if value == "auto" else int(value)


def _version_text(value: int) -> str:
    return "auto" if value <= 0 else str(value)


def _mask_text(value: int) -> str:
    return "auto" if value < 0 else str(value)
