# ADR 0001: ADK first, LangGraph orchestrator later, A2A between them

Status: proposed
Date: 2026-11-22. Phase: 0.

## Context

Banque Ardoise wants an agent that answers staff questions from internal procedures and, by go-live, runs on Gemini Enterprise Agent Platform inside the EU. The framework choice has to work in three situations at once: offline in CI with no credentials (phase 0), on Google's managed runtime and session store once the bank pays for them (phase 2), and next to the orchestration code a bank's own teams may already run. That last point is the one most PoCs skip, and a large bank rarely starts from an empty estate.

## Options considered

| Option | What it is | For Banque Ardoise | Against, for Banque Ardoise |
|---|---|---|---|
| A. ADK now, LangGraph orchestrator in phase 3, A2A between them | ADK agents do the work; a LangGraph graph routes between them and calls them over the A2A protocol | ADK is the only framework with full Agent Runtime integration, deployed with the `adk` CLI ([Agent Runtime](https://docs.cloud.google.com/gemini-enterprise-agent-platform/build/runtime#supported-frameworks)). ADK Python can both expose an agent over A2A and call a remote one ([ADK A2A](https://adk.dev/a2a/)). Phase 3 then shows ADK agents serving an orchestrator the bank didn't build on Google. | Two frameworks to learn, pin and patch. The A2A hop adds a network call and a second place to check authorisation. |
| B. ADK only | ADK for the agents and the routing, no second framework | Simplest to run: one dependency tree, one deployment path. | Shows nothing about working with existing orchestration, which is the integration question a bank's architects ask first. |
| C. LangGraph only | LangGraph for agents and routing, deployed to Agent Runtime through the SDK template | LangGraph has a managed template on Agent Runtime, and LangSmith's Agent Server exposes A2A at `/a2a/{assistant_id}` ([Agent Runtime](https://docs.cloud.google.com/gemini-enterprise-agent-platform/build/runtime#supported-frameworks), [LangSmith A2A](https://docs.langchain.com/langsmith/server-a2a)). | It sits one support level below ADK on Agent Runtime, and the ADK-side integrations, such as Memory Bank through `VertexAiMemoryBankService`, wouldn't apply ([Memory Bank](https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/memory-bank)). |
| D. CrewAI | Role-based multi-agent framework | Quick to prototype a team of agents. | Agent Runtime supports it only through a custom template the team adapts and maintains ([Agent Runtime](https://docs.cloud.google.com/gemini-enterprise-agent-platform/build/runtime#supported-frameworks)). That's ongoing work for the bank with no payoff in this use case. |
| E. AutoGen | Microsoft's multi-agent conversation framework | Mature conversation patterns between agents. | The repository is archived: Microsoft provides no bug fixes or security fixes and points new users to Microsoft Agent Framework ([microsoft/autogen](https://github.com/microsoft/autogen)). A regulated bank can't put an unpatched framework in production. AG2, a separate community project, has its own Agent Runtime template, but it would add a third framework for no gain here. |
| F. Gemini API with no framework | Direct calls through `google-genai`, with hand-written tool loop and state | Fewest dependencies; full control of every request. | The team would write and maintain the tool loop, session state, an A2A server, evaluation and packaging for Agent Runtime, all of which ADK already provides. It also loses ADK's model interface, which is what lets phase 0 swap in an offline stub model. |

## Decision

Option A. ADK first, because it has the deepest integration with the platform the bank is evaluating, and because its model interface lets phase 0 run the real agent code against a stub with no cloud access ([What is simulated](../simulated.md)). The LangGraph orchestrator comes in phase 3 and talks A2A, because the go-live question for a bank isn't "does ADK work" but "does it work next to what we already run".

The answer changes if Banque Ardoise has no orchestration code of its own: option B is then enough and phase 3 shrinks to a short A2A test. It also changes if Agent Runtime moves LangGraph to full integration, which would make option C competitive.

## Consequences

- The bank gets agents that deploy to Agent Runtime with the standard tooling, and an orchestrator that could be swapped for its own without touching them. It also gets two frameworks to keep current, plus the A2A endpoint to secure: the user's identity has to travel across that hop, which phase 1's identity work must allow for.
- Phase 0 pins `google-adk` 2.15.0 ([F1](../findings.md#f1-adk-release-and-python-support)). LangGraph and the A2A SDK get pinned in phase 3, at whatever is current then.
- This PoC can't show production behaviour: the model is a stub until phase 2, the data is fictional, and there's no real load. The A2A part stays unverified until phase 3 runs it.

## Evidence

- Agent Runtime, supported languages and frameworks: <https://docs.cloud.google.com/gemini-enterprise-agent-platform/build/runtime#supported-frameworks>
- ADK and A2A, Python supported, Go and Java experimental: <https://adk.dev/a2a/>
- LangSmith Agent Server A2A endpoint: <https://docs.langchain.com/langsmith/server-a2a>
- Memory Bank and ADK: <https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/memory-bank>
- AutoGen repository status: <https://github.com/microsoft/autogen>
- Pages read on 22 November 2026.
