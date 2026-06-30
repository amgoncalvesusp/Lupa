# Implementation Plan: Metadata, Entities and Comparative Analyses

> Translation of [PLANO_METADADOS_E_ANALISES.md](PLANO_METADADOS_E_ANALISES.md).

> Status on 2026-06-20: phases 0 to 8 are implemented and integrated into written outputs, XLSX/CSV/JSON and visual exploration. Phase 9 includes core thematic segmentation, tabular import and Krippendorff alpha. Presidential detection remains only as internal compatibility. Reviewed metadata is persisted in v2 projects and v1 projects are migrated automatically.

## 1. Objective

Generalize Lupa for heterogeneous corpora and make it possible to answer, in an auditable way:

- who produced the documents;
- which institutions the authors were affiliated with;
- when and where documents were published;
- which document types make up the corpus;
- which people and institutions published most about a topic;
- how terms, associations and vocabulary vary across groups and periods.

Offline processing remains the default. DOI, ORCID or ROR enrichment will be optional, will send only public identifiers and will use local cache.

## 2. Methodological Principles

1. **Evidence before value:** every detected metadata field stores source, excerpt, page and confidence.
2. **Do not guess:** lack of evidence results in "Not identified".
3. **Person is not institution:** personal authors, corporate authors, editors, advisors and issuing bodies are distinct entities and roles.
4. **Mention is not authorship:** names found in the body or references cannot be automatically promoted to authors.
5. **Human correction prevails:** manually reviewed values are protected against automatic overwriting.
6. **Transparent counting:** consolidations offer both full and fractional counts for multi-author documents.
7. **Descriptive results:** publication volume must not be presented as impact, quality or scientific influence.
8. **Compatibility:** existing projects and exports continue to open.

## 3. Presidential Detection Scope

- Remove the visible UI option and use `detect_president=False` by default.
- Keep `presidents.json`, `_detect_president()` and the project flag for compatibility and possible future reactivation.
- Do not include a President column in new projects.
- Continue accepting the `presidente` key in version 1 projects and old results.

## 4. Data Model

### Document

```json
{
  "document_id": "sha256:...",
  "title": "Detected or reviewed title",
  "publication_year": 2024,
  "document_type": "Scientific article",
  "language": "pt",
  "publisher": "Publisher or source",
  "venue": "Journal, newspaper, event or organization",
  "identifiers": {
    "doi": "10.xxxx/xxxx",
    "isbn": "",
    "issn": "",
    "orcid": [],
    "law_number": "",
    "url": ""
  },
  "contributors": [],
  "metadata_evidence": [],
  "metadata_status": "review"
}
```

`document` is temporarily kept as an alias for `document_type` to preserve exporter and project compatibility.

### Contributor

```json
{
  "entity_id": "person:...",
  "entity_type": "person",
  "raw_name": "Maria da Silva",
  "canonical_name": "Maria da Silva",
  "roles": ["author"],
  "orcid": "",
  "affiliations": [],
  "confidence": "high"
}
```

Initial roles: `author`, `corporate_author`, `editor`, `advisor`, `issuer`, `translator` and `reporter`.

### Affiliation

Affiliations are many-to-many. If the document lists institutions but does not link them to specific authors, the affiliation remains document-level and is marked as `unassigned`.

### Evidence

Evidence records include field, value, source, page, snippet, confidence and whether the value is a manual override. Sources include DOI, embedded metadata, first page, filename, sidecar, manual and legacy.

## 5. Metadata Precedence

Publication year precedence: DOI API when enabled, structured file field, explicit first-page/header pattern, reporting byline date, filename and finally file creation date as low-confidence evidence.

Authors and contributors precedence: DOI/Crossref, structured file properties, first-page authorship block, bylines and issuing body for institutional documents. References and body names are excluded from authorship detection.

Affiliations precedence: DOI-associated structured affiliations, numbered or marked first-page blocks, institutional vocabulary lines and optional ROR normalization.

Document type is rule-based, score-based and conservative. Weak evidence or ties remain for review.

## 6. Architecture

- `text_extractor.py`: source metadata extraction for PDF, DOCX and TXT.
- `bibliographic_metadata.py`: detection orchestration and precedence.
- Identifier, contributor, affiliation, entity-normalization and metadata-provider modules for future optional enrichment.
- Corpus analyzers run after document-level analyzers and preserve existing contracts.
- `.lupa.json` projects evolve to version 2 with manual overrides, entity aliases/merges, group configuration, count mode, online-provider consent and cache references.

## 7. Implementation Phases

- **Phase 0:** bibliographic base and hidden president detection.
- **Phase 1:** consolidation of people and institutions.
- **Phase 2:** term dispersion.
- **Phase 3:** keyness between groups.
- **Phase 4:** normalized co-occurrence.
- **Phase 5:** MATTR lexical diversity.
- **Phase 6:** document similarity.
- **Phase 7:** temporal lexical change.
- **Phase 8:** sentiment diagnostics.
- **Phase 9:** thematic segmentation and human coding.

Each phase must end with methodology documentation, export integration, visualization where applicable, tests, coverage, security review and executable build.

## 8. Interface

Corpus: hide President, add metadata review control and show identification status by document.

Results: default columns are File, Title, Year, Type, Authors, Institutions, Pages, Words and Confidence. Long names go to details. `Review metadata` opens evidence-backed forms.

Exploration: authors, institutions, dispersion, keyness, similarity, co-occurrence and temporal-change modes, with coordinated filters and exportable tables.

## 9. Consolidated Counts

For each author and institution: documents, fractional documents, words, corpus share, active period, term/category counts and document-type distribution. Corporate authors enter organization summaries. Unconfirmed affiliations remain separate as "Affiliation to review".

## 10. Tests and Validation

Use TDD per phase: failing unit test, minimal implementation, integration tests for pipeline/exporters and E2E tests for add/process/review/consolidate/export. Owned-code coverage must remain at least 80%.

Metadata gold corpus: legally redistributable examples of scientific articles, laws, news reports, theses/dissertations, institutional reports and documents without metadata.

## 11. Risks and Controls

Controls address false authorship, homonyms, ambiguous affiliations, reference-year confusion, wrong document type, unavailable APIs, content leakage, rankings misread as impact, and small groups in keyness/JSD.

## 12. Main Methodological References

- Gries, S. T. (2008). *Dispersions and adjusted frequencies in corpora*. <https://doi.org/10.1075/ijcl.13.4.02gri>
- Rayson, P.; Garside, R. (2000). *Comparing Corpora using Frequency Profiling*. <https://aclanthology.org/W00-0901/>
- Dunning, T. (1993). *Accurate Methods for the Statistics of Surprise and Coincidence*. <https://aclanthology.org/J93-1003/>
- Church, K.; Hanks, P. (1989). *Word association norms, mutual information, and lexicography*. <https://doi.org/10.3115/981623.981633>
- Covington, M.; McFall, J. (2010). *Moving-Average Type-Token Ratio*. <https://doi.org/10.1080/09296171003643098>
- Bestgen, Y. (2025). *Estimating lexical diversity using MATTR*. <https://doi.org/10.1016/j.rmal.2024.100168>
- Salton, G.; Wong, A.; Yang, C. S. (1975). *A vector space model for automatic indexing*. <https://doi.org/10.1145/361219.361220>
- Lin, J. (1991). *Divergence measures based on the Shannon entropy*. <https://doi.org/10.1109/18.61115>
- Hearst, M. (1997). *TextTiling*. <https://aclanthology.org/J97-1003/>
- Hayes, A.; Krippendorff, K. (2007). *Answering the Call for a Standard Reliability Measure for Coding Data*. <https://doi.org/10.1080/19312450709336664>
