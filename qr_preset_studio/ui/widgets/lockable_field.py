from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QToolButton, QWidget


class LockableField(QWidget):
    def __init__(self, control: QWidget, parent=None) -> None:
        super().__init__(parent)
        self._control = control
        self._content_enabled = True

        self.lock_button = QToolButton()
        self.lock_button.setCheckable(True)
        self.lock_button.setCursor(Qt.PointingHandCursor)
        self.lock_button.setFixedWidth(34)
        self.lock_button.setStyleSheet(
            "QToolButton {"
            "border: 1px solid #CBD5E1;"
            "border-radius: 8px;"
            "padding: 4px;"
            "background: #FFFFFF;"
            "font-size: 14px;"
            "}"
            "QToolButton:checked {"
            "background: #E2E8F0;"
            "}"
        )

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        layout.addWidget(self._control, 1)
        layout.addWidget(self.lock_button)

        self.lock_button.toggled.connect(self._apply_state)
        self._apply_state()

    def is_locked(self) -> bool:
        return self.lock_button.isChecked()

    def set_locked(self, locked: bool) -> None:
        self.lock_button.setChecked(locked)

    def set_content_enabled(self, enabled: bool) -> None:
        self._content_enabled = enabled
        self._apply_state()

    def _apply_state(self) -> None:
        self._control.setEnabled(self._content_enabled and not self.is_locked())
        self.lock_button.setText("🔒" if self.is_locked() else "🔓")
        self.lock_button.setToolTip(
            "Разблокировать настройку" if self.is_locked() else "Заблокировать настройку"
        )