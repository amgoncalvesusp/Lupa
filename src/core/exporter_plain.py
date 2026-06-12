"""Plain CSV and JSON exports for interoperability with research tools."""

import csv
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from .analysis import ColumnSpec
from .exporter import _infer_column_specs
from .methodology_report import build_methodology_report, render_methodology_text

APP_VERSION = "1.0"


def export_to_csv(
    results: List[Dict],
    output_dir: str | Path,
    column_specs: Optional[List[ColumnSpec]] = None,
    methodology_options: Optional[Dict] = None,
) -> None:
    """Write the main result table and available detail tables as CSV files."""
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    if column_specs is None:
        column_specs = _infer_column_specs(results)

    _write_csv(
        out_dir / "resultados.csv",
        [spec.label for spec in column_specs],
        _main_rows(results, column_specs),
    )
    _write_csv_if_rows(
        out_dir / "sentencas.csv",
        ["Nº Doc.", "Arquivo", "Página", "Sentença", "Compound", "Classe"],
        _sentiment_rows(results),
    )
    _write_csv_if_rows(
        out_dir / "palavras.csv",
        ["Nº Doc.", "Arquivo", "Palavra", "Frequência"],
        _keyword_rows(results),
    )
    _write_csv_if_rows(
        out_dir / "ngramas.csv",
        ["Nº Doc.", "Arquivo", "Expressão", "N", "Frequência"],
        _ngram_rows(results),
    )
    _write_csv_if_rows(
        out_dir / "categorias.csv",
        ["Nº Doc.", "Arquivo", "Categoria", "Termo", "PDF Completo", "Corpus Analítico"],
        _category_rows(results),
    )
    _write_csv_if_rows(
        out_dir / "kwic.csv",
        [
            "Nº Doc.",
            "Arquivo",
            "Página",
            "Termo",
            "Contexto à esquerda",
            "Ocorrência",
            "Contexto à direita",
        ],
        _kwic_rows(results),
    )
    _write_csv_if_rows(
        out_dir / "emocoes.csv",
        ["Nº Doc.", "Arquivo", "Emoção", "Palavra", "Contagem"],
        _emotion_rows(results),
    )
    _write_csv_if_rows(
        out_dir / "territorio.csv",
        ["Nº Doc.", "Arquivo", "Local", "Tipo", "UF", "Contagem"],
        _geography_rows(results),
    )
    _write_csv_if_rows(
        out_dir / "coocorrencia.csv",
        ["Nº Doc.", "Arquivo", "Termo A", "Termo B", "Sentenças"],
        _cooccurrence_rows(results),
    )
    _write_csv_if_rows(
        out_dir / "paginas_excluidas.csv",
        ["Nº Doc.", "Arquivo", "Página", "Motivo da Exclusão", "Palavras na Página"],
        _excluded_rows(results),
    )
    report = build_methodology_report(results, methodology_options)
    (out_dir / "metodologia.txt").write_text(
        render_methodology_text(report),
        encoding="utf-8",
    )


def export_to_json(
    results: List[Dict],
    output_path: str | Path,
    methodology_options: Optional[Dict] = None,
) -> None:
    """Write a single JSON file with complete public result dictionaries."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "gerado_por": f"Lupa {APP_VERSION}",
        "metodologia": build_methodology_report(results, methodology_options),
        "documentos": [_remove_internal_keys(result) for result in results],
    }
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _main_rows(results: List[Dict], column_specs: List[ColumnSpec]) -> Iterable[List[Any]]:
    for doc_idx, result in enumerate(results, start=1):
        enriched = {"doc_id": doc_idx, **result}
        yield [enriched.get(spec.key, "") for spec in column_specs]


def _sentiment_rows(results: List[Dict]) -> Iterable[List[Any]]:
    for doc_idx, result in enumerate(results, start=1):
        for sent in result.get("sentiment_sentences", []):
            yield [
                doc_idx,
                result.get("filename", ""),
                sent.get("page", ""),
                sent.get("text", ""),
                sent.get("compound", ""),
                sent.get("classe", ""),
            ]


def _keyword_rows(results: List[Dict]) -> Iterable[List[Any]]:
    for doc_idx, result in enumerate(results, start=1):
        for word, count in result.get("keyword_freq", []):
            yield [doc_idx, result.get("filename", ""), word, count]


def _ngram_rows(results: List[Dict]) -> Iterable[List[Any]]:
    for doc_idx, result in enumerate(results, start=1):
        for phrase, n, count in result.get("ngram_freq", []):
            yield [doc_idx, result.get("filename", ""), phrase, n, count]


def _category_rows(results: List[Dict]) -> Iterable[List[Any]]:
    for doc_idx, result in enumerate(results, start=1):
        for name, data in result.get("category_results", {}).items():
            yield [
                doc_idx,
                result.get("filename", ""),
                name,
                "(total da categoria)",
                data.get("total", ""),
                data.get("analytical", ""),
            ]
            for label, counts in data.get("members", {}).items():
                yield [
                    doc_idx,
                    result.get("filename", ""),
                    name,
                    label,
                    counts.get("total", ""),
                    counts.get("analytical", ""),
                ]


def _kwic_rows(results: List[Dict]) -> Iterable[List[Any]]:
    for doc_idx, result in enumerate(results, start=1):
        for line in result.get("kwic", []):
            yield [
                doc_idx,
                result.get("filename", ""),
                line.get("page", ""),
                line.get("term", ""),
                line.get("left", ""),
                line.get("keyword", ""),
                line.get("right", ""),
            ]


def _excluded_rows(results: List[Dict]) -> Iterable[List[Any]]:
    for doc_idx, result in enumerate(results, start=1):
        for page in result.get("excluded_pages", []):
            yield [
                doc_idx,
                result.get("filename", ""),
                page.get("page_number", ""),
                page.get("exclusion_reason", ""),
                page.get("word_count", ""),
            ]


def _emotion_rows(results: List[Dict]) -> Iterable[List[Any]]:
    for doc_idx, result in enumerate(results, start=1):
        for emotion, words in result.get("emotion_words", {}).items():
            for word, count in words:
                yield [doc_idx, result.get("filename", ""), emotion, word, count]


def _geography_rows(results: List[Dict]) -> Iterable[List[Any]]:
    for doc_idx, result in enumerate(results, start=1):
        for name, place_type, uf, count in result.get("geo_mentions", []):
            yield [doc_idx, result.get("filename", ""), name, place_type, uf, count]


def _cooccurrence_rows(results: List[Dict]) -> Iterable[List[Any]]:
    for doc_idx, result in enumerate(results, start=1):
        for term_a, term_b, count in result.get("cooccurrence", []):
            yield [doc_idx, result.get("filename", ""), term_a, term_b, count]


def _write_csv_if_rows(path: Path, headers: List[str], rows: Iterable[List[Any]]) -> None:
    materialized = list(rows)
    if materialized:
        _write_csv(path, headers, materialized)


def _write_csv(path: Path, headers: List[str], rows: Iterable[List[Any]]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.writer(fh, delimiter=";", lineterminator="\n")
        writer.writerow(headers)
        writer.writerows(rows)


def _remove_internal_keys(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: _remove_internal_keys(item)
            for key, item in value.items()
            if not str(key).startswith("_")
        }
    if isinstance(value, list):
        return [_remove_internal_keys(item) for item in value]
    if isinstance(value, tuple):
        return [_remove_internal_keys(item) for item in value]
    return value
