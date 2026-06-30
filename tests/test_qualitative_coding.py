"""Lexical segmentation and human-coding reliability tests."""

import csv

import pytest

from src.core.qualitative_coding import (
    import_codings_csv,
    krippendorff_alpha_nominal,
    krippendorff_alpha_by_code,
    coding_disagreements,
    segment_by_lexical_cohesion,
)

pytestmark = pytest.mark.unit


def test_lexical_segmentation_detects_strong_topic_shift():
    pages = [
        "energia solar renovavel painel eletricidade energia",
        "energia eolica renovavel eletricidade turbina energia",
        "saude hospital paciente medicina enfermagem saude",
        "saude publica paciente hospital medicina saude",
    ]

    segments = segment_by_lexical_cohesion(pages, threshold=0.12)

    assert len(segments) == 2
    assert segments[0]["page_start"] == 1
    assert segments[0]["page_end"] == 2
    assert segments[1]["page_start"] == 3


def test_krippendorff_alpha_is_one_for_perfect_nominal_agreement():
    records = [
        {"unit": "u1", "coder": "a", "code": "clima"},
        {"unit": "u1", "coder": "b", "code": "clima"},
        {"unit": "u2", "coder": "a", "code": "economia"},
        {"unit": "u2", "coder": "b", "code": "economia"},
    ]

    assert krippendorff_alpha_nominal(records) == 1.0
    assert krippendorff_alpha_by_code(records) == {"clima": 1.0, "economia": 1.0}
    assert coding_disagreements(records) == []


def test_coding_disagreements_identifies_units_and_coders():
    records = [
        {"unit": "u1", "coder": "ana", "code": "clima"},
        {"unit": "u1", "coder": "bia", "code": "economia"},
    ]

    disagreements = coding_disagreements(records)
    assert disagreements == [{"unit": "u1", "assignments": {"ana": "clima", "bia": "economia"}}]


def test_import_codings_validates_required_columns(tmp_path):
    path = tmp_path / "codigos.csv"
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["unit", "coder", "code"])
        writer.writeheader()
        writer.writerow({"unit": "u1", "coder": "ana", "code": "clima"})

    assert import_codings_csv(path)[0]["coder"] == "ana"

    invalid = tmp_path / "invalido.csv"
    invalid.write_text("unidade;codigo\nu1;clima\n", encoding="utf-8")
    with pytest.raises(ValueError):
        import_codings_csv(invalid)
