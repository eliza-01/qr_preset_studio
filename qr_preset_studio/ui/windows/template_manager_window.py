from __future__ import annotations

import base64
import hashlib
from pathlib import Path

from PySide6.QtCore import Qt, QSize, QUrl
from PySide6.QtGui import QAction, QIcon, QPixmap
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest
from PySide6.QtWidgets import (
    QBoxLayout,
    QDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QToolBar,
    QVBoxLayout,
    QWidget,
    QHeaderView,
    QScrollArea,
)

from qr_preset_studio.application.services.template_service import TemplateService
from qr_preset_studio.domain.models.template import CardTemplate


_THUMB_SIZE = QSize(220, 140)
_VIEW_SIZE = QSize(900, 600)


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
        self._pending: dict[QNetworkReply, tuple[QLabel, Path]] = {}

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

        self._content_layout.addWidget(self._wrap_scroll(self.front_label), 1)
        self._content_layout.addWidget(self._wrap_scroll(self.back_label), 1)

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

    def _wrap_scroll(self, label: QLabel) -> QScrollArea:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setAlignment(Qt.AlignCenter)
        scroll.setWidget(label)
        return scroll

    def _image_panel(self, title: str) -> QLabel:
        label = QLabel()
        label.setAlignment(Qt.AlignCenter)
        label.setWordWrap(True)
        label.setMinimumSize(420, 320)
        label.setStyleSheet(
            "QLabel { background: #E2E8F0; border: 1px solid #CBD5E1; border-radius: 12px; padding: 10px; }"
        )
        label.setText(f"{title}\n(нет превью)")
        return label

    def _apply_pixmap(self, target: QLabel, pixmap: QPixmap) -> None:
        if pixmap.isNull():
            target.setText("Превью не удалось загрузить")
            return
        scaled = pixmap.scaled(_VIEW_SIZE, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        target.setPixmap(scaled)
        target.adjustSize()

    def _set_image(self, target: QLabel, source: str) -> None:
        src = (source or "").strip()
        if not src:
            target.setText("(нет превью)")
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

            target.setText("Загрузка превью...")
            req = QNetworkRequest(url)
            reply = self._net.get(req)
            self._pending[reply] = (target, cache_path)
            reply.finished.connect(lambda r=reply: self._on_download_finished(r))
            return

        path = Path(src).expanduser()
        if path.is_file():
            self._apply_pixmap(target, QPixmap(str(path)))
            return

        target.setText("Превью не найдено")

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
                target.setText(f"Ошибка загрузки: {reply.errorString()}")
                return

            data = bytes(reply.readAll())
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            cache_path.write_bytes(data)

            pixmap = QPixmap()
            pixmap.loadFromData(data)
            self._apply_pixmap(target, pixmap)
        finally:
            reply.deleteLater()


class TemplateManagerWindow(QMainWindow):
    def __init__(self, template_service: TemplateService) -> None:
        super().__init__()
        self._template_service = template_service

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
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["id", "slug", "front_preview", "back_preview"])
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