from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QGroupBox, QPushButton, QVBoxLayout


class ActionsPanel(QGroupBox):
    save_requested = Signal()
    load_requested = Signal()
    export_requested = Signal()

    # templates
    save_template_requested = Signal()
    template_manager_requested = Signal()

    def __init__(self) -> None:
        super().__init__("Действия")
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        save_button = QPushButton("Сохранить пресет")
        save_template_button = QPushButton("Сохранить шаблон")
        load_button = QPushButton("Загрузить пресет")
        export_button = QPushButton("Экспорт PNG")
        templates_button = QPushButton("Открыть Template Manager")

        save_button.clicked.connect(self.save_requested)
        save_template_button.clicked.connect(self.save_template_requested)
        load_button.clicked.connect(self.load_requested)
        export_button.clicked.connect(self.export_requested)
        templates_button.clicked.connect(self.template_manager_requested)

        layout.addWidget(save_button)
        layout.addWidget(save_template_button)
        layout.addWidget(load_button)
        layout.addWidget(export_button)
        layout.addWidget(templates_button)