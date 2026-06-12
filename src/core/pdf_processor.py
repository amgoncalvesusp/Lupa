"""Document processing orchestrator.

Extracts text once per document (PDF, DOCX or TXT), then runs pluggable
analyzers over a shared :class:`DocumentContext`. ``PDFProcessor`` is kept as a
compatibility alias for older callers and tests.
"""

from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

from .analysis import Analyzer, DocumentContext, build_default_analyzers
from .corpus_filter import classify_all_pages
from .ocr_engine import configure_tesseract
from .text_extractor import extract_pages


class DocumentProcessor:
    def __init__(
        self,
        enable_ocr: bool = True,
        ocr_lang: str = "por",
        search_terms: Optional[List[Tuple[str, bool]]] = None,
        analyzers: Optional[List[Analyzer]] = None,
        detect_sentiment: bool = True,
        detect_emotions: bool = True,
        detect_president: bool = True,
        detect_textmetrics: bool = True,
        detect_kwic: bool = True,
        categories=None,
    ):
        self.enable_ocr = enable_ocr
        self.ocr_lang = ocr_lang
        self.tesseract_available = configure_tesseract() if enable_ocr else False
        self.analyzers = (
            analyzers
            if analyzers is not None
            else build_default_analyzers(
                search_terms,
                detect_president=detect_president,
                detect_sentiment=detect_sentiment,
                detect_emotions=detect_emotions,
                detect_textmetrics=detect_textmetrics,
                detect_kwic=detect_kwic,
                categories=categories,
            )
        )

    def process(
        self,
        document_path: str,
        progress_cb: Optional[Callable[[int, int], None]] = None,
    ) -> Dict:
        path = Path(document_path)
        pages_text, extraction_stats = extract_pages(
            path,
            enable_ocr=self.enable_ocr,
            ocr_lang=self.ocr_lang,
            progress_cb=progress_cb,
        )
        total_pages = len(pages_text)
        ocr_used_pages = extraction_stats.get("ocr_pages_list", [])
        empty_pages = extraction_stats.get("empty_pages", [])

        page_classifications = classify_all_pages(pages_text)
        if path.suffix.lower() in {".docx", ".txt"} and not any(
            p["is_analytical"] for p in page_classifications
        ):
            page_classifications = [
                {
                    **p,
                    "is_analytical": bool(pages_text[p["page_number"] - 1].strip()),
                    "exclusion_reason": ""
                    if pages_text[p["page_number"] - 1].strip()
                    else p["exclusion_reason"],
                }
                for p in page_classifications
            ]
        excluded = [p for p in page_classifications if not p["is_analytical"]]
        analytical = [p for p in page_classifications if p["is_analytical"]]
        analytical_page_numbers = [p["page_number"] for p in analytical]

        pages_with_text = extraction_stats.get("pages_with_text", 0)
        pages_problematic = extraction_stats.get("pages_problematic", 0)
        confidence = self._assess_confidence(
            total_pages, pages_with_text, ocr_used_pages
        )

        ctx = DocumentContext(
            filename=path.name,
            pages_text=pages_text,
            analytical_page_numbers=analytical_page_numbers,
            total_pages=total_pages,
            stats={
                "pages_with_text": pages_with_text,
                "pages_problematic": pages_problematic,
                "ocr_pages_count": len(ocr_used_pages),
            },
        )

        result: Dict = {
            "filename": path.name,
            "ocr_pages_list": ocr_used_pages,
            "excluded_pages": excluded,
            "empty_pages": empty_pages,
            "confidence": confidence,
            "observations": self._build_observations(
                total_pages, pages_with_text, ocr_used_pages, empty_pages, len(excluded)
            ),
        }

        for analyzer in self.analyzers:
            result.update(analyzer.run(ctx))

        return result

    def _assess_confidence(self, total, with_text, ocr_pages):
        if total == 0:
            return "Baixo"
        ratio = with_text / total
        ocr_ratio = len(ocr_pages) / total if total else 0
        if ratio >= 0.95 and ocr_ratio < 0.2:
            return "Alto"
        if ratio >= 0.80:
            return "Médio"
        return "Baixo"

    def _build_observations(self, total, with_text, ocr_pages, empty, excluded):
        parts = []
        if ocr_pages:
            parts.append(f"OCR aplicado em {len(ocr_pages)} página(s)")
        if empty:
            parts.append(f"{len(empty)} página(s) sem texto extraível")
        parts.append(f"{excluded} página(s) excluída(s) do corpus analítico")
        return "; ".join(parts) if parts else "Extração limpa"


PDFProcessor = DocumentProcessor
