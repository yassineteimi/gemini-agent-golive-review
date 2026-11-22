# What is simulated

Phase 0 runs on a laptop and in GitHub Actions with no Google Cloud credentials. Nothing here has been run against Gemini yet. This page lists what stands in for the real thing, and each item carries the same label where it appears in the repository.

| What | Stands in for | Why | Real from |
|---|---|---|---|
| Stub model, built on ADK's own model interface, returning canned answers | Gemini on Gemini Enterprise Agent Platform | Tests run offline, cost nothing and give the same answer every time | Not planned before phase 2 |
| Gemini configuration (`GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION`, model ID) | A live call to `gemini-3.8-flash` on the `eu` endpoint | Configured and checked in tests, never called: phase 0 spends nothing | Not planned before phase 2 |
| Banque Ardoise and its four or five documents in `data/` | A real bank's policies and customer documents | Banque Ardoise is invented; no client, employer or personal data goes in this repository | Never: the bank stays fictional |
| Every user sees every document | Per-user access through OIDC sign-in and an MCP server | Identity and connectors come later | Phase 1 |
| No residency pinning, no audit trail, no guardrails | `europe-west9` or EU-only processing, audit logs, policy checks | See [findings](findings.md): several services aren't in `europe-west9` | Phase 2 |

The feasibility scorecard and ADR 0001 are drafts written from documentation and the stub runs. Where they say something about Gemini's behaviour, they cite a source, because no live result exists yet.
