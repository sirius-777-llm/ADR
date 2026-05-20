#!/usr/bin/env python3
"""AI 自动孵化 Speaker IP

输入：speaker 名 + 一句话简介
输出：完整 IP json + meta_grid PNG

用法:
  python3 tools/create_speaker_ip.py "杜甫" "唐代诗人，忧国忧民的现实主义诗圣"
  python3 tools/create_speaker_ip.py "Elon Musk" "Tesla/SpaceX/X 创始人，特立独行的科技狂人"

会自动:
  1. LLM 生成 visual_subject / personality / catchphrases / era / 服装/姿势/场景
  2. 推荐 voice_asset_id（从 voice_assets.json 池中按性别 + 调性匹配）
  3. 生成 meta_grid PNG (4×3 中文标签 grid)
  4. 写 voice_assets/speaker_ips/{name}.json
"""
import json
import os
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# 加载 env
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

_real_args = list(sys.argv[1:])  # 保留真实参数
sys.argv = ["create_speaker_ip.py", "ip", "h", "--adsd"]
sys.path.insert(0, str(ROOT))
import run_adr_v8 as adr  # noqa
sys.argv = ["create_speaker_ip.py"] + _real_args  # 恢复


def llm_generate_ip_skeleton(speaker: str, brief: str) -> dict:
    """LLM 生成 IP 骨架字段。"""
    prompt = f"""你是 ADR 项目的角色卡设计师。为以下角色生成完整 Speaker IP 数据。

角色名: {speaker}
简介: {brief}

输出严格 JSON，含字段:
  aliases: 该角色的别称数组 (中英文都可，0-5 个)
  visual_subject: 25-40 词英文描述外形（年龄+种族+体型+面部特征+服饰+时代背景）
  era: 该角色所处时代/年代（中文短语）
  personality: 4-6 条性格/特质短语（中文，每条 4-8 字）
  catchphrases: 该角色 2-4 句典型/历史/标志性台词（中文原文，避免争议性政治内容）
  costume_variants: 4 套该角色不同场合服装名（中文短语）
  poses: 6 种该角色典型姿态/动作（中文短语，如「说话」「沉思」「书写」）
  emotion_palette: 4 种该角色情绪基调（中文短语）
  scenes: 4 个该角色典型场景（中文短语）
  voice_gender: "male" 或 "female"
  voice_tone_hint: 中文短语描述音色调性（如「磁性深沉纪录片」「斯文学者」「年轻活力」）
  note: 1-2 句使用提示（召唤时优先什么基调）

要求:
1. 严格 JSON，不要 markdown，不要解释
2. 历史人物用真实信息；虚构/小说人物按设定
3. catchphrases 避开教科书超级著名诗句（会触发 audit）
4. visual_subject 详细但避免明星名字

只输出 JSON。"""
    raw = adr.chat("GEMINI_25_FLASH", "你只输出严格 JSON。", prompt, max_tokens=1500, timeout=90)
    start = raw.find("{")
    end = raw.rfind("}")
    if start < 0 or end <= start:
        raise RuntimeError(f"LLM 输出 JSON 解析失败：{raw[:300]}")
    data = json.loads(raw[start:end + 1])
    return data


def pick_voice_asset(voice_gender: str, voice_tone_hint: str) -> str:
    """从 voice_assets.json 池中按 gender + tone hint 推荐。"""
    catalog_path = ROOT / "voice_assets" / "voice_assets.json"
    if not catalog_path.exists():
        return adr.ADSD_DEFAULT_MALE_VOICE_ASSET
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    assets = catalog.get("assets", [])
    # 过滤性别匹配 + 不是高风险公众人物
    candidates = [
        a for a in assets
        if a.get("gender", "").lower() == voice_gender.lower()
        and not a.get("high_risk_public_figure", False)
        and "singing_not_speech" not in (a.get("quality_flags") or [])
    ]
    if not candidates:
        return adr.ADSD_DEFAULT_MALE_VOICE_ASSET if voice_gender == "male" else adr.ADSD_DEFAULT_FEMALE_VOICE_ASSET

    # LLM 二次推荐
    short_pool = [
        {
            "voice_id": a.get("voice_id"),
            "name": a.get("display_name", ""),
            "tone_tags": (a.get("tone_tags") or [])[:4],
            "age": a.get("age_style", ""),
            "person": str(a.get("identified_person", ""))[:40],
        }
        for a in candidates[:30]
    ]
    prompt = f"""从下面 voice_asset 池里挑最匹配的 1 个 voice_id。

候选池（gender={voice_gender}）:
{json.dumps(short_pool, ensure_ascii=False)}

目标音色调性: {voice_tone_hint}

只输出 1 个 voice_id 字符串，不要解释，不要 markdown。"""
    try:
        raw = adr.chat("GEMINI_25_FLASH", "你只输出一个 voice_id 字符串。", prompt, max_tokens=80, timeout=30)
        vid = raw.strip().strip('"').strip("'").strip()
        valid = {a["voice_id"] for a in candidates}
        if vid in valid:
            return vid
    except Exception as e:
        print(f"LLM voice_asset 推荐失败：{e}")
    # fallback 池里第一个
    return candidates[0].get("voice_id", adr.ADSD_DEFAULT_MALE_VOICE_ASSET)


def main():
    if len(sys.argv) < 3:
        print("Usage: create_speaker_ip.py <speaker> <brief>")
        print("  e.g. create_speaker_ip.py 杜甫 '唐代诗人，忧国忧民'")
        sys.exit(1)
    speaker, brief = sys.argv[1], sys.argv[2]
    print(f"\n=== 孵化 Speaker IP: {speaker} ===")
    print(f"简介: {brief}")

    # 检查是否已存在
    existing = adr._match_speaker_ip(speaker)
    if existing:
        print(f"⚠️ Speaker IP「{existing['speaker']}」已存在，覆盖? (y/n)")
        if input().strip().lower() != "y":
            print("取消")
            return

    # 1. LLM 生成 IP 骨架
    print("\n[1/3] LLM 生成 IP 骨架...")
    skeleton = llm_generate_ip_skeleton(speaker, brief)
    print(f"  visual_subject: {skeleton.get('visual_subject', '')[:80]}...")
    print(f"  era: {skeleton.get('era', '')}")
    print(f"  personality: {skeleton.get('personality', [])}")
    print(f"  catchphrases: {skeleton.get('catchphrases', [])[:2]}")

    # 2. 推荐 voice_asset
    print("\n[2/3] 推荐 voice_asset...")
    voice_gender = skeleton.get("voice_gender", "male")
    voice_tone_hint = skeleton.get("voice_tone_hint", "")
    voice_asset_id = pick_voice_asset(voice_gender, voice_tone_hint)
    print(f"  voice_asset_id: {voice_asset_id}")

    # 组装完整 IP
    ip = {
        "speaker": speaker,
        "aliases": skeleton.get("aliases", []),
        "voice_asset_id": voice_asset_id,
        "voice_gender": voice_gender,
        "visual_subject": skeleton.get("visual_subject", ""),
        "meta_grid": f"voice_assets/character_meta_grids/{speaker}.png",
        "era": skeleton.get("era", ""),
        "accent": "mandarin",
        "personality": skeleton.get("personality", []),
        "catchphrases": skeleton.get("catchphrases", []),
        "costume_variants": skeleton.get("costume_variants", []),
        "poses": skeleton.get("poses", []),
        "emotion_palette": skeleton.get("emotion_palette", []),
        "scenes": skeleton.get("scenes", []),
        "note": skeleton.get("note", ""),
        "created_at": "auto_generated_by_create_speaker_ip",
    }

    # 3. 生成 meta_grid（在 cache dir 直接生成，IP 路径指向该 cache）
    print("\n[3/3] 生成 meta_grid 人设符 grid (4K, ~2 min)...")
    cache_dir = ROOT / "voice_assets" / "character_meta_grids"
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_path = cache_dir / f"{speaker}.png"
    if cache_path.exists() and cache_path.stat().st_size > 100000:
        print(f"  reuse existing cache: {cache_path}")
    else:
        # 临时设置 OUTPUT_DIR 让 generate_character_meta_grid 写入指定路径
        # ADR 函数会先写入 OUTPUT_DIR 再复制到 cache
        import tempfile
        with tempfile.TemporaryDirectory(prefix="meta_grid_") as tmp:
            adr.OUTPUT_DIR = Path(tmp)
            adr.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            generated = adr.generate_character_meta_grid_gpt_image2(speaker, ip["visual_subject"], voice_gender)
            if not generated or not os.path.exists(generated):
                print("  ❌ meta_grid 生成失败，IP 仍保存但缺 meta_grid")
                ip["meta_grid"] = ""
            else:
                # 复制到 cache_dir
                from shutil import copyfile
                copyfile(generated, cache_path)
                print(f"  ✓ meta_grid: {cache_path}")

    # 4. 保存 IP json
    saved = adr._save_speaker_ip(speaker, ip)
    print(f"\n=== IP 已保存: {saved} ===")
    print(f"aliases: {ip['aliases']}")
    print(f"voice_asset: {ip['voice_asset_id']}")
    print(f"meta_grid: {ip['meta_grid']}")
    print()
    print(f"测试匹配:")
    for q in [speaker] + (ip.get("aliases") or [])[:2]:
        hit = adr._match_speaker_ip(q)
        print(f"  '{q}' -> {hit['speaker'] if hit else None}")


if __name__ == "__main__":
    main()
