"""Per-document result detail dialog.

Lets the researcher inspect everything that goes into the XLSX without leaving
the application: summary metrics, sentiment sentence by sentence, keyword
frequencies, KWIC concordance lines and excluded pages.
"""

from typing import Dict, List

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QDialog,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

POSITIVE_COLOR = QColor("#15803d")
NEGATIVE_COLOR = QColor("#b4413c")

_TAB_STYLE = """
QTabWidget::pane {
    border: 1px solid #e4ddcf;
    border-radius: 10px;
    background: #ffffff;
    top: -1px;
}
QTabBar::tab {
    background: #ece6da;
    color: #3b454f;
    padding: 8px 18px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    margin-right: 3px;
    font-weight: 600;
}
QTabBar::tab:selected {
    background: #0f766e;
    color: #ffffff;
}
QTabBar::tab:hover:!selected {
    background: #e0d9c9;
}
"""


def _fmt(value) -> str:
    if isinstance(value, int):
        return f"{value:,}".replace(",", ".")
    return str(value)


class ResultDetailDialog(QDialog):
    def __init__(self, result: Dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Detalhes — {result.get('filename', '')}")
        self.resize(1020, 720)
        self.setStyleSheet("QDialog { background-color: #f4f1ea; }")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        tabs = QTabWidget()
        tabs.setStyleSheet(_TAB_STYLE)
        tabs.addTab(self._build_summary_tab(result), "Resumo")

        sentences = result.get("sentiment_sentences", [])
        if sentences:
            tabs.addTab(self._build_sentences_tab(sentences), "Sentimento por sentença")

        keywords = result.get("keyword_freq", [])
        if keywords:
            tabs.addTab(self._build_keywords_tab(keywords), "Palavras-chave")

        ngrams = result.get("ngram_freq", [])
        if ngrams:
            tabs.addTab(self._build_ngrams_tab(ngrams), "N-gramas")

        emotions = result.get("emotion_words", {})
        if any(emotions.values()):
            tabs.addTab(self._build_emotions_tab(emotions), "Emoções")

        categories = result.get("category_results", {})
        if categories:
            tabs.addTab(self._build_categories_tab(categories), "Categorias")

        geography = result.get("geo_mentions", [])
        if geography:
            tabs.addTab(self._build_geography_tab(geography), "Território")

        kwic = result.get("kwic", [])
        if kwic:
            tabs.addTab(self._build_kwic_tab(kwic), "Concordância (KWIC)")

        cooccurrence = result.get("cooccurrence", [])
        if cooccurrence:
            tabs.addTab(self._build_cooccurrence_tab(cooccurrence), "Co-ocorrência")

        excluded = result.get("excluded_pages", [])
        if excluded:
            tabs.addTab(self._build_excluded_tab(excluded), "Páginas excluídas")

        layout.addWidget(tabs)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_close = QPushButton("Fechar")
        btn_close.setStyleSheet(
            "QPushButton { background-color: #0f766e; color: #ffffff; border: none;"
            " border-radius: 9px; padding: 10px 24px; font-weight: 600; min-width: 100px; }"
            "QPushButton:hover { background-color: #0d9488; }"
        )
        btn_close.clicked.connect(self.accept)
        btn_row.addWidget(btn_close)
        layout.addLayout(btn_row)

    # ---- tabs -----------------------------------------------------------

    def _build_summary_tab(self, result: Dict) -> QWidget:
        rows = [
            ("Arquivo", result.get("filename", "")),
            ("Ano", result.get("year", "")),
            ("Tipo de documento", result.get("document", "")),
            ("Presidente", result.get("president", "")),
            ("Total de páginas", result.get("total_pages", "")),
            ("Páginas com texto", result.get("pages_with_text", "")),
            ("Páginas com OCR", result.get("ocr_pages_count", "")),
            ("Palavras (PDF completo)", result.get("words_total", "")),
            ("Palavras (corpus analítico)", result.get("words_analytical", "")),
            ("Grau de confiança", result.get("confidence", "")),
        ]
        if "sent_classe" in result:
            rows += [
                ("Sentimento (classe)", result.get("sent_classe", "")),
                ("Sentimento (composto médio)", result.get("sent_compound_medio", "")),
                ("% sentenças positivas", result.get("sent_pct_positivo", "")),
                ("% sentenças negativas", result.get("sent_pct_negativo", "")),
                ("% sentenças neutras", result.get("sent_pct_neutro", "")),
                ("Nº de sentenças analisadas", result.get("sent_n_sentencas", "")),
            ]
        if "leg_indice" in result:
            rows += [
                ("Legibilidade Flesch-PT", result.get("leg_indice", "")),
                ("Legibilidade (classe)", result.get("leg_classe", "")),
                ("Palavras por frase", result.get("leg_palavras_frase", "")),
                ("Sílabas por palavra", result.get("leg_silabas_palavra", "")),
                ("Diversidade lexical (TTR)", result.get("lex_ttr", "")),
                ("Índice de Guiraud", result.get("lex_guiraud", "")),
                ("Vocabulário (tipos)", result.get("lex_vocabulario", "")),
            ]
        rows.append(("Observações", result.get("observations", "")))

        container = QWidget()
        grid = QGridLayout(container)
        grid.setContentsMargins(22, 18, 22, 18)
        grid.setHorizontalSpacing(28)
        grid.setVerticalSpacing(8)
        for i, (label, value) in enumerate(rows):
            lab = QLabel(label)
            lab.setStyleSheet("color: #b5670a; font-weight: 700;")
            val = QLabel(_fmt(value))
            val.setWordWrap(True)
            val.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            grid.addWidget(lab, i, 0, alignment=Qt.AlignmentFlag.AlignTop)
            grid.addWidget(val, i, 1)
        grid.setColumnStretch(1, 1)
        grid.setRowStretch(len(rows), 1)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(container)
        scroll.setStyleSheet("QScrollArea { border: none; background: #ffffff; }")
        return scroll

    def _build_sentences_tab(self, sentences: List[Dict]) -> QWidget:
        table = self._make_table(["Página", "Sentença", "Composto", "Classe"])
        table.setRowCount(len(sentences))
        for i, s in enumerate(sentences):
            table.setItem(i, 0, self._cell(str(s.get("page", "")), center=True))
            table.setItem(i, 1, self._cell(s.get("text", "")))
            table.setItem(i, 2, self._cell(str(s.get("compound", "")), center=True))
            classe_item = self._cell(s.get("classe", ""), center=True)
            if s.get("classe") == "Positivo":
                classe_item.setForeground(POSITIVE_COLOR)
            elif s.get("classe") == "Negativo":
                classe_item.setForeground(NEGATIVE_COLOR)
            table.setItem(i, 3, classe_item)
        table.setColumnWidth(0, 70)
        table.setColumnWidth(2, 90)
        table.setColumnWidth(3, 90)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        return table

    def _build_keywords_tab(self, keywords: List) -> QWidget:
        table = self._make_table(["Palavra", "Frequência"])
        table.setRowCount(len(keywords))
        for i, (word, count) in enumerate(keywords):
            table.setItem(i, 0, self._cell(word))
            table.setItem(i, 1, self._cell(str(count), center=True))
        table.setColumnWidth(0, 320)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        return table

    def _build_ngrams_tab(self, ngrams: List) -> QWidget:
        table = self._make_table(["Expressão", "N", "Frequência"])
        table.setRowCount(len(ngrams))
        for i, (phrase, n, count) in enumerate(ngrams):
            table.setItem(i, 0, self._cell(phrase))
            table.setItem(i, 1, self._cell(str(n), center=True))
            table.setItem(i, 2, self._cell(str(count), center=True))
        table.setColumnWidth(0, 380)
        table.setColumnWidth(1, 60)
        table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        return table

    def _build_emotions_tab(self, emotions: Dict) -> QWidget:
        rows = [
            (emotion, word, count)
            for emotion, words in emotions.items()
            for word, count in words
        ]
        table = self._make_table(["Emoção", "Palavra", "Contagem"])
        table.setRowCount(len(rows))
        for i, (emotion, word, count) in enumerate(rows):
            table.setItem(i, 0, self._cell(emotion))
            table.setItem(i, 1, self._cell(word))
            table.setItem(i, 2, self._cell(str(count), center=True))
        table.setColumnWidth(0, 180)
        table.setColumnWidth(2, 100)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        return table

    def _build_categories_tab(self, categories: Dict) -> QWidget:
        rows = []
        for name, data in categories.items():
            rows.append(
                (name, "(total da categoria)", data["total"], data["analytical"], True)
            )
            for label, counts in data.get("members", {}).items():
                rows.append((name, label, counts["total"], counts["analytical"], False))
        table = self._make_table(
            ["Categoria", "Termo", "PDF Completo", "Corpus Analítico"]
        )
        table.setRowCount(len(rows))
        for i, (name, label, total, analytical, is_total) in enumerate(rows):
            cells = [
                self._cell(name),
                self._cell(label),
                self._cell(str(total), center=True),
                self._cell(str(analytical), center=True),
            ]
            for j, cell in enumerate(cells):
                if is_total:
                    cell.setForeground(QColor("#115e59"))
                    font = cell.font()
                    font.setBold(True)
                    cell.setFont(font)
                table.setItem(i, j, cell)
        table.setColumnWidth(0, 220)
        table.setColumnWidth(1, 260)
        table.setColumnWidth(2, 130)
        table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        return table

    def _build_geography_tab(self, mentions: List) -> QWidget:
        table = self._make_table(["Local", "Tipo", "UF", "Contagem"])
        table.setRowCount(len(mentions))
        for i, (name, place_type, uf, count) in enumerate(mentions):
            table.setItem(i, 0, self._cell(name))
            table.setItem(i, 1, self._cell(place_type, center=True))
            table.setItem(i, 2, self._cell(uf, center=True))
            table.setItem(i, 3, self._cell(str(count), center=True))
        table.setColumnWidth(1, 140)
        table.setColumnWidth(2, 70)
        table.setColumnWidth(3, 100)
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        return table

    def _build_kwic_tab(self, kwic: List[Dict]) -> QWidget:
        table = self._make_table(
            [
                "Página",
                "Termo",
                "Contexto à esquerda",
                "Ocorrência",
                "Contexto à direita",
            ]
        )
        table.setRowCount(len(kwic))
        for i, line in enumerate(kwic):
            table.setItem(i, 0, self._cell(str(line.get("page", "")), center=True))
            table.setItem(i, 1, self._cell(line.get("term", ""), center=True))
            left = self._cell(line.get("left", ""))
            left.setTextAlignment(
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            )
            table.setItem(i, 2, left)
            kw = self._cell(line.get("keyword", ""), center=True)
            kw.setForeground(QColor("#0f766e"))
            table.setItem(i, 3, kw)
            table.setItem(i, 4, self._cell(line.get("right", "")))
        table.setColumnWidth(0, 70)
        table.setColumnWidth(1, 120)
        table.setColumnWidth(3, 130)
        header = table.horizontalHeader()
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        return table

    def _build_cooccurrence_tab(self, rows: List) -> QWidget:
        table = self._make_table(["Termo A", "Termo B", "Sentenças"])
        table.setRowCount(len(rows))
        for i, (term_a, term_b, count) in enumerate(rows):
            table.setItem(i, 0, self._cell(term_a))
            table.setItem(i, 1, self._cell(term_b))
            table.setItem(i, 2, self._cell(str(count), center=True))
        table.setColumnWidth(2, 110)
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        return table

    def _build_excluded_tab(self, excluded: List[Dict]) -> QWidget:
        table = self._make_table(["Página", "Motivo da exclusão", "Palavras na página"])
        table.setRowCount(len(excluded))
        for i, page in enumerate(excluded):
            table.setItem(
                i, 0, self._cell(str(page.get("page_number", "")), center=True)
            )
            table.setItem(i, 1, self._cell(page.get("exclusion_reason", "")))
            table.setItem(
                i, 2, self._cell(str(page.get("word_count", "")), center=True)
            )
        table.setColumnWidth(0, 70)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        return table

    # ---- helpers --------------------------------------------------------

    def _make_table(self, headers: List[str]) -> QTableWidget:
        table = QTableWidget(0, len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setAlternatingRowColors(True)
        table.verticalHeader().setVisible(False)
        table.setWordWrap(True)
        return table

    def _cell(self, text: str, center: bool = False) -> QTableWidgetItem:
        item = QTableWidgetItem(text)
        if center:
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        return item
