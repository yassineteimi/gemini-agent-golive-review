# Run it locally

!!! warning "Work in progress, phase 0 of 4. Not yet run against Gemini."
    Everything on this page runs offline against the stub model. No Google Cloud account, no credentials, no cost.

## What you need

- Python 3.11 or newer
- [uv](https://docs.astral.sh/uv/), which installs the locked dependencies
- `make`

The tests block every outgoing network connection, so they also prove the agent makes no call to Google Cloud. You don't need a `.env` file: the default model mode is the stub. `.env.example` shows the Gemini settings that phase 0 configures and never uses.

## Install, test, lint

```{ .sh .terminal }
$ git clone https://github.com/yassineteimi/gemini-agent-golive-review.git
$ cd gemini-agent-golive-review
$ make install
$ make test
$ make lint
```

`make install` runs `uv sync --locked`, which installs exactly what `uv.lock` pins: `google-adk` 2.15.0 and `google-genai` 2.34.0, plus pytest and ruff for development.

```text title="make test, on macOS with uv 0.13.9 and Python 3.11.18"
collected 33 items

tests/test_agent.py .....                                                [ 15%]
tests/test_config.py .........                                           [ 42%]
tests/test_endpoint.py ........                                          [ 66%]
tests/test_tools.py ...........                                          [100%]

============================== 33 passed in 2.37s ==============================
```

```text title="make lint"
uv run ruff check .
All checks passed!
uv run ruff format --check .
25 files already formatted
```

GitHub Actions runs the same `make lint` and `make test` on Python 3.11 and 3.14 on every push.

## Chat with the agent

```{ .sh .terminal }
$ make run
```

This starts `adk run agent`, ADK's terminal chat, on the stub model. Type a question about one of the four documents in `data/` and press Enter; press Ctrl+C to quit. Ask in the document's language: the search matches words, so an English question won't find a French procedure.

## Sample output (simulated)

!!! note "This is the stub model, not Gemini"
    The stub doesn't write an answer. It quotes the passage that best matches the question and lists up to three documents that share at least one keyword with it, which is why a weaker second source shows up in both examples below. A real model would phrase the answer itself and cite only the documents it used.

    The search behind it is plain keyword matching: lowercase, accents stripped, crude plural folding, no meaning. Four sentences in two documents in `data/` were reworded so that the passage holding the figure ranks first for the 14 test questions in [`tests/smoke/questions.json`](https://github.com/yassineteimi/gemini-agent-golive-review/blob/main/tests/smoke/questions.json), which `make smoke` runs. That's tuning the documents to a simple matcher, and it says nothing about how Gemini would rank them.

```text
--- EN ---
[user]: How quickly are accounts disabled when an employee leaves?
[banque_ardoise_assistant]: - **Leaving.** Human Resources triggers the departure in the HR system and every account is disabled within 4 hours of the end of the last working day. For a dismissal, accounts are disabled before the employee is told.

Sources: internal-access-policy.md, card-dispute-procedure.md
--- FR ---
[user]: Quel est le délai pour envoyer l'accusé de réception d'une réclamation ?
[banque_ardoise_assistant]: | Étape | Délai maximum |
| Accusé de réception au client | 10 jours ouvrés après la réception |

Sources: procedure-reclamations.md, politique-conservation-donnees.md
```

The French answer is a table row returned with its header, so it reads as raw Markdown here. [What is simulated](simulated.md) lists the stub and the other stand-ins, and the phase that replaces each one.
