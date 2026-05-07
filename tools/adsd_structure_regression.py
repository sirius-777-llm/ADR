#!/usr/bin/env python3
"""Local ADSD structure regression.

This does not call WeryAI generation APIs. It imports run_adr_v8.py with local
environment already loaded and validates the ADSD script-shape contract:
monologue, dialogue, ensemble, and injected override scripts.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_adr():
    sys.argv = ["run_adr_v8.py", "adsd-structure-regression", "v", "--ads-dialogue", "--onsite-pov"]
    spec = importlib.util.spec_from_file_location("adr", ROOT / "run_adr_v8.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def run_generated_shape_case(adr, name: str, rows: list[dict], expected_shape: str, expected_count: int) -> None:
    def fake_chat(*args, **kwargs):
        return json.dumps(rows, ensure_ascii=False)

    adr.chat = fake_chat
    turns = adr._generate_adsd_dialogue_turns("1895年5月2日公车上书", len(rows), "中性", "朴素直接")
    speakers = list(dict.fromkeys(t["speaker"] for t in turns))
    assert turns[0]["dialogue_shape"] == expected_shape, (name, turns[0]["dialogue_shape"])
    assert turns[0]["speaker_count"] == expected_count, (name, turns[0]["speaker_count"])
    assert len(speakers) == expected_count, (name, speakers)
    assert all("记者" != t["speaker"] for t in turns), (name, speakers)
    print(f"generated:{name}: {expected_shape} {speakers}")


def run_override_case(adr, name: str, rows: list[str], expected_shape: str, min_count: int, max_count: int) -> None:
    turns = adr._parse_adsd_override_turns(rows, "1895年5月2日公车上书")
    speakers = list(dict.fromkeys(t["speaker"] for t in turns))
    assert turns[0]["dialogue_shape"] == expected_shape, (name, turns[0]["dialogue_shape"])
    assert min_count <= turns[0]["speaker_count"] <= max_count, (name, turns[0]["speaker_count"])
    assert all("记者" != t["speaker"] for t in turns), (name, speakers)
    print(f"override:{name}: {expected_shape} {speakers}")


def main() -> int:
    adr = load_adr()
    base = "这句话直接说明事实背景，让普通观众能立刻听懂原因。"

    run_generated_shape_case(
        adr,
        "monologue",
        [
            {"speaker": "上书士人", "text": base, "shot": "案前，上书士人低声说明奏章内容", "emotion": "solemn"},
            {"speaker": "上书士人", "text": base, "shot": "人群边，上书士人举起纸页继续讲述", "emotion": "explanatory"},
            {"speaker": "上书士人", "text": base, "shot": "门廊下，上书士人回望众人补充因果", "emotion": "neutral"},
            {"speaker": "上书士人", "text": base, "shot": "书案旁，上书士人点明这件事的后果", "emotion": "solemn"},
        ],
        "monologue",
        1,
    )
    run_generated_shape_case(
        adr,
        "dialogue",
        [
            {"speaker": "上书士人", "text": base, "shot": "街口，上书士人指着榜文发问", "emotion": "tense"},
            {"speaker": "旁观官员", "text": base, "shot": "门前，旁观官员解释朝廷处境", "emotion": "explanatory"},
            {"speaker": "上书士人", "text": base, "shot": "案旁，上书士人追问上书缘由", "emotion": "neutral"},
            {"speaker": "旁观官员", "text": base, "shot": "廊下，旁观官员说明结果", "emotion": "solemn"},
        ],
        "dialogue",
        2,
    )
    run_generated_shape_case(
        adr,
        "ensemble",
        [
            {"speaker": "上书士人", "text": base, "shot": "会馆里，上书士人先说明危机", "emotion": "tense"},
            {"speaker": "旁观官员", "text": base, "shot": "门边，旁观官员解释朝局", "emotion": "explanatory"},
            {"speaker": "在京举人", "text": base, "shot": "桌旁，在京举人补充众人反应", "emotion": "neutral"},
            {"speaker": "书吏", "text": base, "shot": "案前，书吏记录上书文本", "emotion": "solemn"},
        ],
        "ensemble",
        4,
    )

    run_override_case(
        adr,
        "plain_four_line_monologue",
        [
            "这是一句直接说明事实的独白台词，观众能听懂。",
            "第二句继续交代人物处境，不需要其他人发问。",
            "第三句解释关键原因，把事情说清楚。",
            "第四句说明后果，收束到历史判断。",
        ],
        "monologue",
        1,
        1,
    )
    run_override_case(
        adr,
        "role_prefixed_ensemble",
        [
            "上书士人：这份上书今天必须递进去，不能再拖了。",
            "旁观官员：朝廷已经知道消息，但局势很紧。",
            "在京举人：大家聚在会馆，就是想说清楚理由。",
            "上书士人：割地赔款不是小事，关系到国家去向。",
            "记者：我不该作为现代角色出现，会被替换。",
            "书吏：我把这些话记下来，免得递交时漏掉。",
        ],
        "ensemble",
        3,
        4,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
