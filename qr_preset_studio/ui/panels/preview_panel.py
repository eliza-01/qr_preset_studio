from __future__ import annotations

from PIL.ImageQt import ImageQt
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QHBoxLayout, QLabel, QScrollArea, QSlider, QVBoxLayout, QWidget


class PreviewPanel(QWidget):
    zoom_changed = Signal(int)

    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        toolbar = QWidget()
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(8, 4, 8, 0)
        toolbar_layout.setSpacing(10)
        toolbar_layout.addWidget(QLabel("Масштаб превью"))

        self.zoom_slider = QSlider(Qt.Horizontal)
        self.zoom_slider.setRange(10, 400)
        self.zoom_slider.setSingleStep(10)
        self.zoom_slider.setPageStep(25)
        self.zoom_slider.setValue(100)
        toolbar_layout.addWidget(self.zoom_slider, 1)

        self.zoom_value_label = QLabel("100%")
        self.zoom_value_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.zoom_value_label.setMinimumWidth(56)
        toolbar_layout.addWidget(self.zoom_value_label)
        layout.addWidget(toolbar)

        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumSize(700, 700)
        self.preview_label.setStyleSheet(
            "QLabel { background: #E2E8F0; border: 1px solid #CBD5E1; border-radius: 12px; }"
        )

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setAlignment(Qt.AlignCenter)
        scroll.setWidget(self.preview_label)
        layout.addWidget(scroll)

        hint = QLabel("Превью обновляется автоматически")
        hint.setAlignment(Qt.AlignCenter)
        hint.setStyleSheet("color: #475569;")
        layout.addWidget(hint)

        self.zoom_slider.valueChanged.connect(self._sync_zoom_label)
        self.zoom_slider.valueChanged.connect(self.zoom_changed)

    def zoom_percent(self) -> int:
        return self.zoom_slider.value()

    def set_preview_image(self, image) -> None:
        pixmap = QPixmap.fromImage(ImageQt(image))
        self.preview_label.setPixmap(pixmap)
        self.preview_label.adjustSize()

    def _sync_zoom_label(self, value: int) -> None:
        self.zoom_value_label.setText(f"{value}%")
