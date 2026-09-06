#!/usr/bin/env python3
"""Regression tests for chat() model failover; never call external APIs."""

import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
ADR_PATH = ROOT / "run_adr_v8.py"
_OUTPUT_TMP = tempfile.TemporaryDirectory(prefix="adr_chat_fallback_test_")
_ENV_KEYS = (
    "WERYAI_API_KEY",
    "TG_BOT_TOKEN",
    "TG_CHAT_ID",
    "OUTPUT_DIR",
    "ADR_CREATIVE_MODEL",
    "ADR_JUDGMENT_MODEL",
    "ADR_VISION_MODEL",
    "ADR_CREATIVE_FALLBACK_MODELS",
    "ADR_JUDGMENT_FALLBACK_MODELS",
    "ADR_VISION_FALLBACK_MODELS",
    "ADR_CHAT_FALLBACK_MODELS",
    "ADR_CHAT_FALLBACK_MODEL",
)
_OLD_ENV = {key: os.environ.get(key) for key in _ENV_KEYS}
_TEST_ARGV = sys.argv[:]
_TEST_PATH = sys.path[:]
try:
    for _key in _ENV_KEYS[4:]:
        os.environ.pop(_key, None)
    os.environ.update({
        "WERYAI_API_KEY": "test_dummy",
        "TG_BOT_TOKEN": "test_dummy",
        "TG_CHAT_ID": "test_dummy",
        "OUTPUT_DIR": _OUTPUT_TMP.name,
    })
    sys.argv = ["test_chat_fallback.py", "chat-fallback-test", "h", "--no-motion"]
    sys.path.insert(0, str(ROOT))
    _SPEC = importlib.util.spec_from_file_location("adr_chat_fallback_under_test", ADR_PATH)
    assert _SPEC is not None and _SPEC.loader is not None
    adr = importlib.util.module_from_spec(_SPEC)
    _SPEC.loader.exec_module(adr)
finally:
    sys.argv = _TEST_ARGV
    sys.path[:] = _TEST_PATH
    for _key, _value in _OLD_ENV.items():
        if _value is None:
            os.environ.pop(_key, None)
        else:
            os.environ[_key] = _value


PRIMARY = "CLAUDE_4_8_OPUS"
FALLBACK = "GEMINI_25_FLASH"


def _ok(text="fallback ok"):
    return {"choices": [{"message": {"content": f"  {text}  "}}]}


class ChatFallbackTests(unittest.TestCase):
    def _run_chat(self, responses, *, fallback_models_env="", fallback_models_arg=None):
        calls = []
        sleeps = []
        remaining = iter(responses)

        def fake_post(path, payload, timeout):
            self.assertEqual(path, "/chat/completions")
            self.assertEqual(timeout, 123)
            calls.append(str(payload["model"]))
            response = next(remaining)
            if isinstance(response, Exception):
                raise response
            return response

        with (
            patch.dict(os.environ, {
                "ADR_CHAT_FALLBACK_MODEL": FALLBACK,
                "ADR_CHAT_FALLBACK_MODELS": fallback_models_env,
            }),
            patch.object(adr, "req_post", side_effect=fake_post),
            patch.object(adr, "log"),
            patch.object(adr.time, "sleep", side_effect=sleeps.append),
        ):
            result = adr.chat(
                PRIMARY,
                "system",
                "user",
                max_tokens=321,
                timeout=123,
                fallback_models=fallback_models_arg,
            )
        return result, calls, sleeps

    def test_default_production_model_tiers(self):
        self.assertEqual(adr.CREATIVE_MODEL, "GPT_5_6_SOL")
        self.assertEqual(adr.JUDGMENT_MODEL, "GEMINI_3_7_FLASH")
        self.assertEqual(adr.VISION_MODEL, "GEMINI_3_7_FLASH")
        self.assertEqual(
            adr.CREATIVE_FALLBACK_MODELS,
            ("CLAUDE_4_8_OPUS", "GEMINI_3_7_FLASH", "GEMINI_25_FLASH"),
        )
        self.assertEqual(adr.JUDGMENT_FALLBACK_MODELS, ("GEMINI_25_FLASH",))
        self.assertEqual(adr.VISION_FALLBACK_MODELS, ("GEMINI_25_FLASH",))

    def test_business_500_switches_to_fallback(self):
        production_error = {
            "status": 500,
            "desc": "Server error, please try again later",
            "message": "抱歉，我没听清楚您说的话。可以请您再说一次吗？",
            "success": False,
        }
        result, calls, sleeps = self._run_chat([production_error, _ok()])
        self.assertEqual(result, "fallback ok")
        self.assertEqual(calls, [PRIMARY, FALLBACK])
        self.assertEqual(sleeps, [])

    def test_raised_http_5xx_switches_to_fallback(self):
        result, calls, sleeps = self._run_chat(
            [RuntimeError("503 Server Error: Service Unavailable"), _ok("http fallback ok")]
        )
        self.assertEqual(result, "http fallback ok")
        self.assertEqual(calls, [PRIMARY, FALLBACK])
        self.assertEqual(sleeps, [])

    def test_exception_wrapped_json_5xx_switches_to_fallback(self):
        result, calls, _sleeps = self._run_chat(
            [RuntimeError('upstream failed: {"status": 503, "success": false}'), _ok("json fallback")]
        )
        self.assertEqual(result, "json fallback")
        self.assertEqual(calls, [PRIMARY, FALLBACK])

    def test_explicit_non_5xx_status_wins_over_vague_text(self):
        self.assertFalse(
            adr._is_llm_retryable_server_error({"status": 400, "desc": "server error-like user input"})
        )

    def test_fallback_does_not_bounce_or_retry_forever(self):
        error = {"status": 500, "desc": "Server error", "success": False}
        calls = []

        def always_error(_path, payload, timeout):
            calls.append(str(payload["model"]))
            return error

        with (
            patch.dict(os.environ, {
                "ADR_CHAT_FALLBACK_MODEL": FALLBACK,
                "ADR_CHAT_FALLBACK_MODELS": "",
            }),
            patch.object(adr, "req_post", side_effect=always_error),
            patch.object(adr, "log"),
            patch.object(adr.time, "sleep"),
            self.assertRaisesRegex(RuntimeError, "模型链"),
        ):
            adr.chat(PRIMARY, "system", "user")
        self.assertEqual(calls, [PRIMARY, FALLBACK, FALLBACK])

    def test_429_keeps_primary_and_uses_quota_backoff(self):
        quota = {"status": 429, "message": "Resource has been exhausted; check quota"}
        result, calls, sleeps = self._run_chat([quota, _ok("quota recovered")])
        self.assertEqual(result, "quota recovered")
        self.assertEqual(calls, [PRIMARY, PRIMARY])
        self.assertEqual(sleeps, [adr._LLM_RATE_LIMIT_BACKOFF])

    def test_1006_model_missing_still_switches(self):
        missing = {"status": 1006, "message": "request rejected"}
        result, calls, sleeps = self._run_chat([missing, _ok("missing fallback")])
        self.assertEqual(result, "missing fallback")
        self.assertEqual(calls, [PRIMARY, FALLBACK])
        self.assertEqual(sleeps, [])

    def test_1006_alternate_code_field_still_switches(self):
        missing = {"data": {"code": "1006"}, "message": "request rejected"}
        result, calls, sleeps = self._run_chat([missing, _ok("nested missing fallback")])
        self.assertEqual(result, "nested missing fallback")
        self.assertEqual(calls, [PRIMARY, FALLBACK])
        self.assertEqual(sleeps, [])

    def test_last_original_attempt_still_gets_real_fallback_call(self):
        generic = {"status": 400, "message": "temporary malformed response"}
        server_error = {"status": 500, "desc": "Server error"}
        result, calls, _sleeps = self._run_chat(
            [generic, generic, server_error, _ok("late fallback")]
        )
        self.assertEqual(result, "late fallback")
        self.assertEqual(calls, [PRIMARY, PRIMARY, PRIMARY, FALLBACK])

    def test_multistage_5xx_walks_ordered_chain(self):
        error = {"status": 500, "desc": "Server error"}
        result, calls, sleeps = self._run_chat(
            [error, error, _ok("third model ok")],
            fallback_models_env="MODEL_A, MODEL_B",
        )
        self.assertEqual(result, "third model ok")
        self.assertEqual(calls, [PRIMARY, "MODEL_A", "MODEL_B"])
        self.assertEqual(sleeps, [])

    def test_last_attempt_can_cascade_across_multiple_models(self):
        generic = {"status": 400, "message": "temporary malformed response"}
        server_error = {"status": 500, "desc": "Server error"}
        result, calls, _sleeps = self._run_chat(
            [generic, generic, server_error, server_error, _ok("cascade ok")],
            fallback_models_env="MODEL_A, MODEL_B",
        )
        self.assertEqual(result, "cascade ok")
        self.assertEqual(calls, [PRIMARY, PRIMARY, PRIMARY, "MODEL_A", "MODEL_B"])

    def test_429_on_intermediate_model_does_not_advance_chain(self):
        server_error = {"status": 500, "desc": "Server error"}
        quota = {"status": 429, "message": "Resource has been exhausted; check quota"}
        result, calls, sleeps = self._run_chat(
            [server_error, quota, _ok("quota recovered")],
            fallback_models_env="MODEL_A, MODEL_B",
        )
        self.assertEqual(result, "quota recovered")
        self.assertEqual(calls, [PRIMARY, "MODEL_A", "MODEL_A"])
        self.assertEqual(sleeps, [adr._LLM_RATE_LIMIT_BACKOFF * 2])

    def test_chain_deduplicates_primary_empty_and_repeated_entries(self):
        server_error = {"status": 500, "desc": "Server error"}
        result, calls, _sleeps = self._run_chat(
            [server_error, server_error, _ok("dedup ok")],
            fallback_models_env=f" {PRIMARY},,MODEL_A,MODEL_A,MODEL_B ",
        )
        self.assertEqual(result, "dedup ok")
        self.assertEqual(calls, [PRIMARY, "MODEL_A", "MODEL_B"])

    def test_explicit_fallback_argument_overrides_environment(self):
        server_error = {"status": 500, "desc": "Server error"}
        result, calls, _sleeps = self._run_chat(
            [server_error, _ok("explicit ok")],
            fallback_models_env="ENV_MODEL",
            fallback_models_arg=("EXPLICIT_MODEL",),
        )
        self.assertEqual(result, "explicit ok")
        self.assertEqual(calls, [PRIMARY, "EXPLICIT_MODEL"])

    def test_explicit_route_disambiguates_equal_primary_models(self):
        server_error = {"status": 500, "desc": "Server error"}
        calls = []

        def fake_post(_path, payload, timeout):
            calls.append(str(payload["model"]))
            return server_error if len(calls) == 1 else _ok("judgment route ok")

        with (
            patch.dict(os.environ, {
                "ADR_CHAT_FALLBACK_MODEL": "",
                "ADR_CHAT_FALLBACK_MODELS": "",
            }),
            patch.object(adr, "CREATIVE_MODEL", "SHARED_MODEL"),
            patch.object(adr, "JUDGMENT_MODEL", "SHARED_MODEL"),
            patch.object(adr, "req_post", side_effect=fake_post),
            patch.object(adr, "log"),
            patch.object(adr.time, "sleep"),
        ):
            result = adr.chat(
                "SHARED_MODEL",
                "system",
                "user",
                fallback_route="judgment",
            )
        self.assertEqual(result, "judgment route ok")
        self.assertEqual(calls, ["SHARED_MODEL", "GEMINI_25_FLASH"])

    def test_creative_model_uses_its_own_default_chain(self):
        server_error = {"status": 500, "desc": "Server error"}
        calls = []

        def fake_post(_path, payload, timeout):
            calls.append(str(payload["model"]))
            return server_error if len(calls) == 1 else _ok("creative fallback ok")

        with (
            patch.dict(os.environ, {
                "ADR_CHAT_FALLBACK_MODEL": "",
                "ADR_CHAT_FALLBACK_MODELS": "",
            }),
            patch.object(adr, "req_post", side_effect=fake_post),
            patch.object(adr, "log"),
            patch.object(adr.time, "sleep"),
        ):
            result = adr.chat(adr.CREATIVE_MODEL, "system", "user")
        self.assertEqual(result, "creative fallback ok")
        self.assertEqual(calls, ["GPT_5_6_SOL", "CLAUDE_4_8_OPUS"])

    def test_legacy_single_fallback_overrides_default_creative_chain(self):
        server_error = {"status": 500, "desc": "Server error"}
        calls = []

        def fake_post(_path, payload, timeout):
            calls.append(str(payload["model"]))
            return server_error if len(calls) == 1 else _ok("legacy override ok")

        with (
            patch.dict(os.environ, {
                "ADR_CHAT_FALLBACK_MODEL": "LEGACY_MODEL",
                "ADR_CHAT_FALLBACK_MODELS": "",
            }),
            patch.object(adr, "req_post", side_effect=fake_post),
            patch.object(adr, "log"),
            patch.object(adr.time, "sleep"),
        ):
            result = adr.chat(adr.CREATIVE_MODEL, "system", "user")
        self.assertEqual(result, "legacy override ok")
        self.assertEqual(calls, ["GPT_5_6_SOL", "LEGACY_MODEL"])

    def test_vision_5xx_uses_vision_fallback_chain(self):
        server_error = {"status": 500, "desc": "Server error"}
        calls = []

        def fake_post(path, payload, timeout):
            self.assertEqual(path, "/chat/completions")
            self.assertEqual(timeout, 45)
            calls.append(str(payload["model"]))
            return server_error if len(calls) == 1 else _ok("vision fallback ok")

        payload = {"model": adr.VISION_MODEL, "messages": [], "max_tokens": 10}
        with (
            patch.object(adr, "req_post", side_effect=fake_post),
            patch.object(adr, "log"),
        ):
            result = adr._vision_chat_completion(payload, timeout=45)
        self.assertEqual(result, _ok("vision fallback ok"))
        self.assertEqual(calls, ["GEMINI_3_7_FLASH", "GEMINI_25_FLASH"])
        self.assertEqual(payload["model"], "GEMINI_3_7_FLASH")

    def test_vision_429_does_not_advance_chain(self):
        quota = {"status": 429, "message": "Resource has been exhausted; check quota"}
        calls = []

        def fake_post(_path, payload, timeout):
            calls.append(str(payload["model"]))
            return quota

        sleeps = []
        with (
            patch.object(adr, "req_post", side_effect=fake_post),
            patch.object(adr, "log"),
            patch.object(adr.time, "sleep", side_effect=sleeps.append),
        ):
            result = adr._vision_chat_completion(
                {"model": adr.VISION_MODEL, "messages": [], "max_tokens": 10}
            )
        self.assertEqual(result, quota)
        self.assertEqual(calls, ["GEMINI_3_7_FLASH"] * 3)
        self.assertEqual(sleeps, [adr._LLM_RATE_LIMIT_BACKOFF, adr._LLM_RATE_LIMIT_BACKOFF * 2])

    def test_vision_1006_alternate_status_field_uses_fallback(self):
        missing = {"status_code": "1006", "message": "request rejected"}
        calls = []

        def fake_post(_path, payload, timeout):
            calls.append(str(payload["model"]))
            return missing if len(calls) == 1 else _ok("vision missing fallback")

        with (
            patch.object(adr, "req_post", side_effect=fake_post),
            patch.object(adr, "log"),
        ):
            result = adr._vision_chat_completion(
                {"model": adr.VISION_MODEL, "messages": [], "max_tokens": 10}
            )
        self.assertEqual(result, _ok("vision missing fallback"))
        self.assertEqual(calls, ["GEMINI_3_7_FLASH", "GEMINI_25_FLASH"])


if __name__ == "__main__":
    unittest.main()
