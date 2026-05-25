#!/usr/bin/env python3
"""达尔文 R3 (2026-05-26): 题材推荐器.

基于历史 quality_audit fitness 数据自动识别 elite 题材模式 (>=80 分)
+ 给用户推荐「这类题材跑通率高」、避开「这类反复失败」.

这是达尔文「适者生存」的终极体现 — 系统自己学会做什么.

用法:
  python3 tools/topic_recommender.py            # 输出推荐报告
  python3 tools/topic_recommender.py --md       # markdown 输出
  python3 tools/topic_recommender.py --next     # 推荐下一个跑的题材
"""
import os
import re
import sys
from collections import defaultdict
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


def scan_run_fitness() -> list[dict]:
    """复用 quality_audit 的 scan_runs 拿 fitness + topic."""
    sys.path.insert(0, str(ROOT / "tools"))
    from quality_audit import scan_runs  # noqa
    return scan_runs()


def topic_signature(topic: str) -> set[str]:
    """提取 topic 关键词 (用于聚类相似题材).
    codex 审查 fix: 用 sliding window 不漏「国电」类 + 整段中文 span 提取."""
    stops = {"的", "与", "和", "在", "之", "者", "了", "是", "对", "及", "或", "等", "之间", "之中"}
    tokens = set()
    # 先抽连续中文 span
    spans = re.findall(r"[一-鿿]+", topic)
    for span in spans:
        # sliding window n=2,3,4
        for n in (2, 3, 4):
            if len(span) < n:
                continue
            for i in range(len(span) - n + 1):
                t = span[i:i+n]
                if not any(s in t for s in stops):
                    tokens.add(t)
    return tokens


def _jaccard(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0


def cluster_topics(runs: list[dict]) -> list[dict]:
    """codex 审查 fix: Jaccard 相似度 + connected-components 聚类，避免 lexicographic 错位.

    返回: [{"signatures": [...], "runs": [...], "shared_keywords": [...]}]"""
    items = []
    for r in runs:
        topic = r.get("topic") or ""
        if not topic:
            continue
        sig = topic_signature(topic)
        if not sig:
            continue
        items.append({"run": r, "sig": sig, "topic": topic})

    # Union-Find by Jaccard >= 0.3
    n = len(items)
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x, y):
        rx, ry = find(x), find(y)
        if rx != ry:
            parent[rx] = ry

    JACCARD_THRESHOLD = 0.3
    for i in range(n):
        for j in range(i + 1, n):
            if _jaccard(items[i]["sig"], items[j]["sig"]) >= JACCARD_THRESHOLD:
                union(i, j)

    clusters: dict[int, list[dict]] = defaultdict(list)
    for i, it in enumerate(items):
        clusters[find(i)].append(it)

    out = []
    for cluster_items in clusters.values():
        runs_in_cluster = [it["run"] for it in cluster_items]
        # cluster shared keywords: 交集前 4 个
        common = set.intersection(*(it["sig"] for it in cluster_items)) if len(cluster_items) > 1 else cluster_items[0]["sig"]
        # 选有意义的关键词 (3-4 字优先)
        kw_sorted = sorted(common, key=lambda x: (-len(x), x))[:4]
        out.append({
            "keywords": kw_sorted,
            "runs": runs_in_cluster,
        })
    return out


def _patterns_from_clusters(clusters: list[dict], reverse_fit: bool = True) -> list[dict]:
    """codex 审查 fix: count >= 2 才算 confident pattern, 1-run 标 low_confidence."""
    patterns = []
    for c in clusters:
        items = c["runs"]
        avg_fit = sum(r["fitness_score"] for r in items) / len(items) if items else 0
        patterns.append({
            "signature": "+".join(c["keywords"]) or "(无共同关键词)",
            "count": len(items),
            "avg_fitness": round(avg_fit, 1),
            "confidence": "high" if len(items) >= 2 else "low",
            "sample_topics": [r["topic"][:60] for r in items[:3]],
        })
    patterns.sort(
        key=lambda x: (x["count"], x["avg_fitness"] if reverse_fit else -x["avg_fitness"]),
        reverse=True,
    )
    return patterns


def find_elite_patterns(runs: list[dict], threshold: float = 80) -> list[dict]:
    elite_runs = [r for r in runs if r.get("fitness_score", 0) >= threshold]
    return _patterns_from_clusters(cluster_topics(elite_runs), reverse_fit=True)


def find_failed_patterns(runs: list[dict], threshold: float = 30) -> list[dict]:
    failed_runs = [r for r in runs if r.get("fitness_score", 0) < threshold]
    return _patterns_from_clusters(cluster_topics(failed_runs), reverse_fit=False)


def _md_escape(s: str) -> str:
    """codex 审查 fix: markdown 表格 cell 转义 `|` 防破表."""
    return str(s).replace("|", "\\|").replace("\n", " ")


def recommend_next_topic(elite: list[dict], failed: list[dict]) -> str:
    """给一个新题材建议 (从 elite 取 inspire, 避 failed 关键词)."""
    if not elite:
        return "暂无足够 elite 数据 (需至少 1 个 fitness >= 80 run)"
    top = elite[0]
    avoid_words = set()
    for p in failed[:3]:
        avoid_words.update(p["signature"].split("+"))
    elite_words = top["signature"].split("+")
    return (
        f"推荐方向: 跟「{'+'.join(elite_words)}」类似的题材"
        f" (平均 fitness {top['avg_fitness']}, 历史 {top['count']} run elite)。"
        f"避免词: {', '.join(sorted(avoid_words)[:5]) or '(无)'}"
    )


def main():
    _load_env()
    runs = scan_run_fitness()
    if not runs:
        print("无历史 run 数据")
        sys.exit(1)

    elite = find_elite_patterns(runs)
    failed = find_failed_patterns(runs)

    if "--next" in sys.argv:
        print(recommend_next_topic(elite, failed))
        return

    md = "--md" in sys.argv
    if md:
        print("# ADR 题材推荐报告 (达尔文 R3)")
        print(f"\n生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"\n基于 {len(runs)} 个历史 run 的 fitness 数据 (>= 80 = elite, < 30 = failed)")
        print()

    # Elite patterns
    if md:
        print(f"\n## 🏆 Elite 题材模式 (推荐做)\n")
        print("| Pattern | Count | Avg Fitness | Confidence | Sample Topics |")
        print("|---|---|---|---|---|")
        for p in elite[:8]:
            samples = _md_escape(" · ".join(p["sample_topics"]))
            print(f"| {_md_escape(p['signature'])} | {p['count']} | {p['avg_fitness']} | {p['confidence']} | {samples} |")
    else:
        print(f"\n=== 🏆 Elite 题材模式 (fitness >= 80, 推荐做) ===")
        for p in elite[:8]:
            conf_tag = "" if p["confidence"] == "high" else "  ⚠️ low-confidence (单 run)"
            print(f"  {p['signature']:30} count={p['count']:>2}  avg={p['avg_fitness']:>5.1f}{conf_tag}")
            for s in p["sample_topics"]:
                print(f"    · {s}")

    # Failed patterns
    if md:
        print(f"\n## 🔴 Failed 题材模式 (避免)\n")
        print("| Pattern | Count | Avg Fitness | Confidence | Sample Topics |")
        print("|---|---|---|---|---|")
        for p in failed[:5]:
            samples = _md_escape(" · ".join(p["sample_topics"]))
            print(f"| {_md_escape(p['signature'])} | {p['count']} | {p['avg_fitness']} | {p['confidence']} | {samples} |")
    else:
        print(f"\n=== 🔴 Failed 题材模式 (fitness < 30, 避免) ===")
        for p in failed[:5]:
            conf_tag = "" if p["confidence"] == "high" else "  ⚠️ low-confidence (单 run)"
            print(f"  {p['signature']:30} count={p['count']:>2}  avg={p['avg_fitness']:>5.1f}{conf_tag}")
            for s in p["sample_topics"]:
                print(f"    · {s}")

    if md:
        print(f"\n## 🎯 下一题材建议\n")
        print(f"> {recommend_next_topic(elite, failed)}")
    else:
        print(f"\n=== 🎯 下一题材建议 ===")
        print(f"  {recommend_next_topic(elite, failed)}")


if __name__ == "__main__":
    main()
