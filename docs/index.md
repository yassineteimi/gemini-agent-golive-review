# Gemini agent go-live review: Banque Ardoise

!!! warning "Work in progress, phase 0 of 4. Not yet run against Gemini."
    Everything on this site comes from documentation, source code at pinned versions and offline runs against a stub model. [What is simulated](simulated.md) lists each stand-in.

Banque Ardoise is a fictional regulated French bank. Its staff want an AI agent that answers their questions from internal procedures: how to handle a disputed card payment, how long a complaint file is kept, who may read which documents. This project takes that request the way a customer engineer would on a real deal, from the technical evaluation to a go-live decision, and writes down what holds up and what doesn't.

The agent uses Google's Agent Development Kit (ADK) on Gemini Enterprise Agent Platform, the product formerly called Vertex AI.

## What changed the plan already

The brief said "everything in Paris". The first check, before any code, found that no current Gemini model, agent runtime or session store runs in `europe-west9`, and that the one Gemini model that processed data inside France retired on 20 October 2026. The target design therefore uses the `eu` multi-region, which keeps processing inside the EU, and treats Paris residency as an open question for phase 2. The sources are in [Findings](findings.md), F3 to F6.

## Read next

| Page | What it answers |
|---|---|
| [Run it locally](run-locally.md) | How to install, test and chat with the agent offline, and what the stub's answers look like |
| [Architecture](architecture.md) | What phase 0 builds, what later phases add, and where each part runs |
| [Feasibility scorecard](feasibility-scorecard.md) | The questions a bank asks before go-live, and how and when this project tests each one |
| [ADR 0001](adr/0001-adk-first-langgraph-later.md) | Why ADK first and a LangGraph orchestrator later, with the frameworks left out |
| [Findings](findings.md) | Every gap between the plan, the docs and the product, each with its source |
| [What is simulated](simulated.md) | The stub model, the fictional documents and the rest of what phase 0 fakes |

## Roadmap

| Phase | Adds | Status |
|---|---|---|
| 0 | ADK agent answering from four fictional documents, Gemini configured for the `eu` endpoint but not called, offline tests in CI, scorecard draft, ADR 0001, this site | In progress |
| 1 | Sign-in through Keycloak (OIDC); each user sees only their own documents through an MCP server; several ADK agents with routing | Planned |
| 2 | Each service pinned to `europe-west9` or to the nearest EU option, with a written finding where Paris isn't offered; audit trail; guardrails | Planned |
| 3 | Orchestrator rebuilt in LangGraph, talking to the ADK agents over A2A | Planned |
| 4 | Go-live write-up: integration design, engagement request for the Forward Deployed Engineering team, bug and workaround log | Planned |

## The sample documents

The agent reads four short documents in [`data/`](https://github.com/yassineteimi/gemini-agent-golive-review/tree/main/data), two in English and two in French, each marked as fictional on its first line: a card dispute procedure, a data retention policy, a complaints procedure and an internal access policy.

Source code, tests and history: [github.com/yassineteimi/gemini-agent-golive-review](https://github.com/yassineteimi/gemini-agent-golive-review).
