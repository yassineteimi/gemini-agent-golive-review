# Findings

Anything that didn't match the plan, an assumption, or the docs. Each finding has its source and the date I checked it. A gap goes here as it is, with no quiet workaround: the residency gaps below become the phase 2 story.

Checked on 22 November 2026. Every Google Cloud page cited here showed "Last updated 2026-11-20".

## Summary

| # | Finding | Effect on the plan |
|---|---|---|
| F1 | `google-adk` 2.15.0 is current and supports Python 3.11 to 3.15, but it caps `google-genai` below 3, so the newest SDK (3.6.1) can't be installed with it | Pin `google-adk==2.15.0`; the lock file carries `google-genai` 2.34.0 |
| F2 | Vertex AI is now called Gemini Enterprise Agent Platform; the SDK switch is `GOOGLE_GENAI_USE_ENTERPRISE`, and `GOOGLE_GENAI_USE_VERTEXAI` is deprecated | Use the new variable; `location="eu"` reaches the EU endpoint with no extra setting |
| F3 | No current Gemini model can be called on a `europe-west9` endpoint, and the SDK accepts that location without complaint | The Paris-only plan fails for the model; the `eu` multi-region is the closest option |
| F4 | Only one model ran ML processing inside France, and it was retired on 20 October 2026 | No Gemini model processes data in France today |
| F5 | Agent Runtime, Sessions, Memory Bank, Sandboxes and Agent Gateway aren't offered in `europe-west9` | The agent's state and runtime have to live in another EU region or in `eu` |
| F6 | Runtime can't use CMEK on the `eu` multi-region endpoint | The bank has to choose between in-EU processing on `eu` and its own keys in a single region |
| F7 | The docs say ADK agents take their location from `vertexai.init()`; ADK 2.15.0's Gemini model doesn't read it | Set the location through `GOOGLE_CLOUD_LOCATION` or the model's client settings |
| F8 | The ADK docs moved from `google.github.io/adk-docs` to `adk.dev` | Cite `adk.dev`; older links still redirect |

Phase 0 default for `.env.example`: model `gemini-3.8-flash`, `GOOGLE_CLOUD_LOCATION=eu`. It's GA, it's served on the `eu` multi-region with ML processing kept inside the EU, and it retires no earlier than 2 September 2027. Phase 0 never calls it.

## F1. ADK release and Python support

`google-adk` 2.15.0 is the latest release. It went up on PyPI on 20 November 2026 (00:30 UTC), and the matching GitHub release `v2.15.0` is dated 19 November 2026 at 22:59 UTC. `requires_python` is `>=3.11`, and the classifiers list 3.11, 3.12, 3.13, 3.14 and 3.15. The companion SDK `google-genai` is at 3.6.1, also `>=3.11`, but ADK 2.15.0 can't use it: its metadata declares `Requires-Dist: google-genai>=2.34,<3`. The newest release inside that range is `google-genai` 2.34.0, uploaded on 29 October 2026, so that's the version the lock file carries. The backend and endpoint code quoted under F2 is the same in 2.34.0 and 3.6.1.

- https://pypi.org/pypi/google-adk/json
- https://github.com/google/adk-python/releases/tag/v2.15.0
- https://pypi.org/pypi/google-genai/json
- https://pypi.org/pypi/google-adk/2.15.0/json (`requires_dist`)

## F2. Vertex AI renamed, and the switch that goes with it

What used to be Vertex AI generative AI now sits under Gemini Enterprise Agent Platform, and the docs live at `docs.cloud.google.com/gemini-enterprise-agent-platform/`. Agent Engine shows up as Agent Runtime.

The SDK followed the rename. Reading the source at the locked versions:

- **Backend switch.** `google-genai` reads `GOOGLE_GENAI_USE_ENTERPRISE` first and falls back to `GOOGLE_GENAI_USE_VERTEXAI`. Only `true` or `1` count. If the two disagree, the enterprise variable wins and the SDK logs a warning (`google/genai/_api_client.py`, lines 868 to 895 in 2.34.0, 1137 to 1160 in 3.6.1). `genai.Client(enterprise=...)` is the new argument and `vertexai=` the legacy one; passing both with different values raises `ValueError` (`google/genai/client.py`, lines 361 to 414). ADK applies the same order and raises a `DeprecationWarning` for the old variable (`google/adk/utils/env_utils.py`, lines 82 to 98; `google/adk/utils/_gcp_metadata.py`, lines 113 to 144).
- **EU endpoint.** `_MULTI_REGIONAL_LOCATIONS = {'us', 'eu'}` (`_api_client.py`, line 152), and a location in that set becomes `https://aiplatform.{location}.rep.googleapis.com/` (lines 1024 to 1030 in 2.34.0, 1290 to 1296 in 3.6.1). Setting `location="eu"` is enough; the agent needs no `base_url` override.

The phase 0 agent therefore sets `enterprise=True` and `location="eu"`, and an offline test asserts both behaviours against the locked versions so that CI catches a change.

- https://docs.cloud.google.com/gemini-enterprise-agent-platform/resources/locations#multi-region-endpoints
- `google-genai` 2.34.0 and 3.6.1, `google-adk` 2.15.0 source, at the lines above

## F3. Gemini models and `europe-west9`

The Paris column of the regional endpoint table lists four Gemini-family entries: `gemini-2.5-pro`, `gemini-2.5-flash`, `gemini-2.5-flash-lite` and `gemini-embedding-001`, plus the older text and multimodal embeddings and `virtual-try-on-001`. All three 2.5 models retired on 20 October 2026 (see F4), so the table is a month out of date for Paris and nothing current is left.

None of the current GA models (Gemini 4 Neon, Hydrogen, Carbon and Argon, 3.8 Flash, 3.7 Flash, 3.6 Flash, 3.5 Flash, 3.5 Flash-Lite, 3.1 Flash-Lite) has a `europe-west9` endpoint. Most of them have no single-region endpoint in Europe at all. The exceptions are `gemini-3.5-flash` (London, Frankfurt) and `gemini-4-argon` (London). What they all share is the `eu` multi-region endpoint, `https://aiplatform.eu.rep.googleapis.com`, and the global endpoint. The `eu` endpoint keeps ML processing inside EU member states, which rules out the UK and Switzerland.

The SDK doesn't warn about any of this. Any location outside `us` and `eu` becomes `https://{location}-aiplatform.googleapis.com/` with no check (`_api_client.py`, lines 1042 to 1045 in 2.34.0), so `GOOGLE_CLOUD_LOCATION=europe-west9` builds a Paris URL without error and only fails on the first real call. A bank that assumes Paris and tests offline won't find out until go-live.

- https://docs.cloud.google.com/gemini-enterprise-agent-platform/resources/locations#europe
- https://docs.cloud.google.com/gemini-enterprise-agent-platform/resources/locations#multi-region
- https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/google-models

## F4. ML processing inside France

The data residency page separates where data is stored from where the model processes it. In the France (`europe-west9`) column, Gemini has a single entry: `gemini-2.5-flash` with the 128k context. Chirp 3 HD Voices and Instant Custom Voice also process in France, but they're speech models. Every current Gemini model processes inside the EU multi-region boundary, not in France.

`gemini-2.5-flash` retired on 20 October 2026, and the model versions page names `gemini-3.8-flash` or `gemini-3.5-flash-lite` as its replacement. Neither of those processes in France.

For Banque Ardoise that means in-country processing in France isn't available for Gemini today. EU-boundary processing is. Whether the EU boundary is enough is a question for the bank's compliance team, and ADR 0004 in phase 2 takes it up.

- https://docs.cloud.google.com/gemini-enterprise-agent-platform/resources/data-residency#ml-processing-google-models
- https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/gemini/2-5-flash
- https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/model-versions

## F5. Agent services and `europe-west9`

Runtime, Sessions, Memory Bank, Sandboxes (code execution, shell, computer use, custom images) and Agent Gateway share one region list, and `europe-west9` isn't on it. In Europe it holds `europe-west1` (Belgium), `europe-west2` (London), `europe-west3` (Frankfurt), `europe-west4` (Netherlands), `europe-west6` (Zurich), `europe-west8` (Milan) and `europe-southwest1` (Madrid). Runtime, Sessions, Memory Bank and Code Execution also take the `eu` multi-region; Sessions and Memory Bank take `global` as well.

The general machine learning locations page confirms it from the other side. Its `europe-west9` entry lists custom training and inference, Vector Search, Pipelines and similar services, and no agent service.

- https://docs.cloud.google.com/gemini-enterprise-agent-platform/resources/agent-locations
- https://docs.cloud.google.com/gemini-enterprise-agent-platform/machine-learning/general/locations

## F6. CMEK and the `eu` endpoint

Runtime doesn't support CMEK on a multi-region endpoint, and Sessions and Memory Bank don't support it on `global`. A bank that needs its own keys therefore picks a single EU region for Runtime, such as `europe-west1` or `europe-west3`. A bank that wants the `eu` processing boundary for Runtime gives up CMEK there. The trade-off goes into the phase 2 residency design.

- https://docs.cloud.google.com/gemini-enterprise-agent-platform/resources/agent-locations#multi-regional_and_global_endpoints
- https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale

## F7. Where ADK takes the location from

The multi-region page says ADK agents "automatically use the location specified" through `vertexai.init()` or `vertexai.Client()`. ADK 2.15.0's Gemini model doesn't work that way. `Gemini.api_client` builds a `genai.Client` from environment variables plus the model's `client_kwargs` (`google/adk/models/google_llm.py`, lines 441 to 480), and adds `enterprise=True` by itself only for model IDs that start with `projects/` (lines 466 to 467). `get_gcp_client_defaults` fills in the project alone, from the metadata server (`google/adk/utils/_gcp_metadata.py`, lines 147 to 188). `google_llm.py` never imports `vertexai`, which ADK 2.15.0 uses only in its evaluation, code executor, RAG and telemetry modules. The location comes from `GOOGLE_CLOUD_LOCATION` or `client_kwargs={"location": ...}`. This is product feedback for the docs team.

- https://docs.cloud.google.com/gemini-enterprise-agent-platform/resources/locations#multi-region-endpoints
- `google-adk` 2.15.0 source, at the lines above

## F8. ADK docs moved

`https://google.github.io/adk-docs/` now answers with a 301 to `https://adk.dev/`. Old links still work through the redirect, but anything that pins or quotes ADK documentation (ADR 0001 cites `adk.dev/a2a/`) should use the new host.

- `curl -sIL https://google.github.io/adk-docs/` on 22 November 2026: `HTTP/2 301`, `location: https://adk.dev/`
