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


def _snippet(text: str, terms: set[str]) -> str:
    """The first body paragraph that shares a term with the query."""
    best, best_score = "", 0
    for paragraph in (p.strip() for p in text.split("\n\n")):
        if not paragraph or paragraph.startswith(("#", ">")):
            continue
        score = len(_terms(paragraph) & terms)
        if score > best_score:
            best, best_score = paragraph, score
    return best[:SNIPPET_CHARS]


def search_documents(query: str) -> dict:
    """Searches Banque Ardoise's internal documents for passages about the query.

    Args:
        query: The staff member's question or the keywords to look for.

    Returns:
        A dict with `matches`, a list of {document, score, snippet}, best first.
    """
    terms = _terms(query)
    root = docs_dir()
    matches = []
    if terms and root.is_dir():
        for path in sorted(root.glob("*.md")):
            text = path.read_text(encoding="utf-8")
            score = len(terms & _terms(text))
            if score:
                matches.append(
                    {"document": path.name, "score": score, "snippet": _snippet(text, terms)}
                )
    matches.sort(key=lambda m: (-m["score"], m["document"]))
    return {"query": query, "matches": matches[:MAX_RESULTS]}
