"""Category coding analyzer (Bardin's coding categories).

The researcher groups search terms into named categories in the search box
(``MITIGAÇÃO: clima, carbono, "efeito estufa"``). Each category's figure is the
sum of the occurrences of its member terms — turning raw term counts into the
category-level coding of content analysis (Bardin, 2011).

Counting reuses the term-search engine (accent-insensitive, word boundaries,
exact phrases), so a term counted alone and inside a category always yields the
same number.
"""

from typing import Dict, List

from .base import ColumnSpec, DocumentContext
from ..term_search import Category, search_all_terms


class CategoryAnalyzer:
    name = "categories"

    def __init__(self, categories: List[Category] = None):
        self.categories = categories or []

    def columns(self) -> List[ColumnSpec]:
        cols: List[ColumnSpec] = []
        for name, _members in self.categories:
            cols.append(ColumnSpec(f"_cat_{name}_total", f"{name}\n(PDF)", 16, "term"))
            cols.append(
                ColumnSpec(f"_cat_{name}_analytical", f"{name}\n(Corpus)", 16, "term")
            )
        return cols

    def run(self, ctx: DocumentContext) -> Dict[str, object]:
        out: Dict[str, object] = {"category_results": {}}
        for name, members in self.categories:
            results = search_all_terms(
                ctx.pages_text, members, ctx.analytical_page_numbers
            )
            total = sum(r["total"] for r in results.values())
            analytical = sum(r["analytical"] for r in results.values())
            member_counts = {
                label: {"total": r["total"], "analytical": r["analytical"]}
                for label, r in results.items()
            }
            out["category_results"][name] = {
                "total": total,
                "analytical": analytical,
                "members": member_counts,
            }
            out[f"_cat_{name}_total"] = total
            out[f"_cat_{name}_analytical"] = analytical
        return out
