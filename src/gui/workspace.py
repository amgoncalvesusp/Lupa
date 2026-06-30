"""Workspace components for the Lupa research workbench."""

from pathlib import Path

from PyQt6.QtCore import QSize, Qt, pyqtSignal
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QPixmap
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
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
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from src.gui.resources import asset_path
from src.gui import i18n

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
        self.language = i18n.DEFAULT_LANGUAGE

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

    def set_language(self, language: str) -> None:
        self.language = i18n.normalize_language(language)
        self.label.setText(
            "Drop PDF, DOCX or TXT documents"
            if self.language == "en"
            else "Solte documentos PDF, DOCX ou TXT"
        )


class NavigationSidebar(QFrame):
    page_requested = pyqtSignal(int)
    help_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("NavigationSidebar")
        self.setFixedWidth(214)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 24, 0, 18)
        layout.setSpacing(8)

        logo = QLabel()
        logo.setObjectName("SidebarLogo")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pixmap = QPixmap(str(asset_path("lupa-icon.png")))
        logo.setPixmap(
            pixmap.scaled(
                86,
                86,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )
        layout.addWidget(logo)

        brand = QLabel("Lupa")
        brand.setObjectName("SidebarBrand")
        brand.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(brand)

        self.descriptor = QLabel("ANÁLISE DOCUMENTAL")
        self.descriptor.setObjectName("SidebarDescriptor")
        self.descriptor.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.descriptor)
        layout.addSpacing(22)

        navigation_items = (
            ("Corpus", QStyle.StandardPixmap.SP_DirIcon),
            ("Resultados", QStyle.StandardPixmap.SP_FileDialogDetailedView),
            ("Exploração", QStyle.StandardPixmap.SP_ComputerIcon),
        )
        self.buttons = []
        self._navigation_items = navigation_items
        for index, (label, icon_type) in enumerate(navigation_items):
            button = QPushButton(label)
            button.setObjectName("NavigationButton")
            button.setCheckable(True)
            button.setAutoExclusive(True)
            button.setIcon(self.style().standardIcon(icon_type))
            button.setIconSize(QSize(20, 20))
            button.clicked.connect(
                lambda _checked=False, page=index: self.page_requested.emit(page)
            )
            self.buttons.append(button)
            layout.addWidget(button)
        self.buttons[0].setChecked(True)
        layout.addStretch()

        self.help_button = QPushButton("Ajuda e métodos")
        self.help_button.setObjectName("SidebarHelpButton")
        self.help_button.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_DialogHelpButton)
        )
        self.help_button.clicked.connect(self.help_requested)
        layout.addWidget(self.help_button)
        self.language = i18n.DEFAULT_LANGUAGE

    def set_page_enabled(self, index: int, enabled: bool) -> None:
        self.buttons[index].setEnabled(enabled)

    def set_current_index(self, index: int) -> None:
        self.buttons[index].setChecked(True)

    def set_language(self, language: str) -> None:
        self.language = i18n.normalize_language(language)
        labels = (
            ("Corpus", "Corpus"),
            ("Resultados", "Results"),
            ("Exploração", "Explore"),
        )
        for button, (pt, en) in zip(self.buttons, labels):
            button.setText(en if self.language == "en" else pt)
        self.descriptor.setText("DOCUMENT ANALYSIS" if self.language == "en" else "ANÁLISE DOCUMENTAL")
        self.help_button.setText("Help and methods" if self.language == "en" else "Ajuda e métodos")


class WorkspaceHeader(QFrame):
    help_requested = pyqtSignal()
    language_requested = pyqtSignal()

    PAGES = (
        ("Corpus", "Prepare documentos e parâmetros para a análise."),
        ("Resultados", "Revise o corpus processado e abra a trilha de auditoria."),
        ("Exploração visual", "Compare documentos, períodos e indicadores."),
    )

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("WorkspaceHeader")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 14, 20, 12)
        layout.setSpacing(14)

        title_group = QVBoxLayout()
        title_group.setSpacing(1)
        self.title = QLabel()
        self.title.setObjectName("WorkspacePageTitle")
        self.description = QLabel()
        self.description.setObjectName("WorkspacePageDescription")
        title_group.addWidget(self.title)
        title_group.addWidget(self.description)
        layout.addLayout(title_group)
        layout.addStretch()

        self.context = QLabel("CORPUS OFFLINE")
        self.context.setObjectName("WorkspaceContext")
        layout.addWidget(self.context)
        self.language_button = QPushButton("EN")
        self.language_button.setObjectName("HeaderIconButton")
        self.language_button.setToolTip("Switch to English")
        self.language_button.clicked.connect(self.language_requested)
        layout.addWidget(self.language_button)
        help_button = QPushButton()
        help_button.setObjectName("HeaderIconButton")
        help_button.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_DialogHelpButton)
        )
        help_button.setToolTip("Abrir ajuda")
        help_button.clicked.connect(self.help_requested)
        layout.addWidget(help_button)
        self.language = i18n.DEFAULT_LANGUAGE
        self._context_value = "CORPUS OFFLINE"
        self.set_page(0)

    def set_page(self, index: int) -> None:
        self.current_index = index
        title, description = self.PAGES[index]
        if self.language == "en":
            translated = (
                ("Corpus", "Prepare documents and analysis parameters."),
                ("Results", "Review the processed corpus and open the audit trail."),
                ("Visual exploration", "Compare documents, periods and indicators."),
            )
            title, description = translated[index]
        self.title.setText(title)
        self.description.setText(description)

    def set_context(self, text: str) -> None:
        self._context_value = text
        if self.language == "en":
            text = text.replace("DOCUMENTOS", "DOCUMENTS").replace("PROCESSANDO", "PROCESSING")
        self.context.setText(text)

    def set_language(self, language: str) -> None:
        self.language = i18n.normalize_language(language)
        self.language_button.setText("PT" if self.language == "en" else "EN")
        self.language_button.setToolTip(
            "Mudar para português" if self.language == "en" else "Switch to English"
        )
        self.set_page(getattr(self, "current_index", 0))
        self.set_context(getattr(self, "_context_value", "CORPUS OFFLINE"))


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
        self.language = i18n.DEFAULT_LANGUAGE
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 14, 16, 14)
        root.setSpacing(12)

        columns = QHBoxLayout()
        columns.setSpacing(0)
        columns.addWidget(self._build_corpus_panel(), stretch=3)
        analysis_panel = self._build_analysis_panel()
        analysis_panel.setMaximumWidth(430)
        columns.addWidget(analysis_panel, stretch=2)
        root.addLayout(columns, stretch=1)
        root.addWidget(self._build_action_bar())

    def _build_corpus_panel(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("DocumentCanvas")
        panel.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Expanding)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 14, 16, 16)
        layout.setSpacing(10)

        header = QHBoxLayout()
        self.documents_title = QLabel("Documentos")
        self.documents_title.setObjectName("WorkspaceTitle")
        header.addWidget(self.documents_title)
        self.file_count = QLabel("0 documentos")
        self.file_count.setObjectName("MutedText")
        header.addWidget(self.file_count)
        header.addStretch()

        self.btn_add = QPushButton("Adicionar arquivos")
        self.btn_add.setObjectName("PrimaryButton")
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
        panel.setObjectName("AnalysisInspector")
        panel.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Expanding)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 14, 16, 16)
        layout.setSpacing(9)

        header = QHBoxLayout()
        self.analysis_title = QLabel("Configuração da análise")
        self.analysis_title.setObjectName("WorkspaceTitle")
        header.addWidget(self.analysis_title)
        header.addStretch()
        self.btn_methodology = QPushButton("Métodos")
        self.btn_methodology.clicked.connect(self.methodology_requested)
        header.addWidget(self.btn_methodology)
        layout.addLayout(header)

        terms_header = QHBoxLayout()
        self.terms_label = QLabel("Termos e categorias")
        self.terms_label.setObjectName("FieldLabel")
        terms_header.addWidget(self.terms_label)
        terms_header.addStretch()
        search_help = QPushButton()
        search_help.setObjectName("InlineIconButton")
        search_help.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogHelpButton))
        self.search_help = search_help
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

        self.analyses_label = QLabel("Análises ativas")
        self.analyses_label.setObjectName("FieldLabel")
        layout.addWidget(self.analyses_label)
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
        self.president_checkbox.setChecked(False)
        self.president_checkbox.setVisible(False)
        grid.addWidget(self.sentiment_checkbox, 0, 0)
        grid.addWidget(self.emotions_checkbox, 1, 0)
        grid.addWidget(self.textmetrics_checkbox, 2, 0)
        grid.addWidget(self.kwic_checkbox, 3, 0)
        grid.addWidget(self.ocr_checkbox, 4, 0)
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
        if self.language == "en":
            self.file_count.setText(f"{count} document{'s' if count != 1 else ''}")
        else:
            self.file_count.setText(f"{count} documento{'s' if count != 1 else ''}")

    def set_language(self, language: str) -> None:
        self.language = i18n.normalize_language(language)
        english = self.language == "en"
        self.documents_title.setText("Documents" if english else "Documentos")
        self.btn_add.setText("Add files" if english else "Adicionar arquivos")
        self.btn_clear.setToolTip("Clear list" if english else "Limpar lista")
        self.drop_zone.set_language(self.language)
        self.analysis_title.setText("Analysis settings" if english else "Configuração da análise")
        self.btn_methodology.setText("Methods" if english else "Métodos")
        self.terms_label.setText("Terms and categories" if english else "Termos e categorias")
        self.search_help.setToolTip(
            "Term and category syntax" if english else "Sintaxe de termos e categorias"
        )
        self.terms_input.setPlaceholderText(
            "climate\n"
            '"greenhouse effect"\n'
            'MITIGATION: carbon, methane, "greenhouse effect"'
            if english
            else "clima\n"
            '"efeito estufa"\n'
            'MITIGAÇÃO: carbono, metano, "efeito estufa"'
        )
        self.analyses_label.setText("Active analyses" if english else "Análises ativas")
        checkbox_texts = {
            self.sentiment_checkbox: ("Sentiment", "Sentimento"),
            self.emotions_checkbox: ("NRC emotions", "Emoções NRC"),
            self.textmetrics_checkbox: ("Text metrics", "Métricas textuais"),
            self.kwic_checkbox: ("KWIC and co-occurrence", "KWIC e coocorrência"),
            self.president_checkbox: ("Detect president", "Detectar presidente"),
            self.ocr_checkbox: ("OCR on scanned pages", "OCR em páginas escaneadas"),
        }
        checkbox_tips = {
            self.sentiment_checkbox: (
                "Classifies sentence sentiment with LeIA/VADER-PT.",
                "Classifica o sentimento das sentenças com LeIA/VADER-PT.",
            ),
            self.emotions_checkbox: (
                "Counts emotions from the NRC lexicon configured in the project.",
                "Conta emoções do léxico NRC configurado no projeto.",
            ),
            self.textmetrics_checkbox: (
                "Calculates readability, lexical diversity and frequencies.",
                "Calcula legibilidade, diversidade lexical e frequências.",
            ),
            self.kwic_checkbox: (
                "Registers context and co-occurrences for searched terms.",
                "Registra contexto e coocorrências dos termos pesquisados.",
            ),
            self.president_checkbox: (
                "Identifies the president from text and year.",
                "Identifica o presidente a partir do texto e do ano.",
            ),
            self.ocr_checkbox: (
                "Applies Tesseract only to pages without extractable text.",
                "Aplica Tesseract somente em páginas sem texto extraível.",
            ),
        }
        for checkbox, (en, pt) in checkbox_texts.items():
            checkbox.setText(en if english else pt)
            tip_en, tip_pt = checkbox_tips[checkbox]
            checkbox.setToolTip(tip_en if english else tip_pt)
        self.btn_process.setText("Process corpus" if english else "Processar corpus")
        self.btn_cancel.setText("Cancel" if english else "Cancelar")
        if self.processing_label.text() in {
            "Pronto para processar",
            "Ready to process",
        }:
            self.processing_label.setText("Ready to process" if english else "Pronto para processar")
        self.set_file_count(self.file_list.count())


class ResultsWorkspace(QWidget):
    export_requested = pyqtSignal()
    details_requested = pyqtSignal()
    charts_requested = pyqtSignal()
    review_requested = pyqtSignal()
    coding_import_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.language = i18n.DEFAULT_LANGUAGE
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(10)
        layout.addWidget(self._build_summary_band())

        header = QHBoxLayout()
        self.results_title = QLabel("Resultados do corpus")
        self.results_title.setObjectName("WorkspaceTitle")
        header.addWidget(self.results_title)
        header.addStretch()
        self.btn_charts = QPushButton("Explorar gráficos")
        self.btn_charts.clicked.connect(self.charts_requested)
        header.addWidget(self.btn_charts)
        self.btn_details = QPushButton("Ver detalhes")
        self.btn_details.setEnabled(False)
        self.btn_details.clicked.connect(self.details_requested)
        header.addWidget(self.btn_details)
        self.btn_review = QPushButton("Revisar metadados")
        self.btn_review.setEnabled(False)
        self.btn_review.clicked.connect(self.review_requested)
        header.addWidget(self.btn_review)
        self.btn_export = QPushButton("Exportar")
        self.btn_export.setObjectName("PrimaryButton")
        self.btn_export.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton))
        self.btn_export.setEnabled(False)
        self.btn_export.clicked.connect(self.export_requested)
        header.addWidget(self.btn_export)
        layout.addLayout(header)

        self.content = QStackedWidget()
        self.empty = QLabel("Nenhum resultado disponível")
        self.empty.setObjectName("EmptyState")
        self.empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content.addWidget(self.empty)
        self.result_tabs = QTabWidget()
        documents_page = QWidget()
        documents_layout = QVBoxLayout(documents_page)
        documents_layout.setContentsMargins(0, 0, 0, 0)
        self.results_table = QTableWidget(0, 8)
        self.results_table.setObjectName("ResultsTable")
        self.results_table.setAlternatingRowColors(True)
        documents_layout.addWidget(self.results_table)
        self.result_tabs.addTab(documents_page, "Documentos")

        corpus_page = QWidget()
        corpus_layout = QVBoxLayout(corpus_page)
        corpus_layout.setContentsMargins(0, 0, 0, 0)
        corpus_controls = QHBoxLayout()
        self.corpus_table_selector = QComboBox()
        self._corpus_selector_items = (
            ("Autores consolidados", "authors"),
            ("Instituições", "institutions"),
            ("Dispersão de termos", "dispersion"),
            ("Termos distintivos (keyness)", "keyness"),
            ("Associação entre termos (NPMI)", "cooccurrence_association"),
            ("Mudança lexical temporal", "temporal_change"),
            ("Diagnóstico de sentimento", "sentiment_diagnostics"),
            ("Matriz de similaridade", "similarity"),
        )
        for label, key in self._corpus_selector_items:
            self.corpus_table_selector.addItem(label, key)
        self.corpus_table_selector.currentIndexChanged.connect(self._populate_corpus_table)
        corpus_controls.addWidget(self.corpus_table_selector, stretch=1)
        self.btn_import_coding = QPushButton("Importar codificação")
        self.btn_import_coding.setToolTip("CSV com colunas unit, coder e code")
        self.btn_import_coding.clicked.connect(self.coding_import_requested)
        corpus_controls.addWidget(self.btn_import_coding)
        corpus_layout.addLayout(corpus_controls)
        self.corpus_table = QTableWidget(0, 0)
        self.corpus_table.setAlternatingRowColors(True)
        corpus_layout.addWidget(self.corpus_table, stretch=1)
        self.result_tabs.addTab(corpus_page, "Sínteses do corpus")
        self.content.addWidget(self.result_tabs)
        layout.addWidget(self.content, stretch=1)
        self.corpus_analyses = {}
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

    def _summary_item(self, layout: QHBoxLayout, label: str) -> QLabel:
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
        if not hasattr(self, "_summary_captions"):
            self._summary_captions = []
        self._summary_captions.append(caption)
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

    def set_corpus_analyses(self, analyses) -> None:
        self.corpus_analyses = dict(analyses or {})
        self._populate_corpus_table()

    def _populate_corpus_table(self) -> None:
        if not hasattr(self, "corpus_table"):
            return
        key = self.corpus_table_selector.currentData()
        if key in {"authors", "institutions"}:
            rows = list((self.corpus_analyses.get("entities") or {}).get(key, []))
        elif key == "similarity":
            similarity = self.corpus_analyses.get("similarity") or {}
            labels = list(similarity.get("labels", []))
            rows = [
                {"documento": label, **{other: value for other, value in zip(labels, similarity.get("matrix", [])[index])}}
                for index, label in enumerate(labels)
            ]
        else:
            rows = list(self.corpus_analyses.get(key, []))
        headers = list(rows[0]) if rows else []
        self.corpus_table.setColumnCount(len(headers))
        self.corpus_table.setHorizontalHeaderLabels([self._corpus_header(header) for header in headers])
        self.corpus_table.setRowCount(len(rows))
        for row_index, row in enumerate(rows):
            for column_index, header in enumerate(headers):
                value = row.get(header, "")
                if isinstance(value, list):
                    value = "; ".join(str(item) for item in value)
                self.corpus_table.setItem(row_index, column_index, QTableWidgetItem(str(value)))
        self.corpus_table.resizeColumnsToContents()

    def _corpus_header(self, key: str) -> str:
        labels = {
            "name": "Nome", "documents": "Documentos", "fractional_documents": "Contagem fracionária",
            "words": "Palavras", "year_start": "Ano inicial", "year_end": "Ano final",
            "document_types": "Tipos", "files": "Arquivos", "term": "Termo", "frequency": "Frequência",
            "dp": "DP", "document_range": "Alcance (docs)", "document_range_pct": "Alcance (%)",
            "group": "Grupo", "g2": "G²", "log_ratio": "Log-ratio", "p_value": "p", "q_value": "q (BH)",
            "term_a": "Termo A", "term_b": "Termo B", "npmi": "NPMI",
            "period_start": "Período inicial", "period_end": "Período final", "js_divergence": "Divergência JS",
            "top_terms": "Termos que mais mudaram", "filename": "Arquivo", "lexicon_coverage_pct": "Cobertura léxica (%)",
        }
        text = labels.get(key, key.replace("_", " ").title())
        translations = {
            "Nome": "Name",
            "Documentos": "Documents",
            "Contagem fracionária": "Fractional count",
            "Palavras": "Words",
            "Ano inicial": "Start year",
            "Ano final": "End year",
            "Tipos": "Types",
            "Arquivos": "Files",
            "Termo": "Term",
            "Frequência": "Frequency",
            "Alcance (docs)": "Range (docs)",
            "Alcance (%)": "Range (%)",
            "Grupo": "Group",
            "Termo A": "Term A",
            "Termo B": "Term B",
            "Período inicial": "Start period",
            "Período final": "End period",
            "Divergência JS": "JS divergence",
            "Termos que mais mudaram": "Terms that changed most",
            "Arquivo": "File",
            "Cobertura léxica (%)": "Lexicon coverage (%)",
        }
        return translations.get(text, text) if self.language == "en" else text

    def set_language(self, language: str) -> None:
        self.language = i18n.normalize_language(language)
        english = self.language == "en"
        self.results_title.setText("Corpus results" if english else "Resultados do corpus")
        self.btn_charts.setText("Explore charts" if english else "Explorar gráficos")
        self.btn_details.setText("View details" if english else "Ver detalhes")
        self.btn_review.setText("Review metadata" if english else "Revisar metadados")
        self.btn_export.setText("Export" if english else "Exportar")
        self.empty.setText("No results available" if english else "Nenhum resultado disponível")
        self.result_tabs.setTabText(0, "Documents" if english else "Documentos")
        self.result_tabs.setTabText(1, "Corpus summaries" if english else "Sínteses do corpus")
        summary_labels = (
            ("DOCUMENTS", "DOCUMENTOS"),
            ("WORDS IN CORPUS", "PALAVRAS NO CORPUS"),
            ("YEARS IDENTIFIED", "ANOS IDENTIFICADOS"),
            ("MEAN SENTIMENT", "SENTIMENTO MÉDIO"),
        )
        for caption, (en, pt) in zip(getattr(self, "_summary_captions", []), summary_labels):
            caption.setText(en if english else pt)
        for index, (pt, _key) in enumerate(self._corpus_selector_items):
            translations = {
                "Autores consolidados": "Consolidated authors",
                "Instituições": "Institutions",
                "Dispersão de termos": "Term dispersion",
                "Termos distintivos (keyness)": "Distinctive terms (keyness)",
                "Associação entre termos (NPMI)": "Term association (NPMI)",
                "Mudança lexical temporal": "Temporal lexical change",
                "Diagnóstico de sentimento": "Sentiment diagnostics",
                "Matriz de similaridade": "Similarity matrix",
            }
            self.corpus_table_selector.setItemText(index, translations.get(pt, pt) if english else pt)
        self.btn_import_coding.setText("Import coding" if english else "Importar codificação")
        self.btn_import_coding.setToolTip(
            "CSV with unit, coder and code columns" if english else "CSV com colunas unit, coder e code"
        )
        self._populate_corpus_table()
