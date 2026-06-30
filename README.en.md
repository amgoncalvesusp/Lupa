# Lupa

**Lupa** is a standalone desktop application for **content analysis and textual metrics** over PDF, DOCX, and TXT files, in a standardized, auditable, and reproducible manner. It is designed for academic research requiring methodological rigor in document corpus analysis—with an emphasis on content analysis (Bardin) and meaning cores (Aguiar & Ozella).

> English documentation is available in [README.en.md](README.en.md). The application interface can be switched between Portuguese and English from the language button in the header.

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21053241.svg)](https://doi.org/10.5281/zenodo.21053241)
![Language](https://img.shields.io/badge/Python-3.10%2B-blue)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)
![GUI](https://img.shields.io/badge/GUI-PyQt6-brightgreen)
![OCR](https://img.shields.io/badge/OCR-Tesseract-yellow)

---

## Overview

Lupa processes documents in batches, performing text extraction and analysis following explicit and auditable rules. For each document, it returns:

- **Word count**: total (entire text) and **analytical corpus** (substantive content, automatically excluding pre-textual elements)
- **Term and expression search** defined by the researcher (total and in the corpus)
- **Sentiment analysis** (LeIA / VADER-PT) per sentence
- **Discrete emotions** (NRC EmoLex, when the editable lexicon is populated)
- **Textual metrics**: readability (Flesch-PT), lexical diversity (TTR / Guiraud / MATTR), keyword frequency
- **Concordance (KWIC)**: context surrounding each occurrence of terms
- **Co-occurrence**: pairs of terms appearing in the same sentence
- **Territorial mentions**: Brazilian states, regions, and biomes via an editable gazetteer
- **Bibliographic metadata**: title, authors, affiliations, year, document type, and identifiers, with evidence and manual review
- **Corpus-level analysis**: consolidation of authors/institutions, DP dispersion, keyness, NPMI, similarity, and temporal lexical change
- **Reliability indicators**: pages with text, problematic pages, OCR usage, degree of confidence

Results are presented in a modern graphical user interface and are exportable to formatted XLSX, CSV, and JSON, with summary and detailed outputs (excluded pages, sentences, word frequencies, KWIC concordance).

## Key Features

- PyQt6 graphical interface with drag-and-drop support for multiple PDFs, DOCX, TXT files, and folders
- Language button to toggle the interface, integrated help, and exports between Portuguese and English
- Asynchronous processing (non-blocking UI) with progress bars per file and overall
- Automatic OCR via Tesseract for scanned PDFs (Portuguese language)
- Heuristic detection of pre-textual pages (cataloging data, table of contents, staff page, list of ministers/authorities, etc.)
- Offline automatic detection of title, authors, affiliations, year, document type, and identifiers from embedded metadata and headers
- Auditable manual metadata review, persisted in the project; authors and institutions are consolidated across the corpus
- Presidential detection remains available internally for compatibility, but is hidden and disabled
- Word and expression search with exact phrase support using quotation marks
- Sentiment analysis in Portuguese (LeIA / VADER-PT) per sentence, with exportable details for content analysis and meaning cores
- Discrete emotions using an editable NRC lexicon (`data/nrc_emolex_pt.txt`), with a word audit trail
- Textual metrics: readability (Flesch-PT), lexical diversity (TTR / Guiraud / MATTR), frequency, and lexical cohesion segmentation
- KWIC Concordance: context surrounding each occurrence of search terms ("Concordance (KWIC)" tab), the context unit in Bardin's content analysis
- Term co-occurrence per sentence and temporal synthesis by corpus year
- Exploration hub with 14 interactive charts, including authors, institutions, DP dispersion, keyness, similarity, NPMI, lexical change, and sentiment diagnostics
- Brazilian territorial mentions via `data/gazetteer_br.json`
- Save and open `.lupa.json` projects with files, terms, categories, and flags
- Export in formatted XLSX, interoperable CSV (`;`, `utf-8-sig`), and JSON for archiving/re-use in R or Python
- Integrated documentation (F1 shortcut) explaining all rules and workflows
- Fully offline application; no data is sent to external services

## Screenshots

> Add screenshots of the main interface, the help dialog, and an exported XLSX file here.

---

## Installation

### Option 1: End User (Windows Installer)

Execute `LupaSetup-1.0.1-x64.exe`. Installation is done per-user in `%LOCALAPPDATA%\Programs\Lupa`, requiring no administrative privileges, and creates shortcuts in the Start Menu and, optionally, on the Desktop.

The installer includes the Python runtime, Lupa's dependencies, and Tesseract OCR.
Windows 10 1809 or later, on x64 architecture, is required.

### Option 2: Development (from Source Code)

**Requirements:**

- Python 3.10 or higher
- Windows 10/11 (tested); Linux/macOS are likely compatible with adjustments
- Tesseract-OCR installed (optional, only for scanned PDFs)

**Steps:**

```bash
git clone https://github.com/amgoncalvesusp/Lupa.git
cd Lupa
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m src.main
```

### Tesseract (OCR)

Only required if you process scanned PDFs (image-only).

1. Download the Windows version from: <https://github.com/UB-Mannheim/tesseract/wiki>
2. During installation, select the **Portuguese** (`por`) language pack
3. Keep the default path `C:\Program Files\Tesseract-OCR` for automatic detection

The software detects Tesseract upon startup and enables/disables the OCR option accordingly.

---

## How to Use

### Basic Flow

1. In **Corpus**, drag documents to the dotted area or click **Add files**. Folders are also accepted (PDF, DOCX, and TXT files will be included).
2. In the **Analysis Configuration** panel, input terms/categories and select the desired modules.
3. Enable OCR only when there are scanned PDFs, and click **Process corpus**.
4. The **Results** area opens upon completion with the batch summary, the auditable table, details, and export options.
5. Use **Exploration** in the sidebar to compare documents, filters, and series without leaving the main window.

### Term Search Syntax

| Input                      | Behavior                                                   |
|----------------------------|------------------------------------------------------------|
| `clima`                    | Simple word, accent-insensitive, and case-insensitive      |
| `mudança do clima`         | Sequence allowing variable whitespace between words        |
| `"efeito estufa"`          | Exact phrase search, within word boundaries                |
| `# comentário`             | Ignored line                                               |
| (blank line)               | Ignored                                                    |

**Example:**

```text
# Terms related to mitigation
carbono
desmatamento
"efeito estufa"
"mudança do clima"
mitigação

# Terms related to adaptation
adaptação
resiliência
"perdas e danos"
```

Search is case and accent-insensitive. Each term returns two counts: one for the full PDF and another for the analytical corpus only.

### Accepted Formats

- **PDF**: extraction via PyMuPDF; if the document is scanned, Tesseract OCR can be applied.
- **DOCX**: paragraph extraction via `python-docx`; since the format does not expose printed pages, Lupa creates approximate blocks of up to 3000 characters.
- **TXT**: blocks separated by double line breaks; very large blocks are split into chunks of up to 3000 characters.

In DOCX/TXT, the "page" number in details represents a textual block, not a printed page.

### Word Counting Rules

**Counted as a word:**

- Sequences of letters (including accented ones): *política*, *açúcar*
- Hyphenated words as a single lexical unit: *cooperação-internacional*
- Acronyms formed by letters: *ONU*, *FMI*, *SUS*, *PIB*
- Letter-based abbreviations

**Not counted:**

- Isolated numbers (*2024*, *15*)
- Roman numerals as chapter markers (*III*, *IV*, *XIV*)
- Punctuation and symbols
- Stray characters resulting from OCR errors

### Analytical Corpus Detection

The software automatically identifies pages to be excluded from the analytical corpus count based on keywords and heuristics:

- Cover and title page
- Cataloging-in-publication data (ISBN, CDD, CDU, Presidency Library)
- Table of Contents or Index (also detected by dotted line patterns)
- Editorial/staff pages
- Lists of ministers and authorities
- Blank pages

The *Excluded Pages* tab in the exported XLSX file contains the complete list and the reason for each exclusion, allowing manual audit.

### Concordance (KWIC)

For each search term, the **Concordance (KWIC)** (*Keyword-In-Context*, enabled by default) option records the **context** around each occurrence—a few words to the left, the term, and a few words to the right. Unlike counts, this is a **qualitative** output: it allows reading each occurrence in context, the *unit of context* in Bardin's content analysis.

- Requires at least one search term; uses the same matching rules as term search (accent-insensitive, multi-word phrases supported).
- The original spelling of the context words is preserved in the export.
- Results appear in the **"Concordance (KWIC)"** tab of the XLSX: document number, filename, page, term, left context, match, and right context.

Reference: Bardin, L. (2011). *Análise de Conteúdo*. São Paulo: Edições 70.

### Term Co-occurrence

When there are at least two search terms, Lupa counts pairs that appear in the same sentence of the analytical corpus. The **"Co-occurrence"** tab shows term A, term B, and the number of sentences. This is a descriptive measure of textual association, not evidence of causality.

### Textual Metrics

A set of measures (the "Textual metrics" checkbox, enabled by default) calculated over the analytical corpus and exported in the XLSX. Designed for content analysis and identifying meaning cores.

- **Readability — Flesch formula adapted to Portuguese:**
  `ILF = 248.835 − 1.015 × (words/sentences) − 84.6 × (syllables/words)`.
  Classes: Very easy (≥75), Easy (50–75), Difficult (25–50), Very difficult (<25).
  Syllable counting uses an approximate vocalic group heuristic.
- **Lexical Diversity:** TTR, Guiraud Index, and MATTR in moving windows. The effective window size and number of windows are exported.
- **Keyword Frequency:** the most frequent content words, after removing stopwords (editable list in `data/stopwords_pt.txt`). The top 10 most frequent words are shown in the main table, and the top 30 in the **"Word Frequency"** tab—the quantitative basis of content analysis.

**Methodological References:**

- Martins, T. B. F. et al. (1996). *Readability formulas applied to textbooks in Brazilian Portuguese*. Notas do ICMC-USP, n. 28.
- Guiraud, P. (1954). *Les caractères statistiques du vocabulaire*. Paris: PUF.
- Templin, M. (1957). *Certain language skills in children*. University of Minnesota Press.
- Bardin, L. (2011). *Análise de Conteúdo*. São Paulo: Edições 70.

### Discrete Emotions (NRC)

The **Emotions (NRC)** analysis uses an editable file at `src/core/data/nrc_emolex_pt.txt`, in the format `word<TAB>emotion`, to count eight emotions: joy, sadness, anger, fear, trust, disgust, surprise, and anticipation. The file is distributed empty by default to comply with the NRC Word-Emotion Association Lexicon terms; once populated by the researcher, the XLSX will include the **"Emotions (Words)"** tab with the audit trail.

Reference: Mohammad, S. M. & Turney, P. D. (2013). *Crowdsourcing a Word-Emotion Association Lexicon*. Computational Intelligence, 29(3).

### Territorial Mentions

Lupa counts mentions of Brazilian states, regions, and biomes using the editable gazetteer `src/core/data/gazetteer_br.json`. Long variants take priority over short variants to avoid double counting within the same segment. The output appears in the "Territorial mentions" column and the **"Territorial Mentions"** tab.

### Temporal Synthesis of the Corpus

When the batch has documents from two or more distinct years, the XLSX includes the **"Synthesis by Year"** tab: number of documents, corpus words, descriptive averages of sentiment/readability, and counts per term/category. The main window enables the **Results** and **Exploration** areas after processing.

### Interactive Charts

The **Exploration** area offers a visual hub based on `QPainter`, with no heavy dependencies and entirely offline. The following are available:

- **Time Series:** combines volume, sentiment, readability, terms, and categories by year.
- **Document Comparison:** compares words, terms, categories, territory, emotion, or keyword selected.
- **Sentiment:** stacked bars of positive, neutral, and negative sentences, by document or year.
- **Lexical Dispersion:** readability × TTR; dot size represents words, and color represents sentiment.
- **Co-occurrence Matrix:** symmetric heatmap of term pairs in the same sentence.
- **Territorial Profile:** ranking of mentioned states, regions, and biomes.

Controls allow filtering by year/document, normalizing counts per 1000 words, hiding series via the legend, zooming with the mouse wheel, copying the displayed data, and exporting the chart as a PNG. Clicking on a document bar or dot opens its details. Charts are descriptive: they do not represent statistical inference or causal relationships.

### President Detection (Legacy)

State leader identification remains in the engine for compatibility with historical projects, but the option is hidden and disabled for general corpora. The "President" column is omitted from the table and the XLSX.

The list is external to the code, at `src/core/data/presidents.json`, and can be edited to adapt the tool to other countries or periods:

```json
{
  "presidents": [
    {
      "canonical": "Official Name",
      "start": 2023,
      "end": 2026,
      "variants": ["Official Name", "Nickname"]
    }
  ]
}
```

- `start`/`end`: mandate years (YYYY), used to disambiguate by document year.
- `variants`: spellings searched (case-insensitive) at the beginning of the document.

If the file is missing or invalid, detection returns empty—the rest of the analysis continues normally.

### Confidence Level

| Level  | Criterion                                                             |
|--------|-----------------------------------------------------------------------|
| High   | ≥95% of pages have extracted text; little to no OCR                   |
| Medium | 80–95% of pages have text; or intensive OCR usage                     |
| Low    | Less than 80% of pages have extracted text                            |

### Sentiment Analysis

Sentiment analysis uses a **rule- and lexicon-based** model (VADER), ensuring **transparency and reproducibility**: each score is traceable back to the word and rule that produced it—a desirable property in qualitative interpretive research, unlike "black-box" models.

- **Method:** VADER (*Valence Aware Dictionary and sEntiment Reasoner*)—a lexicon validated by human judges combined with heuristics for negation, intensifiers, capitalization emphasis, and punctuation. It produces a normalized `compound` score in `[-1, +1]`.
- **Adaptation to Portuguese:** **LeIA** (*Léxico para Inferência Adaptada*), a VADER fork for Brazilian Portuguese (lexicon and rules vendored in the project under the MIT license, fully offline).
- **Unit of Analysis:** the **sentence**. Each sentence receives a score and classification (Positive `compound ≥ 0.05`; Negative `compound ≤ -0.05`; Neutral otherwise). Per document, the general classification, average compound score, and percentage of positive/negative/neutral sentences are reported.
- **Output for Qualitative Analysis:** the XLSX includes the **"Sentiment (Sentences)"** tab containing every sentence, page, score, and classification. This detail provides the **recording units** for Content Analysis (Bardin) and the **affective pre-indicators** for Meaning Cores (Aguiar & Ozella), allowing the researcher to group affect-laden excerpts into indicators and cores.

Sentiment analysis can be toggled on/off via a checkbox in the interface.

**Methodological References:**

- Hutto, C. J. & Gilbert, E. E. (2014). *VADER: A Parsimonious Rule-based Model for Sentiment Analysis of Social Media Text*. ICWSM-14. Ann Arbor, MI.
- Almeida, R. J. de A. *LeIA — Léxico para Inferência Adaptada*. <https://github.com/rafjaa/LeIA>
- Bardin, L. (2011). *Análise de Conteúdo*. São Paulo: Edições 70.
- Aguiar, W. M. J. & Ozella, S. (2006; 2013). *Núcleos de significação como instrumento para a apreensão da constituição dos sentidos* / *Apreensão dos sentidos: aprimorando a proposta dos núcleos de significação*.

### Exporting Results

Lupa exports the processed batch in three formats:

- **XLSX**: formatted spreadsheet for reading, manual auditing, and sharing.
- **CSV**: creates a folder with `resultados.csv`, `metodologia.txt`, and detailed files when data is present (`sentencas.csv`, `palavras.csv`, `ngramas.csv`, `categorias.csv`, `kwic.csv`, `paginas_excluidas.csv`). The files use `;` separator and `utf-8-sig` encoding for compatibility with Excel in Portuguese/Spanish/etc.
- **JSON**: a single file with `gerado_por`, `metodologia`, and `documentos`, preserving the complete results of each document for archiving or re-use in R/Python.

Every export includes an **automatic methodological report** containing the date, files, formats, flags, terms/categories, analyses performed, configuration files, and methodological criteria. In the XLSX, it appears in the **"Methodology"** tab.

### `.lupa.json` Projects

The **File** menu allows saving and opening analysis projects. The project file stores document paths, the raw text of terms/categories, and analysis flags. When opening a project, missing files are reported without preventing the others from loading.

### Keyboard Shortcuts

| Shortcut      | Action                           |
|---------------|----------------------------------|
| `Ctrl+O`      | Add documents                    |
| `Ctrl+S`      | Save project                     |
| `Ctrl+Shift+O`| Open project                     |
| `Ctrl+E`      | Export results                   |
| `Ctrl+Q`      | Exit                             |
| `F1`          | Open integrated documentation    |

---

## Project Structure

```text
Lupa/
├── src/
│   ├── main.py                  # entry point
│   ├── core/
│   │   ├── word_counter.py      # word counting rules (Unicode regex)
│   │   ├── corpus_filter.py     # page exclusion detection
│   │   ├── metadata_detector.py # year/president/document detection
│   │   ├── term_search.py       # term and expression search
│   │   ├── ocr_engine.py        # Tesseract wrapper + fallback
│   │   ├── pdf_processor.py     # pipeline orchestrator
│   │   └── exporter.py          # formatted XLSX export
│   └── gui/
│       ├── main_window.py       # main window
│       ├── help_dialog.py       # integrated help dialog
│       ├── workers.py           # QThread workers (asynchronous processing)
│       └── styles.py            # stylesheet (Catppuccin Mocha dark theme)
├── requirements.txt
├── build.bat                    # PyInstaller script (Windows)
├── LICENSE
└── README.md
```

### Technologies

- **PyQt6** — Graphical user interface
- **PyMuPDF (fitz)** — Text extraction and page rendering
- **pytesseract** + **Pillow** — Python wrapper for Tesseract OCR
- **openpyxl** — XLSX generation
- **regex** — Advanced Unicode support for `\p{L}` classes
- **PyInstaller** — Executable packaging (build)

---

## Building the Executable

In a Windows environment with Python and dependencies installed:

```cmd
build.bat
```

Output: `dist\Lupa.exe`

To generate a local installer, see the [`installer/`](installer/) directory (PowerShell script `install.ps1`, which has no dependencies, and Inno Setup script `Lupa.iss`).

If Tesseract is installed at `C:\Program Files\Tesseract-OCR`, the build script will automatically bundle it into the executable. Otherwise, the end user will need to install it separately.

---

## Reproducibility

All counting follows deterministic rules with no random components. Processing the same PDFs under the same conditions yields identical results. Differences between runs can only occur when OCR is applied to marginal quality pages where character recognition may vary.

Full documentation of the counting, exclusion, and confidence classification criteria is embedded in the software (F1 shortcut) and this README, ensuring process auditability.

---

## Tests

The suite uses **pytest** and covers the counting engine, term search, corpus filtering, metadata detection, analyzers (including sentiment), and exporting, as well as an integration test of the full pipeline on a synthetic PDF.

```bash
pip install -r requirements-dev.txt
pytest                       # runs the suite
pytest --cov=src/core        # with coverage report
```

Current code coverage for owned code (excluding the vendored LeIA library) is **~92%**.

---

## Known Limitations

- Pre-textual page detection is heuristic and may produce false positives on atypical layouts. Always check the *Excluded Pages* tab of the exported XLSX.
- Automatic year and president detection is based on textual patterns; in PDFs with low extraction quality, it may fail (fields return empty).
- OCR adds significant processing time (seconds per page). Use only when necessary.

---

## Authors

Work developed within the Graduate Program in Territorial Development and Environment of the University of Araraquara (UNIARA):

- Adriano Marques Gonçalves — University of Araraquara (UNIARA)
- Thaís Angeli — Araraquara Education Secretariat

---

## License

MIT — see the [LICENSE](LICENSE) file for details.

---

## Citation

If you use this software in your research, please cite it as follows:

> GONÇALVES, A. M.; ANGELI, T. *Lupa: tool for content analysis and textual metrics of document corpora in PDF*. Araraquara: UNIARA, 2026. DOI: [10.5281/zenodo.21053241](https://doi.org/10.5281/zenodo.21053241).

> Lupa is derived from *WordCounter*.
