from agent.providers.registry import available_providers, get_provider


def test_registry_exposes_builtin_providers():
    assert available_providers() == ["noop", "ollama", "openai"]
    assert get_provider(" NOOP ").name == "noop"


def test_registry_rejects_unknown_provider():
    try:
        get_provider("missing")
    except ValueError as exc:
        message = str(exc)
        assert "unknown provider" in message
        assert "noop" in message
    else:
        raise AssertionError("expected ValueError")
