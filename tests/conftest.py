"""Shared test setup: offline, no Google Cloud credentials, fixture documents."""

from __future__ import annotations

import socket
from pathlib import Path

import pytest

FIXTURE_DOCS = Path(__file__).parent / "fixtures" / "docs"

_GOOGLE_ENV = (
    "AGENT_MODEL_MODE",
    "MODEL_ID",
    "GOOGLE_CLOUD_PROJECT",
    "GOOGLE_CLOUD_LOCATION",
    "GOOGLE_GENAI_USE_ENTERPRISE",
    "GOOGLE_GENAI_USE_VERTEXAI",
    "GOOGLE_API_KEY",
    "GEMINI_API_KEY",
    "GOOGLE_APPLICATION_CREDENTIALS",
)


class NetworkBlocked(RuntimeError):
    pass


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    """Fail any test that tries to open a network connection."""

    def refuse(*args, **kwargs):
        raise NetworkBlocked("tests must not open network connections")

    monkeypatch.setattr(socket.socket, "connect", refuse)
    monkeypatch.setattr(socket.socket, "connect_ex", refuse)
    monkeypatch.setattr(socket, "create_connection", refuse)


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    """Start every test from a known environment, whatever the developer's shell has."""
    for name in _GOOGLE_ENV:
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("BANQUE_DOCS_DIR", str(FIXTURE_DOCS))
