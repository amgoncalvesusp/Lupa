"""Workspace components for the tabbed Lupa desktop interface."""

from pathlib import Path

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QDragEnterEvent, QDropEvent
from PyQt6.QtWidgets import (
    QCheckBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QStackedWidget,
    QStyle,
    QTableWidget,
    QVBoxLayout,
    QWidget,
)

SUPPORTED_EXTENSIONS = (".pdf", ".docx", ".txt")


class DropZone(QFrame):
    files_dropped = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("DropZone")
        self.setAcceptDrops(True)
        layout = QVBoxLayout(self)
        self.label = QLabel("Solte documentos PDF, DOCX ou TXT")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setObjectName("DropZoneLabel")
        layout.addWidget(self.label)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if not event.mimeData().hasUrls():
            return
        paths = [url.toLocalFile() for url in event.mimeData().urls()]
        has_document = any(path.lower().endswith(SUPPORTED_EXTENSIONS) for path in paths)
        has_directory = any(Path(path).is_dir() for path in paths)
        if has_document or has_directory:
            self.setProperty("active", "true")
            self.style().unpolish(self)
            self.style().polish(self)
            event.acceptProposedAction()

    def dragLeaveEvent(self, event):
        self._reset_state()
        super().dragLeaveEvent(event)

    def dropEvent(self, event: QDropEvent):
        paths = []
        for url in event.mimeData().urls():
            local = url.toLocalFile()
            path = Path(local)
            if path.is_dir():
                for extension in SUPPORTED_EXTENSIONS:
                    paths.extend(str(item) for item in path.glob(f"*{extension}"))
                    paths.extend(str(item) for item in path.glob(f"*{extension.upper()}"))
            elif local.lower().endswith(SUPPORTED_EXTENSIONS):
                paths.append(local)
        self._reset_state()
        if paths:
            self.files_dropped.emit(paths)
            event.acceptProposedAction()

    def _reset_state(self):
        self.setProperty("active", "false")
        self.style().unpolish(self)
        self.style().polish(self)


class ApplicationHeader(QFrame):
    help_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("AppHeader")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 10)
        layout.setSpacing(16)

        brand = QLabel("Lupa")
        brand.setObjectName("AppBrand")
        layout.addWidget(brand)

        separator = QFrame()
        separator.setObjectName("HeaderSeparator")
        separator.setFrameShape(QFrame.Shape.VLine)
        layout.addWidget(separator)

        subtitle = QLabel("Análise documental auditável")
        subtitle.setObjectName("AppSubtitle")
        layout.addWidget(subtitle)
        layout.addStretch()

        self.context = QLabel("CORPUS OFFLINE")
        self.context.setObjectName("HeaderContext")
        layout.addWidget(self.context)

        help_button = QPushButton()
        help_button.setObjectName("HeaderIconButton")
        help_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogHelpButton))
        help_button.setToolTip("Abrir ajuda")
        help_button.clicked.connect(self.help_requested)
        layout.addWidget(help_button)


class SetupWorkspace(QWidget):
    add_requested = pyqtSignal()
    clear_requested = pyqtSignal()
    process_requested = pyqtSignal()
    cancel_requested = pyqtSignal()
    methodology_requested = pyqtSignal()
    search_help_requested = pyqtSignal()
    files_dropped = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 14, 16, 14)
        root.setSpacing(12)

        columns = QHBoxLayout()
        columns.setSpacing(12)
        columns.addWidget(self._build_corpus_panel(), stretch=3)
        columns.addWidget(self._build_analysis_panel(), stretch=2)
        root.addLayout(columns, stretch=1)
        root.addWidget(self._build_action_bar())

    def _build_corpus_panel(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("WorkspacePanel")
        panel.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Expanding)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 14, 16, 16)
        layout.setSpacing(10)

        header = QHBoxLayout()
        title = QLabel("Corpus documental")
        title.setObjectName("WorkspaceTitle")
        header.addWidget(title)
        self.file_count = QLabel("0 documentos")
        self.file_count.setObjectName("MutedText")
        header.addWidget(self.file_count)
        header.addStretch()

        self.btn_add = QPushButton("Adicionar")
        self.btn_add.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogOpenButton))
        self.btn_add.clicked.connect(self.add_requested)
        header.addWidget(self.btn_add)
        self.btn_clear = QPushButton()
        self.btn_clear.setObjectName("DangerIconButton")
        self.btn_clear.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_TrashIcon))
        self.btn_clear.setToolTip("Limpar lista")
        self.btn_clear.clicked.connect(self.clear_requested)
        header.addWidget(self.btn_clear)
        layout.addLayout(header)

        self.drop_zone = DropZone()
        self.drop_zone.files_dropped.connect(self.files_dropped)
        layout.addWidget(self.drop_zone)

        self.file_list = QListWidget()
        self.file_list.setObjectName("CorpusFileList")
        layout.addWidget(self.file_list, stretch=1)
        return panel

    def _build_analysis_panel(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("WorkspacePanel")
        panel.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Expanding)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 14, 16, 16)
        layout.setSpacing(9)

        header = QHBoxLayout()
        title = QLabel("Configuração da análise")
        title.setObjectName("WorkspaceTitle")
        header.addWidget(title)
        header.addStretch()
        self.btn_methodology = QPushButton("Metodologias")
        self.btn_methodology.clicked.connect(self.methodology_requested)
        header.addWidget(self.btn_methodology)
        layout.addLayout(header)

        terms_header = QHBoxLayout()
        terms_label = QLabel("Termos e categorias")
        terms_label.setObjectName("FieldLabel")
        terms_header.addWidget(terms_label)
        terms_header.addStretch()
        search_help = QPushButton()
        search_help.setObjectName("InlineIconButton")
        search_help.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogHelpButton))
        search_help.setToolTip("Sintaxe de termos e categorias")
        search_help.clicked.connect(self.search_help_requested)
        terms_header.addWidget(search_help)
        layout.addLayout(terms_header)

        self.terms_input = QPlainTextEdit()
        self.terms_input.setPlaceholderText(
            "clima\n"
            '"efeito estufa"\n'
            'MITIGAÇÃO: carbono, metano, "efeito estufa"'
        )
        layout.addWidget(self.terms_input, stretch=1)

        analyses_label = QLabel("Análises ativas")
        analyses_label.setObjectName("FieldLabel")
        layout.addWidget(analyses_label)
        grid = QGridLayout()
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(8)
        self.sentiment_checkbox = QCheckBox("Sentimento")
        self.emotions_checkbox = QCheckBox("Emoções NRC")
        self.textmetrics_checkbox = QCheckBox("Métricas textuais")
        self.kwic_checkbox = QCheckBox("KWIC e coocorrência")
        self.president_checkbox = QCheckBox("Detectar presidente")
        self.ocr_checkbox = QCheckBox("OCR em páginas escaneadas")
        tooltips = {
            self.sentiment_checkbox: "Classifica o sentimento das sentenças com LeIA/VADER-PT.",
            self.emotions_checkbox: "Conta emoções do léxico NRC configurado no projeto.",
            self.textmetrics_checkbox: "Calcula legibilidade, diversidade lexical e frequências.",
            self.kwic_checkbox: "Registra contexto e coocorrências dos termos pesquisados.",
            self.president_checkbox: "Identifica o presidente a partir do texto e do ano.",
            self.ocr_checkbox: "Aplica Tesseract somente em páginas sem texto extraível.",
        }
        for checkbox in (
            self.sentiment_checkbox,
            self.emotions_checkbox,
            self.textmetrics_checkbox,
            self.kwic_checkbox,
            self.president_checkbox,
            self.ocr_checkbox,
        ):
            checkbox.setChecked(True)
            checkbox.setToolTip(tooltips[checkbox])
        grid.addWidget(self.sentiment_checkbox, 0, 0)
        grid.addWidget(self.emotions_checkbox, 1, 0)
        grid.addWidget(self.textmetrics_checkbox, 2, 0)
        grid.addWidget(self.kwic_checkbox, 3, 0)
        grid.addWidget(self.president_checkbox, 4, 0)
        grid.addWidget(self.ocr_checkbox, 5, 0)
        layout.addLayout(grid)
        return panel

    def _build_action_bar(self) -> QFrame:
        bar = QFrame()
        bar.setObjectName("ActionBar")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(14, 10, 14, 10)

        self.btn_process = QPushButton("Processar corpus")
        self.btn_process.setObjectName("PrimaryButton")
        self.btn_process.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.btn_process.clicked.connect(self.process_requested)
        layout.addWidget(self.btn_process)

        self.btn_cancel = QPushButton("Cancelar")
        self.btn_cancel.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogCancelButton))
        self.btn_cancel.setEnabled(False)
        self.btn_cancel.clicked.connect(self.cancel_requested)
        layout.addWidget(self.btn_cancel)

        self.processing_label = QLabel("Pronto para processar")
        self.processing_label.setObjectName("MutedText")
        layout.addWidget(self.processing_label)
        layout.addStretch()

        self.progress = QProgressBar()
        self.progress.setFixedWidth(280)
        self.progress.setVisible(False)
        layout.addWidget(self.progress)
        return bar

    def set_file_count(self, count: int) -> None:
        self.file_count.setText(f"{count} documento{'s' if count != 1 else ''}")


class ResultsWorkspace(QWidget):
    export_requested = pyqtSignal()
    details_requested = pyqtSignal()
    charts_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(10)
        layout.addWidget(self._build_summary_band())

        header = QHBoxLayout()
        title = QLabel("Resultados do corpus")
        title.setObjectName("WorkspaceTitle")
        header.addWidget(title)
        header.addStretch()
        self.btn_charts = QPushButton("Explorar gráficos")
        self.btn_charts.clicked.connect(self.charts_requested)
        header.addWidget(self.btn_charts)
        self.btn_details = QPushButton("Ver detalhes")
        self.btn_details.setEnabled(False)
        self.btn_details.clicked.connect(self.details_requested)
        header.addWidget(self.btn_details)
        self.btn_export = QPushButton("Exportar")
        self.btn_export.setObjectName("PrimaryButton")
        self.btn_export.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton))
        self.btn_export.setEnabled(False)
        self.btn_export.clicked.connect(self.export_requested)
        header.addWidget(self.btn_export)
        layout.addLayout(header)

        self.content = QStackedWidget()
        empty = QLabel("Nenhum resultado disponível")
        empty.setObjectName("EmptyState")
        empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content.addWidget(empty)
        self.results_table = QTableWidget(0, 8)
        self.results_table.setObjectName("ResultsTable")
        self.results_table.setAlternatingRowColors(True)
        self.content.addWidget(self.results_table)
        layout.addWidget(self.content, stretch=1)
        self.set_results_summary([])

    def _build_summary_band(self) -> QFrame:
        band = QFrame()
        band.setObjectName("SummaryBand")
        layout = QHBoxLayout(band)
        layout.setContentsMargins(18, 10, 18, 10)
        self.docs_value = self._summary_item(layout, "DOCUMENTOS")
        self.words_value = self._summary_item(layout, "PALAVRAS NO CORPUS")
        self.years_value = self._summary_item(layout, "ANOS IDENTIFICADOS")
        self.sentiment_value = self._summary_item(layout, "SENTIMENTO MÉDIO")
        return band

    @staticmethod
    def _summary_item(layout: QHBoxLayout, label: str) -> QLabel:
        container = QWidget()
        item_layout = QVBoxLayout(container)
        item_layout.setContentsMargins(12, 0, 12, 0)
        item_layout.setSpacing(1)
        caption = QLabel(label)
        caption.setObjectName("SummaryCaption")
        value = QLabel("-")
        value.setObjectName("SummaryValue")
        item_layout.addWidget(caption)
        item_layout.addWidget(value)
        layout.addWidget(container, stretch=1)
        return value

    def set_results_summary(self, results) -> None:
        self.docs_value.setText(str(len(results)))
        words = sum(int(result.get("words_analytical") or 0) for result in results)
        self.words_value.setText(f"{words:,}".replace(",", "."))
        years = {str(result.get("year")) for result in results if result.get("year")}
        self.years_value.setText(str(len(years)))
        compounds = [
            float(result["sent_compound_medio"])
            for result in results
            if result.get("sent_compound_medio") not in (None, "")
        ]
        mean = sum(compounds) / len(compounds) if compounds else 0.0
        self.sentiment_value.setText(f"{mean:.3f}" if compounds else "-")
        self.content.setCurrentIndex(1 if results else 0)
        self.btn_charts.setEnabled(bool(results))
