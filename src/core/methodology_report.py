"""Automatic methodology report for exported Lupa analyses."""

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from src.gui import i18n

APP_VERSION = "1.0.1"

CONFIG_FILES = [
    ("src/core/data/stopwords_pt.txt", "stopwords de frequência de palavras"),
    ("src/core/data/presidents.json", "detecção opcional de presidente"),
    ("src/core/data/document_types.json", "detecção do tipo de documento"),
    ("src/core/data/gazetteer_br.json", "menções territoriais"),
    ("src/core/data/nrc_emolex_pt.txt", "emoções discretas NRC"),
]

CRITERIA = [
    "Processamento 100% offline; nenhum dado é enviado a serviços externos.",
    "PDFs são extraídos por PyMuPDF; OCR Tesseract é aplicado apenas quando habilitado e necessário.",
    "DOCX/TXT são tratados como blocos textuais aproximados; número de página equivale ao bloco.",
    "O corpus analítico exclui páginas/blocos pré-textuais por heurísticas auditáveis.",
    "Contagens de termos, categorias, KWIC e co-ocorrência são insensíveis a maiúsculas/minúsculas e acentos.",
    "Sentimento usa LeIA/VADER-PT por sentença; emoções usam léxico NRC editável quando preenchido.",
    "Metadados bibliográficos seguem precedência explícita: revisão manual, metadados embutidos, cabeçalho e nome do arquivo.",
    "DP mede dispersão; keyness usa G², log-ratio e correção Benjamini-Hochberg; coocorrência normalizada usa NPMI.",
    "Similaridade usa TF-IDF e cosseno; mudança lexical usa divergência Jensen-Shannon entre períodos consecutivos.",
    "Resultados com poucos documentos ou tokens são identificados como exploratórios e não constituem inferência causal.",
]


def build_methodology_report(
    results: List[Dict],
    options: Optional[Dict] = None,
) -> Dict:
    """Build a serializable methodology report for an exported result set."""
    options = options or {}
    return {
        "gerado_por": f"Lupa {APP_VERSION}",
        "gerado_em": options.get("generated_at") or datetime.now().isoformat(timespec="seconds"),
        "documentos": [str(r.get("filename", "")) for r in results],
        "arquivos_origem": list(options.get("arquivos", [])),
        "formatos": _formats(results, options),
        "flags": dict(options.get("flags") or _infer_flags(results)),
        "termos_raw": str(options.get("termos_raw", "")),
        "termos": _terms(results),
        "categorias": _categories(results),
        "analises": _analyses(results),
        "arquivos_configuracao": _config_files(),
        "criterios": list(CRITERIA),
    }


def render_methodology_text(report: Dict, language: str = "pt") -> str:
    """Render the methodology report as a human-readable text file."""
    if language == "en":
        return _render_methodology_text_en(report)
    lines = [
        "Relatório metodológico - Lupa",
        f"Gerado por: {report.get('gerado_por', '')}",
        f"Gerado em: {report.get('gerado_em', '')}",
        "",
        "Arquivos analisados:",
    ]
    for item in report.get("arquivos_origem") or report.get("documentos", []):
        lines.append(f"- {item}")
    lines += ["", "Flags:"]
    for key, value in report.get("flags", {}).items():
        lines.append(f"- {key}: {_yes_no(value)}")
    lines += ["", "Termos brutos:"]
    lines.append(report.get("termos_raw", "") or "(não informado)")
    lines += ["", "Termos:"]
    terms = report.get("termos", [])
    lines.extend(f"- {term}" for term in terms)
    if not terms:
        lines.append("- nenhum")
    lines += ["", "Categorias:"]
    categories = report.get("categorias", [])
    lines.extend(f"- {cat}" for cat in categories)
    if not categories:
        lines.append("- nenhuma")
    lines += ["", "Análises executadas:"]
    for analysis in report.get("analises", []):
        lines.append(f"- {analysis}")
    lines += ["", "Arquivos de configuração:"]
    for cfg in report.get("arquivos_configuracao", []):
        lines.append(f"- {cfg['arquivo']} ({cfg['uso']}): {cfg['status']}")
    lines += ["", "Critérios metodológicos:"]
    for criterion in report.get("criterios", []):
        lines.append(f"- {criterion}")
    return "\n".join(lines).rstrip() + "\n"


def flatten_methodology_rows(report: Dict, language: str = "pt") -> List[List[str]]:
    """Flatten the report into rows suitable for the XLSX methodology sheet."""
    rows = [
        ["Gerado por", report.get("gerado_por", "")],
        ["Gerado em", report.get("gerado_em", "")],
        ["Documentos", "\n".join(report.get("documentos", []))],
        ["Arquivos de origem", "\n".join(report.get("arquivos_origem", []))],
        ["Formatos", ", ".join(report.get("formatos", []))],
        ["Flags", "\n".join(f"{k}: {_yes_no(v)}" for k, v in report.get("flags", {}).items())],
        ["Termos brutos", report.get("termos_raw", "")],
        ["Termos", "\n".join(report.get("termos", []))],
        ["Categorias", "\n".join(report.get("categorias", []))],
        ["Análises", "\n".join(report.get("analises", []))],
        [
            "Arquivos de configuração",
            "\n".join(
                f"{cfg['arquivo']} ({cfg['uso']}): {cfg['status']}"
                for cfg in report.get("arquivos_configuracao", [])
            ),
        ],
        ["Critérios metodológicos", "\n".join(report.get("criterios", []))],
    ]
    if language != "en":
        return rows
    return [[i18n.label(key, language), value] for key, value in rows]


def _render_methodology_text_en(report: Dict) -> str:
    lines = [
        "Methodology report - Lupa",
        f"Generated by: {report.get('gerado_por', '')}",
        f"Generated at: {report.get('gerado_em', '')}",
        "",
        "Analyzed files:",
    ]
    for item in report.get("arquivos_origem") or report.get("documentos", []):
        lines.append(f"- {item}")
    lines += ["", "Flags:"]
    for key, value in report.get("flags", {}).items():
        lines.append(f"- {key}: {_yes_no_en(value)}")
    lines += ["", "Raw terms:"]
    lines.append(report.get("termos_raw", "") or "(not informed)")
    lines += ["", "Terms:"]
    terms = report.get("termos", [])
    lines.extend(f"- {term}" for term in terms)
    if not terms:
        lines.append("- none")
    lines += ["", "Categories:"]
    categories = report.get("categorias", [])
    lines.extend(f"- {cat}" for cat in categories)
    if not categories:
        lines.append("- none")
    lines += ["", "Analyses executed:"]
    for analysis in report.get("analises", []):
        lines.append(f"- {i18n.label(analysis, 'en')}")
    lines += ["", "Configuration files:"]
    for cfg in report.get("arquivos_configuracao", []):
        lines.append(f"- {cfg['arquivo']} ({cfg['uso']}): {cfg['status']}")
    lines += ["", "Methodological criteria:"]
    for criterion in report.get("criterios", []):
        lines.append(f"- {criterion}")
    return "\n".join(lines).rstrip() + "\n"


def _yes_no_en(value) -> str:
    if isinstance(value, bool):
        return "yes" if value else "no"
    return str(value)


def _infer_flags(results: List[Dict]) -> Dict[str, bool]:
    return {
        "ocr": any(int(r.get("ocr_pages_count") or 0) > 0 for r in results),
        "sentimento": any("sent_n_sentencas" in r for r in results),
        "emocoes": any("emo_dominante" in r for r in results),
        "presidente": any(bool(r.get("president")) for r in results),
        "metricas": any("lex_ttr" in r or "leg_indice" in r for r in results),
        "kwic": any("kwic" in r for r in results),
    }


def _terms(results: List[Dict]) -> List[str]:
    terms: List[str] = []
    for result in results:
        for label in result.get("term_results", {}):
            if label not in terms:
                terms.append(label)
    return terms


def _categories(results: List[Dict]) -> List[str]:
    categories: List[str] = []
    for result in results:
        for name in result.get("category_results", {}):
            if name not in categories:
                categories.append(name)
    return categories


def _analyses(results: List[Dict]) -> List[str]:
    checks = [
        ("Metadados documentais", lambda r: "year" in r or "document" in r),
        ("Metadados bibliográficos e autoria", lambda r: "authors" in r or "title" in r),
        ("Contagem de palavras", lambda r: "words_total" in r),
        ("Métricas textuais", lambda r: "lex_ttr" in r or "leg_indice" in r),
        ("Frequência de palavras-chave", lambda r: bool(r.get("keyword_freq"))),
        ("N-gramas", lambda r: bool(r.get("ngram_freq"))),
        ("Análise de sentimento", lambda r: "sent_n_sentencas" in r),
        ("Emoções discretas", lambda r: "emo_dominante" in r),
        ("Categorias de codificação", lambda r: bool(r.get("category_results"))),
        ("Busca de termos", lambda r: bool(r.get("term_results"))),
        ("Concordância KWIC", lambda r: "kwic" in r),
        ("Co-ocorrência de termos", lambda r: "cooccurrence" in r),
        ("Menções territoriais", lambda r: "geo_top" in r or bool(r.get("geo_mentions"))),
        ("Diversidade lexical MATTR", lambda r: "lex_mattr" in r),
        ("Segmentação por coesão lexical", lambda r: "segments" in r),
        ("Diagnóstico de cobertura e IC95% do sentimento", lambda r: "sent_ci_low" in r),
    ]
    return [label for label, predicate in checks if any(predicate(r) for r in results)]


def _formats(results: List[Dict], options: Dict) -> List[str]:
    source_files = list(options.get("arquivos", [])) or [r.get("filename", "") for r in results]
    formats = sorted({Path(str(path)).suffix.lower().lstrip(".") for path in source_files if Path(str(path)).suffix})
    return formats


def _config_files() -> List[Dict[str, str]]:
    root = Path(__file__).resolve().parents[1]
    rows = []
    for rel_path, usage in CONFIG_FILES:
        path = root.parent / rel_path if rel_path.startswith("src/") else root / rel_path
        rows.append(
            {
                "arquivo": rel_path,
                "uso": usage,
                "status": "presente" if path.exists() else "ausente",
            }
        )
    return rows


def _yes_no(value) -> str:
    if isinstance(value, bool):
        return "sim" if value else "não"
    return str(value)
