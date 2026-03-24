from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from qr_preset_studio.ui.widgets.collapsible_section import CollapsibleSection
from qr_preset_studio.ui.widgets.lockable_field import LockableField


class BackgroundPanel(QWidget):
    changed = Signal()
    browse_requested = Signal()
    clear_requested = Signal()

    def __init__(self) -> None:
        super().__init__()

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.section = CollapsibleSection("Фон")
        root.addWidget(self.section)

        self.background_path_input = QLineEdit()
        self.background_path_input.setReadOnly(True)
        self.browse_button = QPushButton("Выбрать")
        self.clear_button = QPushButton("Сбросить")

        buttons = QHBoxLayout()
        buttons.setContentsMargins(0, 0, 0, 0)
        buttons.setSpacing(8)
        buttons.addWidget(self.browse_button)
        buttons.addWidget(self.clear_button)

        background_widget = QWidget()
        bg_layout = QVBoxLayout(background_widget)
        bg_layout.setContentsMargins(0, 0, 0, 0)
        bg_layout.setSpacing(8)
        bg_layout.addWidget(self.background_path_input)
        bg_layout.addLayout(buttons)

        self.background_field = LockableField(background_widget)

        content = QWidget()
        form = QFormLayout(content)
        form.setSpacing(10)
        form.addRow("Изображение", self.background_field)

        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.addWidget(content)
        self.section.set_content_layout(content_layout)
        self.section.set_expanded(False)

        self.browse_button.clicked.connect(self.browse_requested)
        self.clear_button.clicked.connect(self.clear_requested)
        self.background_path_input.textChanged.connect(self.changed)

    def set_background_path(self, path: str) -> None:
        self.background_path_input.setText(path)