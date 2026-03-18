# qr_preset_studio/ui/main_window.py
from __future__ import annotations

from pathlib import Path

from PIL.ImageQt import ImageQt
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QSplitter,
    QVBoxLayout,
    QWidget,
    QCheckBox,
    QComboBox,
)

from qr_preset_studio.core.models import (
    BODY_SHAPES,
    EYE_BALL_SHAPES,
    EYE_FRAME_SHAPES,
    GRADIENT_DIRECTIONS,
    Preset,
)
from qr_preset_studio.core.preset_store import load_preset, save_preset
from qr_preset_studio.core.renderer import render_preview, render_preset
from qr_preset_studio.ui.color_button import ColorButton


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("QR Preset Studio")
        self.resize(1480, 920)
        self._preset = Preset()
        self._presets_dir = Path.home() / "QRPresetStudio" / "presets"
        self._presets_dir.mkdir(parents=True, exist_ok=True)
        self._preview_pixmap: QPixmap | None = None

        self._build_ui()
        self._set_controls_from_preset(self._preset)
        self._bind_events()
        self._refresh_preview()
        self.statusBar().showMessage("Готово")

    def _build_ui(self) -> None:
        root = QWidget()
        layout = QHBoxLayout(root)
        layout.setContentsMargins(12, 12, 12, 12)

        splitter = QSplitter(Qt.Horizontal)
        splitter.setChildrenCollapsible(False)
        layout.addWidget(splitter)

        controls_container = QWidget()
        controls_layout = QVBoxLayout(controls_container)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(12)

        controls_scroll = QScrollArea()
        controls_scroll.setWidgetResizable(True)
        controls_scroll.setWidget(controls_container)
        splitter.addWidget(controls_scroll)

        preview_container = QWidget()
        preview_layout = QVBoxLayout(preview_container)
        preview_layout.setContentsMargins(0, 0, 0, 0)
        preview_layout.setSpacing(12)

        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumSize(700, 700)
        self.preview_label.setStyleSheet(
            "QLabel { background: #E2E8F0; border: 1px solid #CBD5E1; border-radius: 12px; }"
        )

        preview_scroll = QScrollArea()
        preview_scroll.setWidgetResizable(True)
        preview_scroll.setAlignment(Qt.AlignCenter)
        preview_scroll.setWidget(self.preview_label)
        preview_layout.addWidget(preview_scroll)

        preview_hint = QLabel("Превью обновляется автоматически")
        preview_hint.setAlignment(Qt.AlignCenter)
        preview_hint.setStyleSheet("color: #475569;")
        preview_layout.addWidget(preview_hint)
        splitter.addWidget(preview_container)
        splitter.setSizes([480, 980])

        controls_layout.addWidget(self._build_content_group())
        controls_layout.addWidget(self._build_canvas_group())
        controls_layout.addWidget(self._build_background_group())
        controls_layout.addWidget(self._build_qr_style_group())
        controls_layout.addWidget(self._build_qr_card_group())
        controls_layout.addWidget(self._build_actions_group())
        controls_layout.addStretch(1)

        self.setCentralWidget(root)

    def _build_content_group(self) -> QGroupBox:
        group = QGroupBox("QR")
        form = QFormLayout(group)
        form.setSpacing(10)

        self.link_input = QLineEdit()
        self.link_input.setPlaceholderText("https://example.com")
        form.addRow("Ссылка", self.link_input)

        self.qr_scale_spin = self._spin(10, 90, suffix=" %")
        form.addRow("Размер QR", self.qr_scale_spin)

        self.qr_offset_x_spin = self._spin(-5000, 5000, suffix=" px")
        self.qr_offset_y_spin = self._spin(-5000, 5000, suffix=" px")
        form.addRow("Сдвиг X", self.qr_offset_x_spin)
        form.addRow("Сдвиг Y", self.qr_offset_y_spin)
        return group

    def _build_canvas_group(self) -> QGroupBox:
        group = QGroupBox("Итоговое изображение")
        form = QFormLayout(group)
        form.setSpacing(10)

        self.canvas_width_spin = self._spin(256, 8000, suffix=" px")
        self.canvas_height_spin = self._spin(256, 8000, suffix=" px")
        self.canvas_bg_color_button = ColorButton("#F3F4F6", "Цвет фона")

        form.addRow("Ширина", self.canvas_width_spin)
        form.addRow("Высота", self.canvas_height_spin)
        form.addRow("Цвет фона", self.canvas_bg_color_button)
        return group

    def _build_background_group(self) -> QGroupBox:
        group = QGroupBox("Фон")
        form = QFormLayout(group)
        form.setSpacing(10)

        self.background_path_input = QLineEdit()
        self.background_path_input.setReadOnly(True)
        browse_button = QPushButton("Выбрать")
        clear_button = QPushButton("Сбросить")
        buttons = QHBoxLayout()
        buttons.addWidget(browse_button)
        buttons.addWidget(clear_button)
        background_widget = QWidget()
        bg_layout = QVBoxLayout(background_widget)
        bg_layout.setContentsMargins(0, 0, 0, 0)
        bg_layout.setSpacing(8)
        bg_layout.addWidget(self.background_path_input)
        bg_layout.addLayout(buttons)

        browse_button.clicked.connect(self._choose_background)
        clear_button.clicked.connect(self._clear_background)

        form.addRow("Изображение", background_widget)
        return group

    def _build_qr_style_group(self) -> QGroupBox:
        group = QGroupBox("Стиль QR")
        form = QFormLayout(group)
        form.setSpacing(10)

        self.body_shape_combo = self._combo(BODY_SHAPES)
        self.eye_frame_combo = self._combo(EYE_FRAME_SHAPES)
        self.eye_ball_combo = self._combo(EYE_BALL_SHAPES)

        self.qr_color_button = ColorButton("#0F172A", "Основной цвет QR")
        self.gradient_enabled_check = QCheckBox("Включить градиент")
        self.gradient_color_button = ColorButton("#2563EB", "Второй цвет градиента")
        self.gradient_direction_combo = self._combo(GRADIENT_DIRECTIONS)

        form.addRow("Body shape", self.body_shape_combo)
        form.addRow("Eye frame", self.eye_frame_combo)
        form.addRow("Eye ball", self.eye_ball_combo)
        form.addRow("Цвет QR", self.qr_color_button)
        form.addRow("Градиент", self.gradient_enabled_check)
        form.addRow("Второй цвет", self.gradient_color_button)
        form.addRow("Направление", self.gradient_direction_combo)
        return group

    def _build_qr_card_group(self) -> QGroupBox:
        group = QGroupBox("Фон и границы QR")
        form = QFormLayout(group)
        form.setSpacing(10)

        self.qr_background_enabled_check = QCheckBox("Показывать фон QR")
        self.qr_background_color_button = ColorButton("#FFFFFF", "Цвет фона QR")
        self.qr_background_padding_spin = self._spin(0, 500, suffix=" px")
        self.qr_background_radius_spin = self._spin(0, 200, suffix=" px")
        self.qr_border_width_spin = self._spin(0, 50, suffix=" px")
        self.qr_border_color_button = ColorButton("#CBD5E1", "Цвет границы")

        form.addRow("Показ", self.qr_background_enabled_check)
        form.addRow("Цвет", self.qr_background_color_button)
        form.addRow("Отступы", self.qr_background_padding_spin)
        form.addRow("Скругление", self.qr_background_radius_spin)
        form.addRow("Толщина границы", self.qr_border_width_spin)
        form.addRow("Цвет границы", self.qr_border_color_button)
        return group

    def _build_actions_group(self) -> QGroupBox:
        group = QGroupBox("Действия")
        layout = QVBoxLayout(group)
        layout.setSpacing(10)

        save_preset_button = QPushButton("Сохранить пресет")
        load_preset_button = QPushButton("Загрузить пресет")
        export_button = QPushButton("Экспорт PNG")

        save_preset_button.clicked.connect(self._save_preset)
        load_preset_button.clicked.connect(self._load_preset)
        export_button.clicked.connect(self._export_png)

        layout.addWidget(save_preset_button)
        layout.addWidget(load_preset_button)
        layout.addWidget(export_button)
        return group

    def _bind_events(self) -> None:
        widgets = [
            self.link_input,
            self.qr_scale_spin,
            self.qr_offset_x_spin,
            self.qr_offset_y_spin,
            self.canvas_width_spin,
            self.canvas_height_spin,
            self.body_shape_combo,
            self.eye_frame_combo,
            self.eye_ball_combo,
            self.gradient_enabled_check,
            self.gradient_direction_combo,
            self.qr_background_enabled_check,
            self.qr_background_padding_spin,
            self.qr_background_radius_spin,
            self.qr_border_width_spin,
        ]
        for widget in widgets:
            signal = getattr(widget, "textChanged", None) or getattr(widget, "valueChanged", None) or getattr(widget, "currentTextChanged", None) or getattr(widget, "toggled", None)
            if signal is not None:
                signal.connect(self._refresh_preview)

        for button in [
            self.canvas_bg_color_button,
            self.qr_color_button,
            self.gradient_color_button,
            self.qr_background_color_button,
            self.qr_border_color_button,
        ]:
            button.clicked.connect(self._refresh_preview)

    def _refresh_preview(self) -> None:
        self._preset = self._collect_preset_from_controls()
        image = render_preview(self._preset)
        self._preview_pixmap = QPixmap.fromImage(ImageQt(image))
        self.preview_label.setPixmap(self._preview_pixmap)
        self.preview_label.adjustSize()

    def _collect_preset_from_controls(self) -> Preset:
        return Preset(
            link=self.link_input.text().strip(),
            canvas_width=self.canvas_width_spin.value(),
            canvas_height=self.canvas_height_spin.value(),
            canvas_background_color=self.canvas_bg_color_button.color(),
            background_image_path=self.background_path_input.text().strip(),
            qr_scale_percent=self.qr_scale_spin.value(),
            qr_offset_x=self.qr_offset_x_spin.value(),
            qr_offset_y=self.qr_offset_y_spin.value(),
            body_shape=self.body_shape_combo.currentText(),
            eye_frame_shape=self.eye_frame_combo.currentText(),
            eye_ball_shape=self.eye_ball_combo.currentText(),
            qr_foreground_color=self.qr_color_button.color(),
            gradient_enabled=self.gradient_enabled_check.isChecked(),
            gradient_color=self.gradient_color_button.color(),
            gradient_direction=self.gradient_direction_combo.currentText(),
            qr_background_enabled=self.qr_background_enabled_check.isChecked(),
            qr_background_color=self.qr_background_color_button.color(),
            qr_background_padding=self.qr_background_padding_spin.value(),
            qr_background_radius=self.qr_background_radius_spin.value(),
            qr_border_width=self.qr_border_width_spin.value(),
            qr_border_color=self.qr_border_color_button.color(),
        )

    def _set_controls_from_preset(self, preset: Preset) -> None:
        self.link_input.setText(preset.link)
        self.canvas_width_spin.setValue(preset.canvas_width)
        self.canvas_height_spin.setValue(preset.canvas_height)
        self.canvas_bg_color_button.set_color(preset.canvas_background_color)
        self.background_path_input.setText(preset.background_image_path)

        self.qr_scale_spin.setValue(preset.qr_scale_percent)
        self.qr_offset_x_spin.setValue(preset.qr_offset_x)
        self.qr_offset_y_spin.setValue(preset.qr_offset_y)

        self.body_shape_combo.setCurrentText(preset.body_shape)
        self.eye_frame_combo.setCurrentText(preset.eye_frame_shape)
        self.eye_ball_combo.setCurrentText(preset.eye_ball_shape)

        self.qr_color_button.set_color(preset.qr_foreground_color)
        self.gradient_enabled_check.setChecked(preset.gradient_enabled)
        self.gradient_color_button.set_color(preset.gradient_color)
        self.gradient_direction_combo.setCurrentText(preset.gradient_direction)

        self.qr_background_enabled_check.setChecked(preset.qr_background_enabled)
        self.qr_background_color_button.set_color(preset.qr_background_color)
        self.qr_background_padding_spin.setValue(preset.qr_background_padding)
        self.qr_background_radius_spin.setValue(preset.qr_background_radius)
        self.qr_border_width_spin.setValue(preset.qr_border_width)
        self.qr_border_color_button.set_color(preset.qr_border_color)

    def _save_preset(self) -> None:
        preset = self._collect_preset_from_controls()
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить пресет",
            str(self._presets_dir / "preset.json"),
            "JSON (*.json)",
        )
        if not path:
            return
        save_preset(path, preset)
        self.statusBar().showMessage(f"Пресет сохранён: {path}", 4000)

    def _load_preset(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Загрузить пресет",
            str(self._presets_dir),
            "JSON (*.json)",
        )
        if not path:
            return
        preset = load_preset(path)
        self._set_controls_from_preset(preset)
        self._refresh_preview()
        missing_background = preset.background_image_path and not Path(preset.background_image_path).expanduser().is_file()
        if missing_background:
            self.statusBar().showMessage("Пресет загружен, но файл фона не найден", 5000)
            return
        self.statusBar().showMessage(f"Пресет загружен: {path}", 4000)

    def _export_png(self) -> None:
        preset = self._collect_preset_from_controls()
        if not preset.link:
            QMessageBox.warning(self, "Нужна ссылка", "Заполни поле со ссылкой для QR перед экспортом.")
            return
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Экспорт PNG",
            str(Path.home() / "qr_export.png"),
            "PNG (*.png)",
        )
        if not path:
            return
        image = render_preset(preset)
        image.save(path, format="PNG")
        self.statusBar().showMessage(f"PNG сохранён: {path}", 5000)

    def _choose_background(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Выбрать фон",
            str(Path.home()),
            "Изображения (*.png *.jpg *.jpeg *.webp *.bmp)",
        )
        if not path:
            return
        self.background_path_input.setText(path)
        self._refresh_preview()

    def _clear_background(self) -> None:
        self.background_path_input.clear()
        self._refresh_preview()

    @staticmethod
    def _spin(minimum: int, maximum: int, suffix: str = "") -> QSpinBox:
        spin = QSpinBox()
        spin.setRange(minimum, maximum)
        if suffix:
            spin.setSuffix(suffix)
        spin.setSingleStep(1)
        return spin

    @staticmethod
    def _combo(values: list[str]) -> QComboBox:
        combo = QComboBox()
        combo.addItems(values)
        return combo
