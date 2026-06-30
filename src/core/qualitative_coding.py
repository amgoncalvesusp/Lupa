"""Transparent lexical segmentation and nominal coding reliability."""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path
from typing import Dict, List, Sequence

from .term_search import normalize
from .word_counter import tokenize

_STOPWORDS_PATH = Path(__file__).resolve().parent / "data" / "stopwords_pt.txt"
try:
    STOPWORDS = {
        normalize(line.strip())
        for line in _STOPWORDS_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    }
except OSError:
    STOPWORDS = {"de", "do", "da", "e", "a", "o", "em", "para", "com"}


def segment_by_lexical_cohesion(
    pages_text: Sequence[str], threshold: float = 0.12
) -> List[Dict]:
    """Split at adjacent page/block boundaries with low lexical Jaccard cohesion."""
    if not pages_text:
        return []
    vocabularies = [_content_terms(text) for text in pages_text]
    boundaries = [
        index
        for index in range(1, len(vocabularies))
        if _jaccard(vocabularies[index - 1], vocabularies[index]) < threshold
    ]
    starts = [0, *boundaries]
    ends = [*boundaries, len(pages_text)]
    return [
        {
            "segment_id": index + 1,
            "page_start": start + 1,
            "page_end": end,
            "text": "\n".join(pages_text[start:end]),
            "word_count": sum(len(tokenize(text)) for text in pages_text[start:end]),
        }
        for index, (start, end) in enumerate(zip(starts, ends))
    ]


def import_codings_csv(path: str | Path) -> List[Dict[str, str]]:
    """Import long-format coding records with unit, coder and code columns."""
    source = Path(path)
    with source.open("r", encoding="utf-8-sig", newline="") as handle:
        sample = handle.read(4096)
        handle.seek(0)
        dialect = csv.Sniffer().sniff(sample, delimiters=";,\t")
        reader = csv.DictReader(handle, dialect=dialect)
        required = {"unit", "coder", "code"}
        if not required.issubset(set(reader.fieldnames or [])):
            raise ValueError("A codificação deve conter as colunas: unit, coder e code.")
        rows = [
            {key: str(row.get(key, "")).strip() for key in required}
            for row in reader
            if all(str(row.get(key, "")).strip() for key in required)
        ]
    return rows


def krippendorff_alpha_nominal(records: Sequence[Dict[str, str]]) -> float:
    """Calculate nominal Krippendorff alpha for long-format coder assignments."""
    units: Dict[str, List[str]] = defaultdict(list)
    category_counts: Counter = Counter()
    for record in records:
        unit, code = str(record.get("unit", "")), str(record.get("code", ""))
        if unit and code:
            units[unit].append(code)
            category_counts[code] += 1
    pairs = [pair for values in units.values() if len(values) >= 2 for pair in combinations(values, 2)]
    if not pairs:
        raise ValueError("São necessárias ao menos duas codificações para uma mesma unidade.")
    observed = sum(left != right for left, right in pairs) / len(pairs)
    total = sum(category_counts.values())
    if total < 2:
        return 1.0
    agreement_expected = sum(count * (count - 1) for count in category_counts.values()) / (total * (total - 1))
    expected = 1 - agreement_expected
    if expected == 0:
        return 1.0 if observed == 0 else 0.0
    return round(1 - observed / expected, 6)


def krippendorff_alpha_by_code(records: Sequence[Dict[str, str]]) -> Dict[str, float]:
    """Return one-vs-rest nominal alpha for every observed code."""
    codes = sorted({str(record.get("code", "")) for record in records if record.get("code")})
    return {
        code: krippendorff_alpha_nominal(
            [{**record, "code": "presente" if record.get("code") == code else "ausente"} for record in records]
        )
        for code in codes
    }


def coding_disagreements(records: Sequence[Dict[str, str]]) -> List[Dict]:
    """List units whose coders assigned different nominal codes."""
    units: Dict[str, Dict[str, str]] = defaultdict(dict)
    for record in records:
        units[str(record.get("unit", ""))][str(record.get("coder", ""))] = str(record.get("code", ""))
    return [
        {"unit": unit, "assignments": dict(sorted(assignments.items()))}
        for unit, assignments in sorted(units.items())
        if len(set(assignments.values())) > 1
    ]


def _content_terms(text: str) -> set[str]:
    return {
        normalized
        for token in tokenize(text)
        if len(normalized := normalize(token)) >= 3 and normalized not in STOPWORDS
    }


def _jaccard(left: set[str], right: set[str]) -> float:
    union = left | right
    return len(left & right) / len(union) if union else 1.0
