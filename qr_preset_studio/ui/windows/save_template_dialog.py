from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QVBoxLayout,
)

from qr_preset_studio.domain.models.template import CardTemplate


class SaveTemplateDialog(QDialog):
    def __init__(self, templates: list[CardTemplate], parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Сохранить шаблон")
        self.resize(520, 220)

        self._templates = templates

        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(10)

        hint = QLabel(
            "Выбери существующий шаблон для замены front/back\n"
            "или выбери создание нового (укажи slug)."
        )
        hint.setStyleSheet("color: #475569;")
        root.addWidget(hint)

        self.template_combo = QComboBox()
        self.template_combo.addItem("➕ Создать новый шаблон", userData=None)
        for tpl in templates:
            label = f"{tpl.id} | {tpl.slug}".strip()
            self.template_combo.addItem(label, userData=str(tpl.id))

        self.slug_input = QLineEdit()
        self.slug_input.setPlaceholderText("например: minimal_black")

        self.side_combo = QComboBox()
        self.side_combo.addItems(["front", "back"])

        form = QFormLayout()
        form.setSpacing(10)
        form.addRow("Шаблон", self.template_combo)
        form.addRow("Slug (только для нового)", self.slug_input)
        form.addRow("Сторона", self.side_combo)

        root.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._validate_and_accept)
        buttons.rejected.connect(self.reject)
        root.addWidget(buttons)

        self.template_combo.currentIndexChanged.connect(self._sync_state)
        self._sync_state()

    def is_new(self) -> bool:
        return self.template_combo.currentData() is None

    def template_id(self) -> str:
        value = self.template_combo.currentData()
        return "" if value is None else str(value)

    def slug(self) -> str:
        return self.slug_input.text().strip()

    def side(self) -> str:
        return self.side_combo.currentText().strip().lower()

    def _sync_state(self) -> None:
        new_mode = self.is_new()
        self.slug_input.setEnabled(new_mode)
        if not new_mode:
            self.slug_input.setText("")

    def _validate_and_accept(self) -> None:
        side = self.side()
        if side not in {"front", "back"}:
            QMessageBox.warning(self, "Ошибка", "Сторона должна быть front или back.")
            return

        if self.is_new():
            if not self.slug():
                QMessageBox.warning(self, "Нужен slug", "Для нового шаблона укажи slug.")
                return
        else:
            if not self.template_id():
                QMessageBox.warning(self, "Нужен шаблон", "Выбери существующий шаблон.")
                return

        self.accept()