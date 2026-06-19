"""Main application window."""

from pathlib import Path
from typing import List

from PyQt6.QtCore import Qt, QThread
from PyQt6.QtGui import QAction, QColor
from PyQt6.QtWidgets import (
    QFileDialog,
    QHeaderView,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QStatusBar,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from src.gui.styles import STYLE
from src.gui.workers import ProcessingWorker
from src.gui.help_dialog import HelpDialog
from src.gui.detail_dialog import ResultDetailDialog
from src.gui.charts import ChartWorkspace
from src.gui.workspace import (
    ApplicationHeader,
    ResultsWorkspace,
    SetupWorkspace,
    SUPPORTED_EXTENSIONS,
)
from src.core.analysis import build_column_specs, build_default_analyzers
from src.core.exporter import export_to_xlsx
from src.core.exporter_plain import export_to_csv, export_to_json
from src.core.ocr_engine import configure_tesseract
from src.core.project_io import load_project, save_project
from src.core.term_search import parse_input

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lupa — Análise Textual de Documentos")
        self.resize(1280, 860)
        self.setStyleSheet(STYLE)

        self.pdf_files: List[str] = []
        self.results: List[dict] = []
        self.worker_thread = None
        self.worker = None
        self._term_labels: List[str] = []

        self._build_ui()
        self._build_menu()
        self._check_tesseract()

    def _build_menu(self):
        menubar = self.menuBar()
        # Menu styling comes from the global stylesheet (styles.STYLE).
        file_menu = menubar.addMenu("&Arquivo")
        act_add = QAction("Adicionar documentos...", self)
        act_add.setShortcut("Ctrl+O")
        act_add.triggered.connect(self.browse_files)
        file_menu.addAction(act_add)

        act_open_project = QAction("Abrir projeto...", self)
        act_open_project.setShortcut("Ctrl+Shift+O")
        act_open_project.triggered.connect(self.open_project)
        file_menu.addAction(act_open_project)

        act_save_project = QAction("Salvar projeto...", self)
        act_save_project.setShortcut("Ctrl+S")
        act_save_project.triggered.connect(self.save_project)
        file_menu.addAction(act_save_project)

        file_menu.addSeparator()

        act_export = QAction("Exportar resultados...", self)
        act_export.setShortcut("Ctrl+E")
        act_export.triggered.connect(self.export_results)
        file_menu.addAction(act_export)

        file_menu.addSeparator()
        act_exit = QAction("Sair", self)
        act_exit.setShortcut("Ctrl+Q")
        act_exit.triggered.connect(self.close)
        file_menu.addAction(act_exit)

        help_menu = menubar.addMenu("Aj&uda")
        act_help = QAction("Como usar", self)
        act_help.setShortcut("F1")
        act_help.triggered.connect(self.show_help)
        help_menu.addAction(act_help)

        act_about = QAction("Sobre", self)
        act_about.triggered.connect(self.show_about)
        help_menu.addAction(act_about)

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.app_header = ApplicationHeader()
        self.app_header.help_requested.connect(self.show_help)
        layout.addWidget(self.app_header)

        self.workspace_tabs = QTabWidget()
        self.workspace_tabs.setObjectName("WorkspaceTabs")
        self.setup_workspace = SetupWorkspace()
        self.results_workspace = ResultsWorkspace()
        self.charts_workspace = ChartWorkspace([])
        self.charts_workspace.document_requested.connect(self.open_result_by_filename)

        self.workspace_tabs.addTab(self.setup_workspace, "Corpus")
        self.workspace_tabs.addTab(self.results_workspace, "Resultados")
        self.workspace_tabs.addTab(self.charts_workspace, "Gráficos")
        self.workspace_tabs.setTabEnabled(1, False)
        self.workspace_tabs.setTabEnabled(2, False)
        layout.addWidget(self.workspace_tabs, stretch=1)

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
        self.btn_charts = self.results_workspace.btn_charts
        self.results_table = self.results_workspace.results_table
        self.results_table.cellDoubleClicked.connect(self.open_result_details)
        self.results_table.itemSelectionChanged.connect(
            lambda: self.btn_details.setEnabled(
                bool(self.results) and self.results_table.currentRow() >= 0
            )
        )
        self._rebuild_results_table([])

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Pronto. Pressione F1 para ajuda.")

    def show_help(self):
        dlg = HelpDialog(self)
        dlg.exec()

    def open_result_details(self, row: int, _col: int = 0):
        if 0 <= row < len(self.results):
            dlg = ResultDetailDialog(self.results[row], self)
            dlg.exec()

    def open_selected_details(self):
        self.open_result_details(self.results_table.currentRow())

    def open_charts(self):
        if self.results:
            self.workspace_tabs.setCurrentIndex(2)

    def open_result_by_filename(self, filename: str):
        for row, result in enumerate(self.results):
            if result.get("filename") == filename:
                self.open_result_details(row)
                return

    def show_about(self):
        QMessageBox.about(
            self,
            "Sobre — Lupa",
            "<h3>Lupa</h3>"
            "<p>Análise de conteúdo e métricas textuais de documentos para pesquisa acadêmica.</p>"
            "<p>Versão 1.0 — sentimento (LeIA/VADER-PT), legibilidade, "
            "diversidade lexical, palavras-chave, concordância KWIC, busca de "
            "termos e OCR Tesseract.</p>"
            "<hr>"
            "<p><b>Autoria</b></p>"
            "<ul style='margin-left:8px;'>"
            "<li>Adriano Marques Gonçalves</li>"
            "<li>Thaís Angeli</li>"
            "</ul>"
            "<p><i>Programa de Pós-graduação em Desenvolvimento Territorial "
            "e Meio Ambiente — UNIARA</i></p>",
        )

    def save_project(self):
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Salvar projeto",
            "projeto.lupa.json",
            "Projeto Lupa (*.lupa.json);;JSON (*.json)",
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
                        "presidente": self.president_checkbox.isChecked(),
                        "metricas": self.textmetrics_checkbox.isChecked(),
                        "kwic": self.kwic_checkbox.isChecked(),
                    },
                    "arquivos": self.pdf_files,
                },
            )
            self.status_bar.showMessage(f"Projeto salvo: {path}")
        except Exception as e:
            QMessageBox.critical(self, "Erro ao salvar projeto", str(e))

    def open_project(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Abrir projeto",
            "",
            "Projeto Lupa (*.lupa.json);;JSON (*.json)",
        )
        if not path:
            return
        try:
            project = load_project(path)
            flags = project.get("flags", {})
            self.terms_input.setPlainText(project.get("termos_raw", ""))
            self.ocr_checkbox.setChecked(bool(flags.get("ocr", True)))
            self.sentiment_checkbox.setChecked(bool(flags.get("sentimento", True)))
            self.emotions_checkbox.setChecked(bool(flags.get("emocoes", True)))
            self.president_checkbox.setChecked(bool(flags.get("presidente", True)))
            self.textmetrics_checkbox.setChecked(bool(flags.get("metricas", True)))
            self.kwic_checkbox.setChecked(bool(flags.get("kwic", True)))
            self.clear_files()
            self.add_files(project.get("arquivos", []))
            missing = project.get("ausentes", [])
            if missing:
                QMessageBox.warning(
                    self,
                    "Arquivos ausentes",
                    "Alguns arquivos do projeto não foram encontrados:\n\n"
                    + "\n".join(missing),
                )
            self.status_bar.showMessage(f"Projeto aberto: {path}")
        except Exception as e:
            QMessageBox.critical(self, "Erro ao abrir projeto", str(e))

    def _check_tesseract(self):
        if configure_tesseract():
            self.status_bar.showMessage(
                "Tesseract detectado — OCR disponível. F1 para ajuda."
            )
        else:
            self.ocr_checkbox.setChecked(False)
            self.ocr_checkbox.setEnabled(False)
            self.status_bar.showMessage(
                "Tesseract não encontrado — OCR desabilitado. F1 para ajuda."
            )

    def browse_files(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Selecionar documentos",
            "",
            "Documentos (*.pdf *.docx *.txt);;PDF (*.pdf);;Word (*.docx);;Texto (*.txt)",
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
            f"{added} arquivo(s) adicionado(s). Total: {len(self.pdf_files)}"
        )

    def clear_files(self):
        self.pdf_files.clear()
        self.file_list.clear()
        self.results.clear()
        self.results_table.setRowCount(0)
        self.setup_workspace.set_file_count(0)
        self.results_workspace.set_results_summary([])
        self.charts_workspace.set_results([])
        self.btn_export.setEnabled(False)
        self.btn_charts.setEnabled(False)
        self.btn_details.setEnabled(False)
        self.workspace_tabs.setTabEnabled(1, False)
        self.workspace_tabs.setTabEnabled(2, False)
        self.workspace_tabs.setCurrentIndex(0)
        self.app_header.context.setText("CORPUS OFFLINE")
        self.status_bar.showMessage("Lista limpa.")

    def start_processing(self):
        if not self.pdf_files:
            QMessageBox.warning(
                self, "Nenhum arquivo", "Adicione documentos antes de processar."
            )
            return

        search_terms, categories = parse_input(self.terms_input.toPlainText())
        self._search_terms = search_terms
        self._categories = categories
        self._enable_sentiment = self.sentiment_checkbox.isChecked()
        self._enable_emotions = self.emotions_checkbox.isChecked()
        self._enable_president = self.president_checkbox.isChecked()
        self._enable_textmetrics = self.textmetrics_checkbox.isChecked()
        self._enable_kwic = self.kwic_checkbox.isChecked()
        self._rebuild_results_table(search_terms, categories)

        self.results.clear()
        self.results_workspace.set_results_summary([])
        self.charts_workspace.set_results([])
        self.workspace_tabs.setTabEnabled(1, False)
        self.workspace_tabs.setTabEnabled(2, False)
        self.btn_process.setEnabled(False)
        self.btn_cancel.setEnabled(True)
        self.btn_add.setEnabled(False)
        self.btn_clear.setEnabled(False)
        self.btn_export.setEnabled(False)
        self.btn_charts.setEnabled(False)
        self.progress.setVisible(True)
        self.progress.setRange(0, len(self.pdf_files) * 100)
        self.progress.setValue(0)
        self.setup_workspace.processing_label.setText("Preparando análise...")
        self.app_header.context.setText("PROCESSANDO")

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
        self._president_on = getattr(self, "_enable_president", True)
        base_headers = ["#", "Arquivo", "Ano", "Tipo"]
        base_widths = [40, 260, 70, 170]
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
        self.results_table.setHorizontalHeaderLabels(base_headers)
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
        self.status_bar.showMessage("Cancelando...")
        self.setup_workspace.processing_label.setText("Cancelando processamento...")

    def on_file_started(self, idx: int, filename: str):
        self.setup_workspace.processing_label.setText(
            f"{Path(filename).name} · {idx + 1}/{len(self.pdf_files)}"
        )
        self.status_bar.showMessage(
            f"Processando {Path(filename).name} ({idx + 1}/{len(self.pdf_files)})..."
        )

    def on_file_progress(self, file_idx: int, current: int, total: int):
        per_file = (current / total) * 100 if total else 100
        overall = file_idx * 100 + per_file
        self.progress.setValue(int(overall))

    def on_file_finished(self, idx: int, result: dict):
        self.results.append(result)
        self._add_result_row(idx + 1, result)
        self.results_workspace.set_results_summary(self.results)

    def on_all_finished(self, results: List[dict]):
        self.worker_thread.quit()
        self.worker_thread.wait()
        self.btn_process.setEnabled(True)
        self.btn_cancel.setEnabled(False)
        self.btn_add.setEnabled(True)
        self.btn_clear.setEnabled(True)
        self.btn_export.setEnabled(len(results) > 0)
        self.btn_charts.setEnabled(bool(results))
        self.progress.setVisible(False)
        self.results_workspace.set_results_summary(results)
        self.charts_workspace.set_results(results)
        self.workspace_tabs.setTabEnabled(1, bool(results))
        self.workspace_tabs.setTabEnabled(2, bool(results))
        if results:
            self.workspace_tabs.setCurrentIndex(1)
        self.setup_workspace.processing_label.setText("Processamento concluído")
        self.app_header.context.setText(f"{len(results)} DOCUMENTOS")
        self.status_bar.showMessage(
            f"Concluído. {len(results)} arquivo(s) processado(s)."
        )

    def on_error(self, idx: int, path: str, error_msg: str):
        self.setup_workspace.processing_label.setText("Falha no processamento")
        QMessageBox.critical(
            self, "Erro no processamento", f"{Path(path).name}:\n\n{error_msg}"
        )

    def _add_result_row(self, doc_id: int, result: dict):
        row = self.results_table.rowCount()
        self.results_table.insertRow(row)
        words_total_str = f"{result['words_total']:,}".replace(",", ".")
        words_corpus_str = f"{result['words_analytical']:,}".replace(",", ".")
        cells = [str(doc_id), result["filename"], result["year"], result["document"]]
        if getattr(self, "_president_on", True):
            cells.append(result["president"])
        cells += [
            str(result["total_pages"]),
            words_total_str,
            words_corpus_str,
            result["confidence"],
        ]
        conf_col = len(cells) - 1
        for col, value in enumerate(cells):
            item = QTableWidgetItem(value)
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
            item_cls = QTableWidgetItem(classe)
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
                self, "Sem resultados", "Processe ao menos um documento antes de exportar."
            )
            return
        path, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Salvar resultados",
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
                detect_president=getattr(self, "_enable_president", True),
                detect_sentiment=getattr(self, "_enable_sentiment", True),
                detect_emotions=getattr(self, "_enable_emotions", True),
                detect_textmetrics=getattr(self, "_enable_textmetrics", True),
                detect_kwic=getattr(self, "_enable_kwic", True),
                categories=getattr(self, "_categories", []),
            )
            column_specs = build_column_specs(analyzers)
            methodology_options = self._methodology_options()
            suffix = path_obj.suffix.lower()
            if suffix == ".csv":
                output_dir = path_obj.with_suffix("")
                export_to_csv(
                    self.results,
                    output_dir,
                    column_specs,
                    methodology_options=methodology_options,
                )
                exported_to = str(output_dir)
                message = f"Arquivos CSV salvos em:\n{exported_to}"
            elif suffix == ".json":
                export_to_json(
                    self.results,
                    path_obj,
                    methodology_options=methodology_options,
                )
                exported_to = str(path_obj)
                message = f"Arquivo JSON salvo em:\n{exported_to}"
            else:
                export_to_xlsx(
                    self.results,
                    path_obj,
                    column_specs,
                    methodology_options=methodology_options,
                )
                exported_to = str(path_obj)
                message = f"Arquivo XLSX salvo em:\n{exported_to}"
            QMessageBox.information(self, "Exportado", message)
            self.status_bar.showMessage(f"Exportado: {exported_to}")
        except Exception as e:
            QMessageBox.critical(self, "Erro ao exportar", str(e))

    def _methodology_options(self):
        return {
            "termos_raw": self.terms_input.toPlainText(),
            "arquivos": list(self.pdf_files),
            "flags": {
                "ocr": self.ocr_checkbox.isChecked(),
                "sentimento": getattr(self, "_enable_sentiment", self.sentiment_checkbox.isChecked()),
                "emocoes": getattr(self, "_enable_emotions", self.emotions_checkbox.isChecked()),
                "presidente": getattr(self, "_enable_president", self.president_checkbox.isChecked()),
                "metricas": getattr(self, "_enable_textmetrics", self.textmetrics_checkbox.isChecked()),
                "kwic": getattr(self, "_enable_kwic", self.kwic_checkbox.isChecked()),
            },
        }
