"""Pure, immutable data preparation for Lupa interactive charts."""

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Sequence, Tuple

from .corpus_summary import build_corpus_summary

Metadata = Tuple[Tuple[str, str], ...]


@dataclass(frozen=True)
class ChartSeries:
    name: str
    values: Tuple[float, ...]
    metadata: Tuple[Metadata, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class ChartPoint:
    label: str
    x: float
    y: float
    size: float = 1.0
    value: float = 0.0
    metadata: Metadata = field(default_factory=tuple)


@dataclass(frozen=True)
class ChartData:
    kind: str
    title: str
    labels: Tuple[str, ...] = field(default_factory=tuple)
    series: Tuple[ChartSeries, ...] = field(default_factory=tuple)
    points: Tuple[ChartPoint, ...] = field(default_factory=tuple)
    matrix: Tuple[Tuple[float, ...], ...] = field(default_factory=tuple)
    x_label: str = ""
    y_label: str = ""
    value_suffix: str = ""
    normalized: bool = False


def filter_results(
    results: Sequence[Dict], year: str = "", filename: str = ""
) -> List[Dict]:
    """Return a filtered copy of the result list."""
    return [
        result
        for result in results
        if (not year or str(result.get("year") or "s/ ano") == year)
        and (not filename or result.get("filename") == filename)
    ]


def chart_options(results: Sequence[Dict]) -> Dict[str, Tuple[str, ...]]:
    """Discover filter and metric options available in a result set."""
    years = _unique(str(r.get("year") or "s/ ano") for r in results)
    filenames = _unique(str(r.get("filename", "")) for r in results)
    terms = _unique(label for r in results for label in r.get("term_results", {}))
    categories = _unique(
        name for r in results for name in r.get("category_results", {})
    )
    territories = _unique(
        str(item[0]) for r in results for item in r.get("geo_mentions", [])
    )
    territory_types = _unique(
        str(item[1]) for r in results for item in r.get("geo_mentions", [])
    )
    emotions = _unique(
        key.removeprefix("emo_pct_")
        for r in results
        for key in r
        if key.startswith("emo_pct_")
    )
    keywords = _unique(
        str(item[0]) for r in results for item in r.get("keyword_freq", [])
    )
    return {
        "years": tuple(years),
        "filenames": tuple(filenames),
        "terms": tuple(terms),
        "categories": tuple(categories),
        "territories": tuple(territories),
        "territory_types": tuple(territory_types),
        "emotions": tuple(emotions),
        "keywords": tuple(keywords),
    }


def build_temporal_chart(
    results: Sequence[Dict],
    metrics: Sequence[Tuple[str, str, str]] = (
        ("Palavras", "base", "words_analytical"),
    ),
    normalized: bool = False,
) -> ChartData:
    """Build one or more year-level line series."""
    summary = build_corpus_summary(list(results))
    labels = tuple(summary.keys())
    series = []
    for display_name, metric_type, key in metrics:
        values = []
        metadata = []
        for year, row in summary.items():
            if metric_type == "base":
                value = _number(row.get(key))
            else:
                value = _number(row.get(metric_type, {}).get(key))
                if normalized:
                    words = _number(row.get("words_analytical"))
                    value = 1000 * value / words if words else 0.0
            values.append(round(value, 4))
            metadata.append(_meta(year=year, metric=display_name))
        series_name = (
            f"{display_name} (por mil)"
            if normalized and metric_type in {"terms", "categories"}
            else display_name
        )
        series.append(ChartSeries(series_name, tuple(values), tuple(metadata)))
    return ChartData(
        kind="line",
        title="Série temporal do corpus",
        labels=labels,
        series=tuple(series),
        x_label="Ano",
        y_label="Valor; contagens normalizadas indicadas na legenda"
        if normalized
        else "Valor",
        normalized=normalized,
    )


def build_comparison_chart(
    results: Sequence[Dict],
    metric_kind: str = "words",
    key: str = "",
    normalized: bool = False,
) -> ChartData:
    """Compare one selected metric across documents with horizontal bars."""
    labels = tuple(str(r.get("filename", "")) for r in results)
    values = []
    metadata = []
    for result in results:
        value = _comparison_value(result, metric_kind, key)
        if normalized and metric_kind in {"term", "category", "territory", "keyword"}:
            words = _number(result.get("words_analytical"))
            value = 1000 * value / words if words else 0.0
        values.append(round(value, 4))
        metadata.append(
            _meta(filename=result.get("filename", ""), year=result.get("year", ""), key=key)
        )
    display = _comparison_display(metric_kind, key)
    return ChartData(
        kind="bar",
        title=f"Comparação entre documentos - {display}",
        labels=labels,
        series=(ChartSeries(display, tuple(values), tuple(metadata)),),
        x_label="Valor por mil palavras" if normalized else "Valor",
        y_label="Documento",
        normalized=normalized,
    )


def build_sentiment_chart(
    results: Sequence[Dict], group_by: str = "document"
) -> ChartData:
    """Build positive/neutral/negative stacked percentages by document or year."""
    if group_by == "year":
        summary = build_corpus_summary(list(results))
        labels = tuple(summary.keys())
        rows = tuple(summary.values())
        values = (
            tuple(_number(row.get("sent_pct_positivo")) for row in rows),
            tuple(
                max(
                    0.0,
                    100
                    - _number(row.get("sent_pct_positivo"))
                    - _number(row.get("sent_pct_negativo")),
                )
                for row in rows
            ),
            tuple(_number(row.get("sent_pct_negativo")) for row in rows),
        )
        metadata = tuple(_meta(year=label) for label in labels)
    else:
        labels = tuple(str(r.get("filename", "")) for r in results)
        values = (
            tuple(_number(r.get("sent_pct_positivo")) for r in results),
            tuple(_number(r.get("sent_pct_neutro")) for r in results),
            tuple(_number(r.get("sent_pct_negativo")) for r in results),
        )
        metadata = tuple(
            _meta(filename=r.get("filename", ""), year=r.get("year", ""))
            for r in results
        )
    series = tuple(
        ChartSeries(name, tuple(series_values), metadata)
        for name, series_values in zip(("Positivo", "Neutro", "Negativo"), values)
    )
    return ChartData(
        kind="stacked",
        title="Distribuição de sentimento",
        labels=labels,
        series=series,
        x_label="Percentual de sentenças",
        y_label="Documento" if group_by == "document" else "Ano",
        value_suffix="%",
    )


def build_lexical_scatter(results: Sequence[Dict]) -> ChartData:
    """Build readability x lexical-diversity points sized by corpus words."""
    points = []
    for result in results:
        if result.get("leg_indice") in (None, "") or result.get("lex_ttr") in (
            None,
            "",
        ):
            continue
        points.append(
            ChartPoint(
                label=str(result.get("filename", "")),
                x=_number(result.get("leg_indice")),
                y=_number(result.get("lex_ttr")),
                size=max(1.0, _number(result.get("words_analytical"))),
                value=_number(result.get("sent_compound_medio")),
                metadata=_meta(
                    filename=result.get("filename", ""),
                    year=result.get("year", ""),
                    sentiment=result.get("sent_compound_medio", ""),
                ),
            )
        )
    return ChartData(
        kind="scatter",
        title="Legibilidade e diversidade lexical",
        points=tuple(points),
        x_label="Legibilidade Flesch-PT",
        y_label="Diversidade lexical (TTR)",
    )


def build_cooccurrence_heatmap(results: Sequence[Dict]) -> ChartData:
    """Aggregate sentence co-occurrence pairs into a symmetric heatmap."""
    totals: Dict[Tuple[str, str], float] = {}
    terms = set()
    for result in results:
        for term_a, term_b, count in result.get("cooccurrence", []):
            a, b = sorted((str(term_a), str(term_b)))
            terms.update((a, b))
            totals[(a, b)] = totals.get((a, b), 0.0) + _number(count)
    labels = tuple(sorted(terms))
    index = {label: idx for idx, label in enumerate(labels)}
    matrix = [[0.0 for _ in labels] for _ in labels]
    for (term_a, term_b), count in totals.items():
        a_idx, b_idx = index[term_a], index[term_b]
        matrix[a_idx][b_idx] = count
        matrix[b_idx][a_idx] = count
    return ChartData(
        kind="heatmap",
        title="Matriz de coocorrência por sentença",
        labels=labels,
        matrix=tuple(tuple(row) for row in matrix),
        x_label="Termo",
        y_label="Termo",
    )


def build_territory_chart(
    results: Sequence[Dict], place_type: str = "", limit: int = 20
) -> ChartData:
    """Aggregate territorial mentions into ranked horizontal bars."""
    totals: Dict[str, float] = {}
    types: Dict[str, str] = {}
    for result in results:
        for name, item_type, _uf, count in result.get("geo_mentions", []):
            if place_type and item_type != place_type:
                continue
            name = str(name)
            totals[name] = totals.get(name, 0.0) + _number(count)
            types[name] = str(item_type)
    ranked = sorted(totals.items(), key=lambda item: (-item[1], item[0]))[:limit]
    labels = tuple(name for name, _value in ranked)
    values = tuple(value for _name, value in ranked)
    metadata = tuple(_meta(place=name, type=types.get(name, "")) for name in labels)
    return ChartData(
        kind="bar",
        title="Menções territoriais",
        labels=labels,
        series=(ChartSeries("Menções", values, metadata),),
        x_label="Contagem",
        y_label="Local",
    )


def chart_to_rows(chart: ChartData) -> List[List[object]]:
    """Return exactly the values displayed by a chart as tabular rows."""
    if chart.kind in {"line", "bar", "stacked"}:
        rows: List[List[object]] = [
            ["Rótulo", *[series.name for series in chart.series]]
        ]
        for idx, label in enumerate(chart.labels):
            rows.append([label, *[series.values[idx] for series in chart.series]])
        return rows
    if chart.kind == "scatter":
        return [["Documento", "X", "Y", "Tamanho", "Valor"], *[
            [point.label, point.x, point.y, point.size, point.value]
            for point in chart.points
        ]]
    if chart.kind == "heatmap":
        return [["Termo", *chart.labels], *[
            [label, *chart.matrix[idx]] for idx, label in enumerate(chart.labels)
        ]]
    return []


def _comparison_value(result: Dict, metric_kind: str, key: str) -> float:
    if metric_kind == "words":
        return _number(result.get("words_analytical"))
    if metric_kind == "term":
        return _number(result.get("term_results", {}).get(key, {}).get("analytical"))
    if metric_kind == "category":
        return _number(
            result.get("category_results", {}).get(key, {}).get("analytical")
        )
    if metric_kind == "territory":
        return sum(
            _number(item[3])
            for item in result.get("geo_mentions", [])
            if item[0] == key
        )
    if metric_kind == "emotion":
        return _number(result.get(f"emo_pct_{key}"))
    if metric_kind == "keyword":
        return sum(
            _number(count)
            for word, count in result.get("keyword_freq", [])
            if word == key
        )
    return 0.0


def _comparison_display(metric_kind: str, key: str) -> str:
    labels = {
        "words": "Palavras do corpus",
        "term": f"Termo: {key}",
        "category": f"Categoria: {key}",
        "territory": f"Território: {key}",
        "emotion": f"Emoção: {key}",
        "keyword": f"Palavra-chave: {key}",
    }
    return labels.get(metric_kind, key or "Valor")


def _unique(values: Iterable[str]) -> List[str]:
    seen = set()
    ordered = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            ordered.append(value)
    return ordered


def _number(value) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def _meta(**values) -> Metadata:
    return tuple((key, str(value)) for key, value in values.items())
