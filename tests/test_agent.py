"""End to end through ADK's runner with the stub model, fully offline."""

from google.adk.runners import InMemoryRunner
from google.genai import types

from agent import root_agent
from agent.agent import AGENT_NAME, build_agent
from agent.config import Settings
from agent.stub_model import NO_MATCH_ANSWER, StubModel


async def ask(agent, question: str) -> list:
    runner = InMemoryRunner(agent=agent, app_name="test")
    session = await runner.session_service.create_session(app_name="test", user_id="staff")
    message = types.Content(role="user", parts=[types.Part(text=question)])
    return [
        event
        async for event in runner.run_async(
            user_id="staff", session_id=session.id, new_message=message
        )
    ]


def final_text(events) -> str:
    return "".join(p.text or "" for p in events[-1].content.parts)


def test_root_agent_defaults_to_the_stub():
    assert root_agent.name == AGENT_NAME
    assert isinstance(root_agent.model, StubModel)


async def test_answer_goes_through_the_search_tool_and_cites_the_document():
    events = await ask(build_agent(Settings()), "What is the deadline to dispute a card payment?")

    calls = [c for e in events for c in e.get_function_calls()]
    assert [c.name for c in calls] == ["search_documents"]

    answer = final_text(events)
    assert "60 days" in answer
    assert "card-dispute-procedure.md" in answer


async def test_french_question_gets_a_french_source():
    events = await ask(build_agent(Settings()), "Combien de temps garde-t-on les relevés ?")
    answer = final_text(events)
    assert "10 ans" in answer
    assert "politique-conservation-donnees.md" in answer


async def test_unknown_topic_is_declined_rather_than_guessed():
    events = await ask(build_agent(Settings()), "What is the cryptocurrency staking policy?")
    assert final_text(events) == NO_MATCH_ANSWER


def test_gemini_mode_builds_a_gemini_model_with_enterprise_kwargs():
    agent = build_agent(Settings(mode="gemini", project="test-project"))
    assert type(agent.model).__name__ == "Gemini"
    assert agent.model.model == "gemini-3.8-flash"
    assert agent.model.client_kwargs == {
        "enterprise": True,
        "project": "test-project",
        "location": "eu",
    }
