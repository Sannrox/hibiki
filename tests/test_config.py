import pytest

from hibiki.config import ConfigurationError, Settings


def valid_environment() -> dict[str, str]:
    return {
        "HIBIKI_TENKAI_REPOSITORY": "example/tenkai",
        "HIBIKI_BIRDCLAW_ACCOUNT": "builder",
        "HIBIKI_CHISEI_TARGET": "unix:///tmp/sekai.sock",
    }


def test_defaults_are_safe_and_credential_free() -> None:
    settings = Settings.from_environ(valid_environment())

    assert settings.namespace == "hibiki"
    assert settings.allow_live_writes is False
    assert set(settings.public_dict()) == {
        "namespace",
        "tenkai_repository",
        "birdclaw_account",
        "chisei_target",
        "allow_live_writes",
    }


@pytest.mark.parametrize("value", ["1", "true", "YES", "on"])
def test_live_write_guard_requires_an_explicit_true_value(value: str) -> None:
    environment = valid_environment() | {"HIBIKI_ALLOW_LIVE_WRITES": value}
    assert Settings.from_environ(environment).allow_live_writes is True


@pytest.mark.parametrize("value", ["1", "true", "yes"])
def test_ci_categorically_disables_live_writes(value: str) -> None:
    environment = valid_environment() | {
        "HIBIKI_ALLOW_LIVE_WRITES": "true",
        "CI": value,
    }

    assert Settings.from_environ(environment).allow_live_writes is False


@pytest.mark.parametrize(
    ("name", "value"),
    [
        ("HIBIKI_NAMESPACE", "Not Valid"),
        ("HIBIKI_TENKAI_REPOSITORY", "tenkai"),
        ("HIBIKI_BIRDCLAW_ACCOUNT", "two accounts"),
        ("HIBIKI_CHISEI_TARGET", "https://localhost:50051"),
        ("HIBIKI_ALLOW_LIVE_WRITES", "perhaps"),
    ],
)
def test_invalid_configuration_fails_closed(name: str, value: str) -> None:
    with pytest.raises(ConfigurationError):
        Settings.from_environ(valid_environment() | {name: value})
