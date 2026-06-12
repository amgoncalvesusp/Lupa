"""Corpus temporal summary dialog."""

from typing import Dict, List

from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from src.core.corpus_summary import build_corpus_summary


class CorpusSummaryDialog(QDialog):
    def __init__(self, results: List[Dict], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Síntese do corpus")
        self.resize(920, 620)
        self.setStyleSheet("QDialog { background-color: #f4f1ea; }")
        self.summary = build_corpus_summary(results)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(10)

        top = QHBoxLayout()
        top.addWidget(QLabel("Indicador"))
        self.metric_combo = QComboBox()
        self.metric_combo.addItem("Palavras (Corpus)", ("base", "words_analytical"))
        for label in self._term_labels():
            self.metric_combo.addItem(f"Termo: {label}", ("terms", label))
        for name in self._category_names():
            self.metric_combo.addItem(f"Categoria: {name}", ("categories", name))
        self.metric_combo.currentIndexChanged.connect(self._refresh_table)
        top.addWidget(self.metric_combo)
        top.addStretch()
        layout.addLayout(top)

        self.table = QTableWidget()
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        close = QPushButton("Fechar")
        close.clicked.connect(self.accept)
        btn_row.addWidget(close)
        layout.addLayout(btn_row)
        self._refresh_table()

    def _refresh_table(self):
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(
            [
                "Ano",
                "Docs",
                "Palavras",
                "Sent. médio",
                "Legib. média",
                "% positivas",
                "% negativas",
                self.metric_combo.currentText(),
            ]
        )
        self.table.setRowCount(len(self.summary))
        metric_type, metric_key = self.metric_combo.currentData()
        for row_idx, (_year, data) in enumerate(self.summary.items()):
            values = [
                data["year"],
                data["docs"],
                data["words_analytical"],
                data["sent_compound_medio"],
                data["leg_indice_medio"],
                data["sent_pct_positivo"],
                data["sent_pct_negativo"],
                self._metric_value(data, metric_type, metric_key),
            ]
            for col_idx, value in enumerate(values):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))
        self.table.resizeColumnsToContents()

    def _metric_value(self, data: Dict, metric_type: str, metric_key: str):
        if metric_type == "base":
            return data.get(metric_key, 0)
        return data.get(metric_type, {}).get(metric_key, 0)

    def _term_labels(self):
        labels = []
        for data in self.summary.values():
            for label in data["terms"]:
                if label not in labels:
                    labels.append(label)
        return labels

    def _category_names(self):
        names = []
        for data in self.summary.values():
            for name in data["categories"]:
                if name not in names:
                    names.append(name)
        return names
