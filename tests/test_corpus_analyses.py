"""Statistical corpus analysis tests with small auditable fixtures."""

import pytest

from src.core.corpus_analysis import build_corpus_analyses

pytestmark = pytest.mark.unit


@pytest.fixture
def corpus_results():
    return [
        {
            "filename": "energia-2020.txt",
            "year": "2020",
            "publication_year": "2020",
            "document_type": "Artigo científico",
            "words_analytical": 100,
            "word_counts": {"energia": 12, "solar": 8, "trabalho": 2},
            "term_results": {"energia": {"analytical": 12}, "trabalho": {"analytical": 2}},
            "cooccurrence_base": {
                "windows": 10,
                "term_windows": {"energia": 8, "trabalho": 3},
                "pair_windows": {"energia\u241ftrabalho": 3},
            },
            "authors": [{"name": "Ana Souza", "affiliations": ["UFMG"]}],
            "sent_n_sentencas": 10,
            "sent_compound_medio": 0.2,
            "sent_ci_low": 0.1,
            "sent_ci_high": 0.3,
            "sent_lexicon_coverage_pct": 18.0,
        },
        {
            "filename": "carvao-2021.txt",
            "year": "2021",
            "publication_year": "2021",
            "document_type": "Reportagem",
            "words_analytical": 100,
            "word_counts": {"carvao": 12, "mina": 8, "trabalho": 2},
            "term_results": {"energia": {"analytical": 0}, "trabalho": {"analytical": 2}},
            "cooccurrence_base": {
                "windows": 10,
                "term_windows": {"energia": 2, "trabalho": 4},
                "pair_windows": {"energia\u241ftrabalho": 1},
            },
            "authors": [{"name": "Bruno Lima", "affiliations": ["Instituto Clima"]}],
            "sent_n_sentencas": 8,
            "sent_compound_medio": -0.1,
            "sent_ci_low": -0.2,
            "sent_ci_high": 0.0,
            "sent_lexicon_coverage_pct": 12.0,
        },
    ]


def test_builds_all_comparative_analysis_tables(corpus_results):
    analyses = build_corpus_analyses(corpus_results)

    assert set(analyses) >= {
        "entities",
        "dispersion",
        "keyness",
        "cooccurrence_association",
        "similarity",
        "temporal_change",
        "sentiment_diagnostics",
    }
    assert analyses["entities"]["authors"][0]["documents"] == 1
    assert analyses["similarity"]["labels"] == ["energia-2020.txt", "carvao-2021.txt"]
    assert analyses["similarity"]["matrix"][0][0] == pytest.approx(1.0)
    assert 0 <= analyses["similarity"]["matrix"][0][1] < 1


def test_dispersion_distinguishes_concentrated_and_even_terms(corpus_results):
    rows = {row["term"]: row for row in build_corpus_analyses(corpus_results)["dispersion"]}

    assert rows["energia"]["dp"] > rows["trabalho"]["dp"]
    assert rows["energia"]["document_range_pct"] == 50.0
    assert rows["trabalho"]["document_range_pct"] == 100.0


def test_keyness_and_temporal_change_are_directional(corpus_results):
    analyses = build_corpus_analyses(corpus_results)
    keyness = analyses["keyness"]

    energy = next(row for row in keyness if row["group"] == "2020" and row["term"] == "energia")
    assert energy["log_ratio"] > 0
    assert 0 <= energy["q_value"] <= 1
    assert analyses["temporal_change"][0]["js_divergence"] > 0


def test_npmi_uses_window_marginals(corpus_results):
    row = build_corpus_analyses(corpus_results)["cooccurrence_association"][0]

    assert row["term_a"] == "energia"
    assert row["term_b"] == "trabalho"
    assert -1 <= row["npmi"] <= 1
    assert row["windows_together"] == 4

