#!/usr/bin/env python3
"""Claude × Codex 协同协议 (CCP) 落地工具 · 2026-05-26.

4 阶段协同, 每阶段调 codex exec 拿独立第二视角:
  1. review-spec  · 需求评审 (Codex pre-review): 这需求该做吗 / 漏的边界
  2. propose-alt  · 方案设计 (Dual Design): 独立给方案 B 让 Claude 对比
  3. review-code  · 代码落地 (Mid-write Review): 写到一半审 bug
  4. final-qa     · 交付验证 (Final QA): ship 后端到端 sanity

输出自动写 voice_assets/collab_history.json (跨 session 持久).

用法:
  python3 tools/codex_collab.py review-spec --topic "B10 ADS 多音色 fix" --context "Root cause: ..."
  python3 tools/codex_collab.py propose-alt --topic "B10 自动 IP 进化" --my-plan "..."
  python3 tools/codex_collab.py review-code --files "run_adr_v8.py:790-820" --topic "B10 mapping table"
  python3 tools/codex_collab.py final-qa --topic "B10" --files "tools/evolve_ips.py,run_adr_v8.py"
  python3 tools/codex_collab.py history --last 10
"""
import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HISTORY_PATH = ROOT / "voice_assets" / "collab_history.json"
DEFAULT_TIMEOUT = 600  # 10min per codex call

STAGE_PROMPTS = {
    "review-spec": """需求评审 (Codex pre-review). 视角: 独立 senior PM/dev 评审.

判断这个需求/bug 是否值得做, 漏的边界, 替代方案:

Topic: {topic}
Context: {context}
Files: {files}

请输出 120 字以内 markdown 列表:
- ROI: 该不该做
- 漏的边界 (audit/dup/empty/timeout)
- 简化路径 (有没有 30min 就能解决的版本)
- 替代方案 (如果完全不做这个, 用别的方式解决)""",

    "propose-alt": """方案设计独立 alternative (Dual Design). 视角: 独立 senior architect.

Claude 已经有方案 A, 请你独立思考方案 B 不偏 Claude 思路:

Topic: {topic}
Claude 的方案 A:
{my_plan}

请输出 150 字 markdown:
- 方案 B 描述 (不要复述 A)
- 工程量
- 跟 A 的核心差异
- A vs B 在工程量/质量/风险三维度对比
- 你的推荐 (A / B / 融合)""",

    "review-code": """代码落地审查 (Mid-write Review). 视角: 严格的 code reviewer.

读这些文件/段落, 找:
- syntax / type / logic bug
- edge case (None/NaN/empty/巨大 input)
- path traversal / injection / race condition
- 性能问题 (重复 LLM call / loop 嵌套)

Topic: {topic}
Files: {files}
Context: {context}

请输出 150 字 markdown 严重度 列表 (High/Medium/Low).""",

    "final-qa": """ship 完交付 QA. 视角: 端到端验收.

Topic: {topic}
Files changed: {files}
Context: {context}

跑端到端 sanity check, 然后报告:
- syntax check pass/fail
- mock data unit test (你能想到的最严苛 case)
- regression risk (历史 run 数据会不会被破坏)
- ROADMAP / ship_log 是否同步更新

判断 ship 是否真的成功. 100 字 markdown.""",
}


def _load_env():
    env_path = Path.home() / "telegram-claude-bot" / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        k, v = k.strip(), v.strip().strip('"').strip("'")
        if k and k not in os.environ:
            os.environ[k] = v


def _load_history() -> dict:
    if HISTORY_PATH.exists():
        try:
            return json.loads(HISTORY_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"version": 1, "ccp_version": "1.0", "entries": []}


def _save_history(h: dict) -> None:
    HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    HISTORY_PATH.write_text(json.dumps(h, ensure_ascii=False, indent=2), encoding="utf-8")


def _run_codex(prompt: str, timeout: int = DEFAULT_TIMEOUT) -> str:
    """调 codex exec 拿输出."""
    cmd = ["codex", "exec", "--skip-git-repo-check", prompt]
    t0 = time.time()
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        dur = time.time() - t0
        if result.returncode != 0:
            return f"[codex error rc={result.returncode}] {result.stderr[-500:]}"
        # codex 输出含 prompt echo + meta, 抓 codex 块
        out = result.stdout
        # 从 "codex\n" 标记开始或者直接 strip
        if "\ncodex\n" in out:
            out = out.split("\ncodex\n", 1)[-1]
        return out.strip()[:3000]
    except subprocess.TimeoutExpired:
        return f"[codex timeout {timeout}s]"
    except Exception as e:
        return f"[codex exception] {e}"


def _record_entry(stage: str, topic: str, context: str, files: str, codex_output: str) -> None:
    h = _load_history()
    h.setdefault("entries", []).append({
        "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "stage": stage,
        "topic": topic,
        "context": context[:500],
        "files": files,
        "codex_output": codex_output,
    })
    _save_history(h)


def run_stage(stage: str, topic: str, context: str, files: str, my_plan: str = "") -> str:
    tpl = STAGE_PROMPTS.get(stage)
    if not tpl:
        return f"unknown stage: {stage}"
    prompt = tpl.format(
        topic=topic or "(none)",
        context=context or "(none)",
        files=files or "(none)",
        my_plan=my_plan or "(none)",
    )
    print(f"=== Codex CCP {stage} · topic={topic[:40]} ===")
    print(f"calling codex (timeout {DEFAULT_TIMEOUT}s)...")
    output = _run_codex(prompt)
    print(f"\nCodex 输出:\n{output}\n")
    _record_entry(stage, topic, context, files, output)
    return output


def show_history(last: int = 10) -> None:
    h = _load_history()
    entries = (h.get("entries") or [])[-last:]
    print(f"=== CCP 协同历史 (最近 {len(entries)} 条 / 共 {len(h.get('entries') or [])} 条) ===\n")
    for e in entries:
        print(f"[{e['timestamp']}] {e['stage']:12} · {e['topic'][:50]}")
        out = e.get("codex_output", "")[:200].replace("\n", " ")
        print(f"  → {out}")
        print()


def main():
    _load_env()
    ap = argparse.ArgumentParser(description="Claude × Codex 协同协议 (CCP) 工具")
    sub = ap.add_subparsers(dest="stage", required=True)

    for s in ("review-spec", "propose-alt", "review-code", "final-qa"):
        sp = sub.add_parser(s, help=f"CCP Stage {list(STAGE_PROMPTS).index(s) + 1}")
        sp.add_argument("--topic", required=True, help="需求/bug 简述")
        sp.add_argument("--context", default="", help="背景描述 (root cause/约束)")
        sp.add_argument("--files", default="", help="相关文件路径或行号")
        if s == "propose-alt":
            sp.add_argument("--my-plan", default="", help="Claude 的方案 A 描述")

    hp = sub.add_parser("history", help="查看协同历史")
    hp.add_argument("--last", type=int, default=10)

    args = ap.parse_args()
    if args.stage == "history":
        show_history(args.last)
        return

    my_plan = getattr(args, "my_plan", "") or ""
    run_stage(args.stage, args.topic, args.context, args.files, my_plan)


if __name__ == "__main__":
    main()
