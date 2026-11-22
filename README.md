# Go-live review of an AI agent for a regulated French bank

> **Work in progress, phase 0 of 4. Not yet run against Gemini.**

Banque Ardoise is a fictional regulated French bank that wants an AI agent to answer staff questions from its internal documents. This repository follows the agent from technical evaluation to a go-live decision: whether the use case can go live at all, how the agent plugs into the bank's identity, connectors and data residency rules, what the Forward Deployed Engineering team would need to build, and which bugs and workarounds come up along the way. The agent uses Google's Agent Development Kit (ADK) on Gemini Enterprise Agent Platform.

The first check already changed the plan: no current Gemini model, agent runtime or session store runs in `europe-west9` (Paris). The details and sources are in [docs/findings.md](docs/findings.md), and [docs/simulated.md](docs/simulated.md) lists what phase 0 simulates.

More soon.
