# What is simulated

Phase 0 runs on a laptop and in GitHub Actions with no Google Cloud credentials. Nothing here has been run against Gemini yet. This page lists what stands in for the real thing, and each item carries the same label where it appears in the repository.

| What | Stands in for | Why | Real from |
|---|---|---|---|
| Stub model, built on ADK's own model interface, that quotes the best-matching passage instead of writing an answer | Gemini on Gemini Enterprise Agent Platform | Tests run offline, cost nothing and give the same answer every time | Not planned before phase 2 |
| Gemini configuration (`GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION`, model ID) | A live call to `gemini-3.8-flash` on the `eu` endpoint | Configured and checked in tests, never called: phase 0 spends nothing | Not planned before phase 2 |
| Banque Ardoise and its four documents in `data/` | A real bank's policies and customer documents | Banque Ardoise is invented; no client, employer or personal data goes in this repository | Never: the bank stays fictional |
| Every user sees every document | Per-user access through OIDC sign-in and an MCP server | Identity and connectors come later | Phase 1 |
| No residency pinning, no audit trail, no guardrails | `europe-west9` or EU-only processing, audit logs, policy checks | See [findings](findings.md): several services aren't in `europe-west9` | Phase 2 |

## How the stub finds an answer

The stub doesn't write answers. It calls the agent's `search_documents` tool, which does plain keyword matching over `data/`. It then quotes the best-matching passage (a paragraph, a list item, or a table row with its header) and lists up to three documents that share any keyword with the question. A real model would phrase the answer and cite only what it used.

A set of 14 test questions, in [`tests/smoke/questions.json`](https://github.com/yassineteimi/gemini-agent-golive-review/blob/main/tests/smoke/questions.json), gives the expected document and figures for each. A question passes when the stub agent cites the right document first and every expected figure appears in its answer. `make smoke` runs them, and CI runs them on every push:

| Step | Passed |
|---|---|
| First version of `data/`, first matcher | 8 of 14 |
| Matcher scores list items and table rows as separate passages | 11 of 14 |
| Four sentences in two documents reworded so the figure sits next to the words people search for | 14 of 14 |

The rewording changed `data/`, not the matcher, and no question has special handling. One answer is still partial. Asked for the deadline on a payment-service complaint, the stub returns the 15-business-day row and leaves out the 35-day exception in the next row, because it quotes one table row at a time. Keyword search on fictional documents written by the same team is an easy test. The scorecard's answer-quality row only moves once Gemini runs the same questions.

The feasibility scorecard and ADR 0001 are drafts written from documentation and the stub runs. Where they say something about Gemini's behaviour, they cite a source, because no live result exists yet.
