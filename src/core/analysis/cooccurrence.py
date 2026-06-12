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
            return {"cooccurrence": []}

        counts = {(a, b): 0 for a, b in combinations(self.terms, 2)}
        for page in ctx.analytical_page_numbers:
            for sentence in segment_sentences(ctx.pages_text[page - 1]):
                present = [
                    term_info
                    for term_info in self.terms
                    if count_term(sentence, term_info[0], exact=term_info[1]) > 0
                ]
                for pair in combinations(present, 2):
                    counts[pair] += 1

        rows = [
            (_label(a), _label(b), count)
            for (a, b), count in counts.items()
            if count >= 1
        ]
        rows.sort(key=lambda item: -item[2])
        return {"cooccurrence": rows}


def _label(term_info: Tuple[str, bool]) -> str:
    term, exact = term_info
    return f'"{term}"' if exact else term
