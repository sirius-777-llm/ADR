#!/usr/bin/env python3
"""Tests for Almighty-specific model routing without making API calls."""

import ast
from collections import Counter
import json
import os
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parent.parent
ADR_PATH = ROOT / "run_adr_v8.py"
SUPPORTED = {
    "WERYDANCE",
    "SEEDANCE_2_0_OS",
    "SEEDANCE_2_0_FAST_OS",
    "SEEDANCE_2_0_MINI_OS",
}


def _import_config(primary: str | None, fallback: str | None) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env.update({
        "WERYAI_API_KEY": "test_dummy",
        "TG_BOT_TOKEN": "test_dummy",
        "TG_CHAT_ID": "test_dummy",
    })
    for key, value in (
        ("ADR_ALMIGHTY_MODEL", primary),
        ("ADR_ALMIGHTY_FAST_MODEL", fallback),
    ):
        if value is None:
            env.pop(key, None)
        else:
            env[key] = value

    code = (
        "import json, run_adr_v8 as adr; "
        "print(json.dumps([adr.ALMIGHTY_MODEL, adr.ALMIGHTY_FAST_MODEL]))"
    )
    return subprocess.run(
        [sys.executable, "-c", code],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        timeout=30,
    )


def test_config_values() -> None:
    default = _import_config(None, None)
    assert default.returncode == 0, default.stderr
    assert json.loads(default.stdout.strip().splitlines()[-1]) == [
        "WERYDANCE",
        "SEEDANCE_2_0_FAST_OS",
    ]

    for model in SUPPORTED:
        result = _import_config(model.lower(), model)
        assert result.returncode == 0, result.stderr
        assert json.loads(result.stdout.strip().splitlines()[-1]) == [model, model]

    invalid = _import_config("WERYDANCE_2_0", None)
    assert invalid.returncode == 2
    assert "ADR_ALMIGHTY_MODEL" in invalid.stderr
    assert "WERYDANCE_2_0" in invalid.stderr


class _CallCollector(ast.NodeVisitor):
    def __init__(self) -> None:
        self.function_stack: list[ast.AST] = []
        self.calls: list[tuple[ast.Call, ast.AST | None, str]] = []

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self.function_stack.append(node)
        self.generic_visit(node)
        self.function_stack.pop()

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_Call(self, node: ast.Call) -> None:
        if (
            isinstance(node.func, ast.Name)
            and node.func.id == "req_post"
            and node.args
            and isinstance(node.args[0], ast.Constant)
            and isinstance(node.args[0].value, str)
        ):
            owner = self.function_stack[-1] if self.function_stack else None
            self.calls.append((node, owner, node.args[0].value))
        self.generic_visit(node)


def _model_value_from_dict(node: ast.AST) -> ast.expr | None:
    if not isinstance(node, ast.Dict):
        return None
    for key, value in zip(node.keys, node.values):
        if isinstance(key, ast.Constant) and key.value == "model":
            return value
    return None


def _dict_model_value(call: ast.Call) -> ast.expr | None:
    return _model_value_from_dict(call.args[1]) if len(call.args) >= 2 else None


def _assigned_dict_model(owner: ast.AST, variable: str) -> ast.expr | None:
    matches = []
    for node in ast.walk(owner):
        if not isinstance(node, ast.Assign):
            continue
        if any(isinstance(target, ast.Name) and target.id == variable for target in node.targets):
            model = _model_value_from_dict(node.value)
            if model is not None:
                matches.append(model)
    assert len(matches) == 1, f"expected one {variable} dict with model, found {len(matches)}"
    return matches[0]


def _variant_model_values(owner: ast.AST) -> list[ast.expr]:
    tuples: list[ast.Tuple] = []
    for node in ast.walk(owner):
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "variants" for target in node.targets
        ) and isinstance(node.value, ast.List):
            tuples.extend(item for item in node.value.elts if isinstance(item, ast.Tuple))
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if not isinstance(node.func.value, ast.Name) or node.func.value.id != "variants":
                continue
            tuple_arg = node.args[-1] if node.func.attr in {"append", "insert"} and node.args else None
            if isinstance(tuple_arg, ast.Tuple):
                tuples.append(tuple_arg)
    return [item.elts[1] for item in tuples if len(item.elts) == 4]


def test_endpoint_routing() -> None:
    tree = ast.parse(ADR_PATH.read_text(encoding="utf-8"), filename=str(ADR_PATH))
    collector = _CallCollector()
    collector.visit(tree)

    almighty = [item for item in collector.calls if item[2] == "/generation/almighty-reference-to-video"]
    assert len(almighty) == 11, f"expected 11 Almighty submits, found {len(almighty)}"
    counts = Counter(owner.name for _, owner, _ in almighty if isinstance(owner, ast.FunctionDef))
    assert counts == Counter({
        "_mtv_lip_sync_segment": 1,
        "_try_motion_audio_dub_video": 1,
        "_generate_character_trailer_motion": 1,
        "_gen_segment": 1,
        "_generate_storyboard_trailer_motion": 1,
        "_generate_previs_page_motion_segments": 1,
        "_run_grid_group": 3,
        "_lip_sync_one_group": 1,
        "_lip_sync_one_scene": 1,
    })

    direct_functions = {
        "_mtv_lip_sync_segment",
        "_try_motion_audio_dub_video",
        "_generate_character_trailer_motion",
        "_gen_segment",
        "_generate_storyboard_trailer_motion",
        "_generate_previs_page_motion_segments",
    }
    for call, owner, _ in almighty:
        assert isinstance(owner, ast.FunctionDef)
        if owner.name in direct_functions:
            model = _dict_model_value(call)
            assert isinstance(model, ast.Name) and model.id == "ALMIGHTY_MODEL"
        elif owner.name == "_run_grid_group":
            assert isinstance(call.args[1], ast.Name) and call.args[1].id == "payload"
            model = _assigned_dict_model(owner, "base_payload")
            assert isinstance(model, ast.Name) and model.id == "ALMIGHTY_MODEL"
        elif owner.name == "_lip_sync_one_group":
            assert isinstance(call.args[1], ast.Name) and call.args[1].id == "payload"
            model = _assigned_dict_model(owner, "payload")
            assert isinstance(model, ast.Name) and model.id == "ALMIGHTY_MODEL"
        elif owner.name == "_lip_sync_one_scene":
            assert isinstance(call.args[1], ast.Name) and call.args[1].id == "payload"
            model = _assigned_dict_model(owner, "payload")
            assert isinstance(model, ast.Name) and model.id == "model"
            variant_models = _variant_model_values(owner)
            assert variant_models
            assert all(
                isinstance(value, ast.Name) and value.id in {"ALMIGHTY_MODEL", "ALMIGHTY_FAST_MODEL"}
                for value in variant_models
            )
            assert {value.id for value in variant_models if isinstance(value, ast.Name)} == {
                "ALMIGHTY_MODEL",
                "ALMIGHTY_FAST_MODEL",
            }
        else:
            raise AssertionError(f"unhandled Almighty submit in {owner.name}")

    legacy_video_calls = [
        item for item in collector.calls
        if item[2] in {"/generation/image-to-video", "/generation/text-to-video"}
    ]
    assert len(legacy_video_calls) == 4
    for call, _, _ in legacy_video_calls:
        model = _dict_model_value(call)
        assert isinstance(model, ast.Constant)
        assert model.value == "WERYDANCE_2_0"


def main() -> None:
    test_config_values()
    test_endpoint_routing()
    print("Almighty model tests: 2/2 passed")


if __name__ == "__main__":
    main()
