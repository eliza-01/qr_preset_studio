from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class BackgroundPanel(QGroupBox):
    changed = Signal()
    browse_requested = Signal()
    clear_requested = Signal()

    def __init__(self) -> None:
        super().__init__("Фон")
        form = QFormLayout(self)
        form.setSpacing(10)

        self.background_path_input = QLineEdit()
        self.background_path_input.setReadOnly(True)
        self.browse_button = QPushButton("Выбрать")
        self.clear_button = QPushButton("Сбросить")

        buttons = QHBoxLayout()
        buttons.addWidget(self.browse_button)
        buttons.addWidget(self.clear_button)

        background_widget = QWidget()
        bg_layout = QVBoxLayout(background_widget)
        bg_layout.setContentsMargins(0, 0, 0, 0)
        bg_layout.setSpacing(8)
        bg_layout.addWidget(self.background_path_input)
        bg_layout.addLayout(buttons)

        form.addRow("Изображение", background_widget)

        self.browse_button.clicked.connect(self.browse_requested)
        self.clear_button.clicked.connect(self.clear_requested)
        self.background_path_input.textChanged.connect(self.changed)

    def set_background_path(self, path: str) -> None:
        self.background_path_input.setText(path)
