"""Territorial mention analyzer based on an editable Brazilian gazetteer."""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

from .base import ColumnSpec, DocumentContext
from ..term_search import normalize
from ..word_counter import WORD_PATTERN


Place = Dict[str, object]


def _data_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS) / "src" / "core" / "data"
    return Path(__file__).resolve().parents[1] / "data"


def load_gazetteer(path: str | Path | None = None) -> List[Place]:
    try:
        with open(path or (_data_dir() / "gazetteer_br.json"), encoding="utf-8") as fh:
            raw = json.load(fh)
        return list(raw.get("places", []))
    except (OSError, ValueError, TypeError):
        return []


class GeographyAnalyzer:
    name = "geography"

    def __init__(self, places: List[Place] | None = None):
        self.places = load_gazetteer() if places is None else places
        self._variants = _prepare_variants(self.places)

    def columns(self) -> List[ColumnSpec]:
        return [ColumnSpec("geo_top", "Menções territoriais", 50, "text")]

    def run(self, ctx: DocumentContext) -> Dict[str, object]:
        counts: Dict[Tuple[str, str, str], int] = {}
        for page in ctx.analytical_page_numbers:
            tokens = [
                normalize(m.group(0)) for m in WORD_PATTERN.finditer(ctx.pages_text[page - 1])
            ]
            index = 0
            while index < len(tokens):
                match = self._match_at(tokens, index)
                if match is None:
                    index += 1
                    continue
                length, place = match
                key = (
                    str(place.get("name", "")),
                    str(place.get("type", "")),
                    str(place.get("uf", "")),
                )
                counts[key] = counts.get(key, 0) + 1
                index += length

        mentions = [
            (name, place_type, uf, count)
            for (name, place_type, uf), count in counts.items()
        ]
        mentions.sort(key=lambda item: (-item[3], item[0]))
        return {
            "geo_top": "; ".join(f"{name} ({count})" for name, _t, _uf, count in mentions[:5]),
            "geo_mentions": mentions,
        }

    def _match_at(self, tokens: List[str], index: int):
        for seq, place in self._variants:
            end = index + len(seq)
            if tokens[index:end] == seq:
                return len(seq), place
        return None


def _prepare_variants(places: List[Place]):
    prepared = []
    for place in places:
        variants = list(place.get("variants", []))
        name = place.get("name")
        if name:
            variants.append(str(name))
        for variant in variants:
            seq = [normalize(part) for part in str(variant).split() if normalize(part)]
            if seq == ["para"]:
                continue
            if seq:
                prepared.append((seq, place))
    prepared.sort(key=lambda item: len(item[0]), reverse=True)
    return prepared
