"""Pins the endpoint behaviour behind findings F2 and F3 to the locked SDK versions.

Every client here is built offline: with a project set, google-genai neither looks up
credentials nor opens a connection at construction time, and the autouse `no_network`
fixture would fail the test if it did. Nothing here sends a request to Gemini.
"""

import warnings

import pytest
from google.adk.utils.env_utils import is_enterprise_mode_enabled
from google.genai import Client

from agent.agent import build_agent
from agent.config import Settings

EU_REP = "https://aiplatform.eu.rep.googleapis.com/"


def base_url(client: Client) -> str:
    return client._api_client.get_read_only_http_options()["base_url"]


def test_network_guard_is_active():
    import socket

    with pytest.raises(RuntimeError, match="must not open network connections"):
        socket.create_connection(("aiplatform.eu.rep.googleapis.com", 443))


def test_eu_resolves_to_the_eu_multi_region_rep_endpoint_by_itself():
    client = Client(enterprise=True, project="test-project", location="eu")
    assert client.vertexai is True
    assert base_url(client) == EU_REP


def test_paris_builds_a_url_without_any_check():
    # F3: no current Gemini model is served there, but the SDK doesn't know that.
    client = Client(enterprise=True, project="test-project", location="europe-west9")
    assert base_url(client) == "https://europe-west9-aiplatform.googleapis.com/"


def test_enterprise_env_var_selects_the_enterprise_backend(monkeypatch):
    monkeypatch.setenv("GOOGLE_GENAI_USE_ENTERPRISE", "1")
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "test-project")
    monkeypatch.setenv("GOOGLE_CLOUD_LOCATION", "eu")
    client = Client()
    assert client.vertexai is True
    assert base_url(client) == EU_REP


def test_enterprise_env_var_wins_over_the_legacy_vertexai_var(monkeypatch):
    monkeypatch.setenv("GOOGLE_GENAI_USE_ENTERPRISE", "false")
    monkeypatch.setenv("GOOGLE_GENAI_USE_VERTEXAI", "true")
    monkeypatch.setenv("GOOGLE_API_KEY", "not-a-real-key")
    with pytest.warns(UserWarning, match="GOOGLE_GENAI_USE_ENTERPRISE will be used"):
        client = Client()
    assert client.vertexai is False


def test_legacy_vertexai_var_still_works_but_adk_flags_it_deprecated(monkeypatch):
    monkeypatch.setenv("GOOGLE_GENAI_USE_VERTEXAI", "true")
    with pytest.warns(DeprecationWarning, match="GOOGLE_GENAI_USE_ENTERPRISE"):
        assert is_enterprise_mode_enabled() is True


def test_adk_enterprise_var_is_read_without_a_warning(monkeypatch):
    monkeypatch.setenv("GOOGLE_GENAI_USE_ENTERPRISE", "1")
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        assert is_enterprise_mode_enabled() is True


async def test_agent_in_gemini_mode_is_configured_for_eu_and_never_called():
    agent = build_agent(Settings(mode="gemini", project="test-project"))
    client = agent.model.api_client  # built, not used: no request is sent
    assert agent.model.model == "gemini-3.8-flash"
    assert client.vertexai is True
    assert base_url(client) == EU_REP
