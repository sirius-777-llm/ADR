#!/usr/bin/env python3
"""达尔文 R4 (2026-05-26): Batch 演化 Runner.

闭环达尔文进化：
  1. 读 topic_recommender 的 elite 题材模式
  2. LLM 基于 elite 模式生成 N 个**新**题材 (变异)
  3. 自动跑 ADR (选择)
  4. 跑完自动 evolve_ips + learn_audit_blacklist (遗传)
  5. TG 推送进度 + 最终 fitness 报告

防爆控:
  · 默认 N=1, --count 显式设
  · 每个 topic 跑前 ADR 自带 Hard Abort 拦高危
  · Smart Abort 失败率 >50% 自动 kill

用法:
  python3 tools/evolve_runner.py             # 跑 1 个 elite-pattern 新题材
  python3 tools/evolve_runner.py --count 3   # 跑 3 个
  python3 tools/evolve_runner.py --dry-run   # 只生成 topics，不跑
  python3 tools/evolve_runner.py --topic "..."  # 跳过 LLM 用指定 topic
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
    os.environ.setdefault("TG_BOT_TOKEN", os.environ.get("TELEGRAM_TOKEN", ""))
    os.environ.setdefault("TG_CHAT_ID", os.environ.get("OWNER_CHAT_ID", ""))


def get_elite_inspire() -> tuple[list[str], list[str]]:
    """从 topic_recommender 取 elite 关键词 + failed 关键词."""
    sys.path.insert(0, str(ROOT / "tools"))
    from topic_recommender import scan_run_fitness, find_elite_patterns, find_failed_patterns  # noqa
    runs = scan_run_fitness()
    elite = find_elite_patterns(runs)
    failed = find_failed_patterns(runs)
    # high confidence 优先
    elite_kw: list[str] = []
    for p in elite:
        if p.get("confidence") == "high":
            elite_kw.extend(p.get("signature", "").split("+"))
        if len(elite_kw) >= 10:
            break
    failed_kw: list[str] = []
    for p in failed[:3]:
        failed_kw.extend(p.get("signature", "").split("+"))
    return list(dict.fromkeys(elite_kw))[:10], list(dict.fromkeys(failed_kw))[:8]


def _validate_topics(raw_list, n: int) -> list[str]:
    """codex fix: 验证 LLM 输出 topics list (str type + length + dedup + 基本长度)."""
    if not isinstance(raw_list, list):
        return []
    seen = set()
    valid = []
    for item in raw_list:
        if not isinstance(item, str):
            continue
        s = item.strip()
        if not s or len(s) < 20 or len(s) > 300:
            continue
        if s in seen:
            continue
        seen.add(s)
        valid.append(s)
    return valid[:n]


def llm_generate_new_topic(elite_kw: list[str], failed_kw: list[str], n: int = 1) -> list[str]:
    """LLM 基于 elite 模式生成 N 个新题材 (变异)."""
    sys.argv = ["evolve_runner", "evolve", "h", "--adsd"]
    sys.path.insert(0, str(ROOT))
    import run_adr_v8 as adr  # noqa
    prompt = f"""你是 ADR 题材策展人。基于以下达尔文进化数据，生成 {n} 个新题材。

历史 elite 模式关键词 (跑这类题材通过率 >80%):
{', '.join(elite_kw) if elite_kw else '(暂无数据)'}

历史 failed 模式关键词 (避免):
{', '.join(failed_kw) if failed_kw else '(暂无)'}

要求:
1. 新题材必须是「未跑过」的题材 (避开 elite 关键词的字面组合, 但保持气质)
2. 题材气质继承 elite (古典/虚构/历史/武侠/神话/文学/品鉴)
3. 严禁含现代真人 + 商标 + 品牌 + 政治领导人
4. 每个 60-100 字, 含 6-8 个关键概念 (情节钩子 / 武戏密度 / 情感主线)
5. 输出严格 JSON: {{"topics": ["topic1", "topic2", ...]}}

只输出 JSON 不解释。"""
    try:
        raw = adr.chat("GEMINI_25_FLASH", "你只输出严格 JSON。", prompt, max_tokens=800, timeout=60)
        obj = adr._extract_json_object(raw) if hasattr(adr, "_extract_json_object") else None
        if not obj:
            start = raw.find("{"); end = raw.rfind("}")
            obj = json.loads(raw[start:end+1]) if start >= 0 else {}
        topics_raw = obj.get("topics") if isinstance(obj, dict) else None
        topics = _validate_topics(topics_raw, n)
        if topics:
            return topics
        print(f"LLM 输出验证失败 (got {len(topics_raw) if isinstance(topics_raw, list) else 'invalid'})")
    except Exception as e:
        print(f"LLM 生成题材失败: {e}")
    return []


def run_adr(topic: str, timeout_sec: int = 3600) -> bool:
    """调 run_adr_v8.py 跑 1 个题材, 返回 success."""
    print(f"\n=== 跑 ADR: {topic[:60]}... (timeout {timeout_sec}s) ===")
    env = os.environ.copy()
    # codex fix: 用 sys.executable 替代 hardcoded /opt/homebrew/bin/python3
    cmd = [sys.executable, "run_adr_v8.py", topic, "h", "--adsd", "--skip-approval"]
    t0 = time.time()
    try:
        result = subprocess.run(cmd, env=env, cwd=str(ROOT), capture_output=True, text=True, timeout=timeout_sec)
        dur = time.time() - t0
        print(f"  返回 {result.returncode}, {dur/60:.1f} min")
        if result.returncode != 0:
            tail = (result.stderr or result.stdout)[-500:]
            print(f"  错误尾: {tail}")
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"  TIMEOUT (>{timeout_sec/60:.0f}min)")
        return False


def apply_evolution_feedback() -> None:
    """跑完后自动 evolve_ips + learn_audit_blacklist (闭环)."""
    print("\n=== 闭环反馈：自动 evolve_ips ===")
    # codex fix: feedback subprocess 加 timeout
    subprocess.run([sys.executable, str(ROOT / "tools" / "evolve_ips.py")], cwd=str(ROOT), timeout=300)
    print("\n=== 闭环反馈：自动 learn_audit_blacklist ===")
    subprocess.run([sys.executable, str(ROOT / "tools" / "learn_audit_blacklist.py")], cwd=str(ROOT), timeout=600)


def main():
    _load_env()

    # codex fix: argparse 替代手 parse, 类型验证 + range check
    ap = argparse.ArgumentParser(description="达尔文 R4 · Batch 演化 Runner")
    ap.add_argument("--count", type=int, default=1, choices=range(1, 6), metavar="[1-5]",
                    help="生成 + 跑的题材数 (1-5, 防 credits 爆炸)")
    ap.add_argument("--dry-run", action="store_true", help="只生成题材不跑")
    ap.add_argument("--topic", type=str, default=None, help="跳过 LLM 用指定 topic")
    ap.add_argument("--max-hours", type=float, default=float(os.environ.get("ADR_EVOLVE_MAX_HOURS", "2.0")),
                    help="全局时间上限 (小时, 防失控)")
    args = ap.parse_args()

    count = args.count
    dry_run = args.dry_run
    forced_topic = args.topic
    # 每 run timeout = max_hours / count
    per_run_timeout = int(max(600, args.max_hours * 3600 / max(1, count)))

    print(f"=== 达尔文 R4 · Batch 演化 Runner ===")
    print(f"  count={count} dry_run={dry_run} max_hours={args.max_hours} per_run_timeout={per_run_timeout}s")

    # Step 1: 生成新题材
    if forced_topic:
        topics = [forced_topic]
    else:
        elite_kw, failed_kw = get_elite_inspire()
        print(f"\nElite 关键词 ({len(elite_kw)}): {', '.join(elite_kw[:8])}")
        print(f"Failed 关键词 ({len(failed_kw)}): {', '.join(failed_kw[:5])}")
        topics = llm_generate_new_topic(elite_kw, failed_kw, count)
        if not topics:
            print("LLM 题材生成失败, exit")
            sys.exit(1)
        print(f"\nLLM 生成 {len(topics)} 个新题材 (变异):")
        for i, t in enumerate(topics):
            print(f"  {i+1}. {t}")

    if dry_run:
        print("\ndry_run 不跑 ADR, exit")
        return

    # Step 2: 跑 ADR
    results = []
    total_start = time.time()
    for i, topic in enumerate(topics):
        # 全局时间上限 cap
        elapsed = time.time() - total_start
        if elapsed > args.max_hours * 3600:
            print(f"\n⏰ 全局上限 {args.max_hours}h 超时, 剩余 topic 跳过")
            break
        print(f"\n>>> Topic {i+1}/{len(topics)} <<<")
        ok = run_adr(topic, timeout_sec=per_run_timeout)
        results.append({"topic": topic, "ok": ok})

    # Step 3: 闭环反馈
    apply_evolution_feedback()

    # Final report
    succ = sum(1 for r in results if r["ok"])
    print(f"\n=== 完成: {succ}/{len(results)} 个 topic 成功 ===")
    for r in results:
        flag = "✓" if r["ok"] else "❌"
        print(f"  {flag} {r['topic'][:70]}")


if __name__ == "__main__":
    main()
