# qr_preset_studio/bootstrap.py
from __future__ import annotations

from PySide6.QtWidgets import QApplication

from qr_preset_studio.application.services.app_state_service import AppStateService
from qr_preset_studio.application.services.output_profile_service import OutputProfileService
from qr_preset_studio.application.services.print_batch_service import PrintBatchService
from qr_preset_studio.application.services.preset_service import PresetService
from qr_preset_studio.application.services.render_service import RenderService
from qr_preset_studio.application.services.swyp_card_assignment_service import SwypCardAssignmentService
from qr_preset_studio.application.services.template_service import TemplateService
from qr_preset_studio.infrastructure.database.mysql_session import MySqlSessionFactory, MySqlSettings
from qr_preset_studio.infrastructure.paths import AppPaths
from qr_preset_studio.infrastructure.persistence.json_app_state_repository import JsonAppStateRepository
from qr_preset_studio.infrastructure.persistence.json_preset_repository import JsonPresetRepository
from qr_preset_studio.infrastructure.persistence.mysql_swyp_card_repository import MySqlSwypCardRepository
from qr_preset_studio.infrastructure.persistence.mysql_template_repository import MySqlTemplateRepository
from qr_preset_studio.ui.windows.main_window import MainWindow


def run() -> int:
    app = QApplication([])
    app.setApplicationName("QR Preset Studio")

    paths = AppPaths.default()
    preset_repository = JsonPresetRepository()
    app_state_repository = JsonAppStateRepository()

    # MySQL templates
    mysql_settings = MySqlSettings.default_from_env()
    mysql_session_factory = MySqlSessionFactory(mysql_settings)
    template_repository = MySqlTemplateRepository(mysql_session_factory, table="swyp_cards_templates")
    swyp_card_repository = MySqlSwypCardRepository(mysql_session_factory, table="swyp_cards")

    preset_service = PresetService(repository=preset_repository, presets_dir=paths.presets_dir)
    template_service = TemplateService(repository=template_repository, cache_dir=paths.templates_cache_dir)
    swyp_card_assignment_service = SwypCardAssignmentService(repository=swyp_card_repository)
    app_state_service = AppStateService(repository=app_state_repository, state_file=paths.app_state_file)
    output_profile_service = OutputProfileService()
    render_service = RenderService()
    print_batch_service = PrintBatchService(
        render_service=render_service,
        output_profile_service=output_profile_service,
        print_batches_dir=paths.print_batches_dir,
    )

    window = MainWindow(
        preset_service=preset_service,
        render_service=render_service,
        app_state_service=app_state_service,
        template_service=template_service,
        swyp_card_assignment_service=swyp_card_assignment_service,
        output_profile_service=output_profile_service,
        print_batch_service=print_batch_service,
    )
    window.show()
    return app.exec()
