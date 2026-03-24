from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QToolButton, QVBoxLayout, QWidget


class CollapsibleSection(QWidget):
    def __init__(self, title: str, parent=None) -> None:
        super().__init__(parent)

        self.toggle_button = QToolButton()
        self.toggle_button.setText(title)
        self.toggle_button.setCheckable(True)
        self.toggle_button.setChecked(False)
        self.toggle_button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.toggle_button.setArrowType(Qt.RightArrow)
        self.toggle_button.setStyleSheet(
            "QToolButton {"
            "border: 1px solid #CBD5E1;"
            "border-radius: 10px;"
            "padding: 8px 10px;"
            "background: #FFFFFF;"
            "font-weight: 600;"
            "text-align: left;"
            "}"
            "QToolButton:checked {"
            "background: #F8FAFC;"
            "}"
        )

        self.content_widget = QWidget()
        self.content_widget.setVisible(False)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        layout.addWidget(self.toggle_button)
        layout.addWidget(self.content_widget)

        self.toggle_button.toggled.connect(self._apply_state)
        self._apply_state(False)

    def set_content_layout(self, layout) -> None:
        self.content_widget.setLayout(layout)

    def set_expanded(self, expanded: bool) -> None:
        self.toggle_button.setChecked(expanded)

    def is_expanded(self) -> bool:
        return self.toggle_button.isChecked()

    def _apply_state(self, expanded: bool) -> None:
        self.toggle_button.setArrowType(Qt.DownArrow if expanded else Qt.RightArrow)
        self.content_widget.setVisible(expanded)