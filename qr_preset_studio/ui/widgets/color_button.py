from __future__ import annotations

from PySide6.QtGui import QColor
from PySide6.QtWidgets import QColorDialog, QPushButton


class ColorButton(QPushButton):
    def __init__(self, color: str, title: str, parent=None) -> None:
        super().__init__(parent)
        self._color = color
        self._title = title
        self.clicked.connect(self._choose_color)
        self._apply_view()

    def color(self) -> str:
        return self._color

    def set_color(self, color: str) -> None:
        self._color = color
        self._apply_view()

    def _choose_color(self) -> None:
        selected = QColorDialog.getColor(QColor(self._color), self, self._title)
        if not selected.isValid():
            return
        self._color = selected.name().upper()
        self._apply_view()

    def _apply_view(self) -> None:
        self.setText(self._color.upper())
        self.setStyleSheet(
            "QPushButton {"
            f"background-color: {self._color};"
            "border: 1px solid #94A3B8;"
            "border-radius: 8px;"
            "padding: 8px 10px;"
            "text-align: left;"
            "font-weight: 600;"
            "}"
        )
