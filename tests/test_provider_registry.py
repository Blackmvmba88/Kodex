import pytest

from agent.providers.registry import available_providers, get_provider


def test_provider_registry_lists_core_providers():
    assert available_providers() == ["noop", "ollama", "openai"]


def test_provider_registry_returns_noop_provider():
    provider = get_provider("noop")
    assert provider.name == "noop"


def test_provider_registry_rejects_unknown_provider():
    with pytest.raises(ValueError):
        get_provider("missing")
