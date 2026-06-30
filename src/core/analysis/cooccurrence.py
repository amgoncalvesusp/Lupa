"""Sentence-level co-occurrence of search terms."""

from itertools import combinations
from typing import Dict, List, Tuple

from .base import ColumnSpec, DocumentContext
from .sentiment import segment_sentences
from ..term_search import count_term


class CooccurrenceAnalyzer:
    name = "cooccurrence"

    def __init__(self, terms: List[Tuple[str, bool]] = None):
        self.terms = terms or []

    def columns(self) -> List[ColumnSpec]:
        return []

    def run(self, ctx: DocumentContext) -> Dict[str, object]:
        if len(self.terms) < 2:
            return {
                "cooccurrence": [],
                "cooccurrence_base": {"windows": 0, "term_windows": {}, "pair_windows": {}},
            }

        counts = {(a, b): 0 for a, b in combinations(self.terms, 2)}
        term_windows = {term_info: 0 for term_info in self.terms}
        windows = 0
        for page in ctx.analytical_page_numbers:
            for sentence in segment_sentences(ctx.pages_text[page - 1]):
                windows += 1
                present = [
                    term_info
                    for term_info in self.terms
                    if count_term(sentence, term_info[0], exact=term_info[1]) > 0
                ]
                for term_info in present:
                    term_windows[term_info] += 1
                for pair in combinations(present, 2):
                    counts[pair] += 1

        rows = [
            (_label(a), _label(b), count)
            for (a, b), count in counts.items()
            if count >= 1
        ]
        rows.sort(key=lambda item: -item[2])
        return {
            "cooccurrence": rows,
            "cooccurrence_base": {
                "windows": windows,
                "term_windows": {_label(term): count for term, count in term_windows.items()},
                "pair_windows": {
                    f"{_label(a)}\u241f{_label(b)}": count
                    for (a, b), count in counts.items()
                    if count > 0
                },
            },
        }


def _label(term_info: Tuple[str, bool]) -> str:
    term, exact = term_info
    return f'"{term}"' if exact else term
