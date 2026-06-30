"""Pluggable document-analysis pipeline.

Public surface:
    - Analyzer, ColumnSpec, DocumentContext  : core abstractions
    - build_default_analyzers(...)            : standard analyzer set
    - build_column_specs(...)                 : full ordered output schema
"""

from typing import List, Tuple

from .base import Analyzer, ColumnSpec, DocumentContext
from .categories import CategoryAnalyzer
from .cooccurrence import CooccurrenceAnalyzer
from .doc_stats import DocStatsAnalyzer
from .emotions import EmotionAnalyzer
from .geography import GeographyAnalyzer
from .keywords import KeywordAnalyzer
from .kwic import KwicAnalyzer
from .lexical_diversity import LexicalDiversityAnalyzer
from .metadata import MetadataAnalyzer
from .ngrams import NgramAnalyzer
from .readability import ReadabilityAnalyzer
from .sentiment import SentimentAnalyzer
from .segmentation import SegmentationAnalyzer
from .term_search import TermSearchAnalyzer
from .word_count import WordCountAnalyzer

__all__ = [
    "Analyzer",
    "CategoryAnalyzer",
    "ColumnSpec",
    "CooccurrenceAnalyzer",
    "DocumentContext",
    "DocStatsAnalyzer",
    "EmotionAnalyzer",
    "GeographyAnalyzer",
    "KeywordAnalyzer",
    "KwicAnalyzer",
    "LexicalDiversityAnalyzer",
    "MetadataAnalyzer",
    "NgramAnalyzer",
    "ReadabilityAnalyzer",
    "SentimentAnalyzer",
    "SegmentationAnalyzer",
    "TermSearchAnalyzer",
    "WordCountAnalyzer",
    "build_default_analyzers",
    "build_column_specs",
]


def build_default_analyzers(
    search_terms: List[Tuple[str, bool]] = None,
    detect_president: bool = False,
    detect_sentiment: bool = True,
    detect_emotions: bool = True,
    detect_textmetrics: bool = True,
    detect_kwic: bool = True,
    categories=None,
) -> List[Analyzer]:
    """Standard analyzer set, in output-column order."""
    analyzers: List[Analyzer] = [
        MetadataAnalyzer(detect_president=detect_president),
        DocStatsAnalyzer(),
        WordCountAnalyzer(),
    ]
    if detect_textmetrics:
        analyzers.append(ReadabilityAnalyzer())
        analyzers.append(LexicalDiversityAnalyzer())
        analyzers.append(KeywordAnalyzer())
        analyzers.append(NgramAnalyzer())
        analyzers.append(GeographyAnalyzer())
        analyzers.append(SegmentationAnalyzer())
    if detect_sentiment:
        analyzers.append(SentimentAnalyzer())
    if detect_emotions:
        analyzers.append(EmotionAnalyzer())
    if categories:
        analyzers.append(CategoryAnalyzer(categories))
    analyzers.append(TermSearchAnalyzer(search_terms or []))
    if detect_kwic:
        # Detail-only analyzers: qualitative concordance and sentence links.
        analyzers.append(KwicAnalyzer(search_terms or []))
        analyzers.append(CooccurrenceAnalyzer(search_terms or []))
    return analyzers


def build_column_specs(analyzers: List[Analyzer]) -> List[ColumnSpec]:
    """Full ordered column schema: id + filename, analyzer columns, then tail."""
    specs: List[ColumnSpec] = [
        ColumnSpec("doc_id", "Nº Doc.", 8),
        ColumnSpec("filename", "Nome do Arquivo", 35),
    ]
    for analyzer in analyzers:
        specs.extend(analyzer.columns())
    specs.append(ColumnSpec("confidence", "Grau de Confiança", 14))
    specs.append(ColumnSpec("observations", "Observações", 50))
    return specs
