"""Unit tests for automatic methodology reports."""

import pytest

from src.core.methodology_report import (
    build_methodology_report,
    render_methodology_text,
)

pytestmark = pytest.mark.unit


def test_methodology_report_keeps_files_flags_terms_and_categories():
    results = [
        {
            "filename": "a.txt",
            "term_results": {"clima": {"analytical": 2}},
            "category_results": {"CLIMA": {"analytical": 3}},
            "sent_n_sentencas": 4,
            "lex_ttr": 0.5,
            "kwic": [],
        }
    ]
    report = build_methodology_report(
        results,
        {
            "generated_at": "2026-06-12T10:00:00",
            "flags": {"ocr": False, "sentimento": True},
            "termos_raw": "clima\nCLIMA: clima",
            "arquivos": ["C:/corpus/a.txt"],
        },
    )

    assert report["gerado_por"] == "Lupa 1.0"
    assert report["gerado_em"] == "2026-06-12T10:00:00"
    assert report["documentos"] == ["a.txt"]
    assert report["arquivos_origem"] == ["C:/corpus/a.txt"]
    assert report["flags"]["sentimento"] is True
    assert report["termos"] == ["clima"]
    assert report["categorias"] == ["CLIMA"]
    assert "Análise de sentimento" in report["analises"]


def test_methodology_text_is_reader_friendly():
    report = build_methodology_report(
        [{"filename": "a.pdf"}],
        {"generated_at": "2026-06-12T10:00:00", "flags": {"ocr": True}},
    )
    text = render_methodology_text(report)

    assert "Relatório metodológico - Lupa" in text
    assert "Arquivos analisados" in text
    assert "ocr: sim" in text
