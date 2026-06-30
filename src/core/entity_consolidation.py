"""Conservative consolidation of contributors and institutions."""

from __future__ import annotations

import re
import unicodedata
from typing import Dict, List, Mapping, Sequence


def consolidate_entities(
    results: Sequence[Dict], aliases: Mapping[str, str] | None = None
) -> Dict[str, List[Dict]]:
    """Aggregate entities, merging variants only through explicit aliases."""
    alias_index = {_key(source): target for source, target in (aliases or {}).items()}
    authors: Dict[str, Dict] = {}
    institutions: Dict[str, Dict] = {}
    for result in results:
        raw_authors = result.get("authors") or []
        author_names = [_canonical(item.get("name", ""), alias_index) for item in raw_authors]
        author_names = list(dict.fromkeys(name for name in author_names if name))
        fraction = 1.0 / len(author_names) if author_names else 0.0
        affiliations = list(result.get("affiliations") or [])
        for item in raw_authors:
            affiliations.extend({"name": name} for name in item.get("affiliations", []))
        institution_names = list(
            dict.fromkeys(
                name
                for name in (
                    _canonical(item.get("name", "") if isinstance(item, dict) else str(item), alias_index)
                    for item in affiliations
                )
                if name
            )
        )
        for name in author_names:
            _record(authors, name, result, fraction)
        for name in institution_names:
            _record(institutions, name, result, 1.0 / len(institution_names))
    return {
        "authors": _finalize(authors),
        "institutions": _finalize(institutions),
    }


def _record(target: Dict[str, Dict], name: str, result: Dict, fraction: float) -> None:
    key = _key(name)
    current = target.get(
        key,
        {
            "name": name,
            "documents": 0,
            "fractional_documents": 0.0,
            "words": 0,
            "years": set(),
            "document_types": set(),
            "files": [],
            "term_counts": {},
            "category_counts": {},
        },
    )
    year = str(result.get("publication_year") or result.get("year") or "")
    doc_type = str(result.get("document_type") or result.get("document") or "")
    target[key] = {
        **current,
        "documents": current["documents"] + 1,
        "fractional_documents": current["fractional_documents"] + fraction,
        "words": current["words"] + int(result.get("words_analytical") or 0),
        "years": current["years"] | ({year} if year else set()),
        "document_types": current["document_types"] | ({doc_type} if doc_type else set()),
        "files": [*current["files"], str(result.get("filename", ""))],
        "term_counts": _sum_counts(
            current["term_counts"],
            {term: data.get("analytical", 0) for term, data in (result.get("term_results") or {}).items()},
        ),
        "category_counts": _sum_counts(
            current["category_counts"],
            {name: data.get("analytical", 0) for name, data in (result.get("category_results") or {}).items()},
        ),
    }


def _finalize(items: Dict[str, Dict]) -> List[Dict]:
    rows = []
    for item in items.values():
        years = sorted(item["years"])
        rows.append(
            {
                **item,
                "fractional_documents": round(item["fractional_documents"], 6),
                "years": years,
                "year_start": years[0] if years else "",
                "year_end": years[-1] if years else "",
                "document_types": sorted(item["document_types"]),
                "term_rates_per_1000": _rates(item["term_counts"], item["words"]),
                "category_rates_per_1000": _rates(item["category_counts"], item["words"]),
            }
        )
    return sorted(rows, key=lambda item: (-item["documents"], item["name"]))


def _canonical(value: str, aliases: Mapping[str, str]) -> str:
    cleaned = re.sub(r"\s+", " ", value).strip(" ,.;")
    return aliases.get(_key(cleaned), cleaned)


def _key(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value.casefold())
    return "".join(char for char in normalized if not unicodedata.combining(char)).strip()


def _sum_counts(left: Mapping[str, object], right: Mapping[str, object]) -> Dict[str, float]:
    keys = set(left) | set(right)
    return {key: float(left.get(key, 0) or 0) + float(right.get(key, 0) or 0) for key in keys}


def _rates(counts: Mapping[str, object], words: int) -> Dict[str, float]:
    return {key: round(1000 * float(value) / words, 4) for key, value in counts.items()} if words else {}
