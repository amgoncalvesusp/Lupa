"""Detail-only thematic segmentation analyzer."""

from typing import Dict, List

from .base import ColumnSpec, DocumentContext
from ..qualitative_coding import segment_by_lexical_cohesion


class SegmentationAnalyzer:
    name = "segmentation"

    def columns(self) -> List[ColumnSpec]:
        return []

    def run(self, ctx: DocumentContext) -> Dict[str, object]:
        pages = [ctx.pages_text[index - 1] for index in ctx.analytical_page_numbers]
        segments = segment_by_lexical_cohesion(pages)
        return {"segments": segments, "segment_count": len(segments)}

