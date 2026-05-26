#!/usr/bin/env python3
"""达尔文 R5 (2026-05-26): 进化世代追踪.

记录每次 evolve_runner / ADR run 的 generation + fitness + ship 改动，
输出世代曲线看系统是否真的越来越聪明.

evolve_history.json schema:
{
  "version": 1,
  "generations": [
    {
      "gen": 1,
      "timestamp": "2026-05-25T12:00",
      "ship_events": ["B4 武戏 SFX", "meta_grid 重构"],
      "runs": [{"topic": "...", "fitness": 95}],
      "avg_fitness": 95,
      "elite_count": 1,
      "failed_count": 0,
    },
    ...
  ]
}

用法:
  python3 tools/evolution_log.py             # 输出世代曲线 (auto-generation by date)
  python3 tools/evolution_log.py --md        # markdown 输出
  python3 tools/evolution_log.py --record "ship event" # 手动记 ship 事件
"""
import json
import os
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HISTORY_PATH = ROOT / "voice_assets" / "evolution_history.json"


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


def load_history() -> dict:
    if HISTORY_PATH.exists():
        try:
            return json.loads(HISTORY_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"version": 1, "ship_log": [], "generations": []}


def save_history(h: dict) -> None:
    HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    HISTORY_PATH.write_text(json.dumps(h, ensure_ascii=False, indent=2), encoding="utf-8")


def record_ship_event(label: str) -> None:
    """手动记一次 ship 事件 (用于关联 generation 和功能 ship)."""
    h = load_history()
    # codex fix: setdefault 防老版/损坏 history 缺 ship_log 字段
    h.setdefault("ship_log", []).append({
        "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "label": label,
    })
    save_history(h)
    print(f"recorded ship event: {label}")


def _md_cell(s: str) -> str:
    """codex fix: md table cell 转义 | 防破表."""
    return str(s).replace("|", "\\|").replace("\n", " ")


def build_generations_from_history() -> list[dict]:
    """从 quality_audit 历史 run + ship_log 自动拼接 generations.

    Generation 定义: 按日期分组 (每天一个 generation)，更细可按 ship event 分组。
    """
    sys.path.insert(0, str(ROOT / "tools"))
    from quality_audit import scan_runs  # noqa
    runs = scan_runs()
    by_day: dict[str, list[dict]] = defaultdict(list)
    for r in runs:
        ts = r.get("ts", "")  # "20260525_141507"
        # codex fix: 验 ts 是 8 位日期数字, 否则跳过 (防 "?" 变 "?--")
        day = ts[:8]
        if len(day) != 8 or not day.isdigit():
            continue
        by_day[day].append(r)

    history = load_history()
    ship_by_day: dict[str, list[str]] = defaultdict(list)
    for ev in history.get("ship_log", []):
        ts = ev.get("timestamp", "")
        day = ts[:10].replace("-", "")
        ship_by_day[day].append(ev.get("label", ""))

    generations = []
    for gen_idx, day in enumerate(sorted(by_day.keys()), 1):
        day_runs = by_day[day]
        fitness_values = [r.get("fitness_score", 0) for r in day_runs]
        elite_count = sum(1 for f in fitness_values if f >= 80)
        failed_count = sum(1 for f in fitness_values if f < 30)
        avg = sum(fitness_values) / len(fitness_values) if fitness_values else 0
        date_iso = f"{day[:4]}-{day[4:6]}-{day[6:8]}"
        generations.append({
            "gen": gen_idx,
            "date": date_iso,
            "run_count": len(day_runs),
            "avg_fitness": round(avg, 1),
            "max_fitness": round(max(fitness_values, default=0), 1),
            "min_fitness": round(min(fitness_values, default=0), 1),
            "elite_count": elite_count,
            "failed_count": failed_count,
            "ship_events": ship_by_day.get(day, []),
            "sample_topics": [r["topic"][:50] for r in day_runs[:3]],
        })
    return generations


def print_evolution_curve(generations: list[dict], markdown: bool = False) -> None:
    if markdown:
        print("# ADR 达尔文进化世代曲线")
        print(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"\n共 {len(generations)} 个 generation (按日期分)")
        print()
        print("| Gen | Date | Runs | Avg Fit | Elite | Failed | Ship Events |")
        print("|---|---|---|---|---|---|---|")
        for g in generations:
            ship = _md_cell("; ".join(g["ship_events"][:3])) or "-"
            print(f"| {g['gen']} | {g['date']} | {g['run_count']} | {g['avg_fitness']} | {g['elite_count']} | {g['failed_count']} | {ship} |")
    else:
        print(f"=== 达尔文进化世代曲线 ({len(generations)} generations) ===\n")
        print(f"{'Gen':>3} {'Date':<11} {'Runs':>4} {'Avg':>5} {'Max':>5} {'Elite':>5} {'Failed':>6}  Ship")
        print("-" * 100)
        for g in generations:
            ship = "; ".join(g["ship_events"][:2])[:50] or "-"
            print(f"{g['gen']:>3} {g['date']:<11} {g['run_count']:>4} {g['avg_fitness']:>5.1f} {g['max_fitness']:>5.1f} "
                  f"{g['elite_count']:>5} {g['failed_count']:>6}  {ship}")

    # 趋势 - codex fix: run-weighted 不是 daily-equal-weighted
    if len(generations) >= 3:
        mid = len(generations) // 2
        early_gens = generations[:mid]
        late_gens = generations[mid:]

        def _weighted_avg(gens: list[dict]) -> float:
            total_score = 0.0
            total_runs = 0
            for g in gens:
                runs = g.get("run_count", 0)
                total_score += g.get("avg_fitness", 0) * runs
                total_runs += runs
            return total_score / total_runs if total_runs else 0.0

        early_avg = _weighted_avg(early_gens)
        late_avg = _weighted_avg(late_gens)
        if markdown:
            print(f"\n## 进化趋势")
            print(f"\n- 前期 avg fitness: **{early_avg:.1f}**")
            print(f"- 后期 avg fitness: **{late_avg:.1f}**")
            print(f"- Delta: **{late_avg - early_avg:+.1f}** {'📈 正向进化 ✓' if late_avg > early_avg else '📉 倒退'}")
        else:
            print(f"\n=== 进化趋势 ===")
            print(f"  前期 avg: {early_avg:.1f}")
            print(f"  后期 avg: {late_avg:.1f}")
            print(f"  Delta: {late_avg - early_avg:+.1f} {'📈 正向 ✓' if late_avg > early_avg else '📉 倒退'}")


def main():
    _load_env()
    if "--record" in sys.argv:
        i = sys.argv.index("--record")
        if i + 1 < len(sys.argv):
            record_ship_event(sys.argv[i + 1])
        else:
            print("Usage: --record \"event label\"")
        return
    md = "--md" in sys.argv
    generations = build_generations_from_history()
    if not generations:
        print("无 run 数据")
        return
    print_evolution_curve(generations, markdown=md)


if __name__ == "__main__":
    main()
