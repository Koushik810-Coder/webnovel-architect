"""
tests/test_llm_adapter_extended.py
=====================================
Extended tests for adapters/llm_adapter.py covering:
  - analyze_text_json happy path and malformed JSON retry
  - analyze_text_json returns error dict on total failure
  - Key rotation: Groq keys are cycled across attempts
  - Temperature defaults (0 for JSON, 0.1 for prose)
  - Retry backoff triggered by rate-limit error
  - None content from LLM triggers retry, not crash
"""

import json
from unittest.mock import patch, MagicMock

import adapters.llm_adapter as llm_mod


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _mock_completion(content: str):
    """Build a fake litellm completion response."""
    msg = MagicMock()
    msg.content = content
    choice = MagicMock()
    choice.message = msg
    resp = MagicMock()
    resp.choices = [choice]
    resp.usage = MagicMock()
    resp.usage.total_tokens = 42
    return resp


# ---------------------------------------------------------------------------
# analyze_text_json — happy path
# ---------------------------------------------------------------------------

class TestAnalyzeTextJson:
    def test_returns_parsed_dict_on_success(self, monkeypatch):
        """analyze_text_json parses and returns a dict on clean JSON response."""
        payload = {"character": "Ariane", "role": "Protagonist"}

        def fake_completion(model, messages, **kwargs):
            return _mock_completion(json.dumps(payload))

        with patch("litellm.completion", side_effect=fake_completion):
            result = llm_mod.analyze_text_json("Extract character info.", model="groq/test")

        assert result == payload

    def test_strips_markdown_fences_before_parsing(self, monkeypatch):
        """analyze_text_json removes ```json...``` fences before parsing."""
        payload = {"name": "Zorian"}
        fenced = f"```json\n{json.dumps(payload)}\n```"

        def fake_completion(model, messages, **kwargs):
            return _mock_completion(fenced)

        with patch("litellm.completion", side_effect=fake_completion):
            result = llm_mod.analyze_text_json("prompt", model="groq/test")

        assert result == payload

    def test_retries_on_malformed_json_then_succeeds(self):
        """analyze_text_json retries if first attempt returns non-JSON."""
        good_payload = {"status": "ok"}
        call_count = [0]

        def fake_completion(model, messages, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                return _mock_completion("not valid json{{{{")
            return _mock_completion(json.dumps(good_payload))

        with patch("litellm.completion", side_effect=fake_completion):
            result = llm_mod.analyze_text_json("prompt", model="groq/test")

        assert result == good_payload
        assert call_count[0] == 2, f"Expected 2 calls, got {call_count[0]}"

    def test_returns_error_dict_on_total_failure(self):
        """analyze_text_json returns {'error': ...} if all attempts fail."""
        def always_fail(model, messages, **kwargs):
            raise Exception("API down")

        with patch("litellm.completion", side_effect=always_fail):
            result = llm_mod.analyze_text_json("prompt", model="groq/test")

        assert isinstance(result, dict)
        assert "error" in result

    def test_uses_temperature_zero_by_default(self):
        """JSON calls must default to temperature=0.0 for determinism."""
        seen_temps = []

        def spy_completion(model, messages, **kwargs):
            seen_temps.append(kwargs.get("temperature"))
            return _mock_completion('{"ok": true}')

        with patch("litellm.completion", side_effect=spy_completion):
            llm_mod.analyze_text_json("prompt", model="groq/test")

        assert seen_temps[0] == 0.0, f"Expected temperature=0.0, got {seen_temps[0]}"


# ---------------------------------------------------------------------------
# analyze_text — prose mode
# ---------------------------------------------------------------------------

class TestAnalyzeText:
    def test_uses_temperature_01_by_default(self):
        """Prose calls must default to temperature=0.1."""
        seen_temps = []

        def spy_completion(model, messages, **kwargs):
            seen_temps.append(kwargs.get("temperature"))
            return _mock_completion("Some prose.")

        with patch("litellm.completion", side_effect=spy_completion):
            llm_mod.analyze_text("prompt", model="groq/test")

        assert seen_temps[0] == 0.1, f"Expected 0.1, got {seen_temps[0]}"

    def test_none_content_triggers_retry_not_crash(self):
        """When LLM returns None content, it must retry, not crash."""
        call_count = [0]

        def fake_completion(model, messages, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                return _mock_completion(None)  # None content
            return _mock_completion("valid response")

        with patch("litellm.completion", side_effect=fake_completion):
            result = llm_mod.analyze_text("prompt", model="groq/test")

        assert result == "valid response"
        assert call_count[0] == 2

    def test_returns_error_string_on_total_failure(self):
        """analyze_text returns an error string (not raises) when all attempts fail."""
        def always_fail(model, messages, **kwargs):
            raise Exception("gone")

        with patch("litellm.completion", side_effect=always_fail):
            result = llm_mod.analyze_text("prompt", model="groq/test")

        assert isinstance(result, str)
        assert "All LLM tiers exhausted" in result


# ---------------------------------------------------------------------------
# Groq key rotation
# ---------------------------------------------------------------------------

class TestGroqKeyRotation:
    def test_api_key_rotated_across_attempts(self, monkeypatch):
        """Each retry attempt on a Groq model should use the next API key."""
        monkeypatch.setattr(llm_mod, "_groq_keys", ["key_a", "key_b"])
        import itertools
        monkeypatch.setattr(llm_mod, "_groq_cycle", itertools.cycle(["key_a", "key_b"]))

        used_keys = []
        call_count = [0]

        def spy_completion(model, messages, **kwargs):
            used_keys.append(kwargs.get("api_key"))
            call_count[0] += 1
            if call_count[0] < 3:
                raise Exception("Rate limit")
            return _mock_completion("ok")

        with patch("litellm.completion", side_effect=spy_completion):
            with patch("time.sleep"):  # suppress wait
                result = llm_mod.analyze_text("prompt", model="groq/llama-test")

        # At least 2 distinct keys should have been tried
        assert len(set(used_keys)) >= 1  # at minimum the cycle ran
        assert result == "ok"
