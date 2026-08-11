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
SPIKE_PATH = ROOT / "tools" / "spike_almighty.py"
ADS_PATH = ROOT.parent / "ADS" / "run_ads.py"
SUPPORTED = {
    "WERYDANCE",
    "SEEDANCE_2_0_OS",
    "SEEDANCE_2_0_FAST_OS",
    "SEEDANCE_2_0_MINI_OS",
    "WERYDANCE_2_0",
    "WERYDANCE_2_0_FAST",
    "WERYDANCE_2_0_MINI",
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
        "print(json.dumps({'models':[adr.ALMIGHTY_MODEL,adr.ALMIGHTY_FAST_MODEL],"
        "'cache_files':[adr._motion_tasks_file().name,adr._lip_sync_tasks_file().name,"
        "adr._grid_multiref_tasks_file().name,adr._previs_page_tasks_file().name]}))"
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
    default_snapshot = json.loads(default.stdout.strip().splitlines()[-1])
    assert default_snapshot["models"] == [
        "WERYDANCE",
        "SEEDANCE_2_0_FAST_OS",
    ]
    assert default_snapshot["cache_files"] == [
        "motion_tasks.json",
        "lip_sync_tasks.json",
        "grid_multiref_motion_tasks.json",
        "previs_page_motion_tasks.json",
    ]

    for model in SUPPORTED:
        result = _import_config(model.lower(), model)
        assert result.returncode == 0, result.stderr
        snapshot = json.loads(result.stdout.strip().splitlines()[-1])
        assert snapshot["models"] == [model, model]
        assert snapshot["cache_files"] == [
            "motion_tasks.json",
            "lip_sync_tasks.json",
            "grid_multiref_motion_tasks.json",
            "previs_page_motion_tasks.json",
        ]

    invalid = _import_config("TYPO_MODEL", None)
    assert invalid.returncode == 2
    assert "ADR_ALMIGHTY_MODEL" in invalid.stderr
    assert "TYPO_MODEL" in invalid.stderr


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
        literals = {node.value for node in ast.walk(owner) if isinstance(node, ast.Constant)}
        assert "negative_prompt" not in literals
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


def test_probe_routing() -> None:
    env = os.environ.copy()
    env["ADR_ALMIGHTY_MODEL"] = "SEEDANCE_2_0_MINI_OS"
    code = (
        "import json; from tools.adsd_lipsync_poc import make_candidates; "
        "items=make_candidates('image','audio','prompt',5,'16:9'); "
        "print(json.dumps([[x['path'],x['payload']['model']] for x in items]))"
    )
    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stderr
    candidates = json.loads(result.stdout.strip().splitlines()[-1])
    assert candidates[0] == [
        "/generation/almighty-reference-to-video",
        "SEEDANCE_2_0_MINI_OS",
    ]
    assert all(model == "WERYDANCE_2_0" for _, model in candidates[1:])

    spike_tree = ast.parse(SPIKE_PATH.read_text(encoding="utf-8"), filename=str(SPIKE_PATH))
    submit_fn = next(
        node for node in spike_tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "submit_almighty"
    )
    payload_model = _assigned_dict_model(submit_fn, "payload")
    assert isinstance(payload_model, ast.Attribute)
    assert isinstance(payload_model.value, ast.Name) and payload_model.value.id == "adr"
    assert payload_model.attr == "ALMIGHTY_MODEL"


def test_resume_cache_contract() -> None:
    env = os.environ.copy()
    env.update({
        "WERYAI_API_KEY": "test_dummy",
        "TG_BOT_TOKEN": "test_dummy",
        "TG_CHAT_ID": "test_dummy",
    })
    code = r'''
import json
from pathlib import Path
import tempfile
import run_adr_v8 as adr

root = Path(tempfile.mkdtemp(prefix="adr_resume_cache_"))
adr.OUTPUT_DIR = root
legacy_specs = [
    (adr._motion_tasks_file(), "0", "legacy-motion", adr._load_motion_tasks),
    (adr._lip_sync_tasks_file(), "0", "legacy-lip", adr._load_lip_sync_tasks),
    (adr._grid_multiref_tasks_file(), "01_04", "legacy-grid", adr._load_grid_multiref_tasks),
    (adr._previs_page_tasks_file(), "01_04", "legacy-previs", adr._load_previs_page_tasks),
]
for path, key, task_id, loader in legacy_specs:
    path.write_text(json.dumps({key: task_id}), encoding="utf-8")
    loaded = loader()[key]
    assert loaded["task_id"] == task_id
    assert loaded["legacy_format"] is True

adr._save_motion_task(
    1,
    "motion-new",
    model="WERYDANCE_2_0",
    interface="/generation/image-to-video",
    mode="storyboard-reference-motion",
)
adr._save_lip_sync_task(
    1,
    "lip-fast",
    model="SEEDANCE_2_0_FAST_OS",
    variant="audio_dub_fast_retry_1",
    generate_audio="true",
)
adr._save_grid_multiref_task("05_08", "grid-new", model="SEEDANCE_2_0_OS")
adr._save_previs_page_task("05_08", "previs-new", model="WERYDANCE")

assert adr._load_motion_tasks()["1"]["interface"] == "image-to-video"
fast_record = adr._load_lip_sync_tasks()["1"]
assert fast_record["model"] == "SEEDANCE_2_0_FAST_OS"
assert fast_record["interface"] == "almighty-reference-to-video"
assert adr._load_grid_multiref_tasks()["05_08"]["model"] == "SEEDANCE_2_0_OS"
assert adr._load_previs_page_tasks()["05_08"]["model"] == "WERYDANCE"

adr._lip_sync_poll_download_and_process = lambda *args, **kwargs: (True, {"pass": True})
scene = {}
ok, info = adr._resume_lip_sync_task(1, fast_record, scene, 5.0)
assert ok is True
assert info["submit_model"] == "SEEDANCE_2_0_FAST_OS"
assert info["variant"] == "audio_dub_fast_retry_1"
assert scene["_almighty_audio_dub_attempt"] is True

# A legacy unresolved task must enter the poll path and never submit a replacement.
adr._motion_tasks_file().write_text(json.dumps({"0": "paid-waiting-task"}), encoding="utf-8")
polls = []
submits = []
adr._motion_poll_and_download = lambda idx, task_id, path, target_dur=None: polls.append(task_id) or False
adr.req_post = lambda *args, **kwargs: submits.append(args) or (_ for _ in ()).throw(AssertionError("unexpected submit"))
result = adr._motion_one_scene(
    0,
    {"img_path": "unused.png", "vid_path": str(root / "seg_0.mp4"), "dur": 5},
    "motion",
    "16:9",
)
assert result is False
assert polls == ["paid-waiting-task"]
assert submits == []

# A newly submitted lip-sync task timing out must not fall through to FAST variants.
adr._upload_to_weryai = lambda path: "https://example.invalid/ref"
adr._wait_motion_submit_slot = lambda label: None
lip_submits = []
adr.req_post = lambda *args, **kwargs: lip_submits.append(args[1]["model"]) or {"data": {"task_id": "lip-pending"}}
adr._lip_sync_poll_download_and_process = lambda *args, **kwargs: (
    False,
    {"pass": False, "reason": "poll_timeout"},
)
idx, ok, pending_info = adr._lip_sync_one_scene(
    2,
    {
        "turn_type": "silent_b",
        "needs_lip_sync": False,
        "img_path": "unused.png",
        "vid_path": str(root / "seg_2.mp4"),
        "text": "",
    },
    5.0,
    "16:9",
)
assert idx == 2 and ok is False
assert pending_info["timed_out_or_reusable"] is True
assert lip_submits == [adr.ALMIGHTY_MODEL]
assert adr._load_lip_sync_tasks()["2"]["task_id"] == "lip-pending"

# Grid B40.3 may retry terminal task_failed, but never a still-cached poll timeout.
adr.STORYBOARD_GRID_MULTIREF_MOTION = True
adr.STORYBOARD_GRID_MULTIREF_MAIN = False
adr.ADS_DIALOGUE_MODE = False
adr.tg = lambda message: None
adr._grid_multiref_tts_duration_buffered = lambda: 0.0
adr._select_voice_asset_reference = lambda *args, **kwargs: None
for i in range(2):
    (root / f"grid_ref_{i}.png").write_bytes(b"ref")
grid_submits = []
adr.req_post = lambda *args, **kwargs: grid_submits.append(args[1]["model"]) or {"data": {"task_id": "grid-pending"}}
adr._poll_video_task_download = lambda *args, **kwargs: (
    False,
    {"pass": False, "reason": "poll_timeout"},
)
grid_qa = adr._generate_grid_multiref_motion_segments(
    [
        {
            "storyboard_grid_mode": True,
            "img_path": str(root / f"grid_ref_{i}.png"),
            "text": f"scene {i}",
            "dur": 5,
        }
        for i in range(2)
    ],
    ["move one", "move two"],
    "16:9",
)
assert grid_submits == [adr.ALMIGHTY_MODEL]
assert grid_qa["records"][0]["timed_out_or_reusable"] is True
assert adr._load_grid_multiref_tasks()["01_02"]["task_id"] == "grid-pending"

print(json.dumps({
    "legacy": 4,
    "structured": 4,
    "fast_resume_model": info["submit_model"],
    "lip_timeout_submits": len(lip_submits),
    "grid_timeout_submits": len(grid_submits),
}))
'''
    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stderr
    snapshot = json.loads(result.stdout.strip().splitlines()[-1])
    assert snapshot == {
        "legacy": 4,
        "structured": 4,
        "fast_resume_model": "SEEDANCE_2_0_FAST_OS",
        "lip_timeout_submits": 1,
        "grid_timeout_submits": 1,
    }


def test_ads_model_config() -> None:
    assert ADS_PATH.exists(), ADS_PATH

    def run(model: str | None) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["WERYAI_API_KEY"] = "test_dummy"
        if model is None:
            env.pop("ADR_ALMIGHTY_MODEL", None)
        else:
            env["ADR_ALMIGHTY_MODEL"] = model
        return subprocess.run(
            [
                sys.executable,
                "-c",
                "import json,run_ads; print(json.dumps([run_ads.ALMIGHTY_MODEL,run_ads.ALMIGHTY_RESOLUTION]))",
            ],
            cwd=ADS_PATH.parent,
            env=env,
            text=True,
            capture_output=True,
            timeout=30,
        )

    default = run(None)
    assert default.returncode == 0, default.stderr
    assert json.loads(default.stdout.strip()) == ["WERYDANCE", "1080p"]
    fast = run("seedance_2_0_fast_os")
    assert fast.returncode == 0, fast.stderr
    assert json.loads(fast.stdout.strip()) == ["SEEDANCE_2_0_FAST_OS", "720p"]
    invalid = run("TYPO_MODEL")
    assert invalid.returncode == 2
    assert "ADR_ALMIGHTY_MODEL" in invalid.stderr

    tree = ast.parse(ADS_PATH.read_text(encoding="utf-8"), filename=str(ADS_PATH))
    generate = next(
        node for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "generate_beat_video"
    )
    calls = [
        node for node in ast.walk(generate)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "req_post"
        and node.args
        and isinstance(node.args[0], ast.Constant)
        and node.args[0].value == "/generation/almighty-reference-to-video"
    ]
    assert len(calls) == 1
    model = _dict_model_value(calls[0])
    assert isinstance(model, ast.Name) and model.id == "ALMIGHTY_MODEL"


def main() -> None:
    test_config_values()
    test_endpoint_routing()
    test_probe_routing()
    test_resume_cache_contract()
    test_ads_model_config()
    print("Almighty model tests: 5/5 passed")


if __name__ == "__main__":
    main()
