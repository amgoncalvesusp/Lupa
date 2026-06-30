"""Immutable application of researcher-reviewed bibliographic metadata."""

from __future__ import annotations

from typing import Dict, Mapping


def apply_metadata_override(result: Dict, override: Mapping[str, object]) -> Dict:
    title = str(override.get("title", result.get("title", ""))).strip()
    year = str(override.get("publication_year", result.get("publication_year", result.get("year", "")))).strip()
    document_type = str(override.get("document_type", result.get("document_type", result.get("document", "")))).strip()
    author_names = _names(override.get("authors", result.get("authors", [])))
    affiliation_names = _names(override.get("affiliations", result.get("affiliations", [])))
    changed = {
        key: value
        for key, value in {
            "title": title,
            "publication_year": year,
            "document_type": document_type,
            "authors": "; ".join(author_names),
            "affiliations": "; ".join(affiliation_names),
        }.items()
        if key in override
    }
    evidence = {
        **dict(result.get("metadata_evidence") or {}),
        **{
            key: {"source": "manual_override", "excerpt": str(value), "confidence": 1.0}
            for key, value in changed.items()
        },
    }
    return {
        **result,
        "title": title,
        "year": year,
        "publication_year": year,
        "document": document_type,
        "document_type": document_type,
        "authors": [{"name": name, "role": "author", "affiliations": [], "source": "manual_override", "confidence": 1.0} for name in author_names],
        "contributors": [{"name": name, "role": "author", "affiliations": [], "source": "manual_override", "confidence": 1.0} for name in author_names],
        "affiliations": [{"name": name, "source": "manual_override", "confidence": 1.0} for name in affiliation_names],
        "authors_display": "; ".join(author_names),
        "affiliations_display": "; ".join(affiliation_names),
        "metadata_evidence": evidence,
        "metadata_status": "revisado",
    }


def _names(value) -> list[str]:
    if isinstance(value, str):
        return [part.strip() for part in value.split(";") if part.strip()]
    return [
        str(item.get("name", "") if isinstance(item, dict) else item).strip()
        for item in (value or [])
        if str(item.get("name", "") if isinstance(item, dict) else item).strip()
    ]

