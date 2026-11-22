"""The Banque Ardoise staff assistant, built with Google's Agent Development Kit."""

from __future__ import annotations

from google.adk.agents import LlmAgent
from google.adk.models import BaseLlm, Gemini

from .config import Settings, load_settings
from .stub_model import StubModel
from .tools import search_documents

AGENT_NAME = "banque_ardoise_assistant"
INSTRUCTION = """\
You answer Banque Ardoise staff questions using only the bank's internal documents.
Always call search_documents first. Answer from what it returns and name the documents
you used. If nothing relevant comes back, say you could not find it; never guess.
"""


def build_model(settings: Settings) -> BaseLlm:
    if settings.mode == "stub":
        return StubModel()
    # Configured, never called in phase 0 (docs/simulated.md).
    return Gemini(model=settings.model_id, client_kwargs=settings.gemini_client_kwargs())


def build_agent(settings: Settings | None = None) -> LlmAgent:
    settings = settings or load_settings()
    return LlmAgent(
        name=AGENT_NAME,
        model=build_model(settings),
        description="Answers staff questions from Banque Ardoise's internal documents.",
        instruction=INSTRUCTION,
        tools=[search_documents],
    )


root_agent = build_agent()
