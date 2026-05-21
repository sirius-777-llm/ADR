#!/usr/bin/env python3
"""Speaker IP 调用统计 + 推荐 (F)

用法:
  python3 tools/show_ip_stats.py             # 全库热度排行
  python3 tools/show_ip_stats.py 曹操         # 单 IP 详情 + 推荐相关 IP
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

env_path = Path.home() / "telegram-claude-bot" / ".env"
if env_path.exists():
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        k, v = k.strip(), v.strip().strip('"').strip("'")
        if k and k not in os.environ:
            os.environ[k] = v
if "TG_BOT_TOKEN" not in os.environ and "TELEGRAM_TOKEN" in os.environ:
    os.environ["TG_BOT_TOKEN"] = os.environ["TELEGRAM_TOKEN"]
if "TG_CHAT_ID" not in os.environ and "OWNER_CHAT_ID" in os.environ:
    os.environ["TG_CHAT_ID"] = os.environ["OWNER_CHAT_ID"]

_real_args = list(sys.argv[1:])
sys.argv = ["show_ip_stats.py", "ip_stats", "h", "--adsd"]
sys.path.insert(0, str(ROOT))
import run_adr_v8 as adr  # noqa
sys.argv = ["show_ip_stats.py"] + _real_args


def show_all():
    stats = adr._ip_usage_stats()
    if not stats:
        print("IP 库为空")
        return
    print(f"\n=== Speaker IP 库热度排行（共 {len(stats)} 个 IP）===\n")
    print(f"{'#':>2}  {'speaker':<12} {'usage':>5}  {'turn 累计':>8}  {'era':<24}")
    print("-" * 70)
    for i, s in enumerate(stats, 1):
        print(f"{i:>2}  {s['speaker']:<12} {s['usage_count']:>5}  {s['history_turn_count']:>8}  {s['era']:<24}")
    total_runs = sum(s['usage_count'] for s in stats)
    total_turns = sum(s['history_turn_count'] for s in stats)
    print("-" * 70)
    print(f"    总 IP run: {total_runs}    总 turn 累计: {total_turns}")


def show_one(speaker: str):
    ip = adr._match_speaker_ip(speaker)
    if not ip:
        print(f"未找到 IP「{speaker}」(包括 alias 模糊匹配)")
        return
    print(f"\n=== Speaker IP · {ip.get('speaker')} ===\n")
    print(f"aliases:       {ip.get('aliases', [])}")
    print(f"era:           {ip.get('era')}")
    print(f"voice_asset:   {ip.get('voice_asset_id')}")
    print(f"voice_gender:  {ip.get('voice_gender')}")
    print(f"usage_count:   {ip.get('usage_count', 0)}")
    print(f"history turn:  {len(ip.get('usage_history') or [])}")
    print(f"schema_ver:    {ip.get('schema_version', '?')}")
    print(f"personality:   {ip.get('personality', [])}")
    print(f"catchphrases:  {ip.get('catchphrases', [])[:3]}")
    history = ip.get("usage_history") or []
    if history:
        recent_topics = list(dict.fromkeys(h.get("topic", "") for h in history if h.get("topic")))[-5:]
        print(f"recent topics: {recent_topics}")
    print()

    recommendations = adr._recommend_related_ips(ip.get("speaker"))
    if recommendations:
        print(f"=== 推荐相关 IP (基于 relationships + usage_count) ===\n")
        for r in recommendations:
            print(f"  · {r['speaker']:<12} (usage {r['usage_count']:>2})  {r['era']:<24}")
            print(f"      关系: {r['relation_label']}")
    else:
        print("（无 relationships 信息，无法推荐）")


def main():
    if len(sys.argv) < 2:
        show_all()
    else:
        show_one(sys.argv[1])


if __name__ == "__main__":
    main()
