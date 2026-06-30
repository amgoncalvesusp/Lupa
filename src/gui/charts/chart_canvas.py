"""Lightweight interactive QPainter chart canvas."""

import math
from dataclasses import replace
from typing import Dict, List, Set, Tuple

from PyQt6.QtCore import QPointF, QRectF, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QPainter, QPen
from PyQt6.QtWidgets import QToolTip, QWidget

from src.core.chart_data import ChartData
from src.gui import i18n

COLORS = (
    QColor("#0f766e"),
    QColor("#b5670a"),
    QColor("#b4413c"),
    QColor("#3b82a0"),
    QColor("#6b7280"),
    QColor("#7c6f64"),
)
POSITIVE = QColor("#15803d")
NEUTRAL = QColor("#8a8475")
NEGATIVE = QColor("#b4413c")


class ChartCanvas(QWidget):
    point_clicked = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(680, 460)
        self.setMouseTracking(True)
        self._data = ChartData("", "")
        self._hidden_series: Set[str] = set()
        self._hits: List[Tuple[QRectF, Dict[str, str], str]] = []
        self._zoom = 1.0
        self.language = i18n.DEFAULT_LANGUAGE

    @property
    def data(self) -> ChartData:
        return self._data

    def set_data(self, data: ChartData) -> None:
        self._data = data
        self._hidden_series = set()
        self._zoom = 1.0
        self.update()

    def set_hidden_series(self, names: Set[str]) -> None:
        self._hidden_series = set(names)
        self.update()

    def visible_data(self) -> ChartData:
        """Return the chart exactly as currently displayed by the legend."""
        return replace(self._data, series=self._visible_series())

    def reset_zoom(self) -> None:
        self._zoom = 1.0
        self.update()

    def export_png(self, path: str) -> bool:
        return self.grab().save(path, "PNG")

    def set_language(self, language: str) -> None:
        self.language = i18n.normalize_language(language)
        self.update()

    def paintEvent(self, _event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor("#ffffff"))
        self._hits = []
        self._draw_title(painter)
        if not self._has_values():
            painter.setPen(QColor("#6b7280"))
            painter.drawText(
                self.rect(),
                Qt.AlignmentFlag.AlignCenter,
                "No data available for this chart."
                if self.language == "en"
                else "Não há dados disponíveis para este gráfico.",
            )
            return
        if self._data.kind == "line":
            self._draw_line(painter)
        elif self._data.kind == "bar":
            self._draw_bar(painter)
        elif self._data.kind == "stacked":
            self._draw_stacked(painter)
        elif self._data.kind == "scatter":
            self._draw_scatter(painter)
        elif self._data.kind == "heatmap":
            self._draw_heatmap(painter)
        self._draw_legend(painter)

    def mouseMoveEvent(self, event):
        hit = self._hit_at(event.position())
        if hit:
            QToolTip.showText(event.globalPosition().toPoint(), hit[2], self)
            self.setCursor(Qt.CursorShape.PointingHandCursor)
        else:
            QToolTip.hideText()
            self.unsetCursor()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            hit = self._hit_at(event.position())
            if hit:
                self.point_clicked.emit(dict(hit[1]))

    def wheelEvent(self, event):
        factor = 1.15 if event.angleDelta().y() > 0 else 1 / 1.15
        self._zoom = min(3.0, max(0.7, self._zoom * factor))
        self.update()
        event.accept()

    def _has_values(self) -> bool:
        if self._data.kind == "scatter":
            return bool(self._data.points)
        if self._data.kind == "heatmap":
            return bool(self._data.labels)
        return bool(self._data.labels and self._data.series)

    def _plot_rect(self, left: float = 90, bottom: float = 64) -> QRectF:
        return QRectF(left, 64, max(80, self.width() - left - 30), max(80, self.height() - 64 - bottom))

    def _draw_title(self, painter: QPainter) -> None:
        painter.setPen(QColor("#103d3a"))
        font = QFont("Segoe UI", 13)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(
            QRectF(18, 12, self.width() - 36, 30),
            _chart_text(self._data.title, self.language),
        )

    def _draw_axes(self, painter: QPainter, plot: QRectF, min_y: float, max_y: float) -> None:
        painter.setFont(QFont("Segoe UI", 8))
        for step in range(6):
            ratio = step / 5
            y = plot.bottom() - ratio * plot.height()
            value = min_y + ratio * (max_y - min_y)
            painter.setPen(QPen(QColor("#ece6da"), 1))
            painter.drawLine(QPointF(plot.left(), y), QPointF(plot.right(), y))
            painter.setPen(QColor("#6b7280"))
            painter.drawText(QRectF(4, y - 9, plot.left() - 10, 18), Qt.AlignmentFlag.AlignRight, _fmt(value))
        painter.setPen(QPen(QColor("#8a8475"), 1))
        painter.drawLine(plot.bottomLeft(), plot.bottomRight())
        painter.drawLine(plot.topLeft(), plot.bottomLeft())

    def _draw_line(self, painter: QPainter) -> None:
        plot = self._plot_rect()
        visible = self._visible_series()
        values = [value for series in visible for value in series.values]
        min_y, max_y = _range(values, zoom=self._zoom)
        self._draw_axes(painter, plot, min_y, max_y)
        count = len(self._data.labels)
        for idx, label in enumerate(self._data.labels):
            x = plot.left() + (plot.width() * idx / max(1, count - 1))
            painter.setPen(QColor("#5c6670"))
            painter.drawText(QRectF(x - 45, plot.bottom() + 8, 90, 20), Qt.AlignmentFlag.AlignCenter, label)
        for series in visible:
            series_idx = self._data.series.index(series)
            color = COLORS[series_idx % len(COLORS)]
            painter.setPen(QPen(color, 2.5))
            points = []
            for idx, value in enumerate(series.values):
                x = plot.left() + (plot.width() * idx / max(1, count - 1))
                y = _map_y(value, plot, min_y, max_y)
                point = QPointF(x, y)
                points.append(point)
                painter.setBrush(color)
                painter.drawEllipse(point, 4.5, 4.5)
                metadata = _metadata(series, idx)
                tooltip = f"{_chart_text(series.name, self.language)}\n{self._data.labels[idx]}: {_fmt(value)}{self._data.value_suffix}"
                self._hits.append((QRectF(x - 9, y - 9, 18, 18), metadata, tooltip))
            for left, right in zip(points, points[1:]):
                painter.drawLine(left, right)

    def _draw_bar(self, painter: QPainter) -> None:
        labels = self._data.labels
        series = self._visible_series()
        if not series:
            return
        plot = self._plot_rect(left=min(220, max(110, self.width() * 0.24)), bottom=45)
        values = series[0].values
        max_value = max(values or (1.0,)) / self._zoom
        max_value = max(max_value, 1e-9)
        row_height = plot.height() / max(1, len(labels))
        bar_height = min(28.0, row_height * 0.62)
        for idx, (label, value) in enumerate(zip(labels, values)):
            y = plot.top() + idx * row_height + (row_height - bar_height) / 2
            width = min(plot.width(), plot.width() * max(0.0, value) / max_value)
            rect = QRectF(plot.left(), y, max(1.0, width), bar_height)
            painter.setBrush(COLORS[0])
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(rect, 3, 3)
            painter.setPen(QColor("#3b454f"))
            painter.drawText(QRectF(8, y - 2, plot.left() - 16, bar_height + 4), Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, _elide(label, 28))
            painter.drawText(QRectF(rect.right() + 6, y, 90, bar_height), Qt.AlignmentFlag.AlignVCenter, _fmt(value))
            metadata = _metadata(series[0], idx)
            self._hits.append((rect.adjusted(-3, -3, 55, 3), metadata, f"{label}: {_fmt(value)}"))
        painter.setPen(QPen(QColor("#8a8475"), 1))
        painter.drawLine(plot.topLeft(), plot.bottomLeft())

    def _draw_stacked(self, painter: QPainter) -> None:
        plot = self._plot_rect(left=min(220, max(110, self.width() * 0.24)), bottom=45)
        visible = self._visible_series()
        row_height = plot.height() / max(1, len(self._data.labels))
        bar_height = min(30.0, row_height * 0.65)
        colors = {"Positivo": POSITIVE, "Neutro": NEUTRAL, "Negativo": NEGATIVE}
        for idx, label in enumerate(self._data.labels):
            y = plot.top() + idx * row_height + (row_height - bar_height) / 2
            x = plot.left()
            total = sum(max(0.0, series.values[idx]) for series in visible) or 1.0
            painter.setPen(QColor("#3b454f"))
            painter.drawText(QRectF(8, y - 2, plot.left() - 16, bar_height + 4), Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, _elide(label, 28))
            for series in visible:
                value = max(0.0, series.values[idx])
                width = plot.width() * value / total
                rect = QRectF(x, y, width, bar_height)
                painter.setBrush(colors.get(series.name, COLORS[0]))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawRect(rect)
                metadata = {**_metadata(series, idx), "classe": series.name}
                self._hits.append((rect, metadata, f"{label}\n{series.name}: {_fmt(value)}%"))
                x += width

    def _draw_scatter(self, painter: QPainter) -> None:
        plot = self._plot_rect()
        xs = [point.x for point in self._data.points]
        ys = [point.y for point in self._data.points]
        min_x, max_x = _range(xs, zoom=self._zoom)
        min_y, max_y = _range(ys, zoom=self._zoom)
        self._draw_axes(painter, plot, min_y, max_y)
        max_size = max((point.size for point in self._data.points), default=1.0)
        for point in self._data.points:
            x = plot.left() + (point.x - min_x) / max(1e-9, max_x - min_x) * plot.width()
            y = _map_y(point.y, plot, min_y, max_y)
            radius = 6 + 12 * math.sqrt(point.size / max_size)
            color = _sentiment_color(point.value)
            painter.setBrush(color)
            painter.setPen(QPen(QColor("#ffffff"), 1.5))
            painter.drawEllipse(QPointF(x, y), radius, radius)
            metadata = dict(point.metadata)
            tooltip = (
                f"{point.label}\nReadability: {_fmt(point.x)}\nTTR: {_fmt(point.y)}\nWords: {_fmt(point.size)}"
                if self.language == "en"
                else f"{point.label}\nLegibilidade: {_fmt(point.x)}\nTTR: {_fmt(point.y)}\nPalavras: {_fmt(point.size)}"
            )
            self._hits.append((QRectF(x - radius, y - radius, 2 * radius, 2 * radius), metadata, tooltip))

    def _draw_heatmap(self, painter: QPainter) -> None:
        labels = self._data.labels
        count = len(labels)
        left = min(210, max(100, self.width() * 0.2))
        plot = self._plot_rect(left=left, bottom=min(150, 50 + count * 2))
        cell = min(plot.width(), plot.height()) / max(1, count)
        plot = QRectF(plot.left(), plot.top(), cell * count, cell * count)
        max_value = max((value for row in self._data.matrix for value in row), default=1.0) or 1.0
        painter.setFont(QFont("Segoe UI", 8))
        for row_idx, label in enumerate(labels):
            y = plot.top() + row_idx * cell
            painter.setPen(QColor("#3b454f"))
            painter.drawText(QRectF(4, y, plot.left() - 10, cell), Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, _elide(label, 22))
            for col_idx, value in enumerate(self._data.matrix[row_idx]):
                x = plot.left() + col_idx * cell
                rect = QRectF(x, y, cell, cell)
                painter.setBrush(_heat_color(value / max_value))
                painter.setPen(QPen(QColor("#ffffff"), 0.5))
                painter.drawRect(rect)
                if value > 0 and cell >= 24:
                    painter.setPen(QColor("#ffffff") if value / max_value > 0.5 else QColor("#103d3a"))
                    painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, _fmt(value))
                metadata = {"term_a": labels[row_idx], "term_b": labels[col_idx], "count": str(value)}
                unit = "sentences" if self.language == "en" else "sentenças"
                self._hits.append((rect, metadata, f"{labels[row_idx]} × {labels[col_idx]}: {_fmt(value)} {unit}"))
        for col_idx, label in enumerate(labels):
            x = plot.left() + col_idx * cell
            painter.save()
            painter.translate(x + cell / 2, plot.bottom() + 8)
            painter.rotate(45)
            painter.setPen(QColor("#3b454f"))
            painter.drawText(QRectF(0, 0, 120, 18), _elide(label, 18))
            painter.restore()

    def _draw_legend(self, painter: QPainter) -> None:
        if len(self._data.series) <= 1:
            return
        x = self.width() - 175
        y = 16
        colors = {"Positivo": POSITIVE, "Neutro": NEUTRAL, "Negativo": NEGATIVE}
        painter.setFont(QFont("Segoe UI", 8))
        for idx, series in enumerate(self._data.series):
            color = colors.get(series.name, COLORS[idx % len(COLORS)])
            painter.setBrush(color)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRect(QRectF(x, y + idx * 18, 10, 10))
            painter.setPen(QColor("#9ca3af") if series.name in self._hidden_series else QColor("#3b454f"))
            painter.drawText(QRectF(x + 15, y - 3 + idx * 18, 150, 18), _elide(_chart_text(series.name, self.language), 24))

    def _visible_series(self):
        return tuple(
            series for series in self._data.series if series.name not in self._hidden_series
        )

    def _hit_at(self, point: QPointF):
        for hit in reversed(self._hits):
            if hit[0].contains(point):
                return hit
        return None


def _metadata(series, idx: int) -> Dict[str, str]:
    if idx < len(series.metadata):
        return dict(series.metadata[idx])
    return {}


def _range(values, zoom: float = 1.0):
    if not values:
        return 0.0, 1.0
    low, high = min(values), max(values)
    if math.isclose(low, high):
        pad = max(1.0, abs(low) * 0.1)
        low, high = low - pad, high + pad
    else:
        pad = (high - low) * 0.1
        low, high = low - pad, high + pad
    center = (low + high) / 2
    half = (high - low) / (2 * zoom)
    return center - half, center + half


def _map_y(value: float, plot: QRectF, min_y: float, max_y: float) -> float:
    return plot.bottom() - (value - min_y) / max(1e-9, max_y - min_y) * plot.height()


def _fmt(value: float) -> str:
    if abs(value) >= 1000:
        return f"{value:,.0f}".replace(",", ".")
    return f"{value:.2f}".rstrip("0").rstrip(",").rstrip(".")


def _elide(text: str, limit: int) -> str:
    return text if len(text) <= limit else text[: limit - 1] + "…"


def _chart_text(text: str, language: str) -> str:
    if language != "en":
        return text
    translations = {
        "Série temporal do corpus": "Corpus time series",
        "Distribuição de sentimento": "Sentiment distribution",
        "Legibilidade e diversidade lexical": "Readability and lexical diversity",
        "Matriz de coocorrência por sentença": "Sentence co-occurrence matrix",
        "Menções territoriais": "Territorial mentions",
        "Autores com maior contribuição": "Authors with highest contribution",
        "Instituições com maior contribuição": "Institutions with highest contribution",
        "Frequência e dispersão dos termos": "Term frequency and dispersion",
        "Termos distintivos por grupo": "Distinctive terms by group",
        "Similaridade textual entre documentos": "Textual similarity between documents",
        "Associação normalizada entre termos (NPMI)": "Normalized term association (NPMI)",
        "Mudança lexical entre períodos": "Lexical change between periods",
        "Cobertura do léxico de sentimento": "Sentiment lexicon coverage",
        "Palavras": "Words",
        "Sentimento médio": "Mean sentiment",
        "Legibilidade média": "Mean readability",
        "% positivas": "% positive",
        "% negativas": "% negative",
        "Positivo": "Positive",
        "Neutro": "Neutral",
        "Negativo": "Negative",
        "Menções": "Mentions",
        "Documentos": "Documents",
        "Cobertura (%)": "Coverage (%)",
        "Divergência Jensen-Shannon": "Jensen-Shannon divergence",
    }
    if text.startswith("Comparação entre documentos - "):
        return text.replace("Comparação entre documentos - ", "Document comparison - ", 1)
    if text.startswith("Termo: "):
        return text.replace("Termo: ", "Term: ", 1)
    if text.startswith("Categoria: "):
        return text.replace("Categoria: ", "Category: ", 1)
    return translations.get(text, i18n.value(text, language))


def _sentiment_color(value: float) -> QColor:
    if value >= 0.05:
        return POSITIVE
    if value <= -0.05:
        return NEGATIVE
    return NEUTRAL


def _heat_color(ratio: float) -> QColor:
    ratio = min(1.0, max(0.0, ratio))
    start = QColor("#eef6f4")
    end = QColor("#0f766e")
    return QColor(
        int(start.red() + (end.red() - start.red()) * ratio),
        int(start.green() + (end.green() - start.green()) * ratio),
        int(start.blue() + (end.blue() - start.blue()) * ratio),
    )
