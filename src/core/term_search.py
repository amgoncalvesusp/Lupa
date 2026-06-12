"""Term and phrase search engine for analytical corpus."""

import regex
import unicodedata
from typing import Dict, List, Tuple


# A category line looks like  NOME DA CATEGORIA: termo1, termo2, "frase exata"
# The name must not contain quotes or commas (so quoted phrases with colons are
# still treated as plain terms).
CATEGORY_LINE = regex.compile(r'^(?P<name>[^:"\',]+):(?P<members>.+)$')

# (category name, [(term, exact_match), ...])
Category = Tuple[str, List[Tuple[str, bool]]]


def _parse_single_term(token: str) -> Tuple[str, bool]:
    m = regex.match(r'^"(.+)"$|^\'(.+)\'$', token)
    if m:
        return ((m.group(1) or m.group(2)).strip(), True)
    return (token, False)


def parse_terms(raw_input: str) -> List[Tuple[str, bool]]:
    """
    Parse user input into list of (term, exact_match) tuples.

    Rules:
    - One term per line
    - Lines starting with # are ignored (comments)
    - Quotes around a term mark exact phrase match
    - Category lines (NOME: t1, t2) are handled by parse_categories, not here
    """
    terms = []
    for line in raw_input.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or CATEGORY_LINE.match(line):
            continue
        terms.append(_parse_single_term(line))
    return terms


def parse_categories(raw_input: str) -> List[Category]:
    """Parse category lines: ``NOME: termo1, termo2, "frase exata"``.

    The counts of all member terms are summed into one figure per category
    (Bardin's coding categories). Member terms follow the same quoting rules
    as plain term lines.
    """
    categories: List[Category] = []
    for line in raw_input.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        m = CATEGORY_LINE.match(line)
        if not m:
            continue
        name = m.group("name").strip()
        members = [
            _parse_single_term(tok.strip())
            for tok in m.group("members").split(",")
            if tok.strip()
        ]
        if name and members:
            categories.append((name, members))
    return categories


def parse_input(raw_input: str) -> Tuple[List[Tuple[str, bool]], List[Category]]:
    """Split the search box into plain terms and coding categories."""
    return parse_terms(raw_input), parse_categories(raw_input)


def normalize(text: str, strip_accents: bool = True) -> str:
    """Lowercase + optional accent removal."""
    text = text.lower()
    if strip_accents:
        text = "".join(
            c
            for c in unicodedata.normalize("NFD", text)
            if unicodedata.category(c) != "Mn"
        )
    return text


def count_term(
    text: str, term: str, exact: bool = False, strip_accents: bool = True
) -> int:
    """Count occurrences of term in text with word boundaries."""
    if not text or not term:
        return 0

    norm_text = normalize(text, strip_accents)
    norm_term = normalize(term, strip_accents)

    if exact:
        pattern = r"\b" + regex.escape(norm_term) + r"\b"
    else:
        words = norm_term.split()
        pattern = r"\b" + r"\s+".join(regex.escape(w) for w in words) + r"\b"

    return len(regex.findall(pattern, norm_text, regex.IGNORECASE))


def search_all_terms(
    pages_text: List[str],
    terms: List[Tuple[str, bool]],
    analytical_pages: List[int] = None,
) -> Dict[str, Dict]:
    """Search for all terms across pages, returning total and analytical counts."""
    results = {}
    analytical_set = set(analytical_pages) if analytical_pages is not None else None

    for term, exact in terms:
        label = f'"{term}"' if exact else term
        total_count = 0
        analytical_count = 0
        for i, page_text in enumerate(pages_text):
            c = count_term(page_text, term, exact=exact)
            total_count += c
            if analytical_set is None or (i + 1) in analytical_set:
                analytical_count += c
        results[label] = {
            "total": total_count,
            "analytical": analytical_count,
            "exact": exact,
            "term": term,
        }
    return results
