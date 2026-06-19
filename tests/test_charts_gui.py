"""Offscreen smoke tests for the interactive chart widgets."""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtGui import QImage, QPainter
from PyQt6.QtWidgets import QApplication
import pytest

from src.core.chart_data import (
    build_cooccurrence_heatmap,
    build_lexical_scatter,
    build_sentiment_chart,
    build_temporal_chart,
    build_territory_chart,
)
from src.gui.charts.chart_canvas import ChartCanvas
from src.gui.charts.chart_dialog import ChartDialog

pytestmark = pytest.mark.unit


@pytest.fixture(scope="module")
def app():
    application = QApplication.instance() or QApplication([])
    yield application


@pytest.fixture
def results():
    return [
        {
            "filename": "a.pdf",
            "year": "2020",
            "words_analytical": 1000,
            "sent_pct_positivo": 50,
            "sent_pct_neutro": 30,
            "sent_pct_negativo": 20,
            "sent_compound_medio": 0.2,
            "leg_indice": 60,
            "lex_ttr": 0.4,
            "term_results": {"clima": {"analytical": 10}},
            "category_results": {"AMBIENTE": {"analytical": 10}},
            "geo_mentions": [("Cerrado", "bioma", "", 2)],
            "cooccurrence": [("clima", "carbono", 3)],
        },
        {
            "filename": "b.pdf",
            "year": "2021",
            "words_analytical": 2000,
            "sent_pct_positivo": 20,
            "sent_pct_neutro": 50,
            "sent_pct_negativo": 30,
            "sent_compound_medio": -0.1,
            "leg_indice": 40,
            "lex_ttr": 0.6,
            "term_results": {"clima": {"analytical": 20}},
            "category_results": {"AMBIENTE": {"analytical": 20}},
            "geo_mentions": [("Amazônia", "bioma", "", 5)],
            "cooccurrence": [("clima", "carbono", 2)],
        },
    ]


def test_canvas_renders_all_visual_modes(app, results):
    charts = [
        build_temporal_chart(results),
        build_territory_chart(results),
        build_sentiment_chart(results),
        build_lexical_scatter(results),
        build_cooccurrence_heatmap(results),
    ]
    canvas = ChartCanvas()
    canvas.resize(800, 520)
    for chart in charts:
        canvas.set_data(chart)
        image = QImage(canvas.size(), QImage.Format.Format_ARGB32)
        image.fill(0xFFFFFFFF)
        painter = QPainter(image)
        canvas.render(painter)
        painter.end()
        sampled_colors = {
            image.pixelColor(x, y).name()
            for x in range(0, image.width(), 20)
            for y in range(0, image.height(), 20)
        }
        assert sampled_colors != {"#ffffff"}


def test_dialog_switches_between_six_chart_types(app, results):
    dialog = ChartDialog(results)
    assert dialog.chart_type.count() == 6
    assert dialog.normalize.isEnabled()
    expected = ["line", "bar", "stacked", "scatter", "heatmap", "bar"]
    for index, kind in enumerate(expected):
        dialog.chart_type.setCurrentIndex(index)
        app.processEvents()
        assert dialog.canvas.data.kind == kind
    dialog.chart_type.setCurrentIndex(1)
    dialog.comparison_kind.setCurrentIndex(0)
    assert not dialog.normalize.isEnabled()
    dialog.comparison_kind.setCurrentIndex(1)
    assert dialog.normalize.isEnabled()
    dialog.close()


def test_hidden_legend_series_are_excluded_from_visible_data(app, results):
    canvas = ChartCanvas()
    canvas.set_data(build_sentiment_chart(results))
    canvas.set_hidden_series({"Neutro"})
    assert [series.name for series in canvas.visible_data().series] == [
        "Positivo",
        "Negativo",
    ]
