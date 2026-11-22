"""SIMULATED: a stub model that stands in for Gemini in phase 0.

Built on ADK's own model interface (BaseLlm), so the real agent loop, tool calling
and session handling run offline, at no cost, with the same answer every time.
It never calls a network service. See docs/simulated.md.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator

from google.adk.models import BaseLlm
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.genai import types

STUB_MODEL_NAME = "stub-banque-ardoise"
SEARCH_TOOL = "search_documents"
NO_QUESTION_ANSWER = "Please ask a question about Banque Ardoise's documents."
NO_MATCH_ANSWER = (
    "I could not find this in Banque Ardoise's documents, so I can't answer it. "
    "Please ask the team that owns the policy."
)


class StubModel(BaseLlm):
    """Turn 1: call search_documents with the question. Turn 2: answer from the results."""

    model: str = STUB_MODEL_NAME

    @classmethod
    def supported_models(cls) -> list[str]:
        return [STUB_MODEL_NAME]

    async def generate_content_async(
        self, llm_request: LlmRequest, stream: bool = False
    ) -> AsyncGenerator[LlmResponse, None]:
        last = llm_request.contents[-1] if llm_request.contents else None
        tool_result = _function_response(last, SEARCH_TOOL)
        if tool_result is not None:
            yield _text_response(_answer(tool_result))
            return
        question = _user_text(last)
        if not question:
            yield _text_response(NO_QUESTION_ANSWER)
            return
        call = types.FunctionCall(name=SEARCH_TOOL, args={"query": question})
        yield LlmResponse(
            content=types.Content(role="model", parts=[types.Part(function_call=call)])
        )


def _function_response(content: types.Content | None, name: str) -> dict | None:
    for part in (content.parts or []) if content else []:
        if part.function_response and part.function_response.name == name:
            return part.function_response.response or {}
    return None


def _user_text(content: types.Content | None) -> str:
    if not content or content.role != "user":
        return ""
    return " ".join(p.text for p in content.parts or [] if p.text).strip()


def _answer(result: dict) -> str:
    matches = result.get("matches") or []
    if not matches:
        return NO_MATCH_ANSWER
    sources = ", ".join(m["document"] for m in matches)
    return f"{matches[0]['snippet']}\n\nSources: {sources}"


def _text_response(text: str) -> LlmResponse:
    return LlmResponse(content=types.Content(role="model", parts=[types.Part(text=text)]))
