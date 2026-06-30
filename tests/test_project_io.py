"""Unit tests for Lupa project files."""

import json

import pytest

from src.core.project_io import load_project, save_project

pytestmark = pytest.mark.unit


def test_project_round_trip(tmp_path):
    doc = tmp_path / "a.pdf"
    doc.write_text("x", encoding="utf-8")
    path = tmp_path / "estudo.lupa.json"

    save_project(
        path,
        {
            "termos_raw": "clima",
            "flags": {"ocr": True, "sentimento": False},
            "arquivos": [str(doc)],
        },
    )
    loaded = load_project(path)

    assert loaded["versao"] == 2
    assert loaded["termos_raw"] == "clima"
    assert loaded["flags"]["ocr"] is True
    assert loaded["arquivos"] == [str(doc)]
    assert loaded["ausentes"] == []


def test_missing_file_is_reported(tmp_path):
    path = tmp_path / "estudo.lupa.json"
    missing = tmp_path / "missing.pdf"
    save_project(path, {"termos_raw": "", "flags": {}, "arquivos": [str(missing)]})

    loaded = load_project(path)

    assert loaded["arquivos"] == []
    assert loaded["ausentes"] == [str(missing)]


def test_unknown_version_raises_value_error(tmp_path):
    path = tmp_path / "old.lupa.json"
    path.write_text(json.dumps({"versao": 999}), encoding="utf-8")

    with pytest.raises(ValueError):
        load_project(path)


def test_v1_project_is_migrated_with_new_research_defaults(tmp_path):
    path = tmp_path / "legado.lupa.json"
    path.write_text(
        json.dumps(
            {
                "versao": 1,
                "termos_raw": "clima",
                "flags": {"presidente": True},
                "arquivos": [],
            }
        ),
        encoding="utf-8",
    )

    loaded = load_project(path)

    assert loaded["versao"] == 2
    assert loaded["flags"]["presidente"] is False
    assert loaded["metadata_overrides"] == {}
    assert loaded["entity_aliases"] == {}
    assert loaded["count_mode"] == "integral"
    assert loaded["online_metadata"] is False
    assert loaded["coding_records"] == []
