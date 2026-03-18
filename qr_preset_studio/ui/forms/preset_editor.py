from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QVBoxLayout, QWidget

from qr_preset_studio.domain.models.preset import Preset
from qr_preset_studio.ui.panels.actions_panel import ActionsPanel
from qr_preset_studio.ui.panels.background_panel import BackgroundPanel
from qr_preset_studio.ui.panels.canvas_panel import CanvasPanel
from qr_preset_studio.ui.panels.content_panel import ContentPanel
from qr_preset_studio.ui.panels.qr_card_panel import QrCardPanel
from qr_preset_studio.ui.panels.qr_style_panel import QrStylePanel


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
        self.qr_card_panel = QrCardPanel()
        self.actions_panel = ActionsPanel()

        for panel in [
            self.content_panel,
            self.canvas_panel,
            self.background_panel,
            self.qr_style_panel,
            self.qr_card_panel,
        ]:
            panel.changed.connect(self.changed)
            layout.addWidget(panel)

        layout.addWidget(self.actions_panel)
        layout.addStretch(1)

    def to_preset(self) -> Preset:
        return Preset(
            link=self.content_panel.link_input.text().strip(),
            canvas_width=self.canvas_panel.canvas_width_spin.value(),
            canvas_height=self.canvas_panel.canvas_height_spin.value(),
            canvas_background_color=self.canvas_panel.canvas_bg_color_button.color(),
            background_image_path=self.background_panel.background_path_input.text().strip(),
            qr_scale_percent=self.content_panel.qr_scale_spin.value(),
            qr_offset_x=self.content_panel.qr_offset_x_spin.value(),
            qr_offset_y=self.content_panel.qr_offset_y_spin.value(),
            body_shape=self.qr_style_panel.body_shape_combo.currentText(),
            eye_frame_shape=self.qr_style_panel.eye_frame_combo.currentText(),
            eye_ball_shape=self.qr_style_panel.eye_ball_combo.currentText(),
            qr_foreground_color=self.qr_style_panel.qr_color_button.color(),
            gradient_enabled=self.qr_style_panel.gradient_enabled_check.isChecked(),
            gradient_color=self.qr_style_panel.gradient_color_button.color(),
            gradient_direction=self.qr_style_panel.gradient_direction_combo.currentText(),
            qr_background_enabled=self.qr_card_panel.qr_background_enabled_check.isChecked(),
            qr_background_color=self.qr_card_panel.qr_background_color_button.color(),
            qr_background_padding=self.qr_card_panel.qr_background_padding_spin.value(),
            qr_background_radius=self.qr_card_panel.qr_background_radius_spin.value(),
            qr_border_width=self.qr_card_panel.qr_border_width_spin.value(),
            qr_border_color=self.qr_card_panel.qr_border_color_button.color(),
        )

    def set_preset(self, preset: Preset) -> None:
        self.content_panel.link_input.setText(preset.link)
        self.canvas_panel.canvas_width_spin.setValue(preset.canvas_width)
        self.canvas_panel.canvas_height_spin.setValue(preset.canvas_height)
        self.canvas_panel.canvas_bg_color_button.set_color(preset.canvas_background_color)
        self.background_panel.set_background_path(preset.background_image_path)

        self.content_panel.qr_scale_spin.setValue(preset.qr_scale_percent)
        self.content_panel.qr_offset_x_spin.setValue(preset.qr_offset_x)
        self.content_panel.qr_offset_y_spin.setValue(preset.qr_offset_y)

        self.qr_style_panel.body_shape_combo.setCurrentText(preset.body_shape)
        self.qr_style_panel.eye_frame_combo.setCurrentText(preset.eye_frame_shape)
        self.qr_style_panel.eye_ball_combo.setCurrentText(preset.eye_ball_shape)
        self.qr_style_panel.qr_color_button.set_color(preset.qr_foreground_color)
        self.qr_style_panel.gradient_enabled_check.setChecked(preset.gradient_enabled)
        self.qr_style_panel.gradient_color_button.set_color(preset.gradient_color)
        self.qr_style_panel.gradient_direction_combo.setCurrentText(preset.gradient_direction)

        self.qr_card_panel.qr_background_enabled_check.setChecked(preset.qr_background_enabled)
        self.qr_card_panel.qr_background_color_button.set_color(preset.qr_background_color)
        self.qr_card_panel.qr_background_padding_spin.setValue(preset.qr_background_padding)
        self.qr_card_panel.qr_background_radius_spin.setValue(preset.qr_background_radius)
        self.qr_card_panel.qr_border_width_spin.setValue(preset.qr_border_width)
        self.qr_card_panel.qr_border_color_button.set_color(preset.qr_border_color)
