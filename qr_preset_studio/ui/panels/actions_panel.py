# qr_preset_studio/ui/panels/actions_panel.py
from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QComboBox, QGroupBox, QLabel, QPushButton, QVBoxLayout

from qr_preset_studio.domain.models.output_profile import OutputProfile


class ActionsPanel(QGroupBox):
    save_requested = Signal()
    load_requested = Signal()
    export_requested = Signal()
    output_profile_changed = Signal(str)

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
        export_button = QPushButton("Экспорт файла")
        templates_button = QPushButton("Открыть Template Manager")
        self.output_profile_combo = QComboBox()
        self.output_profile_combo.currentIndexChanged.connect(self._emit_output_profile_changed)
        self.output_profile_combo.currentIndexChanged.connect(self._update_output_profile_tooltip)

        save_button.clicked.connect(self.save_requested)
        save_template_button.clicked.connect(self.save_template_requested)
        load_button.clicked.connect(self.load_requested)
        export_button.clicked.connect(self.export_requested)
        templates_button.clicked.connect(self.template_manager_requested)

        layout.addWidget(save_button)
        layout.addWidget(save_template_button)
        layout.addWidget(load_button)
        layout.addWidget(QLabel("Профиль сохранения"))
        layout.addWidget(self.output_profile_combo)
        layout.addWidget(export_button)
        layout.addWidget(templates_button)

    def set_output_profiles(self, profiles: list[OutputProfile]) -> None:
        current_id = self.current_output_profile_id()
        self.output_profile_combo.blockSignals(True)
        self.output_profile_combo.clear()
        for profile in profiles:
            self.output_profile_combo.addItem(profile.label, profile.id)
            self.output_profile_combo.setItemData(
                self.output_profile_combo.count() - 1,
                profile.description,
                role=3,
            )
        self.output_profile_combo.blockSignals(False)
        self.set_output_profile_id(current_id)
        self._update_output_profile_tooltip()

    def set_output_profile_id(self, profile_id: str) -> None:
        wanted = (profile_id or "").strip()
        if not wanted:
            if self.output_profile_combo.count() > 0:
                self.output_profile_combo.setCurrentIndex(0)
            return

        for index in range(self.output_profile_combo.count()):
            if str(self.output_profile_combo.itemData(index) or "") == wanted:
                self.output_profile_combo.setCurrentIndex(index)
                return

        if self.output_profile_combo.count() > 0:
            self.output_profile_combo.setCurrentIndex(0)

    def current_output_profile_id(self) -> str:
        data = self.output_profile_combo.currentData()
        return "" if data is None else str(data)

    def _emit_output_profile_changed(self) -> None:
        self.output_profile_changed.emit(self.current_output_profile_id())

    def _update_output_profile_tooltip(self) -> None:
        index = self.output_profile_combo.currentIndex()
        if index < 0:
            self.output_profile_combo.setToolTip("")
            return
        description = self.output_profile_combo.itemData(index, role=3)
        self.output_profile_combo.setToolTip("" if description is None else str(description))
