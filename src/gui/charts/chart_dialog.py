"""Interactive chart center for the current Lupa result set."""

import csv
import io
from typing import Dict, List

from PyQt6.QtCore import QSignalBlocker, Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.core.chart_data import (
    build_corpus_chart,
    build_comparison_chart,
    build_cooccurrence_heatmap,
    build_lexical_scatter,
    build_sentiment_chart,
    build_temporal_chart,
    build_territory_chart,
    chart_options,
    chart_to_rows,
    filter_results,
)
from src.core.corpus_analysis import build_corpus_analyses
from src.gui import i18n

from .chart_canvas import ChartCanvas


class ChartWorkspace(QWidget):
    document_requested = pyqtSignal(str)

    def __init__(self, results: List[Dict], parent=None):
        super().__init__(parent)
        self.setMinimumSize(760, 540)
        self.results = list(results)
        self.corpus_analyses = build_corpus_analyses(self.results)
        self.options = chart_options(self.results)
        self._updating = False
        self.language = i18n.DEFAULT_LANGUAGE

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        content = QHBoxLayout()
        content.setSpacing(14)
        content.addWidget(self._build_controls())
        self.canvas = ChartCanvas()
        self.canvas.point_clicked.connect(self._on_chart_clicked)
        content.addWidget(self.canvas, stretch=1)
        layout.addLayout(content, stretch=1)

        bottom = QHBoxLayout()
        self.status = QLabel("Passe o mouse sobre o gráfico para ver valores exatos.")
        self.status.setStyleSheet("color: #6b7280;")
        self.status.setWordWrap(True)
        bottom.addWidget(self.status, stretch=1)
        self.reset_button = QPushButton("Redefinir zoom")
        self.reset_button.clicked.connect(self.canvas.reset_zoom)
        self.copy_button = QPushButton("Copiar dados")
        self.copy_button.clicked.connect(self._copy_data)
        self.export_button = QPushButton("Exportar PNG")
        self.export_button.clicked.connect(self._export_png)
        for button in (self.reset_button, self.copy_button, self.export_button):
            bottom.addWidget(button)
        layout.addLayout(bottom)
        self._refresh_chart()

    def set_language(self, language: str) -> None:
        self.language = i18n.normalize_language(language)
        english = self.language == "en"
        self.canvas.set_language(self.language)
        self.status.setText(
            "Hover over the chart to inspect exact values."
            if english
            else "Passe o mouse sobre o gráfico para ver valores exatos."
        )
        self.reset_button.setText("Reset zoom" if english else "Redefinir zoom")
        self.copy_button.setText("Copy data" if english else "Copiar dados")
        self.export_button.setText("Export PNG" if english else "Exportar PNG")
        self.normalize.setText("Normalize per thousand words" if english else "Normalizar por mil palavras")
        self._translate_combos()

    def set_results(self, results: List[Dict]) -> None:
        """Replace the corpus displayed by an embedded chart workspace."""
        self.results = list(results)
        self.corpus_analyses = build_corpus_analyses(self.results)
        self.options = chart_options(self.results)
        self._updating = True
        self.year_filter.clear()
        self.year_filter.addItem("All years" if self.language == "en" else "Todos os anos", "")
        for year in self.options["years"]:
            self.year_filter.addItem(year, year)
        self.document_filter.clear()
        self.document_filter.addItem("All documents" if self.language == "en" else "Todos os documentos", "")
        for filename in self.options["filenames"]:
            self.document_filter.addItem(filename, filename)
        self.temporal_metrics.clear()
        self._populate_temporal_metrics()
        self.territory_type.clear()
        self.territory_type.addItem("All types" if self.language == "en" else "Todos os tipos", "")
        for item_type in self.options["territory_types"]:
            self.territory_type.addItem(item_type, item_type)
        self._updating = False
        self._comparison_kind_changed()

    def _build_controls(self) -> QWidget:
        panel = QWidget()
        panel.setFixedWidth(280)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(7)

        layout.addWidget(self._label("GRÁFICO"))
        self.chart_type = QComboBox()
        self.chart_type.addItem("Série temporal", "temporal")
        self.chart_type.addItem("Comparação entre documentos", "comparison")
        self.chart_type.addItem("Sentimento", "sentiment")
        self.chart_type.addItem("Dispersão lexical", "scatter")
        self.chart_type.addItem("Matriz de coocorrência", "cooccurrence")
        self.chart_type.addItem("Perfil territorial", "territory")
        self.chart_type.addItem("Autores", "authors")
        self.chart_type.addItem("Instituições", "institutions")
        self.chart_type.addItem("Dispersão de termos", "dispersion")
        self.chart_type.addItem("Termos distintivos", "keyness")
        self.chart_type.addItem("Similaridade documental", "similarity")
        self.chart_type.addItem("Associação normalizada", "association")
        self.chart_type.addItem("Mudança lexical temporal", "temporal_change")
        self.chart_type.addItem("Diagnóstico de sentimento", "sentiment_diagnostics")
        self.chart_type.currentIndexChanged.connect(self._controls_changed)
        layout.addWidget(self.chart_type)

        layout.addWidget(self._label("FILTROS"))
        self.year_filter = QComboBox()
        self.year_filter.addItem("Todos os anos", "")
        for year in self.options["years"]:
            self.year_filter.addItem(year, year)
        self.year_filter.currentIndexChanged.connect(self._refresh_chart)
        layout.addWidget(self.year_filter)

        self.document_filter = QComboBox()
        self.document_filter.addItem("Todos os documentos", "")
        for filename in self.options["filenames"]:
            self.document_filter.addItem(filename, filename)
        self.document_filter.currentIndexChanged.connect(self._refresh_chart)
        layout.addWidget(self.document_filter)

        self.normalize = QCheckBox("Normalizar por mil palavras")
        self.normalize.stateChanged.connect(self._refresh_chart)
        layout.addWidget(self.normalize)

        self.temporal_group = QWidget()
        temporal_layout = QVBoxLayout(self.temporal_group)
        temporal_layout.setContentsMargins(0, 0, 0, 0)
        temporal_layout.addWidget(self._label("SÉRIES TEMPORAIS"))
        self.temporal_metrics = QListWidget()
        self.temporal_metrics.setFixedHeight(190)
        self.temporal_metrics.itemChanged.connect(self._refresh_chart)
        temporal_layout.addWidget(self.temporal_metrics)
        self._populate_temporal_metrics()
        layout.addWidget(self.temporal_group)

        self.comparison_group = QWidget()
        comparison_layout = QVBoxLayout(self.comparison_group)
        comparison_layout.setContentsMargins(0, 0, 0, 0)
        comparison_layout.addWidget(self._label("INDICADOR"))
        self.comparison_kind = QComboBox()
        for label, key in (
            ("Palavras do corpus", "words"),
            ("Termo", "term"),
            ("Categoria", "category"),
            ("Território", "territory"),
            ("Emoção", "emotion"),
            ("Palavra-chave", "keyword"),
        ):
            self.comparison_kind.addItem(label, key)
        self.comparison_kind.currentIndexChanged.connect(self._comparison_kind_changed)
        comparison_layout.addWidget(self.comparison_kind)
        self.comparison_key = QComboBox()
        self.comparison_key.currentIndexChanged.connect(self._refresh_chart)
        comparison_layout.addWidget(self.comparison_key)
        layout.addWidget(self.comparison_group)

        self.sentiment_group = QWidget()
        sentiment_layout = QVBoxLayout(self.sentiment_group)
        sentiment_layout.setContentsMargins(0, 0, 0, 0)
        sentiment_layout.addWidget(self._label("AGRUPAR SENTIMENTO"))
        self.sentiment_grouping = QComboBox()
        self.sentiment_grouping.addItem("Por documento", "document")
        self.sentiment_grouping.addItem("Por ano", "year")
        self.sentiment_grouping.currentIndexChanged.connect(self._refresh_chart)
        sentiment_layout.addWidget(self.sentiment_grouping)
        layout.addWidget(self.sentiment_group)

        self.territory_group = QWidget()
        territory_layout = QVBoxLayout(self.territory_group)
        territory_layout.setContentsMargins(0, 0, 0, 0)
        territory_layout.addWidget(self._label("TIPO TERRITORIAL"))
        self.territory_type = QComboBox()
        self.territory_type.addItem("Todos os tipos", "")
        for item_type in self.options["territory_types"]:
            self.territory_type.addItem(item_type, item_type)
        self.territory_type.currentIndexChanged.connect(self._refresh_chart)
        territory_layout.addWidget(self.territory_type)
        layout.addWidget(self.territory_group)

        self.legend_label = self._label("LEGENDA")
        layout.addWidget(self.legend_label)
        self.legend = QListWidget()
        self.legend.setFixedHeight(112)
        self.legend.itemChanged.connect(self._legend_changed)
        layout.addWidget(self.legend)
        layout.addStretch()
        self._comparison_kind_changed()
        self._update_control_visibility()
        return panel

    def _populate_temporal_metrics(self):
        metrics = [
            ("Palavras", "base", "words_analytical"),
            ("Sentimento médio", "base", "sent_compound_medio"),
            ("Legibilidade média", "base", "leg_indice_medio"),
            ("% positivas", "base", "sent_pct_positivo"),
            ("% negativas", "base", "sent_pct_negativo"),
        ]
        metrics.extend((f"Termo: {key}", "terms", key) for key in self.options["terms"])
        metrics.extend(
            (f"Categoria: {key}", "categories", key)
            for key in self.options["categories"]
        )
        for index, metric in enumerate(metrics):
            item = QListWidgetItem(metric[0])
            item.setData(Qt.ItemDataRole.UserRole, metric)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Checked if index == 0 else Qt.CheckState.Unchecked)
            self.temporal_metrics.addItem(item)

    def _comparison_kind_changed(self):
        kind = self.comparison_kind.currentData()
        keys = {
            "term": self.options["terms"],
            "category": self.options["categories"],
            "territory": self.options["territories"],
            "emotion": self.options["emotions"],
            "keyword": self.options["keywords"],
        }.get(kind, ())
        self._updating = True
        self.comparison_key.clear()
        for key in keys:
            self.comparison_key.addItem(key, key)
        self.comparison_key.setVisible(kind != "words")
        self._updating = False
        self._update_control_visibility()
        self._refresh_chart()

    def _controls_changed(self):
        self._update_control_visibility()
        self._refresh_chart()

    def _update_control_visibility(self):
        chart_type = self.chart_type.currentData()
        self.temporal_group.setVisible(chart_type == "temporal")
        self.comparison_group.setVisible(chart_type == "comparison")
        self.sentiment_group.setVisible(chart_type == "sentiment")
        self.territory_group.setVisible(chart_type == "territory")
        self.normalize.setVisible(chart_type in {"temporal", "comparison"})
        can_normalize = chart_type == "temporal" or (
            chart_type == "comparison"
            and self.comparison_kind.currentData()
            in {"term", "category", "territory", "keyword"}
        )
        self.normalize.setEnabled(can_normalize)
        if chart_type == "comparison" and not can_normalize:
            blocker = QSignalBlocker(self.normalize)
            self.normalize.setChecked(False)
            del blocker

    def _refresh_chart(self):
        if self._updating or not hasattr(self, "canvas"):
            return
        results = filter_results(
            self.results,
            year=self.year_filter.currentData() or "",
            filename=self.document_filter.currentData() or "",
        )
        chart_type = self.chart_type.currentData()
        if chart_type == "temporal":
            metrics = tuple(
                self.temporal_metrics.item(index).data(Qt.ItemDataRole.UserRole)
                for index in range(self.temporal_metrics.count())
                if self.temporal_metrics.item(index).checkState() == Qt.CheckState.Checked
            )
            data = build_temporal_chart(
                results,
                metrics=metrics or (("Palavras", "base", "words_analytical"),),
                normalized=self.normalize.isChecked(),
            )
        elif chart_type == "comparison":
            data = build_comparison_chart(
                results,
                self.comparison_kind.currentData(),
                self.comparison_key.currentData() or "",
                normalized=self.normalize.isChecked(),
            )
        elif chart_type == "sentiment":
            data = build_sentiment_chart(results, self.sentiment_grouping.currentData())
        elif chart_type == "scatter":
            data = build_lexical_scatter(results)
        elif chart_type == "cooccurrence":
            data = build_cooccurrence_heatmap(results)
        elif chart_type == "territory":
            data = build_territory_chart(results, self.territory_type.currentData() or "")
        else:
            data = build_corpus_chart(build_corpus_analyses(results), chart_type)
        self.canvas.set_data(data)
        self._rebuild_legend(data)
        self.status.setText(
            "Hover over the chart to inspect exact values."
            if self.language == "en"
            else "Passe o mouse sobre o gráfico para ver valores exatos."
        )

    def _rebuild_legend(self, data):
        self._updating = True
        self.legend.clear()
        for series in data.series:
            item = QListWidgetItem(series.name)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Checked)
            self.legend.addItem(item)
        show_legend = len(data.series) > 1
        self.legend_label.setVisible(show_legend)
        self.legend.setVisible(show_legend)
        self._updating = False

    def _legend_changed(self):
        if self._updating:
            return
        hidden = {
            self.legend.item(index).text()
            for index in range(self.legend.count())
            if self.legend.item(index).checkState() != Qt.CheckState.Checked
        }
        self.canvas.set_hidden_series(hidden)

    def _copy_data(self):
        rows = chart_to_rows(self.canvas.visible_data())
        stream = io.StringIO()
        writer = csv.writer(stream, delimiter=";", lineterminator="\n")
        writer.writerows(rows)
        QApplication.clipboard().setText(stream.getvalue())
        self.status.setText(
            "Displayed data copied to the clipboard."
            if self.language == "en"
            else "Dados exibidos copiados para a área de transferência."
        )

    def _export_png(self):
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Export chart" if self.language == "en" else "Exportar gráfico",
            "grafico.png",
            "PNG image (*.png)" if self.language == "en" else "Imagem PNG (*.png)",
        )
        if not path:
            return
        if not path.lower().endswith(".png"):
            path += ".png"
        if self.canvas.export_png(path):
            self.status.setText(
                f"Chart exported: {path}" if self.language == "en" else f"Gráfico exportado: {path}"
            )
        else:
            QMessageBox.critical(
                self,
                "Export error" if self.language == "en" else "Erro ao exportar",
                "Could not save the PNG." if self.language == "en" else "Não foi possível salvar o PNG.",
            )

    def _on_chart_clicked(self, metadata: Dict[str, str]):
        filename = metadata.get("filename")
        if filename:
            self.status.setText(
                f"Opening details for {filename}." if self.language == "en" else f"Abrindo detalhes de {filename}."
            )
            self.document_requested.emit(filename)
            return
        if metadata.get("term_a"):
            self.status.setText(
                f"{metadata['term_a']} × {metadata['term_b']}: {metadata.get('count', '0')} "
                + ("sentences" if self.language == "en" else "sentenças")
            )
            return
        if metadata.get("year"):
            self.status.setText(
                f"Selected year: {metadata['year']}" if self.language == "en" else f"Ano selecionado: {metadata['year']}"
            )

    def _translate_combos(self) -> None:
        english = self.language == "en"
        chart_labels = {
            "temporal": ("Série temporal", "Time series"),
            "comparison": ("Comparação entre documentos", "Document comparison"),
            "sentiment": ("Sentimento", "Sentiment"),
            "scatter": ("Dispersão lexical", "Lexical scatter"),
            "cooccurrence": ("Matriz de coocorrência", "Co-occurrence matrix"),
            "territory": ("Perfil territorial", "Territorial profile"),
            "authors": ("Autores", "Authors"),
            "institutions": ("Instituições", "Institutions"),
            "dispersion": ("Dispersão de termos", "Term dispersion"),
            "keyness": ("Termos distintivos", "Distinctive terms"),
            "similarity": ("Similaridade documental", "Document similarity"),
            "association": ("Associação normalizada", "Normalized association"),
            "temporal_change": ("Mudança lexical temporal", "Temporal lexical change"),
            "sentiment_diagnostics": ("Diagnóstico de sentimento", "Sentiment diagnostics"),
        }
        for index in range(self.chart_type.count()):
            pt, en = chart_labels.get(
                self.chart_type.itemData(index),
                (self.chart_type.itemText(index), self.chart_type.itemText(index)),
            )
            self.chart_type.setItemText(index, en if english else pt)
        comparison_labels = {
            "words": ("Palavras do corpus", "Corpus words"),
            "term": ("Termo", "Term"),
            "category": ("Categoria", "Category"),
            "territory": ("Território", "Territory"),
            "emotion": ("Emoção", "Emotion"),
            "keyword": ("Palavra-chave", "Keyword"),
        }
        for index in range(self.comparison_kind.count()):
            pt, en = comparison_labels.get(
                self.comparison_kind.itemData(index),
                (self.comparison_kind.itemText(index), self.comparison_kind.itemText(index)),
            )
            self.comparison_kind.setItemText(index, en if english else pt)
        for index in range(self.sentiment_grouping.count()):
            data = self.sentiment_grouping.itemData(index)
            text = {"document": "By document", "year": "By year"} if english else {"document": "Por documento", "year": "Por ano"}
            self.sentiment_grouping.setItemText(index, text.get(data, self.sentiment_grouping.itemText(index)))

    @staticmethod
    def _label(text: str) -> QLabel:
        label = QLabel(text)
        label.setStyleSheet(
            "color: #b5670a; font-size: 8pt; font-weight: 700; padding-top: 5px;"
        )
        return label


class ChartDialog(QDialog):
    document_requested = pyqtSignal(str)

    def __init__(self, results: List[Dict], parent=None, language: str = i18n.DEFAULT_LANGUAGE):
        super().__init__(parent)
        self.language = i18n.normalize_language(language)
        self.setWindowTitle("Interactive charts - Lupa" if self.language == "en" else "Gráficos interativos - Lupa")
        self.resize(1240, 780)
        self.setMinimumSize(980, 640)
        self.setStyleSheet("QDialog { background-color: #f4f1ea; }")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 12)
        self.workspace = ChartWorkspace(results, self)
        self.workspace.set_language(self.language)
        self.workspace.document_requested.connect(self.document_requested.emit)
        layout.addWidget(self.workspace, stretch=1)
        button_row = QHBoxLayout()
        button_row.addStretch()
        close = QPushButton("Close" if self.language == "en" else "Fechar")
        close.clicked.connect(self.accept)
        button_row.addWidget(close)
        layout.addLayout(button_row)
