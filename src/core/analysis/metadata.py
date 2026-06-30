"""Document metadata analyzer (year, optional president, document type)."""

from typing import Dict, List

from .base import ColumnSpec, DocumentContext
from ..bibliographic_metadata import detect_bibliographic_metadata
from ..metadata_detector import detect_metadata


class MetadataAnalyzer:
    name = "metadata"

    def __init__(self, detect_president: bool = False):
        self.detect_president = detect_president

    def columns(self) -> List[ColumnSpec]:
        cols = [
            ColumnSpec("title", "Título", 35),
            ColumnSpec("authors_display", "Autores", 32),
            ColumnSpec("affiliations_display", "Afiliações", 36),
            ColumnSpec("year", "Ano", 8),
        ]
        if self.detect_president:
            cols.append(ColumnSpec("president", "Presidente", 28))
        cols.append(ColumnSpec("document", "Documento", 32))
        return cols

    def run(self, ctx: DocumentContext) -> Dict[str, object]:
        md = detect_metadata(
            ctx.pages_text, ctx.filename, detect_president=self.detect_president
        )
        # "president" key is always present so downstream consumers can use a
        # plain lookup; it is blank when detection is disabled.
        bibliographic = detect_bibliographic_metadata(
            ctx.pages_text, ctx.filename, ctx.source_metadata
        )
        return {
            **bibliographic,
            "year": bibliographic["publication_year"] or md["year"],
            "president": md["president"],
            "document": bibliographic["document_type"] or md["document"],
        }
