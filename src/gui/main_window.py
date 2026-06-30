"""Main application window."""

from pathlib import Path
from typing import List

from PyQt6.QtCore import Qt, QThread
from PyQt6.QtGui import QAction, QColor, QIcon
from PyQt6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHeaderView,
    QHBoxLayout,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QStatusBar,
    QStackedWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from src.gui.styles import STYLE
from src.gui.workers import ProcessingWorker
from src.gui.help_dialog import HelpDialog
from src.gui.detail_dialog import ResultDetailDialog
from src.gui.metadata_editor import MetadataEditorDialog
from src.gui.charts import ChartWorkspace
from src.gui import i18n
from src.gui.resources import asset_path
from src.gui.workspace import (
    NavigationSidebar,
    ResultsWorkspace,
    SetupWorkspace,
    SUPPORTED_EXTENSIONS,
    WorkspaceHeader,
)
from src.core.analysis import build_column_specs, build_default_analyzers
from src.core.corpus_analysis import build_corpus_analyses
from src.core.exporter import export_to_xlsx
from src.core.exporter_plain import export_to_csv, export_to_json
from src.core.ocr_engine import configure_tesseract
from src.core.project_io import load_project, save_project
from src.core.metadata_review import apply_metadata_override
from src.core.qualitative_coding import (
    coding_disagreements,
    import_codings_csv,
    krippendorff_alpha_by_code,
    krippendorff_alpha_nominal,
)
from src.core.term_search import parse_input

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lupa — Análise Textual de Documentos")
        self.setWindowIcon(QIcon(str(asset_path("lupa-icon.png"))))
        self.resize(1280, 860)
        self.setStyleSheet(STYLE)

        self.pdf_files: List[str] = []
        self.results: List[dict] = []
        self.worker_thread = None
        self.worker = None
        self._term_labels: List[str] = []
        self.corpus_analyses = {}
        self.metadata_overrides = {}
        self.entity_aliases = {}
        self.coding_records = []
        self.language = i18n.DEFAULT_LANGUAGE

        self._build_ui()
        self._build_menu()
        self._apply_language()
        self._check_tesseract()

    def _build_menu(self):
        menubar = self.menuBar()
        # Menu styling comes from the global stylesheet (styles.STYLE).
        self.file_menu = menubar.addMenu("&Arquivo")
        self.act_add = QAction("Adicionar documentos...", self)
        self.act_add.setShortcut("Ctrl+O")
        self.act_add.triggered.connect(self.browse_files)
        self.file_menu.addAction(self.act_add)

        self.act_open_project = QAction("Abrir projeto...", self)
        self.act_open_project.setShortcut("Ctrl+Shift+O")
        self.act_open_project.triggered.connect(self.open_project)
        self.file_menu.addAction(self.act_open_project)

        self.act_save_project = QAction("Salvar projeto...", self)
        self.act_save_project.setShortcut("Ctrl+S")
        self.act_save_project.triggered.connect(self.save_project)
        self.file_menu.addAction(self.act_save_project)

        self.file_menu.addSeparator()

        self.act_export = QAction("Exportar resultados...", self)
        self.act_export.setShortcut("Ctrl+E")
        self.act_export.triggered.connect(self.export_results)
        self.file_menu.addAction(self.act_export)

        self.file_menu.addSeparator()
        self.act_exit = QAction("Sair", self)
        self.act_exit.setShortcut("Ctrl+Q")
        self.act_exit.triggered.connect(self.close)
        self.file_menu.addAction(self.act_exit)

        self.help_menu = menubar.addMenu("Aj&uda")
        self.act_help = QAction("Como usar", self)
        self.act_help.setShortcut("F1")
        self.act_help.triggered.connect(self.show_help)
        self.help_menu.addAction(self.act_help)

        self.act_about = QAction("Sobre", self)
        self.act_about.triggered.connect(self.show_about)
        self.help_menu.addAction(self.act_about)

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.navigation = NavigationSidebar()
        self.navigation.page_requested.connect(self.show_workspace)
        self.navigation.help_requested.connect(self.show_help)
        layout.addWidget(self.navigation)

        content = QFrame()
        content.setObjectName("WorkbenchContent")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        layout.addWidget(content, stretch=1)

        self.workspace_header = WorkspaceHeader()
        self.workspace_header.help_requested.connect(self.show_help)
        self.workspace_header.language_requested.connect(self.toggle_language)
        content_layout.addWidget(self.workspace_header)

        self.workspace_stack = QStackedWidget()
        self.workspace_stack.setObjectName("WorkspaceStack")
        self.setup_workspace = SetupWorkspace()
        self.results_workspace = ResultsWorkspace()
        self.charts_workspace = ChartWorkspace([])
        self.charts_workspace.document_requested.connect(self.open_result_by_filename)

        self.workspace_stack.addWidget(self.setup_workspace)
        self.workspace_stack.addWidget(self.results_workspace)
        self.workspace_stack.addWidget(self.charts_workspace)
        self.set_results_navigation_enabled(False)
        content_layout.addWidget(self.workspace_stack, stretch=1)

        self.setup_workspace.add_requested.connect(self.browse_files)
        self.setup_workspace.clear_requested.connect(self.clear_files)
        self.setup_workspace.process_requested.connect(self.start_processing)
        self.setup_workspace.cancel_requested.connect(self.cancel_processing)
        self.setup_workspace.methodology_requested.connect(self.show_help)
        self.setup_workspace.search_help_requested.connect(self.show_help)
        self.setup_workspace.files_dropped.connect(self.add_files)
        self.results_workspace.export_requested.connect(self.export_results)
        self.results_workspace.details_requested.connect(self.open_selected_details)
        self.results_workspace.charts_requested.connect(self.open_charts)
        self.results_workspace.review_requested.connect(self.review_selected_metadata)
        self.results_workspace.coding_import_requested.connect(self.import_coding)

        self.drop_zone = self.setup_workspace.drop_zone
        self.btn_add = self.setup_workspace.btn_add
        self.btn_clear = self.setup_workspace.btn_clear
        self.ocr_checkbox = self.setup_workspace.ocr_checkbox
        self.sentiment_checkbox = self.setup_workspace.sentiment_checkbox
        self.emotions_checkbox = self.setup_workspace.emotions_checkbox
        self.president_checkbox = self.setup_workspace.president_checkbox
        self.textmetrics_checkbox = self.setup_workspace.textmetrics_checkbox
        self.kwic_checkbox = self.setup_workspace.kwic_checkbox
        self.btn_methodology = self.setup_workspace.btn_methodology
        self.file_list = self.setup_workspace.file_list
        self.terms_input = self.setup_workspace.terms_input
        self.btn_process = self.setup_workspace.btn_process
        self.btn_cancel = self.setup_workspace.btn_cancel
        self.progress = self.setup_workspace.progress

        self.btn_export = self.results_workspace.btn_export
        self.btn_details = self.results_workspace.btn_details
        self.btn_review = self.results_workspace.btn_review
        self.btn_charts = self.results_workspace.btn_charts
        self.results_table = self.results_workspace.results_table
        self.results_table.cellDoubleClicked.connect(self.open_result_details)
        self.results_table.itemSelectionChanged.connect(self._selection_changed)
        self._rebuild_results_table([])

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage(self._text("Pronto. Pressione F1 para ajuda.", "Ready. Press F1 for help."))

    def show_help(self):
        dlg = HelpDialog(self, language=self.language)
        dlg.exec()

    def open_result_details(self, row: int, _col: int = 0):
        if 0 <= row < len(self.results):
            dlg = ResultDetailDialog(self.results[row], self, language=self.language)
            dlg.exec()

    def open_selected_details(self):
        self.open_result_details(self.results_table.currentRow())

    def toggle_language(self):
        self.language = "en" if self.language == "pt" else "pt"
        self._apply_language()
        self._refresh_result_views()
        self.status_bar.showMessage(
            self._text("Idioma alterado para português.", "Language changed to English.")
        )

    def _apply_language(self):
        self.setWindowTitle(
            self._text("Lupa — Análise Textual de Documentos", "Lupa — Document Text Analysis")
        )
        if hasattr(self, "file_menu"):
            self.file_menu.setTitle(self._text("&Arquivo", "&File"))
            self.act_add.setText(self._text("Adicionar documentos...", "Add documents..."))
            self.act_open_project.setText(self._text("Abrir projeto...", "Open project..."))
            self.act_save_project.setText(self._text("Salvar projeto...", "Save project..."))
            self.act_export.setText(self._text("Exportar resultados...", "Export results..."))
            self.act_exit.setText(self._text("Sair", "Exit"))
            self.help_menu.setTitle(self._text("Aj&uda", "&Help"))
            self.act_help.setText(self._text("Como usar", "How to use"))
            self.act_about.setText(self._text("Sobre", "About"))
        for widget in (
            getattr(self, "navigation", None),
            getattr(self, "workspace_header", None),
            getattr(self, "setup_workspace", None),
            getattr(self, "results_workspace", None),
            getattr(self, "charts_workspace", None),
        ):
            if widget and hasattr(widget, "set_language"):
                widget.set_language(self.language)
        if hasattr(self, "results_table"):
            self._rebuild_results_table(
                getattr(self, "_search_terms", []),
                getattr(self, "_categories", []),
            )

    def _text(self, pt: str, en: str) -> str:
        return en if self.language == "en" else pt

    def _selection_changed(self):
        enabled = bool(self.results) and self.results_table.currentRow() >= 0
        self.btn_details.setEnabled(enabled)
        self.btn_review.setEnabled(enabled)

    def review_selected_metadata(self):
        row = self.results_table.currentRow()
        if not (0 <= row < len(self.results)):
            return
        dialog = MetadataEditorDialog(self.results[row], self, language=self.language)
        if not dialog.exec():
            return
        override = dialog.override()
        key = self.pdf_files[row] if row < len(self.pdf_files) else self.results[row].get("filename", "")
        self.metadata_overrides = {**self.metadata_overrides, key: override}
        self.results = [
            apply_metadata_override(result, override) if index == row else result
            for index, result in enumerate(self.results)
        ]
        self._refresh_result_views()
        self.status_bar.showMessage(
            self._text(
                "Metadados revisados e sínteses recalculadas.",
                "Metadata reviewed and summaries recalculated.",
            )
        )

    def _refresh_result_views(self):
        self._rebuild_results_table(getattr(self, "_search_terms", []), getattr(self, "_categories", []))
        for index, result in enumerate(self.results, start=1):
            self._add_result_row(index, result)
        self.results_workspace.set_results_summary(self.results)
        self.corpus_analyses = build_corpus_analyses(self.results, self.entity_aliases)
        self.results_workspace.set_corpus_analyses(self.corpus_analyses)
        self.charts_workspace.set_results(self.results)

    def import_coding(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            self._text("Importar codificação humana", "Import human coding"),
            "",
            self._text("CSV (*.csv);;Todos os arquivos (*)", "CSV (*.csv);;All files (*)"),
        )
        if not path:
            return
        try:
            records = import_codings_csv(path)
            self.coding_records = [dict(record) for record in records]
            alpha = krippendorff_alpha_nominal(records)
            by_code = krippendorff_alpha_by_code(records)
            disagreements = coding_disagreements(records)
            details = "\n".join(f"{code}: {value:.3f}" for code, value in by_code.items())
            QMessageBox.information(
                self,
                self._text("Confiabilidade da codificação", "Coding reliability"),
                self._text(
                    f"Krippendorff Alpha total: {alpha:.3f}\n\nPor código:\n{details or '(sem códigos)'}"
                    f"\n\nUnidades com divergência: {len(disagreements)}",
                    f"Krippendorff alpha total: {alpha:.3f}\n\nBy code:\n{details or '(no codes)'}"
                    f"\n\nUnits with disagreement: {len(disagreements)}",
                ),
            )
            self.status_bar.showMessage(
                self._text(
                    f"Codificação importada: {len(records)} registros; alpha {alpha:.3f}.",
                    f"Coding imported: {len(records)} records; alpha {alpha:.3f}.",
                )
            )
        except Exception as error:
            QMessageBox.critical(self, self._text("Erro na codificação", "Coding error"), str(error))

    def open_charts(self):
        if self.results:
            self.show_workspace(2)

    def show_workspace(self, index: int) -> None:
        if not self.navigation.buttons[index].isEnabled():
            return
        self.workspace_stack.setCurrentIndex(index)
        self.navigation.set_current_index(index)
        self.workspace_header.set_page(index)

    def set_results_navigation_enabled(self, enabled: bool) -> None:
        self.navigation.set_page_enabled(1, enabled)
        self.navigation.set_page_enabled(2, enabled)

    def open_result_by_filename(self, filename: str):
        for row, result in enumerate(self.results):
            if result.get("filename") == filename:
                self.open_result_details(row)
                return

    def show_about(self):
        QMessageBox.about(
            self,
            self._text("Sobre — Lupa", "About — Lupa"),
            "<h3>Lupa</h3>"
            + self._text(
                "<p>Análise de conteúdo e métricas textuais de documentos para pesquisa acadêmica.</p>"
                "<p>Versão 1.0.1 — sentimento (LeIA/VADER-PT), legibilidade, "
                "diversidade lexical, palavras-chave, concordância KWIC, busca de "
                "termos e OCR Tesseract.</p>",
                "<p>Content analysis and textual metrics for academic document research.</p>"
                "<p>Version 1.0.1 — sentiment (LeIA/VADER-PT), readability, "
                "lexical diversity, keywords, KWIC concordance, term search and "
                "Tesseract OCR.</p>",
            )
            + "<hr>"
            + self._text("<p><b>Autoria</b></p>", "<p><b>Authors</b></p>")
            + "<ul style='margin-left:8px;'>"
            "<li>Adriano Marques Gonçalves — Universidade de Araraquara (UNIARA)</li>"
            "<li>Thaís Angeli — Secretaria de Educação de Araraquara</li>"
            "</ul>",
        )

    def save_project(self):
        path, _ = QFileDialog.getSaveFileName(
            self,
            self._text("Salvar projeto", "Save project"),
            "projeto.lupa.json",
            self._text("Projeto Lupa (*.lupa.json);;JSON (*.json)", "Lupa Project (*.lupa.json);;JSON (*.json)"),
        )
        if not path:
            return
        try:
            save_project(
                path,
                {
                    "termos_raw": self.terms_input.toPlainText(),
                    "flags": {
                        "ocr": self.ocr_checkbox.isChecked(),
                        "sentimento": self.sentiment_checkbox.isChecked(),
                        "emocoes": self.emotions_checkbox.isChecked(),
                        "presidente": False,
                        "metricas": self.textmetrics_checkbox.isChecked(),
                        "kwic": self.kwic_checkbox.isChecked(),
                    },
                    "arquivos": self.pdf_files,
                    "metadata_overrides": self.metadata_overrides,
                    "entity_aliases": self.entity_aliases,
                    "count_mode": "integral",
                    "online_metadata": False,
                    "coding_records": self.coding_records,
                },
            )
            self.status_bar.showMessage(self._text(f"Projeto salvo: {path}", f"Project saved: {path}"))
        except Exception as e:
            QMessageBox.critical(self, self._text("Erro ao salvar projeto", "Error saving project"), str(e))

    def open_project(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            self._text("Abrir projeto", "Open project"),
            "",
            self._text("Projeto Lupa (*.lupa.json);;JSON (*.json)", "Lupa Project (*.lupa.json);;JSON (*.json)"),
        )
        if not path:
            return
        try:
            project = load_project(path)
            flags = project.get("flags", {})
            self.metadata_overrides = dict(project.get("metadata_overrides", {}))
            self.entity_aliases = dict(project.get("entity_aliases", {}))
            self.coding_records = list(project.get("coding_records", []))
            self.terms_input.setPlainText(project.get("termos_raw", ""))
            self.ocr_checkbox.setChecked(bool(flags.get("ocr", True)))
            self.sentiment_checkbox.setChecked(bool(flags.get("sentimento", True)))
            self.emotions_checkbox.setChecked(bool(flags.get("emocoes", True)))
            self.president_checkbox.setChecked(False)
            self.textmetrics_checkbox.setChecked(bool(flags.get("metricas", True)))
            self.kwic_checkbox.setChecked(bool(flags.get("kwic", True)))
            self.clear_files()
            self.add_files(project.get("arquivos", []))
            missing = project.get("ausentes", [])
            if missing:
                QMessageBox.warning(
                    self,
                    self._text("Arquivos ausentes", "Missing files"),
                    self._text(
                        "Alguns arquivos do projeto não foram encontrados:\n\n",
                        "Some project files were not found:\n\n",
                    )
                    + "\n".join(missing),
                )
            self.status_bar.showMessage(self._text(f"Projeto aberto: {path}", f"Project opened: {path}"))
        except Exception as e:
            QMessageBox.critical(self, self._text("Erro ao abrir projeto", "Error opening project"), str(e))

    def _check_tesseract(self):
        if configure_tesseract():
            self.status_bar.showMessage(
                self._text(
                    "Tesseract detectado — OCR disponível. F1 para ajuda.",
                    "Tesseract detected — OCR available. F1 for help.",
                )
            )
        else:
            self.ocr_checkbox.setChecked(False)
            self.ocr_checkbox.setEnabled(False)
            self.status_bar.showMessage(
                self._text(
                    "Tesseract não encontrado — OCR desabilitado. F1 para ajuda.",
                    "Tesseract not found — OCR disabled. F1 for help.",
                )
            )

    def browse_files(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self,
            self._text("Selecionar documentos", "Select documents"),
            "",
            self._text(
                "Documentos (*.pdf *.docx *.txt);;PDF (*.pdf);;Word (*.docx);;Texto (*.txt)",
                "Documents (*.pdf *.docx *.txt);;PDF (*.pdf);;Word (*.docx);;Text (*.txt)",
            ),
        )
        if paths:
            self.add_files(paths)

    def add_files(self, paths: List[str]):
        added = 0
        for p in paths:
            if p not in self.pdf_files and p.lower().endswith(SUPPORTED_EXTENSIONS):
                self.pdf_files.append(p)
                item = QListWidgetItem(Path(p).name)
                item.setToolTip(p)
                self.file_list.addItem(item)
                added += 1
        self.setup_workspace.set_file_count(len(self.pdf_files))
        self.status_bar.showMessage(
            self._text(
                f"{added} arquivo(s) adicionado(s). Total: {len(self.pdf_files)}",
                f"{added} file(s) added. Total: {len(self.pdf_files)}",
            )
        )

    def clear_files(self):
        self.pdf_files.clear()
        self.file_list.clear()
        self.results.clear()
        self.corpus_analyses = {}
        self.results_table.setRowCount(0)
        self.setup_workspace.set_file_count(0)
        self.results_workspace.set_results_summary([])
        self.results_workspace.set_corpus_analyses({})
        self.charts_workspace.set_results([])
        self.btn_export.setEnabled(False)
        self.btn_charts.setEnabled(False)
        self.btn_details.setEnabled(False)
        self.btn_review.setEnabled(False)
        self.set_results_navigation_enabled(False)
        self.show_workspace(0)
        self.workspace_header.set_context("CORPUS OFFLINE")
        self.status_bar.showMessage(self._text("Lista limpa.", "List cleared."))

    def start_processing(self):
        if not self.pdf_files:
            QMessageBox.warning(
                self,
                self._text("Nenhum arquivo", "No file"),
                self._text("Adicione documentos antes de processar.", "Add documents before processing."),
            )
            return

        search_terms, categories = parse_input(self.terms_input.toPlainText())
        self._search_terms = search_terms
        self._categories = categories
        self._enable_sentiment = self.sentiment_checkbox.isChecked()
        self._enable_emotions = self.emotions_checkbox.isChecked()
        self._enable_president = False
        self._enable_textmetrics = self.textmetrics_checkbox.isChecked()
        self._enable_kwic = self.kwic_checkbox.isChecked()
        self._rebuild_results_table(search_terms, categories)

        self.results.clear()
        self.results_workspace.set_results_summary([])
        self.results_workspace.set_corpus_analyses({})
        self.charts_workspace.set_results([])
        self.set_results_navigation_enabled(False)
        self.btn_process.setEnabled(False)
        self.btn_cancel.setEnabled(True)
        self.btn_add.setEnabled(False)
        self.btn_clear.setEnabled(False)
        self.btn_export.setEnabled(False)
        self.btn_charts.setEnabled(False)
        self.btn_review.setEnabled(False)
        self.progress.setVisible(True)
        self.progress.setRange(0, len(self.pdf_files) * 100)
        self.progress.setValue(0)
        self.setup_workspace.processing_label.setText(
            self._text("Preparando análise...", "Preparing analysis...")
        )
        self.workspace_header.set_context("PROCESSANDO")

        self.worker_thread = QThread()
        self.worker = ProcessingWorker(
            self.pdf_files.copy(),
            enable_ocr=self.ocr_checkbox.isChecked(),
            search_terms=search_terms,
            enable_sentiment=self._enable_sentiment,
            enable_emotions=self._enable_emotions,
            enable_president=self._enable_president,
            enable_textmetrics=self._enable_textmetrics,
            enable_kwic=self._enable_kwic,
            categories=categories,
        )
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.started.connect(self.worker.run)
        self.worker.file_started.connect(self.on_file_started)
        self.worker.file_progress.connect(self.on_file_progress)
        self.worker.file_finished.connect(self.on_file_finished)
        self.worker.all_finished.connect(self.on_all_finished)
        self.worker.error.connect(self.on_error)
        self.worker_thread.start()

    def _rebuild_results_table(self, search_terms, categories=None):
        self._president_on = False
        base_headers = ["#", "Arquivo", "Título", "Autores", "Afiliações", "Ano", "Tipo"]
        base_widths = [40, 220, 240, 210, 230, 70, 170]
        if self._president_on:
            base_headers.append("Presidente")
            base_widths.append(190)
        base_headers += ["Páginas", "Palavras (PDF)", "Palavras (Corpus)", "Confiança"]
        base_widths += [80, 130, 150, 90]

        self._sentiment_on = getattr(self, "_enable_sentiment", False)
        if self._sentiment_on:
            base_headers += ["Sentimento", "Comp. médio"]
            base_widths += [110, 100]
        self._sentiment_cols = 2 if self._sentiment_on else 0

        self._category_names = [name for name, _members in (categories or [])]
        for name in self._category_names:
            base_headers.append(f"{name}\n(Corpus)")

        self._term_labels = []
        for term, exact in search_terms:
            label = f'"{term}"' if exact else term
            self._term_labels.append(label)
            base_headers.append(f"{label}\n(Corpus)")

        self.results_table.setColumnCount(len(base_headers))
        self.results_table.setHorizontalHeaderLabels(
            [i18n.label(header, self.language) for header in base_headers]
        )
        self.results_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Interactive
        )
        self.results_table.setRowCount(0)
        widths = (
            base_widths
            + [120] * len(self._category_names)
            + [110] * len(self._term_labels)
        )
        for i, w in enumerate(widths):
            self.results_table.setColumnWidth(i, w)

    def cancel_processing(self):
        if self.worker:
            self.worker.cancel()
        self.status_bar.showMessage(self._text("Cancelando...", "Cancelling..."))
        self.setup_workspace.processing_label.setText(
            self._text("Cancelando processamento...", "Cancelling processing...")
        )

    def on_file_started(self, idx: int, filename: str):
        self.setup_workspace.processing_label.setText(
            f"{Path(filename).name} · {idx + 1}/{len(self.pdf_files)}"
        )
        self.status_bar.showMessage(
            self._text(
                f"Processando {Path(filename).name} ({idx + 1}/{len(self.pdf_files)})...",
                f"Processing {Path(filename).name} ({idx + 1}/{len(self.pdf_files)})...",
            )
        )

    def on_file_progress(self, file_idx: int, current: int, total: int):
        per_file = (current / total) * 100 if total else 100
        overall = file_idx * 100 + per_file
        self.progress.setValue(int(overall))

    def on_file_finished(self, idx: int, result: dict):
        source = self.pdf_files[idx] if idx < len(self.pdf_files) else result.get("filename", "")
        override = self.metadata_overrides.get(source)
        if override:
            result = apply_metadata_override(result, override)
        self.results.append(result)
        self._add_result_row(idx + 1, result)
        self.results_workspace.set_results_summary(self.results)

    def on_all_finished(self, results: List[dict]):
        final_results = list(self.results)
        self.worker_thread.quit()
        self.worker_thread.wait()
        self.btn_process.setEnabled(True)
        self.btn_cancel.setEnabled(False)
        self.btn_add.setEnabled(True)
        self.btn_clear.setEnabled(True)
        self.btn_export.setEnabled(len(final_results) > 0)
        self.btn_charts.setEnabled(bool(final_results))
        self.progress.setVisible(False)
        self.results_workspace.set_results_summary(final_results)
        self.corpus_analyses = build_corpus_analyses(final_results, self.entity_aliases)
        self.results_workspace.set_corpus_analyses(self.corpus_analyses)
        self.charts_workspace.set_results(final_results)
        self.set_results_navigation_enabled(bool(final_results))
        if final_results:
            self.show_workspace(1)
        self.setup_workspace.processing_label.setText(
            self._text("Processamento concluído", "Processing complete")
        )
        self.workspace_header.set_context(f"{len(final_results)} DOCUMENTOS")
        self.status_bar.showMessage(
            self._text(
                f"Concluído. {len(final_results)} arquivo(s) processado(s).",
                f"Complete. {len(final_results)} file(s) processed.",
            )
        )

    def on_error(self, idx: int, path: str, error_msg: str):
        self.setup_workspace.processing_label.setText(
            self._text("Falha no processamento", "Processing failed")
        )
        QMessageBox.critical(
            self,
            self._text("Erro no processamento", "Processing error"),
            f"{Path(path).name}:\n\n{error_msg}",
        )

    def _add_result_row(self, doc_id: int, result: dict):
        row = self.results_table.rowCount()
        self.results_table.insertRow(row)
        words_total_str = f"{result['words_total']:,}".replace(",", ".")
        words_corpus_str = f"{result['words_analytical']:,}".replace(",", ".")
        cells = [
            str(doc_id),
            result["filename"],
            result.get("title", ""),
            result.get("authors_display", ""),
            result.get("affiliations_display", ""),
            result["year"],
            i18n.value(result["document"], self.language),
        ]
        if getattr(self, "_president_on", False):
            cells.append(result["president"])
        cells += [
            str(result["total_pages"]),
            words_total_str,
            words_corpus_str,
            result["confidence"],
        ]
        conf_col = len(cells) - 1
        for col, value in enumerate(cells):
            display_value = i18n.value(value, self.language) if col == conf_col else value
            item = QTableWidgetItem(str(display_value))
            if col == conf_col:
                if value == "Alto":
                    item.setForeground(QColor("#15803d"))
                elif value == "Médio":
                    item.setForeground(QColor("#b5670a"))
                else:
                    item.setForeground(QColor("#b4413c"))
            self.results_table.setItem(row, col, item)

        next_col = len(cells)
        if getattr(self, "_sentiment_cols", 0):
            classe = result.get("sent_classe", "")
            item_cls = QTableWidgetItem(i18n.value(classe, self.language))
            item_cls.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if classe == "Positivo":
                item_cls.setForeground(QColor("#15803d"))
            elif classe == "Negativo":
                item_cls.setForeground(QColor("#b4413c"))
            self.results_table.setItem(row, next_col, item_cls)

            comp = QTableWidgetItem(str(result.get("sent_compound_medio", "")))
            comp.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.results_table.setItem(row, next_col + 1, comp)
            next_col += self._sentiment_cols

        category_results = result.get("category_results", {})
        for name in getattr(self, "_category_names", []):
            count = category_results.get(name, {}).get("analytical", 0)
            item = QTableWidgetItem(str(count))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setForeground(QColor("#0f766e"))
            self.results_table.setItem(row, next_col, item)
            next_col += 1

        term_results = result.get("term_results", {})
        for i, label in enumerate(self._term_labels):
            count = term_results.get(label, {}).get("analytical", 0)
            item = QTableWidgetItem(str(count))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.results_table.setItem(row, next_col + i, item)

    def export_results(self):
        if not self.results:
            QMessageBox.information(
                self,
                self._text("Sem resultados", "No results"),
                self._text(
                    "Processe ao menos um documento antes de exportar.",
                    "Process at least one document before exporting.",
                ),
            )
            return
        path, selected_filter = QFileDialog.getSaveFileName(
            self,
            self._text("Salvar resultados", "Save results"),
            "contagem_palavras",
            "Excel (*.xlsx);;CSV (*.csv);;JSON (*.json)",
        )
        if not path:
            return
        try:
            path_obj = Path(path)
            if not path_obj.suffix:
                if "CSV" in selected_filter:
                    path_obj = path_obj.with_suffix(".csv")
                elif "JSON" in selected_filter:
                    path_obj = path_obj.with_suffix(".json")
                else:
                    path_obj = path_obj.with_suffix(".xlsx")

            analyzers = build_default_analyzers(
                getattr(self, "_search_terms", []),
                detect_president=False,
                detect_sentiment=getattr(self, "_enable_sentiment", True),
                detect_emotions=getattr(self, "_enable_emotions", True),
                detect_textmetrics=getattr(self, "_enable_textmetrics", True),
                detect_kwic=getattr(self, "_enable_kwic", True),
                categories=getattr(self, "_categories", []),
            )
            column_specs = i18n.column_specs(build_column_specs(analyzers), self.language)
            methodology_options = self._methodology_options()
            methodology_options = {**methodology_options, "language": self.language}
            suffix = path_obj.suffix.lower()
            if suffix == ".csv":
                output_dir = path_obj.with_suffix("")
                export_to_csv(
                    self.results,
                    output_dir,
                    column_specs,
                    methodology_options=methodology_options,
                    language=self.language,
                )
                exported_to = str(output_dir)
                message = self._text(
                    f"Arquivos CSV salvos em:\n{exported_to}",
                    f"CSV files saved to:\n{exported_to}",
                )
            elif suffix == ".json":
                export_to_json(
                    self.results,
                    path_obj,
                    methodology_options=methodology_options,
                    language=self.language,
                )
                exported_to = str(path_obj)
                message = self._text(
                    f"Arquivo JSON salvo em:\n{exported_to}",
                    f"JSON file saved to:\n{exported_to}",
                )
            else:
                export_to_xlsx(
                    self.results,
                    path_obj,
                    column_specs,
                    methodology_options=methodology_options,
                    language=self.language,
                )
                exported_to = str(path_obj)
                message = self._text(
                    f"Arquivo XLSX salvo em:\n{exported_to}",
                    f"XLSX file saved to:\n{exported_to}",
                )
            QMessageBox.information(self, self._text("Exportado", "Exported"), message)
            self.status_bar.showMessage(self._text(f"Exportado: {exported_to}", f"Exported: {exported_to}"))
        except Exception as e:
            QMessageBox.critical(self, self._text("Erro ao exportar", "Export error"), str(e))

    def _methodology_options(self):
        return {
            "termos_raw": self.terms_input.toPlainText(),
            "arquivos": list(self.pdf_files),
            "flags": {
                "ocr": self.ocr_checkbox.isChecked(),
                "sentimento": getattr(self, "_enable_sentiment", self.sentiment_checkbox.isChecked()),
                "emocoes": getattr(self, "_enable_emotions", self.emotions_checkbox.isChecked()),
                "presidente": False,
                "metricas": getattr(self, "_enable_textmetrics", self.textmetrics_checkbox.isChecked()),
                "kwic": getattr(self, "_enable_kwic", self.kwic_checkbox.isChecked()),
            },
        }
