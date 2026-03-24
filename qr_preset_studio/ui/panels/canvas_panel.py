from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from qr_preset_studio.ui.widgets.color_button import ColorButton
from qr_preset_studio.ui.widgets.lockable_field import LockableField


class CanvasPanel(QGroupBox):
    changed = Signal()

    def __init__(self) -> None:
        super().__init__("Итоговое изображение")
        root = QVBoxLayout(self)
        root.setSpacing(10)

        self.canvas_width_spin = _spin(256, 8000, " px")
        self.canvas_height_spin = _spin(256, 8000, " px")
        self.canvas_bg_color_button = ColorButton("#F3F4F6", "Цвет фона")
        self.swap_dimensions_button = QPushButton("⇄")
        self.swap_dimensions_button.setFixedWidth(42)
        self.swap_dimensions_button.setToolTip("Поменять местами ширину и высоту")

        self.canvas_width_field = LockableField(self.canvas_width_spin)
        self.canvas_height_field = LockableField(self.canvas_height_spin)
        self.canvas_bg_color_field = LockableField(self.canvas_bg_color_button)

        form = QFormLayout()
        form.setSpacing(10)
        form.addRow(
            _dimensions_row(
                ("Ширина", self.canvas_width_field),
                ("Высота", self.canvas_height_field),
                self.swap_dimensions_button,
            )
        )
        form.addRow("Цвет фона", self.canvas_bg_color_field)
        root.addLayout(form)

        self.canvas_width_spin.valueChanged.connect(self.changed)
        self.canvas_height_spin.valueChanged.connect(self.changed)
        self.canvas_bg_color_button.clicked.connect(self.changed)
        self.swap_dimensions_button.clicked.connect(self._swap_dimensions)
        self.canvas_width_field.state_changed.connect(self._sync_swap_button_state)
        self.canvas_height_field.state_changed.connect(self._sync_swap_button_state)
        self._sync_swap_button_state()

    def _swap_dimensions(self) -> None:
        if not self.swap_dimensions_button.isEnabled():
            return
        width = self.canvas_width_spin.value()
        height = self.canvas_height_spin.value()
        self.canvas_width_spin.setValue(height)
        self.canvas_height_spin.setValue(width)

    def _sync_swap_button_state(self) -> None:
        self.swap_dimensions_button.setEnabled(
            self.canvas_width_spin.isEnabled() and self.canvas_height_spin.isEnabled()
        )


def _spin(minimum: int, maximum: int, suffix: str = "") -> QSpinBox:
    spin = QSpinBox()
    spin.setRange(minimum, maximum)
    spin.setSingleStep(1)
    if suffix:
        spin.setSuffix(suffix)
    return spin


def _dimensions_row(
    left: tuple[str, QWidget],
    right: tuple[str, QWidget],
    swap_button: QPushButton,
) -> QWidget:
    row = QWidget()
    layout = QHBoxLayout(row)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(10)
    layout.addWidget(_field_column(*left), 1)
    layout.addWidget(_field_column(*right), 1)
    layout.addWidget(_swap_column(swap_button))
    return row


def _field_column(title: str, control: QWidget) -> QWidget:
    column = QWidget()
    layout = QVBoxLayout(column)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(6)
    layout.addWidget(QLabel(title))
    layout.addWidget(control)
    return column


def _swap_column(button: QPushButton) -> QWidget:
    column = QWidget()
    layout = QVBoxLayout(column)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(6)
    layout.addWidget(QLabel("Инверсия"))
    layout.addWidget(button)
    layout.addStretch(1)
    return column