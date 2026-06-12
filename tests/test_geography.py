"""Unit tests for territorial mention detection."""

import pytest

from src.core.analysis.base import DocumentContext
from src.core.analysis.geography import GeographyAnalyzer

pytestmark = pytest.mark.unit


PLACES = [
    {
        "name": "São Paulo",
        "type": "estado",
        "uf": "SP",
        "variants": ["sao paulo", "estado de sao paulo"],
    },
    {
        "name": "Mato Grosso do Sul",
        "type": "estado",
        "uf": "MS",
        "variants": ["mato grosso do sul", "estado de mato grosso do sul"],
    },
]


def test_state_detected_with_and_without_accents():
    ctx = DocumentContext("a.pdf", ["São Paulo e Sao Paulo avançaram."], [1], 1)
    result = GeographyAnalyzer(PLACES).run(ctx)
    assert ("São Paulo", "estado", "SP", 2) in result["geo_mentions"]
    assert result["geo_top"] == "São Paulo (2)"


def test_long_variant_consumes_shorter_overlap():
    ctx = DocumentContext("a.pdf", ["estado de sao paulo"], [1], 1)
    result = GeographyAnalyzer(PLACES).run(ctx)
    assert result["geo_mentions"] == [("São Paulo", "estado", "SP", 1)]


def test_place_outside_analytical_corpus_is_not_counted():
    ctx = DocumentContext("a.pdf", ["São Paulo", "Mato Grosso do Sul"], [2], 2)
    result = GeographyAnalyzer(PLACES).run(ctx)
    assert ("Mato Grosso do Sul", "estado", "MS", 1) in result["geo_mentions"]
    assert all(row[0] != "São Paulo" for row in result["geo_mentions"])


def test_missing_gazetteer_returns_empty_result():
    ctx = DocumentContext("a.pdf", ["São Paulo"], [1], 1)
    result = GeographyAnalyzer([]).run(ctx)
    assert result == {"geo_top": "", "geo_mentions": []}
