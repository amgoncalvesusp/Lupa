# Lupa — Implementation Plan (Next Analyses)

> Translation of [PLANO_IMPLEMENTACAO.md](PLANO_IMPLEMENTACAO.md).

> **For the implementing AI:** this document is self-contained. Read "Context and conventions" before writing code. Implement phases in order. Each phase includes target files, data structures, acceptance criteria and required tests. Do not break existing tests.

## Context and Conventions

### What Lupa Is

Lupa is a Windows desktop application built with PyQt6 for content analysis and textual metrics over PDFs and other document formats. It targets academic qualitative research, especially Bardin's content analysis and Aguiar & Ozella's meaning nuclei, but it is general enough for heterogeneous corpora.

### Non-negotiable Constraints

- **100% offline.** No network calls, APIs or model downloads by default.
- **Auditable.** Use lexical/rule-based methods with publishable citations. Every aggregate number needs a detail trail in XLSX and/or the details dialog.
- **Lightweight.** Do not add heavy dependencies such as torch, transformers or spaCy models. Prefer small pure-Python packages or vendored code with license and citation.
- **Bilingual UI and outputs.** The interface, integrated help and exports support Portuguese and English. Code and comments remain in English.

### Analyzer Pipeline

`PDFProcessor.process()` extracts text once, builds a `DocumentContext`, runs analyzer objects and merges their output dictionaries into one result per document.

Each analyzer implements `Analyzer` from `src/core/analysis/base.py`: a `name`, `columns() -> list[ColumnSpec]` and `run(ctx) -> dict`. Exporters and GUI derive schemas from `columns()` instead of hardcoding columns.

### Recipe for Adding an Analysis

1. Create a module under `src/core/analysis/` with a class docstring that explains method and citation.
2. Register it in `build_default_analyzers()` and `__all__`.
3. If optional, thread the flag through processor, worker and GUI checkbox.
4. Add detail rows to XLSX and the details dialog when useful.
5. Add pytest tests in `tests/test_<name>.py` and update factory tests if the default analyzer set changes.
6. Document method, citation and exported sheets in the help dialog and README.
7. Put editable config files in `src/core/data/` with safe fallbacks.

## Commands

```cmd
"..\WordCounter\venv_build\Scripts\python.exe" -m pytest
"..\WordCounter\venv_build\Scripts\python.exe" -m pytest --cov=src/core
"..\WordCounter\venv_build\Scripts\python.exe" -m PyInstaller --noconfirm Lupa.spec
powershell -ExecutionPolicy Bypass -File installer\install.ps1
```

## Current State

Existing analyzers include metadata, document stats, word count, readability, lexical diversity, keywords, n-grams, sentiment, categories, term search, KWIC, co-occurrence, emotions, geography, segmentation and corpus analyses. XLSX/CSV/JSON exports and interactive charts are integrated.

## Phase A — CSV/JSON Export

Goal: make analysis outputs interoperable with R, Python, Iramuteq and reproducible archival workflows.

Implementation:

- `src/core/exporter_plain.py` writes the main CSV plus detail CSVs only when data exists.
- JSON stores `generated_by`, methodology, public result dictionaries and corpus analyses.
- GUI dispatches XLSX/CSV/JSON by selected suffix.
- Help section is renamed to Export (XLSX, CSV, JSON).

Tests: main CSV header and row count, detail CSVs conditional on data, JSON round trip and removal of internal keys.

## Phase B — NRC-PT Discrete Emotions

Goal: measure eight emotions beyond positive/negative polarity: joy, sadness, anger, fear, trust, disgust, surprise and anticipation.

Implementation:

- Editable TSV lexicon at `src/core/data/nrc_emolex_pt.txt`.
- `EmotionAnalyzer` loads lexicon with empty fallback and returns percentages, dominant emotion and word-level audit trail.
- Optional GUI checkbox.
- XLSX sheet `Emotions (Words)` and details-dialog tab.

Tests: synthetic lexicon, empty corpus, accent normalization and factory behavior when disabled.

## Phase C — Temporal Panel / Corpus Summary

Goal: reveal yearly trajectories in annual corpora.

Implementation:

- `src/core/corpus_summary.py` groups results by year.
- XLSX sheet `Summary by Year` when there are two or more years.
- GUI charts include temporal volume, sentiment, readability, terms and categories.

Tests: correct aggregation, missing year group and absent sheet for one-year corpora.

## Phase D — Brazilian Territorial Mentions

Goal: map document geographic focus through states, regions and biomes.

Implementation:

- Editable `src/core/data/gazetteer_br.json`.
- `GeographyAnalyzer` performs accent-insensitive token-sequence matching, with longest variant winning.
- XLSX and details tabs expose the audit trail.

Tests: accented/unaccented detection, long-variant precedence, analytical-corpus filtering and missing-gazetteer fallback.

## Phase E — Term Co-occurrence

Goal: describe which searched terms occur together in the same sentence.

Implementation:

- `CooccurrenceAnalyzer` reuses sentence segmentation and term counting.
- Detail-only output: pairs with counts greater than zero.
- XLSX and details-dialog tabs.

Tests: same-sentence pairs count, separated sentences do not count, three terms produce three pairs and empty terms return an empty list.

## Phase F — DOCX and TXT Input

Goal: support mixed real-world corpora.

Implementation:

- `python-docx` dependency.
- `src/core/text_extractor.py` dispatches PDF, DOCX and TXT extraction.
- Keep `PDFProcessor = DocumentProcessor` alias for compatibility.
- GUI file filters and drop zone accept PDF/DOCX/TXT.
- Help documents approximate block-based pagination for DOCX/TXT.

Tests: synthetic DOCX, TXT blocks, PDF regression and clear error for unknown extensions.

## Phase G — Save/Load Analysis Project

Goal: make study configuration reproducible.

Implementation:

- `.lupa.json` stores raw terms/categories, flags and file paths.
- `src/core/project_io.py` validates version and reports missing files without blocking load.
- File menu actions save/open projects.

Tests: save/load round trip, missing-file reporting and unknown-version error.

## Phase Order

Implement A -> C -> D -> E -> B -> G -> F. Phase F is last because it changes the extraction backbone.

## Phase Completion Checklist

- [ ] `pytest` passes and `src/core` coverage remains at least 80%.
- [ ] Help is updated with method, citation and exported sheets.
- [ ] README lists the feature and config files when relevant.
- [ ] Conventional commit in Portuguese.
- [ ] Build and local installation open without error.
