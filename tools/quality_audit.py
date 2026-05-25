#!/usr/bin/env python3
"""ADR 质量评分工具 (达尔文进化数据源).

扫所有 /tmp/adr_v8_*/lip_sync_qa.json + pipeline_state.json
统计每 run 的质量信号 → 输出趋势 markdown 看改进收敛曲线

用法:
  python3 tools/quality_audit.py                # 全 run 汇总
  python3 tools/quality_audit.py --last 10      # 最近 10 个 run
  python3 tools/quality_audit.py --md > /tmp/quality_report.md   # 输出 markdown
"""
import json
import os
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path


def scan_runs(limit: int | None = None) -> list[dict]:
    """扫所有 ADR run output dir，返回质量记录列表"""
    runs = []
    tmp_dirs = sorted(Path("/tmp").glob("adr_v8_*"), key=lambda p: p.name)
    for d in tmp_dirs:
        qa_path = d / "lip_sync_qa.json"
        state_path = d / "pipeline_state.json"
        if not qa_path.exists():
            continue
        try:
            qa = json.loads(qa_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        run_name = d.name
        ts_match = re.search(r"adr_v8_(\d{8}_\d{6})", run_name)
        ts = ts_match.group(1) if ts_match else "?"

        # 基本通过率
        a_total = qa.get("a_roll_total", 0)
        a_pass = qa.get("a_roll_success", 0)
        b_total = qa.get("b_roll_total", 0)
        b_pass = qa.get("b_roll_success", 0)
        total = qa.get("total", 0)
        succ = qa.get("success_count", 0)

        # task_failed 原因汇总
        fail_msgs = Counter()
        action_b_total = 0
        action_b_pass = 0
        for r in qa.get("records", []):
            for a in (r.get("attempts") or []):
                reason = str(a.get("reason", ""))
                if "task_failed" in reason:
                    # 抽 msg 部分
                    msg_part = reason.split("task_failed:", 1)[-1].strip()[:60] if "task_failed:" in reason else "(unknown)"
                    fail_msgs[msg_part] += 1
                resp = a.get("response") or {}
                if isinstance(resp, dict) and resp.get("msg"):
                    fail_msgs[str(resp["msg"])[:60]] += 1
            # action_b 统计
            variants = [a.get("variant", "") for a in (r.get("attempts") or [])]
            if any("action_b" in v for v in variants):
                action_b_total += 1
                if r.get("pass"):
                    action_b_pass += 1

        # topic from pipeline_state
        topic = ""
        if state_path.exists():
            try:
                ps = json.loads(state_path.read_text(encoding="utf-8"))
                topic = (ps.get("topic") or "")[:50]
            except Exception:
                pass

        # codex 审查 fix (2026-05-25): fitness 公式去重权
        # 原 pass + fallback_inv 同源双重计权 → 改用 4 个独立信号
        fallback_count = total - succ if total else 0
        pass_rate = succ / total if total else 0

        # audit 严重度: 0 fail=10pt / 1-3 fail=5pt / 4-8 fail=2pt / 9+=0pt
        audit_fail_count = sum(fail_msgs.values())
        if audit_fail_count == 0:
            audit_severity_score = 10
        elif audit_fail_count <= 3:
            audit_severity_score = 5
        elif audit_fail_count <= 8:
            audit_severity_score = 2
        else:
            audit_severity_score = 0

        # action_b 处理: 无 action_b 算 0.5 (中性) 而非 1.0 (虚高)
        # 这避免「没武戏题材」白拿满分
        if action_b_total > 0:
            action_rate = action_b_pass / action_b_total
        else:
            action_rate = 0.5

        # 加权 fitness score (0-100) - 4 独立信号:
        #   50% 通过率 (主信号)
        #   15% action_b 通过率
        #   15% 单次重试效率 (records 长度均值: < 2 次 attempt = 10pt, > 3 次 = 0pt)
        #   20% audit 严重度
        avg_attempts = 0.0
        if qa.get("records"):
            attempt_counts = [len(r.get("attempts") or []) for r in qa["records"]]
            avg_attempts = sum(attempt_counts) / len(attempt_counts) if attempt_counts else 0
        retry_efficiency_score = max(0.0, min(10.0, 10.0 - max(0.0, avg_attempts - 1.5) * 5))

        fitness_score = round(
            pass_rate * 50 +
            action_rate * 15 +
            (retry_efficiency_score / 10) * 15 +
            (audit_severity_score / 10) * 20,
            1,
        )

        runs.append({
            "run": run_name,
            "ts": ts,
            "topic": topic,
            "total": total,
            "pass_count": succ,
            "pass_rate": pass_rate,
            "a_roll": (a_pass, a_total),
            "b_roll": (b_pass, b_total),
            "action_b": (action_b_pass, action_b_total),
            "fallback_count": fallback_count,
            "audit_fail_count": audit_fail_count,
            "fitness_score": fitness_score,
            "fail_msgs": dict(fail_msgs.most_common(5)),
        })
    if limit:
        runs = runs[-limit:]
    return runs


def _fitness_band(score: float) -> str:
    """达尔文 R1 (2026-05-25): fitness score → 级别标签."""
    if score >= 85:
        return "🏆 elite"
    if score >= 70:
        return "✨ strong"
    if score >= 50:
        return "🟢 viable"
    if score >= 30:
        return "🟡 weak"
    return "🔴 failed"


def print_table(runs: list[dict], markdown: bool = False, threshold: float = 0) -> None:
    # 阶段 A: --threshold 过滤进化失败 run
    if threshold > 0:
        runs = [r for r in runs if r.get("fitness_score", 0) >= threshold]

    if markdown:
        print("# ADR Quality Audit Report")
        print(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"\nTotal runs scanned: {len(runs)}")
        print()
        print("| Run | Topic | Fit | Band | Pass | A-roll | B-roll | action_b | Top fail |")
        print("|---|---|---|---|---|---|---|---|---|")
    else:
        print(f"{'Run':25} {'Fit':>5} {'Band':>10} {'Pass':>8} {'A-roll':>7} {'B-roll':>7} {'act_b':>7} Topic")
        print("-" * 130)

    for r in runs:
        ap, at = r["a_roll"]
        bp, bt = r["b_roll"]
        ap_act, at_act = r["action_b"]
        topic_short = r["topic"][:30] if r["topic"] else "?"
        top_fail = ""
        if r["fail_msgs"]:
            top_fail = list(r["fail_msgs"].keys())[0]
        fit = r.get("fitness_score", 0)
        band = _fitness_band(fit)
        if markdown:
            print(f"| {r['ts']} | {topic_short} | {fit} | {band} | {r['pass_count']}/{r['total']} ({r['pass_rate']*100:.0f}%) | "
                  f"{ap}/{at} | {bp}/{bt} | {ap_act}/{at_act} | {top_fail} |")
        else:
            print(f"{r['ts']:25} {fit:>5.1f} {band:>10} {r['pass_count']:>3}/{r['total']:<3} {ap}/{at:<5} {bp}/{bt:<5} {ap_act}/{at_act:<5} {topic_short}")

    if markdown:
        # 趋势：累计失败原因 top 5
        all_fails = Counter()
        for r in runs:
            for msg, ct in r["fail_msgs"].items():
                all_fails[msg] += ct
        print(f"\n## Top failure reasons across {len(runs)} runs\n")
        print("| Reason | Count |")
        print("|---|---|")
        for msg, ct in all_fails.most_common(10):
            print(f"| {msg or '(none)'} | {ct} |")

        # 改进趋势：前后期对比 (用 fitness_score 而非 pass_rate)
        if len(runs) >= 4:
            half = len(runs) // 2
            early = runs[:half]
            late = runs[half:]
            early_fit = sum(r["fitness_score"] for r in early) / len(early) if early else 0
            late_fit = sum(r["fitness_score"] for r in late) / len(late) if late else 0
            print(f"\n## Fitness 进化趋势\n")
            print(f"- First half avg fitness: **{early_fit:.1f}**")
            print(f"- Latest half avg fitness: **{late_fit:.1f}**")
            print(f"- Delta: **{late_fit - early_fit:+.1f}** ({_fitness_band(late_fit)} vs {_fitness_band(early_fit)})")
            # Top 5 elite run
            elite_runs = sorted(runs, key=lambda r: r["fitness_score"], reverse=True)[:5]
            print(f"\n## Top 5 Elite Runs\n")
            print("| Run | Topic | Fitness | Band |")
            print("|---|---|---|---|")
            for r in elite_runs:
                print(f"| {r['ts']} | {r['topic'][:35]} | {r['fitness_score']} | {_fitness_band(r['fitness_score'])} |")


def main():
    md = "--md" in sys.argv
    limit = None
    threshold = 0.0
    if "--last" in sys.argv:
        i = sys.argv.index("--last")
        if i + 1 < len(sys.argv):
            limit = int(sys.argv[i + 1])
    if "--threshold" in sys.argv:
        i = sys.argv.index("--threshold")
        if i + 1 < len(sys.argv):
            threshold = float(sys.argv[i + 1])
    runs = scan_runs(limit=limit)
    if not runs:
        print("No ADR runs found in /tmp/adr_v8_*")
        sys.exit(1)
    print_table(runs, markdown=md, threshold=threshold)


if __name__ == "__main__":
    main()
