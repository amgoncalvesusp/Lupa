"""Unit tests for sentence-level term co-occurrence."""

import pytest

from src.core.analysis.base import DocumentContext
from src.core.analysis.cooccurrence import CooccurrenceAnalyzer

pytestmark = pytest.mark.unit


def _run(text, terms):
    ctx = DocumentContext("a.pdf", [text], [1], 1)
    return CooccurrenceAnalyzer(terms).run(ctx)["cooccurrence"]


def test_two_terms_in_same_sentence_count_once():
    rows = _run("Clima e carbono aparecem juntos.", [("clima", False), ("carbono", False)])
    assert rows == [("clima", "carbono", 1)]


def test_terms_in_separate_sentences_do_not_count():
    rows = _run("Clima aparece aqui. Carbono aparece depois.", [("clima", False), ("carbono", False)])
    assert rows == []


def test_three_terms_generate_three_pairs():
    rows = _run(
        "Clima, carbono e floresta aparecem juntos.",
        [("clima", False), ("carbono", False), ("floresta", False)],
    )
    assert rows == [
        ("clima", "carbono", 1),
        ("clima", "floresta", 1),
        ("carbono", "floresta", 1),
    ]


def test_no_terms_returns_empty_list():
    assert _run("Clima e carbono.", []) == []
