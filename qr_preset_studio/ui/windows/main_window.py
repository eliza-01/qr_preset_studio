from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QMainWindow,
    QMessageBox,
    QScrollArea,
    QSplitter,
    QWidget,
)

from qr_preset_studio.application.services.app_state_service import AppStateService
from qr_preset_studio.application.services.preset_service import PresetService
from qr_preset_studio.application.services.render_service import RenderService
from qr_preset_studio.domain.models.preset import Preset
from qr_preset_studio.ui.forms.preset_editor import PresetEditor
from qr_preset_studio.ui.panels.preview_panel import PreviewPanel


class MainWindow(QMainWindow):
    def __init__(
        self,
        preset_service: PresetService,
        render_service: RenderService,
        app_state_service: AppStateService,
    ) -> None:
        super().__init__()
        self._preset_service = preset_service
        self._render_service = render_service
        self._app_state_service = app_state_service
        self._preset = Preset()

        self.setWindowTitle("QR Preset Studio")
        self.resize(1480, 920)

        self._build_ui()
        self._bind_events()
        self._restore_initial_preset()
        self._refresh_preview()
        self.statusBar().showMessage("Готово")

    def _build_ui(self) -> None:
        root = QWidget()
        layout = QHBoxLayout(root)
        layout.setContentsMargins(12, 12, 12, 12)

        splitter = QSplitter(Qt.Horizontal)
        splitter.setChildrenCollapsible(False)
        layout.addWidget(splitter)

        controls_scroll = QScrollArea()
        controls_scroll.setWidgetResizable(True)
        self.editor = PresetEditor()
        controls_scroll.setWidget(self.editor)
        splitter.addWidget(controls_scroll)

        self.preview_panel = PreviewPanel()
        splitter.addWidget(self.preview_panel)
        splitter.setSizes([480, 980])

        self.setCentralWidget(root)

    def _bind_events(self) -> None:
        self.editor.changed.connect(self._refresh_preview)
        self.editor.background_panel.browse_requested.connect(self._choose_background)
        self.editor.background_panel.clear_requested.connect(self._clear_background)
        self.editor.actions_panel.save_requested.connect(self._save_preset)
        self.editor.actions_panel.load_requested.connect(self._load_preset)
        self.editor.actions_panel.export_requested.connect(self._export_png)
        self.preview_panel.zoom_changed.connect(self._refresh_preview)

    def _restore_initial_preset(self) -> None:
        last_path = self._app_state_service.last_preset_path()
        if last_path is None:
            self.editor.set_preset(self._preset)
            return

        try:
            preset = self._preset_service.load(last_path)
        except Exception:
            self._app_state_service.clear_last_preset_path()
            self.editor.set_preset(self._preset)
            return

        self._preset = preset
        self.editor.set_preset(preset)

    def _refresh_preview(self) -> None:
        self._preset = self.editor.to_preset()

        try:
            image = self._render_service.render_preview(self._preset, self.preview_panel.zoom_percent())
        except ValueError as exc:
            error_text = str(exc)
            self.preview_panel.set_error_text(error_text)
            self.statusBar().showMessage(error_text, 7000)
            return
        except Exception as exc:
            error_text = f"Ошибка рендера превью: {exc}"
            self.preview_panel.set_error_text(error_text)
            self.statusBar().showMessage(error_text, 7000)
            return

        self.preview_panel.set_preview_image(image)
        self.statusBar().showMessage("Готово")

    def _save_preset(self) -> None:
        preset = self.editor.to_preset()
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить пресет",
            str(self._preset_service.presets_dir / "preset.json"),
            "JSON (*.json)",
        )
        if not path:
            return

        try:
            self._preset_service.save(path, preset)
            self._app_state_service.set_last_preset_path(path)
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка сохранения", str(exc))
            return

        self.statusBar().showMessage(f"Пресет сохранён: {path}", 4000)

    def _load_preset(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Загрузить пресет",
            str(self._preset_service.presets_dir),
            "JSON (*.json)",
        )
        if not path:
            return

        try:
            preset = self._preset_service.load(path)
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка загрузки", str(exc))
            return

        self._app_state_service.set_last_preset_path(path)
        self.editor.set_preset(preset)
        self._refresh_preview()

        background_path = preset.background_image_path
        if background_path and not Path(background_path).expanduser().is_file():
            self.statusBar().showMessage("Пресет загружен, но файл фона не найден", 5000)
            return

        self.statusBar().showMessage(f"Пресет загружен: {path}", 4000)

    def _export_png(self) -> None:
        preset = self.editor.to_preset()
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

        try:
            image = self._render_service.render_export(preset)
            image.save(path, format="PNG", dpi=(preset.qr_dpi, preset.qr_dpi))
        except ValueError as exc:
            QMessageBox.warning(self, "QR не помещается", str(exc))
            return
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка экспорта", str(exc))
            return

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
        self.editor.background_panel.set_background_path(path)
        self._refresh_preview()

    def _clear_background(self) -> None:
        self.editor.background_panel.set_background_path("")
        self._refresh_preview()