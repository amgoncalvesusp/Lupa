"""Unit tests for NRC-style discrete emotion analysis."""

import pytest

from src.core.analysis.base import DocumentContext
from src.core.analysis.emotions import EmotionAnalyzer
from src.core.analysis import build_default_analyzers

pytestmark = pytest.mark.unit


def test_emotion_percentages_and_dominant_with_injected_lexicon():
    lexicon = {
        "feliz": {"alegria", "confiança"},
        "medo": {"medo"},
        "triste": {"tristeza"},
    }
    ctx = DocumentContext("a.pdf", ["Feliz feliz medo triste comum"], [1], 1)

    result = EmotionAnalyzer(lexicon).run(ctx)

    assert result["emo_dominante"] == "alegria"
    assert result["emo_pct_alegria"] == 40.0
    assert result["emo_pct_confiança"] == 40.0
    assert result["emo_pct_medo"] == 20.0
    assert result["emotion_words"]["alegria"] == [("feliz", 2)]


def test_empty_corpus_returns_zeroes():
    result = EmotionAnalyzer({"feliz": {"alegria"}}).run(
        DocumentContext("a.pdf", [""], [], 1)
    )
    assert result["emo_dominante"] == ""
    assert result["emo_pct_alegria"] == 0.0


def test_accented_word_matches_normalized_lexicon():
    result = EmotionAnalyzer({"confianca": {"confiança"}}).run(
        DocumentContext("a.pdf", ["confiança"], [1], 1)
    )
    assert result["emo_pct_confiança"] == 100.0
    assert result["emo_dominante"] == "confiança"


def test_emotion_analyzer_absent_when_disabled():
    names = [a.name for a in build_default_analyzers([], detect_emotions=False)]
    assert "emotions" not in names
