"""Offline-first bibliographic metadata extraction with explicit provenance."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Optional

from .metadata_detector import YEAR_PATTERN, _detect_document_type

_DOI = re.compile(r"\b10\.\d{4,9}/[-._;()/:A-Z0-9]+", re.IGNORECASE)
_ORCID = re.compile(r"\b\d{4}-\d{4}-\d{4}-\d{3}[\dX]\b", re.IGNORECASE)
_ISSN = re.compile(r"\bISSN\s*[:#]?\s*(\d{4}-\d{3}[\dX])\b", re.IGNORECASE)
_ISBN = re.compile(r"\bISBN(?:-1[03])?\s*[:#]?\s*([\dX -]{10,20})", re.IGNORECASE)
_EXPLICIT_DATE = re.compile(
    r"(?:publicad[oa]\s+em|data\s+de\s+publica(?:c|ç)(?:a|ã)o|published\s+(?:in|on))"
    r"[^\n]{0,45}?(?<!\d)(199\d|20[0-3]\d)(?!\d)",
    re.IGNORECASE,
)
_AUTHOR_LINE = re.compile(r"^(?:autores?|authors?|por|by)\s*[:\-]?\s*(.+)$", re.IGNORECASE)
_AFFILIATION_WORDS = re.compile(
    r"\b(universidade|university|instituto|institute|faculdade|departamento|department|"
    r"minist[eé]rio|funda[cç][aã]o|centro de pesquisa|laborat[oó]rio|secretaria)\b",
    re.IGNORECASE,
)
_NON_TITLE = re.compile(
    r"^(?:autores?|authors?|por|by|resumo|abstract|palavras-chave|keywords?|doi|issn|isbn)\b",
    re.IGNORECASE,
)


def extract_embedded_metadata(path: str | Path) -> Dict[str, str]:
    """Read metadata embedded in PDF or DOCX containers without network access."""
    source = Path(path)
    try:
        if source.suffix.lower() == ".pdf":
            import fitz

            with fitz.open(source) as document:
                return {
                    str(key): str(value)
                    for key, value in (document.metadata or {}).items()
                    if value not in (None, "")
                }
        if source.suffix.lower() == ".docx":
            from docx import Document

            props = Document(str(source)).core_properties
            values = {
                "title": props.title,
                "author": props.author,
                "subject": props.subject,
                "keywords": props.keywords,
                "created": props.created.isoformat() if props.created else "",
                "modified": props.modified.isoformat() if props.modified else "",
            }
            return {key: str(value) for key, value in values.items() if value}
    except (OSError, ValueError, RuntimeError):
        return {}
    return {}


def detect_bibliographic_metadata(
    pages_text: List[str],
    filename: str = "",
    embedded_metadata: Optional[Mapping[str, object]] = None,
) -> Dict[str, object]:
    """Extract conservative metadata and retain the source used for each field."""
    embedded = {str(k): str(v).strip() for k, v in (embedded_metadata or {}).items() if v}
    head = "\n".join(pages_text[:3])
    lines = [line.strip() for line in head.splitlines() if line.strip()]
    evidence: Dict[str, Dict[str, object]] = {}

    title = _embedded_value(embedded, "title")
    if title:
        evidence["title"] = _evidence("embedded_metadata", title, 0.98)
    else:
        title = _infer_title(lines)
        if title:
            evidence["title"] = _evidence("first_page", title, 0.65)

    author_value = _embedded_value(embedded, "author", "authors")
    author_source = "embedded_metadata"
    if not author_value:
        author_value = _find_author_line(lines)
        author_source = "first_page"
    author_names = _split_people(author_value)
    affiliations = _find_affiliations(lines)
    authors = [
        {
            "name": name,
            "role": "author",
            "affiliations": list(affiliations) if len(author_names) == 1 else [],
            "confidence": 0.95 if author_source == "embedded_metadata" else 0.72,
            "source": author_source,
        }
        for name in author_names
    ]
    if authors:
        evidence["authors"] = _evidence(author_source, author_value, authors[0]["confidence"])
    if affiliations:
        evidence["affiliations"] = _evidence("first_page", "; ".join(affiliations), 0.7)

    year, year_source, year_excerpt = _publication_year(head, filename, embedded)
    if year:
        evidence["publication_year"] = _evidence(year_source, year_excerpt, 0.9 if year_source == "embedded_metadata" else 0.78)

    document_type = _detect_document_type(head, filename) or "Não identificado"
    identifiers = _identifiers(head)
    complete_fields = sum(bool(value) for value in (title, authors, year, affiliations))
    return {
        "title": title or "",
        "publication_year": year or "",
        "document_type": document_type,
        "authors": authors,
        "contributors": list(authors),
        "affiliations": [
            {"name": name, "source": "first_page", "confidence": 0.7}
            for name in affiliations
        ],
        "authors_display": "; ".join(author_names),
        "affiliations_display": "; ".join(affiliations),
        "identifiers": identifiers,
        "metadata_evidence": evidence,
        "metadata_status": "completo" if complete_fields >= 3 else "incompleto",
    }


def _embedded_value(metadata: Mapping[str, str], *keys: str) -> str:
    lowered = {key.lower(): value for key, value in metadata.items()}
    return next((lowered[key.lower()] for key in keys if lowered.get(key.lower())), "")


def _infer_title(lines: List[str]) -> str:
    for line in lines[:12]:
        if _NON_TITLE.search(line) or _AFFILIATION_WORDS.search(line):
            continue
        if 4 <= len(line) <= 240 and len(line.split()) >= 2:
            return line
    return ""


def _find_author_line(lines: Iterable[str]) -> str:
    for line in list(lines)[:25]:
        match = _AUTHOR_LINE.match(line)
        if match:
            return match.group(1).strip()
    return ""


def _split_people(value: str) -> List[str]:
    if not value:
        return []
    normalized = re.sub(r"\s+(?:e|and|&)\s+", ";", value, flags=re.IGNORECASE)
    names = [part.strip(" ,.;") for part in re.split(r"[;|]", normalized)]
    return [name for name in names if 2 <= len(name.split()) <= 8 and not _AFFILIATION_WORDS.search(name)]


def _find_affiliations(lines: Iterable[str]) -> List[str]:
    found = []
    for line in list(lines)[:35]:
        if _AFFILIATION_WORDS.search(line) and len(line) <= 240 and line not in found:
            found.append(line.strip(" ,.;"))
    return found


def _publication_year(head: str, filename: str, metadata: Mapping[str, str]):
    for key in ("date", "creationdate", "created", "publicationdate", "modified"):
        value = _embedded_value(metadata, key)
        match = re.search(r"(?:D:)?(199\d|20[0-3]\d)", value)
        if match:
            return match.group(1), "embedded_metadata", value
    explicit = _EXPLICIT_DATE.search(head)
    if explicit:
        return explicit.group(1), "first_page", explicit.group(0)
    first_lines = "\n".join(head.splitlines()[:15])
    match = YEAR_PATTERN.search(first_lines)
    if match:
        return match.group(0), "first_page", match.group(0)
    match = YEAR_PATTERN.search(filename)
    if match:
        return match.group(0), "filename", filename
    return "", "", ""


def _identifiers(text: str) -> Dict[str, List[str]]:
    return {
        "doi": _unique(match.rstrip(".,;") for match in _DOI.findall(text)),
        "orcid": _unique(_ORCID.findall(text)),
        "issn": _unique(_ISSN.findall(text)),
        "isbn": _unique(re.sub(r"\s+", "", item) for item in _ISBN.findall(text)),
    }


def _unique(values: Iterable[str]) -> List[str]:
    return list(dict.fromkeys(value for value in values if value))


def _evidence(source: str, excerpt: str, confidence: float) -> Dict[str, object]:
    return {"source": source, "excerpt": excerpt[:300], "confidence": confidence}
