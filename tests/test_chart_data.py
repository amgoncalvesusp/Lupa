"""Unit tests for interactive chart data preparation."""

import pytest

from src.core.chart_data import (
    build_corpus_chart,
    build_comparison_chart,
    build_cooccurrence_heatmap,
    build_lexical_scatter,
    build_sentiment_chart,
    build_temporal_chart,
    build_territory_chart,
    chart_to_rows,
    filter_results,
)
from src.core.corpus_analysis import build_corpus_analyses

pytestmark = pytest.mark.unit


@pytest.fixture
def results():
    return [
        {
            "filename": "a.pdf",
            "year": "2020",
            "words_analytical": 1000,
            "sent_pct_positivo": 50.0,
            "sent_pct_neutro": 30.0,
            "sent_pct_negativo": 20.0,
            "sent_compound_medio": 0.2,
            "leg_indice": 60.0,
            "lex_ttr": 0.4,
            "term_results": {
                "clima": {"analytical": 10},
                "carbono": {"analytical": 5},
            },
            "category_results": {"AMBIENTE": {"analytical": 15}},
            "geo_mentions": [
                ("São Paulo", "estado", "SP", 4),
                ("Cerrado", "bioma", "", 2),
            ],
            "emotion_words": {"alegria": [("avanço", 3)]},
            "emo_pct_alegria": 4.0,
            "keyword_freq": [("política", 7)],
            "cooccurrence": [("clima", "carbono", 3)],
        },
        {
            "filename": "b.pdf",
            "year": "2021",
            "words_analytical": 2000,
            "sent_pct_positivo": 20.0,
            "sent_pct_neutro": 50.0,
            "sent_pct_negativo": 30.0,
            "sent_compound_medio": -0.1,
            "leg_indice": 40.0,
            "lex_ttr": 0.6,
            "term_results": {
                "clima": {"analytical": 20},
                "carbono": {"analytical": 4},
            },
            "category_results": {"AMBIENTE": {"analytical": 24}},
            "geo_mentions": [
                ("São Paulo", "estado", "SP", 1),
                ("Amazônia", "bioma", "", 6),
            ],
            "emotion_words": {"alegria": [("esperança", 2)]},
            "emo_pct_alegria": 2.0,
            "keyword_freq": [("política", 3)],
            "cooccurrence": [
                ("clima", "carbono", 2),
                ("clima", "floresta", 4),
            ],
        },
    ]


def test_temporal_chart_supports_multiple_metrics_and_normalization(results):
    chart = build_temporal_chart(
        results,
        metrics=(
            ("Clima", "terms", "clima"),
            ("Ambiente", "categories", "AMBIENTE"),
        ),
        normalized=True,
    )
    assert chart.kind == "line"
    assert chart.labels == ("2020", "2021")
    assert chart.series[0].values == (10.0, 10.0)
    assert chart.series[1].values == (15.0, 12.0)


@pytest.mark.parametrize(
    ("kind", "key", "expected"),
    [
        ("words", "", (1000.0, 2000.0)),
        ("term", "clima", (10.0, 20.0)),
        ("category", "AMBIENTE", (15.0, 24.0)),
        ("territory", "São Paulo", (4.0, 1.0)),
        ("emotion", "alegria", (4.0, 2.0)),
        ("keyword", "política", (7.0, 3.0)),
    ],
)
def test_comparison_chart_supports_current_analyses(results, kind, key, expected):
    chart = build_comparison_chart(results, kind, key)
    assert chart.kind == "bar"
    assert chart.labels == ("a.pdf", "b.pdf")
    assert chart.series[0].values == expected


def test_sentiment_chart_builds_stacked_percentages(results):
    chart = build_sentiment_chart(results)
    assert chart.kind == "stacked"
    assert [series.name for series in chart.series] == ["Positivo", "Neutro", "Negativo"]
    assert chart.series[0].values == (50.0, 20.0)
    assert chart.series[2].values == (20.0, 30.0)


def test_lexical_scatter_keeps_document_metadata(results):
    chart = build_lexical_scatter(results)
    assert chart.kind == "scatter"
    assert chart.points[0].label == "a.pdf"
    assert chart.points[0].x == 60.0
    assert chart.points[0].y == 0.4
    assert chart.points[0].size == 1000.0
    assert dict(chart.points[0].metadata)["filename"] == "a.pdf"


def test_cooccurrence_heatmap_is_symmetric_and_aggregated(results):
    chart = build_cooccurrence_heatmap(results)
    assert chart.kind == "heatmap"
    assert chart.labels == ("carbono", "clima", "floresta")
    carbon = chart.labels.index("carbono")
    climate = chart.labels.index("clima")
    forest = chart.labels.index("floresta")
    assert chart.matrix[carbon][climate] == 5.0
    assert chart.matrix[climate][carbon] == 5.0
    assert chart.matrix[climate][forest] == 4.0


def test_territory_chart_aggregates_and_filters_type(results):
    chart = build_territory_chart(results, place_type="bioma")
    assert chart.kind == "bar"
    assert chart.labels == ("Amazônia", "Cerrado")
    assert chart.series[0].values == (6.0, 2.0)


def test_filter_results_and_chart_rows(results):
    filtered = filter_results(results, year="2021", filename="b.pdf")
    assert [item["filename"] for item in filtered] == ["b.pdf"]

    chart = build_sentiment_chart(filtered)
    rows = chart_to_rows(chart)
    assert rows[0] == ["Rótulo", "Positivo", "Neutro", "Negativo"]
    assert rows[1][0] == "b.pdf"


@pytest.mark.parametrize(
    ("mode", "kind"),
    [
        ("authors", "bar"),
        ("institutions", "bar"),
        ("dispersion", "scatter"),
        ("keyness", "bar"),
        ("similarity", "heatmap"),
        ("association", "heatmap"),
        ("temporal_change", "bar"),
        ("sentiment_diagnostics", "bar"),
    ],
)
def test_corpus_charts_share_analysis_tables(results, mode, kind):
    enriched = [
        {
            **row,
            "authors": [{"name": f"Autor {index}", "affiliations": ["Instituição X"]}],
            "affiliations": [{"name": "Instituição X"}],
            "word_counts": {"clima": 10 + index, "energia": 2 * index + 1},
            "cooccurrence_base": {
                "windows": 10,
                "term_windows": {"clima": 5, "carbono": 4},
                "pair_windows": {"clima\u241fcarbono": 3},
            },
            "sent_n_sentencas": 5,
            "sent_ci_low": -0.1,
            "sent_ci_high": 0.2,
            "sent_lexicon_coverage_pct": 15,
        }
        for index, row in enumerate(results)
    ]
    chart = build_corpus_chart(build_corpus_analyses(enriched), mode)

    assert chart.kind == kind
    assert chart.title
