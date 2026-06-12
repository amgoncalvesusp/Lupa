"""Corpus-level temporal summary for processed document results."""

from collections import defaultdict
from typing import Dict, List


NO_YEAR = "s/ ano"


def build_corpus_summary(results: List[Dict]) -> Dict[str, Dict]:
    """Aggregate document metrics by year.

    The summary is descriptive: values are simple sums or means over documents
    assigned to the same year, with documents lacking a year grouped as
    ``s/ ano``.
    """
    groups: Dict[str, List[Dict]] = defaultdict(list)
    for result in results:
        year = str(result.get("year") or "").strip() or NO_YEAR
        groups[year].append(result)

    summary: Dict[str, Dict] = {}
    for year, docs in groups.items():
        row: Dict[str, object] = {
            "year": year,
            "docs": len(docs),
            "words_analytical": sum(int(d.get("words_analytical") or 0) for d in docs),
            "sent_compound_medio": _mean(docs, "sent_compound_medio"),
            "leg_indice_medio": _mean(docs, "leg_indice"),
            "sent_pct_positivo": _mean(docs, "sent_pct_positivo"),
            "sent_pct_negativo": _mean(docs, "sent_pct_negativo"),
            "terms": defaultdict(int),
            "categories": defaultdict(int),
        }
        for doc in docs:
            for label, data in doc.get("term_results", {}).items():
                row["terms"][label] += int(data.get("analytical") or 0)
            for name, data in doc.get("category_results", {}).items():
                row["categories"][name] += int(data.get("analytical") or 0)
        row["terms"] = dict(row["terms"])
        row["categories"] = dict(row["categories"])
        summary[year] = row
    return dict(sorted(summary.items(), key=lambda item: _year_sort_key(item[0])))


def has_multiple_years(results: List[Dict]) -> bool:
    years = {str(r.get("year") or "").strip() or NO_YEAR for r in results}
    return len(years) >= 2


def _mean(docs: List[Dict], key: str) -> float:
    values = []
    for doc in docs:
        value = doc.get(key)
        if value in ("", None):
            continue
        try:
            values.append(float(value))
        except (TypeError, ValueError):
            continue
    if not values:
        return 0.0
    return round(sum(values) / len(values), 2)


def _year_sort_key(year: str):
    if year == NO_YEAR:
        return (1, 9999)
    try:
        return (0, int(year))
    except ValueError:
        return (0, year)
