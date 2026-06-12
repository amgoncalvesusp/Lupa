"""Unit tests for plain CSV/JSON exports."""

import csv
import json

import pytest

from src.core.analysis import build_column_specs, build_default_analyzers
from src.core.exporter_plain import export_to_csv, export_to_json

pytestmark = pytest.mark.unit


def _result(**overrides):
    base = {
        "filename": "doc.pdf",
        "year": "2020",
        "document": "Mensagem ao Congresso Nacional",
        "president": "Jair Bolsonaro",
        "total_pages": 3,
        "pages_with_text": 3,
        "pages_problematic": 0,
        "ocr_pages_count": 0,
        "words_total": 100,
        "words_analytical": 80,
        "confidence": "Alto",
        "observations": "ok",
        "excluded_pages": [],
    }
    base.update(overrides)
    return base


def test_csv_main_has_header_and_one_row_per_document(tmp_path):
    specs = build_column_specs(build_default_analyzers([], detect_sentiment=False))
    export_to_csv([_result(filename="a.pdf"), _result(filename="b.pdf")], tmp_path, specs)

    with (tmp_path / "resultados.csv").open(encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.reader(fh, delimiter=";"))

    assert rows[0][0] == "Nº Doc."
    assert rows[0][1] == "Nome do Arquivo"
    assert rows[1][0] == "1"
    assert rows[1][1] == "a.pdf"
    assert rows[2][0] == "2"
    assert rows[2][1] == "b.pdf"


def test_detail_csvs_are_created_only_when_data_exists(tmp_path):
    result = _result(
        sentiment_sentences=[
            {"page": 1, "text": "Foi bom.", "compound": 0.4, "classe": "Positivo"}
        ],
        keyword_freq=[("clima", 7)],
    )
    export_to_csv([result], tmp_path)

    assert (tmp_path / "resultados.csv").exists()
    assert (tmp_path / "sentencas.csv").exists()
    assert (tmp_path / "palavras.csv").exists()
    assert not (tmp_path / "ngramas.csv").exists()
    assert not (tmp_path / "categorias.csv").exists()
    assert not (tmp_path / "kwic.csv").exists()
    assert (tmp_path / "metodologia.txt").exists()


def test_csv_writes_all_detail_file_types_when_present(tmp_path):
    result = _result(
        excluded_pages=[
            {"page_number": 1, "exclusion_reason": "capa", "word_count": 2}
        ],
        ngram_freq=[("mudança do clima", 3, 4)],
        category_results={
            "CLIMA": {
                "total": 3,
                "analytical": 2,
                "members": {"clima": {"total": 3, "analytical": 2}},
            }
        },
        kwic=[
            {
                "page": 2,
                "term": "clima",
                "left": "mudança do",
                "keyword": "clima",
                "right": "global",
            }
        ],
    )
    export_to_csv([result], tmp_path)

    assert (tmp_path / "ngramas.csv").exists()
    assert (tmp_path / "categorias.csv").exists()
    assert (tmp_path / "kwic.csv").exists()
    assert (tmp_path / "paginas_excluidas.csv").exists()


def test_json_round_trip_keeps_public_result_data(tmp_path):
    out = tmp_path / "resultados.json"
    export_to_json(
        [_result(filename="doc.pdf", words_total=42)],
        out,
        methodology_options={"generated_at": "2026-06-12T10:00:00"},
    )

    with out.open(encoding="utf-8") as fh:
        data = json.load(fh)

    assert data["gerado_por"] == "Lupa 1.0"
    assert data["metodologia"]["gerado_em"] == "2026-06-12T10:00:00"
    assert data["documentos"][0]["filename"] == "doc.pdf"
    assert data["documentos"][0]["words_total"] == 42


def test_json_omits_internal_keys(tmp_path):
    out = tmp_path / "resultados.json"
    export_to_json([_result(_term_clima_total=3, public_value={"_skip": 1})], out)

    with out.open(encoding="utf-8") as fh:
        doc = json.load(fh)["documentos"][0]

    assert "_term_clima_total" not in doc
    assert "_skip" not in doc["public_value"]
