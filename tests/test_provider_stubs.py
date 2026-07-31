from agent.providers.base import ProviderRequest
from agent.providers.ollama_provider import OllamaProvider
from agent.providers.openai_provider import OpenAIProvider


def _request() -> ProviderRequest:
    return ProviderRequest(task="Implement MVP", system="safe", context={})


def test_openai_stub_never_calls_network_without_configuration(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    result = OpenAIProvider().generate(_request())

    assert result.ok is False
    assert result.files == {}
    assert "not configured" in result.message
    assert any("no network request" in item for item in result.diagnostics)


def test_ollama_stub_requires_explicit_model(monkeypatch):
    monkeypatch.delenv("KODEX_OLLAMA_MODEL", raising=False)
    result = OllamaProvider().generate(_request())

    assert result.ok is False
    assert result.files == {}
    assert "not configured" in result.message
    assert any("no local network request" in item for item in result.diagnostics)
