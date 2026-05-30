#!/usr/bin/env python3
"""B69 单测: 内容驱动 gate / manifest / crossfade filter / 原子写.

不依赖 ADR / ffmpeg / API key — 纯逻辑层. 跑:
  python3 tools/test_long_video.py
"""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.long_video import (  # noqa: E402
    build_plan, init_manifest, build_crossfade_filter,
    _atomic_write_json, _load_manifest, _final_mp4_belongs, _outdir_belongs, MANIFEST_SCHEMA,
)

_passed = 0
_failed = 0


def check(name: str, cond: bool, detail: str = ""):
    global _passed, _failed
    if cond:
        _passed += 1
        print(f"  ✅ {name}")
    else:
        _failed += 1
        print(f"  ❌ {name} {detail}")


def test_gate():
    print("[build_plan 内容驱动 gate]")
    # 1. 空文本
    mode, chunks = build_plan("", 12, 30)
    check("空文本 → single_run/空", mode == "single_run" and chunks == [], f"got {mode},{chunks}")

    # 2. 短诗 4 句 (远低于阈值) → 单 run 不切, 不注水
    poem = "床前明月光。疑是地上霜。举头望明月。低头思故乡。"
    mode, chunks = build_plan(poem, 12, 30)
    check("短诗4句 → single_run 1段", mode == "single_run" and len(chunks) == 1 and len(chunks[0]) == 4,
          f"got {mode}, {[len(c) for c in chunks]}")

    # 3. 恰好等于阈值 30 句 → 仍 single_run (<=)
    text30 = "".join(f"第{i}句话。" for i in range(30))
    mode, chunks = build_plan(text30, 12, 30)
    check("=30句 边界 → single_run", mode == "single_run" and len(chunks[0]) == 30,
          f"got {mode}, {[len(c) for c in chunks]}")

    # 4. 31 句 (超阈值) → chunked, chunk_size=12 → 12+12+7
    text31 = "".join(f"第{i}句话。" for i in range(31))
    mode, chunks = build_plan(text31, 12, 30)
    check("31句 → chunked 3段(12,12,7)",
          mode == "chunked" and [len(c) for c in chunks] == [12, 12, 7],
          f"got {mode}, {[len(c) for c in chunks]}")

    # 5. 末句无标点也算 (复用 B66 split 尾句补)
    text_tail = "".join(f"句{i}。" for i in range(31)) + "结尾没有标点"
    mode, chunks = build_plan(text_tail, 12, 30)
    total = sum(len(c) for c in chunks)
    check("末句无标点被计入", total == 32, f"got total {total}")

    # 6. 整段无标点 → 1 句 → single_run
    mode, chunks = build_plan("一段没有任何句末标点的连续文字内容", 12, 30)
    check("无标点整段 → single_run 1句", mode == "single_run" and len(chunks[0]) == 1,
          f"got {mode}, {[len(c) for c in chunks]}")

    # 7. 空白/空句被守卫过滤 (夹杂多余空白不应产空段)
    text_ws = "句一。   。  句三。"  # 中间 "。" 前只有空白
    mode, chunks = build_plan(text_ws, 12, 30)
    flat = [s for c in chunks for s in c]
    check("空白句被过滤无空段", all(s.strip() for s in flat) and len(flat) >= 2,
          f"got {flat}")


def test_manifest():
    print("[init_manifest 结构]")
    chunks = [[f"a{i}" for i in range(12)], [f"b{i}" for i in range(12)], [f"c{i}" for i in range(7)]]
    m = init_manifest("滕王阁序", "h", "chunked", chunks, 12, 30, 1.0, Path("/tmp/x"), 1717000000.0)
    check("schema 正确", m["schema"] == MANIFEST_SCHEMA)
    check("total_sentences=31", m["total_sentences"] == 31, f"got {m['total_sentences']}")
    check("3 段", len(m["segments"]) == 3)
    s0, s1, s2 = m["segments"]
    check("段0 范围[0:12]", (s0["sentence_start"], s0["sentence_end"]) == (0, 12),
          f"got {s0['sentence_start']},{s0['sentence_end']}")
    check("段1 范围[12:24]", (s1["sentence_start"], s1["sentence_end"]) == (12, 24),
          f"got {s1['sentence_start']},{s1['sentence_end']}")
    check("段2 范围[24:31]", (s2["sentence_start"], s2["sentence_end"]) == (24, 31),
          f"got {s2['sentence_start']},{s2['sentence_end']}")
    check("初始 status=pending", all(s["status"] == "pending" for s in m["segments"]))
    check("bgm_master 初始 None", m["bgm_master"] is None)
    check("crossfade 透传", m["crossfade_sec"] == 1.0)


def test_crossfade_filter():
    print("[build_crossfade_filter 命令构造]")
    durations = [10.0, 8.0, 6.0]
    filt, vlab, alab = build_crossfade_filter(durations, 1.0)
    # 第一次 xfade offset = 10-1 = 9.000
    check("xfade1 offset=9.000", "offset=9.000" in filt, filt)
    # running = 10+8-1=17; 第二次 offset=17-1=16.000
    check("xfade2 offset=16.000", "offset=16.000" in filt, filt)
    check("含 acrossfade d=1", "acrossfade=d=1" in filt, filt)
    check("transition=fade", "transition=fade" in filt, filt)
    check("final v 标签 [v2]", vlab == "[v2]", f"got {vlab}")
    check("final a 标签 [a2]", alab == "[a2]", f"got {alab}")
    # 两段最简
    filt2, v2, a2 = build_crossfade_filter([5.0, 5.0], 1.0)
    check("两段 offset=4.000", "offset=4.000" in filt2, filt2)
    check("两段 final [v1]/[a1]", v2 == "[v1]" and a2 == "[a1]", f"got {v2},{a2}")


def test_atomic_io():
    print("[manifest 原子写 + load]")
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "b69_manifest.json"
        m = init_manifest("t", "h", "chunked", [["x"], ["y"]], 1, 30, 1.0, Path(d), 1.0)
        _atomic_write_json(p, m)
        check("文件已写", p.exists())
        loaded = _load_manifest(p)
        check("round-trip schema", loaded is not None and loaded["schema"] == MANIFEST_SCHEMA)
        check("round-trip 段数", loaded["segments"][1]["idx"] == 1)
        # 坏 schema 不被 load
        bad = Path(d) / "bad.json"
        bad.write_text('{"schema":"other"}', encoding="utf-8")
        check("错 schema → None", _load_manifest(bad) is None)
        # 不存在 → None
        check("缺文件 → None", _load_manifest(Path(d) / "nope.json") is None)


def test_ownership():
    print("[_final_mp4_belongs 路径归属守卫 (Codex H1/H2)]")
    with tempfile.TemporaryDirectory() as d:
        run_root = Path(d) / "run"
        (run_root / "out_00").mkdir(parents=True)
        good = run_root / "out_00" / "ADR_V8_HADS_x.mp4"
        good.write_bytes(b"x")
        check("run_root 内真实文件 → True", _final_mp4_belongs(str(good), run_root) is True)
        check("None → False", _final_mp4_belongs(None, run_root) is False)
        # run_root 外的文件
        outside = Path(d) / "outside.mp4"
        outside.write_bytes(b"x")
        check("run_root 外文件 → False", _final_mp4_belongs(str(outside), run_root) is False)
        # 不存在
        check("不存在路径 → False", _final_mp4_belongs(str(run_root / "nope.mp4"), run_root) is False)
        # 含换行 (注入) → False
        check("含换行注入 → False", _final_mp4_belongs(str(good) + "\nfile 'x'", run_root) is False)
        # 目录而非文件 → False
        check("目录非文件 → False", _final_mp4_belongs(str(run_root / "out_00"), run_root) is False)


def test_resume_content_guard():
    print("[resume 内容一致性 (Codex Stage4: 同句数改文须拒绝复用)]")
    textA = "".join(f"甲句{i}。" for i in range(31))
    textB = "".join(f"乙句{i}。" for i in range(31))  # 同 31 句, 内容不同
    _, chunksA = build_plan(textA, 12, 30)
    _, chunksB = build_plan(textB, 12, 30)
    check("同句数不同内容 → chunks 不同 (resume 会拒绝)", chunksA != chunksB,
          "若相等则 resume 内容校验失效")
    _, chunksA2 = build_plan(textA, 12, 30)
    check("同 text → chunks 完全一致 (resume 安全复用)", chunksA == chunksA2)
    # 单句改动也要能区分
    textC = "".join((f"甲句{i}。" if i != 5 else "改了第五句。") for i in range(31))
    _, chunksC = build_plan(textC, 12, 30)
    check("仅改 1 句 → chunks 不同", chunksA != chunksC)


def test_outdir_belongs():
    print("[_outdir_belongs rmtree 前 out_dir 安全守卫 (Codex review Med2)]")
    with tempfile.TemporaryDirectory() as d:
        rr = Path(d) / "run"
        rr.mkdir()
        check("run_root/out_00 → True", _outdir_belongs(rr / "out_00", rr) is True)
        check("run_root/out_03 → True", _outdir_belongs(rr / "out_03", rr) is True)
        check("非 out_* 子目录 → False", _outdir_belongs(rr / "foo", rr) is False)
        check("run_root 外目录 → False", _outdir_belongs(Path(d) / "elsewhere", rr) is False)
        check("run_root 自身 → False", _outdir_belongs(rr, rr) is False)
        check("嵌套更深 → False", _outdir_belongs(rr / "out_00" / "sub", rr) is False)
        check("篡改到家目录 → False", _outdir_belongs(Path.home(), rr) is False)


def main():
    test_gate()
    test_manifest()
    test_crossfade_filter()
    test_atomic_io()
    test_ownership()
    test_resume_content_guard()
    test_outdir_belongs()
    print(f"\n{'='*40}\n结果: {_passed} 通过 / {_failed} 失败")
    sys.exit(1 if _failed else 0)


if __name__ == "__main__":
    main()
