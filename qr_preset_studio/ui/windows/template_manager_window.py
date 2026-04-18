# qr_preset_studio/ui/windows/template_manager_window.py
from __future__ import annotations

import base64
import hashlib
from pathlib import Path

from PySide6.QtCore import Signal, Qt, QSize, QUrl
from PySide6.QtGui import QAction, QIcon, QPixmap, QResizeEvent, QWheelEvent
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest
from PySide6.QtWidgets import (
    QBoxLayout,
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QToolBar,
    QVBoxLayout,
    QWidget,
    QHeaderView,
    QScrollArea,
)

from qr_preset_studio.application.services.swyp_card_assignment_service import SwypCardAssignmentService
from qr_preset_studio.application.services.template_service import TemplateService
from qr_preset_studio.domain.models.swyp_card import SwypCard
from qr_preset_studio.domain.models.template import CardTemplate


_THUMB_SIZE = QSize(220, 140)
_VIEW_SIZE = QSize(900, 600)
_ZOOM_MIN = 0.25
_ZOOM_MAX = 5.0
_ZOOM_STEP = 1.15


def _is_url(value: str) -> bool:
    v = (value or "").strip().lower()
    return v.startswith("http://") or v.startswith("https://")


def _is_data_uri(value: str) -> bool:
    v = (value or "").strip().lower()
    return v.startswith("data:image/") and "," in v


def _pixmap_from_data_uri(value: str) -> QPixmap | None:
    if not _is_data_uri(value):
        return None
    try:
        header, b64 = value.split(",", 1)
        _ = header  # not used now
        data = base64.b64decode(b64, validate=False)
    except Exception:
        return None

    pix = QPixmap()
    if not pix.loadFromData(data):
        return None
    return pix


def _safe_suffix_from_url(url: QUrl) -> str:
    suffix = Path(url.path()).suffix.lower()
    if suffix in {".png", ".jpg", ".jpeg", ".webp", ".bmp"}:
        return suffix
    return ".png"


class TemplatePreviewDialog(QDialog):
    def __init__(self, *, title: str, cache_dir: Path, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(_VIEW_SIZE)

        self._cache_dir = cache_dir
        self._cache_dir.mkdir(parents=True, exist_ok=True)

        self._net = QNetworkAccessManager(self)
        self._pending: dict[QNetworkReply, tuple[ZoomablePreviewArea, Path]] = {}

        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(10)

        top_bar = QHBoxLayout()
        header = QLabel(title)
        header.setStyleSheet("font-weight: 700; font-size: 16px;")
        top_bar.addWidget(header, 1)

        self._mode_btn = QPushButton("Вид: Горизонтальный")
        self._mode_btn.setFixedWidth(180)
        self._mode_btn.clicked.connect(self._toggle_view_mode)
        top_bar.addWidget(self._mode_btn)

        root.addLayout(top_bar)

        content = QWidget()
        self._content_layout = QBoxLayout(QBoxLayout.LeftToRight, content)
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.setSpacing(12)

        self.front_label = self._image_panel("Front")
        self.back_label = self._image_panel("Back")

        self._content_layout.addWidget(self.front_label, 1)
        self._content_layout.addWidget(self.back_label, 1)

        root.addWidget(content, 1)

        hint = QLabel("Клик по строке в менеджере открывает увеличенный просмотр.")
        hint.setStyleSheet("color: #475569;")
        root.addWidget(hint)

    def _toggle_view_mode(self) -> None:
        if self._content_layout.direction() == QBoxLayout.LeftToRight:
            self._content_layout.setDirection(QBoxLayout.TopToBottom)
            self._mode_btn.setText("Вид: Вертикальный")
        else:
            self._content_layout.setDirection(QBoxLayout.LeftToRight)
            self._mode_btn.setText("Вид: Горизонтальный")

    def set_images(self, front_source: str, back_source: str) -> None:
        self._set_image(self.front_label, front_source)
        self._set_image(self.back_label, back_source)

    def _image_panel(self, title: str) -> "ZoomablePreviewArea":
        panel = ZoomablePreviewArea(title)
        panel.setMinimumSize(420, 320)
        return panel

    def _apply_pixmap(self, target: "ZoomablePreviewArea", pixmap: QPixmap) -> None:
        if pixmap.isNull():
            target.set_message("Превью не удалось загрузить")
            return
        target.set_pixmap(pixmap)

    def _set_image(self, target: "ZoomablePreviewArea", source: str) -> None:
        src = (source or "").strip()
        if not src:
            target.set_message("(нет превью)")
            return

        data_pix = _pixmap_from_data_uri(src)
        if data_pix is not None:
            self._apply_pixmap(target, data_pix)
            return

        if _is_url(src):
            url = QUrl(src)
            cache_path = self._cache_path_for_url(url)
            if cache_path.is_file():
                self._apply_pixmap(target, QPixmap(str(cache_path)))
                return

            target.set_message("Загрузка превью...")
            req = QNetworkRequest(url)
            reply = self._net.get(req)
            self._pending[reply] = (target, cache_path)
            reply.finished.connect(lambda r=reply: self._on_download_finished(r))
            return

        path = Path(src).expanduser()
        if path.is_file():
            self._apply_pixmap(target, QPixmap(str(path)))
            return

        target.set_message("Превью не найдено")

    def _cache_path_for_url(self, url: QUrl) -> Path:
        digest = hashlib.sha256(url.toString().encode("utf-8")).hexdigest()
        suffix = _safe_suffix_from_url(url)
        return self._cache_dir / f"{digest}{suffix}"

    def _on_download_finished(self, reply: QNetworkReply) -> None:
        try:
            target, cache_path = self._pending.pop(reply)
        except KeyError:
            reply.deleteLater()
            return

        try:
            if reply.error() != QNetworkReply.NetworkError.NoError:
                target.set_message(f"Ошибка загрузки: {reply.errorString()}")
                return

            data = bytes(reply.readAll())
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            cache_path.write_bytes(data)

            pixmap = QPixmap()
            pixmap.loadFromData(data)
            self._apply_pixmap(target, pixmap)
        finally:
            reply.deleteLater()


class ZoomablePreviewArea(QScrollArea):
    def __init__(self, title: str, parent=None) -> None:
        super().__init__(parent)
        self._title = title
        self._base_pixmap: QPixmap | None = None
        self._zoom = 1.0

        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet(
            "QScrollArea { background: #E2E8F0; border: 1px solid #CBD5E1; border-radius: 12px; }"
        )

        self._label = QLabel()
        self._label.setAlignment(Qt.AlignCenter)
        self._label.setWordWrap(True)
        self._label.setStyleSheet("background: transparent; border: 0; padding: 10px;")
        self.setWidget(self._label)
        self.set_message("(нет превью)")

    def set_message(self, text: str) -> None:
        self._base_pixmap = None
        self._zoom = 1.0
        self._label.clear()
        self._label.setText(f"{self._title}\n{text}")
        self._label.adjustSize()
        self._center_on_content()

    def set_pixmap(self, pixmap: QPixmap) -> None:
        self._base_pixmap = pixmap
        self._zoom = 1.0
        self._update_scaled_pixmap()

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        if self._base_pixmap is not None:
            self._update_scaled_pixmap()

    def wheelEvent(self, event: QWheelEvent) -> None:
        if (
            self._base_pixmap is not None
            and event.modifiers() & Qt.ControlModifier
            and event.angleDelta().y() != 0
        ):
            steps = event.angleDelta().y() / 120
            factor = _ZOOM_STEP ** steps
            self._set_zoom(self._zoom * factor)
            event.accept()
            return
        super().wheelEvent(event)

    def _set_zoom(self, zoom: float) -> None:
        if self._base_pixmap is None:
            return
        bounded_zoom = max(_ZOOM_MIN, min(_ZOOM_MAX, zoom))
        if abs(bounded_zoom - self._zoom) < 1e-6:
            return
        self._zoom = bounded_zoom
        self._update_scaled_pixmap()

    def _update_scaled_pixmap(self) -> None:
        if self._base_pixmap is None:
            return

        fit_scale = self._fit_scale()
        scale = fit_scale * self._zoom
        width = max(1, int(round(self._base_pixmap.width() * scale)))
        height = max(1, int(round(self._base_pixmap.height() * scale)))
        scaled = self._base_pixmap.scaled(
            width,
            height,
            Qt.IgnoreAspectRatio,
            Qt.SmoothTransformation,
        )
        self._label.clear()
        self._label.setPixmap(scaled)
        self._label.adjustSize()
        self._center_on_content()

    def _fit_scale(self) -> float:
        if self._base_pixmap is None:
            return 1.0

        viewport_size = self.viewport().size()
        available_width = max(1, viewport_size.width() - 20)
        available_height = max(1, viewport_size.height() - 20)
        width_scale = available_width / max(1, self._base_pixmap.width())
        height_scale = available_height / max(1, self._base_pixmap.height())
        return min(width_scale, height_scale, 1.0)

    def _center_on_content(self) -> None:
        hbar = self.horizontalScrollBar()
        vbar = self.verticalScrollBar()
        hbar.setValue(hbar.maximum() // 2)
        vbar.setValue(vbar.maximum() // 2)


class SelectableCardListItem(QWidget):
    checked_changed = Signal()

    def __init__(self, card: SwypCard, parent=None) -> None:
        super().__init__(parent)
        self.card = card

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(10)

        self.checkbox = QCheckBox()
        self.checkbox.stateChanged.connect(lambda _state: self.checked_changed.emit())
        layout.addWidget(self.checkbox, 0, Qt.AlignTop)

        order_id = card.order_id or "NULL"
        text = QLabel(f"id: {card.id} | order_id: {order_id} | slug: {card.slug}")
        text.setWordWrap(True)
        layout.addWidget(text, 1)

    def is_checked(self) -> bool:
        return self.checkbox.isChecked()

    def set_checked(self, checked: bool) -> None:
        self.checkbox.setChecked(checked)


class AssignTemplateDialog(QDialog):
    def __init__(
        self,
        *,
        template: CardTemplate,
        template_service: TemplateService,
        swyp_card_assignment_service: SwypCardAssignmentService,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._template = template
        self._template_service = template_service
        self._swyp_card_assignment_service = swyp_card_assignment_service
        self._selection_sync_locked = False

        self.setWindowTitle("Присвоить шаблон")
        self.resize(880, 720)

        self._net = QNetworkAccessManager(self)
        self._pending: dict[QNetworkReply, tuple[QLabel, Path]] = {}

        self._build_ui()
        self._load_previews()
        self._load_cards()

    def selected_card_ids(self) -> list[str]:
        ids: list[str] = []
        for index in range(self.cards_list.count()):
            item = self.cards_list.item(index)
            widget = self.cards_list.itemWidget(item)
            if isinstance(widget, SelectableCardListItem) and widget.is_checked():
                ids.append(widget.card.id)
        return ids

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(12)

        preview_row = QHBoxLayout()
        preview_row.setSpacing(12)

        self.front_preview = self._create_preview_label("Front")
        self.back_preview = self._create_preview_label("Back")
        preview_row.addWidget(self.front_preview, 1)
        preview_row.addWidget(self.back_preview, 1)
        root.addLayout(preview_row)

        slug_label = QLabel(f"slug: {self._template.slug or '—'} | id: {self._template.id or '—'}")
        slug_label.setStyleSheet("font-weight: 600;")
        root.addWidget(slug_label)

        form = QFormLayout()
        form.setContentsMargins(0, 0, 0, 0)
        form.setSpacing(8)

        self.count_input = QSpinBox()
        self.count_input.setMinimum(0)
        self.count_input.valueChanged.connect(self._apply_count_selection)
        form.addRow("Количество визиток", self.count_input)
        root.addLayout(form)

        hint = QLabel("Список берётся из swyp_cards, где template_id IS NULL. Можно менять выбор вручную.")
        hint.setStyleSheet("color: #475569;")
        root.addWidget(hint)

        self.cards_list = QListWidget()
        self.cards_list.setAlternatingRowColors(True)
        root.addWidget(self.cards_list, 1)

        buttons = QDialogButtonBox(QDialogButtonBox.Cancel)
        self.assign_button = buttons.addButton("Присвоить", QDialogButtonBox.AcceptRole)
        self.assign_button.clicked.connect(self._assign)
        buttons.rejected.connect(self.reject)
        root.addWidget(buttons)

    def _create_preview_label(self, title: str) -> QLabel:
        label = QLabel(f"{title}\n(нет превью)")
        label.setAlignment(Qt.AlignCenter)
        label.setMinimumSize(220, 160)
        label.setStyleSheet(
            "background: #E2E8F0; border: 1px solid #CBD5E1; border-radius: 12px; padding: 10px;"
        )
        return label

    def _load_previews(self) -> None:
        self._set_preview(self.front_preview, self._template.front_preview, "Front")
        self._set_preview(self.back_preview, self._template.back_preview, "Back")

    def _load_cards(self) -> None:
        self.cards_list.clear()

        try:
            cards = self._swyp_card_assignment_service.list_unassigned()
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка загрузки swyp_cards", str(exc))
            self.assign_button.setEnabled(False)
            self.count_input.setMaximum(0)
            self.count_input.setValue(0)
            return

        self.count_input.blockSignals(True)
        self.count_input.setMaximum(len(cards))
        self.count_input.setValue(0)
        self.count_input.blockSignals(False)

        for card in cards:
            item = QListWidgetItem()
            item.setSizeHint(QSize(100, 48))
            self.cards_list.addItem(item)

            widget = SelectableCardListItem(card, self.cards_list)
            widget.checked_changed.connect(self._sync_count_from_selection)
            self.cards_list.setItemWidget(item, widget)

        self._refresh_assign_button_state()

    def _apply_count_selection(self, value: int) -> None:
        if self._selection_sync_locked:
            return

        self._selection_sync_locked = True
        try:
            for index in range(self.cards_list.count()):
                item = self.cards_list.item(index)
                widget = self.cards_list.itemWidget(item)
                if isinstance(widget, SelectableCardListItem):
                    widget.set_checked(index < value)
        finally:
            self._selection_sync_locked = False

        self._refresh_assign_button_state()

    def _sync_count_from_selection(self) -> None:
        if self._selection_sync_locked:
            return

        selected_count = len(self.selected_card_ids())
        self._selection_sync_locked = True
        try:
            self.count_input.blockSignals(True)
            self.count_input.setValue(selected_count)
            self.count_input.blockSignals(False)
        finally:
            self._selection_sync_locked = False

        self._refresh_assign_button_state()

    def _refresh_assign_button_state(self) -> None:
        self.assign_button.setEnabled(bool(self.selected_card_ids()))

    def _assign(self) -> None:
        selected_ids = self.selected_card_ids()
        if not selected_ids:
            QMessageBox.warning(self, "Нет выбранных ссылок", "Нужно выбрать хотя бы одну ссылку.")
            return

        try:
            updated = self._swyp_card_assignment_service.assign_template(
                template_id=self._template.id,
                template_slug=self._template.slug,
                card_ids=selected_ids,
            )
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка назначения шаблона", str(exc))
            return

        if updated <= 0:
            QMessageBox.warning(
                self,
                "Шаблон не присвоен",
                "Ни одна запись не обновлена. Возможно, ссылки уже были назначены параллельно.",
            )
            self._load_cards()
            return

        self.accept()

    def _set_preview(self, target: QLabel, source: str, title: str) -> None:
        src = (source or "").strip()
        if not src:
            target.setText(f"{title}\n(нет превью)")
            return

        data_pix = _pixmap_from_data_uri(src)
        if data_pix is not None:
            self._apply_preview_pixmap(target, data_pix)
            return

        if _is_url(src):
            url = QUrl(src)
            cache_path = self._cache_path_for_url(url)
            if cache_path.is_file():
                self._apply_preview_pixmap(target, QPixmap(str(cache_path)))
                return

            target.setText(f"{title}\nЗагрузка...")
            req = QNetworkRequest(url)
            reply = self._net.get(req)
            self._pending[reply] = (target, cache_path)
            reply.finished.connect(lambda r=reply: self._on_download_finished(r))
            return

        path = Path(src).expanduser()
        if path.is_file():
            self._apply_preview_pixmap(target, QPixmap(str(path)))
            return

        target.setText(f"{title}\nПревью не найдено")

    def _apply_preview_pixmap(self, target: QLabel, pixmap: QPixmap) -> None:
        if pixmap.isNull():
            target.setText("Превью не удалось загрузить")
            return

        scaled = pixmap.scaled(260, 180, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        target.setPixmap(scaled)

    def _cache_path_for_url(self, url: QUrl) -> Path:
        self._template_service.cache_dir.mkdir(parents=True, exist_ok=True)
        digest = hashlib.sha256(url.toString().encode("utf-8")).hexdigest()
        suffix = _safe_suffix_from_url(url)
        return self._template_service.cache_dir / f"{digest}{suffix}"

    def _on_download_finished(self, reply: QNetworkReply) -> None:
        meta = self._pending.pop(reply, None)
        try:
            if meta is None:
                return

            target, cache_path = meta
            if reply.error() != QNetworkReply.NetworkError.NoError:
                target.setText(f"Ошибка загрузки: {reply.errorString()}")
                return

            data = bytes(reply.readAll())
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            cache_path.write_bytes(data)
            pixmap = QPixmap()
            pixmap.loadFromData(data)
            self._apply_preview_pixmap(target, pixmap)
        finally:
            reply.deleteLater()


class TemplateManagerWindow(QMainWindow):
    def __init__(
        self,
        template_service: TemplateService,
        swyp_card_assignment_service: SwypCardAssignmentService,
    ) -> None:
        super().__init__()
        self._template_service = template_service
        self._swyp_card_assignment_service = swyp_card_assignment_service

        self.setWindowTitle("Template Manager")
        self.resize(1200, 720)

        self._net = QNetworkAccessManager(self)
        self._pending: dict[QNetworkReply, tuple[int, int, Path, str]] = {}
        self._pixmap_cache: dict[str, QPixmap] = {}

        self._build_ui()

    def reload(self) -> None:
        try:
            templates = self._template_service.list_all()
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка загрузки шаблонов", str(exc))
            return

        self._fill_table(templates)
        self.statusBar().showMessage(f"Шаблонов: {len(templates)}", 3000)

    def _build_ui(self) -> None:
        root = QWidget()
        layout = QVBoxLayout(root)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        info = QLabel("Источник: MySQL таблица swyp_cards_templates")
        info.setStyleSheet("color: #475569;")
        layout.addWidget(info)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["id", "slug", "front_preview", "back_preview", "actions"])
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setIconSize(_THUMB_SIZE)
        self.table.cellClicked.connect(self._open_preview_for_row)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)

        layout.addWidget(self.table, 1)
        self.setCentralWidget(root)

        toolbar = QToolBar("Templates")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        refresh_action = QAction("Обновить", self)
        refresh_action.triggered.connect(self.reload)
        toolbar.addAction(refresh_action)

    def _fill_table(self, templates: list[CardTemplate]) -> None:
        self.table.setRowCount(len(templates))

        for row, tpl in enumerate(templates):
            self.table.setRowHeight(row, _THUMB_SIZE.height() + 16)

            id_item = QTableWidgetItem(tpl.id or "—")
            id_item.setData(Qt.ItemDataRole.UserRole, tpl)  # keep full template on the row
            self.table.setItem(row, 0, id_item)

            slug_item = QTableWidgetItem(tpl.slug or "—")
            self.table.setItem(row, 1, slug_item)

            self._set_preview_cell(row, 2, tpl.front_preview)
            self._set_preview_cell(row, 3, tpl.back_preview)
            self._set_actions_cell(row, tpl)

    def _set_actions_cell(self, row: int, tpl: CardTemplate) -> None:
        button = QPushButton("Присвоить шаблон")
        button.clicked.connect(lambda _checked=False, template=tpl: self._open_assign_dialog(template))

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.addWidget(button)
        layout.addStretch(1)
        self.table.setCellWidget(row, 4, container)

    def _set_preview_cell(self, row: int, col: int, source: str) -> None:
        item = QTableWidgetItem(" ")
        item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, col, item)

        src = (source or "").strip()
        if not src:
            item.setText("—")
            return

        # data URI
        data_pix = _pixmap_from_data_uri(src)
        if data_pix is not None and not data_pix.isNull():
            item.setIcon(QIcon(self._scaled_thumb(data_pix)))
            item.setText("")
            return

        # memory pixmap cache
        cached = self._pixmap_cache.get(src)
        if cached is not None and not cached.isNull():
            item.setIcon(QIcon(self._scaled_thumb(cached)))
            item.setText("")
            return

        if _is_url(src):
            url = QUrl(src)
            cache_path = self._cache_path_for_url(url)
            if cache_path.is_file():
                pix = QPixmap(str(cache_path))
                if not pix.isNull():
                    self._pixmap_cache[src] = pix
                    item.setIcon(QIcon(self._scaled_thumb(pix)))
                    item.setText("")
                    return

            item.setText("Загрузка…")
            req = QNetworkRequest(url)
            reply = self._net.get(req)
            self._pending[reply] = (row, col, cache_path, src)
            reply.finished.connect(lambda r=reply: self._on_preview_download_finished(r))
            return

        path = Path(src).expanduser()
        if path.is_file():
            pix = QPixmap(str(path))
            if pix.isNull():
                item.setText("Ошибка")
                return
            self._pixmap_cache[src] = pix
            item.setIcon(QIcon(self._scaled_thumb(pix)))
            item.setText("")
            return

        item.setText("Не найдено")

    def _scaled_thumb(self, pixmap: QPixmap) -> QPixmap:
        return pixmap.scaled(_THUMB_SIZE, Qt.KeepAspectRatio, Qt.SmoothTransformation)

    def _cache_path_for_url(self, url: QUrl) -> Path:
        self._template_service.cache_dir.mkdir(parents=True, exist_ok=True)
        digest = hashlib.sha256(url.toString().encode("utf-8")).hexdigest()
        suffix = _safe_suffix_from_url(url)
        return self._template_service.cache_dir / f"{digest}{suffix}"

    def _on_preview_download_finished(self, reply: QNetworkReply) -> None:
        meta = self._pending.pop(reply, None)
        try:
            if meta is None:
                return

            row, col, cache_path, source_key = meta
            item = self.table.item(row, col)
            if item is None:
                return

            if reply.error() != QNetworkReply.NetworkError.NoError:
                item.setText("Ошибка")
                return

            data = bytes(reply.readAll())
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            cache_path.write_bytes(data)

            pix = QPixmap()
            pix.loadFromData(data)
            if pix.isNull():
                item.setText("Ошибка")
                return

            self._pixmap_cache[source_key] = pix
            item.setIcon(QIcon(self._scaled_thumb(pix)))
            item.setText("")
        finally:
            reply.deleteLater()

    def _open_preview_for_row(self, row: int, _col: int) -> None:
        if _col == 4:
            return

        id_item = self.table.item(row, 0)
        if id_item is None:
            return

        tpl = id_item.data(Qt.ItemDataRole.UserRole)
        if tpl is None:
            return

        title = f"{getattr(tpl, 'id', '')} / {getattr(tpl, 'slug', '')}".strip(" /")
        dlg = TemplatePreviewDialog(title=title or "Template preview", cache_dir=self._template_service.cache_dir, parent=self)
        dlg.set_images(getattr(tpl, "front_preview", ""), getattr(tpl, "back_preview", ""))
        dlg.exec()

    def _open_assign_dialog(self, template: CardTemplate) -> None:
        dlg = AssignTemplateDialog(
            template=template,
            template_service=self._template_service,
            swyp_card_assignment_service=self._swyp_card_assignment_service,
            parent=self,
        )
        if dlg.exec() != int(QDialog.DialogCode.Accepted):
            return

        assigned_count = len(dlg.selected_card_ids())
        self.statusBar().showMessage(
            f"Шаблон id={template.id} присвоен {assigned_count} ссылкам",
            5000,
        )
