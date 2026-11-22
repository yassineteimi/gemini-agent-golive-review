"""Runtime settings for the Banque Ardoise agent.

Phase 0 runs on the stub model. The Gemini settings are read and validated so the
real configuration is reviewed in tests, but phase 0 never sends a request to Gemini.
See docs/findings.md (F3, F4) for why the location is `eu` and not `europe-west9`.
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass

MODES = ("stub", "gemini")
DEFAULT_MODE = "stub"
DEFAULT_MODEL_ID = "gemini-3.8-flash"
DEFAULT_LOCATION = "eu"

# Locations with no endpoint for any current Gemini model (findings F3).
# google-genai builds a URL for these without complaint, so the check lives here.
LOCATIONS_WITHOUT_GEMINI = {
    "europe-west9": (
        "No current Gemini model has a europe-west9 (Paris) endpoint; "
        "use the `eu` multi-region instead (docs/findings.md, F3)."
    ),
}


class ConfigError(ValueError):
    """Raised when the agent settings are invalid."""


@dataclass(frozen=True)
class Settings:
    mode: str = DEFAULT_MODE
    model_id: str = DEFAULT_MODEL_ID
    project: str | None = None
    location: str = DEFAULT_LOCATION

    def __post_init__(self) -> None:
        if self.mode not in MODES:
            raise ConfigError(f"AGENT_MODEL_MODE must be one of {MODES}, got {self.mode!r}")
        if not self.model_id:
            raise ConfigError("MODEL_ID must not be empty")
        check_location(self.location)

    def gemini_client_kwargs(self) -> dict[str, object]:
        """Keyword arguments for google.genai.Client on Gemini Enterprise Agent Platform."""
        if not self.project:
            raise ConfigError("GOOGLE_CLOUD_PROJECT is required in gemini mode")
        return {"enterprise": True, "project": self.project, "location": self.location}


def check_location(location: str) -> None:
    if not location:
        raise ConfigError("GOOGLE_CLOUD_LOCATION must not be empty")
    reason = LOCATIONS_WITHOUT_GEMINI.get(location.strip().lower())
    if reason:
        raise ConfigError(reason)


def load_settings(env: Mapping[str, str] | None = None) -> Settings:
    env = os.environ if env is None else env
    return Settings(
        mode=env.get("AGENT_MODEL_MODE", DEFAULT_MODE).strip().lower(),
        model_id=env.get("MODEL_ID", DEFAULT_MODEL_ID).strip(),
        project=(env.get("GOOGLE_CLOUD_PROJECT") or "").strip() or None,
        location=env.get("GOOGLE_CLOUD_LOCATION", DEFAULT_LOCATION).strip(),
    )
