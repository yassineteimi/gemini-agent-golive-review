"""Smoke questions: the stub agent, end to end, against the real data/ documents.

Excluded from `make test` (the unit tests use tests/fixtures and don't depend on data/).
Run with `make smoke`. SMOKE_DOCS_DIR points it at another copy of the documents.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest
from google.adk.runners import InMemoryRunner
from google.genai import types

from agent.agent import build_agent
from agent.config import Settings

pytestmark = pytest.mark.smoke

REPO_DATA = Path(__file__).resolve().parents[2] / "data"
QUESTIONS = json.loads((Path(__file__).parent / "questions.json").read_text(encoding="utf-8"))[
    "questions"
]


@pytest.fixture(autouse=True)
def real_documents(monkeypatch):
    docs = Path(os.environ.get("SMOKE_DOCS_DIR") or REPO_DATA)
    if not any(docs.glob("*.md")):
        pytest.fail(f"no *.md documents in {docs}")
    monkeypatch.setenv("BANQUE_DOCS_DIR", str(docs))


async def answer(question: str) -> str:
    runner = InMemoryRunner(agent=build_agent(Settings()), app_name="smoke")
    session = await runner.session_service.create_session(app_name="smoke", user_id="staff")
    message = types.Content(role="user", parts=[types.Part(text=question)])
    events = [
        e
        async for e in runner.run_async(user_id="staff", session_id=session.id, new_message=message)
    ]
    return "".join(p.text or "" for p in events[-1].content.parts)


def first_source(text: str) -> str | None:
    for line in text.splitlines():
        if line.startswith("Sources: "):
            return line.removeprefix("Sources: ").split(", ")[0]
    return None


def test_every_question_has_the_expected_shape():
    assert [q["id"] for q in QUESTIONS] == list(range(1, len(QUESTIONS) + 1))
    for q in QUESTIONS:
        assert q["question"] and q["document"].endswith(".md") and q["figures"]


@pytest.mark.parametrize("q", QUESTIONS, ids=lambda q: f"Q{q['id']}")
async def test_question(q):
    text = await answer(q["question"])

    assert first_source(text) == q["document"], text
    for figure in q["figures"]:
        assert figure.lower() in text.lower(), f"{figure!r} missing from:\n{text}"

    if partial := q.get("partial"):
        # Known gap, kept visible: if this starts failing, the answer got more complete
        # and the `partial` entry in questions.json should go.
        assert partial["missing"].lower() not in text.lower(), partial["reason"]
