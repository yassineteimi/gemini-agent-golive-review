import pytest

from agent.config import ConfigError, Settings, load_settings


def test_defaults_are_stub_on_eu_with_gemini_3_8_flash():
    settings = load_settings({})
    assert settings == Settings(
        mode="stub", model_id="gemini-3.8-flash", project=None, location="eu"
    )


def test_env_overrides():
    settings = load_settings(
        {
            "AGENT_MODEL_MODE": " Gemini ",
            "MODEL_ID": "gemini-3.5-flash",
            "GOOGLE_CLOUD_PROJECT": "ardoise-dev",
            "GOOGLE_CLOUD_LOCATION": "europe-west3",
        }
    )
    assert settings.mode == "gemini"
    assert settings.model_id == "gemini-3.5-flash"
    assert settings.project == "ardoise-dev"
    assert settings.location == "europe-west3"


@pytest.mark.parametrize("location", ["europe-west9", "EUROPE-WEST9", " europe-west9 "])
def test_paris_location_is_rejected_with_a_pointer_to_the_finding(location):
    with pytest.raises(ConfigError, match="F3"):
        load_settings({"GOOGLE_CLOUD_LOCATION": location})


def test_unknown_mode_is_rejected():
    with pytest.raises(ConfigError, match="AGENT_MODEL_MODE"):
        load_settings({"AGENT_MODEL_MODE": "live"})


def test_empty_location_is_rejected():
    with pytest.raises(ConfigError, match="GOOGLE_CLOUD_LOCATION"):
        load_settings({"GOOGLE_CLOUD_LOCATION": ""})


def test_gemini_client_kwargs_select_the_enterprise_backend():
    settings = Settings(mode="gemini", project="ardoise-dev")
    assert settings.gemini_client_kwargs() == {
        "enterprise": True,
        "project": "ardoise-dev",
        "location": "eu",
    }


def test_gemini_client_kwargs_need_a_project():
    with pytest.raises(ConfigError, match="GOOGLE_CLOUD_PROJECT"):
        Settings(mode="gemini").gemini_client_kwargs()
