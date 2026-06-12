"""N-gram analyzer (bigrams and trigrams).

Recurring multi-word expressions ("desenvolvimento sustentável", "mudança do
clima") are invisible to single-word frequency counts, yet they are prime
candidates for meaning units in content analysis (Bardin, 2011) and for
núcleos de significação. This analyzer ranks the most frequent 2- and 3-word
sequences over the analytical corpus.

Filtering: an n-gram is kept only when its first and last words are content
words (not stopwords, length >= MIN_LENGTH); internal stopwords are allowed so
that natural phrases like "mudança do clima" survive. Comparison is
accent-insensitive; the most frequent original spelling is displayed.
"""

from collections import Counter
from typing import Dict, List, Tuple

from .base import ColumnSpec, DocumentContext
from .keywords import MIN_LENGTH, STOPWORDS
from ..term_search import normalize
from ..word_counter import tokenize

NGRAM_SIZES = (2, 3)
MIN_FREQUENCY = 2
TOP_N_CELL = 5
TOP_N_SHEET = 30


def _is_content_word(stripped: str) -> bool:
    return len(stripped) >= MIN_LENGTH and stripped not in STOPWORDS


def extract_ngrams(tokens: List[str]) -> Counter:
    """Count n-grams keyed by normalized form; display the common spelling."""
    norm = [normalize(t) for t in tokens]
    counts: Counter = Counter()
    displays: Dict[str, Counter] = {}
    for n in NGRAM_SIZES:
        for i in range(len(tokens) - n + 1):
            first, last = norm[i], norm[i + n - 1]
            if not (_is_content_word(first) and _is_content_word(last)):
                continue
            key = " ".join(norm[i : i + n])
            counts[key] += 1
            display = " ".join(t.lower() for t in tokens[i : i + n])
            displays.setdefault(key, Counter())[display] += 1
    # Re-key by the most common original spelling for readability.
    out: Counter = Counter()
    for key, count in counts.items():
        out[displays[key].most_common(1)[0][0]] = count
    return out


class NgramAnalyzer:
    name = "ngrams"

    def columns(self) -> List[ColumnSpec]:
        return [
            ColumnSpec("ngram_top", "Expressões recorrentes (n-gramas)", 60, "text")
        ]

    def run(self, ctx: DocumentContext) -> Dict[str, object]:
        text = "\n".join(ctx.pages_text[p - 1] for p in ctx.analytical_page_numbers)
        counts = extract_ngrams(tokenize(text))
        ranked: List[Tuple[str, int]] = [
            (phrase, c)
            for phrase, c in counts.most_common(TOP_N_SHEET)
            if c >= MIN_FREQUENCY
        ]
        cell = "; ".join(f"{p} ({c})" for p, c in ranked[:TOP_N_CELL])
        freq = [(phrase, len(phrase.split()), c) for phrase, c in ranked]
        return {"ngram_top": cell, "ngram_freq": freq}
