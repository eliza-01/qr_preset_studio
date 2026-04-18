# qr_preset_studio/ui/windows/main_window.py
from __future__ import annotations

import base64
import io
import sys
from pathlib import Path

from PySide6.QtCore import QProcess, Qt
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from qr_preset_studio.application.services.app_state_service import AppStateService
from qr_preset_studio.application.services.output_profile_service import OutputProfileService
from qr_preset_studio.application.services.print_batch_service import PrintBatchService
from qr_preset_studio.application.services.preset_service import PresetService
from qr_preset_studio.application.services.render_service import RenderService
from qr_preset_studio.application.services.swyp_card_assignment_service import SwypCardAssignmentService
from qr_preset_studio.application.services.template_service import TemplateService
from qr_preset_studio.domain.models.preset import Preset
from qr_preset_studio.ui.forms.preset_editor import PresetEditor
from qr_preset_studio.ui.panels.preview_panel import PreviewPanel
from qr_preset_studio.ui.windows.save_template_dialog import SaveTemplateDialog
from qr_preset_studio.ui.windows.template_manager_window import TemplateManagerWindow


class MainWindow(QMainWindow):
    def __init__(
        self,
        preset_service: PresetService,
        render_service: RenderService,
        app_state_service: AppStateService,
        template_service: TemplateService,
        swyp_card_assignment_service: SwypCardAssignmentService,
        output_profile_service: OutputProfileService,
        print_batch_service: PrintBatchService,
    ) -> None:
        super().__init__()
        self._preset_service = preset_service
        self._render_service = render_service
        self._app_state_service = app_state_service
        self._template_service = template_service
        self._swyp_card_assignment_service = swyp_card_assignment_service
        self._output_profile_service = output_profile_service
        self._print_batch_service = print_batch_service

        self._preset = Preset()
        self._template_manager: TemplateManagerWindow | None = None

        self.setWindowTitle("QR Preset Studio")
        self.resize(1480, 920)

        self._build_ui()
        self._bind_events()
        self._restore_initial_preset()
        self._refresh_preview()
        self.statusBar().showMessage("Готово")

    def _build_ui(self) -> None:
        root = QWidget()
        layout = QVBoxLayout(root)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        splitter = QSplitter(Qt.Horizontal)
        splitter.setChildrenCollapsible(False)
        layout.addWidget(splitter, 1)

        controls_scroll = QScrollArea()
        controls_scroll.setWidgetResizable(True)
        self.editor = PresetEditor()
        controls_scroll.setWidget(self.editor)
        splitter.addWidget(controls_scroll)

        self.preview_panel = PreviewPanel()
        splitter.addWidget(self.preview_panel)
        splitter.setSizes([480, 980])
        self.editor.actions_panel.set_output_profiles(self._output_profile_service.list_all())

        footer = QHBoxLayout()
        footer.addStretch(1)

        self.restart_button = QPushButton("Перезапустить приложение")
        self.restart_button.setFixedHeight(36)
        footer.addWidget(self.restart_button)

        layout.addLayout(footer)

        self.setCentralWidget(root)

    def _bind_events(self) -> None:
        self.editor.changed.connect(self._refresh_preview)
        self.editor.background_panel.browse_requested.connect(self._choose_background)
        self.editor.background_panel.clear_requested.connect(self._clear_background)

        self.editor.actions_panel.save_requested.connect(self._save_preset)
        self.editor.actions_panel.load_requested.connect(self._load_preset)
        self.editor.actions_panel.export_requested.connect(self._export_png)
        self.editor.actions_panel.output_profile_changed.connect(self._on_output_profile_changed)

        self.editor.actions_panel.save_template_requested.connect(self._save_template_to_db)
        self.editor.actions_panel.template_manager_requested.connect(self._open_template_manager)

        self.preview_panel.zoom_changed.connect(self._refresh_preview)
        self.restart_button.clicked.connect(self._restart_application)

    def _open_template_manager(self) -> None:
        if self._template_manager is None:
            self._template_manager = TemplateManagerWindow(
                self._template_service,
                self._swyp_card_assignment_service,
                self._print_batch_service,
                self._output_profile_service,
                self.current_output_profile_id(),
            )
        else:
            self._template_manager.set_output_profile_id(self.current_output_profile_id())

        self._template_manager.reload()
        self._template_manager.show()
        self._template_manager.raise_()
        self._template_manager.activateWindow()

    def _save_template_to_db(self) -> None:
        preset = self.editor.to_preset()
        payload = preset.to_dict()

        # preview as data URI PNG (temporary until asset server is wired)
        try:
            preview_image = self._render_service.render_preview(preset, 100)
            preview_uri = _png_data_uri(preview_image)
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка превью", str(exc))
            return

        # load current templates list to choose existing/create new
        try:
            templates = self._template_service.list_all()
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка БД", str(exc))
            return

        dlg = SaveTemplateDialog(templates, parent=self)
        if dlg.exec() != int(QDialog.DialogCode.Accepted):
            return

        try:
            if dlg.is_new():
                created = self._template_service.create_new(
                    slug=dlg.slug(),
                    side=dlg.side(),
                    payload=payload,
                    preview=preview_uri,
                    assets={},
                )
                self.statusBar().showMessage(f"Шаблон создан: id={created.id}, slug={created.slug}", 5000)
            else:
                self._template_service.update_existing_side(
                    template_id=dlg.template_id(),
                    side=dlg.side(),
                    payload=payload,
                    preview=preview_uri,
                )
                self.statusBar().showMessage(
                    f"Шаблон обновлён: id={dlg.template_id()} ({dlg.side()})",
                    5000,
                )
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка сохранения шаблона", str(exc))
            return

        if self._template_manager is not None:
            self._template_manager.reload()

    def _restore_initial_preset(self) -> None:
        last_path = self._app_state_service.last_preset_path()
        if last_path is None:
            self.editor.set_preset(self._preset)
            self._restore_output_profile()
            return

        try:
            preset = self._preset_service.load(last_path)
        except Exception:
            self._app_state_service.clear_last_preset_path()
            self.editor.set_preset(self._preset)
            self._restore_output_profile()
            return

        self._preset = preset
        self.editor.set_preset(preset)
        self._restore_output_profile()

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
        self._restore_output_profile()
        self._refresh_preview()

        background_path = preset.background_image_path
        if background_path and not Path(background_path).expanduser().is_file():
            self.statusBar().showMessage("Пресет загружен, но файл фона не найден", 5000)
            return

        self.statusBar().showMessage(f"Пресет загружен: {path}", 4000)

    def _export_png(self) -> None:
        preset = self.editor.to_preset()
        if not preset.hide_qr and not preset.link:
            QMessageBox.warning(self, "Нужна ссылка", "Заполни поле со ссылкой для QR перед экспортом.")
            return

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Экспорт файла",
            str(Path.home() / self._default_export_filename()),
            self._export_file_filter(),
        )
        if not path:
            return

        try:
            image = self._render_service.render_export(preset)
            profile = self._output_profile_service.get(self.current_output_profile_id())
            export_path = Path(path)
            if export_path.suffix.lower() != profile.file_extension.lower():
                export_path = export_path.with_suffix(profile.file_extension)
            self._render_service.save_rendered_image(image, export_path, profile)
        except ValueError as exc:
            QMessageBox.warning(self, "QR не помещается", str(exc))
            return
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка экспорта", str(exc))
            return

        self.statusBar().showMessage(
            f"Файл сохранён: {export_path} ({profile.file_format}, {profile.color_mode}, {profile.dpi} dpi)",
            5000,
        )

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

    def _restart_application(self) -> None:
        program = sys.executable
        arguments = sys.argv[:]
        working_directory = str(Path.cwd())

        restarted = QProcess.startDetached(program, arguments, working_directory)
        if not restarted:
            QMessageBox.critical(self, "Ошибка перезапуска", "Не удалось запустить новый экземпляр приложения.")
            return

        self.close()

    def current_output_profile_id(self) -> str:
        return self.editor.actions_panel.current_output_profile_id()

    def _default_export_filename(self) -> str:
        profile = self._output_profile_service.get(self.current_output_profile_id())
        return f"qr_export{profile.file_extension}"

    def _export_file_filter(self) -> str:
        profile = self._output_profile_service.get(self.current_output_profile_id())
        extension = profile.file_extension.lstrip(".").upper()
        return f"{extension} (*{profile.file_extension})"

    def _restore_output_profile(self) -> None:
        stored = self._app_state_service.output_profile_id().strip()
        fallback = self._output_profile_service.default_profile_id()
        profile_id = stored or fallback
        self.editor.actions_panel.set_output_profile_id(profile_id)
        self._app_state_service.set_output_profile_id(self.current_output_profile_id())

    def _on_output_profile_changed(self, profile_id: str) -> None:
        self._app_state_service.set_output_profile_id(profile_id)
        if self._template_manager is not None:
            self._template_manager.set_output_profile_id(profile_id)


def _png_data_uri(pil_image) -> str:
    buf = io.BytesIO()
    pil_image.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")
    return f"data:image/png;base64,{b64}"
