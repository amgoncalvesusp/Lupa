# Lupa

**Lupa** is a standalone desktop application for **content analysis and textual metrics** over PDF, DOCX and TXT document corpora. It is designed for academic research that requires standardized, auditable and reproducible corpus analysis, with special attention to content analysis and qualitative interpretation workflows.

[Portuguese README](README.md)

![Language](https://img.shields.io/badge/Python-3.10%2B-blue)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)
![GUI](https://img.shields.io/badge/GUI-PyQt6-brightgreen)
![OCR](https://img.shields.io/badge/OCR-Tesseract-yellow)

## Overview

Lupa processes documents in batches and returns:

- Word counts for the full extracted text and the analytical corpus.
- User-defined term, expression and coding-category counts.
- Sentence-level sentiment analysis using LeIA / VADER-PT.
- NRC discrete emotions when the editable lexicon file is populated.
- Readability, lexical diversity, keyword frequency and n-grams.
- KWIC concordance and sentence-level term co-occurrence.
- Brazilian territorial mentions through an editable gazetteer.
- Bibliographic metadata: title, authors, affiliations, year and document type, with manual review.
- Corpus-level analyses: consolidated authors/institutions, dispersion, keyness, NPMI, similarity and temporal lexical change.
- Reliability indicators for extraction quality and OCR usage.

The interface, integrated help and exported labels can be switched between Portuguese and English from the language button in the application header.

## Features

- PyQt6 desktop interface with drag-and-drop for PDFs, DOCX, TXT files and folders.
- Asynchronous processing with progress feedback.
- Optional Tesseract OCR for scanned PDFs.
- Offline automatic detection of title, authors, affiliations, year and document type.
- Auditable manual metadata review saved in `.lupa.json` projects.
- Interactive charts for time series, document comparison, sentiment, lexical dispersion, territory, authors, institutions, keyness, similarity, NPMI and sentiment diagnostics.
- XLSX, CSV and JSON exports with an automatic methodology report.
- Fully offline processing; documents are not sent to external services.

## Installation

### End users

Run `LupaSetup-1.0.1-x64.exe`. The installer is per-user, does not require administrator privileges and installs Lupa under `%LOCALAPPDATA%\Programs\Lupa`.

### Development

Requirements:

- Python 3.10 or later.
- Windows 10/11 recommended.
- Tesseract OCR, optional for scanned PDFs.

```bash
git clone https://github.com/<user>/Lupa.git
cd Lupa
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m src.main
```

## Usage

1. In **Corpus**, drop documents into the dotted area or click **Add files**.
2. Enter terms/categories and select the desired analysis modules.
3. Enable OCR only when scanned PDFs are present, then click **Process corpus**.
4. Review results, open document details or use **Explore** for visual comparisons.
5. Export to XLSX, CSV or JSON.

## Term Syntax

| Input | Behavior |
|---|---|
| `climate` | Single-word search, case-insensitive and accent-insensitive |
| `climate change` | Multi-word sequence with flexible whitespace |
| `"greenhouse effect"` | Exact phrase search |
| `MITIGATION: carbon, "greenhouse effect"` | Coding category that sums member terms |
| `# comment` | Ignored line |

## Methodology

Lupa uses deterministic and auditable methods:

- LeIA / VADER-PT for sentence-level sentiment.
- Flesch adapted to Brazilian Portuguese for readability.
- TTR, Guiraud and MATTR for lexical diversity.
- Keyword frequency, n-grams and KWIC for content-analysis support.
- Sentence co-occurrence for descriptive term association.
- Editable gazetteer and lexicon files for territorial mentions and emotions.

All exported datasets include methodology metadata and detail tables where applicable.

## Tests

```bash
pip install -r requirements-dev.txt
pytest
pytest --cov=src/core
```

The current project coverage for owned code is approximately 92%.

## Authors

- Adriano Marques Gonçalves — Universidade de Araraquara (UNIARA)
- Thaís Angeli — Secretaria de Educação de Araraquara

## License

MIT. See [LICENSE](LICENSE).

## Citation

> GONÇALVES, A. M.; ANGELI, T. *Lupa: tool for content analysis and textual metrics of document corpora*. Araraquara: UNIARA, 2026.
