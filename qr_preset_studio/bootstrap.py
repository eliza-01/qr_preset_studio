from __future__ import annotations

from PySide6.QtWidgets import QApplication

from qr_preset_studio.application.services.app_state_service import AppStateService
from qr_preset_studio.application.services.preset_service import PresetService
from qr_preset_studio.application.services.render_service import RenderService
from qr_preset_studio.infrastructure.paths import AppPaths
from qr_preset_studio.infrastructure.persistence.json_app_state_repository import JsonAppStateRepository
from qr_preset_studio.infrastructure.persistence.json_preset_repository import JsonPresetRepository
from qr_preset_studio.ui.windows.main_window import MainWindow


def run() -> int:
    app = QApplication([])
    app.setApplicationName("QR Preset Studio")

    paths = AppPaths.default()
    preset_repository = JsonPresetRepository()
    app_state_repository = JsonAppStateRepository()

    preset_service = PresetService(repository=preset_repository, presets_dir=paths.presets_dir)
    app_state_service = AppStateService(repository=app_state_repository, state_file=paths.app_state_file)
    render_service = RenderService()

    window = MainWindow(
        preset_service=preset_service,
        render_service=render_service,
        app_state_service=app_state_service,
    )
    window.show()
    return app.exec()