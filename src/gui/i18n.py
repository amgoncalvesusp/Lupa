"""Small UI/export localization helpers for Lupa."""

from __future__ import annotations

from dataclasses import replace
from typing import Iterable

from src.core.analysis import ColumnSpec

DEFAULT_LANGUAGE = "pt"
SUPPORTED_LANGUAGES = ("pt", "en")


LABELS_EN = {
    "Arquivo": "File",
    "Título": "Title",
    "Autores": "Authors",
    "Afiliações": "Affiliations",
    "Ano": "Year",
    "Tipo": "Type",
    "Páginas": "Pages",
    "Palavras (PDF)": "Words (PDF)",
    "Palavras (Corpus)": "Words (Corpus)",
    "Confiança": "Confidence",
    "Sentimento": "Sentiment",
    "Comp. médio": "Mean comp.",
    "Presidente": "President",
    "Nº Doc.": "Doc No.",
    "Nome do Arquivo": "File Name",
    "Grau de Confiança": "Confidence Level",
    "Observações": "Notes",
    "Total de Páginas": "Total Pages",
    "Páginas c/ Texto": "Pages w/ Text",
    "Páginas Problemáticas": "Problem Pages",
    "Páginas c/ OCR": "Pages w/ OCR",
    "Palavras (PDF Completo)": "Words (Full PDF)",
    "Palavras (Corpus Analítico)": "Words (Analytical Corpus)",
    "Documento": "Document",
    "Legibilidade (Flesch-PT)": "Readability (Flesch-PT)",
    "Legibilidade (classe)": "Readability (class)",
    "Palavras / frase": "Words / sentence",
    "Sílabas / palavra": "Syllables / word",
    "Diversidade (TTR)": "Diversity (TTR)",
    "Índice de Guiraud": "Guiraud Index",
    "Vocabulário (tipos)": "Vocabulary (types)",
    "Diversidade (MATTR)": "Diversity (MATTR)",
    "Palavras-chave (frequência)": "Keywords (frequency)",
    "Expressões recorrentes (n-gramas)": "Recurring expressions (n-grams)",
    "Menções territoriais": "Territorial mentions",
    "Emoção dominante": "Dominant emotion",
    "Sentimento (classe)": "Sentiment (class)",
    "Sentimento (composto médio)": "Sentiment (mean compound)",
    "% Sentenças Positivas": "% Positive Sentences",
    "% Sentenças Negativas": "% Negative Sentences",
    "% Sentenças Neutras": "% Neutral Sentences",
    "Nº de Sentenças": "No. of Sentences",
    "Sentimento IC95% inferior": "Sentiment 95% CI lower",
    "Sentimento IC95% superior": "Sentiment 95% CI upper",
    "Cobertura do léxico (%)": "Lexicon coverage (%)",
    "Páginas Excluídas": "Excluded Pages",
    "Contagem de Palavras": "Word Count",
    "Sentimento (Sentenças)": "Sentiment (Sentences)",
    "Frequência de Palavras": "Word Frequency",
    "Categorias": "Categories",
    "Concordância (KWIC)": "Concordance (KWIC)",
    "Emoções (Palavras)": "Emotions (Words)",
    "Menções Territoriais": "Territorial Mentions",
    "Co-ocorrência": "Co-occurrence",
    "Síntese por Ano": "Summary by Year",
    "Metodologia": "Methodology",
    "Metadados Bibliográficos": "Bibliographic Metadata",
    "Autores Consolidados": "Consolidated Authors",
    "Instituições": "Institutions",
    "Dispersão": "Dispersion",
    "Associação NPMI": "NPMI Association",
    "Similaridade": "Similarity",
    "Pares de Similaridade": "Similarity Pairs",
    "Mudança Lexical": "Lexical Change",
    "Diagnóstico Sentimento": "Sentiment Diagnostics",
    "Segmentos Temáticos": "Thematic Segments",
    "N-gramas": "N-grams",
    "TF-IDF (Termos Distintivos)": "TF-IDF (Distinctive Terms)",
    "Item": "Item",
    "Valor": "Value",
    "Página": "Page",
    "Sentença": "Sentence",
    "Classe": "Class",
    "Palavra": "Word",
    "Frequência": "Frequency",
    "Expressão": "Expression",
    "Categoria": "Category",
    "Termo": "Term",
    "PDF Completo": "Full PDF",
    "Corpus Analítico": "Analytical Corpus",
    "Contexto à esquerda": "Left context",
    "Ocorrência": "Occurrence",
    "Contexto à direita": "Right context",
    "Emoção": "Emotion",
    "Contagem": "Count",
    "Local": "Place",
    "UF": "State",
    "Termo A": "Term A",
    "Termo B": "Term B",
    "Sentenças": "Sentences",
    "Motivo da Exclusão": "Exclusion Reason",
    "Palavras na Página": "Words on Page",
    "Motivo da exclusão": "Exclusion reason",
    "Palavras na página": "Words on page",
    "Nº Docs": "No. Docs",
    "Sentimento médio": "Mean sentiment",
    "Legibilidade média": "Mean readability",
    "% positivas": "% positive",
    "% negativas": "% negative",
    "Segmento": "Segment",
    "Página inicial": "Start Page",
    "Página final": "End Page",
    "Texto": "Text",
    "Nome": "Name",
    "Documentos": "Documents",
    "Documentos fracionários": "Fractional Documents",
    "Palavras": "Words",
    "Ano inicial": "Start Year",
    "Ano final": "End Year",
    "Tipos": "Types",
    "Rótulo": "Label",
    "Tamanho": "Size",
    "Log-ratio": "Log-ratio",
    "Grupo": "Group",
    "Período": "Period",
    "Período inicial": "Start Period",
    "Período final": "End Period",
    "Divergência": "Divergence",
    "Cobertura (%)": "Coverage (%)",
}

VALUE_LABELS_EN = {
    "Alto": "High",
    "Médio": "Medium",
    "Baixo": "Low",
    "Positivo": "Positive",
    "Neutro": "Neutral",
    "Negativo": "Negative",
    "Muito fácil": "Very easy",
    "Fácil": "Easy",
    "Difícil": "Difficult",
    "Muito difícil": "Very difficult",
    "Não identificado": "Not identified",
    "revisar": "review",
    "revisado": "reviewed",
    "alegria": "joy",
    "tristeza": "sadness",
    "raiva": "anger",
    "medo": "fear",
    "confiança": "trust",
    "repulsa": "disgust",
    "surpresa": "surprise",
    "antecipação": "anticipation",
}


def normalize_language(language: str | None) -> str:
    return language if language in SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE


def label(text: object, language: str = DEFAULT_LANGUAGE) -> str:
    """Translate a display label when English is active."""
    value = str(text)
    if normalize_language(language) != "en":
        return value
    if "\n" in value:
        return "\n".join(label(part, language) for part in value.split("\n"))
    if value.startswith("% "):
        suffix = value[2:]
        if suffix[:1].isupper():
            suffix = suffix[:1].lower() + suffix[1:]
        return "% " + label(suffix, language).capitalize()
    return LABELS_EN.get(value, VALUE_LABELS_EN.get(value, value))


def value(text: object, language: str = DEFAULT_LANGUAGE) -> str:
    raw = str(text)
    if normalize_language(language) != "en":
        return raw
    return VALUE_LABELS_EN.get(raw, raw)


def column_specs(specs: Iterable[ColumnSpec], language: str = DEFAULT_LANGUAGE) -> list[ColumnSpec]:
    """Return localized copies of column specs."""
    return [replace(spec, label=label(spec.label, language)) for spec in specs]
