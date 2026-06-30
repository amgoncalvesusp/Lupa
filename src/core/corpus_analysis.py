"""Corpus-level comparative analyses built from immutable document results."""

from __future__ import annotations

import math
from collections import Counter, defaultdict
from typing import Dict, List, Mapping, Sequence, Tuple

from .entity_consolidation import consolidate_entities


def build_corpus_analyses(
    results: Sequence[Dict], aliases: Mapping[str, str] | None = None
) -> Dict[str, object]:
    """Build all corpus tables once so UI, charts and exports share values."""
    documents = [dict(result) for result in results]
    return {
        "entities": consolidate_entities(documents, aliases),
        "dispersion": calculate_dispersion(documents),
        "keyness": calculate_keyness(documents),
        "cooccurrence_association": calculate_cooccurrence_association(documents),
        "similarity": calculate_similarity(documents),
        "temporal_change": calculate_temporal_change(documents),
        "sentiment_diagnostics": sentiment_diagnostics(documents),
        "sentiment_aggregate": aggregate_sentiment_diagnostic(documents),
    }


def calculate_dispersion(results: Sequence[Dict]) -> List[Dict]:
    """Gries-style deviation of proportions (DP) across documents."""
    if not results:
        return []
    sizes = [_document_size(result) for result in results]
    total_size = sum(sizes)
    expected = [size / total_size if total_size else 1 / len(results) for size in sizes]
    terms = sorted(
        {
            term
            for result in results
            for term in (result.get("term_results") or {}).keys()
        }
    )
    rows = []
    for term in terms:
        counts = [
            _number((result.get("term_results") or {}).get(term, {}).get("analytical"))
            for result in results
        ]
        total = sum(counts)
        observed = [count / total if total else 0.0 for count in counts]
        dp = 0.5 * sum(abs(obs - exp) for obs, exp in zip(observed, expected))
        present = sum(count > 0 for count in counts)
        rows.append(
            {
                "term": term,
                "frequency": int(total),
                "dp": round(dp, 6),
                "document_range": present,
                "document_range_pct": round(100 * present / len(results), 2),
            }
        )
    return sorted(rows, key=lambda row: (-row["frequency"], row["term"]))


def calculate_keyness(results: Sequence[Dict], group_key: str = "year") -> List[Dict]:
    """Compare each group against its complement using G² and log-ratio."""
    groups: Dict[str, Counter] = defaultdict(Counter)
    for result in results:
        label = str(result.get(group_key) or result.get("publication_year") or "s/ grupo")
        groups[label].update({word: int(count) for word, count in (result.get("word_counts") or {}).items()})
    if len(groups) < 2:
        return []
    corpus = sum(groups.values(), Counter())
    corpus_total = sum(corpus.values())
    rows = []
    for label in sorted(groups):
        target = groups[label]
        target_total = sum(target.values())
        reference_total = corpus_total - target_total
        if not target_total or not reference_total:
            continue
        for term in sorted(corpus):
            a = target.get(term, 0)
            b = corpus[term] - a
            if a + b < 2:
                continue
            g2 = _log_likelihood(a, target_total - a, b, reference_total - b)
            target_rate = (a + 0.5) / (target_total + 1)
            reference_rate = (b + 0.5) / (reference_total + 1)
            rows.append(
                {
                    "group": label,
                    "term": term,
                    "target_frequency": a,
                    "reference_frequency": b,
                    "g2": round(g2, 6),
                    "log_ratio": round(math.log2(target_rate / reference_rate), 6),
                    "p_value": math.erfc(math.sqrt(max(0.0, g2) / 2)),
                }
            )
    q_values = _benjamini_hochberg([row["p_value"] for row in rows])
    enriched = [
        {**row, "p_value": round(row["p_value"], 8), "q_value": round(q, 8)}
        for row, q in zip(rows, q_values)
    ]
    return sorted(enriched, key=lambda row: (-row["g2"], row["group"], row["term"]))


def calculate_cooccurrence_association(results: Sequence[Dict]) -> List[Dict]:
    """Aggregate sentence/window marginals and calculate NPMI plus G²."""
    windows = 0
    marginals: Counter = Counter()
    pairs: Counter = Counter()
    for result in results:
        base = result.get("cooccurrence_base") or {}
        windows += int(base.get("windows") or 0)
        marginals.update({str(k): int(v) for k, v in (base.get("term_windows") or {}).items()})
        pairs.update({str(k): int(v) for k, v in (base.get("pair_windows") or {}).items()})
    if windows <= 0:
        return []
    rows = []
    for pair_key, together in pairs.items():
        term_a, term_b = pair_key.split("\u241f", 1)
        count_a, count_b = marginals[term_a], marginals[term_b]
        p_ab = together / windows
        denominator = -math.log(p_ab) if 0 < p_ab < 1 else 0.0
        pmi = math.log(p_ab / ((count_a / windows) * (count_b / windows))) if together else 0.0
        npmi = pmi / denominator if denominator else 0.0
        neither = max(0, windows - count_a - count_b + together)
        g2 = _log_likelihood(together, count_a - together, count_b - together, neither)
        rows.append(
            {
                "term_a": term_a,
                "term_b": term_b,
                "windows_together": together,
                "windows_total": windows,
                "npmi": round(max(-1.0, min(1.0, npmi)), 6),
                "g2": round(g2, 6),
            }
        )
    return sorted(rows, key=lambda row: (-row["npmi"], -row["windows_together"]))


def calculate_similarity(results: Sequence[Dict]) -> Dict[str, object]:
    """Return a TF-IDF cosine similarity matrix across documents."""
    labels = [str(result.get("filename", "")) for result in results]
    counts = [Counter(result.get("word_counts") or {}) for result in results]
    document_frequency = Counter(
        term for counter in counts for term, count in counter.items() if count > 0
    )
    n = len(counts)
    vectors = []
    for counter in counts:
        total = sum(counter.values()) or 1
        vectors.append(
            {
                term: (count / total) * (math.log((1 + n) / (1 + document_frequency[term])) + 1)
                for term, count in counter.items()
                if count > 0
            }
        )
    matrix = [[round(_cosine(left, right), 6) for right in vectors] for left in vectors]
    pairs = sorted(
        (
            {
                "document_a": labels[left],
                "document_b": labels[right],
                "cosine": matrix[left][right],
                "possible_duplicate": matrix[left][right] >= 0.95,
            }
            for left in range(n)
            for right in range(left + 1, n)
        ),
        key=lambda row: -row["cosine"],
    )
    return {"labels": labels, "matrix": matrix, "pairs": pairs}


def calculate_temporal_change(results: Sequence[Dict]) -> List[Dict]:
    """Jensen-Shannon divergence between consecutive year distributions."""
    by_year: Dict[str, Counter] = defaultdict(Counter)
    documents_by_year: Counter = Counter()
    for result in results:
        year = str(result.get("year") or result.get("publication_year") or "")
        if year:
            by_year[year].update(result.get("word_counts") or {})
            documents_by_year[year] += 1
    years = sorted(by_year)
    rows = []
    for left_year, right_year in zip(years, years[1:]):
        divergence, contributions = _jensen_shannon(by_year[left_year], by_year[right_year])
        rows.append(
            {
                "period_start": left_year,
                "period_end": right_year,
                "js_divergence": round(divergence, 6),
                "top_terms": [term for term, _value in contributions[:10]],
                "documents_start": documents_by_year[left_year],
                "documents_end": documents_by_year[right_year],
                "tokens_start": sum(by_year[left_year].values()),
                "tokens_end": sum(by_year[right_year].values()),
                "status": "exploratório" if min(documents_by_year[left_year], documents_by_year[right_year]) < 2 else "adequado",
            }
        )
    return rows


def sentiment_diagnostics(results: Sequence[Dict]) -> List[Dict]:
    return [
        {
            "filename": str(result.get("filename", "")),
            "sentences": int(result.get("sent_n_sentencas") or 0),
            "compound_mean": _number(result.get("sent_compound_medio")),
            "ci_low": _number(result.get("sent_ci_low")),
            "ci_high": _number(result.get("sent_ci_high")),
            "lexicon_coverage_pct": _number(result.get("sent_lexicon_coverage_pct")),
            "tokens": int(result.get("sent_tokens") or 0),
            "lexicon_hits": int(result.get("sent_lexicon_hits") or 0),
            "confidence": str(result.get("sent_diagnostic_confidence", "")),
        }
        for result in results
        if "sent_compound_medio" in result
    ]


def aggregate_sentiment_diagnostic(results: Sequence[Dict]) -> Dict[str, object]:
    values = [_number(result.get("sent_compound_medio")) for result in results if "sent_compound_medio" in result]
    if not values:
        return {"documents": 0, "compound_mean": 0.0, "ci_low": 0.0, "ci_high": 0.0}
    import random

    rng = random.Random(2718)
    samples = sorted(sum(rng.choice(values) for _ in values) / len(values) for _ in range(1000))
    return {
        "documents": len(values),
        "compound_mean": round(sum(values) / len(values), 4),
        "ci_low": round(samples[25], 4),
        "ci_high": round(samples[974], 4),
    }


def _log_likelihood(a: float, b: float, c: float, d: float) -> float:
    cells = (max(0.0, a), max(0.0, b), max(0.0, c), max(0.0, d))
    row_one, row_two = cells[0] + cells[1], cells[2] + cells[3]
    col_one, col_two = cells[0] + cells[2], cells[1] + cells[3]
    total = row_one + row_two
    if total <= 0:
        return 0.0
    expected = (
        row_one * col_one / total,
        row_one * col_two / total,
        row_two * col_one / total,
        row_two * col_two / total,
    )
    return 2 * sum(obs * math.log(obs / exp) for obs, exp in zip(cells, expected) if obs > 0 and exp > 0)


def _benjamini_hochberg(values: List[float]) -> List[float]:
    if not values:
        return []
    order = sorted(range(len(values)), key=values.__getitem__)
    adjusted = [1.0] * len(values)
    running = 1.0
    for rank_index in range(len(values) - 1, -1, -1):
        original_index = order[rank_index]
        rank = rank_index + 1
        running = min(running, values[original_index] * len(values) / rank)
        adjusted[original_index] = min(1.0, running)
    return adjusted


def _cosine(left: Mapping[str, float], right: Mapping[str, float]) -> float:
    left_norm = math.sqrt(sum(value * value for value in left.values()))
    right_norm = math.sqrt(sum(value * value for value in right.values()))
    if not left_norm or not right_norm:
        return 0.0
    common = set(left) & set(right)
    return sum(left[key] * right[key] for key in common) / (left_norm * right_norm)


def _jensen_shannon(left: Counter, right: Counter) -> Tuple[float, List[Tuple[str, float]]]:
    terms = set(left) | set(right)
    left_total, right_total = sum(left.values()) or 1, sum(right.values()) or 1
    contributions = []
    for term in terms:
        p, q = left[term] / left_total, right[term] / right_total
        midpoint = (p + q) / 2
        value = 0.5 * (p * math.log2(p / midpoint) if p else 0.0)
        value += 0.5 * (q * math.log2(q / midpoint) if q else 0.0)
        contributions.append((term, value))
    return sum(value for _term, value in contributions), sorted(contributions, key=lambda item: -item[1])


def _document_size(result: Dict) -> float:
    return max(0.0, _number(result.get("words_analytical")))


def _number(value) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0
