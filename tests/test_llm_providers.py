import sys
import types

from llm_provider import OpenAIProvider


class _FakeCompletions:
    """Records the kwargs chat.completions.create receives, and rejects any the real SDK doesn't accept."""

    ACCEPTED = {"model", "messages", "temperature", "max_tokens"}

    def __init__(self):
        self.kwargs = None

    def create(self, **kwargs):
        unexpected = set(kwargs) - self.ACCEPTED
        if unexpected:
            raise TypeError(f"create() got unexpected keyword argument(s) {sorted(unexpected)}")
        self.kwargs = kwargs
        message = types.SimpleNamespace(content="Answer [DOC-1]")
        usage = types.SimpleNamespace(prompt_tokens=10, completion_tokens=4)
        return types.SimpleNamespace(choices=[types.SimpleNamespace(message=message)], usage=usage)


def test_openai_sends_system_prompt_as_first_message(monkeypatch):
    completions = _FakeCompletions()
    fake_client = types.SimpleNamespace(chat=types.SimpleNamespace(completions=completions))
    monkeypatch.setitem(sys.modules, "openai", types.SimpleNamespace(OpenAI=lambda api_key: fake_client))
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    answer, in_tok, out_tok, _ = OpenAIProvider().generate_answer("Q?", "ctx", "SYSTEM RULES")

    assert (answer, in_tok, out_tok) == ("Answer [DOC-1]", 10, 4)
    first, second = completions.kwargs["messages"]
    assert first == {"role": "system", "content": "SYSTEM RULES"}
    assert second["role"] == "user" and "ctx" in second["content"] and "Q?" in second["content"]
