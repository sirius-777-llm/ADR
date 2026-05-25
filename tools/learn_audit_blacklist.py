#!/usr/bin/env python3
"""达尔文 Round 1 · 阶段 B (2026-05-25): Audit 黑名单自动学习.

扫所有历史 lip_sync_qa.json 提 task_failed 的 turn 对应 text/speaker/topic
→ LLM 提炼触发词聚类 → voice_assets/audit_blacklist.json

下次 script-gen 自动注入 "avoid: [words]" 让编剧避开历史触发词。

用法:
  python3 tools/learn_audit_blacklist.py            # 学习更新黑名单
  python3 tools/learn_audit_blacklist.py --show     # 只展示当前黑名单
"""
import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BLACKLIST_PATH = ROOT / "voice_assets" / "audit_blacklist.json"


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
    if "TG_BOT_TOKEN" not in os.environ and "TELEGRAM_TOKEN" in os.environ:
        os.environ["TG_BOT_TOKEN"] = os.environ["TELEGRAM_TOKEN"]
    if "TG_CHAT_ID" not in os.environ and "OWNER_CHAT_ID" in os.environ:
        os.environ["TG_CHAT_ID"] = os.environ["OWNER_CHAT_ID"]


def collect_fail_evidence() -> list[dict]:
    """扫所有 run 收集 task_failed turn 的证据 (text + speaker + topic + msg)."""
    evidence: list[dict] = []
    for d in sorted(Path("/tmp").glob("adr_v8_*")):
        qa_path = d / "lip_sync_qa.json"
        state_path = d / "pipeline_state.json"
        if not qa_path.exists():
            continue
        try:
            qa = json.loads(qa_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        topic = ""
        script_turns = []
        if state_path.exists():
            try:
                ps = json.loads(state_path.read_text(encoding="utf-8"))
                topic = (ps.get("topic") or "")[:100]
                script_turns = ps.get("script") or []
            except Exception:
                pass
        for r in qa.get("records", []):
            if r.get("pass"):
                continue
            turn_idx = int(r.get("turn", 0)) - 1
            text = ""
            speaker = r.get("speaker", "")
            if 0 <= turn_idx < len(script_turns):
                text = (script_turns[turn_idx].get("text") or "")[:120]
                speaker = speaker or script_turns[turn_idx].get("speaker", "")
            for a in (r.get("attempts") or []):
                reason = str(a.get("reason", ""))
                resp = a.get("response") or {}
                msg = ""
                if isinstance(resp, dict):
                    msg = str(resp.get("msg") or "")
                if not msg and "task_failed:" in reason:
                    msg = reason.split("task_failed:", 1)[-1].strip()
                if not msg:
                    continue
                evidence.append({
                    "run": d.name,
                    "topic": topic,
                    "speaker": speaker,
                    "text": text,
                    "msg": msg[:200],
                })
                break  # 每 turn 算一次
    return evidence


def llm_extract_blacklist_words(evidence: list[dict]) -> dict:
    """LLM 看证据提炼触发词，按 audit msg 类型分组."""
    if not evidence:
        return {}
    sys.argv = ["learn", "learn", "h", "--adsd"]
    sys.path.insert(0, str(ROOT))
    import run_adr_v8 as adr  # noqa

    # 按 msg 类型分桶
    by_audit: dict[str, list[dict]] = defaultdict(list)
    for ev in evidence:
        msg = ev["msg"]
        if "Image asset audit" in msg:
            key = "image_asset_audit"
        elif "Content moderation" in msg:
            key = "content_moderation"
        elif "copyright" in msg.lower():
            key = "copyright_restrictions"
        else:
            key = "other"
        by_audit[key].append(ev)

    result: dict[str, list[str]] = {}
    for audit_type, items in by_audit.items():
        # 取 representative samples
        compact = [
            {"topic": e["topic"][:60], "speaker": e["speaker"], "text": e["text"][:80]}
            for e in items[:30]
        ]
        prompt = f"""你是 AI 视频审核分析师。以下是 WeryAI 平台触发「{audit_type}」拦截的 turn 证据。
从这些证据中提炼出最可能触发审核的关键词、品牌名、人名、敏感概念。

证据 (topic + speaker + text):
{json.dumps(compact, ensure_ascii=False)}

要求:
1. 输出严格 JSON: {{"blocked_words": ["词1", "词2", ...]}}
2. 词必须具体可识别 (品牌名/人名/商标/敏感概念)，不要写「篮球」「运动员」这种泛词
3. 排除可能误伤的中性词
4. 中英文混合 (e.g. "Lakers", "Kobe", "科比", "Bryant")
5. 最多 20 个最高优先级词
6. 不要解释只输出 JSON"""
        try:
            raw = adr.chat("GEMINI_25_FLASH", "你只输出严格 JSON。", prompt, max_tokens=600, timeout=60)
            obj = adr._extract_json_object(raw) if hasattr(adr, "_extract_json_object") else None
            if not obj:
                start = raw.find("{"); end = raw.rfind("}")
                obj = json.loads(raw[start:end+1]) if start >= 0 else {}
            words = obj.get("blocked_words") if isinstance(obj, dict) else None
            if isinstance(words, list):
                result[audit_type] = [str(w).strip() for w in words if str(w).strip()][:20]
        except Exception as e:
            print(f"  LLM 提炼 {audit_type} 失败: {e}")
    return result


def main():
    _load_env()
    if "--show" in sys.argv:
        if BLACKLIST_PATH.exists():
            print(BLACKLIST_PATH.read_text(encoding="utf-8"))
        else:
            print("(no blacklist yet)")
        return

    print("阶段 B · Audit 黑名单自动学习 开始...")
    evidence = collect_fail_evidence()
    print(f"收集到 {len(evidence)} 条失败证据 (跨所有历史 run)")

    if not evidence:
        print("无证据，跳过")
        return

    print(f"LLM 按 audit 类型提炼触发词...")
    blacklist_by_type = llm_extract_blacklist_words(evidence)

    # 汇总成最终黑名单
    all_words: set[str] = set()
    for words in blacklist_by_type.values():
        all_words.update(words)

    blacklist = {
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "version": 1,
        "total_evidence": len(evidence),
        "blocked_words_global": sorted(all_words),
        "blocked_words_by_audit_type": blacklist_by_type,
        "evidence_samples": evidence[:20],
    }
    BLACKLIST_PATH.parent.mkdir(parents=True, exist_ok=True)
    BLACKLIST_PATH.write_text(json.dumps(blacklist, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n黑名单已写入: {BLACKLIST_PATH}")
    print(f"全局触发词 ({len(all_words)} 个):")
    for w in sorted(all_words):
        print(f"  · {w}")


if __name__ == "__main__":
    main()
