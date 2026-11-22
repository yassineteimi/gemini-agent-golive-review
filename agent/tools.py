"""Document search tool.

SIMULATED: every user sees every document. Per-user access through OIDC and an
MCP server comes in phase 1 (docs/simulated.md).
"""

from __future__ import annotations

import os
import re
import unicodedata
from pathlib import Path

DOCS_DIR_ENV = "BANQUE_DOCS_DIR"
DEFAULT_DOCS_DIR = Path(__file__).resolve().parent.parent / "data"
MAX_RESULTS = 3
SNIPPET_CHARS = 400

_WORD = re.compile(r"[a-z0-9]+")
_LIST_ITEM = re.compile(r"^(?:[-*+]|\d+[.)])\s")
_TABLE_RULE = re.compile(r"^\|?[\s:|-]+\|?$")
# Filler words in English and French that would match every document.
_STOPWORDS = {
    "the", "and", "for", "what", "how", "can", "does", "with", "are", "our", "who",
    "which", "when", "long", "many", "much", "have", "this", "that", "from",
    "les", "des", "est", "une", "que", "qui", "pour", "dans", "sur", "par", "avec",
    "quel", "quelle", "quels", "quelles", "combien", "faut", "doit", "nous", "vous",
}  # fmt: skip


def docs_dir() -> Path:
    return Path(os.environ.get(DOCS_DIR_ENV) or DEFAULT_DOCS_DIR)


def _fold(text: str) -> str:
    """Lowercase and strip accents, so `réclamation` matches `reclamation`."""
    decomposed = unicodedata.normalize("NFKD", text.lower())
    return "".join(c for c in decomposed if not unicodedata.combining(c))


def _terms(text: str) -> set[str]:
    terms = set()
    for word in _WORD.findall(_fold(text)):
        if len(word) <= 2 or word in _STOPWORDS:
            continue
        # Crude plural folding, good enough for keyword search in EN and FR.
        terms.add(word[:-1] if len(word) > 4 and word[-1] in "sx" else word)
    return terms


def _passages(text: str) -> list[str]:
    """Splits a Markdown document into answerable passages.

    A plain paragraph is one passage. Each list item is its own passage, and each table
    row is a passage prefixed with the table's header row, so a figure in the fifth row
    of a table or the third step of a procedure isn't lost in a long block. Headings and
    blockquotes (the fictional-document notice) are left out.
    """
    passages = []
    for block in (b.strip() for b in text.split("\n\n")):
        if not block or block.startswith(("#", ">")):
            continue
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        if lines[0].startswith("|"):
            header, rows = lines[0], [r for r in lines[1:] if not _TABLE_RULE.match(r)]
            passages.extend(f"{header}\n{row}" for row in rows) if rows else passages.append(header)
        elif any(_LIST_ITEM.match(line) for line in lines):
            for line in lines:
                if _LIST_ITEM.match(line) or not passages:
                    passages.append(line)
                else:  # a lead-in line or a wrapped continuation of the previous item
                    passages[-1] += " " + line
        else:
            passages.append(" ".join(lines))
    return passages


def _best_passage(passages: list[str], terms: set[str]) -> tuple[int, str]:
    """The passage sharing the most terms with the query, else the first one.

    The fallback covers documents that match the query only on their title or headings.
    """
    best_score, best = 0, (passages[0] if passages else "")
    for passage in passages:
        score = len(_terms(passage) & terms)
        if score > best_score:
            best_score, best = score, passage
    return best_score, best[:SNIPPET_CHARS]


def search_documents(query: str) -> dict:
    """Searches Banque Ardoise's internal documents for passages about the query.

    Args:
        query: The staff member's question or the keywords to look for.

    Returns:
        A dict with `matches`, a list of {document, score, snippet}, best first. A
        document ranks by its best passage, then by its overlap with the query overall.
    """
    terms = _terms(query)
    root = docs_dir()
    ranked = []
    if terms and root.is_dir():
        for path in sorted(root.glob("*.md")):
            text = path.read_text(encoding="utf-8")
            overall = len(terms & _terms(text))
            if overall:
                score, snippet = _best_passage(_passages(text), terms)
                ranked.append((-score, -overall, path.name, snippet))
    ranked.sort()
    matches = [
        {"document": name, "score": -score, "snippet": snippet}
        for score, _, name, snippet in ranked[:MAX_RESULTS]
    ]
    return {"query": query, "matches": matches}
