"""Discrete emotion analyzer using an editable NRC EmoLex-style lexicon.

Methodology
-----------
Counts word associations with the eight NRC Word-Emotion Association Lexicon
emotions (Mohammad & Turney, 2013): anger, anticipation, disgust, fear, joy,
sadness, surprise and trust. The analyzer is lexical, deterministic and
auditable: every aggregate percentage is backed by the matched words retained
in ``emotion_words``.

Reference: Mohammad, S. M. & Turney, P. D. (2013). Crowdsourcing a Word-Emotion
Association Lexicon. Computational Intelligence, 29(3).
"""

import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Set

from .base import ColumnSpec, DocumentContext
from ..term_search import normalize
from ..word_counter import tokenize

EMOTIONS = [
    ("alegria", "joy"),
    ("tristeza", "sadness"),
    ("raiva", "anger"),
    ("medo", "fear"),
    ("confiança", "trust"),
    ("repulsa", "disgust"),
    ("surpresa", "surprise"),
    ("antecipação", "anticipation"),
]

EN_TO_PT = {en: pt for pt, en in EMOTIONS}


def _data_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS) / "src" / "core" / "data"
    return Path(__file__).resolve().parents[1] / "data"


def load_emolex(path: str | Path | None = None) -> Dict[str, Set[str]]:
    """Load ``word<TAB>emotion`` associations. Missing files return empty dict."""
    lexicon: Dict[str, Set[str]] = defaultdict(set)
    try:
        with open(path or (_data_dir() / "nrc_emolex_pt.txt"), encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split("\t")
                if len(parts) < 2:
                    continue
                word = normalize(parts[0])
                emotion = _to_pt_emotion(parts[1].strip())
                if word and emotion:
                    lexicon[word].add(emotion)
    except OSError:
        return {}
    return dict(lexicon)


class EmotionAnalyzer:
    name = "emotions"

    def __init__(self, lexicon: Dict[str, Set[str]] | None = None):
        self.lexicon = load_emolex() if lexicon is None else lexicon

    def columns(self) -> List[ColumnSpec]:
        return [ColumnSpec("emo_dominante", "Emoção dominante", 18, "sentiment")] + [
            ColumnSpec(f"emo_pct_{pt}", f"% {pt.capitalize()}", 14, "sentiment")
            for pt, _en in EMOTIONS
        ]

    def run(self, ctx: DocumentContext) -> Dict[str, object]:
        tokens = []
        for page in ctx.analytical_page_numbers:
            tokens.extend(normalize(token) for token in tokenize(ctx.pages_text[page - 1]))

        total_words = len(tokens)
        counts = {pt: 0 for pt, _en in EMOTIONS}
        word_counts = {pt: Counter() for pt, _en in EMOTIONS}
        for token in tokens:
            for emotion in self.lexicon.get(token, set()):
                if emotion in counts:
                    counts[emotion] += 1
                    word_counts[emotion][token] += 1

        dominant = ""
        if any(counts.values()):
            dominant = max(counts, key=lambda emotion: counts[emotion])

        out: Dict[str, object] = {"emo_dominante": dominant}
        for emotion, _en in EMOTIONS:
            out[f"emo_pct_{emotion}"] = (
                round(100 * counts[emotion] / total_words, 1) if total_words else 0.0
            )
        out["emotion_words"] = {
            emotion: words.most_common(10) for emotion, words in word_counts.items()
        }
        return out


def _to_pt_emotion(value: str) -> str:
    norm = normalize(value)
    if norm in {normalize(pt) for pt, _en in EMOTIONS}:
        for pt, _en in EMOTIONS:
            if norm == normalize(pt):
                return pt
    return EN_TO_PT.get(norm, "")
