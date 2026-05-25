#!/usr/bin/env python3
"""达尔文 Round 2 · 阶段 E (2026-05-25): 自动 IP 进化.

每 IP 根据 usage_history 算 historical_success_rate:
  · <60% 低分 → 自动重孵化 (删 cache + 标 needs_reincubate)
  · >=90% 高分 → 标 production_ready (锁定不改)
  · 60-89% → 保持

用法:
  python3 tools/evolve_ips.py            # 评估 + 应用 (默认)
  python3 tools/evolve_ips.py --dry-run  # 只评估不改
  python3 tools/evolve_ips.py --show     # 只展示当前 IP fitness
"""
import json
import os
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IP_DIR = ROOT / "voice_assets" / "speaker_ips"
GRID_DIR = ROOT / "voice_assets" / "character_meta_grids"


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


def gather_run_qa() -> dict[str, dict]:
    """从所有 run 的 lip_sync_qa.json 提 per-speaker 通过/失败次数."""
    by_speaker_run: dict[str, dict[str, dict]] = defaultdict(dict)
    for d in sorted(Path("/tmp").glob("adr_v8_*")):
        qa_path = d / "lip_sync_qa.json"
        state_path = d / "pipeline_state.json"
        if not qa_path.exists():
            continue
        try:
            qa = json.loads(qa_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        script_turns = []
        if state_path.exists():
            try:
                ps = json.loads(state_path.read_text(encoding="utf-8"))
                script_turns = ps.get("script") or []
            except Exception:
                pass
        for r in qa.get("records", []):
            turn_idx = int(r.get("turn", 0)) - 1
            sp = r.get("speaker", "") or (script_turns[turn_idx].get("speaker", "") if 0 <= turn_idx < len(script_turns) else "")
            sp = (sp or "").strip()
            if not sp or sp in ("(silent)", "(action)"):
                continue
            d_name = d.name
            stat = by_speaker_run[sp].setdefault(d_name, {"pass": 0, "fail": 0})
            if r.get("pass"):
                stat["pass"] += 1
            else:
                stat["fail"] += 1
    return by_speaker_run


def compute_fitness(per_speaker: dict[str, dict]) -> dict[str, dict]:
    """每个 IP 算 historical_success_rate."""
    out = {}
    for sp, runs in per_speaker.items():
        total_pass = sum(r["pass"] for r in runs.values())
        total_fail = sum(r["fail"] for r in runs.values())
        total = total_pass + total_fail
        if total == 0:
            continue
        rate = total_pass / total
        out[sp] = {
            "total_attempts": total,
            "pass": total_pass,
            "fail": total_fail,
            "success_rate": round(rate * 100, 1),
            "runs_count": len(runs),
        }
    return out


def evolve(dry_run: bool = False) -> dict:
    """应用进化决策."""
    by_speaker = gather_run_qa()
    fitness = compute_fitness(by_speaker)

    actions = {"reincubate": [], "production_ready": [], "kept": []}
    for ip_path in sorted(IP_DIR.glob("*.json")):
        try:
            ip = json.loads(ip_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        sp = ip.get("speaker", ip_path.stem)
        f = fitness.get(sp)
        if not f:
            continue  # 没历史数据
        rate = f["success_rate"]
        ip["fitness_score"] = rate
        ip["fitness_total_attempts"] = f["total_attempts"]
        ip["fitness_last_evaluated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 至少 6 attempt 才有显著性 (避免新 IP 1-2 次失败就被标低分)
        if f["total_attempts"] < 6:
            actions["kept"].append((sp, rate, "insufficient_data"))
            if not dry_run:
                ip_path.write_text(json.dumps(ip, ensure_ascii=False, indent=2), encoding="utf-8")
            continue

        if rate < 60:
            ip["needs_reincubate"] = True
            ip.pop("qa_status", None)
            actions["reincubate"].append((sp, rate))
            # 删 cached meta_grid
            grid_path = GRID_DIR / f"{sp}.png"
            if not dry_run and grid_path.exists():
                grid_path.unlink()
            # 清 template cache
            if not dry_run:
                ip["meta_grid_template_cache"] = {}
        elif rate >= 90:
            ip["production_ready"] = True
            ip.pop("needs_reincubate", None)
            actions["production_ready"].append((sp, rate))
        else:
            actions["kept"].append((sp, rate, "viable"))
            ip.pop("needs_reincubate", None)

        if not dry_run:
            ip_path.write_text(json.dumps(ip, ensure_ascii=False, indent=2), encoding="utf-8")

    return {"fitness": fitness, "actions": actions, "dry_run": dry_run}


def main():
    _load_env()
    if "--show" in sys.argv:
        per = gather_run_qa()
        fit = compute_fitness(per)
        print(f"\n=== Speaker IP Fitness (从 {len(per)} 个 IP 跨 run 统计) ===\n")
        for sp, f in sorted(fit.items(), key=lambda x: x[1]["success_rate"], reverse=True):
            print(f"  {sp:14} {f['success_rate']:>5.1f}% ({f['pass']}/{f['total_attempts']}) 跨 {f['runs_count']} run")
        return

    dry = "--dry-run" in sys.argv
    result = evolve(dry_run=dry)
    actions = result["actions"]
    print(f"\n=== 自动 IP 进化结果 (dry_run={dry}) ===\n")
    if actions["production_ready"]:
        print(f"🏆 production_ready ({len(actions['production_ready'])}):")
        for sp, rate in actions["production_ready"]:
            print(f"  · {sp:14} {rate}%")
    if actions["reincubate"]:
        print(f"\n🔄 需重孵化 ({len(actions['reincubate'])}):")
        for sp, rate in actions["reincubate"]:
            print(f"  · {sp:14} {rate}% (低分 < 60%)")
        if dry:
            print("  (dry-run 没动文件，去掉 --dry-run 应用)")
    if actions["kept"]:
        print(f"\n🟢 保持 ({len(actions['kept'])}):")
        for sp, rate, reason in actions["kept"]:
            print(f"  · {sp:14} {rate}% ({reason})")


if __name__ == "__main__":
    main()
