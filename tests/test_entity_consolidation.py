"""Corpus-level contributor consolidation tests."""

import pytest

from src.core.entity_consolidation import consolidate_entities

pytestmark = pytest.mark.unit


def test_consolidates_name_variants_and_fractional_contributions():
    results = [
        {
            "filename": "a.pdf",
            "publication_year": "2021",
            "document_type": "Artigo cientifico",
            "words_analytical": 1000,
            "authors": [{"name": "Ana Maria Souza", "affiliations": ["UFMG"]}],
        },
        {
            "filename": "b.pdf",
            "publication_year": "2022",
            "document_type": "Relatorio",
            "words_analytical": 500,
            "authors": [
                {"name": "A. M. Souza", "affiliations": ["Universidade Federal de Minas Gerais"]},
                {"name": "Bruno Lima", "affiliations": ["Instituto Clima"]},
            ],
        },
    ]

    summary = consolidate_entities(
        results,
        aliases={"A. M. Souza": "Ana Maria Souza", "UFMG": "Universidade Federal de Minas Gerais"},
    )

    ana = next(item for item in summary["authors"] if item["name"] == "Ana Maria Souza")
    ufmg = next(
        item
        for item in summary["institutions"]
        if item["name"] == "Universidade Federal de Minas Gerais"
    )
    assert ana["documents"] == 2
    assert ana["fractional_documents"] == pytest.approx(1.5)
    assert ana["words"] == 1500
    assert ana["year_start"] == "2021"
    assert ana["year_end"] == "2022"
    assert ufmg["documents"] == 2


def test_consolidation_never_merges_distinct_people_without_alias():
    results = [
        {"filename": "a", "authors": [{"name": "Ana Silva"}], "words_analytical": 10},
        {"filename": "b", "authors": [{"name": "Ana Souza"}], "words_analytical": 10},
    ]

    assert [item["name"] for item in consolidate_entities(results)["authors"]] == [
        "Ana Silva",
        "Ana Souza",
    ]

