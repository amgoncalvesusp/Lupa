"""Document text extraction for PDF, DOCX and TXT inputs."""

import io
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

import fitz
from PIL import Image

from .ocr_engine import configure_tesseract, needs_ocr, ocr_image

BLOCK_CHARS = 3000


def extract_pages(
    path: str | Path,
    enable_ocr: bool = True,
    ocr_lang: str = "por",
    progress_cb: Optional[Callable[[int, int], None]] = None,
) -> Tuple[List[str], Dict]:
    """Extract document text as page-like blocks plus extraction statistics."""
    source = Path(path)
    suffix = source.suffix.lower()
    if suffix == ".pdf":
        return _extract_pdf(source, enable_ocr, ocr_lang, progress_cb)
    if suffix == ".docx":
        return _extract_docx(source, progress_cb)
    if suffix == ".txt":
        return _extract_txt(source, progress_cb)
    raise ValueError(f"Formato não suportado: {suffix or source.name}")


def _extract_pdf(
    path: Path,
    enable_ocr: bool,
    ocr_lang: str,
    progress_cb: Optional[Callable[[int, int], None]],
) -> Tuple[List[str], Dict]:
    tesseract_available = configure_tesseract() if enable_ocr else False
    doc = fitz.open(path)
    total_pages = len(doc)
    pages_text: List[str] = []
    ocr_used_pages: List[int] = []
    empty_pages: List[int] = []

    for i, page in enumerate(doc):
        text = page.get_text("text") or ""
        if enable_ocr and tesseract_available and needs_ocr(text):
            pix = page.get_pixmap(dpi=300)
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            ocr_text = ocr_image(img, lang=ocr_lang)
            if ocr_text and len(ocr_text.strip()) > len(text.strip()):
                text = ocr_text
                ocr_used_pages.append(i + 1)
        if not text.strip():
            empty_pages.append(i + 1)
        pages_text.append(text)
        if progress_cb:
            progress_cb(i + 1, total_pages)
    doc.close()
    return pages_text, _stats(pages_text, ocr_used_pages, empty_pages)


def _extract_docx(
    path: Path, progress_cb: Optional[Callable[[int, int], None]]
) -> Tuple[List[str], Dict]:
    from docx import Document

    document = Document(str(path))
    text = "\n\n".join(p.text for p in document.paragraphs if p.text.strip())
    pages = _chunk_text(text)
    if progress_cb:
        progress_cb(len(pages), len(pages))
    return pages, _stats(pages, [], [i + 1 for i, page in enumerate(pages) if not page.strip()])


def _extract_txt(
    path: Path, progress_cb: Optional[Callable[[int, int], None]]
) -> Tuple[List[str], Dict]:
    text = path.read_text(encoding="utf-8-sig")
    pages = _chunk_text_by_paragraph(text)
    if progress_cb:
        progress_cb(len(pages), len(pages))
    return pages, _stats(pages, [], [i + 1 for i, page in enumerate(pages) if not page.strip()])


def _chunk_text(text: str, size: int = BLOCK_CHARS) -> List[str]:
    if not text.strip():
        return [""]
    return [text[i : i + size] for i in range(0, len(text), size)]


def _chunk_text_by_paragraph(text: str, size: int = BLOCK_CHARS) -> List[str]:
    paragraphs = [p.strip() for p in text.replace("\r\n", "\n").split("\n\n") if p.strip()]
    if not paragraphs:
        return [""]
    pages: List[str] = []
    for paragraph in paragraphs:
        pages.extend(_chunk_text(paragraph, size=size))
    return pages


def _stats(pages_text: List[str], ocr_used_pages: List[int], empty_pages: List[int]) -> Dict:
    pages_with_text = sum(1 for text in pages_text if text.strip())
    return {
        "pages_with_text": pages_with_text,
        "pages_problematic": len(pages_text) - pages_with_text,
        "ocr_pages_count": len(ocr_used_pages),
        "ocr_pages_list": ocr_used_pages,
        "empty_pages": empty_pages,
    }
