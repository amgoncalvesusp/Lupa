import pytest

from src.core.metadata_review import apply_metadata_override

pytestmark = pytest.mark.unit


def test_manual_metadata_override_wins_and_is_auditable():
    original = {
        "title": "Título automático",
        "year": "2020",
        "publication_year": "2020",
        "authors": [{"name": "Autor Incorreto"}],
        "metadata_evidence": {},
    }
    updated = apply_metadata_override(
        original,
        {
            "title": "Título revisado",
            "publication_year": "2022",
            "authors": ["Ana Souza", "Bruno Lima"],
            "affiliations": ["UFMG"],
        },
    )

    assert original["title"] == "Título automático"
    assert updated["title"] == "Título revisado"
    assert updated["year"] == "2022"
    assert updated["authors_display"] == "Ana Souza; Bruno Lima"
    assert updated["metadata_status"] == "revisado"
    assert updated["metadata_evidence"]["title"]["source"] == "manual_override"
