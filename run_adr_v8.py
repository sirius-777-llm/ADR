#!/usr/bin/env python3
"""
ADR V8 — 字幕驱动纪录片自动生成管线

用法：
    python3 run_adr_v8.py "1924年泰戈尔访华"

环境变量：
    WERYAI_API_KEY   必填
    TG_BOT_TOKEN     必填（状态推送）
    TG_CHAT_ID       必填
    OUTPUT_DIR       可选，默认 /tmp/adr_v8_output
"""
import json
import math
import os
import re
import subprocess
import sys
import time
import threading
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

import requests

# ── 老黄历数据模块 ────────────────────────────────────────────────────────
# 确保 homebrew site-packages 在 sys.path 中（claude -p 子进程环境可能缺失）
import sys as _sys
_sp = '/opt/homebrew/lib/python3.14/site-packages'
if _sp not in _sys.path:
    _sys.path.insert(0, _sp)
# 项目根目录加入 sys.path，让 adr_data 包可以被 import
_project_root = str(Path(__file__).resolve().parent)
if _project_root not in _sys.path:
    _sys.path.insert(0, _project_root)

# 抽离的纯数据常量（Phase 2 重构）— 保持原变量名兼容现有代码
from adr_data.action_keywords import ACTION_KEYWORDS_ZH as _ACTION_KEYWORDS_ZH  # noqa: E402
from adr_data.emotion import (  # noqa: E402
    EMOTION_KEYWORDS as _EMOTION_KEYWORDS,
    EMOTION_EXPRESSION_PHRASE as _EMOTION_EXPRESSION_PHRASE,
    SUPPORTED_EMOTIONS as _SUPPORTED_EMOTIONS,
)
from adr_data.voices import (  # noqa: E402
    ADSD_VOICES,
    ADSD_MALE_VOICE_POOL,
    ADSD_FEMALE_VOICE_POOL,
    ADSD_MALE_VOICE_IDS,
    ADSD_FEMALE_VOICE_IDS,
    ADSD_VOICE_GENDER_BY_ID,
    ADSD_SPEAKER_KEYWORD_TO_ASSET,
)

def get_almanac_data(topic: str) -> str | None:
    """从 topic 提取日期，用 lunar-python 获取完整老黄历数据，返回结构化文本。
    如果 topic 不含老黄历关键词或无法提取日期，返回 None。"""
    keywords = ["老黄历", "黄历", "彭祖百忌", "星宿", "二十八星宿", "建星", "宜忌", "万年历"]
    if not any(k in topic for k in keywords):
        return None
    import re
    m = re.search(r'(\d{4})\D*(\d{1,2})\D*(\d{1,2})', topic)
    if not m:
        return None
    year, month, day = int(m.group(1)), int(m.group(2)), int(m.group(3))
    try:
        from lunar_python import Solar
        s = Solar.fromYmd(year, month, day)
        l = s.getLunar()
        lines = []
        lines.append(f"公历：{year}年{month}月{day}日")
        lines.append(f"农历：{l}")
        lines.append(f"年干支：{l.getYearInGanZhi()}  月干支：{l.getMonthInGanZhi()}  日干支：{l.getDayInGanZhi()}")
        try: lines.append(f"纳音：{l.getDayNaYin()}")
        except: pass
        try: lines.append(f"生肖：{l.getYearShengXiao()}")
        except: pass
        try: lines.append(f"十二建星：{l.getZhiXing()}")
        except: pass
        try: lines.append(f"二十八星宿：{l.getXiu()}（{l.getXiuLuck()}）— {l.getXiuSong()[:30]}")
        except: pass
        try: lines.append(f"彭祖百忌：{l.getPengZuGan()} {l.getPengZuZhi()}")
        except: pass
        try: lines.append(f"宜：{'、'.join(l.getDayYi())}")
        except: pass
        try: lines.append(f"忌：{'、'.join(l.getDayJi())}")
        except: pass
        try: lines.append(f"吉神宜趋：{'、'.join(l.getDayJiShen())}")
        except: pass
        try: lines.append(f"凶神宜忌：{'、'.join(l.getDayXiongSha())}")
        except: pass
        try: lines.append(f"值日天神：{l.getDayTianShen()}（{l.getDayTianShenLuck()}，{l.getDayTianShenType()}）")
        except: pass
        try: lines.append(f"胎神占方：{l.getDayPositionTai()}")
        except: pass
        try: lines.append(f"冲：{l.getDayChongDesc()}  煞：{l.getDaySha()}")
        except: pass
        try: lines.append(f"财神方位：{l.getDayPositionCaiDesc()}  喜神方位：{l.getDayPositionXiDesc()}  福神方位：{l.getDayPositionFuDesc()}")
        except: pass
        try: lines.append(f"九宫飞星：{l.getDayNineStar()}")
        except: pass
        # 吉时
        try:
            from lunar_python import LunarTime
            good_times = []
            zhi_names = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
            for i in range(12):
                t = LunarTime.fromYmdHms(l.getYear(), l.getMonth(), l.getDay(), i * 2, 0, 0)
                if t.getTianShenLuck() == '吉':
                    good_times.append(f"{zhi_names[i]}时({i*2:02d}:00-{i*2+2:02d}:00 {t.getTianShen()})")
            if good_times:
                lines.append(f"吉时：{'、'.join(good_times)}")
        except: pass
        return '\n'.join(lines)
    except Exception as e:
        print(f"WARNING: 老黄历数据获取失败: {e}", file=__import__('sys').stderr)
        return None


# ── 配置 ────────────────────────────────────────────────────────────────────
WERYAI_API_KEY = os.environ.get("WERYAI_API_KEY", "")
TG_BOT_TOKEN   = os.environ.get("TG_BOT_TOKEN", "")
TG_CHAT_ID     = os.environ.get("TG_CHAT_ID", "")
TG_PROGRESS_MODE = os.environ.get("ADR_TG_PROGRESS_MODE", "dashboard").strip().lower()
TG_DIGEST_INTERVAL_SEC = float(os.environ.get("ADR_TG_DIGEST_INTERVAL_SEC", "120"))
TG_DASHBOARD_EDIT_INTERVAL_SEC = float(os.environ.get("ADR_TG_DASHBOARD_EDIT_INTERVAL_SEC", "8"))

if not all([WERYAI_API_KEY, TG_BOT_TOKEN, TG_CHAT_ID]):
    missing = [k for k, v in [("WERYAI_API_KEY", WERYAI_API_KEY), ("TG_BOT_TOKEN", TG_BOT_TOKEN), ("TG_CHAT_ID", TG_CHAT_ID)] if not v]
    print(f"ERROR: 缺少环境变量: {', '.join(missing)}", file=sys.stderr)
    sys.exit(1)

HEADERS = {
    "Authorization": f"Bearer {WERYAI_API_KEY}",
    "Content-Type": "application/json",
}

BASE_URL = "https://api.weryai.com/v1"

TOPIC = sys.argv[1] if len(sys.argv) > 1 else "历史上的今天"
VIDEO_FORMAT = (sys.argv[2] if len(sys.argv) > 2 else "h").lower()  # "h" = 横屏 16:9, "v" = 竖屏 9:16
IS_VERTICAL = VIDEO_FORMAT == "v"
# 审核默认 OFF（自动免审快速产出）；传 --with-approval 强制审核（仍兼容旧的 --skip-approval flag）
# 异常自动触发审核：封面 OCR DUPLICATED / 分镜 fallback / 等异常会单独推审（已内建）
SKIP_APPROVAL = "--with-approval" not in sys.argv
if "--skip-approval" in sys.argv:
    SKIP_APPROVAL = True  # 显式 skip 也支持
WITH_MOTION = "--with-motion" in sys.argv  # 每分镜走 WERYDANCE_2_0 生成带运动视频，~2x 时长 + $0.3/scene
BGM_ONLY_REQUESTED = (
    "--bgm-only" in sys.argv
    or "--no-tts" in sys.argv
    or "--no-narration" in sys.argv
    or "--no-voice" in sys.argv
    or os.environ.get("ADR_BGM_ONLY", "").strip().lower() in ("1", "true", "yes", "on")
)
ADS_DIALOGUE_MODE = (
    "--ads-dialogue" in sys.argv
    or "--adsd" in sys.argv
    or os.environ.get("ADR_ADS_DIALOGUE", "").strip().lower() in ("1", "true", "yes", "on")
)
if ADS_DIALOGUE_MODE and BGM_ONLY_REQUESTED:
    print("ERROR: --bgm-only/--no-tts/--no-voice 目前只支持 ADR/ADS，不支持 ADSD 对白模式。", file=sys.stderr)
    sys.exit(2)
NO_VOICE = BGM_ONLY_REQUESTED  # ADR/ADS: 跳过 Podcast/TTS，用静音时间轴占位；成片音轨只有 BGM
GPT_IMAGE2_STORYBOARD = (
    "--no-storyboard" not in sys.argv
    and os.environ.get("ADR_GPT_IMAGE2_STORYBOARD", "1").strip().lower() not in ("0", "false", "no", "off")
)
STORYBOARD_REFERENCE_MOTION = (
    "--no-reference-motion" not in sys.argv
    and os.environ.get("ADR_STORYBOARD_REFERENCE_MOTION", "1").strip().lower() not in ("0", "false", "no", "off")
)
STORYBOARD_ANNOTATED_MOTION = (
    "--with-annotated-motion" in sys.argv
    or os.environ.get("ADR_STORYBOARD_ANNOTATED_MOTION", "").strip().lower() in ("1", "true", "yes", "on")
)
GPT_IMAGE2_DIRECT_ANNOTATED_STORYBOARD = (
    "--with-direct-annotated-storyboard" in sys.argv
    or "--with-direct-annotated-storyboards" in sys.argv
    or os.environ.get("ADR_GPT_IMAGE2_DIRECT_ANNOTATED_STORYBOARD", "").strip().lower() in ("1", "true", "yes", "on")
)
GPT_IMAGE2_STORYBOARD_GRID = (
    "--no-storyboard" not in sys.argv
    and "--no-storyboard-grid" not in sys.argv
    and os.environ.get("ADR_DEFAULT_STORYBOARD_GRID", "1").strip().lower() not in ("0", "false", "no", "off")
    or "--with-storyboard-grid" in sys.argv
    or "--with-storyboard-grid-4k" in sys.argv
    or os.environ.get("ADR_GPT_IMAGE2_STORYBOARD_GRID", "").strip().lower() in ("1", "true", "yes", "on")
)
ADSD_STORYBOARD_GRID = (
    ADS_DIALOGUE_MODE
    and os.environ.get("ADR_ADSD_STORYBOARD_GRID", "1").strip().lower() not in ("0", "false", "no", "off")
)
# ADS（单人 POV 记者）也可以可选启用角色形象表——锁住"记者本人 + 受访者 + 关键道具"跨镜一致性
# 默认 OFF；通过 --ads-character-sheet 或 ADR_ADS_CHARACTER_SHEET=1 开启
ADS_CHARACTER_SHEET_REQUESTED = (
    "--ads-character-sheet" in sys.argv
    or os.environ.get("ADR_ADS_CHARACTER_SHEET", "").strip().lower() in ("1", "true", "yes", "on")
)
STORYBOARD_GRID_MULTIREF_MOTION = (
    "--with-grid-multiref-motion" in sys.argv
    or os.environ.get("ADR_STORYBOARD_GRID_MULTIREF_MOTION", "").strip().lower() in ("1", "true", "yes", "on")
)
STORYBOARD_GRID_MULTIREF_SEGMENTS = (
    "--use-grid-multiref-segments" in sys.argv
    and "--no-grid-multiref-segments" not in sys.argv
)
# P1：把 grid_multiref（多 panel 一次出整组）从 sidecar QA 升级为主路径
# 启用后 step7 用 grid_multiref_combined.mp4 当 raw 视频（同 trailer-main 套路）
STORYBOARD_GRID_MULTIREF_MAIN = (
    "--grid-multiref-main" in sys.argv
    or os.environ.get("ADR_STORYBOARD_GRID_MULTIREF_MAIN", "").strip().lower() in ("1", "true", "yes", "on")
)
if STORYBOARD_GRID_MULTIREF_MAIN:
    STORYBOARD_GRID_MULTIREF_MOTION = True  # 主路径必须先生 sidecar
PREVIS_PAGE_MOTION = (
    "--with-previs-page-motion" in sys.argv
    or os.environ.get("ADR_PREVIS_PAGE_MOTION", "").strip().lower() in ("1", "true", "yes", "on")
)
STORYBOARD_TRAILER_MODE = (
    "--storyboard-trailer-mode" in sys.argv
    or "--with-storyboard-trailer" in sys.argv
    or os.environ.get("ADR_STORYBOARD_TRAILER_MODE", "").strip().lower() in ("1", "true", "yes", "on")
)
MOTION_ACTION_STORYBOARD = (
    "--no-motion-action-storyboard" not in sys.argv
    and os.environ.get("ADR_MOTION_ACTION_STORYBOARD", "1").strip().lower() not in ("0", "false", "no", "off")
)
MOTION_BRIDGE_REFS = (
    "--no-motion-bridge-refs" not in sys.argv
    and os.environ.get("ADR_MOTION_BRIDGE_REFS", "1").strip().lower() not in ("0", "false", "no", "off")
)
CHARACTER_TRAILER_MODE = (
    "--character-trailer-mode" in sys.argv
    or "--with-character-trailer" in sys.argv
    or os.environ.get("ADR_CHARACTER_TRAILER_MODE", "").strip().lower() in ("1", "true", "yes", "on")
)
# 实验：故事板 trailer 升格为主路径——跳过单镜 motion，整张故事板一次 WERYDANCE 出主视频
# trailer 时长 5-15s，会被 ffmpeg tpad 拉伸到旁白长度，字幕走原 ASS 烧录
# 暂定 opt-in，验证多题材后可考虑升为默认
STORYBOARD_TRAILER_MAIN = (
    "--storyboard-trailer-main" in sys.argv
    or os.environ.get("ADR_STORYBOARD_TRAILER_MAIN", "").strip().lower() in ("1", "true", "yes", "on")
)
if STORYBOARD_TRAILER_MAIN:
    # 自动开启 trailer 生成（被升格为主路径，不能不生成）
    STORYBOARD_TRAILER_MODE = True
    # 关闭单镜 motion（trailer 已经包含所有运镜）
    WITH_MOTION = False
if STORYBOARD_GRID_MULTIREF_SEGMENTS:
    STORYBOARD_GRID_MULTIREF_MOTION = True
if STORYBOARD_GRID_MULTIREF_MOTION or PREVIS_PAGE_MOTION or STORYBOARD_TRAILER_MODE or CHARACTER_TRAILER_MODE or ADSD_STORYBOARD_GRID:
    GPT_IMAGE2_STORYBOARD_GRID = True
ADSD_LIP_SYNC_EXPERIMENT = (
    ADS_DIALOGUE_MODE
    and "--no-lip-sync" not in sys.argv
    and "--no-adsd-lip-sync" not in sys.argv
    and os.environ.get("ADR_ADSD_LIP_SYNC", "1").strip().lower() not in ("0", "false", "no", "off")
    or "--adsd-lip-sync" in sys.argv
    or "--lip-sync" in sys.argv
)
ADSD_RICH_MOTION_PROMPT = (
    "--adsd-rich-motion" in sys.argv
    or os.environ.get("ADR_ADSD_RICH_MOTION", "").strip().lower() in ("1", "true", "yes", "on")
)
# LLM 智能音色分配 (Phase: voice-LLM)
# 默认 ON — LLM 看 voice_assets.json + 12 turn text 自动选 voice_asset_id
# keyword 规则保留作 fallback (LLM 失败 / 选了不存在的 asset 时)
# 关闭: ADR_ADSD_LLM_VOICE_ASSIGN=0 走纯 keyword 规则
ADSD_LLM_VOICE_ASSIGN = (
    "--no-llm-voice-assign" not in sys.argv
    and os.environ.get("ADR_ADSD_LLM_VOICE_ASSIGN", "1").strip().lower() not in ("0", "false", "no", "off")
)
ADSD_ALMIGHTY_AUDIO_DUB_EXPERIMENT = (
    ADS_DIALOGUE_MODE
    and (
        "--adsd-almighty-audio-dub" in sys.argv
        or "--almighty-audio-dub" in sys.argv
        or (
            "--no-adsd-almighty-audio-dub" not in sys.argv
            and "--no-almighty-audio-dub" not in sys.argv
            and os.environ.get("ADR_ADSD_ALMIGHTY_AUDIO_DUB", "1").strip().lower() not in ("0", "false", "no", "off")
        )
    )
)
# P2：连续同 speaker 的 turn 合并成 1 个 WERYDANCE 调用，节省调用次数 + 自然衔接
# 默认 OFF（实验性，WERYDANCE 时间漂移可能导致段间错位）
ADSD_CONSECUTIVE_SPEAKER_BATCHING = (
    "--adsd-speaker-batch" in sys.argv
    or os.environ.get("ADR_ADSD_SPEAKER_BATCH", "").strip().lower() in ("1", "true", "yes", "on")
)
ADSD_SPEAKER_BATCH_MAX_DURATION = float(os.environ.get("ADR_ADSD_SPEAKER_BATCH_MAX_DUR", "14.0"))
ADSD_DEFAULT_MALE_VOICE_ASSET = os.environ.get("ADR_ADSD_DEFAULT_MALE_VOICE_ASSET", "external_luo_xiang_xyma_001")
ADSD_DEFAULT_FEMALE_VOICE_ASSET = os.environ.get("ADR_ADSD_DEFAULT_FEMALE_VOICE_ASSET", "external_by2_e7gn_001")

# ── 音色库智能匹配（P3） ─────────────────────────────────────────
# 数据已抽到 adr_data/voices.py 的 ADSD_SPEAKER_KEYWORD_TO_ASSET（顶部已 import）
# gender-only fallback（关键字未命中时）
ADSD_GENDER_FALLBACK_VOICE_ASSET = {
    "male": ADSD_DEFAULT_MALE_VOICE_ASSET,
    "female": "external_tiktok_nghithao_0208_7624063339613752594",  # 不用 BY2 歌声
}


# _ACTION_KEYWORDS_ZH 已抽到 adr_data/action_keywords.py（顶部已 import）


def _is_action_scene(text: str, shot: str = "") -> bool:
    """检测是否动作场面（武侠/修真/打斗题材）"""
    combined = str(text or "") + " " + str(shot or "")
    hits = sum(1 for kw in _ACTION_KEYWORDS_ZH if kw in combined)
    return hits >= 2  # 至少 2 个动作关键字


def _needs_storyboard_flow_character_sheet(script: list[dict] | None, topic: str = "") -> bool:
    """GPT Image 2 character sheet auto gate for storyboard-flow WeryDance.

    Use it when the video model needs a reusable identity anchor: action scenes,
    recurring people/creatures/robots, or explicit identity-consistency wording.
    """
    if os.environ.get("ADR_STORYBOARD_FLOW_CHARACTER_SHEET", "1").strip().lower() in ("0", "false", "no", "off"):
        return False
    if ADS_DIALOGUE_MODE:
        return False
    if ADS_CHARACTER_SHEET_REQUESTED or CHARACTER_TRAILER_MODE:
        return True
    script = script or []
    if any(_is_action_scene(s.get("text", ""), s.get("prompt", "")) for s in script):
        return True
    blob = " ".join(
        [topic]
        + [str(s.get("text") or "") for s in script[:12]]
        + [str(s.get("prompt") or "") for s in script[:12]]
    )
    identity_keywords = (
        "人物一致", "角色一致", "人物参考", "角色参考", "主角", "主人公", "角色", "人物",
        "武者", "侠客", "剑客", "机器人", "动物", "鸵鸟", "龙", "怪兽", "英雄",
        "黄仁勋", "Jensen", "特朗普", "川普", "Trump", "黄渤", "罗翔", "许知远",
        "CEO", "总统", "记者", "男主", "女主", "儿童", "孩子",
    )
    return any(k in blob for k in identity_keywords)


def _wuxia_action_panel_prompt(text: str, shot: str = "", visual_subject: str = "", voice_gender: str = "") -> str:
    """生成武侠/修真动作场面的 storyboard 出图 prompt — 让 GPT Image 2 渲染真实打斗画面而非对话场景。
    替换 姜文 LLM 的通用纪录片 prompt，使下游 WERYDANCE 拿到的底图本身就是动作 panel。"""
    text_clip = re.sub(r"\s+", " ", str(text or "")).strip()[:80]
    shot_clip = re.sub(r"\s+", " ", str(shot or "")).strip()[:80]
    subject = re.sub(r"\s+", " ", str(visual_subject or "")).strip()[:80]
    gender_lock = _adsd_gender_lock_phrase(voice_gender)  # 满足 gender_voice_qa 检查
    return (
        "Wide cinematic wuxia/xianxia combat panel at peak-tension freeze frame. "
        f"Narration says: 「{text_clip}」 — render the action described, NOT characters talking about it. "
        f"{('Active subject: ' + subject + '. ') if subject else ''}"
        f"{('Shot direction: ' + shot_clip + '. ') if shot_clip else ''}"
        f"{gender_lock} "
        "Visible sword/blade trails caught mid-swing, qi/spiritual-energy bursts in jade-cyan neon ink-wash palette, "
        "robes and long hair caught mid-flight by impact wind, debris/sparks/talismanic glyphs floating in mid-air, "
        "low-angle hero shot or dramatic over-the-shoulder framing, "
        "dynamic motion blur on weapons and limbs, deep film grain, dramatic rim backlight. "
        "Strictly forbidden: characters standing still and speaking, talking heads, calm portrait, "
        "speech bubbles, captions, subtitles, watermarks, modern clothing, contemporary urban backgrounds."
    )


def _action_motion_fragment() -> str:
    """动作场面专用 WERYDANCE motion prompt 强化 — 武侠/修真打斗节奏"""
    return (
        " High-energy wuxia/xianxia cultivation action sequence. "
        "Dynamic combat choreography: rapid whip pans, low-angle hero shots, dolly-zoom on impact, selective slow-motion. "
        "Visible sword/blade trails, qi/spiritual energy bursts in neon ink-wash palette, "
        "wind-driven garments and hair flying, debris and sparks streaming. "
        "Strong motion blur on weapon strikes, cinematic depth of field, dramatic backlight, "
        "particle effects (dust, embers, talismanic glyphs in mid-air). "
    )


# _EMOTION_KEYWORDS + _EMOTION_EXPRESSION_PHRASE 已抽到 adr_data/emotion.py（顶部已 import）


def _infer_emotion_from_text(text: str, speaker: str = "") -> str:
    """关键字命中推断情绪；未命中按 speaker 类型给默认。
    避免 override 路径所有 turn 永远 neutral 导致 GPT Image 2 画严肃脸。"""
    s = str(text or "")
    sp = str(speaker or "")
    scores = {emo: sum(1 for kw in kws if kw in s) for emo, kws in _EMOTION_KEYWORDS.items()}
    if scores:
        top_emo = max(scores, key=lambda k: scores[k])
        if scores.get(top_emo, 0) > 0:
            return top_emo
    if "旁白" in sp or sp.lower() in ("narrator", "voiceover", "vo"):
        return "contemplative"
    return "neutral"


def _emotion_expression_phrase(emotion: str) -> str:
    return _EMOTION_EXPRESSION_PHRASE.get(
        str(emotion or "").strip().lower(),
        _EMOTION_EXPRESSION_PHRASE["neutral"],
    )


def _infer_needs_lip_sync(speaker: str, text: str = "", emotion: str = "") -> bool:
    """规则推断：本 turn 是否需要走 A-roll lip-sync 路径（说话人正脸 + 嘴对音频）。
    旁白/voiceover/解说类 → False (B-roll voice-over，画面全员可动)
    动作场面（武侠/修真/打斗 ≥2 关键字） → False (B-roll，让 WERYDANCE 自由发挥动作)
    其他 speaker → True (A-roll lip-sync 保留口型同步)
    可被 override 脚本/LLM 显式覆盖。
    """
    sp = str(speaker or "").strip()
    if not sp:
        return True
    # 显式 narrator 类型 → B-roll voice-over
    if "旁白" in sp or sp.lower() in ("narrator", "voiceover", "vo", "解说"):
        return False
    # 动作场面：text 里 ≥2 个武侠/修真/打斗关键字 → B-roll 让画面优先表达动作
    if _is_action_scene(text):
        return False
    return True


# ── 三类 turn 区分 (silent_b PR) ──────────────────────────────────────────────
# a_roll       说话人特写 + 对白 + 克隆音色 (needs_lip_sync=True)
# narrated_b   空镜/远景/剪影 + 旁白 + 克隆音色 (needs_lip_sync=False, has dialogue)
# silent_b     空镜/呼吸位 + 无 dialogue + 仅 BGM (needs_lip_sync=False, no dialogue)
SILENT_B_SPEAKERS = {"(silent)", "silent", "(无)", "无对白", "空镜"}


def _infer_turn_type(speaker: str, text: str = "", emotion: str = "", turn_type_hint: str = "") -> str:
    """推断 turn 类型。优先级：explicit hint > rules。

    返回 "a_roll" | "narrated_b" | "silent_b"
    """
    explicit = (turn_type_hint or "").strip().lower()
    if explicit in ("a_roll", "narrated_b", "silent_b"):
        return explicit
    sp = str(speaker or "").strip()
    txt = str(text or "").strip()
    if not txt or sp in SILENT_B_SPEAKERS or sp.lower() in {"silent", "silent_b"}:
        return "silent_b"
    if "旁白" in sp or sp.lower() in ("narrator", "voiceover", "vo", "解说"):
        return "narrated_b"
    if _is_action_scene(txt):
        return "narrated_b"
    return "a_roll"


def _resolve_turn_type(scene: dict) -> str:
    """从 scene dict 取 turn_type；缺省时按 speaker/text/needs_lip_sync 兜底推断。"""
    if not isinstance(scene, dict):
        return "a_roll"
    explicit = (scene.get("turn_type") or "").strip().lower()
    if explicit in ("a_roll", "narrated_b", "silent_b"):
        return explicit
    speaker = scene.get("speaker", "") or ""
    text = scene.get("text") or scene.get("dialogue") or ""
    # 老 scene 没 turn_type 但有 needs_lip_sync：True → a_roll
    if scene.get("needs_lip_sync") is True and str(text).strip():
        return "a_roll"
    return _infer_turn_type(speaker, text, scene.get("emotion", ""))


def _is_silent_b(scene: dict) -> bool:
    return _resolve_turn_type(scene) == "silent_b"


def _is_narrated_b(scene: dict) -> bool:
    return _resolve_turn_type(scene) == "narrated_b"


def _is_a_roll(scene: dict) -> bool:
    return _resolve_turn_type(scene) == "a_roll"


def _voice_asset_id_for_speaker(speaker: str, gender: str | None = None) -> str:
    """根据 speaker name 关键字命中音色库的 voice_id；命中失败按 gender 走 fallback。"""
    s = str(speaker or "")
    g = (gender or "").strip().lower()
    if not s:
        return ADSD_GENDER_FALLBACK_VOICE_ASSET.get(g, ADSD_DEFAULT_MALE_VOICE_ASSET)
    for keywords, asset_id in ADSD_SPEAKER_KEYWORD_TO_ASSET:
        for kw in keywords:
            if kw and kw in s:
                # 还要按 gender 校验：如果命中的 asset gender 不匹配，跳过
                if g:
                    try:
                        data = _load_voice_assets()
                        asset = next((a for a in data.get("assets", []) if a.get("voice_id") == asset_id), None)
                        if asset and asset.get("gender") and asset.get("gender") != g:
                            continue
                    except Exception:
                        pass
                return asset_id
    # 关键字未命中 → gender fallback
    return ADSD_GENDER_FALLBACK_VOICE_ASSET.get(g, ADSD_DEFAULT_MALE_VOICE_ASSET)


def _llm_assign_voice_assets(turns: list[dict]) -> dict[int, str]:
    """LLM 智能音色分配 — 看完整 voice_assets.json + 全部 turn 文本，per-turn 选最优 voice_asset_id。
    返回 {turn_idx (0-based): voice_asset_id}。
    失败/未命中: 对应 idx 不在 dict → 调用方走 keyword fallback。
    """
    if not turns or not ADSD_LLM_VOICE_ASSIGN:
        return {}
    try:
        catalog = _load_voice_assets()
    except Exception as e:
        log(f"LLM voice assign: 读 voice_assets.json 失败 {e}")
        return {}
    assets = catalog.get("assets", [])
    if not assets:
        return {}
    # 过滤候选池：跳过歌声 / 混音未分离 / 高风险公众人物
    selectable = []
    for a in assets:
        flags = set(a.get("quality_flags", []) or [])
        if "singing_not_speech" in flags or "music_contaminated" in flags:
            continue
        if "mixed_two_speakers_not_diarized" in flags:
            continue
        if a.get("high_risk_public_figure"):
            continue
        selectable.append({
            "voice_id": a.get("voice_id"),
            "name": a.get("display_name", ""),
            "person": str(a.get("identified_person", ""))[:50],
            "gender": a.get("gender", ""),
            "age": a.get("age_style", ""),
            "tone_tags": (a.get("tone_tags") or [])[:5],
            "scene_tags": (a.get("scene_tags") or [])[:3],
            "accent": a.get("accent", ""),
        })
    if not selectable:
        return {}
    turn_summary = [
        {
            "idx": i,
            "speaker": str(t.get("speaker", "")),
            "voice_gender": str(t.get("voice_gender", "")),
            "emotion": str(t.get("emotion", "neutral")),
            "text": str(t.get("text", ""))[:80],
        }
        for i, t in enumerate(turns)
    ]
    prompt = f"""你是 ADR 纪录片音色总监。为每个 turn 从音色库选最匹配的 voice_id。

候选音色池（已过滤歌声 / 混音 / 高风险公众人物）:
{json.dumps(selectable, ensure_ascii=False)}

剧本 {len(turns)} turn:
{json.dumps(turn_summary, ensure_ascii=False)}

选择规则（严格遵守）:
1. 同 speaker 跨 turn 必须用同一 voice_id（角色一致性）
2. **不同 speaker 必须用不同 voice_id**（避免观众听感混淆）
   ★ 例外：候选池里同 gender 可选 asset 数 < 该 gender 的 speaker 数时
     可以重复，但要尽量挑 tone_tags 差异最大的两个分配
3. gender 必须匹配 — turn.voice_gender ≠ asset.gender 时严禁选
4. 语义匹配：text 内容 + speaker 身份 + emotion 综合判定
   • 学者/知识访谈 → 许知远 / 罗翔
   • 工程师/CEO/合伙人 → 黄仁勋
   • 玄幻/古风长者/村长 → 绫璟道人
   • 年轻男弟子/学生 → 秦牧
   • 都市女白领/职场女 → urban_talk
   • 印尼/东南亚口音 → mettsarchive
   • 演员对白/戏剧/体育人物 → 黄渤
5. 严肃纪录片基调避开"短视频网红/活力女"标签
6. 武侠/玄幻题材避开"现代访谈"音色
7. 同 gender 内有多选时，按 tone_tags 与 emotion 最匹配的选；
   优先保证规则 2 的差异化

输出 JSON 数组（仅此，无 markdown / 无解释）:
[{{"idx": 0, "voice_id": "external_xxx_001", "reason": "10字内"}}, ...]
"""
    try:
        raw = chat(
            "GEMINI_25_FLASH",
            "你是 ADR 纪录片音色总监。只输出 JSON 数组，不解释。",
            prompt,
            max_tokens=2000,
            timeout=60,
        )
    except Exception as e:
        log(f"LLM voice assign: chat 调用失败 {e}")
        return {}
    arr_start = raw.find('[')
    arr_end = raw.rfind(']')
    if arr_start < 0 or arr_end <= arr_start:
        log("LLM voice assign: JSON 解析失败（无 [...]）")
        return {}
    try:
        parsed = json.loads(raw[arr_start:arr_end + 1])
    except Exception as e:
        log(f"LLM voice assign: JSON parse 失败 {e}")
        return {}
    valid_ids = {a["voice_id"] for a in selectable}
    by_id = {a["voice_id"]: a for a in selectable}
    result: dict[int, str] = {}
    reasons: dict[int, str] = {}
    for entry in parsed:
        if not isinstance(entry, dict):
            continue
        idx = entry.get("idx")
        vid = entry.get("voice_id")
        if not isinstance(idx, int) or not (0 <= idx < len(turns)):
            continue
        if vid not in valid_ids:
            continue
        # gender 校验：LLM 选的 asset.gender 必须与 turn.voice_gender 匹配
        turn_gender = str(turns[idx].get("voice_gender", "")).strip().lower()
        asset_gender = str(by_id[vid].get("gender", "")).strip().lower()
        if turn_gender and asset_gender and turn_gender != asset_gender:
            log(f"LLM voice assign turn {idx+1}: gender 冲突 ({turn_gender} vs {asset_gender}) → 跳过")
            continue
        result[idx] = vid
        reasons[idx] = str(entry.get("reason", ""))[:40]
    if result:
        log(f"LLM voice assign: {len(result)}/{len(turns)} turn 完成 LLM 分配")
    return result


def _apply_llm_voice_assignment(turns: list[dict]) -> dict | None:
    """在 turns 已通过 keyword 推断后，调 LLM 智能覆盖。
    LLM 失败或未覆盖的 turn 保留原 keyword 决策。
    后处理：检测"不同 speaker 撞同一 voice_id"冲突，第二个起回退到 keyword 决策。
    返回 QA dict (per-turn decision source: llm / keyword / fallback)。
    """
    if not turns or not ADSD_LLM_VOICE_ASSIGN:
        return None
    # 保留 keyword 阶段的原始决策，作冲突回退池
    keyword_decisions = {i: t.get("voice_asset_id", "") for i, t in enumerate(turns)}
    llm_choices = _llm_assign_voice_assets(turns)
    # 加载候选池（同 _llm_assign_voice_assets 的过滤口径）供冲突时 diversifier 使用
    _diversifier_pool: dict[str, list[str]] = {"male": [], "female": []}
    try:
        _catalog = _load_voice_assets()
        for a in _catalog.get("assets", []):
            flags = set(a.get("quality_flags", []) or [])
            if "singing_not_speech" in flags or "music_contaminated" in flags:
                continue
            if "mixed_two_speakers_not_diarized" in flags:
                continue
            if a.get("high_risk_public_figure"):
                continue
            g = str(a.get("gender", "")).strip().lower()
            if g in _diversifier_pool:
                _diversifier_pool[g].append(a.get("voice_id", ""))
    except Exception:
        pass
    # 后处理：speaker → first turn idx 映射，同 speaker 跨 turn 共用 voice_id（保留），
    # 不同 speaker 但 LLM 给同一 voice_id → 冲突
    speaker_to_voice: dict[str, str] = {}  # 第一个出现的 speaker 锁定 voice
    voice_to_speaker: dict[str, str] = {}  # 反向锁
    conflicts: list[dict] = []
    for i, t in enumerate(turns):
        sp = str(t.get("speaker", "")).strip()
        if i not in llm_choices:
            continue
        vid = llm_choices[i]
        if sp in speaker_to_voice:
            # 同 speaker 后续 turn → 强制用第一个 turn 锁定的 voice
            if vid != speaker_to_voice[sp]:
                conflicts.append({
                    "turn": i + 1,
                    "speaker": sp,
                    "reason": "same_speaker_voice_drift",
                    "llm_chose": vid,
                    "locked_to": speaker_to_voice[sp],
                })
                llm_choices[i] = speaker_to_voice[sp]
            continue
        # 新 speaker
        if vid in voice_to_speaker and voice_to_speaker[vid] != sp:
            # 不同 speaker 撞同 voice → 1) keyword 决策；2) 还撞 → 从候选池挑未占用的同 gender voice
            kw_vid = keyword_decisions.get(i, "")
            chosen_vid: str = ""
            choose_source = ""
            if kw_vid and kw_vid not in voice_to_speaker:
                chosen_vid = kw_vid
                choose_source = "keyword_fallback_after_llm_collision"
            else:
                # diversifier: 从池里挑未占用的同 gender
                turn_gender = str(t.get("voice_gender", "")).strip().lower()
                pool = _diversifier_pool.get(turn_gender, [])
                for cand in pool:
                    if cand and cand not in voice_to_speaker:
                        chosen_vid = cand
                        choose_source = "diversifier_pool_pick"
                        break
                if not chosen_vid:
                    # 池子也用尽 → 保持 LLM 重复决策
                    chosen_vid = vid
                    choose_source = "exhausted_keep_llm_dup"
            conflicts.append({
                "turn": i + 1,
                "speaker": sp,
                "reason": "voice_id_collision_with_other_speaker",
                "llm_chose": vid,
                "already_held_by": voice_to_speaker[vid],
                "resolved_to": chosen_vid,
                "resolved_source": choose_source,
            })
            llm_choices[i] = chosen_vid
            speaker_to_voice[sp] = chosen_vid
            if chosen_vid not in voice_to_speaker:
                voice_to_speaker[chosen_vid] = sp
            continue
        speaker_to_voice[sp] = vid
        voice_to_speaker[vid] = sp

    qa = {
        "mode": "adsd_voice_assign_llm_with_keyword_fallback",
        "llm_enabled": True,
        "total_turns": len(turns),
        "llm_assigned_count": len(llm_choices),
        "keyword_fallback_count": len(turns) - len(llm_choices),
        "conflicts_resolved": len(conflicts),
        "conflicts": conflicts,
        "speaker_to_voice_locked": speaker_to_voice,
        "per_turn": [],
    }
    for i, t in enumerate(turns):
        original = keyword_decisions.get(i, "")
        if i in llm_choices:
            new_id = llm_choices[i]
            if new_id == original:
                source = "llm_agrees_with_keyword"
            else:
                source = "llm"
            t["voice_asset_id"] = new_id
        else:
            source = "keyword_fallback"
        qa["per_turn"].append({
            "turn": i + 1,
            "speaker": t.get("speaker", ""),
            "voice_gender": t.get("voice_gender", ""),
            "emotion": t.get("emotion", "neutral"),
            "final_voice_asset_id": t.get("voice_asset_id", ""),
            "decision_source": source,
        })
    return qa


DEFAULT_MALE_VOICE_ASSET = os.environ.get("ADR_DEFAULT_MALE_VOICE_ASSET", ADSD_DEFAULT_MALE_VOICE_ASSET)
DEFAULT_FEMALE_VOICE_ASSET = os.environ.get("ADR_DEFAULT_FEMALE_VOICE_ASSET", ADSD_DEFAULT_FEMALE_VOICE_ASSET)
DEFAULT_VOICE_ASSET = os.environ.get("ADR_DEFAULT_VOICE_ASSET", "").strip()
VOICE_ASSET_AUDIO_DUB_EXPERIMENT = (
    not ADS_DIALOGUE_MODE
    and not NO_VOICE
    and "--no-voice-asset-audio-dub" not in sys.argv
    and "--no-almighty-audio-dub" not in sys.argv
    and os.environ.get("ADR_VOICE_ASSET_AUDIO_DUB", "1").strip().lower() not in ("0", "false", "no", "off")
)
VOICE_ASSET_AUDIO_DUB_RESOLUTION = os.environ.get("ADR_VOICE_ASSET_AUDIO_DUB_RESOLUTION", "720p").strip() or "720p"
VOICE_ASSET_AUDIO_DUB_PARTIAL_OK = (
    os.environ.get("ADR_VOICE_ASSET_AUDIO_DUB_PARTIAL_OK", "1").strip().lower() not in ("0", "false", "no", "off")
)
VOICE_ASSET_AUDIO_DUB_MIN_COVERAGE = min(1.0, max(0.0, float(os.environ.get("ADR_VOICE_ASSET_AUDIO_DUB_MIN_COVERAGE", "0.85"))))
MOTION_VISUAL_QA = (
    "--no-motion-visual-qa" not in sys.argv
    and os.environ.get("ADR_MOTION_VISUAL_QA", "1").strip().lower() not in ("0", "false", "no", "off")
)
MOTION_VISUAL_MIN_SCORE = float(os.environ.get("ADR_MOTION_VISUAL_MIN_SCORE", "1.2"))
MOTION_VISUAL_SAMPLE_FPS = max(1, int(os.environ.get("ADR_MOTION_VISUAL_SAMPLE_FPS", "3")))
MOTION_VISUAL_SAMPLE_WIDTH = max(64, int(os.environ.get("ADR_MOTION_VISUAL_SAMPLE_WIDTH", "160")))
MOTION_VISUAL_IGNORE_BOTTOM_RATIO = min(0.45, max(0.0, float(os.environ.get("ADR_MOTION_VISUAL_IGNORE_BOTTOM_RATIO", "0.22"))))
MOTION_VOICE_REPAIR = (
    "--motion-voice-repair" in sys.argv
    or "--voice-repair" in sys.argv
    or os.environ.get("ADR_MOTION_VOICE_REPAIR", "").strip().lower() in ("1", "true", "yes", "on")
)
MOTION_VOICE_STRICT_LOCK = (
    "--motion-voice-strict" in sys.argv
    or "--voice-strict" in sys.argv
    or os.environ.get("ADR_MOTION_VOICE_STRICT_LOCK", "1").strip().lower() not in ("0", "false", "no", "off")
)
WERYDANCE_CAPTIONS = (
    not NO_VOICE
    and "--with-ass-subtitles" not in sys.argv
    and "--no-werydance-captions" not in sys.argv
    # 默认关闭：WERYDANCE 偶尔不按 prompt 烧字幕，导致这些 turn 既不在 WERYDANCE caption 也不在 ASS 兜底，字幕真空
    # 需要时显式 set ADR_WERYDANCE_CAPTIONS=1 或加 --werydance-captions
    and (
        "--werydance-captions" in sys.argv
        or os.environ.get("ADR_WERYDANCE_CAPTIONS", "0").strip().lower() in ("1", "true", "yes", "on")
    )
)
WERYDANCE_CAPTION_MAX_CHARS = int(os.environ.get("ADR_WERYDANCE_CAPTION_MAX_CHARS", "24"))
ADSD_ONSITE_POV_MODE = (
    "--pov" in sys.argv
    or "--onsite-pov" in sys.argv
    or os.environ.get("ADR_ADSD_ONSITE_POV", "").strip().lower() in ("1", "true", "yes", "on")
)
ADSD_LIPS_CHANGE_REPAIR = (
    "--adsd-lips-change" in sys.argv
    or "--lips-change" in sys.argv
    or os.environ.get("ADR_ADSD_LIPS_CHANGE", "").strip().lower() in ("1", "true", "yes", "on")
)
ADSD_LIPS_CHANGE_ALL = (
    "--adsd-lips-change-all" in sys.argv
    or "--lips-change-all" in sys.argv
    or os.environ.get("ADR_ADSD_LIPS_CHANGE_ALL", "").strip().lower() in ("1", "true", "yes", "on")
)
if ADSD_LIPS_CHANGE_ALL:
    ADSD_LIPS_CHANGE_REPAIR = True

# --ads-reporter：把 ADS 的"拟现场第一人称记者感"并入 ADR 动态化。
# 该模式自动开启 --with-motion，并约束剧本、分镜与 motion prompt；
# 注意它是"拟现场报道"，不是现代直播，严禁手机/电视台/现代麦克风穿帮。
ADS_REPORTER_MODE = (
    "--no-ads-reporter" not in sys.argv
    and "--no-first-person-reporter" not in sys.argv
    and (
        "--ads-reporter" in sys.argv
        or "--first-person-reporter" in sys.argv
        or (
            os.environ.get("ADR_ADS_REPORTER_ALLOW_ENV", "").strip().lower() in ("1", "true", "yes", "on")
            and os.environ.get("ADR_ADS_REPORTER", "").strip().lower() in ("1", "true", "yes", "on")
        )
    )
)
if ADS_REPORTER_MODE:
    WITH_MOTION = True

# ADS/HADS/VADS 动态主路径：故事板是动作/叙事编舞蓝图，优先整组 clean refs 直喂 WeryDance。
# 逐镜 image-to-video / text-to-video 只做兜底。ADSD 口型模式仍保持独立，避免破坏口型同步。
ADS_STORYBOARD_FLOW_DEFAULT = (
    WITH_MOTION
    and not ADS_DIALOGUE_MODE
    and GPT_IMAGE2_STORYBOARD_GRID
    and "--no-storyboard-flow-main" not in sys.argv
    and os.environ.get("ADR_STORYBOARD_FLOW_MAIN", "1").strip().lower() not in ("0", "false", "no", "off")
)
if ADS_STORYBOARD_FLOW_DEFAULT:
    STORYBOARD_GRID_MULTIREF_MOTION = True
    STORYBOARD_GRID_MULTIREF_MAIN = True
    os.environ.setdefault("ADR_STORYBOARD_GRID_MULTIREF_GROUP", "12")
    os.environ.setdefault("ADR_GRID_MULTIREF_MAIN_MIN_PASS_RATIO", "0.75")

ADS_RETENTION_MODE = (
    "--no-ads-retention" not in sys.argv
    and "--no-retention" not in sys.argv
    and os.environ.get("ADR_ADS_RETENTION_MODE", "1").strip().lower() not in ("0", "false", "no", "off")
)

ADSD_MODE_NAME = ("VADSD" if IS_VERTICAL else "HADSD") if ADS_DIALOGUE_MODE else ""

# ADSD_VOICES / ADSD_MALE_VOICE_POOL / ADSD_FEMALE_VOICE_POOL 等
# 已抽到 adr_data/voices.py（顶部已 import）

# 同一 ADR 进程内角色名 → voice 持久映射，确保同一角色跨 turn 用同一声音
_ADSD_SPEAKER_VOICE_CACHE: dict[str, dict] = {}

ADS_REPORTER_SCRIPT_GUIDE = """

【ADS 第一人称历史讲解 POV 模式 · 最高优先级】
• 沉浸感只用于交代"我站在哪里、手里看到什么材料"，台词主体必须是白话历史解释。
• 每句优先回答 5W2H：什么时候、谁、在哪里、做了什么、为什么、怎么做、造成什么后果。
• 每 2~3 句给出一个具体地点或目击物（按主题时代适配），但地点/道具只能服务事实说明：
  - 1900-1949 历史现场 → 外交部门外、码头电报局、报馆、战壕后方、外公墙下
  - 1950-1999 → 编辑部、磁带间、长途电话亭、车间、广场
  - 现代（2000+）→ 办公室窗边、白板前、走廊、咖啡馆、机场、屏幕前的笔记本
• 叙事节奏：短句、现场感、事实优先；避免主播腔、综艺腔、PPT 念稿腔。
• 禁止诗化表达、隐喻、含蓄暗示、空泛金句；少说"时代洪流"，多说"哪一年谁做了什么"。
• 每句都要让普通观众不查资料也能听懂；遇到"二十一条、最后通牒、中立国、军需贷款、潜艇战、广义相对论"这类概念，要顺手解释一句。
• 结尾必须落在清楚判断上：这件事说明了什么历史关系，不能只用情绪化或文学化收束。
• 严禁现代直播、手机自拍、电视台演播室、无线麦、直播间、弹幕、"家人们"等综艺语汇。
"""

ADS_REPORTER_VISUAL_GUIDE = """

★★★ ADS 第一人称电影感 POV 视觉模式（最高优先级，启用 --ads-reporter 时必须执行）★★★

全片采用第一人称电影 POV 视角，沉浸式现场感。每条英文 prompt 必须同时包含 POV 锚点 + 电影摄影语言。

【POV 锚点 · 至少含一项】
• 第一人称镜头：POV first-person handheld / point-of-view shot / over-the-shoulder / through-viewfinder
• 第一人称身体进画面：own hands holding [notebook/telegram/document/keyboard/paper], own boots walking, looking down at lap, looking up at ceiling/banner
• 现场目击物占据前景：notebook page filling lower frame, camera viewfinder edge, window frame in foreground, hand reaching into frame, document edge

【电影摄影语言 · 至少含 1-2 项】
• 镜头：handheld shake, anamorphic lens flare, rack focus, dolly-in, push-in, whip-pan, slow zoom
• 颗粒/质感：16mm film grain, 35mm celluloid texture, light leak, vignette, halation
• 景深：shallow depth of field, foreground bokeh, in-focus subject mid-frame
• 光线：natural window light, dust motes in beam, golden-hour rim, candlelight glow, single-key chiaroscuro

【时代锚 · 按主题年代适配，不强行锁 1910 年代】
• 1900-1949 历史现场 → 战地记者 dispatch（新闻胶片颗粒、记者笔记本、电报纸、号外、电话局、外交衙门门外人群）
• 1950-1999 → 16mm 纪实风（手持胶片、监听电话、磁带、卷带打字机、长途电话亭、报刊亭）
• 现代题材（2000 后）→ 现代纪实 POV（笔记本电脑屏幕反光、便签贴、白板涂鸦、咖啡杯入画、走廊脚步、玻璃幕墙倒影、键盘前手部特写、屏幕滚动条 POV）
  现代场景**仍走 POV 第一人称纪实感**，绝不做主播大头出镜、综艺综艺综艺。

【硬禁条目 · 不分时代】
• 摄影棚灯、绿幕背景、PPT 切换感、卡通儿童插画、综艺背景板
• 第三人称主播大头出镜（这是 ADS 的反面）
• 现代直播设备特写（手机自拍杆、电视台 logo、直播按钮、弹幕滚动）
• 任何"演播室录制"质感

【跨地域/跨场景切换】
通过 POV 道具串联：地图上的手指、票根、电报、信件、白板更新、屏幕滚动、笔记本翻页。
让观众感觉是同一双眼睛在不同地方目击，而不是镜头在切。"""

ADS_RETENTION_SCRIPT_GUIDE = """

【ADS 播放量优先模式 · 非记者版 · 默认开启】
• 目标不是"现场记者感"，而是提高停留、完播、转发：第一句抓住人，中段不断续命，结尾能截图传播。
• 第 1 句必须 ≤ 24 个汉字，直接给出反常识 / 损失 / 危险 / 身份冲突 / 结果悬念；不要先交代年份地点。
• 第 2 句立刻落到具体人、物、决定或代价，不能继续卖关子。
• 每 3~4 句必须刷新一次注意力：新冲突、新后果、新证据、新选择、新反转，严禁连续铺背景。
• 中段必须安排一次"重新上钩"：用"真正的问题是..."、"但代价马上来了"、"谁也没想到..."这类句式把观众拉回来。
• 结尾必须留下可评论的问题或可转发判断，但不能编造事实、不能标题党造谣。
• 禁止低质流量词："震惊、全网、内幕、炸裂、家人们、速看、离谱到家"。
• 禁止记者口吻、直播口吻、电视台口吻；保留电影旁白和短视频叙事效率。
"""

ADS_RETENTION_VISUAL_GUIDE = """

★★★ ADS 播放量优先视觉模式（非记者版，默认开启）★★★
• 第 1 张图必须是 thumb-stopping frame：特写/极特写 + 强物件 + 人脸或手部动作 + 明确危险/欲望/损失，禁止慢悠悠远景开场。
• 前 3 张图必须形成"钩子三连"：冲突物件、关键人物、代价后果；让观众不用读字幕也知道有事发生。
• 每 3~4 张图必须换一次视觉能量：景别、角度、光影或动作状态至少变一个，避免连续静态人物半身像。
• 画面优先服务点击和完播：可截图、可做封面、可在小屏上看懂主体；不要堆复杂背景。
• 仍然遵守事实、年代、服饰、器物一致性；吸引播放量不等于制造穿帮或低质标题党。
"""

# --speaker <id[:name]> 指定 Podcast 音色（覆盖 VDAR 默认晓曼 / LLM 自选）
# 常用：gushijingling-720c0ae5:故事精灵（少儿）、chat-girl-105-cn:晓曼（温柔女声）、
#       gaoqing3-bfb5c88a:高晴（明亮女声）、liyan2-ef9401ec:国栋（沉稳男声）
SPEAKER_OVERRIDE_ID   = ""
SPEAKER_OVERRIDE_NAME = ""
for _i, _arg in enumerate(sys.argv):
    if _arg == "--speaker" and _i + 1 < len(sys.argv):
        _parts = sys.argv[_i + 1].split(":", 1)
        SPEAKER_OVERRIDE_ID = _parts[0].strip()
        SPEAKER_OVERRIDE_NAME = _parts[1].strip() if len(_parts) > 1 else SPEAKER_OVERRIDE_ID
        break

# --bottom-note "xxx" 一次性覆盖封面底部文化注脚（也可 env ADR_BOTTOM_NOTE）
BOTTOM_NOTE_OVERRIDE = ""
for _i, _arg in enumerate(sys.argv):
    if _arg == "--bottom-note" and _i + 1 < len(sys.argv):
        BOTTOM_NOTE_OVERRIDE = sys.argv[_i + 1].strip()
        break
if not BOTTOM_NOTE_OVERRIDE:
    BOTTOM_NOTE_OVERRIDE = os.environ.get("ADR_BOTTOM_NOTE", "").strip()

# --short-title "xxx" 一次性覆盖封面短标题（也可 env ADR_SHORT_TITLE）
SHORT_TITLE_OVERRIDE = ""
for _i, _arg in enumerate(sys.argv):
    if _arg == "--short-title" and _i + 1 < len(sys.argv):
        SHORT_TITLE_OVERRIDE = sys.argv[_i + 1].strip()
        break
if not SHORT_TITLE_OVERRIDE:
    SHORT_TITLE_OVERRIDE = os.environ.get("ADR_SHORT_TITLE", "").strip()

# 根据横竖屏设置分辨率参数
if IS_VERTICAL:
    ASPECT_RATIO = "9:16"
    VIDEO_W, VIDEO_H = 720, 1280
    SUBTITLE_FONTSIZE = 80
    SUBTITLE_MAX_CHARS = 8
else:
    ASPECT_RATIO = "16:9"
    VIDEO_W, VIDEO_H = 1280, 720
    SUBTITLE_FONTSIZE = 48
    SUBTITLE_MAX_CHARS = 16

ts = datetime.now().strftime("%Y%m%d_%H%M%S")
OUTPUT_DIR = Path(os.environ.get("OUTPUT_DIR", f"/tmp/adr_v8_{ts}"))
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

POLL_INTERVAL = 2  # 轮询间隔 2 秒（敏感发现完成）
POLL_MAX      = 300  # 最多轮询 300 次（约 10 分钟，保持总等待时间不变）

EMOTION_STYLE = {
    # ★ 设计原则：emotion 只调"情绪强度修饰"，不切换画风。全片画风由 producer STYLE_KEY 锁死。
    # 严禁人名（OpenAI GPT Image 2 对艺术家风格模仿强拒）。
    "悲壮": "stronger backlight rim glow, deeper shadow contrast, slightly cooler gray-blue accent, slower atmospheric haze",
    "紧张": "shallower depth of field, slight handheld micro-shake, more directional hard key light, deeper warm shadow",
    "孤独": "more negative space around subject, slightly cooler blue rim accent, fewer foreground elements, quieter mood",
    "辉煌": "warmer golden hour light, more sun-ray particles, slightly higher saturation in main subject, subtle low-angle hero feel",
    "压抑": "darker overall exposure, more shadow occupying frame, single tighter key light, contemplative stillness",
    "释然": "softer diffused light, gentle floating dust motes, slightly higher horizon airiness, calmer color balance",
}

# 轻松/儿童/治愈向题材专用情绪池：明亮、鲜艳、有希望感
EMOTION_STYLE_BRIGHT = {
    "欢快": "bright saturated colors, sunny natural light, cheerful wide composition, warm yellow and sky blue palette",
    "希望": "soft morning light, pastel palette, gentle uplifting composition, cream and mint tones, clear bright background",
    "温暖": "golden hour sunlight, cozy warm tones, family-scale composition, peach and honey palette",
    "童趣": "cartoon illustration style, playful primary colors, chunky simple shapes, candy pop palette, clean background",
    "活力": "vivid saturated colors, dynamic action composition, high-key lighting, orange and teal palette",
    "惊喜": "sparkle light accents, bright clean background, centered wonder composition, magenta and turquoise highlights",
}

# ── 工具函数 ─────────────────────────────────────────────────────────────────
def log(msg: str):
    print(f"[ADR V8] {msg}", flush=True)

_tg_lock = threading.Lock()
_tg_last_digest_ts = 0.0
_tg_suppressed_count = 0
_tg_suppressed_tail: list[str] = []
_tg_dashboard_message_id: int | None = None
_tg_dashboard_last_edit_ts = 0.0
_tg_dashboard_stage = 0
_tg_dashboard_recent: list[str] = []

_TG_DASHBOARD_STAGES = [
    ("启动", 2, [r"ADR V8 启动", r"开始处理"]),
    ("剧本", 12, [r"剧本就绪", r"现场台词就绪", r"外部脚本注入"]),
    ("制片", 18, [r"制片人准则就绪", r"画面提示词就绪"]),
    ("音轨", 28, [r"主音轨生成完毕", r"主音轨完成", r"音轨生成完毕"]),
    ("时间轴", 36, [r"时间轴", r"Whisper", r"BGM-driven 时间轴"]),
    ("故事板", 48, [r"storyboard", r"分镜", r"4K storyboard"]),
    ("素材", 58, [r"并行生成", r"图片", r"BGM 生成完毕", r"场景 QA"]),
    ("动态化", 74, [r"动态化启动", r"Motion prompts", r"动作桥接", r"口型同步启动"]),
    ("动态完成", 84, [r"动态化完成", r"口型同步 QA", r"WERYDANCE 渲染 QA", r"Grid multi-ref"]),
    ("合成", 91, [r"视频轨拼接完成", r"最终合成中", r"字幕"]),
    ("交付", 97, [r"成片输出完毕", r"发布门禁", r"社媒文案", r"封面"]),
    ("完成", 100, [r"全流程完成", r"耗时统计"]),
]

_TG_NOISY_PATTERNS = [
    r"^🖼 图片 \d+ 生成完毕",
    r"^🎬 分镜 \d+/\d+ 动态化 ✓",
    r"^👄 Turn \d+/\d+ 口型同步 ✓",
    r"^✅ 图 \d+/\d+ 已通过",
    r"^🔄 图 \d+/\d+ 被拒绝",
    r"^✏️ 图 \d+",
    r"^🎞 Previs page \d+",
    r"^🧪 Grid multi-ref \d+",
    r"^✅ Podcast 文本生成成功",
    r"^✅ Podcast 音频生成成功",
    r"^🎙 Podcast text 尝试",
    r"^⏳ \d+s 后重建 Podcast",
    r"^🎵 BGM 就绪:",
    r"^🎵 BGM-driven 复用 BGM:",
    r"^🎵 step9 BGM 正常传入:",
]

_TG_IMMEDIATE_PATTERNS = [
    r"^❌",
    r"^⚠️",
    r"^🎬 ADR V8 启动",
    r"^🎬 动态化启动",
    r"^✅ 剧本就绪",
    r"^✅ 主音轨",
    r"^✅ .*主音轨完成",
    r"^✅ 时间轴",
    r"^🧩 GPT Image 2 4K storyboard",
    r"^✅ 动作桥接关键帧完成",
    r"^✅ 动态化完成",
    r"^✅ 视频轨拼接完成",
    r"^🎬 最终合成中",
    r"^✅ 成片输出完毕",
    r"^✅ .*发布门禁通过",
    r"^📝 社媒文案",
    r"^🎨 正在生成主题专属封面",
    r"^✅ 全流程完成",
    r"^⏱ 耗时统计",
]


def _tg_send_raw(msg: str) -> dict | None:
    """向 Telegram 推送状态消息。"""
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage",
            json={"chat_id": TG_CHAT_ID, "text": msg},
            timeout=(10, 15),
        )
        if r.ok:
            return r.json()
        log(f"TG 推送失败: HTTP {r.status_code} {r.text[:160]}")
    except Exception as e:
        log(f"TG 推送失败: {e}")
    return None


def _tg_matches(msg: str, patterns: list[str]) -> bool:
    return any(re.search(p, msg, re.S) for p in patterns)


def _tg_summarize(msg: str) -> str:
    text = " ".join(str(msg).split())
    if len(text) > 110:
        text = text[:107] + "..."
    return text


def _tg_dashboard_stage_for(msg: str) -> int:
    text = str(msg)
    for idx, (_, _, patterns) in enumerate(_TG_DASHBOARD_STAGES):
        if any(re.search(p, text, re.I | re.S) for p in patterns):
            return idx
    return _tg_dashboard_stage


def _tg_progress_bar(percent: int, width: int = 18) -> str:
    pct = max(0, min(100, int(percent)))
    filled = round(width * pct / 100)
    return "█" * filled + "░" * (width - filled)


def _tg_dashboard_text(current_msg: str) -> str:
    stage_name, percent, _ = _TG_DASHBOARD_STAGES[_tg_dashboard_stage]
    bar = _tg_progress_bar(percent)
    title = _tg_summarize(TOPIC)
    recent = _tg_dashboard_recent[-5:]
    recent_lines = "\n".join(f"• {x}" for x in recent) if recent else "• 等待下一步..."
    updated = datetime.now().strftime("%H:%M:%S")
    return (
        f"🎛 ADR 任务进度\n"
        f"主题：{title}\n"
        f"阶段：{stage_name} · {percent}%\n"
        f"{bar}\n"
        f"当前：{_tg_summarize(current_msg)}\n\n"
        f"最近日志：\n{recent_lines}\n\n"
        f"更新时间：{updated}"
    )[:3900]


def _tg_dashboard_update(msg: str, *, force: bool = False):
    global _tg_dashboard_message_id, _tg_dashboard_last_edit_ts, _tg_dashboard_stage
    text = str(msg)
    _tg_dashboard_stage = max(_tg_dashboard_stage, _tg_dashboard_stage_for(text))
    summary = _tg_summarize(text)
    if not _tg_dashboard_recent or _tg_dashboard_recent[-1] != summary:
        _tg_dashboard_recent.append(summary)
    if len(_tg_dashboard_recent) > 12:
        del _tg_dashboard_recent[:-12]
    now = time.time()
    if _tg_dashboard_message_id and not force and now - _tg_dashboard_last_edit_ts < TG_DASHBOARD_EDIT_INTERVAL_SEC:
        log(f"[TG dashboard defer] {text}")
        return
    body = _tg_dashboard_text(text)
    if not _tg_dashboard_message_id:
        data = _tg_send_raw(body)
        try:
            _tg_dashboard_message_id = int(data.get("result", {}).get("message_id")) if data else None
        except Exception:
            _tg_dashboard_message_id = None
        _tg_dashboard_last_edit_ts = now
        if not _tg_dashboard_message_id:
            log("[TG dashboard] 无法创建进度面板，回退普通消息")
        return
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{TG_BOT_TOKEN}/editMessageText",
            json={"chat_id": TG_CHAT_ID, "message_id": _tg_dashboard_message_id, "text": body},
            timeout=(10, 15),
        )
        if not r.ok and "message is not modified" not in r.text.lower():
            log(f"TG 进度面板更新失败: HTTP {r.status_code} {r.text[:160]}")
        _tg_dashboard_last_edit_ts = now
    except Exception as e:
        log(f"TG 进度面板更新失败: {e}")


def _tg_maybe_digest(force: bool = False):
    global _tg_last_digest_ts, _tg_suppressed_count, _tg_suppressed_tail
    if TG_PROGRESS_MODE != "compact" or _tg_suppressed_count <= 0:
        return
    now = time.time()
    if not force and now - _tg_last_digest_ts < TG_DIGEST_INTERVAL_SEC:
        return
    tail = _tg_suppressed_tail[-6:]
    lines = "\n".join(f"• {x}" for x in tail)
    _tg_send_raw(f"📌 进度摘要：已合并 {_tg_suppressed_count} 条过程信息\n{lines}")
    _tg_last_digest_ts = now
    _tg_suppressed_count = 0
    _tg_suppressed_tail = []


def tg(msg: str):
    """Telegram 状态推送。默认 dashboard：单条可编辑进度面板。"""
    global _tg_suppressed_count, _tg_suppressed_tail
    text = str(msg)
    if TG_PROGRESS_MODE in ("0", "off", "silent", "none"):
        log(f"[TG silent] {text}")
        return
    if TG_PROGRESS_MODE in ("verbose", "full", "debug"):
        _tg_send_raw(text)
        return
    if TG_PROGRESS_MODE in ("dashboard", "panel", "progress"):
        with _tg_lock:
            force = _tg_matches(text, _TG_IMMEDIATE_PATTERNS) or _tg_matches(text, [r"^❌", r"^⚠️"])
            _tg_dashboard_update(text, force=force)
        return
    with _tg_lock:
        if _tg_matches(text, _TG_IMMEDIATE_PATTERNS):
            _tg_maybe_digest(force=True)
            _tg_send_raw(text)
            return
        _tg_suppressed_count += 1
        _tg_suppressed_tail.append(_tg_summarize(text))
        if len(_tg_suppressed_tail) > 12:
            _tg_suppressed_tail = _tg_suppressed_tail[-12:]
        log(f"[TG compact] {text}")
        if not _tg_matches(text, _TG_NOISY_PATTERNS):
            _tg_maybe_digest(force=False)


# 全局节流：任意两次 WeryAI POST 请求轻微错峰，避免多线程精确同一时刻打上游。
_api_lock = threading.Lock()
_api_last_ts = 0.0
API_MIN_INTERVAL = 0.2  # 真并发：WeryAI 支持 20 并发，错峰 200ms 避免精确同时（vs 5.0 串行节流的 25× 加速）

# 图片生成的限制点是 submit 请求频率，不是后台任务并发数。单独限制 text-to-image
# 提交节奏，后续 poll/download/render 仍可并发跑。
_image_submit_lock = threading.Lock()
_image_last_submit_ts = 0.0
IMAGE_SUBMIT_MIN_INTERVAL = float(os.environ.get("ADR_IMAGE_SUBMIT_INTERVAL", "2.5"))
IMAGE_RATE_LIMIT_BACKOFF = float(os.environ.get("ADR_IMAGE_RATE_LIMIT_BACKOFF", "15"))

# WERYDANCE text-to-video 的 submit 频率限制比普通后台并发更敏感。
# 单独节流 submit；后续 poll/download 仍并发，避免把 20 路 worker 全串行化。
_motion_submit_lock = threading.Lock()
_motion_last_submit_ts = 0.0
MOTION_SUBMIT_MIN_INTERVAL = float(os.environ.get("ADR_MOTION_SUBMIT_INTERVAL", "2.5"))
MOTION_RATE_LIMIT_BACKOFF = float(os.environ.get("ADR_MOTION_RATE_LIMIT_BACKOFF", "30"))


def _wait_image_submit_slot(label: str = ""):
    global _image_last_submit_ts
    if IMAGE_SUBMIT_MIN_INTERVAL <= 0:
        return
    with _image_submit_lock:
        elapsed = time.time() - _image_last_submit_ts
        wait_s = max(0.0, IMAGE_SUBMIT_MIN_INTERVAL - elapsed)
        if wait_s > 0:
            log(f"{label} text-to-image submit 节流等待 {wait_s:.1f}s")
            time.sleep(wait_s)
        _image_last_submit_ts = time.time()


def _wait_motion_submit_slot(label: str = ""):
    global _motion_last_submit_ts
    if MOTION_SUBMIT_MIN_INTERVAL <= 0:
        return
    with _motion_submit_lock:
        elapsed = time.time() - _motion_last_submit_ts
        wait_s = max(0.0, MOTION_SUBMIT_MIN_INTERVAL - elapsed)
        if wait_s > 0:
            log(f"{label} WERYDANCE submit 节流等待 {wait_s:.1f}s")
            time.sleep(wait_s)
        _motion_last_submit_ts = time.time()


def _is_rate_limited_error(exc: Exception) -> bool:
    text = str(exc).lower()
    return (
        "rate limit" in text
        or "请求频率" in text
        or '"status": 1001' in text
        or "'status': 1001" in text
    )


def _is_rate_limited_response(resp: dict) -> bool:
    if not isinstance(resp, dict):
        return False
    text = json.dumps(resp, ensure_ascii=False).lower()
    return (
        resp.get("status") == 1001
        or "request rate limit exceeded" in text
        or "rate limit" in text
        or "请求频率" in text
    )


def submit_text_to_image(payload: dict, label: str, timeout: int = 45, max_attempts: int | None = None) -> dict:
    attempts = max_attempts or max(1, int(os.environ.get("ADR_IMAGE_SUBMIT_RETRIES", "5")))
    base_backoff = max(1.0, float(os.environ.get("ADR_IMAGE_RATE_LIMIT_BACKOFF", str(IMAGE_RATE_LIMIT_BACKOFF))))
    last_resp: dict | None = None
    last_err: Exception | None = None
    for attempt in range(attempts):
        if attempt > 0:
            wait_s = min(180.0, base_backoff * attempt)
            log(f"{label} text-to-image submit 重试 {attempt+1}/{attempts}，等待 {wait_s:.1f}s")
            time.sleep(wait_s)
        try:
            _wait_image_submit_slot(f"{label} submit")
            resp = req_post("/generation/text-to-image", payload, timeout=timeout)
            last_resp = resp
            if _is_rate_limited_response(resp):
                log(f"{label} text-to-image submit 限频: {json.dumps(resp, ensure_ascii=False)[:180]}")
                continue
            return resp
        except Exception as e:
            last_err = e
            if _is_rate_limited_error(e):
                log(f"{label} text-to-image submit 限频异常: {type(e).__name__}: {str(e)[:160]}")
                continue
            raise
    if last_resp is not None:
        raise RuntimeError(f"{label} text-to-image submit retries exhausted: {json.dumps(last_resp, ensure_ascii=False)[:240]}")
    raise RuntimeError(f"{label} text-to-image submit retries exhausted: {last_err}")


def req_post(path: str, payload: dict, timeout: int = 30) -> dict:
    global _api_last_ts
    with _api_lock:
        elapsed = time.time() - _api_last_ts
        if elapsed < API_MIN_INTERVAL:
            time.sleep(API_MIN_INTERVAL - elapsed)
        _api_last_ts = time.time()
    r = requests.post(f"{BASE_URL}{path}", json=payload, headers=HEADERS, timeout=timeout)
    r.raise_for_status()
    if not r.text.strip():
        raise RuntimeError(f"API 返回空响应 ({r.status_code}): {path}")
    return r.json()


def req_get(path: str, timeout: int = 15) -> dict:
    r = requests.get(f"{BASE_URL}{path}", headers=HEADERS, timeout=timeout)
    return r.json()


# ── TG 上传 probe-gap 检测共用 helper ──
# 用前后两条静默 probe 文本消息的 message_id 跳号，识别 SSL 假阴性（实际上传成功但 client 抛错）。
# 用于 sendVideo / sendPhoto 等大 payload 上传场景。
def _tg_probe_send(label: str) -> int | None:
    if not TG_BOT_TOKEN or not TG_CHAT_ID:
        return None
    try:
        rp = requests.post(
            f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage",
            data={
                "chat_id": TG_CHAT_ID,
                "text": f"·{label}·",
                "disable_notification": "true",
            },
            timeout=15,
        )
        if rp.status_code == 200:
            return rp.json().get("result", {}).get("message_id")
    except Exception as e:
        log(f"TG probe '{label}' 发送失败：{e}")
    return None


def _tg_probe_delete(message_id: int | None) -> None:
    if not message_id or not TG_BOT_TOKEN or not TG_CHAT_ID:
        return
    try:
        requests.post(
            f"https://api.telegram.org/bot{TG_BOT_TOKEN}/deleteMessage",
            data={"chat_id": TG_CHAT_ID, "message_id": message_id},
            timeout=10,
        )
    except Exception:
        pass


def _tg_upload_with_probe_gap(
    upload_fn,
    *,
    probe_label_prefix: str,
    max_attempts: int = 2,
    retry_sleep_seconds: float = 5.0,
) -> dict:
    """带 probe-gap 假阴性检测的 TG 上传通用 wrapper。
    upload_fn() 应返回 dict {ok: bool, message_id: int|None, exception: Exception|None}。
    若 upload_fn 抛异常，自动用前后 probe 跳号检测 chat 是否已收到消息。
    返回 {ok: bool, source: str, message_id: int|None, attempts: int}
    """
    last_exc: Exception | None = None
    for attempt in range(max_attempts):
        probe_before = _tg_probe_send(f"{probe_label_prefix}-start-{attempt+1}")
        try:
            result = upload_fn()
            if result.get("ok"):
                _tg_probe_delete(probe_before)
                return {"ok": True, "source": "direct", "message_id": result.get("message_id"), "attempts": attempt + 1}
            last_exc = result.get("exception")
        except Exception as e:
            last_exc = e
        # 异常路径：probe gap 检测
        time.sleep(3)
        probe_after = _tg_probe_send(f"{probe_label_prefix}-check-{attempt+1}")
        if probe_before is not None and probe_after is not None:
            gap = probe_after - probe_before
            if gap >= 2:
                log(f"{probe_label_prefix}: probe-gap={gap} → 上传已落地，本地异常为假阴性")
                _tg_probe_delete(probe_after)
                _tg_probe_delete(probe_before)
                return {"ok": True, "source": "probe_gap_detected", "message_id": None, "attempts": attempt + 1}
        _tg_probe_delete(probe_after)
        _tg_probe_delete(probe_before)
        if attempt < max_attempts - 1:
            time.sleep(retry_sleep_seconds)
    return {"ok": False, "source": "all_failed", "message_id": None, "attempts": max_attempts, "last_exception": str(last_exc) if last_exc else None}


def poll(task_id: str, label: str = "") -> dict:
    """轮询任务状态直到 succeed 或 fail，返回最终 data 字典。"""
    for i in range(POLL_MAX):
        time.sleep(POLL_INTERVAL)
        try:
            resp = req_get(f"/generation/{task_id}/status")
            data = resp.get("data", {})
            status = data.get("task_status", "")
            if status in ("succeed", "success"):
                return data
            if status in ("fail", "failed", "canceled"):
                raise RuntimeError(f"{label} 任务失败: {json.dumps(data, ensure_ascii=False)[:200]}")
        except RuntimeError:
            raise
        except Exception as e:
            log(f"轮询异常 ({label}): {e}")
    raise RuntimeError(f"{label} 轮询超时")


PODCAST_TEXT_TIMEOUT = float(os.environ.get("ADR_PODCAST_TEXT_TIMEOUT", "200"))
PODCAST_AUDIO_TIMEOUT = float(os.environ.get("ADR_PODCAST_AUDIO_TIMEOUT", "400"))
PODCAST_TEXT_POLL_MAX = max(1, int(PODCAST_TEXT_TIMEOUT / POLL_INTERVAL))
PODCAST_AUDIO_POLL_MAX = max(1, int(PODCAST_AUDIO_TIMEOUT / POLL_INTERVAL))


def poll_podcast(task_id: str, wait_for: str = "text-success", max_polls: int | None = None) -> dict:
    """Podcast 专用轮询：按文档要求检查 content_status 而非 task_status。"""
    if max_polls is None:
        max_polls = POLL_MAX
    for i in range(max_polls):
        time.sleep(POLL_INTERVAL)
        try:
            resp = req_get(f"/generation/{task_id}/status")
            data = resp.get("data", {})
            cs = data.get("content_status", "")
            log(f"[Podcast] poll #{i+1}: task_status={data.get('task_status')} content_status={cs}")
            if cs == wait_for:
                return data
            if cs in ("text-fail", "audio-fail"):
                raise RuntimeError(f"Podcast {cs}: {json.dumps(data, ensure_ascii=False)[:200]}")
        except RuntimeError:
            raise
        except Exception as e:
            log(f"Podcast 轮询异常: {e}")
    raise RuntimeError(f"Podcast 轮询超时（等待 {wait_for}, {max_polls * POLL_INTERVAL}s）")


def poll_task_status(task_id: str, label: str = "task", max_wait: float = 180.0) -> dict:
    """Poll generic WeryAI generation task by task_status."""
    polls = max(1, int(max_wait / POLL_INTERVAL))
    for i in range(polls):
        time.sleep(POLL_INTERVAL)
        try:
            resp = req_get(f"/generation/{task_id}/status")
            data = resp.get("data", {})
            st = data.get("task_status", "")
            if i == 0 or (i + 1) % 5 == 0 or st in ("succeed", "failed"):
                log(f"[{label}] poll #{i+1}: task_status={st}")
            if st == "succeed":
                return data
            if st == "failed":
                raise RuntimeError(f"{label} failed: {json.dumps(data, ensure_ascii=False)[:300]}")
        except RuntimeError:
            raise
        except Exception as e:
            log(f"{label} 轮询异常: {e}")
    raise RuntimeError(f"{label} 轮询超时（{max_wait:.0f}s）")


def poll_storyboard_task(task_id: str, label: str, max_wait: float) -> dict:
    """GPT Image 2 storyboard poller with bounded wait and periodic progress logs."""
    polls = max(1, int(max_wait / POLL_INTERVAL))
    log_every = max(1, int(30 / POLL_INTERVAL))
    last_status = ""
    for i in range(polls):
        time.sleep(POLL_INTERVAL)
        try:
            resp = req_get(f"/generation/{task_id}/status")
            data = resp.get("data", {})
            status = data.get("task_status", "")
            last_status = status or last_status
            if i == 0 or (i + 1) % log_every == 0 or status in ("succeed", "success", "fail", "failed", "canceled"):
                elapsed = (i + 1) * POLL_INTERVAL
                log(f"[{label}] poll #{i+1}: task_status={status or 'unknown'} elapsed={elapsed}s/{max_wait:.0f}s")
            if status in ("succeed", "success"):
                return data
            if status in ("fail", "failed", "canceled"):
                raise RuntimeError(f"{label} failed: {json.dumps(data, ensure_ascii=False)[:300]}")
        except RuntimeError:
            raise
        except Exception as e:
            log(f"{label} 轮询异常: {e}")
    raise RuntimeError(f"{label} 轮询超时（{max_wait:.0f}s, last_status={last_status or 'unknown'}）")


def chat(model: str, system: str, user: str, max_tokens: int = 4096, timeout: int = 180) -> str:
    """调用 WeryAI Chat Completion，返回回复文本。3 次重试防瞬断/限流/无 choices。
    timeout 默认 180s，对慢推理模型（GPT-5.4 / Claude Opus / DeepSeek-R1）需传更大值如 600s。"""
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user",   "content": user},
        ],
        "max_tokens": max_tokens,
        "temperature": 0.85,
    }
    last_err = None
    for attempt in range(3):
        try:
            resp = req_post("/chat/completions", payload, timeout=timeout)
            if isinstance(resp, dict) and resp.get("choices"):
                return resp["choices"][0]["message"]["content"].strip()
            last_err = f"响应无 choices: {json.dumps(resp, ensure_ascii=False)[:200]}"
            log(f"[chat/{model}] 尝试 {attempt+1}/3 响应异常: {last_err}")
        except Exception as e:
            last_err = f"{type(e).__name__}: {e}"
            log(f"[chat/{model}] 尝试 {attempt+1}/3 异常: {last_err}")
        if attempt < 2:
            time.sleep(3 * (attempt + 1))  # 退避 3s / 6s
    raise RuntimeError(f"chat({model}) 3 次重试全失败: {last_err}")


def pick_image_model(aspect: str) -> tuple[str, str, dict]:
    """根据画幅选最优的 text-to-image 模型 + 参数。
    GPT_IMAGE_2（OpenAI）：横屏 / 方形 / 2:3 / 4:3 — 画质强 + quality=high
    SEEDREAM_4_5（字节豆包）：9:16 / 3:4 竖屏 — 中文渲染优秀 + 4k
    GEMINI_3_1_FLASH_IMAGE（Nano Banana 2）：冷门比例回退
    返回：(model, aspect_ratio_str, extra_payload_dict)
    """
    # 分流准则（攻克 OpenAI 黑名单 phrasing 后版）：
    # • 真正的触发词不是题材/民族，是 "in the cinematic style of [DIRECTOR_NAME]" phrasing
    #   → OpenAI GPT Image 2 强制拒绝艺术家风格模仿（版权 policy）
    #   → ADR 姜文 prompt + EMOTION_STYLE 已全部清洗为纯描述词，不含具体导演/画家名
    # • 现在 GPT_IMAGE_2 可作为统一主力（9:16 / 16:9 / 3:4(用 2:3) / 1:1）
    # • SEEDREAM_4_5 / Nano Banana 2 仅作 fallback
    if aspect == "16:9":
        return "GPT_IMAGE_2", "16:9(2k)", {"quality": "high"}
    if aspect == "9:16":
        return "GPT_IMAGE_2", "9:16(4k)", {"quality": "high"}
    if aspect == "3:4":
        # GPT Image 2 已新增 3:4 原生支持
        return "GPT_IMAGE_2", "3:4", {"quality": "high"}
    if aspect in ("1:1", "2:3", "4:3"):
        return "GPT_IMAGE_2", aspect, {"quality": "high"}
    return "GEMINI_3_1_FLASH_IMAGE", aspect, {}


def detect_topic_meta(topic: str) -> dict:
    """LLM 一次性判定题材的文化背景、年代、导演风格、视觉母题。
    输出供姜文阶段和 Python 硬注入使用，解决西方题材被中国化的文化错位。"""
    prompt = f"""分析以下视频题材，返回严格 JSON：

题材：{topic}

必填字段（每条都必须给出明确答案，不能模糊）：
{{
  "culture": "chinese / western / japanese / other",
  "region": "具体地域（如 英国伦敦 / 西班牙马德里 / 中国江南 / 日本京都）",
  "era": "具体年代（如 1616年伊丽莎白晚期 / 晚清民国 / 1970年代美国 / 古罗马）",
  "director": "★ 严禁返回任何具体导演/艺术家/画家姓名！只返回视觉风格描述（10-25 词英文）。从以下风格类型选最匹配的并扩展：'epic silhouette composition with storm backlighting and heavy film grain' / 'saturated color-block composition with symmetric framing' / 'Zen contemplative cinematography with soft warm tones' / 'handheld neon-lit profile close-up with shallow depth' / 'historical sepia documentary realism' / 'dramatic chiaroscuro with single harsh key light'",
  "period_visual": "该年代该文化的核心视觉母题（3-5 个英文关键词，逗号分隔。例：'quill pen, parchment, candle flame, ruff collar, Elizabethan theater' 或 'bamboo scroll, bronze incense burner, silk robe, courtyard'）",
  "period_costume": "该年代该文化的人物形象描述（英文 1 句。例：'Caucasian British men in Elizabethan ruff collars and dark doublets, period-accurate 17th century' 或 'Han Chinese scholars in blue changshan robes'）",
  "negative": "必须排除的错位元素（英文，逗号分隔。例：'no East-Asian faces, no modern Chinese elements, no anachronistic setting' 或 'no Western figures, no Caucasian faces, no European architecture'）"
}}
只输出 JSON，不加任何说明文字。"""
    try:
        raw = chat("GEMINI_25_FLASH", "你是历史考证与电影视觉风格专家，只输出 JSON。", prompt, max_tokens=600)
        s = raw.find('{'); e = raw.rfind('}')
        meta = json.loads(raw[s:e+1])
        if is_1919_global_topic(topic):
            meta = apply_1919_global_guardrails(meta)
        log(f"题材分析：culture={meta.get('culture')} region={meta.get('region')} era={meta.get('era')} director={meta.get('director')}")
        return meta
    except Exception as ex:
        log(f"题材分析失败（fallback 到中国默认）: {ex}")
        if any(k in topic for k in ("英国", "伦敦", "乔治", "伊丽莎白", "威斯敏斯特", "欧洲", "美国", "法国", "德国", "西班牙")):
            meta = {
                "culture": "western", "region": "英国伦敦" if any(k in topic for k in ("英国", "伦敦", "威斯敏斯特", "乔治", "伊丽莎白")) else "西方",
                "era": "",
                "director": "historical sepia documentary realism, restrained royal ceremony framing, period-accurate interiors",
                "period_visual": "stone cathedral, royal regalia, formal uniforms, clergy robes, city crowds",
                "period_costume": "Caucasian British people in period-accurate Western formal dress, uniforms, coats and hats",
                "negative": "no East-Asian faces, no Chinese architecture, no hanfu, no qipao, no pagoda, no Chinese palace roof, no red lanterns, no Chinese calligraphy, no ink-wash style",
            }
        else:
            meta = {
                "culture": "chinese", "region": "中国", "era": "",
                "director": "Zen contemplative cinematography, deep focus, soft warm tones, horizontal natural composition",
                "period_visual": "bamboo scroll, red lacquer, traditional Chinese architecture, ink wash",
                "period_costume": "Han Chinese people in traditional attire",
                "negative": "no Western figures, no Caucasian faces, no European architecture",
            }
        if is_1919_global_topic(topic):
            meta = apply_1919_global_guardrails(meta)
        return meta


def _topic_culture_guard(meta: dict) -> str:
    culture = str((meta or {}).get("culture") or "").lower()
    region = str((meta or {}).get("region") or "")
    era = str((meta or {}).get("era") or "")
    if "western" in culture or any(k in region for k in ("英国", "伦敦", "欧洲", "美国", "法国", "德国", "西班牙")):
        return (
            f"Western historical accuracy lock: {region}, {era}. "
            "Use period-accurate Western/Caucasian faces, European architecture, local uniforms, coats, hats, clergy, and civic interiors. "
            "Absolutely no Chinese architecture, no East-Asian faces, no hanfu, no qipao, no changshan, no Chinese robes, no pagoda, "
            "no Chinese palace roof, no red lanterns, no Chinese calligraphy, no Chinese seals, no bamboo scrolls, no ink-wash Chinese style."
        )
    if "japanese" in culture or "日本" in region:
        return (
            f"Japanese historical accuracy lock: {region}, {era}. "
            "Use period-accurate Japanese people, architecture, clothing, props, and local visual motifs. "
            "No Chinese palace roofs, no hanfu, no qipao, no European royal court, no Western cathedral unless the topic explicitly requires it."
        )
    if "chinese" in culture or "中国" in region:
        return (
            f"Chinese historical accuracy lock: {region}, {era}. "
            "Use period-accurate Chinese faces, clothing, architecture, props, and local visual motifs. "
            "No Western royal court, no European cathedral, no Caucasian historical figures unless the topic explicitly requires it."
        )
    return f"Historical accuracy lock: {region}, {era}. Keep faces, clothing, architecture, props, and written motifs local to the topic."


def _write_cultural_visual_qa(script: list[dict], meta: dict) -> None:
    culture = str((meta or {}).get("culture") or "").lower()
    region = str((meta or {}).get("region") or "")
    guard = _topic_culture_guard(meta)
    expected = "western" if ("western" in culture or any(k in region for k in ("英国", "伦敦", "欧洲", "美国", "法国", "德国", "西班牙"))) else culture or "unknown"
    if expected == "western":
        required = ("Western historical accuracy lock", "no Chinese architecture", "no East-Asian faces")
    elif expected == "chinese":
        required = ("Chinese historical accuracy lock", "No Western royal court")
    elif expected == "japanese":
        required = ("Japanese historical accuracy lock", "No Chinese palace roofs")
    else:
        required = ("Historical accuracy lock",)

    missing: list[dict] = []
    image_missing: list[int] = []
    for idx, scene in enumerate(script, start=1):
        prompt = str(scene.get("prompt") or "")
        absent = [token for token in required if token not in prompt]
        if absent:
            missing.append({"scene": idx, "missing_tokens": absent})
        img_path = Path(str(scene.get("img_path") or ""))
        if not img_path.exists() or img_path.stat().st_size <= 10000:
            image_missing.append(idx)

    payload = {
        "mode": "cultural_visual_prompt_guard",
        "expected_culture": expected,
        "region": region,
        "guard": guard,
        "total": len(script),
        "prompt_guard_missing": missing,
        "image_missing_or_too_small": image_missing,
        "pass": not missing and not image_missing,
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }
    qa_path = OUTPUT_DIR / "cultural_visual_qa.json"
    try:
        qa_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as e:
        log(f"cultural_visual_qa.json 写入失败: {e}")
    if payload["pass"]:
        tg(f"✅ 文化一致性 QA：{expected} / {region} 提示词闸门已覆盖 {len(script)} 张图")
    else:
        tg(f"⚠️ 文化一致性 QA：发现 {len(missing)} 条提示词缺口、{len(image_missing)} 张图片缺失，已记录 {qa_path.name}")


def is_1919_global_topic(topic: str) -> bool:
    keys = ("1919", "五四", "巴黎和会", "凡尔赛", "三一运动", "阿姆利则", "民族觉醒")
    return any(k in topic for k in keys)


# topic 里常带的提示性修饰词（如"严格按史实"），不应进入封面短标题
_TOPIC_MODIFIERS = [
    "严格按史实", "严格按历史", "按史实", "按照史实", "符合史实", "符合历史",
    "真实历史", "真实事件", "详细介绍", "详细讲解", "完整版", "深度解析",
]

def _strip_topic_modifiers(text: str) -> str:
    """剥离 topic 中给 LLM 的提示性修饰词，仅用于面向观众的展示场景（短标题/caption）。"""
    if not text:
        return text
    out = text
    for m in _TOPIC_MODIFIERS:
        out = out.replace(m, "")
    out = re.sub(r"\s+", " ", out).strip(" 　，,.、；;:：—-")
    return out


# tone → 封面 Pantone 色卡覆盖（庄重历史题材不再被节气色卡跳色干扰）
_TONE_PANTONE_OVERRIDE = {
    "庄重": {"hex": "#2C2C2C", "code": "MK-9.10", "name": "苍墨"},
    "怀旧": {"hex": "#D4A642", "code": "GD-10.30", "name": "暖金"},
}


def apply_1919_global_guardrails(meta: dict) -> dict:
    """1919/五四全球史题材的历史视觉硬约束，避免新中国时期元素穿帮。"""
    updated = dict(meta)
    updated["culture"] = "global 1919 / Chinese Republican-era plus European and colonial contexts"
    updated["region"] = "北京天安门广场、巴黎凡尔赛、朝鲜京城、印度旁遮普、埃及开罗"
    updated["era"] = "1919年，一战结束后的民国八年与全球殖民地民族运动时期"
    updated["director"] = (
        "post-war archival documentary realism, muted monochrome sepia, newspaper texture, "
        "crowd silhouettes, hand-held reportage tension"
    )
    updated["period_visual"] = (
        "1919 student petitions, plain Tiananmen gate before 1949 decoration, Paris conference tables, "
        "colonial police lines, newspapers, telegrams, cloth banners with period slogans"
    )
    updated["period_costume"] = (
        "1919 Chinese students in long gowns, early Republican jackets and cloth shoes; "
        "European diplomats in dark morning coats; Korean, Indian and Egyptian civilians in period-accurate local clothing"
    )
    extra_negative = (
        "no Mao portrait, no PRC national flag, no five-star red flag, no People's Heroes Monument, "
        "no modern Tiananmen decorations, no post-1949 red political slogans, no Communist-era uniforms, "
        "no Cultural Revolution imagery, no modern LED screens, no modern cars, no skyscrapers, "
        "no simplified post-1949 propaganda poster style"
    )
    old_negative = updated.get("negative", "")
    updated["negative"] = f"{old_negative}, {extra_negative}" if old_negative else extra_negative
    return updated


def build_1919_global_cover_prompt(short_title: str) -> str:
    """1919 全球史题材封面：保留中华万年历视频号封面结构，只替换历史插画内容。"""
    return (
        "A 3:4 vertical Chinese almanac video-account cover, Kinfolk editorial aesthetic, "
        "must preserve the established Zhonghua Wannianli cover structure. "
        "Background: warm aged cream paper #F7EFD6 fading to pale sage, subtle old newspaper grain, "
        "restrained sepia ink-wash texture, generous negative space, elegant Chinese editorial layout. "
        "At the very top edge, horizontally centered: exactly ONE dark-charcoal rounded iPhone Dynamic Island pill, "
        "containing white Chinese text \"中华万年历\" and one tiny green-leaf icon. "
        "Top-right corner: a compact PANTONE-style color swatch chip with thin cream border, "
        "upper 60% muted brass #D4A642, lower 40% cream strip with small text \"PANTONE\" / \"1919\" / \"觉醒金\". "
        "Center rows 2-3, 85% width: render the exact Chinese title "
        f"\"{short_title}\" once only, heavy-bold Chinese Song-ti serif, deep ink #1A1A1A, soft cream outline, "
        "balanced as one or two centered lines, never cropped. "
        "Directly below the main title: a small cream pill with dark sepia text \"1919年5月4日 · 民国八年\". "
        "Middle-lower illustration area: refined ink-wash archival vignette, not a poster collage: "
        "a wooden desk with a 1919 newspaper, a telegram strip, a student petition, a small old world map, "
        "and tiny sepia photo cuttings hinting at pre-1949 Tiananmen, Paris Peace Conference, Korea March First, "
        "Amritsar and Cairo; all elements are secondary, soft, and integrated into the almanac layout. "
        "Very bottom center: small warm sepia-brown Chinese brush calligraphy line \"风起五四，万里同声\", "
        "flanked by two small red seal dots. "
        "Strict structure rule: no dark bottom title bar, no full-page event index, no chaotic museum-wall collage, "
        "no single-person hero poster, no TIME magazine logo, no ADR logo, no large black footer. "
        "Absolute historical accuracy: no Mao portrait, no PRC flag, no five-star flag, no People's Heroes Monument, "
        "no post-1949 Tiananmen decorations or slogans, no Communist-era uniforms, no Cultural Revolution imagery, "
        "no modern cars, LED screens, skyscrapers, watermarks, duplicated title, cropped Chinese characters."
    )


def build_shot_blueprint(n: int) -> list[str]:
    """按分镜号硬生成电影级镜头模板（景别+机位+光影+母题）。
    Python 层直接拼到每句 prompt 前，绕过 LLM 对镜头语法的软性遵从。"""
    blueprint = []
    for i in range(n):
        pos = i / max(n - 1, 1)
        if i == 0:
            shot = "extreme close-up macro shot of a single symbolic object, shallow depth of field, hard key light carving deep shadows, anamorphic lens flare, 35mm film grain"
        elif i == 1:
            shot = "extreme close-up of an eye or a trembling hand, rim light from side, razor-shallow depth, dramatic chiaroscuro, suspenseful spaghetti-western tension"
        elif pos < 0.3:
            shot = "low-angle medium shot with backlit silhouette, strong rim light from behind, atmospheric haze and dust motes, moody shadow"
        elif pos < 0.5:
            shot = "Dutch angle wide shot, chiaroscuro single-key lighting, smoke or embers drifting through frame, cinemascope 2.39:1, unbalanced composition"
        elif pos < 0.7:
            shot = "over-the-shoulder shot with shallow depth of field, profile side view, classical triangle facial lighting, moody low-key atmosphere"
        elif pos < 0.85:
            shot = "low-angle hero shot, silhouette against strong backlight, dramatic sky or flame motif, banner or fabric flapping in wind"
        elif i == n - 1:
            shot = "extreme wide shot silhouette against sunset or dramatic sky, vast negative space, lone figure at frame edge, dust motes swirling in golden light beam"
        else:
            shot = "medium close-up framed through window or mirror reflection, rim light from side, shallow depth, contemplative stillness"
        blueprint.append(shot)
    return blueprint


def ffprobe_duration(path: str) -> float:
    out = subprocess.check_output(
        ["ffprobe", "-v", "error",
         "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1",
         path],
        stderr=subprocess.DEVNULL,
    )
    return float(out.decode().strip())


def ffprobe_video_size(path: str) -> tuple[int | None, int | None]:
    try:
        out = subprocess.check_output(
            [
                "ffprobe", "-v", "error",
                "-select_streams", "v:0",
                "-show_entries", "stream=width,height",
                "-of", "csv=s=x:p=0",
                path,
            ],
            stderr=subprocess.DEVNULL,
        )
        text = out.decode().strip()
        if "x" not in text:
            return None, None
        w, h = text.split("x", 1)
        return int(w), int(h)
    except Exception:
        return None, None


def _video_decode_probe(path: str, frames: int = 3) -> bool:
    try:
        result = subprocess.run(
            [
                "ffmpeg", "-v", "error",
                "-i", path,
                "-map", "0:v:0",
                "-frames:v", str(frames),
                "-f", "null", "-",
            ],
            capture_output=True,
            timeout=30,
        )
        return result.returncode == 0
    except Exception:
        return False


def ffmpeg(*args, timeout: int = 120):
    """ffmpeg 包装：默认 120s timeout 防止损坏图/坏文件让进程无限挂起。
    单图转视频段调用方应传 timeout=30；长视频合成传 timeout=600。"""
    cmd = ["ffmpeg", "-y"] + list(args)
    try:
        result = subprocess.run(cmd, capture_output=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"ffmpeg 超时 ({timeout}s)，命令：{' '.join(cmd)[:200]}")
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg 失败: {result.stderr.decode()[-300:]}")


# ── 第一步：双导演生成剧本 ────────────────────────────────────────────────────
def _extract_json_array(raw: str) -> list:
    fence = re.search(r'```(?:json)?\s*([\s\S]*?)```', raw)
    text = fence.group(1).strip() if fence else raw.strip()
    start = text.find("[")
    end = text.rfind("]")
    if start < 0 or end <= start:
        raise ValueError(f"no JSON array: {raw[:200]}")
    return json.loads(text[start:end + 1])


def _extract_json_object(raw: str) -> dict:
    fence = re.search(r'```(?:json)?\s*([\s\S]*?)```', raw)
    text = fence.group(1).strip() if fence else raw.strip()
    start = text.find("{")
    end = text.rfind("}")
    if start < 0 or end <= start:
        raise ValueError(f"no JSON object: {raw[:200]}")
    return json.loads(text[start:end + 1])


def _voice_for_speaker(speaker: str, gender: str | None = None) -> dict:
    """优先用 LLM 提供的 gender（'male'/'female'）选 voice 池；
    其次按中文角色词关键字命中；最后未知名按 hash 分到男声池（避免全掉女声 News Anchor）。
    同一 speaker 首次分配后写入 cache，后续 turn 复用。"""
    cache_key = f"{speaker}|{gender or ''}"
    if cache_key in _ADSD_SPEAKER_VOICE_CACHE:
        return _ADSD_SPEAKER_VOICE_CACHE[cache_key]
    # 同名 speaker 已有任意 gender 分配过，直接复用（防止同名跨 gender 反复改）
    for k, v in _ADSD_SPEAKER_VOICE_CACHE.items():
        if k.startswith(f"{speaker}|"):
            _ADSD_SPEAKER_VOICE_CACHE[cache_key] = v
            return v

    g = (gender or "").strip().lower()
    if g == "female":
        voice = ADSD_FEMALE_VOICE_POOL[abs(hash(speaker)) % len(ADSD_FEMALE_VOICE_POOL)]
    elif g == "male":
        voice = ADSD_MALE_VOICE_POOL[abs(hash(speaker)) % len(ADSD_MALE_VOICE_POOL)]
    elif speaker in ADSD_VOICES:
        voice = ADSD_VOICES[speaker]
    elif "旁白" in speaker or speaker.lower() in ("narrator", "voiceover", "vo"):
        # 旁白默认走男声沉稳叙述，避免短视频女声错位（如需女声旁白显式 voice_gender=female 即可）
        voice = ADSD_MALE_VOICE_POOL[abs(hash(speaker)) % len(ADSD_MALE_VOICE_POOL)]
    elif any(k in speaker for k in ("少年", "青年", "士人", "书生", "学生", "百姓", "船工", "兵士", "亲历者", "见证人")):
        voice = ADSD_VOICES["记者"]
    elif any(k in speaker for k in ("职员", "官员", "朝臣", "僧", "长者", "将领", "书吏", "幕僚", "使者", "父老", "寺")):
        voice = ADSD_VOICES["职员"]
    elif any(k in speaker for k in ("女", "娘", "姐", "嫂", "母", "婆", "妇")):
        voice = ADSD_FEMALE_VOICE_POOL[abs(hash(speaker)) % len(ADSD_FEMALE_VOICE_POOL)]
    else:
        voice = ADSD_MALE_VOICE_POOL[abs(hash(speaker)) % len(ADSD_MALE_VOICE_POOL)]

    _ADSD_SPEAKER_VOICE_CACHE[cache_key] = voice
    return voice


def _adsd_gender_from_voice(voice: dict | None) -> str:
    try:
        vid = int((voice or {}).get("voice_id"))
    except Exception:
        return ""
    return ADSD_VOICE_GENDER_BY_ID.get(vid, "")


def _adsd_infer_gender_from_speaker(speaker: str) -> str:
    s = str(speaker or "")
    if any(k in s for k in ("女", "王后", "王妃", "夫人", "小姐", "女士", "母", "娘", "姐", "嫂", "婆", "妇")):
        return "female"
    if any(k in s for k in ("男", "国王", "王", "皇帝", "侍从", "记者", "市民", "士兵", "官", "臣", "父", "兄", "叔", "伯", "爷", "僧")):
        return "male"
    return ""


def _adsd_gender_lock_phrase(gender: str | None) -> str:
    g = (gender or "").strip().lower()
    if g == "female":
        return (
            "VOICE-VISUAL GENDER LOCK: the active speaker's TTS voice is FEMALE, so render the active speaker as an adult woman/female-presenting person. "
            "No beard, no male jawline, no masculine body silhouette, no male-presenting face."
        )
    if g == "male":
        return (
            "VOICE-VISUAL GENDER LOCK: the active speaker's TTS voice is MALE, so render the active speaker as an adult man/male-presenting person. "
            "No female face, no feminine body silhouette, no makeup, no dress-coded female styling."
        )
    return "VOICE-VISUAL GENDER LOCK: keep the active speaker's apparent gender consistent with the assigned TTS voice."


def _adsd_visual_subject_has_gender_conflict(visual_subject: str, voice_gender: str | None) -> bool:
    text = str(visual_subject or "").lower()
    g = (voice_gender or "").strip().lower()
    female_words = ("woman", "female", "girl", "lady", "queen", "mother", "actress", "wife", "auntie")
    male_words = ("man", "male", "boy", "gentleman", "king", "father", "actor", "husband", "uncle")
    if g == "male":
        return any(w in text for w in female_words) and not any(w in text for w in male_words)
    if g == "female":
        return any(w in text for w in male_words) and not any(w in text for w in female_words)
    return False


def _adsd_default_roles(topic: str) -> tuple[str, str]:
    roles = _adsd_role_candidates(topic)
    return roles[0], roles[1] if len(roles) > 1 else roles[0]


def _adsd_allows_media_role(topic: str) -> bool:
    explicit = ("明确记者", "记者角色", "记者采访", "新闻采访", "战地记者", "拟现场记者", "记者出镜", "主持人")
    negative = ("不要记者", "不设记者", "没有记者", "无记者", "避免记者", "不要主持人", "不设主持人")
    if any(k in topic for k in negative):
        return False
    return ADS_REPORTER_MODE or any(k in topic for k in explicit)


def _adsd_role_candidates(topic: str) -> list[str]:
    if any(k in topic for k in ("同泰寺", "佛", "僧", "梁武帝", "萧衍", "寺")):
        return ["寺中僧人", "朝廷官员", "梁朝文士", "寺外百姓"]
    if any(k in topic for k in ("公车上书", "康有为", "梁启超", "科举", "上书")):
        return ["上书士人", "旁观官员", "在京举人", "书吏"]
    if any(k in topic for k in ("郑成功", "鹿耳门", "台湾", "海", "潮")):
        return ["水师兵士", "海边百姓", "船上将领", "地方父老"]
    if any(k in topic for k in ("二十一条", "最后通牒", "外交", "条约")):
        return ["街头见证人", "衙署官员", "报馆学生", "电报员"]
    if any(k in topic for k in ("画报", "报馆", "石印", "申报", "新闻图像")):
        return ["画师", "报馆编辑", "印工", "街边茶客"]
    if any(k in topic for k in ("三国", "归晋", "晋", "魏", "蜀", "吴")):
        return ["军中亲历者", "地方官吏", "归降士兵", "城中百姓"]
    return ["现场见证人", "知情讲述人", "当事人", "旁观百姓"]


def _adsd_dialogue_shape(speakers: list[str]) -> str:
    count = len([s for s in dict.fromkeys(speakers) if s])
    if count <= 1:
        return "monologue"
    if count == 2:
        return "dialogue"
    return "ensemble"


def _finalize_adsd_turns(turns: list[dict]) -> list[dict]:
    speakers = [t["speaker"] for t in turns if t.get("speaker")]
    shape = _adsd_dialogue_shape(speakers)
    speaker_count = len(dict.fromkeys(speakers))
    for turn in turns:
        turn["dialogue_shape"] = shape
        turn["speaker_count"] = speaker_count
        # P3 音色库智能匹配：未显式设置 voice_asset_id 的 turn 自动按 speaker name 命中音色库
        if not turn.get("voice_asset_id"):
            turn["voice_asset_id"] = _voice_asset_id_for_speaker(
                turn.get("speaker", ""),
                turn.get("voice_gender") or turn.get("gender"),
            )
        # A-roll / B-roll 自动判定：旁白类默认 B-roll voice-over，其他默认 A-roll lip-sync
        if "needs_lip_sync" not in turn:
            turn["needs_lip_sync"] = _infer_needs_lip_sync(
                turn.get("speaker", ""),
                turn.get("text", ""),
                turn.get("emotion", ""),
            )
        # 三类 turn 区分：a_roll / narrated_b / silent_b
        if not turn.get("turn_type"):
            turn["turn_type"] = _infer_turn_type(
                turn.get("speaker", ""),
                turn.get("text", ""),
                turn.get("emotion", ""),
                turn.get("turn_type_hint", ""),
            )
        # silent_b 的 needs_lip_sync 强制 False（保证下游 A-roll 路径不会误进）
        if turn["turn_type"] == "silent_b":
            turn["needs_lip_sync"] = False
    return turns


def _parse_adsd_override_turns(raw_lines: list[str], topic: str) -> list[dict]:
    """Parse /tmp/adr_script_override.txt into ADSD turns.

    Supported formats:
    - 纯台词: treated as monologue by the default onsite role.
    - 角色：台词 / 角色: 台词: preserves up to four onsite speakers.
    """
    import re as _re
    role_candidates = _adsd_role_candidates(topic)
    fallback_role = role_candidates[0]
    known: list[str] = []
    turns: list[dict] = []
    # silent_b 单行标记：(silent) / [silent] / 空 visual hint
    SILENT_LINE_RE = _re.compile(r"^[\[\(]?\s*silent\s*[\]\)]?(?:\s*:\s*(.*))?$", _re.IGNORECASE)
    for i, raw in enumerate(raw_lines):
        line = str(raw).strip()
        silent_match = SILENT_LINE_RE.match(line)
        if silent_match or line in {"(silent)", "[silent]", "(无)", "空镜"}:
            visual_hint = (silent_match.group(1) if silent_match else "").strip() if silent_match else ""
            speaker = "(silent)"
            text = ""
            voice_gender = "male"
            voice = _voice_for_speaker(speaker, voice_gender)
            inferred_emotion = "neutral"
            shot_desc = visual_hint or "空镜 + 环境氛围呼吸位"
            turns.append({
                "dialogue_turn": i + 1,
                "speaker": speaker,
                "voice_gender": voice_gender,
                "speaker_id": voice["voice_id"],
                "speaker_name": voice["voice_name"],
                "voice_asset_id": ADSD_GENDER_FALLBACK_VOICE_ASSET.get("male", ADSD_DEFAULT_MALE_VOICE_ASSET),
                "needs_lip_sync": False,
                "turn_type": "silent_b",
                "text": "",
                "shot": shot_desc,
                "emotion": inferred_emotion,
                "broll_rule": "environmental",
                "duration_hint": 4.0,
                "injected_script": True,
            })
            continue
        m = _re.match(r"^([^：:]{2,12})[：:]\s*(.+)$", line)
        if m:
            speaker = m.group(1).strip()
            text = m.group(2).strip()
        else:
            speaker = known[0] if known else fallback_role
            text = line
        if not speaker:
            speaker = known[i % len(known)] if known else fallback_role
        if speaker not in known and len(known) < 4:
            known.append(speaker)
        elif speaker not in known:
            speaker = known[i % len(known)] if known else fallback_role
        if not text:
            raise RuntimeError(f"ADSD 注入脚本第 {i+1} 行为空")
        inferred_gender = _adsd_infer_gender_from_speaker(speaker)
        voice = _voice_for_speaker(speaker, inferred_gender or None)
        voice_gender = inferred_gender or _adsd_gender_from_voice(voice) or "male"
        voice_asset_id = _voice_asset_id_for_speaker(speaker, voice_gender)
        needs_lip_sync = _infer_needs_lip_sync(speaker, text)
        shot_desc = (
            f"{speaker}在现场说出这一句，旁人只作倾听或反应"
            if needs_lip_sync
            else f"voice-over：画面展示与「{text[:40]}」相关的场景，镜头自由运动，无需出现说话人正脸"
        )
        inferred_emotion = _infer_emotion_from_text(text, speaker)
        turn_type = _infer_turn_type(speaker, text, inferred_emotion)
        turns.append({
            "dialogue_turn": i + 1,
            "speaker": speaker,
            "voice_gender": voice_gender,
            "speaker_id": voice["voice_id"],
            "speaker_name": voice["voice_name"],
            "voice_asset_id": voice_asset_id,
            "needs_lip_sync": needs_lip_sync if turn_type != "silent_b" else False,
            "turn_type": turn_type,
            "text": text,
            "shot": shot_desc,
            "emotion": inferred_emotion,
            "injected_script": True,
        })
    return _finalize_adsd_turns(turns)


_TIMECODE_RANGE_RE = re.compile(
    r"(?P<start>\d{1,2}:\d{2}(?::\d{2})?)\s*[-–—]\s*(?P<end>\d{1,2}:\d{2}(?::\d{2})?)"
)


def _parse_timecode_seconds(value: str) -> float:
    parts = [float(p) for p in str(value).split(":")]
    if len(parts) == 2:
        return parts[0] * 60 + parts[1]
    if len(parts) == 3:
        return parts[0] * 3600 + parts[1] * 60 + parts[2]
    raise ValueError(f"bad timecode: {value}")


def _clean_override_line_text(text: str) -> str:
    text = re.sub(r"\s+", " ", str(text or "")).strip()
    text = text.strip(" \t\r\n\"'“”‘’")
    return text.strip()


def _parse_override_script_text(raw_text: str) -> tuple[list[str], list[dict | None]]:
    """Parse manual script input; timecode-only lines are metadata, never narration."""
    records: list[dict] = []
    pending_time: dict | None = None
    for raw in str(raw_text or "").splitlines():
        line = raw.strip()
        if not line:
            continue
        m = _TIMECODE_RANGE_RE.search(line)
        timing = None
        text = line
        if m:
            timing = {
                "start": _parse_timecode_seconds(m.group("start")),
                "end": _parse_timecode_seconds(m.group("end")),
                "label": m.group(0).replace("–", "-").replace("—", "-"),
            }
            text = _clean_override_line_text((line[:m.start()] + " " + line[m.end():]).strip())
            if not text:
                if records and not records[-1].get("timing"):
                    records[-1]["timing"] = timing
                else:
                    pending_time = timing
                continue
        text = _clean_override_line_text(text)
        if not text:
            continue
        records.append({"text": text, "timing": timing or pending_time})
        pending_time = None
    lines = [r["text"] for r in records if r.get("text")]
    timings = [r.get("timing") for r in records if r.get("text")]
    return lines, timings


def _adsd_pov_contract() -> str:
    return (
        "Onsite observer POV: the viewer feels physically present in the historical scene, standing at eye level "
        "beside the speaker, near a doorway, table edge, pier, street crowd, temple hall, office corridor, or army tent. "
        "Use first-person documentary camera language such as over-the-shoulder from the crowd edge, shoulder-level handheld sway, "
        "foreground documents or doorframes, and nearby listener reactions. Keep the active speaker's face and mouth readable. "
        "Let the role and framing stay immersive for the topic era; avoid making the viewer feel outside the scene unless the topic calls for it."
    )


def _generate_adsd_dialogue_turns(topic: str, num_turns: int, tone: str, style_guide: str) -> list[dict]:
    """Generate ADSD dialogue turns. Each turn becomes one TTS unit and one video segment.

    三类 turn (silent_b PR):
      a_roll       说话人特写 + 对白 (主导)
      narrated_b   旁白 + 空镜/远景/剪影 (开场/结尾/关键转场，全片 ≤ 3)
      silent_b     无对白 + 空镜呼吸位 (中段呼吸，仅 BGM)
    """
    num_turns = max(4, min(12, num_turns))
    role_candidates = _adsd_role_candidates(topic)
    role_hint = " / ".join(role_candidates)
    fallback_role = role_candidates[0]
    # narrated_b 全片硬上限：3（开场+结尾+最多 1 个关键转场）
    max_narrated = min(3, num_turns // 4 + 2)
    # silent_b 占比目标：20%-35%
    min_silent = max(1, int(num_turns * 0.20))
    max_silent = max(min_silent + 1, int(num_turns * 0.35))

    def _build_prompt(retry_hint: str = "") -> str:
        retry_block = f"\n【重试提醒】上一次输出违反约束：{retry_hint}\n请严格按以下规则重新生成。\n" if retry_hint else ""
        return f"""你是 ADSD 纪录片编剧。{retry_block}
主题：「{topic}」
目标：生成 {num_turns} 句视听节奏合理的纪录片镜头脚本。

【纪录片节奏铁律】
旁白是「框架 + 标点」，不是「主体」。
让说话人自己讲故事，让画面自己呼吸。
不要每个镜头都塞旁白——观众会出戏。

【三类 turn 区分】
a_roll      说话人特写镜头 + 对白 + 角色音色
            画面：说话人面部/半身入镜
            用于：表达观点、冲突、情感
            必须有 text

narrated_b  旁白衔接镜头 + 空镜/远景/剪影 + 旁白音色
            画面：可以有人但禁止嘴部特写
                  推荐：剪影 / 背影 / 远景 / 群像 / 雕像 / 历史画卷
            用于：开场 setup / 关键转场 / 结尾收口
            必须有 text
            speaker = "旁白"

silent_b    氛围呼吸镜头 + 仅 BGM
            画面：场景空镜 / 物件特写 / 环境氛围 / 远景人影
            用于：中段呼吸 / 情绪沉淀 / 节奏调节
            text = ""
            speaker = "(silent)"
            时长 3-6 秒（短）

【硬约束】
1. turn 1 必须是 narrated_b（开场 setup）
2. turn {num_turns} 必须是 narrated_b（结尾收口）
3. narrated_b 全片 ≤ {max_narrated} 个（含开场+结尾）
4. silent_b 数量 ∈ [{min_silent}, {max_silent}]
5. 任意两个 narrated_b 间距 ≥ 3 turn
6. 中段（turn 2~{num_turns-1}）以 a_roll 为主，穿插 silent_b
7. narrated_b 仅在「真转场」用：时间大跳 / 地点大跳 / 视角切换

【可用现场角色方向】（用于 a_roll，按题材微调，必须是题材内部的人）
{role_hint}

【输出字段】每项必须包含：
- turn_type    "a_roll" | "narrated_b" | "silent_b"
- speaker      a_roll: 角色名；narrated_b: "旁白"；silent_b: "(silent)"
- voice_gender "male" | "female"；silent_b 写 "male"（不会用到，但保持字段）
- visual_subject 12-30 词英文角色外形描述（同 speaker 跨 turn 一致；silent_b 写场景外形）
- text         a_roll/narrated_b 中文对白 18-36 字；silent_b 写 ""
- shot         中文画面描述（具体到地点/道具/动作）
                a_roll: speaker 入镜说话
                narrated_b: 必须写「无嘴部特写」类构图 (剪影/背影/远景/群像/雕像/画卷)
                silent_b: 写空镜/物件/环境氛围
- emotion      neutral / tense / solemn / explanatory（silent_b 写 "neutral"）
- duration_hint 数字，秒
                a_roll: 自适应（按 text 长度估算 3-10）
                narrated_b: 6-12
                silent_b: 3-6
- broll_rule   仅 narrated_b/silent_b 填，单选：
                narrated_b: silhouette | back_view | wide_shot | crowd | statue | historical_painting
                silent_b:   empty_scene | object_close_up | environmental | distant_figure
                a_roll: 写 ""

【画面禁忌】（narrated_b / silent_b）
✗ 不能有「角色对镜头说话」
✗ 不能有「嘴部特写」
✗ 不能有「角色直接看镜头并张嘴」

【语言风格】
{style_guide}

【输出格式】严格 JSON 数组，不要 Markdown，不要解释。

【示例输出（混合三类）】
[
  {{"turn_type":"narrated_b","speaker":"旁白","voice_gender":"male","visual_subject":"a documentary narrator voice","text":"这是开场的旁白设定背景。","shot":"远景城墙 + 士兵剪影行进，无嘴部特写","emotion":"solemn","duration_hint":8,"broll_rule":"silhouette"}},
  {{"turn_type":"a_roll","speaker":"{fallback_role}","voice_gender":"male","visual_subject":"an adult Han Chinese man, dark robe, late Han era","text":"这件事必须现在做，不能再等。","shot":"室内案前，{fallback_role} 正脸入镜说话，半身","emotion":"tense","duration_hint":4,"broll_rule":""}},
  {{"turn_type":"silent_b","speaker":"(silent)","voice_gender":"male","visual_subject":"an empty palace hall, dust in light beam","text":"","shot":"洛阳宫殿空镜，光影缓慢流转，无人","emotion":"neutral","duration_hint":4,"broll_rule":"empty_scene"}}
]"""

    def _validate(arr: list[dict]) -> str:
        if len(arr) != num_turns:
            return f"句数不匹配：got {len(arr)}, need {num_turns}"
        tts = [str((x or {}).get("turn_type", "")).strip().lower() for x in arr]
        if tts[0] != "narrated_b":
            return "turn 1 必须是 narrated_b（开场）"
        if tts[-1] != "narrated_b":
            return f"turn {num_turns} 必须是 narrated_b（结尾）"
        n_narrated = sum(1 for t in tts if t == "narrated_b")
        if n_narrated > max_narrated:
            return f"narrated_b 数量 {n_narrated} 超过上限 {max_narrated}"
        n_silent = sum(1 for t in tts if t == "silent_b")
        if not (min_silent <= n_silent <= max_silent):
            return f"silent_b 数量 {n_silent} 不在 [{min_silent}, {max_silent}]"
        last_narrated = -10
        for i, t in enumerate(tts):
            if t == "narrated_b":
                if i - last_narrated < 3:
                    return f"narrated_b 间距违反：turn {last_narrated+1} 和 turn {i+1} 距离 < 3"
                last_narrated = i
        return ""

    arr: list[dict] = []
    last_err = ""
    for attempt in range(2):
        raw = chat("GEMINI_3_1_FLASH_LITE", "你只输出严格 JSON 数组。", _build_prompt(last_err), max_tokens=3000, timeout=180)
        try:
            arr = _extract_json_array(raw)
        except Exception as e:
            last_err = f"JSON 解析失败：{e}"
            continue
        last_err = _validate(arr)
        if not last_err:
            break
        log(f"ADSD script-gen 重试 #{attempt+1}：{last_err}")

    # 仍违反 → 强制后处理（多余 narrated_b → silent_b；缺少 silent_b → 改 narrated_b 为 silent）
    if last_err and arr:
        log(f"ADSD script-gen LLM 重试失败仍违反 ({last_err})，进入强制后处理")
        narrated_idxs = [i for i, x in enumerate(arr) if str((x or {}).get("turn_type", "")).lower() == "narrated_b"]
        # 保留首尾 narrated_b，中段超额转 silent_b
        keep = set([0, num_turns - 1])
        for idx in narrated_idxs:
            if idx in keep:
                continue
            if len([i for i in narrated_idxs if i in keep]) >= max_narrated:
                arr[idx] = {**arr[idx], "turn_type": "silent_b", "speaker": "(silent)", "text": "", "broll_rule": "environmental"}
            else:
                keep.add(idx)
        # 重新检查
        last_err2 = _validate(arr)
        if last_err2:
            log(f"ADSD script-gen 强制后处理仍违反：{last_err2}，使用原结果继续（下游兼容）")
    if not arr:
        raise RuntimeError(f"ADSD 脚本生成失败：{last_err}")
    if len(arr) != num_turns:
        raise RuntimeError(f"ADSD 对话句数不匹配：got {len(arr)}, need {num_turns}")
    turns = []
    speakers_seen: list[str] = []
    # 同一 speaker 跨 turn 锁定 voice_gender + visual_subject（首次出现以 LLM 给的为准）
    speaker_gender_map: dict[str, str] = {}
    speaker_visual_map: dict[str, str] = {}
    for i, item in enumerate(arr):
        turn_type_raw = str(item.get("turn_type", "")).strip().lower()
        if turn_type_raw not in ("a_roll", "narrated_b", "silent_b"):
            # 旧 LLM 未给 turn_type：按 speaker/text 推断
            turn_type_raw = _infer_turn_type(str(item.get("speaker", "")), str(item.get("text", "")))
        is_silent = (turn_type_raw == "silent_b")
        is_narrated = (turn_type_raw == "narrated_b")

        speaker = str(item.get("speaker", "")).strip()
        if is_silent:
            speaker = "(silent)"
        elif is_narrated:
            speaker = "旁白" if not speaker or speaker == "(silent)" else speaker
        if not speaker:
            speaker = speakers_seen[i % len(speakers_seen)] if speakers_seen else fallback_role
        # silent_b / narrated_b 的 speaker 不挤占 a_roll 的 4 个 speaker 配额
        if not is_silent and not is_narrated:
            if speaker not in speakers_seen and len(speakers_seen) < 4:
                speakers_seen.append(speaker)
            elif speaker not in speakers_seen:
                speaker = speakers_seen[i % len(speakers_seen)] if speakers_seen else fallback_role
        text = str(item.get("text", "")).strip()
        shot = str(item.get("shot", "")).strip()
        emotion = str(item.get("emotion", "neutral")).strip().lower()
        if emotion not in _SUPPORTED_EMOTIONS:
            emotion = "neutral"
        broll_rule = str(item.get("broll_rule", "")).strip().lower()
        try:
            duration_hint = float(item.get("duration_hint", 0) or 0)
        except Exception:
            duration_hint = 0.0
        if duration_hint <= 0:
            duration_hint = 4.0 if is_silent else (8.0 if is_narrated else 5.0)

        gender_raw = str(item.get("voice_gender") or item.get("gender") or "").strip().lower()
        if gender_raw not in ("male", "female"):
            gender_raw = ""
        if speaker in speaker_gender_map:
            voice_gender = speaker_gender_map[speaker]
        else:
            voice_gender = gender_raw or "male"
            speaker_gender_map[speaker] = voice_gender

        vs_raw = str(item.get("visual_subject") or "").strip()
        if len(vs_raw.split()) < 4 or len(vs_raw) > 300:
            vs_raw = ""
        if speaker in speaker_visual_map and speaker_visual_map[speaker]:
            visual_subject = speaker_visual_map[speaker]
        else:
            visual_subject = vs_raw
            if visual_subject:
                speaker_visual_map[speaker] = visual_subject

        # silent_b 允许 text 为空；a_roll/narrated_b 必须有 text
        if is_silent:
            text = ""
        else:
            if not text or len(text) > 80:
                raise RuntimeError(f"ADSD 第 {i+1} 句台词异常：{text}")
        voice = _voice_for_speaker(speaker, voice_gender)
        turns.append({
            "dialogue_turn": i + 1,
            "turn_type": turn_type_raw,
            "speaker": speaker,
            "voice_gender": voice_gender,
            "visual_subject": visual_subject,
            "speaker_id": voice["voice_id"],
            "speaker_name": voice["voice_name"],
            "text": text,
            "shot": shot or (f"空镜 + 环境氛围" if is_silent else (f"无嘴部特写：剪影/远景/群像" if is_narrated else f"{speaker}在现场说明材料")),
            "emotion": emotion,
            "broll_rule": broll_rule,
            "duration_hint": duration_hint,
            "needs_lip_sync": (not is_silent and not is_narrated),
        })
    speakers = [t["speaker"] for t in turns if t.get("speaker")]
    shape = _adsd_dialogue_shape(speakers)
    speaker_count = len(dict.fromkeys(speakers))
    for turn in turns:
        turn["dialogue_shape"] = shape
        turn["speaker_count"] = speaker_count
    return _adsd_immersion_qa_rewrite_turns(topic, turns, role_candidates)


def _adsd_immersion_qa_rewrite_turns(topic: str, turns: list[dict], role_candidates: list[str]) -> list[dict]:
    """Use LLM judgment to keep ADSD roles immersive without hard-banning period news roles."""
    try:
        # silent_b / narrated_b 不参与 immersion QA：silent 没台词、narrated 是旁白不算「现场角色」
        compact = [
            {
                "speaker": t.get("speaker", ""),
                "voice_gender": t.get("voice_gender") or t.get("gender", ""),
                "visual_subject": t.get("visual_subject", ""),
                "text": t.get("text", ""),
                "shot": t.get("shot", ""),
            }
            for t in turns
            if _resolve_turn_type(t) == "a_roll"
        ]
        if not compact:
            return _finalize_adsd_turns(turns)
        prompt = f"""你是历史短视频 ADSD 的沉浸感审稿人。判断角色是否让观众跳戏。

主题：{topic}
候选时代内部角色：{" / ".join(role_candidates)}
当前 turns：
{json.dumps(compact, ensure_ascii=False)}

判断标准：
1. 允许时代内部的报馆人、画师、通讯员、战地通信人员、当事人、见证人。
2. 不要用关键词硬判；只判断整体观感是否像时代内部人物自然说话，还是像脱离现场的节目形式。
3. “记者”不是天然禁止；如果它在题材时代内部合理且不形成现代采访感，可以保留。
4. 如果某个 speaker/shot 会破坏沉浸感，请替换为更贴合时代现场的人物，但不要改台词含义。
5. 输出严格 JSON：{{"pass": true/false, "replacements": {{"原speaker":"新speaker"}}, "reasons": ["..."]}}
"""
        raw = chat("GEMINI_3_1_FLASH_LITE", "你只输出严格 JSON 对象。", prompt, max_tokens=900, timeout=90)
        obj = _extract_json_object(raw)
        replacements = obj.get("replacements") if isinstance(obj, dict) else None
        if not isinstance(replacements, dict) or not replacements:
            return _finalize_adsd_turns(turns)
        changed = False
        speaker_gender_map: dict[str, str] = {}
        for turn in turns:
            old = str(turn.get("speaker", "")).strip()
            new = str(replacements.get(old, "")).strip()
            if not new or new == old:
                continue
            turn["speaker"] = new[:12]
            turn["shot"] = str(turn.get("shot", "")).replace(old, turn["speaker"]) or f"{turn['speaker']}在现场说明材料"
            gender = str(turn.get("voice_gender") or turn.get("gender", "")).strip().lower()
            voice = _voice_for_speaker(turn["speaker"], gender if gender in ("male", "female") else None)
            turn["speaker_id"] = voice["voice_id"]
            turn["speaker_name"] = voice["voice_name"]
            changed = True
        if changed:
            log(f"ADSD 沉浸感 QA 替换角色：{replacements}")
        return _finalize_adsd_turns(turns)
    except Exception as e:
        log(f"ADSD 沉浸感 QA 跳过：{e}")
        return _finalize_adsd_turns(turns)


def _adsd_visual_contract(speaker: str, lip_sync: bool | None = None, gender: str | None = None, visual_subject: str | None = None) -> str:
    """Prompt contract for ADSD: keep the active speaker visually accountable.

    主路径：用 LLM 给的 visual_subject 作为锚（任何形态：人/动物/机器人/抽象）。
    兜底：visual_subject 缺失/过短时，按 voice_gender 套 ADULT MAN/WOMAN GENDER LOCK。
    """
    if lip_sync is None:
        lip_sync = ADSD_LIP_SYNC_EXPERIMENT
    vs = (visual_subject or "").strip()
    gender_lock = _adsd_gender_lock_phrase(gender)
    if vs and len(vs.split()) >= 4:
        # LLM 主路径：直接用 visual_subject 锁定外形
        anchor = (
            f"Active speaker is {vs}, internally identified as '{speaker}' for voice continuity only; do not render this name as text. "
            f"{gender_lock} "
            f"APPEARANCE LOCK: render this exact subject consistently across every scene; "
            f"the same speaker name must always have the same appearance/species/form. "
            "Show as the clear speaking subject inside the period scene, face/head readable in three-quarter view, "
            "with any other onsite characters only listening or reacting nearby. Keep the framing immersive for the topic era"
        )
    else:
        # 兜底：穷举 GENDER LOCK
        g = (gender or "").strip().lower()
        if g == "female":
            gender_phrase = "an ADULT WOMAN (female)"
            gender_negative = "no male features, no beard, no masculine jaw"
        elif g == "male":
            gender_phrase = "an ADULT MAN (male)"
            gender_negative = "no female features, no makeup, no feminine hairstyle"
        else:
            gender_phrase = "the historical onsite character"
            gender_negative = "consistent gender across all scenes"
        anchor = (
            f"Active speaker is {gender_phrase}, internally identified as '{speaker}' for voice continuity only; do not render this name as text. "
            f"{gender_lock} "
            f"GENDER LOCK (fallback): render as {g.upper() if g in ('male', 'female') else 'CONSISTENT GENDER'} across every scene; "
            f"the same speaker name must always have the same gender. {gender_negative}. "
            "Show this person as the clear speaking subject inside the period scene, face readable in three-quarter view, "
            "with any other onsite characters only listening or reacting nearby. Keep the framing immersive for the topic era"
        )
    pov = f". {_adsd_pov_contract()}" if ADSD_ONSITE_POV_MODE else ""
    if lip_sync:
        return (
            f"{anchor}. Talking-head friendly framing: medium close-up or over-shoulder two-shot, mouth area visible, "
            f"subtle natural lip movement implied, no extreme mouth close-up, no distorted teeth, keep framing immersive for the topic era{pov}"
        )
    return (
        f"{anchor}. Speaker-focus framing: medium close-up or over-shoulder two-shot, mouth can be visible but do not force exact lip sync, "
        f"use eyes, hands, documents and reaction timing to sell the dialogue, no extreme mouth close-up{pov}"
    )


def step1_script(topic: str) -> list[dict]:
    fmt_label = f"{ADSD_MODE_NAME} {'9:16' if IS_VERTICAL else '16:9'}" if ADS_DIALOGUE_MODE else ("VDAR 9:16" if IS_VERTICAL else "HDAR 16:9")
    tg(f"🎬 ADR V8 启动\n主题：{topic}\n格式：{fmt_label}\n\n斯皮尔伯格正在撰写台词...")
    log(f"开始处理：{topic} [{fmt_label}]")

    # 外部脚本注入场景下，分镜数量已由用户脚本决定；提前探测可跳过
    # "动态分镜数" LLM 调用，避免长稿/分段任务在无意义规划阶段卡住。
    _OVERRIDE_FILE = Path("/tmp/adr_script_override.txt")
    _early_override_lines: list[str] = []
    _early_override_timings: list[dict | None] = []
    if _OVERRIDE_FILE.exists() and _OVERRIDE_FILE.stat().st_size > 0:
        try:
            _early_override_lines, _early_override_timings = _parse_override_script_text(
                _OVERRIDE_FILE.read_text(encoding="utf-8")
            )
            log(f"外部脚本预检测：{len(_early_override_lines)} 句，跳过动态分镜数 LLM 规划")
        except Exception as e:
            log(f"外部脚本预检测失败，继续常规规划：{e}")

    # 检测老黄历主题并注入数据
    almanac_data = get_almanac_data(topic)
    if almanac_data:
        log(f"检测到老黄历主题，已注入完整数据")
        tg(f"📜 检测到老黄历主题，已注入 lunar-python 精确数据")

    # 文化/年代/导演检测（解决西方题材被中国化的文化错位，为镜头蓝本选导演）
    topic_meta = detect_topic_meta(topic)
    if almanac_data:
        # 老黄历强制中国铁律
        topic_meta["culture"] = "chinese"
        topic_meta["region"] = "中国"
        topic_meta["negative"] = "no Western figures, no Caucasian faces, no European architecture, no elderly man reading almanac, no white-bearded scholar"

    # 根据主题判断基调
    tone_prompt = f"""判断以下纪录片主题的情感基调，只输出一个词：
• 庄重（地震、战争、灾难、悼念、屠杀、饥荒、瘟疫、空难、沉船、矿难）
• 轻松（发明、趣闻、美食、节日、民俗、旅行、动物、体育、校园、儿童、小学、幼儿园、演讲、童谣、卡通、动画、亲子、科普入门、家庭日常）
• 怀旧（老物件、旧时光、老书、老电影、老歌、家乡记忆、邻里往事、童年回忆、读书日、怀旧书单、老照片、七八十年代、集体记忆、那些年、中老年情怀）
• 中性（人物传记、历史事件、科技发展、政治变革、文化现象）

主题：{topic}"""
    tone = chat("GEMINI_3_1_FLASH_LITE", "你是情感分析专家。", tone_prompt).strip()
    if tone not in ("庄重", "轻松", "怀旧", "中性"):
        tone = "中性"
    log(f"题材基调判断：{tone}")

    # 风格指南
    if tone == "庄重":
        style_guide = """• 语言风格：朴素、克制、有分量，让60岁老人一听就懂
• 禁止使用文学修辞、排比句、诗化表达
• 禁止使用生僻词、成语堆砌、文言句式
• 禁止使用轻浮口语感叹词（好家伙、您猜怎么着、了不得等）
• 用平实的陈述句，让事实本身说话，不煽情不夸张
• 语气沉稳、尊重事件中的生命与苦难"""
        char_range = "10~25"
    elif tone == "轻松":
        style_guide = """• 语言风格：大白话，像给邻居大爷大妈讲故事一样，口语化、接地气
• 禁止使用文学修辞、排比句、诗化表达
• 禁止使用生僻词、成语堆砌、文言句式
• 用"说人话"的方式讲清楚事情，让60岁老人一听就懂
• 可以用口语化的感叹词：您猜怎么着、好家伙、这下可、了不得"""
        char_range = "10~25"
    else:
        style_guide = """• 语言风格：通俗易懂，平实叙述，让60岁老人一听就懂
• 禁止使用文学修辞、排比句、诗化表达
• 禁止使用生僻词、成语堆砌、文言句式
• 用简单直白的方式把事情讲清楚
• 语气平和自然，不刻意煽情也不刻意轻松"""
        char_range = "10~25"

    # 动态分镜数
    almanac_summary = ""
    if almanac_data:
        almanac_summary = "\n\n该主题包含完整老黄历数据，涵盖以下板块：农历日期/干支/纳音、二十八星宿、十二建星、彭祖百忌、宜忌、吉神凶神、胎神占方、冲煞、五神方位、吉时、九宫飞星、值日天神，共约12个信息板块。"

    plan_prompt = f"""主题：{topic}{almanac_summary}

请判断这个主题适合多少个分镜（每个分镜 = 一句台词），范围 6~18 个
• 信息量大的主题（如老黄历、人物传记）需要更多分镜
• 信息量小的主题（如单一历史事件）可以少一些
• 每个分镜应承载一个独立的信息点或叙事段落

请输出 JSON 格式：{{"count": 数字, "reason": "一句话理由"}}
只输出 JSON，不加任何其他内容。"""
    if _early_override_lines:
        num_lines = len(_early_override_lines)
        log(f"外部脚本注入预设分镜数：{num_lines}")
    else:
        try:
            plan_raw = chat("GEMINI_3_1_FLASH_LITE", "你是纪录片分镜规划师。", plan_prompt)
            fence = re.search(r'```(?:\w*)\s*\n?([\s\S]*?)```', plan_raw)
            plan_clean = fence.group(1).strip() if fence else plan_raw.strip()
            plan = json.loads(re.search(r'\{[\s\S]+\}', plan_clean).group())
            num_lines = max(6, min(18, int(plan["count"])))
            log(f"LLM 规划分镜数：{num_lines}（理由：{plan.get('reason', '')}）")
        except:
            num_lines = 18 if almanac_data else 9
            log(f"LLM 规划失败，使用默认分镜数：{num_lines}")

    current_year = __import__("datetime").datetime.now().year

    # 老黄历主题用专用强约束 prompt
    if almanac_data:
        num_lines = 22  # 老黄历固定 22 句，覆盖全部 24 个数据字段
        almanac_block = f"""

以下是该日期的完整老黄历数据（由系统精确计算，请直接使用这些数据，不要自行编造）：
{almanac_data}

【严格结构要求】你必须严格按照以下 22 句板块顺序逐一创作台词，每个板块对应的句子必须包含上面数据中该板块的实际内容。严禁跳过任何板块，严禁合并板块，严禁用天气预报、生活小贴士等无关内容替代。

第1句：开场引入 — 报出公历日期、农历日期（必须使用注入数据中的确切农历日期）
第2-3句：干支纳音 — 说出今日年月日干支和五行纳音，用通俗语言解释含义和气场
第4-5句：十二建星解读 — 说出今日建星名称，详细解读其吉凶含义及适合做什么
第6-7句：二十八星宿解读 — 说出今日星宿名称，详细解读其吉凶寓意及对日常的影响
第8-9句：彭祖百忌安全化解读 — 用现代白话安全化解读彭祖百忌内容（严禁照搬古文，要翻译成老年人能懂的生活建议，严禁误导健康决策）
第10-11句：宜忌 — 分别说出今日宜做什么、忌做什么（必须使用注入数据中的具体宜忌项）
第12-13句：吉神凶神 — 必须完整列出注入数据中的所有吉神名称（如天德、月德、六合、普护、司命等）和所有凶神名称（如厌对、血忌、大时、小耗等），逐一说明，不能只提一两个
第14-15句：冲煞与胎神 — 说出今日冲什么属相、煞在哪个方位、胎神占方位置（必须用注入数据），用通俗语言解释注意事项
第16-17句：九宫飞星 — 说出今日飞星名称及五行属性，解读其对家居风水和运势的影响
第18-19句：五神方位 — 说出财神、喜神、福神的方位（必须用注入数据中的确切方位），给出实用建议
第20-21句：吉时 — 必须完整列出注入数据中的所有吉时时辰，并说出每个吉时对应的值日吉神（如金匮、天德、玉堂、司命、青龙、明堂等），不能只笼统说"六个吉时"
第22句：收尾祝福 — 温馨收尾，祝福观众

每句台词都必须引用上面老黄历数据中的具体数值，不允许泛泛而谈。"""

        spielberg_prompt = f"""你是老黄历科普视频的解说词作家，面向中老年观众。
当前年份是 {current_year} 年。
主题：「{topic}」
{almanac_block}

【铁律】
1. 你必须严格按照上面的"严格结构要求"中第1句到第{num_lines}句的板块顺序，逐句创作
2. 每句必须包含对应板块的真实数据（从上面的老黄历数据中提取），不允许编造或替换
3. 每句 {char_range} 字
4. 语气平和自然，像一位懂行的长辈在给家人讲今天的日子
5. 彭祖百忌必须用现代白话安全化解读，不能误导健康决策
6. 只输出 {num_lines} 行纯台词，每行一句，不加编号不加标点以外的任何内容
7. 严禁输出天气预报、穿衣建议、带伞提醒等与老黄历无关的内容"""
    else:
        spielberg_prompt = f"""你是顶级短视频爆款编剧（视频号/抖音百万播放量操盘手）。
当前年份是 {current_year} 年，涉及时间跨度时请据此准确计算。

主题：「{topic}」
分镜数：{num_lines} 句

★★★ 爆款铁律（必须严格遵守，违反任何一条则视频注定扑街）★★★

【钩子规则 · 前 3 秒定生死】
第 1 句必须是强钩子，从下列爆款套路选一种：
• 反常识："XX 年前的今天，一个 XX 做了件让所有人跌破眼镜的事"
• 争议悬念："你以为 XX 是 YY，其实他是 ZZ"
• 数字冲击："XX 一生只做了 3 件事，每件都改变了人类"
• 情绪钩："XX 死前留下 8 个字，700 年后还在戳中每个中国人"
• 身份共鸣："如果你是 30 岁的打工人，你必须认识这个人"
• 日期钩："今天是 X 月 X 日，历史上这一天，发生了一件你一定不知道的事"
严禁开头就"XX 年 X 月 X 日，XXX 在 XXX 做了 XXX"这种平铺直叙纪录片腔——那是注定扑街的开头。

【节奏规则 · 每 15 秒一个反转或爽点】
中段必须有至少 2 次反转（"原以为…没想到…" / "表面上…实际上…" / "所有人都以为…但…"）。
每 3-4 句必须有 1 个情绪爆点（惊 / 悲 / 怒 / 唏嘘 / 爽）。
禁止全程平铺直叙，禁止没有情绪起伏。

【金句收尾 · 可做话题的那种】
最后 1 句必须是朗朗上口的金句，具备：短（≤ 15 字）+ 对仗或押韵 + 可截图做封面 + 能当 hashtag。
示例："改革，从来是要命的事" / "所谓皇帝，不过是龙椅上的打工人" / "他们素不相识，却用同一支笔同一天放下" / "历史没有如果，只有后果"

【语言风格】
• 每句 {char_range} 字（严格）
• 短句为主、少长从句、多口语感叹
• 关键词要抓耳——数字对比、反问、惊叹
• 严禁"让我们"、"众所周知"、"话说"这类纪录片套话
{style_guide}
• 如果涉及老黄历、彭祖百忌、宜忌等传统禁忌内容，必须用现代白话做安全化解读，不能照搬古文原句
{ADS_RETENTION_SCRIPT_GUIDE if ADS_RETENTION_MODE and not ADS_DIALOGUE_MODE else ""}
{ADS_REPORTER_SCRIPT_GUIDE if ADS_REPORTER_MODE else ""}
• 只输出 {num_lines} 行纯台词，每行一句，不加编号不加标点以外的任何内容"""

        if ADS_REPORTER_MODE:
            spielberg_prompt = f"""你是历史短视频的白话讲解编剧，负责把复杂历史讲给普通观众听懂。
当前年份是 {current_year} 年，涉及时间跨度时请据此准确计算。

主题：「{topic}」
分镜数：{num_lines} 句

【HADS / VADS 历史讲解铁律】
1. 这不是诗意纪录片，也不是情绪大片；这是"第一人称现场感 + 白话历史解释"。
2. 每句都要讲清楚一个事实点，优先回答 5W2H：什么时候、谁、在哪里、做了什么、为什么、怎么做、造成什么后果。
3. 时间必须精确到年/月/日；人物、国家、机构、事件名称必须具体，不许用"他们、那边、风暴、世界的影子"这类含糊说法代替。
4. 普通观众可能不知道背景，所以要顺手解释专名：例如"最后通牒就是限期答复，不答应就可能动武或断交"。
5. 可以有第一人称现场感，比如"我站在北京外交部外"、"我手里这份电报写着"，但每句后半段必须落回事实解释。
6. 禁止艺术化表达、隐喻、排比、金句、谜语式钩子、含蓄暗示、空泛大词。
7. 禁止"你以为、没想到、历史没有如果、时代洪流、风吹到中国"这类爆款套话。
8. 语言要像给家里长辈讲历史：短句、直白、有因果，不卖弄。
9. 全片必须形成清楚结构：开头交代中国主线，中段说明同年全球战争/金融/科技/文化背景，结尾说明这些背景怎样压到中国外交上。
10. 每句 {char_range} 字；只输出 {num_lines} 行纯台词，每行一句，不加编号。

【语言风格】
{style_guide}
{ADS_REPORTER_SCRIPT_GUIDE}
"""

    # 老黄历数据校验：从注入数据中提取必须出现在台词中的关键值
    almanac_checkpoints = []
    if almanac_data:
        import re as _re
        for data_line in almanac_data.splitlines():
            if data_line.startswith("农历："):
                m = _re.search(r'年(.+)', data_line.replace("农历：", ""))
                if m: almanac_checkpoints.append(m.group(1).strip())
            elif data_line.startswith("日干支：") or "日干支：" in data_line:
                m = _re.search(r'日干支：(\S+)', data_line)
                if m: almanac_checkpoints.append(m.group(1))
            elif data_line.startswith("十二建星："):
                almanac_checkpoints.append(data_line.split("：")[1].strip())
            elif data_line.startswith("二十八星宿："):
                almanac_checkpoints.append(data_line.split("：")[1].split("（")[0].strip())
            elif data_line.startswith("冲："):
                m = _re.search(r'[)）](\S)', data_line)
                if m: almanac_checkpoints.append(m.group(1))  # 冲的生肖，如"虎"
            elif data_line.startswith("九宫飞星："):
                almanac_checkpoints.append(data_line.split("：")[1].strip()[:3])  # 如"九紫火"
            elif data_line.startswith("财神方位："):
                m = _re.search(r'财神方位：(\S+)', data_line)
                if m: almanac_checkpoints.append(m.group(1))
        log(f"黄历校验关键词（{len(almanac_checkpoints)}个）：{almanac_checkpoints}")

    # ── 外部脚本注入（可选开关）──────────────────────────────────
    _script_injected = False
    _override_timings: list[dict | None] = []
    dialogue_turns: list[dict] = []
    if _OVERRIDE_FILE.exists() and _OVERRIDE_FILE.stat().st_size > 0:
        _override_raw = _OVERRIDE_FILE.read_text(encoding="utf-8")
        _override_lines, _override_timings = _parse_override_script_text(_override_raw)
        min_override_lines = 1 if not ADS_DIALOGUE_MODE else 1
        if min_override_lines <= len(_override_lines) <= 22:
            lines = _override_lines
            num_lines = len(lines)
            _script_injected = True
            if ADS_DIALOGUE_MODE:
                dialogue_turns = _parse_adsd_override_turns(_override_lines, topic)
                lines = [t["text"] for t in dialogue_turns]
                roles = " / ".join(dict.fromkeys(t.get("speaker", "") for t in dialogue_turns if t.get("speaker")))
                shape = dialogue_turns[0].get("dialogue_shape", "dialogue") if dialogue_turns else "dialogue"
                log(f"ADSD 注入脚本解析：shape={shape} roles={roles}")
                tg(f"📥 ADSD 注入脚本解析完成\n结构：{shape}\n角色：{roles}")
            log(f"📥 外部脚本注入：读取 {num_lines} 句台词，跳过 LLM 生成")
            timed_count = sum(1 for x in _override_timings if x)
            tg(f"📥 检测到外部脚本注入\n读取 {num_lines} 句台词，时间戳 {timed_count} 条，跳过 LLM 自动生成")
            _used_path = _OVERRIDE_FILE.with_suffix(f".used_{int(time.time())}")
            _OVERRIDE_FILE.rename(_used_path)
            log(f"外部脚本已重命名为 {_used_path.name}")
        else:
            log(f"⚠️ 外部脚本句数 {len(_override_lines)} 不在 {min_override_lines}~22 范围内，忽略，走 LLM 生成")
            tg(f"⚠️ 外部脚本句数 {len(_override_lines)} 不在 {min_override_lines}~22 范围内，已忽略")

    # ADSD：生成角色对白 turn；后续每个 turn 独立 TTS 并驱动画面/字幕。
    if ADS_DIALOGUE_MODE and not almanac_data and not _script_injected:
        for _try in range(3):
            try:
                dialogue_turns = _generate_adsd_dialogue_turns(topic, num_lines, tone, style_guide)
                lines = [t["text"] for t in dialogue_turns]
                num_lines = len(lines)
                roles = " / ".join(dict.fromkeys(t.get("speaker", "") for t in dialogue_turns if t.get("speaker")))
                shape = dialogue_turns[0].get("dialogue_shape", "dialogue") if dialogue_turns else "dialogue"
                tg(f"🎭 {ADSD_MODE_NAME} 现场台词就绪：{num_lines} 个 turn，结构：{shape}，角色：{roles}")
                log(f"ADSD 台词剧本生成成功：{num_lines} turns shape={shape} roles={roles}")
                break
            except Exception as e:
                log(f"ADSD 对话剧本生成失败（第 {_try+1}/3 次）：{e}")
                if _try == 2:
                    raise

    # LLM 智能音色分配（覆盖前面 _voice_asset_id_for_speaker 关键字推断）
    # 启用条件: ADSD 模式 + dialogue_turns 已就绪 + 没关 flag
    if ADS_DIALOGUE_MODE and dialogue_turns:
        try:
            _voice_qa = _apply_llm_voice_assignment(dialogue_turns)
            if _voice_qa:
                (OUTPUT_DIR / "adsd_voice_assign_qa.json").write_text(
                    json.dumps(_voice_qa, ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )
                _llm_n = _voice_qa.get("llm_assigned_count", 0)
                _kw_n = _voice_qa.get("keyword_fallback_count", 0)
                tg(f"🎙 LLM 智能音色分配：{_llm_n} 由 LLM 决策 / {_kw_n} keyword 兜底")
        except Exception as e:
            log(f"LLM voice assign 整体异常（不致命，保留 keyword 决策）：{e}")

    # 最多重试 3 次拿到足够句数 + 通过数据校验（外部注入/ADSD 时跳过）
    if not _script_injected:
        if not ADS_DIALOGUE_MODE:
            lines = []
            for _try in range(3):
                raw_lines = chat("GEMINI_3_1_FLASH_LITE", "你是纪录片旁白创作大师。", spielberg_prompt)
                lines = [l.strip() for l in raw_lines.strip().splitlines() if l.strip()][:num_lines]
                if len(lines) < num_lines:
                    log(f"斯皮尔伯格只生成了 {len(lines)} 句（需要 {num_lines} 句），重试...")
                    continue

                # 老黄历数据校验：台词整体必须包含关键数据值
                if almanac_checkpoints:
                    full_text = ''.join(lines)
                    missing = [cp for cp in almanac_checkpoints if cp not in full_text]
                    if missing:
                        log(f"台词缺少黄历数据：{missing}，重试...")
                        tg(f"⚠️ 台词未引用黄历数据（缺 {', '.join(missing)}），重新生成...")
                        continue
                    log(f"黄历数据校验通过，全部关键词命中")

                break  # 句数够 + 校验通过

        if len(lines) < num_lines:
            raise RuntimeError(f"斯皮尔伯格 3 次重试后仍只有 {len(lines)} 句台词（需要 {num_lines} 句）")

    total_chars = sum(len(l) for l in lines)
    tg(f"✅ 剧本就绪，共 {num_lines} 句，总字符数 {total_chars}\n\n制片人正在制定全片准则（价值观 · 风格 · 事实考证）...")

    # 制片人：全能型把关人——定价值观、定风格、抠事实
    # 产出一份制片准则（Producer Brief），作为姜文/图片模型的第一准则
    producer_prompt = f"""你是本片的总制片人，是最终把关人。你既要把控价值观、又要定调子（视觉风格）、还要抠事实/考证。你的输出将作为姜文（画面导演）、图片模型、字幕的第一准则，优先级高于任何下游指令。

★★★ 文化/年代铁律（系统已预判，绝对优先级，本片全篇必须严格遵守，不得偏移）★★★
• CULTURE: {topic_meta.get('culture')}
• REGION: {topic_meta.get('region')}
• ERA: {topic_meta.get('era')}
• DIRECTOR_STYLE: in the cinematic style of {topic_meta.get('director')}
• PERIOD_COSTUME: {topic_meta.get('period_costume')}
• PERIOD_VISUAL_MOTIFS: {topic_meta.get('period_visual')}
• NEGATIVE（必须排除的错位元素）: {topic_meta.get('negative')}

⚠️ 所有后续字段（尤其是 SUBJECT_DETAILS / VISUAL_CONTINUITY / Hero Anchor）必须严格匹配上方铁律。本片 culture 是 {topic_meta.get('culture')}——如果是 western/japanese/other，严禁把主角画成中国人/东亚面孔；如果是 chinese，严禁画成西方/东欧面孔。张冠李戴即为本片废掉。
{"\n★★★★ 1919 五四/全球史专项铁律 ★★★★\n本片发生在 1919 年，绝对不能出现新中国成立后的任何视觉元素：毛泽东画像、五星红旗、人民英雄纪念碑、1949 后天安门城楼装饰、现代红色政治标语、解放军/红卫兵/中山装集会、现代汽车和 LED 屏幕全部禁止。1919 的天安门必须是民国时期城楼与广场环境，允许学生布旗/纸质标语，但必须是当时语境（如外争主权、还我青岛、拒签和约），不能是新中国宣传视觉。\n" if is_1919_global_topic(topic) else ""}

主题：「{topic}」
基调：{tone}（庄重 / 轻松 / 中性）
格式：{'竖屏 9:16（面向短视频/视频号中老年或儿童观众）' if IS_VERTICAL else '横屏 16:9（面向中长视频/知识科普）'}
台词（已定稿，共 {num_lines} 句）：
{chr(10).join(f'{i+1}. {l}' for i, l in enumerate(lines))}

请输出一份严格结构化的【制片准则】（全英文便于图片模型理解，每项 2~4 个短语，总计 ≤ 280 词）：

AUDIENCE_AND_VALUES: 目标受众（年龄段、文化背景），传递的核心情感，必须规避的内容（如暴力/说教/刻板印象/历史虚无/消费苦难）
STYLE_KEY: 视觉基调的 3~5 个关键词（bright childlike storybook / sepia documentary / traditional Chinese ink wash / high-key editorial / low-key cinematic 等）——这是压倒性风格锚
PALETTE: 具体主色板（warm yellow + sky blue + cream / cold gray + muted blue / golden red + ink black 等）
LIGHTING_AND_CAMERA: 光线与镜头语言（high-key soft front light / golden hour sidelight / low-key dramatic backlight，镜头以特写/中景/广角为主）
SUBJECT_DETAILS: 人物、场景、物件的具体外观描述{'（历史题材：考证后的时代服饰/发型/建筑/器物具体外观，绝不说朝代名，只说外观）' if tone != '轻松' else '（现代题材：现场元素如现代校服/电子屏幕/校园环境/食堂器具，绝不使用历史服饰或器物）'}
VISUAL_CONTINUITY: ★跨分镜一致性锚★（全片 N 张图必须保持同一画风、同一主角、同一场景的视觉连贯）。必须包含：①主角锚（Hero Anchor）：一位固定主角的极详细外观描述（年龄、性别、发型、五官特征、服饰细节），**必须严格匹配开头 PERIOD_COSTUME 铁律**（本片 culture={topic_meta.get('culture')} / era={topic_meta.get('era')}），全片出现主角的画面完全一致；②场景锚（Setting Anchor）：2-3 个核心场景的固定元素，**必须符合开头 REGION={topic_meta.get('region')} / ERA={topic_meta.get('era')}**；③风格锚（Style Anchor）：一个 5-10 词英文 stylebook（全片只用一种），**必须包含 "{topic_meta.get('director')} cinematic" 作为导演风格锚**；④文字锚（Text Anchors）：画面里必须自然出现的文字字符串（按 culture 决定中文或对应语种拉丁字符，如莎士比亚题材可用 Shakespeare 手稿英文）；⑤★ 文化锚（Cultural Anchor）★：所有 human subjects 和场景必须严格匹配开头铁律的 CULTURE/REGION/PERIOD_COSTUME，不得偏移；⑥★ 年代锚（Era Anchor）★：每个分镜具体年代必须匹配开头 ERA={topic_meta.get('era')}，服饰/建筑/器物严格对应；⑦★ 反 cliché negative★：必须在英文 negative prompt 里包含开头 NEGATIVE 铁律："{topic_meta.get('negative')}"
TABOOS: 画面禁区（例：{'儿童/校园题材禁 sepia / 老照片 / 历史服饰 / 阴郁低饱和 / 成人苦难叙事' if tone == '轻松' else '历史题材禁 cartoon / 明亮儿童插画 / anachronistic 现代设备'}；同时列出该主题特有的禁区）。★ 黄历/万年历/节气/传统文化题材必须在 TABOOS 里显式写入英文禁令 "no elderly man reading almanac, no white-bearded old scholar in robe, no stereotypical old fortune-teller"（AI 图模型对黄历题材有老头 cliché，必须硬禁）。注意：不要在 TABOOS 里禁止"文字/text"，本片支持 Nano Banana 2 渲染中文
TITLE_HOOK: 短标题钩子方向（从以下套路选 1~2 种并说明该主题如何落地：反差悬念 / 数字利益 / 身份共鸣 / 情绪冲击 / 警示钩子 / 日期通告）
THUMBNAIL_ANCHOR: 封面视觉锚，用 4~6 个短语描述：主体、主色（三色以内）、构图、情绪钩子、文字留白位

只输出上述 9 项结构化内容，每项用全大写 key + 冒号开头，不加解释、不加 markdown。"""

    if _script_injected:
        historical_context = f"""AUDIENCE_AND_VALUES: informed general audience, clear geopolitical and business explanation, avoid studio reporter framing or propaganda poster cliches.
STYLE_KEY: contemporary geopolitical documentary, dynamic business B-roll, cinematic data visualization, restrained editorial tension.
PALETTE: deep navy, muted steel gray, semiconductor gold accents.
LIGHTING_AND_CAMERA: controlled newsroom-free documentary lighting, tracking shots, close-ups of documents and screens, wide institutional exteriors.
SUBJECT_DETAILS: contemporary US-China technology and business scenes, Air Force One exterior details, semiconductor wafers, executive travel, negotiation tables, financial charts.
VISUAL_CONTINUITY: fixed visual world of 2020s Washington and global tech supply chains; recurring anchors: black leather jacket tech CEO silhouette, aircraft boarding stairs, chip wafer macro, conference-room table, market chart overlays; no talking-head studio.
TABOOS: no onsite reporter, no TV studio anchor, no ancient costume, no generic Chinese palace, no fake flags or offensive caricature, no distorted text.
TITLE_HOOK: high-stakes business reversal and chip negotiation signal.
THUMBNAIL_ANCHOR: Air Force One stairs, black leather jacket figure, glowing chip wafer, tense blue-gray palette, bold title-safe empty space.
"""
        log("外部脚本注入：使用确定性 Producer Brief，跳过重模型制片准则生成")
    else:
        historical_context = chat("CLAUDE_4_6_OPUS", "你是总制片人，全能把关人，只输出严格结构化英文准则。", producer_prompt)
    tg(f"✅ 制片人准则就绪（已定调子 + 事实考证 + 价值观把关）\n\n姜文正在据此标注情绪 + 生成画面提示词...")

    # 老黄历主题：给每句台词标注板块名，让姜文生成针对性画面
    if almanac_data:
        ALMANAC_SECTIONS = {
            1: "开场引入（日历翻页）",
            2: "干支纳音（天干地支符号）", 3: "干支纳音（五行元素）",
            4: "十二建星（星盘/罗盘）", 5: "十二建星（吉凶场景）",
            6: "二十八星宿（星空/星图）", 7: "二十八星宿（星宿寓意）",
            8: "彭祖百忌（古代生活）", 9: "彭祖百忌（现代化解）",
            10: "宜事（吉祥场景）", 11: "忌事（警示场景）",
            12: "吉神凶神（神像/符咒）", 13: "值日天神（天神形象）",
            14: "冲煞（生肖冲克）", 15: "胎神占方（胎神方位/家居）",
            16: "九宫飞星（九宫格/风水）", 17: "九宫飞星（飞星方位）",
            18: "五神方位（罗盘/方位图）", 19: "五神方位（财神/喜神）",
            20: "吉时（时辰/日晷）", 21: "吉时（办事场景）",
            22: "收尾祝福（温馨家庭）",
        }
        lines_with_section = []
        for i, l in enumerate(lines):
            sec = ALMANAC_SECTIONS.get(i + 1, "")
            lines_with_section.append(f"{i+1}. [{sec}] {l}")
        lines_display = chr(10).join(lines_with_section)
        almanac_visual_guide = """

【老黄历视觉设计指南】
这是一个老黄历科普视频，每句台词对应不同的黄历板块。画面必须与该板块主题高度相关。

★★★ 反 cliché 铁律（最重要）★★★
黄历题材 AI 图生成最常见的翻车是"每张图都出现一个穿长袍看黄历的老头/长者"。本片严禁这种刻板形象。
• 默认所有板块走"无人器物派"：画面主体是器物/符号/纹样/神像/场景，不出现任何人物
• 只有以下 3 类板块允许出现人物：彭祖百忌（多职业剪影轮换）、吉神凶神（神像本身）、收尾祝福（现代家庭温馨场景）
• 即使允许人物的板块，也必须**明确多样化**（古代织女 / 医者 / 书生 / 农夫 / 现代家庭主妇 / 儿童），严禁"翻黄历的老者/老头/长者/白须老人/读书的长袍老人"

★★★★ 全片视觉形态：传统黄历抽签卡牌风（最高优先级铁律）★★★★

整片是一组 {num_lines} 张"今日黄历抽签卡"——每张图都必须是**一张实体卡片的特写**，像传统寺庙抽签卡 / 老黄历翻页卡 / 收藏级卡牌艺术那样：

强制视觉构成（每张图都必须有）：
✅ **卡片实体可见**：4:5 至 9:16 比例的竖向矩形卡牌悬浮于中性背景，卡片边缘清晰可辨（不是无边框场景图）
✅ **金色或朱砂红边框**：传统纹样烫金边 / 朱砂红勾边 / 古铜雕花边
✅ **卡名在卡片顶部**：用粗宋体大字写该板块的中文标题（如"庚午"、"宜祭"、"忌动土"、"星宿"、"福星"等）
✅ **中央插画**：板块对应的吉祥物件 / 神像 / 生活场景 / 节气符号（工笔水彩混合质感）
✅ **卡背或纸纹底色**：奶白宣纸 / 米黄古纸 / 红金织锦 / 老木桌面 任选其一
✅ **统一卡牌系列感**：22 张卡如同同一套抽签盒里抽出的，**严禁** 22 张用 22 种不同设计风格

参考视觉：
• 寺庙求签抽出的红纸签条 + 金线
• 老式印刷的"今日运势"小卡片
• 传统中国年画风格的礼盒卡套
• 收藏级老黄历"卡背 + 卡面"双面设计

禁忌：
❌ 没有卡片边框的场景大片（那是 v6 的样式，不是抽卡）
❌ extreme close-up of trembling hand / silhouette against storm sky / CG concept art
❌ 西方塔罗牌风（要中国传统签卡风，不是西方占卜）

★★★ 22 板块卡面内容库（中老年熟悉的吉祥/生活/传统元素，每张卡画一个具体物件/场景）★★★

设计原则：每张卡的中央插画都要让中老年观众"看一眼想起自家厨房/院子/老乡邻"。
每个板块从下列候选画面中选 1 个具体卡面，禁止 cinematic dramatic 风格。

第 1 句 [开场引入]：候选 → 老式撕拉日历挂在木门上 / 红色小皮日历翻到今日 / 阳光透窗照在桌上的黄历本
第 2 句 [干支纳音/天干地支]：候选 → 红绸缎面金箔"庚午"二字 / 朱砂红印章盖在宣纸上"庚午" / 古木刻"庚午"字屏风
第 3 句 [干支纳音/五行]：候选 → 五件传统物件分别代表金木水火土（小铜锣/木鱼/陶瓷水罐/红蜡烛/陶土碗）摆桌面 / 五色丝线编织成结
第 4 句 [十二建星/星盘]：候选 → 老黄铜罗盘特写在木桌上 / 木桌上古代日晷 / 老式四合院屋脊
第 5 句 [十二建星/吉凶]：候选 → 厨房灶台贴着红"吉"字纸 / 阳台门联红色"福"字 / 老人手中红色平安符
第 6 句 [二十八星宿/星空]：候选 → 夜空北斗七星 + 古亭子剪影 / 古庙屋脊望星 / 老式天文仪器特写
第 7 句 [二十八星宿/寓意]：候选 → 庙宇里挂的星宿动物木牌 / 古亭横梁吉祥兽装饰 / 朱漆窗棂内的星图
第 8 句 [彭祖百忌/古代]：候选 → 古代织女在窗前织布（侧脸） / 货郎挑担在巷口（背影） / 田间插秧农夫（远景剪影）/ 集市卖菜大娘（侧面）
第 9 句 [彭祖百忌/现代]：候选 → 现代家庭主妇晾被子 / 老两口在阳台浇花（背影）/ 中年儿子陪老父亲下棋 / 三代同桌吃饭
第 10 句 [宜事/祭祀]：候选 → 庙宇香炉烟雾袅袅 / 家中神龛供桌摆水果 / 烛台红蜡烛 / 案几上香烟笔直
第 11 句 [忌事/警示]：候选 → 锁着的老木门 / 闭合的窗户 / 阴雨青石板小巷 / 落锁的院门 / 蛛网门环
第 12 句 [吉神凶神]：候选 → 关二爷塑像红脸长须 / 财神爷瓷像捧元宝 / 灶王爷年画 / 门神年画一对
第 13 句 [值日天神]：候选 → 紫微大帝彩绘 / 太岁神像 / 庙宇天神壁画 / 道观里的星君像
第 14 句 [冲煞/生肖]：候选 → 红绳挂玉佩生肖造型（如玉鼠）/ 十二生肖剪纸 / 木刻生肖印章 / 庙宇生肖石雕
第 15 句 [胎神占方]：候选 → 老式四合院俯视图 / 老房间摆着摇篮 / 老木床雕花床头 / 院落格局水墨白描
第 16 句 [九宫飞星]：候选 → 九宫格红印章 / 老木质九宫游戏盘 / 八卦镜挂门楣 / 风水罗盘特写
第 17 句 [九宫飞星/方位]：候选 → 八卦图 + 红绸结 / 罗盘指针特写 / 老书页"九宫"图谱 / 朱砂笔画八卦图
第 18 句 [五神方位/罗盘]：候选 → 风水罗盘指南针特写 / 朱漆案几摆罗盘 / 老黄铜方位仪
第 19 句 [五神方位/财神]：候选 → 财神爷招财进宝彩塑 / 喜神牌位红绸 / 福神门画 / 灶王爷上方贴满红纸
第 20 句 [吉时/时辰]：候选 → 老式座钟钟摆 / 沙漏倒计时 / 日晷阴影 / 古代更鼓
第 21 句 [吉时/办事]：候选 → 老人慢走青石板巷子 / 老两口在茶馆喝茶 / 庙会上买东西的人群（背影）/ 集市开张挂红绸
第 22 句 [收尾祝福]：候选 → 红灯笼挂满老院子 / 福字贴老木门 / 一家三代围坐吃饭（背影）/ 老房子门口的猫和落日

★★★ 严禁画面（每条铁律）★★★
❌ 任何"翻黄历的老者 / 白须老人 / 长袍学者 / 算命先生"——黄历题材最大 cliché
❌ extreme close-up of trembling hand / silhouette against storm sky / Dutch angle / 抽象戏剧画面（这是电影分镜，不是黄历）
❌ CG concept art / 夜空星座大全景 / 戏剧光影血滴 / 烟尘剪影（中老年看不懂"恐怖片预告"）
❌ 现代都市场景（咖啡馆 / 高楼 / 办公室 / 网红地标）
❌ 西方面孔 / 二次元 / 抽象插画
❌ 不同分镜切换"摄影 / CG / 水墨 / 装饰金"医介（必须全片同一种 medium 一致到底）

★ 画面风格统一锚（22 张图必须共享）：
温暖中国传统美术 + 暖红朱砂奶白配色 + 柔和自然光 + 4k 编辑级摄影质感（不是 cinematic dramatic）+ 工笔/水彩混合质感"""
    else:
        lines_display = chr(10).join(f'{i+1}. {l}' for i, l in enumerate(lines))
        almanac_visual_guide = ""

    jiangwen_prompt = f"""你是顶级电影导演姜文，同时精通黑泽明/张艺谋/李安/王家卫/诺兰/昆汀的镜头语言。你的任务不是"描述画面"，是"设计电影镜头"。
以下是纪录片的 {num_lines} 句旁白台词（主题：{topic}）：

{lines_display}

【制片人准则（最高优先级，所有画面必须严格遵循：价值观 · 风格 · 事实）】
{historical_context}{almanac_visual_guide}

★★★ 视觉一致性铁律（最高优先级，比所有其他条款都重要！违反 = 全片精分废掉）★★★

全片 {num_lines} 张图**必须看起来是同一摄影师 / 同一镜头 / 同一日杂大片系列拍出来的**，像 Kinfolk 杂志一期 22 页大片。
严禁出现：
❌ 第 1 张真人摄影 + 第 5 张 CG concept art + 第 10 张水墨戏剧 + 第 15 张装饰金屏风（这就是精分）
❌ 不同分镜切换"摄影 / 插画 / 水墨 / 3D" 媒介（必须全部是同一种 medium）
❌ 不同分镜切换色板（warm cream / cool blue / neon / sepia 不得在一组镜头里同时出现）

强制要求：
✅ 每条 prompt 头部第一句必须**完全相同**地引用 producer STYLE_KEY（一字不差）：定 medium + 定色板 + 定光源风格 + 定画质
✅ 每张图都是同一种 medium（如 "editorial Kinfolk magazine photography, soft warm natural light"）
✅ 全片色板一致（如 "warm cream paper / sage green / soft amber, never neon, never high-contrast cool blue"）
✅ 所有人物（即使不同分镜）必须共享相同的视觉处理（同一摄影师拍法、同一光线系统、同一色温）
✅ 即使是空镜 / 物件特写，也要保持与人物镜头**同一画风**

★★★ 镜头语言铁律（次优先级，在保证视觉一致性的前提下做镜头变化）★★★

每条英文 prompt **必须**显式包含以下 4 要素（缺一不可，否则本片废掉）：

1. **景别**（从下列选一个，全片必须有变化，严禁全部中景）：
   `extreme close-up` / `close-up` / `medium shot` / `wide shot` / `extreme wide shot` / `insert shot` / `over-the-shoulder`

2. **机位 / 角度**（从下列选一个，严禁全部正面平视）：
   `low-angle heroic` / `high-angle oppressive` / `Dutch angle unstable` / `bird's-eye aerial` / `worm's-eye` / `POV first-person` / `profile side view`

3. **光影风格**（从下列选一个，严禁全部 "well-lit / clear"）：
   `silhouette backlit` / `rim light from behind` / `chiaroscuro single-key` / `hard shadow key light` / `rembrandt triangle` / `low-key film noir` / `golden hour sidelight` / `overhead harsh top-light`

4. **视觉母题**（画面里必须有一个强烈物件锚定情绪，从下列选或自创）：
   `flapping banner` / `smoke and embers` / `pouring rain` / `single blood drop` / `trembling hand grip` / `eye reflection close` / `candle flame flicker` / `mirror reflection` / `window frame shadow` / `silhouette against sunset` / `dust motes in light beam`

★ 镜头节奏分布（按分镜号强制执行）：
• **前 2 句（钩子区）**：必须 `extreme close-up` + 强烈物件母题（眼睛/手/血滴/火苗），3 秒锁住观众
• **中段（情绪递进）**：混合使用 `Dutch angle` / `low-angle` / `silhouette` / `rim light`，制造戏剧张力
• **最后 1-2 句（金句/收尾）**：`extreme wide shot` + `silhouette against sky/sunset` + 大留白，给余韵

★ 根据题材锁定全片视觉风格（用纯描述词，**严禁提任何具体导演/艺术家/画家姓名**——OpenAI GPT Image 2 对"模仿艺术家风格"phrasing 强制拒绝触发版权 filter，必须用风格描述代替姓名）：
• 历史悲剧 / 战争 / 死亡题材 → epic silhouette composition with storm backlighting / heavy film grain / cinemascope / dramatic shadow play
• 帝王 / 政治 / 权谋题材 → saturated color-block composition / symmetric centered framing / red-gold palette / low-angle hero shots
• 文人 / 诗意 / 禅意题材 → Zen contemplative cinematography / static deep focus / soft warm tones / horizontal natural composition
• 悬疑 / 反转 / 黑色题材 → hard key light with smoke / low-angle dramatic / high saturation / pulpy retro tones
• 都市 / 现代 / 情感题材 → handheld neon-lit profile close-ups / shallow depth / asymmetric negative space
• 民俗 / 自然 / 时令题材 → long takes with natural sunlight / shadow-cut compositions / atmospheric haze

★ **绝对禁令（OpenAI 触发版权 filter）**：永远不要在你输出的英文 prompt 里写：
❌ "in the cinematic style of [任何人名]"
❌ "[导演姓名] style" / "[画家姓名] lighting"
❌ "Akira Kurosawa / Zhang Yimou / Ang Lee / Jiang Wen / Wong Kar-wai / Christopher Nolan / Stanley Kubrick / Caravaggio / Rembrandt / Tarkovsky / Sergio Leone / 任何具体导演画家名"
正确做法：用动作 + 光影 + 构图 + 色调的描述词，不引用人名

★ 严禁词汇（任何一条 prompt 里出现以下词就是失败）：
❌ `centered composition` / `well-lit` / `clear visibility` / `standard shot` / `documentary style` / `normal angle` / `straightforward composition`
{ADS_RETENTION_VISUAL_GUIDE if ADS_RETENTION_MODE and not ADS_DIALOGUE_MODE else ""}
{ADS_REPORTER_VISUAL_GUIDE if ADS_REPORTER_MODE else ""}

为每句台词输出：
• 情绪标签（从以下选一个）：{'欢快 / 希望 / 温暖 / 童趣 / 活力 / 惊喜' if tone == '轻松' else '悲壮 / 紧张 / 孤独 / 辉煌 / 压抑 / 释然'}
• {ASPECT_RATIO} 英文画面提示词（**严格限 40~60 词**，过长会触发 WeryAI gateway 504 timeout），要求：
  - ★ 开头强制引用制片人 VISUAL_CONTINUITY 里的 Style Anchor 短语（一字不差）+ Hero Anchor 外观（当画面里有主角时）作为前置描述，确保全片 {num_lines} 张图画风、主角、色板完全一致
  - ★★ 文化铁律（题材相关，已由系统预判）：本片文化背景 = **{topic_meta.get('culture')}** / 地域 = **{topic_meta.get('region')}** / 年代 = **{topic_meta.get('era')}**。人物形象铁律："{topic_meta.get('period_costume', '')}"。视觉母题池："{topic_meta.get('period_visual', '')}"。每张图必须严格符合该文化/地域/年代，严禁张冠李戴（中国题材画成欧美、西方题材画成东亚都是失败）
  - ★★ 反 cliché negative（题材相关）：英文 prompt 结尾必须含 "{topic_meta.get('negative', '')}"
  - {'★★ 1919 专项禁令：每条英文 prompt 必须显式包含 "1919 Republican-era Beijing or post-WWI global setting; no Mao portrait, no PRC flag, no People Heroes Monument, no post-1949 Tiananmen decorations, no modern propaganda slogans"。' if is_1919_global_topic(topic) else ''}
  - 每张图必须使用制片人 PALETTE 指定的主色板，不得偏离
  - {'严格按照每句台词方括号内的板块主题设计画面' if almanac_data else '画面聚焦台词中的现代/校园/童趣场景，不使用历史元素' if tone == '轻松' else '严格符合上述历史参考中的年代、服饰、建筑、器物特征'}
  - {'中国传统美术风格，工笔画或水墨画质感，暖色调，高清' if almanac_data else '画风严格遵循制片人 STYLE_KEY，高清细腻' if tone == '轻松' else '写实老照片风格，sepia tone，高清'}
  - {'竖版构图（9:16）：人物特写为主，上留天空下留地面，主体居中偏上' if IS_VERTICAL else '横版构图（16:9）：注重场景纵深和环境氛围'}，包含具体的光线、景别描述
  - {'每张画面必须包含该板块的核心视觉元素' if almanac_data else '人物描述与制片人 Hero Anchor 完全一致（同一主角、同一发型、同一服饰）；场景取自 Setting Anchor' if tone == '轻松' else '人物的穿着、发型、体态必须符合该历史时期'}
  - ★ 中文元素渲染：如果制片人 VISUAL_CONTINUITY 里指定了 Chinese Text Anchors，在对应分镜号里，必须在画面自然位置（校牌 / 门楣 / 勋章 / 墙面 / 校徽）渲染这些中文字串。英文 prompt 里要用 `render the exact Chinese text "..."` 明确指令 Nano Banana 2
  - 每张图必须与对应台词内容直接相关，严禁出现与台词主题无关的画面
  - ★ 动态素材优先：普通 ADR/HADS 不是全程口播头像。即使题材来自演讲/采访/人物传记，也最多少量使用讲台/正面发言镜头；其余必须优先给可运动 B-roll（人物走动、手部操作、设备运转、观众反应、场景穿行、道具特写、屏幕/机器/车辆/人群运动），避免连续静态 talking-head。
  - {'★ 黄历反 cliché：严禁"翻黄历的老者/老头/白须长袍老人"刻板形象出现在任何一张图里。默认无人（物件派）；允许人物的板块必须多样化（织女/医者/书生/农夫/神像/现代家庭），不得重复老者。英文 prompt 里可加 negative 指令 "no elderly man reading almanac, no white-bearded old scholar in robe"' if almanac_data else ''}
  - 最后一张图必须是{'明亮温馨的收尾场景（如孩子们的笑脸、阳光洒满场景、竖起大拇指、举手欢呼等），充满希望与祝福' if tone == '轻松' else '温馨收尾调性（如福字、红灯笼、家庭团圆、祝福场景）'}，与结尾祝语呼应

输出格式（严格 JSON 数组，{num_lines} 个元素）：
[
  {{"emotion": "情绪标签", "prompt": "英文提示词"}},
  ...
]
只输出 JSON，不加任何说明文字。"""

    # 姜文导演用 Claude 4.6 Opus（顶级推理 + 多约束遵守）
    # ★ max_tokens=3072（22 个 50 词 prompt ≈ 2200 tokens 输出，留余量但不让 Opus 推理太久撞 gateway 504）
    # ★ Opus 写"40-60 词短 prompt"——降低单次输出 tokens → gateway 推理时间内完成
    if _script_injected:
        motif_pool = [
            "macro glowing semiconductor wafer on a dark table",
            "Air Force One boarding stairs at night with tense silhouettes",
            "executive black leather jacket figure walking through airport security",
            "Washington negotiation room with folders, flags cropped abstractly, market charts",
            "Wall Street terminal screens showing semiconductor supply-chain graphs",
            "chip factory cleanroom with robotic arms moving wafers",
            "Boeing aircraft storage line under cloudy industrial sky",
            "Midwest farm grain elevator and commodity price dashboard",
            "corporate blacklist document stamped on glass table",
            "wide geopolitical map with trade routes and data overlays",
        ]
        emotions = ["紧张", "压抑", "辉煌", "紧张", "压抑", "释然"]
        visuals = []
        for i, line in enumerate(lines):
            dialogue_meta = dialogue_turns[i] if ADS_DIALOGUE_MODE and i < len(dialogue_turns) else {}
            speaker = str(dialogue_meta.get("speaker", "")).strip()
            needs_lip_sync = bool(dialogue_meta.get("needs_lip_sync", False))
            motif = motif_pool[i % len(motif_pool)]
            if needs_lip_sync and any(k in speaker for k in ("黄仁勋", "Jensen")):
                motif = (
                    "cinematic A-roll of Jensen Huang-like Asian male technology CEO in black leather jacket, "
                    "three-quarter close-up, active speaking mouth, small hand gesture, GPU demo screen behind him"
                )
            elif needs_lip_sync and any(k in speaker for k in ("特朗普", "川普", "Trump")):
                motif = (
                    "cinematic A-roll of older blond American president-like politician in navy suit and red tie, "
                    "three-quarter close-up, active speaking mouth, assertive hand gesture, White House press corridor behind him"
                )
            elif needs_lip_sync and speaker:
                motif = (
                    f"cinematic A-roll of {speaker} speaking on location, three-quarter close-up, "
                    "active mouth, expressive hand gesture, listeners blurred behind"
                )
            elif any(k in line for k in ("黄仁勋", "老黄", "英伟达")):
                motif = "black leather jacket technology CEO silhouette beside a glowing GPU chip"
            elif any(k in line for k in ("空军1号", "飞机", "机舱")):
                motif = "Air Force One boarding stairs, executive traveler with backpack, night runway lights"
            elif any(k in line for k in ("财报", "市场份额", "高通", "美光", "苹果")):
                motif = "financial dashboard, semiconductor revenue chart, chip wafer macro foreground"
            elif any(k in line for k in ("波音", "737")):
                motif = "grounded Boeing-style narrow-body jets, hangar shadows, anxious aerospace executives"
            elif any(k in line for k in ("农业", "大豆", "玉米", "农场")):
                motif = "Midwest soybean and corn fields with commodity futures chart overlay"
            prompt = (
                "contemporary geopolitical business documentary photography, deep navy and steel gray palette, "
                "semiconductor gold accents, 4k photorealistic detail, "
                f"{'extreme close-up' if i < 2 else 'wide shot' if i >= len(lines)-2 else 'medium shot'}, "
                f"{'low-angle tense' if i % 3 == 0 else 'high-angle analytical' if i % 3 == 1 else 'profile side view'}, "
                "chiaroscuro single-key lighting, motion-ready B-roll, "
                f"{motif}, no TV studio, no onsite reporter, no talking-head anchor, no ancient costume"
            )
            if dialogue_meta:
                prompt += (
                    f", semantic context from the spoken line: 「{str(line)[:90]}」, "
                    "use this only to choose visuals, do not render subtitles or visible text"
                )
            visuals.append({"emotion": emotions[i % len(emotions)], "prompt": prompt})
        log(f"外部脚本注入：使用确定性财经科技分镜 prompt，共 {len(visuals)} 个")
    else:
        raw_json = chat(
            "CLAUDE_4_6_OPUS",
            "你是精通各类电影镜头语言的导演。每个画面必须指定景别+机位+光影+视觉母题，严禁默认居中中景平庸画面。★ 输出限制：每条英文 prompt 严格 40-60 词（更长会撞 WeryAI gateway 504 timeout）。★ 绝对禁令：你输出的英文 prompt 里禁止出现任何具体导演/画家/艺术家姓名（Akira Kurosawa / Zhang Yimou / Ang Lee / Wong Kar-wai / Christopher Nolan / Caravaggio / Rembrandt / Sergio Leone 等都禁止），改用纯描述词。OpenAI GPT Image 2 对人名风格模仿触发版权 filter 强制拒绝。只输出 JSON。",
            jiangwen_prompt,
            max_tokens=3072,
            timeout=300,
        )
        # 直接定位 JSON 数组边界：第一个 [ 到最后一个 ]
        arr_start = raw_json.find('[')
        arr_end = raw_json.rfind(']')
        if arr_start == -1:
            raise RuntimeError(f"姜文输出解析失败（无 [）: {raw_json[:200]}")
        if arr_end == -1 or arr_end <= arr_start:
            # JSON 被截断（max_tokens 不够），尝试补全：截到最后一个完整 }，补 ]
            last_brace = raw_json.rfind('}')
            if last_brace > arr_start:
                repaired = raw_json[arr_start:last_brace + 1] + ']'
                log(f"JSON 被截断，尝试修复（补 ]）")
            else:
                raise RuntimeError(f"姜文输出解析失败（无 ]）: {raw_json[:200]}")
        else:
            repaired = raw_json[arr_start:arr_end + 1]
        try:
            visuals = json.loads(repaired)[:num_lines]
        except json.JSONDecodeError:
            # JSON 内部截断（对象写到一半），逐步回退到最后一个完整对象
            fixed = repaired
            while fixed and fixed != '[':
                last_brace = fixed.rfind('}')
                if last_brace <= 0:
                    break
                fixed = fixed[:last_brace + 1] + ']'
                try:
                    visuals = json.loads(fixed)[:num_lines]
                    log(f"JSON 修复成功（回退到 {len(visuals)} 个完整对象）")
                    break
                except json.JSONDecodeError:
                    fixed = fixed[:last_brace]  # 继续回退
            else:
                raise RuntimeError(f"姜文输出 JSON 无法修复: {raw_json[:200]}")
    # 视觉描述不足时用默认值填充（兜底也随题材走，避免历史 cliché 污染黄历/现代题材）
    if almanac_data:
        fb_emotion = "平和"
        fb_prompt = "traditional Chinese almanac scene, ink-wash brush painting, bamboo scroll with red seal stamp, warm earth tones, Jiangnan garden atmosphere, no elderly man reading almanac, no white-bearded scholar"
    elif tone == "轻松":
        fb_emotion = "欢快"
        fb_prompt = "bright cheerful children's illustration, warm sunny colors, modern school cafeteria scene, smiling kids, high saturation, hopeful atmosphere"
    else:
        fb_emotion = "紧张"
        fb_prompt = "cinematic historical documentary still, sepia tone, dramatic lighting"
    while len(visuals) < num_lines:
        visuals.append({"emotion": fb_emotion, "prompt": fb_prompt})
    log(f"姜文输出 {len(visuals)} 个视觉描述（需要 {num_lines} 个）")

    # tone 决定情绪→风格查询池
    style_pool = EMOTION_STYLE_BRIGHT if tone == "轻松" else EMOTION_STYLE

    # 生成镜头蓝本（按分镜号硬注入景别+机位+光影+母题，绕过 LLM 对镜头语法的软性遵从）
    shot_blueprint = build_shot_blueprint(num_lines)
    # ★ STYLE_KEY 锁全片画风（最高优先级，每条 prompt 头部强制引用，确保 22 张图视觉一致）
    # director 字段已改为返回纯描述词（无具体姓名）
    base_style = topic_meta.get("director", "Zen contemplative cinematography, deep focus, soft warm tones")
    # 强化为全片 visual cohesion 锚——所有 22 张图都是这个 STYLE_KEY 系列大片
    style_key = (
        f"editorial magazine photography series, {base_style}, "
        f"warm cream and sage green palette, soft natural daylight, "
        f"4k photorealistic detail, consistent visual identity throughout series, "
        f"shot by single photographer with single camera and lighting setup"
    )
    director_tag = style_key
    neg_tag = topic_meta.get("negative", "")
    culture_guard = _topic_culture_guard(topic_meta)

    script = []
    emotion_count: dict[str, int] = {}
    for i, line in enumerate(lines):
        emotion = visuals[i].get("emotion", fb_emotion)
        dialogue_meta = dialogue_turns[i] if ADS_DIALOGUE_MODE and i < len(dialogue_turns) else {}
        if dialogue_meta.get("emotion"):
            emotion = dialogue_meta["emotion"]
        style   = style_pool.get(emotion, "")
        shot_tmpl = shot_blueprint[i] if i < len(shot_blueprint) else ""
        subject = visuals[i].get("prompt", "")
        if dialogue_meta:
            _dlg_gender = (dialogue_meta.get("voice_gender") or dialogue_meta.get("gender") or "").strip().lower()
            if _dlg_gender not in ("male", "female"):
                _voice_gender = _adsd_gender_from_voice({"voice_id": dialogue_meta.get("speaker_id")})
                _dlg_gender = _voice_gender or _adsd_infer_gender_from_speaker(dialogue_meta.get("speaker", "")) or "male"
            _dlg_visual = (dialogue_meta.get("visual_subject") or "").strip()
            if _adsd_visual_subject_has_gender_conflict(_dlg_visual, _dlg_gender):
                log(f"ADSD visual_subject 与音色性别冲突，忽略 visual_subject：{dialogue_meta.get('speaker')} {_dlg_gender} / {_dlg_visual}")
                _dlg_visual = ""
                dialogue_meta["visual_subject"] = ""
            visual_contract = _adsd_visual_contract(
                dialogue_meta.get("speaker", ""),
                gender=_dlg_gender,
                visual_subject=_dlg_visual,
            )
            # 路径区分：LLM 主路径（visual_subject）/ 兜底（仅 gender）
            speaker_meta = dialogue_meta.get('speaker', '')
            if _dlg_visual and len(_dlg_visual.split()) >= 4:
                speaker_tag = f"{speaker_meta} (voice={_dlg_gender or 'unknown'}, form={_dlg_visual})"
            else:
                speaker_tag = f"{speaker_meta} ({_dlg_gender or 'unknown'})"
            subject = (
                f"{dialogue_meta.get('shot', '')}. "
                f"Dialogue speaker: {speaker_tag}; "
                f"{visual_contract}. "
                f"{subject}"
            )
        # 硬拼接：导演 + 镜头模板 + 主体 + 情绪风格 + negative
        parts = [director_tag, culture_guard, shot_tmpl, subject]
        if style:
            parts.append(style)
        prompt = ", ".join(p for p in parts if p)
        if is_1919_global_topic(topic):
            prompt += (
                ". Historical accuracy lock: 1919 Republican-era Beijing or post-WWI global setting; "
                "Tiananmen must be pre-1949 without Mao portrait, without PRC flag, without People's Heroes Monument, "
                "without modern Tiananmen decorations; use period student petitions, newspapers, telegrams, dark diplomatic coats, colonial-era streets"
            )
        if neg_tag:
            prompt += f". Negative: {neg_tag}"
        if not ADS_DIALOGUE_MODE:
            prompt += (
                ". Motion-ready shot design: avoid static talking-head or podium repetition; include one visible kinetic element "
                "such as walking, hand operation, machinery, crowd reaction, screen interaction, fabric, smoke, dust, or a moving camera path"
            )
        # 武侠/修真动作场面：B-roll 且 text 命中 ≥2 个 action keyword → 替换 prompt 为专用 combat panel
        # 让 GPT Image 2 出真打斗画面（剑光/灵气/凌空）而不是"两人交谈"通用纪录片调
        if (
            ADS_DIALOGUE_MODE
            and dialogue_meta
            and not dialogue_meta.get("needs_lip_sync", True)
            and _is_action_scene(dialogue_meta.get("text", ""), dialogue_meta.get("shot", ""))
        ):
            prompt = _wuxia_action_panel_prompt(
                dialogue_meta.get("text", ""),
                dialogue_meta.get("shot", ""),
                dialogue_meta.get("visual_subject", ""),
                voice_gender=dialogue_meta.get("voice_gender") or _dlg_gender,
            )
            log(f"动作 panel 替换 prompt: turn {i+1} 「{dialogue_meta.get('text','')[:30]}...」 → 武侠 combat panel")
        item = {
            "text": line,
            "emotion": emotion,
            "prompt": prompt,
            "historical_context": historical_context,
            "tone": tone,
            "topic_meta": topic_meta,
            "culture_guard": culture_guard,
        }
        if _script_injected:
            item["injected_script"] = True
            if i < len(_override_timings) and _override_timings[i]:
                timing = _override_timings[i] or {}
                item.update({
                    "override_time_label": timing.get("label"),
                    "override_audio_start": timing.get("start"),
                    "override_audio_end": timing.get("end"),
                    "override_duration": max(0.1, float(timing.get("end", 0)) - float(timing.get("start", 0))),
                })
        if ADS_RETENTION_MODE and not ADS_DIALOGUE_MODE:
            if i == 0:
                retention_role = "hook"
            elif i == len(lines) - 1:
                retention_role = "payoff"
            elif abs(i - (len(lines) // 2)) <= 1:
                retention_role = "mid_rehook"
            else:
                retention_role = "progression"
            item.update({
                "retention_mode": True,
                "retention_role": retention_role,
            })
        if dialogue_meta:
            item.update({
                "dialogue_mode": True,
                "dialogue_turn": dialogue_meta.get("dialogue_turn", i + 1),
                "speaker": dialogue_meta.get("speaker", ""),
                "voice_gender": dialogue_meta.get("voice_gender") or dialogue_meta.get("gender"),
                "visual_subject": dialogue_meta.get("visual_subject", ""),
                "speaker_id": dialogue_meta.get("speaker_id"),
                "speaker_name": dialogue_meta.get("speaker_name", ""),
                # P3：把 voice_asset_id 从 dialogue_meta 透传到 script item
                # 否则 step66 的 _select_voice_asset_reference 拿不到 explicit asset，
                # 全部降级到 ADSD_DEFAULT_MALE/FEMALE_VOICE_ASSET
                "voice_asset_id": dialogue_meta.get("voice_asset_id"),
                # A-roll / B-roll 判定：True = WERYDANCE lip-sync，False = motion mode 自由动效
                "needs_lip_sync": dialogue_meta.get("needs_lip_sync", True),
                "shot": dialogue_meta.get("shot", ""),
                "dialogue_shape": dialogue_meta.get("dialogue_shape", ""),
                "speaker_count": dialogue_meta.get("speaker_count"),
                "speaker_visual_contract": visual_contract,
                "lip_sync_experiment": ADSD_LIP_SYNC_EXPERIMENT,
                "onsite_pov_mode": ADSD_ONSITE_POV_MODE,
            })
        script.append(item)
        emotion_count[emotion] = emotion_count.get(emotion, 0) + 1

    emotion_summary = " / ".join(f"{k}×{v}" for k, v in emotion_count.items())
    _ensure_motion_action_plan(script)
    tg(f"✅ 画面提示词就绪，情绪标签分布：{emotion_summary}")

    # 音色选择：根据主题和情绪由 LLM 推荐最合适的音色
    voice_style_samples = " / ".join(
        lines[i]
        for i in sorted({0, len(lines) // 2, len(lines) - 1})
        if 0 <= i < len(lines)
    )
    voice_prompt = f"""你是纪录片音频导演。根据主题和情绪，从以下音色中选择最合适的一个。

主题：{topic}
情绪分布：{emotion_summary}
台词风格：{voice_style_samples}

可选音色：
• 古今先生 pingshu-c7c18f5a — 评书风格，沧桑厚重，适合古代史、传奇人物、战争
• 常四爷 shuoshurennan-fdfa85f9 — 说书人，叙事感强，适合民间故事、历史事件
• 国栋 liyan2-ef9401ec — 标准男声，沉稳可靠，适合现代史、科技、人物传记
• 子墨 liyan3-f74976d9 — 温润男声，内敛儒雅，适合文化、艺术、哲学题材
• 谷川 zh-male-guchuan-9d6a4666 — 低沉男声，适合自然、地理、探险题材
• 原野 CN-Man-Beijing-V2 — 北京口音，质朴有力，适合革命史、延安、北方题材
• 故事精灵 gushijingling-720c0ae5 — 生动活泼，适合轻松科普、少儿向
• 苏哲 suzhe-45bbbe54 — 知性男声，适合社会议题、纪实调查
• 晓曼 chat-girl-105-cn — 温柔女声，适合女性人物、情感类
• 高晴 gaoqing3-bfb5c88a — 明亮女声，适合积极向上的现代题材
• 柳飞霜 shuoshurennan-b09f844f — 古风女声，适合古代女性人物

只输出一行 JSON：{{"speaker_id": "xxx", "speaker_name": "xxx", "reason": "一句话理由"}}"""

    # 音色选择优先级：--speaker 显式指定 > VDAR 竖屏默认晓曼 > LLM 自选 > 硬编码兜底
    if SPEAKER_OVERRIDE_ID:
        picked_id = SPEAKER_OVERRIDE_ID
        picked_name = SPEAKER_OVERRIDE_NAME
        tg(f"🎤 用户指定音色：{picked_name}（{picked_id}）")
    elif IS_VERTICAL:
        # 竖屏 VDAR 默认女声（面向中老年受众）
        picked_id = "chat-girl-105-cn"
        picked_name = "晓曼"
        tg(f"🎤 竖屏模式，使用女声：{picked_name}")
    else:
        try:
            raw = chat("GEMINI_25_FLASH", "你是音频导演，只输出 JSON。", voice_prompt)
            voice_pick = json.loads(re.search(r'\{[\s\S]+\}', raw).group())
            picked_id = voice_pick["speaker_id"]
            picked_name = voice_pick["speaker_name"]
            reason = voice_pick.get("reason", "")
            tg(f"🎤 音色推荐：{picked_name}（{picked_id}）\n理由：{reason}")
        except Exception as e:
            log(f"音色推荐失败，使用默认: {e}")
            picked_id = "liyan2-ef9401ec"
            picked_name = "国栋"

    _write_ads_retention_qa(script)
    return script, picked_id, picked_name


def _write_ads_retention_qa(script: list[dict]) -> dict:
    if not ADS_RETENTION_MODE or ADS_DIALOGUE_MODE:
        return {"enabled": False}

    def _plain_len(text: str) -> int:
        return len(re.sub(r"\s+", "", str(text or "")))

    def _contains_any(text: str, needles: list[str]) -> bool:
        return any(n in text for n in needles)

    first = script[0] if script else {}
    first_text = str(first.get("text", "")).strip()
    first_prompt = str(first.get("prompt", "")).lower()
    all_text = "\n".join(str(x.get("text", "")) for x in script)
    mid_items = script[max(0, len(script) // 2 - 2): len(script) // 2 + 3] if script else []
    mid_text = "\n".join(str(x.get("text", "")) for x in mid_items)
    banned_terms = ["震惊", "全网", "内幕", "炸裂", "家人们", "速看", "离谱到家"]
    flat_opening = bool(re.match(r"^\s*(公元)?\d{3,4}年|^\s*\d{1,2}月\d{1,2}日|^\s*在.{0,8}\d{3,4}年", first_text))
    hook_markers = ["？", "?", "但", "却", "竟", "只", "最", "第一", "不是", "真正", "代价", "危险", "改变", "死", "输", "赢"]
    visual_markers = [
        "close-up", "extreme close-up", "insert shot", "hand", "eye", "face",
        "blood", "flame", "document", "telegram", "letter", "shadow", "silhouette",
    ]
    generic_visual = any(term in first_prompt for term in [
        "wide establishing shot", "documentary style", "standard shot", "straightforward composition"
    ])

    checks = {
        "first_line_short": _plain_len(first_text) <= 24,
        "first_line_not_flat_date": not flat_opening,
        "first_line_has_hook_signal": _contains_any(first_text, hook_markers),
        "no_low_quality_traffic_terms": not _contains_any(all_text, banned_terms),
        "first_prompt_thumb_stopping": _contains_any(first_prompt, visual_markers) and not generic_visual,
        "has_mid_rehook": _contains_any(mid_text, ["真正", "但", "可是", "谁也没想到", "代价", "问题", "结果", "为什么", "怎么"]),
    }
    qa = {
        "enabled": True,
        "mode": "ads_retention_non_reporter",
        "pass": all(checks.values()),
        "checks": checks,
        "first_text": first_text,
        "first_prompt": first.get("prompt", ""),
        "retention_roles": [x.get("retention_role") for x in script if x.get("retention_mode")],
    }
    try:
        with open(os.path.join(OUTPUT_DIR, "retention_qa.json"), "w", encoding="utf-8") as f:
            json.dump(qa, f, ensure_ascii=False, indent=2)
        if qa["pass"]:
            tg("✅ ADS 播放量模式 QA 通过：前三秒钩子、低质流量词、首图吸引力已检查")
        else:
            failed = ", ".join(k for k, v in checks.items() if not v)
            tg(f"⚠️ ADS 播放量模式 QA 有警告：{failed}")
    except Exception as e:
        log(f"retention QA 写入失败: {e}")
    return qa


# ── 第二步：逐句生成音轨（WeryAI Podcast，线程池并发）─────────────────────────
def _openai_tts_fallback(script: list[dict]) -> str:
    """OpenAI gpt-4o-mini-tts 兜底——纪录片旁白质量优于 edge-tts。"""
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY 未设置")

    VOICE = "coral"
    INSTRUCTIONS = (
        "用中文纪录片旁白的语气朗读：温柔、缓慢、稳重，"
        "句末适度下沉，关键词处适当停顿。不要做戏剧化处理。"
    )

    tg(f"🎙 启用 OpenAI TTS 兜底（gpt-4o-mini-tts, 音色：{VOICE}）...")

    seg_paths = []
    for i, s in enumerate(script):
        p = OUTPUT_DIR / f"voice_{i}.mp3"
        resp = requests.post(
            "https://api.openai.com/v1/audio/speech",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "gpt-4o-mini-tts",
                "voice": VOICE,
                "input": s["text"],
                "instructions": INSTRUCTIONS,
            },
            timeout=60,
        )
        resp.raise_for_status()
        with open(p, "wb") as f:
            f.write(resp.content)
        seg_paths.append(str(p))

    concat_list = OUTPUT_DIR / "voice_concat.txt"
    with open(concat_list, "w") as f:
        for p in seg_paths:
            f.write(f"file '{p}'\n")

    voice_path = str(OUTPUT_DIR / "master_voice.mp3")
    ffmpeg("-f", "concat", "-safe", "0", "-i", str(concat_list), "-c", "copy", voice_path)
    return voice_path


def _edge_tts_fallback(script: list[dict]) -> str:
    """edge-tts 二级兜底——OpenAI 也失败时使用。"""
    import asyncio as _aio
    import edge_tts

    VOICE = "zh-CN-YunjianNeural"
    tg(f"🎙 Podcast 不可用，启用 Edge TTS 兜底（音色：{VOICE}）...")

    seg_paths = []
    async def _synth():
        for i, s in enumerate(script):
            p = str(OUTPUT_DIR / f"voice_{i}.mp3")
            await edge_tts.Communicate(s["text"], VOICE, rate="-10%", pitch="-30Hz").save(p)
            seg_paths.append(p)

    _aio.run(_synth())

    concat_list = OUTPUT_DIR / "voice_concat.txt"
    with open(concat_list, "w") as f:
        for p in seg_paths:
            f.write(f"file '{p}'\n")

    voice_path = str(OUTPUT_DIR / "master_voice.mp3")
    ffmpeg("-f", "concat", "-safe", "0", "-i", str(concat_list), "-c", "copy", voice_path)
    return voice_path


# 第三方 API content-policy 脱敏：仅作用于外部接口入参，ADR 内部 script/字幕/文案保持原词
_SENSITIVE_TERMS = {
    "大屠杀": "重大冲突", "惨案": "事件", "屠杀": "冲突",
    "国耻": "历史", "殉难": "殉职", "殉国": "牺牲",
    "侵略": "入境", "暴行": "行为", "血洗": "进入",
}

_ADSD_POLICY_REWRITE_TERMS = {
    "最后通牒": "限期照会",
    "威胁": "施压",
    "胁迫": "施压",
    "开战": "扩大冲突",
    "战争": "战事",
    "军事": "军务",
}

def _sanitize_for_external_api(text: str) -> str:
    if not text:
        return text
    out = text
    for k, v in _SENSITIVE_TERMS.items():
        out = out.replace(k, v)
    return out


def _is_content_policy_error(err: Exception) -> bool:
    s = str(err).lower()
    return (
        "text-fail" in s
        or "audio-fail" in s
        or "content policy" in s
        or "policy violation" in s
        or "sensitive" in s
        or "1002" in s
        or "敏感内容" in s
        or "内容审查" in s
    )


def _rewrite_adsd_tts_text_for_policy(text: str, speaker: str, err: Exception) -> str:
    """Rewrite only the blocked ADSD TTS line into neutral historical wording."""
    original = text or ""
    sanitized = _sanitize_for_external_api(original)
    prompt = f"""把下面这句短视频对白改写成更中性、可播报的历史说明，用于 TTS。

要求：
1. 保留事实含义，不新增事件。
2. 避免强烈控诉、暴力、威胁、仇恨、煽动词。
3. 仍然像人物对白，不要写成论文。
4. 不超过 {max(28, min(70, len(original) + 8))} 个汉字。
5. 只输出改写后的这一句，不加引号、不加解释。

角色：{speaker}
原句：{sanitized}
接口错误：{str(err)[:120]}
"""
    rewritten = ""
    try:
        rewritten = chat(
            "GEMINI_25_FLASH",
            "你是历史短视频对白编辑，只输出一行可播报中文。",
            prompt,
            max_tokens=180,
            timeout=90,
        ).strip()
    except Exception as e:
        log(f"ADSD TTS policy 改写 LLM 失败，走规则兜底：{e}")
    rewritten = re.sub(r'^[「"“”]+|[」"“”]+$', "", rewritten).strip()
    rewritten = rewritten.splitlines()[0].strip() if rewritten else ""
    if not rewritten or rewritten == original:
        rewritten = sanitized
        for k, v in _ADSD_POLICY_REWRITE_TERMS.items():
            rewritten = rewritten.replace(k, v)
    rewritten = _sanitize_for_external_api(rewritten)[:500]
    if not rewritten:
        rewritten = "这件事需要放回当年的国际形势里看。"
    return rewritten


def _record_adsd_tts_rewrite(idx: int, speaker: str, before: str, after: str, err: Exception):
    try:
        path = OUTPUT_DIR / "tts_policy_rewrites.jsonl"
        payload = {
            "turn": idx + 1,
            "speaker": speaker,
            "before": before,
            "after": after,
            "error": str(err)[:300],
            "created_at": datetime.now().isoformat(timespec="seconds"),
        }
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")
    except Exception as e:
        log(f"ADSD TTS policy 改写记录失败: {e}")


# text-to-audio 主路径默认 voice_id：横竖屏均默认女声（万年历视频号主力听众偏好）
# 用户可通过 ADR_TTS_VOICE_ID 显式覆盖；--speaker 走 podcast 兜底路径不影响这里
_TEXT_TO_AUDIO_DEFAULT_VOICE = {
    "h": 78,   # Gentle Senior       - 女声温柔知性，纪录片向
    "v": 78,   # Gentle Senior       - 同上
}


def _build_silence_mp3(duration_s: float, out_path: str, sample_rate: int = 44100) -> str:
    """生成指定时长的静音 mp3 段，用于拼接到 master_voice 中。"""
    duration_s = max(0.0, float(duration_s))
    ffmpeg(
        "-f", "lavfi",
        "-i", f"anullsrc=channel_layout=mono:sample_rate={sample_rate}",
        "-t", f"{duration_s:.3f}",
        "-acodec", "libmp3lame", "-b:a", "128k",
        out_path,
    )
    return out_path


def _audio_duration_seconds(audio_path: str) -> float:
    try:
        out = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=nw=1:nokey=1", audio_path],
            capture_output=True, text=True, timeout=15,
        ).stdout.strip()
        return float(out) if out else 0.0
    except Exception:
        return 0.0


def _text_to_audio_master_voice_timed(script: list[dict], voice_id: int, speed: str, vol: str) -> str | None:
    """override timing 模式：每段独立 TTS + 用静音段补齐到 timecode 目标位置，
    让最终 master_voice 总时长 ≈ override 总时长，每段对位 timecode。

    QA：落盘 master_voice_timed_qa.json，方便人工对照"
    """
    fmt_topic = OUTPUT_DIR.name
    seg_files: list[tuple[str, float, float]] = []   # (path, kind=tts/silence, dur)
    qa_records: list[dict] = []
    cumulative = 0.0  # 拼接后游标
    for idx, s in enumerate(script):
        text_raw = (s.get("text") or "").strip()
        target_start = float(s.get("override_audio_start") or 0.0)
        target_end = float(s.get("override_audio_end") or 0.0)
        target_dur = max(0.1, target_end - target_start)
        # 先补齐到 target_start
        pad_before = max(0.0, target_start - cumulative)
        if pad_before > 0.05:
            sp = str(OUTPUT_DIR / f"tts_silence_pre_{idx:02d}.mp3")
            _build_silence_mp3(pad_before, sp)
            seg_files.append((sp, "silence", pad_before))
            cumulative += pad_before
        # TTS this section
        if not text_raw:
            # 空文本 → 用静音填满 target_dur
            sp = str(OUTPUT_DIR / f"tts_silence_only_{idx:02d}.mp3")
            _build_silence_mp3(target_dur, sp)
            seg_files.append((sp, "silence", target_dur))
            cumulative += target_dur
            qa_records.append({"line": idx + 1, "tts_dur": 0.0, "target_dur": target_dur,
                               "pad_before": pad_before, "pad_after": 0.0,
                               "kind": "empty_text_silence_only"})
            continue
        sanitized = _sanitize_for_external_api(text_raw)
        if sanitized and sanitized[-1] not in "。！？.!?；;":
            sanitized = sanitized + "。"
        try:
            r = req_post("/generation/text-to-audio", {
                "text": sanitized,
                "voice_id": voice_id,
                "speed": speed,
                "vol": vol,
                "trace_id": f"adr-{fmt_topic}-timed-{idx+1:02d}",
            }, timeout=30)
            task_id = r.get("data", {}).get("task_id") or (r.get("data", {}).get("task_ids") or [None])[0]
            if not task_id:
                log(f"timed TTS 第 {idx+1} 段无 task_id: {json.dumps(r, ensure_ascii=False)[:200]}")
                return None
            data = poll_task_status(task_id, f"timed TTS {idx+1}", max_wait=180)
            audios = data.get("audios") or []
            if not audios:
                log(f"timed TTS 第 {idx+1} 段无 audios")
                return None
            tts_path = str(OUTPUT_DIR / f"tts_line_{idx:02d}.mp3")
            urllib.request.urlretrieve(audios[0], tts_path)
        except Exception as e:
            log(f"timed TTS 第 {idx+1} 段失败：{e}")
            return None
        tts_dur = _audio_duration_seconds(tts_path)
        seg_files.append((tts_path, "tts", tts_dur))
        cumulative += tts_dur
        # 补齐到 target_end
        pad_after = max(0.0, target_end - cumulative)
        if pad_after > 0.05:
            sp = str(OUTPUT_DIR / f"tts_silence_post_{idx:02d}.mp3")
            _build_silence_mp3(pad_after, sp)
            seg_files.append((sp, "silence", pad_after))
            cumulative += pad_after
        qa_records.append({
            "line": idx + 1,
            "target_start": target_start,
            "target_end": target_end,
            "target_dur": round(target_dur, 3),
            "tts_dur": round(tts_dur, 3),
            "pad_before": round(pad_before, 3),
            "pad_after": round(pad_after, 3),
            "tts_exceeds_target": tts_dur > target_dur + 0.5,
            "cumulative_after_segment": round(cumulative, 3),
        })

    if not seg_files:
        return None
    concat_list = OUTPUT_DIR / "tts_timed_concat.txt"
    with open(concat_list, "w") as f:
        for p, _kind, _dur in seg_files:
            f.write(f"file '{p}'\n")
    voice_path = str(OUTPUT_DIR / "master_voice.mp3")
    # 静音 mp3 + TTS mp3 编码参数可能不同，用 re-encode 而不是 copy
    ffmpeg("-f", "concat", "-safe", "0", "-i", str(concat_list),
           "-c:a", "libmp3lame", "-b:a", "128k", voice_path)
    final_dur = _audio_duration_seconds(voice_path)
    total_target = float(script[-1].get("override_audio_end") or cumulative)
    qa = {
        "mode": "text_to_audio_timed_with_silence_padding",
        "policy": "respect_override_timecodes_pad_silence_to_match",
        "voice_id": voice_id,
        "speed": speed,
        "vol": vol,
        "total_lines": len(script),
        "tts_segment_count": sum(1 for _, k, _ in seg_files if k == "tts"),
        "silence_segment_count": sum(1 for _, k, _ in seg_files if k == "silence"),
        "final_master_voice_duration": round(final_dur, 3),
        "override_total_target_duration": round(total_target, 3),
        "duration_delta_vs_target": round(final_dur - total_target, 3),
        "tts_overruns_count": sum(1 for r in qa_records if r.get("tts_exceeds_target")),
        "per_line": qa_records,
        "manual_visual_checks_required": [
            "each_line_audio_aligns_with_timecode",
            "no_tts_clipping_at_section_boundaries",
            "silence_pads_dont_feel_too_long_in_between",
        ],
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }
    try:
        (OUTPUT_DIR / "master_voice_timed_qa.json").write_text(
            json.dumps(qa, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as e:
        log(f"master_voice_timed_qa.json 写入失败: {e}")
    overruns = qa["tts_overruns_count"]
    tg(f"🎙 timed TTS 完成：{qa['tts_segment_count']} 段 + {qa['silence_segment_count']} 静音 "
       f"→ {qa['final_master_voice_duration']}s（target {qa['override_total_target_duration']}s）"
       + (f"\n⚠️ {overruns} 段 TTS 超出 timecode 目标，节奏会被挤" if overruns else ""))
    return voice_path


def _text_to_audio_master_voice(script: list[dict]) -> str | None:
    """主路径：用 /generation/text-to-audio TTS，拼接成主音轨。
    优先策略：脚本总字符 ≤ 500 时一次性整段送，保留 TTS 引擎自然语义停顿；
    超长则按句号边界 smart-split 成多个 ≤ 500 字符 chunk。
    若 script 携带 override_audio_start/end → 切换 timed 模式，逐句 TTS + 静音补齐到 timecode。
    成功返回 master_voice.mp3 路径；失败返回 None 让调用方降级到 Podcast。"""
    fmt_key = "v" if IS_VERTICAL else "h"
    default_voice = _TEXT_TO_AUDIO_DEFAULT_VOICE[fmt_key]
    voice_id = int(os.environ.get("ADR_TTS_VOICE_ID", default_voice))
    speed = os.environ.get("ADR_TTS_SPEED", "1.0")
    vol = os.environ.get("ADR_TTS_VOL", "4.0")

    # override timing 优先：注入脚本带 0:00-X:XX 时间码 → 走 timed 模式，
    # 每段独立 TTS + 静音补齐 timecode 目标位置，最终时长 ≈ override 总时长
    if any(s.get("override_audio_start") is not None for s in script):
        tg(f"🎙 检测到 override timecode（{len(script)} 段），TTS 切换 timed 模式")
        return _text_to_audio_master_voice_timed(script, voice_id, speed, vol)

    # 拼接所有台词，句末加中文句号确保 TTS 识别停顿
    parts: list[str] = []
    for s in script:
        t = (s.get("text") or "").strip()
        if not t:
            continue
        # 确保句末有标点，让 TTS 自然换气
        if t and t[-1] not in "。！？.!?；;":
            t = t + "。"
        parts.append(t)
    full_text = "".join(parts)
    if not full_text:
        return None
    full_text = _sanitize_for_external_api(full_text)

    # smart-split：尽量按句号切，控制每块 ≤ 500 字符
    LIMIT = 500
    chunks: list[str] = []
    if len(full_text) <= LIMIT:
        chunks = [full_text]
    else:
        # 按句号/感叹/问号切分，贪心装箱
        sentences = re.split(r"(?<=[。！？!?])", full_text)
        sentences = [s for s in sentences if s.strip()]
        cur = ""
        for s in sentences:
            if len(s) > LIMIT:
                # 单句超长（罕见），硬切
                if cur:
                    chunks.append(cur)
                    cur = ""
                for j in range(0, len(s), LIMIT):
                    chunks.append(s[j:j + LIMIT])
                continue
            if len(cur) + len(s) > LIMIT:
                chunks.append(cur)
                cur = s
            else:
                cur += s
        if cur:
            chunks.append(cur)

    tg(f"🎙 text-to-audio 主路径：voice_id={voice_id}，{len(full_text)} 字 → {len(chunks)} 段...")

    seg_paths: list[str] = []
    for i, chunk in enumerate(chunks):
        try:
            r = req_post("/generation/text-to-audio", {
                "text": chunk,
                "voice_id": voice_id,
                "speed": speed,
                "vol": vol,
                "trace_id": f"adr-{OUTPUT_DIR.name}-chunk-{i+1}",
            }, timeout=30)
            task_id = r.get("data", {}).get("task_id") or (r.get("data", {}).get("task_ids") or [None])[0]
            if not task_id:
                log(f"text-to-audio chunk {i+1} 无 task_id: {json.dumps(r, ensure_ascii=False)[:200]}")
                return None
            data = poll_task_status(task_id, f"text-to-audio chunk {i+1}", max_wait=180)
            audios = data.get("audios") or []
            if not audios:
                log(f"text-to-audio chunk {i+1} succeed 但无 audios")
                return None
            mp3_path = str(OUTPUT_DIR / f"tts_chunk_{i:02d}.mp3")
            urllib.request.urlretrieve(audios[0], mp3_path)
            seg_paths.append(mp3_path)
        except Exception as e:
            log(f"text-to-audio chunk {i+1} 失败：{e}")
            return None

    voice_path = str(OUTPUT_DIR / "master_voice.mp3")
    if len(seg_paths) == 1:
        # 单 chunk 直接重命名/copy，零拼接开销
        import shutil
        shutil.copy(seg_paths[0], voice_path)
    else:
        # 多 chunk concat
        concat_list = OUTPUT_DIR / "tts_concat.txt"
        with open(concat_list, "w") as f:
            for p in seg_paths:
                f.write(f"file '{p}'\n")
        ffmpeg("-f", "concat", "-safe", "0", "-i", str(concat_list), "-c", "copy", voice_path)
    return voice_path


def step2_master_voice(script: list[dict], speaker_id: str = "liyan2-ef9401ec", speaker_name: str = "国栋") -> str:
    n = len(script)
    MAX_RETRIES = 5

    # ★ 新主路径：text-to-audio（速度更稳、API 更简洁），失败降级到现有 Podcast 路径
    # 注意：ADR step1 的 LLM 自选 speaker_id 是 podcast-format 字符串（含 "-"），
    # 不能用 "-" 判定"用户显式 --speaker"。要走 podcast 必须显式 ADR_TTS_LEGACY_PODCAST=1
    use_text_to_audio = (
        os.environ.get("ADR_TTS_LEGACY_PODCAST", "").strip().lower() not in ("1", "true", "yes", "on")
    )
    if use_text_to_audio:
        try:
            voice_path = _text_to_audio_master_voice(script)
            if voice_path and os.path.exists(voice_path) and os.path.getsize(voice_path) > 5000:
                total_dur = ffprobe_duration(voice_path)
                size_kb = os.path.getsize(voice_path) // 1024
                tg(f"✅ text-to-audio 主音轨完成 {total_dur:.1f}s {size_kb}KB")
                return voice_path
            tg("⚠️ text-to-audio 主路径未产出有效音轨，降级到 Podcast")
        except Exception as e:
            tg(f"⚠️ text-to-audio 主路径异常：{str(e)[:120]}，降级到 Podcast")

    tg(f"🎙 单次 Podcast 生成完整音轨（音色：{speaker_name}），{n} 句...")

    def _edge_fallback_with_report(reason: str) -> str:
        tg(f"⚠️ {reason}，自动切换 TTS 兜底...")
        try:
            voice_path = _openai_tts_fallback(script)
            tier = "OpenAI gpt-4o-mini-tts"
        except Exception as e:
            tg(f"⚠️ OpenAI TTS 兜底失败：{e}\n继续退到 Edge TTS...")
            voice_path = _edge_tts_fallback(script)
            tier = "Edge TTS"
        size_kb = os.path.getsize(voice_path) // 1024
        total_dur = ffprobe_duration(voice_path)
        tg(f"✅ {tier} 音轨生成完毕，时长 {total_dur:.2f}s，{size_kb} KB")
        return voice_path

    # Podcast 分层重试：
    # 1) 先拿 text task_id；
    # 2) 同一 task 的 audio 失败先轻量重试；
    # 3) 若状态已固定为 audio-fail，则重建 text task，避免死磕不可恢复 task。
    audio_data = None
    last_err = None
    policy_blocked = False
    AUDIO_RETRIES_PER_TEXT = 2
    for text_attempt in range(MAX_RETRIES):
        tid = None
        try:
            tg(f"🎙 Podcast text 尝试 {text_attempt+1}/{MAX_RETRIES}...")
            r1 = req_post("/generation/podcast/generate/text", {
                "query": _sanitize_for_external_api(script[0]["text"]),
                "speakers": [speaker_id],
                "language": "zh",
                "mode": "deep",
            })
            tid = r1["data"]["task_id"]
            poll_podcast(tid, wait_for="text-success", max_polls=PODCAST_TEXT_POLL_MAX)
            tg(f"✅ Podcast 文本生成成功（task_id={tid}）")
        except Exception as e:
            last_err = e
            if _is_content_policy_error(e):
                policy_blocked = True
                tg(f"⚠️ Podcast text 触发内容审查（{e}），跳过剩余重试，直接走 Edge TTS 兜底...")
                break
            if text_attempt < MAX_RETRIES - 1:
                wait_s = 5 * (text_attempt + 1)
                tg(f"⚠️ Podcast text 第 {text_attempt+1}/{MAX_RETRIES} 次失败：{e}\n{wait_s}s 后重建 text task...")
                time.sleep(wait_s)
                continue
            break

        for audio_attempt in range(AUDIO_RETRIES_PER_TEXT):
            try:
                req_post(f"/generation/podcast/generate/{tid}/audio", {
                    "scripts": [{"speaker_id": speaker_id, "speaker_name": speaker_name, "content": s["text"]} for s in script],
                })
                tg(
                    f"🎙 Podcast audio 尝试 {audio_attempt+1}/{AUDIO_RETRIES_PER_TEXT} "
                    f"（text task {text_attempt+1}/{MAX_RETRIES}, task_id={tid}）..."
                )
                audio_data = poll_podcast(tid, wait_for="audio-success", max_polls=PODCAST_AUDIO_POLL_MAX)
                tg(f"✅ Podcast 音频生成成功（task_id={tid}）")
                break
            except Exception as e:
                last_err = e
                if _is_content_policy_error(e):
                    policy_blocked = True
                    tg(f"⚠️ Podcast audio 触发内容审查（{e}），跳过剩余重试，直接走 Edge TTS 兜底...")
                    break
                if audio_attempt < AUDIO_RETRIES_PER_TEXT - 1:
                    tg(f"⚠️ Podcast audio 失败：{e}\n5s 后复用同一 task 重试 audio...")
                    time.sleep(5)
                    continue
                tg(f"⚠️ Podcast audio 在 task_id={tid} 上失败，重建 text task 再试：{e}")

        if audio_data:
            break
        if policy_blocked:
            break
        if text_attempt < MAX_RETRIES - 1:
            wait_s = 5 * (text_attempt + 1)
            tg(f"⏳ {wait_s}s 后重建 Podcast text task...")
            time.sleep(wait_s)

    if not audio_data:
        reason = f"Podcast 触发内容审查（{last_err}）" if policy_blocked else f"Podcast audio/text {MAX_RETRIES} 轮失败（{last_err}）"
        return _edge_fallback_with_report(reason)

    tr = audio_data.get("task_result") or {}
    audios = audio_data.get("audios") or tr.get("audios") or []
    audio_url = (
        audio_data.get("audio_url")
        or tr.get("audio_url")
        or (audios[0].get("url") if audios and isinstance(audios[0], dict) else (audios[0] if audios else None))
    )
    if not audio_url:
        return _edge_fallback_with_report("Podcast audio 响应无 URL")

    voice_path = str(OUTPUT_DIR / "master_voice.mp3")
    urllib.request.urlretrieve(audio_url, voice_path)
    size_kb = os.path.getsize(voice_path) // 1024
    total_dur = ffprobe_duration(voice_path)
    tg(f"✅ 主音轨生成完毕，时长 {total_dur:.2f}s，{size_kb} KB")

    return voice_path


def _tts_turn_to_audio(turn: dict, idx: int, max_retries: int = 3) -> tuple[str, float, dict]:
    """Generate one ADSD dialogue turn via WeryAI text-to-audio."""
    voice_id = int(turn.get("speaker_id") or ADSD_VOICES["旁白"]["voice_id"])
    speaker = turn.get("speaker", "speaker")
    original_text = turn["text"]
    text = _sanitize_for_external_api(original_text)[:500]
    if text != original_text:
        turn["text"] = text
        turn["tts_policy_rewritten"] = True
        _record_adsd_tts_rewrite(idx, speaker, original_text, text, RuntimeError("initial external-api sanitization"))
    last_err = None
    rewrite_count = 0
    for attempt in range(max_retries):
        try:
            payload = {
                "text": text,
                "voice_id": voice_id,
                "speed": os.environ.get("ADR_ADSD_TTS_SPEED", "1.0"),
                "vol": os.environ.get("ADR_ADSD_TTS_VOL", "4.0"),
                "trace_id": f"adsd-{OUTPUT_DIR.name}-turn-{idx+1}",
            }
            r = req_post("/generation/text-to-audio", payload, timeout=30)
            task_id = r.get("data", {}).get("task_id") or (r.get("data", {}).get("task_ids") or [None])[0]
            if not task_id:
                raise RuntimeError(f"text-to-audio 无 task_id: {json.dumps(r, ensure_ascii=False)[:200]}")
            data = poll_task_status(task_id, f"ADSD TTS {idx+1}", max_wait=180)
            audios = data.get("audios") or []
            if not audios:
                raise RuntimeError(f"text-to-audio 成功但无 audios: {json.dumps(data, ensure_ascii=False)[:200]}")
            mp3_path = str(OUTPUT_DIR / f"turn_{idx+1:02d}_{speaker}.mp3")
            urllib.request.urlretrieve(audios[0], mp3_path)
            wav_path = str(OUTPUT_DIR / f"turn_{idx+1:02d}_{speaker}.wav")
            ffmpeg("-i", mp3_path, "-ar", "44100", "-ac", "1", "-c:a", "pcm_s16le", wav_path, timeout=60)
            dur = ffprobe_duration(wav_path)
            return wav_path, dur, {
                "task_id": task_id,
                "cost_credits": data.get("cost_credits"),
                "mp3_path": mp3_path,
                "tts_policy_rewritten": bool(turn.get("tts_policy_rewritten")),
            }
        except Exception as e:
            last_err = e
            if _is_content_policy_error(e) and rewrite_count < 2:
                before = turn.get("text", text)
                after = _rewrite_adsd_tts_text_for_policy(before, speaker, e)
                rewrite_count += 1
                turn["text"] = after
                turn["tts_policy_rewritten"] = True
                text = _sanitize_for_external_api(after)[:500]
                _record_adsd_tts_rewrite(idx, speaker, before, after, e)
                tg(f"⚠️ ADSD TTS {idx+1} 触发内容审查，已自动改写为中性历史表述后重试")
                log(f"ADSD TTS {idx+1} policy rewrite: {before} -> {after}")
                continue
            if attempt < max_retries - 1:
                wait_s = 2 * (attempt + 1)
                log(f"ADSD TTS {idx+1} 失败（第 {attempt+1}/{max_retries} 次）：{e}，{wait_s}s 后重试")
                time.sleep(wait_s)
                continue
            raise RuntimeError(f"ADSD TTS {idx+1} 重试失败：{last_err}")
    raise RuntimeError(f"ADSD TTS {idx+1} 重试失败：{last_err}")


def _asr_verify_dialogue_audio(audio_path: str, label: str = "ADSD ASR", result_name: str = "speech_recognize_result.json") -> dict | None:
    """Upload ADSD master audio through Telegram (作匿名文件托管) → 拿 URL → 调 weryai ASR 验证 TTS 文本一致性。
    上传走静默通知 (disable_notification=true)；ASR 完成后自动 deleteMessage 撤回中转 mp3，避免污染用户 TG。
    """
    if os.environ.get("ADR_ADSD_SKIP_ASR", "").strip().lower() in ("1", "true", "yes", "on"):
        return None
    _tg_message_id: int | None = None  # 中转 mp3 的 message_id，用于完成后撤回
    try:
        with open(audio_path, "rb") as f:
            r = requests.post(
                f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendAudio",
                data={
                    "chat_id": TG_CHAT_ID,
                    "caption": "·ADSD ASR 中转(自动删)·",
                    "disable_notification": "true",  # 静默上传不弹推送
                },
                files={"audio": (os.path.basename(audio_path), f, "audio/mpeg")},
                timeout=(30, 180),
            )
        r.raise_for_status()
        _result = r.json().get("result") or {}
        _tg_message_id = _result.get("message_id")
        file_id = (_result.get("audio") or {}).get("file_id")
        if not file_id:
            raise RuntimeError("Telegram sendAudio 无 file_id")
        fr = requests.get(
            f"https://api.telegram.org/bot{TG_BOT_TOKEN}/getFile",
            params={"file_id": file_id},
            timeout=30,
        )
        fr.raise_for_status()
        file_path = (fr.json().get("result") or {}).get("file_path")
        if not file_path:
            raise RuntimeError("Telegram getFile 无 file_path")
        audio_url = f"https://api.telegram.org/file/bot{TG_BOT_TOKEN}/{file_path}"
        r2 = req_post("/generation/speech-recognize", {"audio_url": audio_url, "language": "zh"}, timeout=30)
        task_id = r2.get("data", {}).get("task_id") or (r2.get("data", {}).get("task_ids") or [None])[0]
        if not task_id:
            raise RuntimeError(f"speech-recognize 无 task_id: {json.dumps(r2, ensure_ascii=False)[:200]}")
        data = poll_task_status(task_id, label, max_wait=240)
        (OUTPUT_DIR / result_name).write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return data
    except Exception as e:
        log(f"ADSD ASR 校验失败（不阻断）：{e}")
        tg(f"⚠️ ADSD ASR 校验失败，不阻断成片：{e}")
        return None
    finally:
        # ASR 完成（成功或失败）后撤回中转 mp3，避免污染用户 TG
        if _tg_message_id is not None:
            try:
                requests.post(
                    f"https://api.telegram.org/bot{TG_BOT_TOKEN}/deleteMessage",
                    data={"chat_id": TG_CHAT_ID, "message_id": _tg_message_id},
                    timeout=10,
                )
            except Exception:
                pass


def _asr_verify_dialogue_turns(script: list[dict]) -> dict | None:
    """Fallback ASR: recognize each TTS turn independently, then concatenate text."""
    parts = []
    records = []
    for i, turn in enumerate(script):
        audio_path = turn.get("dialogue_audio_mp3") or turn.get("dialogue_audio")
        if not audio_path or not os.path.exists(audio_path):
            records.append({"turn": i + 1, "speaker": turn.get("speaker"), "ok": False, "error": "audio_missing"})
            continue
        data = _asr_verify_dialogue_audio(
            audio_path,
            label=f"ADSD ASR turn {i+1}",
            result_name=f"speech_recognize_turn_{i+1:02d}.json",
        )
        text = (data or {}).get("speech_text", "")
        if text:
            parts.append(text)
        records.append({
            "turn": i + 1,
            "speaker": turn.get("speaker"),
            "ok": bool(text),
            "speech_text": text,
            "task_id": (data or {}).get("task_id"),
            "task_status": (data or {}).get("task_status"),
        })
    if not parts:
        return None
    payload = {
        "task_id": "per-turn-fallback",
        "task_status": "succeed" if all(r.get("ok") for r in records) else "partial",
        "speech_text": "".join(parts),
        "fallback": "per_turn_asr",
        "records": records,
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }
    (OUTPUT_DIR / "speech_recognize_result.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return payload


def _normalize_cn_number_token(token: str) -> str:
    digits = {"零": 0, "〇": 0, "一": 1, "二": 2, "两": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}
    if not token:
        return token
    if "百" in token:
        left, _, right = token.partition("百")
        hundreds = digits.get(left, 1 if not left else None)
        if hundreds is None:
            return token
        return str(hundreds * 100 + int(_normalize_cn_number_token(right) or "0"))
    if "十" in token:
        left, _, right = token.partition("十")
        tens = digits.get(left, 1 if not left else None)
        ones = digits.get(right, 0 if not right else None)
        if tens is None or ones is None:
            return token
        return str(tens * 10 + ones)
    if all(ch in digits for ch in token):
        return "".join(str(digits[ch]) for ch in token)
    return token


def _compact_zh_text(text: str) -> str:
    compact = re.sub(r"[\s，。！？、；：,.!?;:'\"“”‘’（）()《》【】\[\]\-—…·]", "", text or "")
    compact = compact.replace("儿", "")
    compact = compact.replace("真得", "真的")
    return re.sub(r"[零〇一二两三四五六七八九十百]+", lambda m: _normalize_cn_number_token(m.group(0)), compact)


def _write_adsd_asr_text_qa(script: list[dict], asr_data: dict) -> dict | None:
    """Compare subtitle/script text against ASR text to catch silent TTS rewrites."""
    try:
        import difflib
        expected = _compact_zh_text("".join(s.get("text", "") for s in script))
        recognized = _compact_zh_text(asr_data.get("speech_text", ""))
        ratio = difflib.SequenceMatcher(None, expected, recognized).ratio() if expected and recognized else 0.0
        missing_chunks = []
        for i, turn in enumerate(script):
            line = _compact_zh_text(turn.get("text", ""))
            if len(line) < 6:
                continue
            starts = list(range(0, max(len(line) - 5, 1), 6))
            for start in starts:
                chunk = line[start:start + 6]
                if len(chunk) >= 6 and chunk not in recognized:
                    missing_chunks.append({"turn": i + 1, "speaker": turn.get("speaker"), "chunk": chunk})
                    break
        strict_pass = ratio >= 0.92 and not missing_chunks
        # tolerant 放宽到 95%+ / missing ≤ 5，吸收英文专有名词被 ASR 听岔的误差
        tolerant_pass = ratio >= 0.95 and len(missing_chunks) <= 5
        qa = {
            "expected_chars": len(expected),
            "recognized_chars": len(recognized),
            "similarity": round(ratio, 4),
            "missing_chunks": missing_chunks[:20],
            "missing_count": len(missing_chunks),
            "strict_pass": strict_pass,
            "pass": strict_pass or tolerant_pass,
            "severity": "ok" if strict_pass else "warn" if tolerant_pass else "fail",
            "created_at": datetime.now().isoformat(timespec="seconds"),
        }
        (OUTPUT_DIR / "asr_qa.json").write_text(json.dumps(qa, ensure_ascii=False, indent=2), encoding="utf-8")
        return qa
    except Exception as e:
        log(f"ADSD ASR 文本 QA 写入失败: {e}")
        return None


def _write_adsd_speaker_focus_qa(script: list[dict], motion_results: dict[int, bool] | None = None) -> dict | None:
    """Record ADSD speaker-to-shot contract; this is the gate before real lip-sync."""
    if not ADS_DIALOGUE_MODE:
        return None
    try:
        scenes = []
        for i, scene in enumerate(script):
            prompt = scene.get("prompt", "")
            speaker = scene.get("speaker", "")
            contract = scene.get("speaker_visual_contract", "")
            # B-roll motion 路径不需要 active speaker / lip-sync prompt 锁定
            # 包含：旁白 voice-over 和 action 场面 panel override
            is_b_roll = not bool(scene.get("needs_lip_sync", True))
            scenes.append({
                "turn": i + 1,
                "speaker": speaker,
                "dialogue_shape": scene.get("dialogue_shape"),
                "speaker_count": scene.get("speaker_count"),
                "audio_start": scene.get("audio_start"),
                "audio_end": scene.get("audio_end"),
                "duration": scene.get("dur"),
                "is_b_roll": is_b_roll,
                "speaker_contract_exists": bool(contract),
                "prompt_has_active_speaker": "Active speaker is" in prompt,
                "prompt_names_speaker_role": bool(speaker) and (speaker in prompt or "historical onsite character" in prompt),
                "onsite_pov_prompt": (not ADSD_ONSITE_POV_MODE) or ("Onsite observer POV" in prompt),
                "motion_succeeded": motion_results.get(i) if motion_results is not None else None,
            })
        failed = [
            s for s in scenes
            if not s["speaker"]
            or not s["speaker_contract_exists"]
            or s["audio_start"] is None
            or s["audio_end"] is None
            # A-roll lip-sync 才要求 active speaker / onsite POV；B-roll 不检查
            or (not s["is_b_roll"] and not s["prompt_has_active_speaker"])
            or (not s["is_b_roll"] and not s["onsite_pov_prompt"])
        ]
        payload = {
            "mode": ADSD_MODE_NAME,
            "dialogue_shape": script[0].get("dialogue_shape") if script else None,
            "speakers": list(dict.fromkeys(scene.get("speaker", "") for scene in script if scene.get("speaker"))),
            "policy": "lip_sync_prompt_experiment" if ADSD_LIP_SYNC_EXPERIMENT else "speaker_focus_required",
            "real_lip_sync": False,
            "onsite_pov_mode": ADSD_ONSITE_POV_MODE,
            "note": "Current WERYDANCE path is text-to-video; it can enforce active speaker framing, but cannot guarantee audio-driven viseme alignment.",
            "total": len(script),
            "failed_count": len(failed),
            "pass": len(failed) == 0,
            "motion_success_count": sum(1 for v in motion_results.values() if v) if motion_results is not None else None,
            "scenes": scenes,
            "created_at": datetime.now().isoformat(timespec="seconds"),
        }
        (OUTPUT_DIR / "speaker_focus_qa.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return payload
    except Exception as e:
        log(f"ADSD speaker_focus_qa 写入失败: {e}")
        return None


def _write_adsd_gender_voice_qa(script: list[dict]) -> dict | None:
    """Gate ADSD visual gender against the assigned TTS voice gender."""
    if not ADS_DIALOGUE_MODE:
        return None
    try:
        scenes = []
        failures = []
        for i, scene in enumerate(script):
            voice = {"voice_id": scene.get("speaker_id")}
            voice_gender = str(scene.get("voice_gender") or "").strip().lower()
            if voice_gender not in ("male", "female"):
                voice_gender = _adsd_gender_from_voice(voice) or _adsd_infer_gender_from_speaker(scene.get("speaker", ""))
            voice_id_gender = _adsd_gender_from_voice(voice)
            prompt = str(scene.get("prompt") or "")
            visual_subject = str(scene.get("visual_subject") or "")
            conflict = _adsd_visual_subject_has_gender_conflict(visual_subject, voice_gender)
            prompt_lock = "VOICE-VISUAL GENDER LOCK" in prompt
            voice_match = bool(voice_gender) and (not voice_id_gender or voice_gender == voice_id_gender)
            rec = {
                "turn": i + 1,
                "speaker": scene.get("speaker"),
                "voice_gender": voice_gender,
                "voice_id": scene.get("speaker_id"),
                "voice_name": scene.get("speaker_name"),
                "voice_id_gender": voice_id_gender,
                "visual_subject": visual_subject,
                "prompt_has_voice_visual_gender_lock": prompt_lock,
                "visual_subject_gender_conflict": conflict,
                "pass": voice_match and prompt_lock and not conflict,
            }
            scenes.append(rec)
            if not rec["pass"]:
                failures.append(rec)
        payload = {
            "mode": ADSD_MODE_NAME,
            "policy": "voice_gender_must_match_visible_speaker_gender",
            "total": len(script),
            "failed_count": len(failures),
            "pass": len(failures) == 0,
            "scenes": scenes,
            "created_at": datetime.now().isoformat(timespec="seconds"),
        }
        (OUTPUT_DIR / "gender_voice_qa.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        if payload["pass"]:
            tg(f"✅ 声画性别 QA：{len(script)} 个 turn 均有 voice-visual gender lock")
        else:
            tg(f"⚠️ 声画性别 QA：{len(failures)} 个 turn 失败，已记录 gender_voice_qa.json")
        return payload
    except Exception as e:
        log(f"ADSD gender_voice_qa 写入失败: {e}")
        return None


def step2_dialogue_voice(script: list[dict]) -> str:
    """ADSD voice core: one TTS per dialogue turn, deterministic timeline.

    HADSD 默认走"直接 concat 紧凑节奏"：忽略 override timecode 的 silence pad，
    每 turn 接 0.22s 自然停顿。这样视频总长 = sum(TTS turn dur)，不会出现 6-9s 冻帧/cutaway 等待。
    timecode 字段仍保留 (override_audio_start/end) 供字幕参考，但不撑总长。

    若需保留旧 timecode-pad 行为：set ADR_HADSD_RESPECT_TIMECODE_LENGTH=1
    """
    # HADSD 紧凑模式默认 0：消除 turn 间 silence pad 产生的可见冻帧
    # 需要每段间自然呼吸感时显式 set ADR_ADSD_TURN_PAUSE=0.22
    pause = float(os.environ.get("ADR_ADSD_TURN_PAUSE", "0.0"))
    respect_timecode = os.environ.get("ADR_HADSD_RESPECT_TIMECODE_LENGTH", "0").strip().lower() in ("1", "true", "yes", "on")
    has_override_timing = respect_timecode and any(s.get("override_audio_start") is not None for s in script)
    if has_override_timing:
        tg(f"🎭 {ADSD_MODE_NAME} TTS 按 ADR_HADSD_RESPECT_TIMECODE_LENGTH=1 → 按 timecode silence pad 撑总长")
    elif any(s.get("override_audio_start") is not None for s in script):
        tg(f"🎭 {ADSD_MODE_NAME} TTS 检测到 override timecode，但 HADSD 默认走紧凑直接 concat（不撑总长）；如需旧行为 set ADR_HADSD_RESPECT_TIMECODE_LENGTH=1")
    tg(f"🎭 {ADSD_MODE_NAME} TTS 启动：text-to-audio × {len(script)} turn，逐句生成确定性时间轴...")
    timeline = []
    wav_files: list[str] = []
    cursor = 0.0
    # 若首段 override_audio_start > 0，开头加 silence pad
    if has_override_timing:
        first_target = float(script[0].get("override_audio_start") or 0.0)
        if first_target > 0.05:
            head_sil = str(OUTPUT_DIR / "silence_head_override.wav")
            ffmpeg("-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono",
                   "-t", f"{first_target:.3f}", "-c:a", "pcm_s16le", head_sil, timeout=30)
            wav_files.append(head_sil)
            cursor += first_target
    timing_qa: list[dict] = []
    for i, turn in enumerate(script):
        if _is_silent_b(turn):
            # silent_b 跳过 TTS API，直接生成 duration_hint 长度静音 wav 段
            sb_dur = float(turn.get("duration_hint", 0.0) or 0.0)
            if sb_dur < 1.0:
                sb_dur = 4.0
            sb_dur = min(max(sb_dur, 2.0), 8.0)  # silent_b 限 2-8s
            wav_path = str(OUTPUT_DIR / f"silent_b_{i:02d}.wav")
            ffmpeg("-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono",
                   "-t", f"{sb_dur:.3f}", "-c:a", "pcm_s16le", wav_path, timeout=30)
            dur = sb_dur
            meta = {"task_id": None, "cost_credits": 0, "mp3_path": None, "silent_b": True}
        else:
            wav_path, dur, meta = _tts_turn_to_audio(turn, i)
        # override timing 模式下：本 turn 录到 dialogue_audio 之后，下一段 silence 的长度由 timecode 决定
        target_start = turn.get("override_audio_start")
        target_end = turn.get("override_audio_end")
        target_dur = (float(target_end) - float(target_start)) if (target_start is not None and target_end is not None) else None
        turn.update({
            "dialogue_mode": True,
            "dialogue_audio": wav_path,
            "dialogue_audio_mp3": meta.get("mp3_path"),
            "dialogue_tts_task_id": meta.get("task_id"),
            "dialogue_tts_cost_credits": meta.get("cost_credits"),
            "audio_start": cursor,
            "audio_end": cursor + dur,
            "sub_start": cursor + SUB_DELAY,
            "sub_end": cursor + dur + SUB_DELAY,
            "dur": dur,
            "vid_duration": max(1.0, dur + (AUDIO_DELAY if i == len(script) - 1 else pause)),
            "img_path": str(OUTPUT_DIR / f"img_{i}.jpg"),
            "vid_path": str(OUTPUT_DIR / f"seg_{i}.mp4"),
        })
        timeline.append({
            "turn": i + 1,
            "speaker": turn.get("speaker"),
            "voice_gender": turn.get("voice_gender") or turn.get("gender"),
            "visual_subject": turn.get("visual_subject"),
            "dialogue_shape": turn.get("dialogue_shape"),
            "speaker_count": turn.get("speaker_count"),
            "voice_id": turn.get("speaker_id"),
            "voice_name": turn.get("speaker_name"),
            "text": turn.get("text"),
            "shot": turn.get("shot"),
            "audio": wav_path,
            "start": round(cursor, 3),
            "end": round(cursor + dur, 3),
            "duration": round(dur, 3),
            "tts_task_id": meta.get("task_id"),
            "tts_cost_credits": meta.get("cost_credits"),
        })
        wav_files.append(wav_path)
        # 计算本 turn 之后的 silence 长度
        if i < len(script) - 1:
            if has_override_timing:
                next_target = script[i + 1].get("override_audio_start")
                if next_target is not None:
                    gap = max(pause, float(next_target) - (cursor + dur))
                else:
                    gap = pause
            else:
                gap = pause
            silence = str(OUTPUT_DIR / f"silence_{i+1:02d}.wav")
            ffmpeg(
                "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono",
                "-t", f"{gap:.3f}",
                "-c:a", "pcm_s16le",
                silence,
                timeout=30,
            )
            wav_files.append(silence)
            cursor += dur + gap
        else:
            # 最后一 turn：若有 timecode，补齐到 override_audio_end
            if has_override_timing and target_end is not None:
                tail_gap = max(0.0, float(target_end) - (cursor + dur))
                if tail_gap > 0.05:
                    tail_sil = str(OUTPUT_DIR / "silence_tail_override.wav")
                    ffmpeg("-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono",
                           "-t", f"{tail_gap:.3f}", "-c:a", "pcm_s16le", tail_sil, timeout=30)
                    wav_files.append(tail_sil)
                    cursor += dur + tail_gap
                else:
                    cursor += dur
            else:
                cursor += dur
        if has_override_timing:
            timing_qa.append({
                "turn": i + 1,
                "speaker": turn.get("speaker"),
                "target_start": target_start,
                "target_end": target_end,
                "target_dur": round(target_dur, 3) if target_dur is not None else None,
                "tts_dur": round(dur, 3),
                "actual_start": round(turn["audio_start"], 3),
                "actual_end": round(turn["audio_end"], 3),
                "tts_exceeds_target": (target_dur is not None and dur > target_dur + 0.5),
            })
        log(f"ADSD turn {i+1}: {turn.get('speaker')} {dur:.3f}s [{turn['audio_start']:.3f}-{turn['audio_end']:.3f}]")
    timeline_path = OUTPUT_DIR / "turn_timeline.json"
    timeline_path.write_text(json.dumps(timeline, ensure_ascii=False, indent=2), encoding="utf-8")
    if has_override_timing:
        try:
            qa = {
                "mode": "adsd_per_turn_silence_pad_to_override_timecode",
                "policy": "respect_override_timecodes_via_inter_turn_silence",
                "total_turns": len(script),
                "tts_overruns_count": sum(1 for r in timing_qa if r.get("tts_exceeds_target")),
                "final_master_audio_duration": round(cursor, 3),
                "override_total_target_duration": round(float(script[-1].get("override_audio_end") or cursor), 3),
                "duration_delta_vs_target": round(cursor - float(script[-1].get("override_audio_end") or cursor), 3),
                "per_turn": timing_qa,
                "manual_visual_checks_required": [
                    "each_turn_audio_aligns_with_timecode",
                    "silence_gaps_dont_feel_artificial",
                    "lip_sync_video_extends_to_match_audio_length",
                ],
                "created_at": datetime.now().isoformat(timespec="seconds"),
            }
            (OUTPUT_DIR / "adsd_timed_master_qa.json").write_text(
                json.dumps(qa, ensure_ascii=False, indent=2), encoding="utf-8")
            overruns = qa["tts_overruns_count"]
            tg(f"🎭 ADSD timed master 完成：{qa['total_turns']} turn → {qa['final_master_audio_duration']}s "
               f"(target {qa['override_total_target_duration']}s)"
               + (f"\n⚠️ {overruns} turn TTS 超出 timecode" if overruns else ""))
        except Exception as e:
            log(f"adsd_timed_master_qa.json 写入失败: {e}")
    concat_txt = OUTPUT_DIR / "dialogue_wav_concat.txt"
    with open(concat_txt, "w", encoding="utf-8") as f:
        for p in wav_files:
            f.write(f"file '{p}'\n")
    wav_master = str(OUTPUT_DIR / "dialogue_master.wav")
    ffmpeg("-f", "concat", "-safe", "0", "-i", str(concat_txt), "-c", "copy", wav_master, timeout=120)
    voice_path = str(OUTPUT_DIR / "dialogue_master.mp3")
    ffmpeg("-i", wav_master, "-c:a", "libmp3lame", "-b:a", "128k", voice_path, timeout=120)
    total_dur = ffprobe_duration(voice_path)
    asr_data = _asr_verify_dialogue_audio(voice_path)
    if asr_data and asr_data.get("speech_text"):
        asr_qa = _write_adsd_asr_text_qa(script, asr_data)
        if asr_qa and not asr_qa.get("pass"):
            expected_chars = int(asr_qa.get("expected_chars") or 0)
            recognized_chars = int(asr_qa.get("recognized_chars") or 0)
            if expected_chars and recognized_chars < expected_chars * 0.65:
                tg(
                    f"⚠️ ADSD 主音轨 ASR 过短：{recognized_chars}/{expected_chars} 字，"
                    "启动逐 turn ASR 兜底..."
                )
                turn_asr = _asr_verify_dialogue_turns(script)
                if turn_asr and turn_asr.get("speech_text"):
                    asr_qa = _write_adsd_asr_text_qa(script, turn_asr)
            if asr_qa and not asr_qa.get("pass"):
                samples = [m.get("chunk") for m in asr_qa.get("missing_chunks", [])[:5]]
                tg(
                    f"⚠️ ADSD ASR 文本一致性需复查：similarity={asr_qa.get('similarity')}, "
                    f"missing={asr_qa.get('missing_count')}，样例：{', '.join(samples)}"
                )
            else:
                tg(f"✅ ADSD ASR 文本一致性通过 similarity={asr_qa.get('similarity') if asr_qa else 'n/a'}")
        else:
            tg(f"✅ ADSD ASR 文本一致性通过 similarity={asr_qa.get('similarity') if asr_qa else 'n/a'}")
    tg(f"✅ {ADSD_MODE_NAME} 主音轨完成：{total_dur:.2f}s，时间轴 {timeline_path}")
    return voice_path


# ── 第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）────────
# 默认严格音画同步；如需电影感 J-Cut，可通过环境变量手动开启：
#   ADR_AUDIO_DELAY=0.5 ADR_SUB_DELAY=0.2 python3 run_adr_v8.py "主题"
AUDIO_DELAY = float(os.environ.get("ADR_AUDIO_DELAY", "0.0"))  # 配音延迟秒数（-itsoffset 控制）
SUB_DELAY   = float(os.environ.get("ADR_SUB_DELAY", "0.0"))    # 字幕延迟秒数


# ── silencedetect 校准工具 ──────────────────────────────────────────────
def _detect_silences(audio_path: str, noise_db: int = -35, min_duration: float = 0.15) -> list[float]:
    """用 ffmpeg silencedetect 提取所有静音区间的中点作为候选分句锚点。"""
    cmd = [
        "ffmpeg", "-i", audio_path,
        "-af", f"silencedetect=noise={noise_db}dB:d={min_duration}",
        "-f", "null", "-"
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        stderr = result.stderr
    except Exception as e:
        log(f"silencedetect 执行失败: {e}")
        return []

    silence_midpoints: list[float] = []
    starts: list[float] = []
    for line in stderr.splitlines():
        if "silence_start" in line:
            try:
                t = float(line.split("silence_start:")[1].strip().split()[0])
                starts.append(t)
            except (ValueError, IndexError):
                continue
        elif "silence_end" in line and starts:
            try:
                parts = line.split("silence_end:")[1].strip().split()
                t_end = float(parts[0])
                mid = (starts[-1] + t_end) / 2.0
                silence_midpoints.append(mid)
            except (ValueError, IndexError):
                continue
    log(f"silencedetect 检测到 {len(silence_midpoints)} 个静音中点")
    return silence_midpoints


def _calibrate_boundaries(boundaries: list[float], silence_midpoints: list[float],
                          snap_threshold: float = 0.8) -> list[float]:
    """
    用静音点校准字符插值边界。
    对每个边界，在静音点中找最近的：距离在 snap_threshold 内就吸附，否则保留原值。
    每个静音点只能被吸附一次，防止多个边界抢同一个点。
    """
    if not silence_midpoints:
        return boundaries

    calibrated: list[float] = []
    used: set[int] = set()

    for wb in boundaries:
        best_idx = None
        best_dist = float("inf")

        for i, sp in enumerate(silence_midpoints):
            if i in used:
                continue
            dist = abs(sp - wb)
            if dist < best_dist:
                best_dist = dist
                best_idx = i

        if best_idx is not None and best_dist <= snap_threshold:
            calibrated.append(silence_midpoints[best_idx])
            used.add(best_idx)
        else:
            calibrated.append(wb)

    return calibrated


def _enforce_monotonic(boundaries: list[float], min_gap: float = 0.3) -> list[float]:
    """强制边界单调递增，相邻边界至少间隔 min_gap 秒。"""
    result: list[float] = []
    prev = 0.0
    for b in boundaries:
        if b <= prev + min_gap:
            b = prev + min_gap
        result.append(b)
        prev = b
    return result


def _manual_override_segments(script: list[dict]) -> list[dict] | None:
    if not script or not all(s.get("override_duration") for s in script):
        return None
    result: list[dict] = []
    cursor = 0.0
    for s in script:
        has_start_end = s.get("override_audio_start") is not None and s.get("override_audio_end") is not None
        if has_start_end:
            start = max(0.0, float(s.get("override_audio_start") or 0.0))
            end = max(start + 0.1, float(s.get("override_audio_end") or 0.0))
            dur = end - start
            cursor = end
        else:
            start = cursor
            dur = max(0.1, float(s.get("override_duration") or 0.1))
            end = start + dur
            cursor = end
        result.append({"start": start, "end": end, "dur": dur})
    return result


def _calc_sentence_boundaries(voice_path: str, script: list[dict]) -> list[dict]:
    """
    三源融合方案：Whisper 语速曲线 + 字符数插值 + silencedetect 物理校准。

    第一层：Whisper segment 建立粗粒度"累积字数 → 时间"映射表
    第二层：用台词字符数在映射表上线性插值，精细化到每句边界
    第三层：silencedetect 提取音频中的物理静音点，对插值边界做吸附校准

    回退：Whisper 不可用时退化为纯字数比例（不做 silencedetect 校准）。
    """
    n = len(script)
    manual = _manual_override_segments(script)
    if manual and len(manual) == n:
        log(f"使用外部时间戳分配时间轴：{n} 段")
        return manual

    total_dur = ffprobe_duration(voice_path)
    sentence_chars = [len(s["text"]) for s in script]
    total_script_chars = sum(sentence_chars)

    # ── 第一层：Whisper 构建语速曲线 ──
    char_time_map = None  # [(cumulative_chars, time), ...]
    try:
        from faster_whisper import WhisperModel
        model = WhisperModel("base", compute_type="int8")
        w_segs = list(model.transcribe(voice_path, language="zh")[0])
        log(f"Whisper 识别出 {len(w_segs)} 段")

        if w_segs:
            # 构建"累积字数 → 时间"映射表
            char_time_map = [(0, 0.0)]
            cum_chars = 0
            for seg in w_segs:
                seg_chars = len(seg.text.strip())
                if seg_chars > 0:
                    cum_chars += seg_chars
                    char_time_map.append((cum_chars, seg.end))
            # 末尾兜底
            if char_time_map[-1][1] < total_dur:
                char_time_map.append((cum_chars, total_dur))
            log(f"语速曲线：{len(char_time_map)} 个采样点，Whisper 总字数 {cum_chars}，台词总字数 {total_script_chars}")
    except Exception as e:
        log(f"Whisper 失败，回退纯字数比例: {e}")

    if not char_time_map or len(char_time_map) < 2:
        # 回退：纯字数比例（不做 silencedetect 校准，因为没有可靠的初始估算）
        log("使用纯字数比例分配")
        cursor = 0.0
        result = []
        for s in script:
            dur = total_dur * (len(s["text"]) / total_script_chars)
            result.append({"start": cursor, "end": cursor + dur, "dur": dur})
            cursor += dur
        return result

    # ── 第二层：字符数插值 ──
    whisper_total_chars = char_time_map[-1][0]

    def _interpolate_time(target_chars: float) -> float:
        # 将台词字数缩放到 Whisper 字数空间
        scaled = target_chars * (whisper_total_chars / total_script_chars) if total_script_chars > 0 else 0
        # 在映射表中二分查找 + 线性插值
        for j in range(1, len(char_time_map)):
            c0, t0 = char_time_map[j - 1]
            c1, t1 = char_time_map[j]
            if scaled <= c1:
                if c1 == c0:
                    return t0
                ratio = (scaled - c0) / (c1 - c0)
                return t0 + ratio * (t1 - t0)
        return total_dur

    # 字符插值得到每句的结束时间
    boundaries_end: list[float] = []
    cum = 0
    for i, sc in enumerate(sentence_chars):
        cum += sc
        end_time = _interpolate_time(cum)
        boundaries_end.append(end_time)

    # ── 第三层：silencedetect 物理校准 ──
    silence_midpoints = _detect_silences(voice_path)

    if silence_midpoints:
        # 只对中间边界做校准（最后一句的结束时间固定为 total_dur）
        inner_boundaries = boundaries_end[:-1]
        inner_calibrated = _calibrate_boundaries(inner_boundaries, silence_midpoints)
        inner_calibrated = _enforce_monotonic(inner_calibrated)

        # 打印校准对比日志
        for i, (wb, cb) in enumerate(zip(inner_boundaries, inner_calibrated)):
            delta = cb - wb
            if abs(delta) > 0.01:
                log(f"句{i+1}尾: 字符插值={wb:.2f}s → 校准={cb:.2f}s (Δ{delta:+.2f}s)")

        boundaries_end = inner_calibrated + [total_dur]
    else:
        log("无静音点可用，保留纯字符插值结果")
        boundaries_end[-1] = total_dur

    # 由 end 时间点反推 start/end/dur
    result: list[dict] = []
    for i in range(n):
        start_time = 0.0 if i == 0 else boundaries_end[i - 1]
        end_time = boundaries_end[i]
        dur = max(end_time - start_time, 0.5)
        result.append({"start": start_time, "end": end_time, "dur": dur})

    return result


def step345_timeline(script: list[dict], voice_path: str) -> list[dict]:
    total_dur = ffprobe_duration(voice_path)
    tg(f"✅ 主音轨时长探测完成：{total_dur:.3f} 秒")

    if ADS_DIALOGUE_MODE and script and script[0].get("dialogue_mode") and "audio_start" in script[0]:
        lines = []
        for i, s in enumerate(script):
            s.setdefault("img_path", str(OUTPUT_DIR / f"img_{i}.jpg"))
            s.setdefault("vid_path", str(OUTPUT_DIR / f"seg_{i}.mp4"))
            s.setdefault("sub_start", s["audio_start"] + SUB_DELAY)
            s.setdefault("sub_end", s.get("audio_end", s["audio_start"] + s.get("dur", 1.0)) + SUB_DELAY)
            s.setdefault("vid_duration", max(1.0, s.get("dur", 1.0)))
            lines.append(
                f"Turn {i+1} {s.get('speaker','')}（{s.get('dur', 0):.2f}s）→ "
                f"画面 {s['audio_start']:.2f}s / 字幕 {s['sub_start']:.2f}s"
            )
        speaker_qa = _write_adsd_speaker_focus_qa(script)
        if speaker_qa and speaker_qa.get("pass"):
            tg(f"✅ {ADSD_MODE_NAME} 说话人镜头同步 QA 通过：{speaker_qa.get('total')} turn")
        elif speaker_qa:
            tg(f"⚠️ {ADSD_MODE_NAME} 说话人镜头同步 QA 未通过：failed={speaker_qa.get('failed_count')}")
        shape = script[0].get("dialogue_shape") if script else ""
        speakers = " / ".join(dict.fromkeys(s.get("speaker", "") for s in script if s.get("speaker")))
        shape_note = f"结构：{shape}；角色：{speakers}\n" if shape or speakers else ""
        tg(f"✅ {ADSD_MODE_NAME} 时间轴采用逐句 TTS 真实时长\n{shape_note}" + "\n".join(lines))
        return script

    segs = _calc_sentence_boundaries(voice_path, script)
    tg(f"✅ 时间轴分配完成（Whisper 语速曲线 + 字符分界），{len(segs)} 段")

    timeline_lines = []
    for i, s in enumerate(script):
        duration = segs[i]["dur"]
        cursor = segs[i]["start"]

        vid_duration = duration + (AUDIO_DELAY if i == len(script) - 1 else 0)
        vid_duration = max(vid_duration, 1.0)

        # 字幕比画面晚 SUB_DELAY，比配音早 (AUDIO_DELAY - SUB_DELAY)
        # 画面 t=0 → 字幕 t=0.2 → 配音 t=0.5
        sub_start = cursor + SUB_DELAY
        sub_end   = cursor + duration + SUB_DELAY

        s.update({
            "audio_start":  cursor,
            "sub_start":    sub_start,
            "sub_end":      sub_end,
            "vid_duration": vid_duration,
            "img_path":     str(OUTPUT_DIR / f"img_{i}.jpg"),
            "vid_path":     str(OUTPUT_DIR / f"seg_{i}.mp4"),
        })
        timeline_lines.append(
            f"句 {i+1}（{duration:.2f}s）→ 画面 {cursor:.2f}s / 配音+字幕 {sub_start:.2f}s"
        )

    tg("✅ 时间轴分配完成\n画面 → +{:.1f}s 字幕 → +{:.1f}s 配音\n\n".format(SUB_DELAY, AUDIO_DELAY) + "\n".join(timeline_lines))
    return script


def _analyze_bgm_energy_cuts(bgm_path: str, target_total: float) -> dict:
    """Analyze local BGM energy and return candidate cut points for BGM-only editing."""
    window = float(os.environ.get("ADR_BGM_ONLY_ENERGY_WINDOW", "0.5"))
    min_gap = float(os.environ.get("ADR_BGM_ONLY_ENERGY_MIN_GAP", "1.2"))
    samples: list[dict] = []
    candidates: list[dict] = []
    try:
        result = subprocess.run([
            "ffmpeg", "-hide_banner", "-nostats", "-i", bgm_path,
            "-af", (
                f"aresample=16000,asetnsamples=n={max(1, int(16000 * window))},"
                "astats=metadata=1:reset=1,"
                "ametadata=print:key=lavfi.astats.Overall.RMS_level"
            ),
            "-f", "null", "-"
        ], capture_output=True, text=True, timeout=90)
        current_t = None
        for line in result.stderr.splitlines():
            m_t = re.search(r"pts_time:([0-9.]+)", line)
            if m_t:
                current_t = float(m_t.group(1))
                continue
            m_rms = re.search(r"lavfi\.astats\.Overall\.RMS_level=(-?(?:inf|\d+(?:\.\d+)?))", line)
            if m_rms and current_t is not None and m_rms.group(1) != "-inf":
                if 0.5 <= current_t <= target_total - 0.5:
                    samples.append({"t": round(current_t, 3), "rms_db": round(float(m_rms.group(1)), 3)})
        if len(samples) >= 4:
            diffs = []
            for i in range(1, len(samples)):
                diff = samples[i]["rms_db"] - samples[i - 1]["rms_db"]
                diffs.append((samples[i]["t"], diff, samples[i]["rms_db"]))
            sorted_diffs = sorted(diffs, key=lambda x: abs(x[1]), reverse=True)
            chosen: list[tuple[float, float, float]] = []
            for t, diff, rms in sorted_diffs:
                if all(abs(t - prev[0]) >= min_gap for prev in chosen):
                    chosen.append((t, diff, rms))
                if len(chosen) >= 80:
                    break
            candidates = [
                {"t": round(t, 3), "delta_db": round(diff, 3), "rms_db": round(rms, 3)}
                for t, diff, rms in sorted(chosen, key=lambda x: x[0])
            ]
    except Exception as e:
        log(f"BGM energy 分析失败，保留时长驱动切点: {e}")
    payload = {
        "policy": "ffmpeg_astats_rms_delta",
        "window": window,
        "min_gap": min_gap,
        "sample_count": len(samples),
        "candidate_count": len(candidates),
        "samples_preview": samples[:20],
        "candidates": candidates,
    }
    try:
        (OUTPUT_DIR / "bgm_energy_cuts.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except Exception as e:
        log(f"bgm_energy_cuts.json 写入失败: {e}")
    return payload


def _snap_bgm_only_boundaries(
    boundaries: list[float],
    durations: list[float],
    chars: list[int],
    energy_cuts: list[dict],
    scene_total: float,
    min_shot: float,
    cps: float,
) -> tuple[list[float], list[dict]]:
    """Snap inner scene boundaries to nearby BGM energy changes without hurting readability."""
    if len(boundaries) <= 2 or not energy_cuts:
        return boundaries, []
    snap_window = float(os.environ.get("ADR_BGM_ONLY_SNAP_WINDOW", "0.65"))
    max_cps = cps * float(os.environ.get("ADR_BGM_ONLY_CPS_TOLERANCE", "1.2"))
    min_delta_db = float(os.environ.get("ADR_BGM_ONLY_MIN_DELTA_DB", "1.5"))
    used: set[float] = set()
    snapped = boundaries[:]
    records: list[dict] = []

    def _valid_interval(boundary_idx: int, candidate: float) -> bool:
        left_scene_idx = boundary_idx - 1
        right_scene_idx = boundary_idx
        prev_b = snapped[boundary_idx - 1] if boundary_idx - 1 >= 0 else 0.0
        next_b = snapped[boundary_idx + 1] if boundary_idx + 1 < len(snapped) else scene_total
        left_dur = candidate - prev_b
        right_dur = next_b - candidate
        if left_dur < min_shot * 0.9 or right_dur < min_shot * 0.9:
            return False
        if chars[left_scene_idx] / max(left_dur, 0.1) > max_cps:
            return False
        if chars[right_scene_idx] / max(right_dur, 0.1) > max_cps:
            return False
        return True

    for idx in range(1, len(boundaries) - 1):
        original = snapped[idx]
        ranked = sorted(
            (
                cut for cut in energy_cuts
                if cut.get("t") not in used and abs(float(cut.get("t", 0)) - original) <= snap_window
                and abs(float(cut.get("delta_db", 0))) >= min_delta_db
            ),
            key=lambda c: (-abs(float(c.get("delta_db", 0))), abs(float(c.get("t", 0)) - original)),
        )
        for cut in ranked:
            candidate = float(cut.get("t"))
            if _valid_interval(idx, candidate):
                snapped[idx] = candidate
                used.add(cut.get("t"))
                records.append({
                    "boundary_after_scene": idx,
                    "from": round(original, 3),
                    "to": round(candidate, 3),
                    "delta": round(candidate - original, 3),
                    "energy_delta_db": cut.get("delta_db"),
                })
                break
    return snapped, records


def step345_bgm_only_timeline(script: list[dict], bgm_path: str, voice_path: str) -> list[dict]:
    """ADR/ADS BGM-only timeline: let BGM duration and energy changes drive shot lengths."""
    bgm_dur = ffprobe_duration(bgm_path)
    if bgm_dur <= 0:
        raise RuntimeError("BGM-only 时间轴失败：BGM 时长无效")
    n = max(1, len(script))
    manual = _manual_override_segments(script)
    if manual and len(manual) == len(script):
        timeline = []
        for i, (s, seg) in enumerate(zip(script, manual)):
            cursor = float(seg["start"])
            dur = max(1.0, float(seg["dur"]))
            sub_start = cursor + SUB_DELAY
            sub_end = cursor + dur + SUB_DELAY
            s.update({
                "audio_start": cursor,
                "sub_start": sub_start,
                "sub_end": sub_end,
                "dur": dur,
                "vid_duration": dur,
                "img_path": str(OUTPUT_DIR / f"img_{i}.jpg"),
                "vid_path": str(OUTPUT_DIR / f"seg_{i}.mp4"),
                "bgm_only": True,
            })
            timeline.append({
                "scene": i + 1,
                "text": s.get("text", ""),
                "start": round(cursor, 3),
                "end": round(cursor + dur, 3),
                "duration": round(dur, 3),
                "chars": len(str(s.get("text", ""))),
                "manual_timecode": s.get("override_time_label"),
            })
        (OUTPUT_DIR / "bgm_only_timeline.json").write_text(
            json.dumps({
                "policy": "manual_timecode_override",
                "bgm_path": bgm_path,
                "bgm_duration": bgm_dur,
                "target_total": round(max(seg["end"] for seg in manual), 3),
                "scene_total": round(max(seg["end"] for seg in manual), 3),
                "timeline": timeline,
                "created_at": datetime.now().isoformat(timespec="seconds"),
            }, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        tg(f"✅ BGM-only 时间轴采用外部时间戳：{len(script)} 镜，目标 {max(seg['end'] for seg in manual):.1f}s")
        return script

    cps = float(os.environ.get("ADR_BGM_ONLY_CPS", "2.4"))
    max_total = float(os.environ.get("ADR_BGM_ONLY_MAX_DURATION", "90"))
    min_shot_cfg = float(os.environ.get("ADR_BGM_ONLY_MIN_SHOT", "2.5"))
    max_shot = float(os.environ.get("ADR_BGM_ONLY_MAX_SHOT", "8.0"))
    outro = float(os.environ.get("ADR_BGM_ONLY_OUTRO", "0.8"))

    target_total = min(bgm_dur, max_total)
    scene_total = max(1.0, target_total - outro)
    min_shot = min_shot_cfg
    if scene_total < n * min_shot:
        min_shot = max(1.0, scene_total / n)
    max_shot = max(max_shot, min_shot, scene_total / n)

    chars = [max(1, len(str(s.get("text", "")))) for s in script]
    base = [max(min_shot, c / max(cps, 0.1)) for c in chars]

    if sum(base) > scene_total:
        floor_total = n * min_shot
        if scene_total <= floor_total:
            durations = [scene_total / n for _ in script]
        else:
            extra_budget = scene_total - floor_total
            extras = [max(0.0, b - min_shot) for b in base]
            extra_sum = sum(extras) or 1.0
            durations = [min_shot + extra_budget * e / extra_sum for e in extras]
    else:
        durations = base[:]
        remaining = scene_total - sum(durations)
        expandable = [max(0.0, max_shot - d) for d in durations]
        expandable_sum = sum(expandable)
        if remaining > 0 and expandable_sum > 0:
            durations = [d + remaining * e / expandable_sum for d, e in zip(durations, expandable)]
        elif remaining > 0 and durations:
            durations[-1] += remaining

    boundaries = [0.0]
    for dur in durations:
        boundaries.append(boundaries[-1] + float(dur))
    boundaries[-1] = scene_total
    energy_payload = _analyze_bgm_energy_cuts(bgm_path, target_total)
    energy_cuts = energy_payload.get("candidates") if isinstance(energy_payload, dict) else []
    snapped_boundaries, snap_records = _snap_bgm_only_boundaries(
        boundaries, durations, chars, energy_cuts or [], scene_total, min_shot, cps
    )
    durations = [
        max(1.0, snapped_boundaries[i + 1] - snapped_boundaries[i])
        for i in range(len(script))
    ]
    snap_rate = (len(snap_records) / max(1, len(script) - 1)) if len(script) > 1 else 0.0

    cursor = 0.0
    timeline = []
    for i, (s, dur) in enumerate(zip(script, durations)):
        dur = max(1.0, float(dur))
        sub_start = cursor + SUB_DELAY
        sub_end = cursor + dur + SUB_DELAY
        s.update({
            "audio_start": cursor,
            "sub_start": sub_start,
            "sub_end": sub_end,
            "dur": dur,
            "vid_duration": dur,
            "img_path": str(OUTPUT_DIR / f"img_{i}.jpg"),
            "vid_path": str(OUTPUT_DIR / f"seg_{i}.mp4"),
            "bgm_only": True,
        })
        timeline.append({
            "scene": i + 1,
            "text": s.get("text", ""),
            "start": round(cursor, 3),
            "end": round(cursor + dur, 3),
            "duration": round(dur, 3),
            "chars": chars[i],
            "reading_cps": round(chars[i] / dur, 3) if dur > 0 else None,
        })
        cursor += dur

    (OUTPUT_DIR / "bgm_only_timeline.json").write_text(
        json.dumps({
            "policy": "bgm_duration_driven",
            "energy_policy": energy_payload.get("policy") if isinstance(energy_payload, dict) else None,
            "bgm_path": bgm_path,
            "bgm_duration": bgm_dur,
            "target_total": target_total,
            "scene_total": cursor,
            "cps_limit": cps,
            "min_shot": min_shot,
            "max_shot": max_shot,
            "energy_candidate_count": len(energy_cuts or []),
            "snap_count": len(snap_records),
            "snap_rate": round(snap_rate, 4),
            "snap_records": snap_records,
            "timeline": timeline,
            "created_at": datetime.now().isoformat(timespec="seconds"),
        }, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    tg(f"✅ BGM-driven 时间轴完成：BGM {bgm_dur:.1f}s → 成片目标 {target_total:.1f}s，{n} 镜，能量吸附 {len(snap_records)}/{max(1, n-1)}，阅读上限 {cps:.1f}字/s")
    return script


# ── 第六步：并行生成图片 + BGM + 视频片段 ────────────────────────────────────
def _extract_img_url(data: dict):
    """从轮询结果中提取图片 URL，兼容多种响应格式。"""
    # 格式1: data.images = ["url"] 或 [{"url": "..."}]
    images = data.get("images") or []
    if images:
        item = images[0]
        return item.get("url") if isinstance(item, dict) else item
    # 格式2: data.task_result.image_url
    tr = data.get("task_result") or {}
    if tr.get("image_url"):
        return tr["image_url"]
    # 格式3: data.task_result.images = ["url"] 或 [{"url": "..."}]
    tr_images = tr.get("images") or []
    if tr_images:
        item = tr_images[0]
        return item.get("url") if isinstance(item, dict) else item
    # 格式4: data.image_url
    if data.get("image_url"):
        return data["image_url"]
    return None


def _extract_img_urls(data: dict) -> list[str]:
    """Extract all image URLs from a WeryAI task response."""
    urls: list[str] = []

    def _add(item):
        if isinstance(item, str) and item.startswith("http"):
            urls.append(item)
        elif isinstance(item, dict):
            for key in ("url", "image_url", "src"):
                val = item.get(key)
                if isinstance(val, str) and val.startswith("http"):
                    urls.append(val)
                    break

    for container in (
        data.get("images"),
        (data.get("task_result") or {}).get("images"),
    ):
        if isinstance(container, list):
            for item in container:
                _add(item)
        else:
            _add(container)
    for key in ("image_url",):
        _add(data.get(key))
        _add((data.get("task_result") or {}).get(key))
    deduped = []
    for url in urls:
        if url not in deduped:
            deduped.append(url)
    return deduped


def _extract_video_url(data: dict) -> str | None:
    """Extract a generated video URL from WeryAI task data."""
    candidates = [
        data.get("video_url"),
        data.get("video"),
        data.get("videos"),
        (data.get("task_result") or {}).get("video_url"),
        (data.get("task_result") or {}).get("video"),
        (data.get("task_result") or {}).get("videos"),
    ]
    for item in candidates:
        if isinstance(item, str) and item.startswith("http"):
            return item
        if isinstance(item, list) and item:
            first = item[0]
            if isinstance(first, str) and first.startswith("http"):
                return first
            if isinstance(first, dict):
                for key in ("url", "video_url", "src"):
                    val = first.get(key)
                    if isinstance(val, str) and val.startswith("http"):
                        return val
    return None


def _count_bands(flags: list[bool]) -> int:
    bands = 0
    in_band = False
    for flag in flags:
        if flag and not in_band:
            bands += 1
            in_band = True
        elif not flag:
            in_band = False
    return bands


def _detect_contact_sheet_like_image(path: str) -> dict:
    """Detect obvious contact sheets/grids using full-width/height white separators."""
    info = {
        "path": path,
        "contact_sheet": False,
        "horizontal_separator_bands": 0,
        "vertical_separator_bands": 0,
    }
    try:
        w, h = 96, 54
        raw = subprocess.check_output(
            [
                "ffmpeg", "-v", "error", "-i", path,
                "-vf", f"scale={w}:{h},format=gray",
                "-f", "rawvideo", "-",
            ],
            stderr=subprocess.DEVNULL,
            timeout=20,
        )
        if len(raw) < w * h:
            return info
        pixels = list(raw[: w * h])
        row_flags = []
        row_uniform_flags = []
        for y in range(h):
            row = pixels[y * w:(y + 1) * w]
            row_flags.append(sum(px >= 235 for px in row) / w >= 0.72)
            mean = sum(row) / w
            std = (sum((px - mean) ** 2 for px in row) / w) ** 0.5
            row_uniform_flags.append(mean >= 110 and std <= 28)
        col_flags = []
        col_uniform_flags = []
        for x in range(w):
            col = [pixels[y * w + x] for y in range(h)]
            col_flags.append(sum(px >= 235 for px in col) / h >= 0.72)
            mean = sum(col) / h
            std = (sum((px - mean) ** 2 for px in col) / h) ** 0.5
            col_uniform_flags.append(mean >= 110 and std <= 28)
        h_bands = max(_count_bands(row_flags), _count_bands(row_uniform_flags))
        v_bands = max(_count_bands(col_flags), _count_bands(col_uniform_flags))
        info.update({
            "horizontal_separator_bands": h_bands,
            "vertical_separator_bands": v_bands,
            "contact_sheet": h_bands > 0 or v_bands > 0,
        })
        return info
    except Exception as e:
        info["error"] = str(e)
        return info


_weryai_upload_lock = threading.Lock()


def _guess_upload_mime(file_path: str) -> str:
    """Prefer file signatures over extensions because WeryAI image URLs may save PNG bytes as .jpg."""
    try:
        with open(file_path, "rb") as f:
            head = f.read(16)
        if head.startswith(b"\x89PNG\r\n\x1a\n"):
            return "image/png"
        if head.startswith(b"\xff\xd8\xff"):
            return "image/jpeg"
        if head.startswith(b"RIFF") and head[8:12] == b"WEBP":
            return "image/webp"
        if head[4:8] == b"ftyp":
            return "video/mp4"
        if head.startswith(b"ID3") or head.startswith(b"\xff\xfb"):
            return "audio/mpeg"
        if head.startswith(b"RIFF") and head[8:12] == b"WAVE":
            return "audio/wav"
    except Exception:
        pass
    import mimetypes
    return mimetypes.guess_type(file_path)[0] or "application/octet-stream"


def _upload_to_weryai(file_path: str) -> str:
    """Upload a local media file to WeryAI official storage and return its URL."""
    mime = _guess_upload_mime(file_path)
    last_err = None
    for attempt in range(3):
        try:
            with _weryai_upload_lock:
                with open(file_path, "rb") as f:
                    r = requests.post(
                        f"{BASE_URL}/generation/upload-file",
                        headers={"Authorization": f"Bearer {WERYAI_API_KEY}"},
                        files={"file": (os.path.basename(file_path), f, mime)},
                        timeout=(30, 180),
                    )
            r.raise_for_status()
            data = r.json()
            urls = (data.get("data") or {}).get("object_url_list") or []
            if not urls:
                raise RuntimeError(f"upload-file 无 object_url_list: {json.dumps(data, ensure_ascii=False)[:300]}")
            return urls[0]
        except Exception as e:
            last_err = e
            if attempt < 2:
                wait_s = 3 * (attempt + 1)
                log(f"upload-file 失败（{Path(file_path).name} 第 {attempt+1}/3 次）：{e}，{wait_s}s 后重试")
                time.sleep(wait_s)
    raise RuntimeError(f"upload-file 重试失败: {last_err}")


APPROVAL_DIR = Path("/tmp/adr_approval")


def _send_for_approval(img_path: str, idx: int, scene_or_text) -> None:
    """发送图片到 TG 带审批按钮 + 写 pending 信号。
    5 次重试 + 渐进退避（5/10/20/40/80s），穿越 macOS 间歇 SSL 抖动。
    每次重试前先压缩图片（如果还是 PNG 大文件，转 JPG 减少传输撞 SSL 概率）。"""
    APPROVAL_DIR.mkdir(exist_ok=True)
    for ext in (".pending", ".approved", ".rejected"):
        (APPROVAL_DIR / f"{idx}{ext}").unlink(missing_ok=True)
    (APPROVAL_DIR / f"{idx}.pending").write_text("")

    # 预压缩：4MB+ PNG → ~500K JPG（传输时间 < 2s，远低于 SSL 抖动周期）
    compressed = str(Path(img_path).with_suffix(".compressed.jpg"))
    try:
        subprocess.run([
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-i", img_path,
            "-vf", "scale=720:-2",
            "-q:v", "5",
            compressed,
        ], check=True, timeout=20)
        upload_path = compressed
    except Exception:
        upload_path = img_path  # 压缩失败用原图

    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendPhoto"
    reply_markup = json.dumps({
        "inline_keyboard": [[
            {"text": "✅ 通过", "callback_data": f"adr_approve_{idx}"},
            {"text": "🔄 重做", "callback_data": f"adr_reject_{idx}"},
        ]]
    })
    if isinstance(scene_or_text, dict):
        scene = scene_or_text
        if NO_VOICE:
            visual_text = str(scene.get("prompt") or "").strip()
            internal_text = str(scene.get("text") or "").strip()
            caption = (
                f"🖼 图 {idx+1} 审批（BGM-only，无字幕）\n\n"
                f"视觉意图：{visual_text[:900]}\n\n"
                f"内部文案（仅用于分镜节奏，不会出现在成片）：{internal_text[:180]}"
            )
        else:
            caption = f"🖼 图 {idx+1} 审批\n\n{str(scene.get('text') or '')}"
    else:
        caption = f"🖼 图 {idx+1} 审批\n\n{str(scene_or_text)}"

    delays = [0, 5, 10, 20, 40, 80]  # 第 0-5 次尝试前的等待
    for attempt in range(6):
        if delays[attempt] > 0:
            time.sleep(delays[attempt])
        try:
            with open(upload_path, "rb") as f:
                resp = requests.post(url, data={
                    "chat_id": TG_CHAT_ID,
                    "caption": caption,
                    "reply_markup": reply_markup,
                }, files={"photo": f}, timeout=(15, 60))
            if resp.status_code == 200 and resp.json().get("ok"):
                return  # 成功
            log(f"审批图 {idx+1} 第 {attempt+1}/6 次 HTTP {resp.status_code}: {resp.text[:150]}")
        except Exception as e:
            log(f"审批图 {idx+1} 第 {attempt+1}/6 次异常: {type(e).__name__}: {str(e)[:150]}")
    log(f"审批图 {idx+1} 6 次全失败，标记为已发送但 Telegram 未到达（5min 超时自动通过）")


def _wait_approval(idx: int, timeout: int = 300) -> bool:
    """轮询信号文件，返回 True=通过，False=重做。超时视为通过。"""
    for _ in range(timeout // 2):
        if (APPROVAL_DIR / f"{idx}.approved").exists():
            return True
        if (APPROVAL_DIR / f"{idx}.rejected").exists():
            return False
        time.sleep(2)
    log(f"图 {idx+1} 审批超时（{timeout}s），自动通过")
    return True


def _render_still_segment(scene: dict, timeout: int = 30) -> None:
    """Render one still image into its timed video segment."""
    dur = scene["vid_duration"]
    ffmpeg(
        "-loop", "1", "-framerate", "24", "-t", str(dur),
        "-i", scene["img_path"],
        "-vf", f"scale={VIDEO_W}:{VIDEO_H}:force_original_aspect_ratio=increase,crop={VIDEO_W}:{VIDEO_H},setsar=1",
        "-c:v", "libx264", "-crf", "23", "-preset", "ultrafast",
        "-pix_fmt", "yuv420p", "-an",
        scene["vid_path"],
        timeout=timeout,
    )


def _scene_text_visual_alignment(scene: dict, idx: int) -> dict:
    text = str(scene.get("text") or "")
    prompt = str(scene.get("prompt") or "")
    prompt_l = prompt.lower()
    tokens = []
    tokens.extend(re.findall(r"[A-Za-z][A-Za-z0-9_\-]{2,}", text))
    tokens.extend(re.findall(r"\d{2,4}(?:年|月|日)?", text))
    tokens.extend(re.findall(r"[\u4e00-\u9fff]{2,6}", text))
    stop = {
        "这个", "那个", "他们", "我们", "你们", "一个", "一种", "不是", "就是", "因为", "所以", "但是", "如果",
        "今天", "历史", "时候", "事情", "真正", "所有", "可能", "没有", "已经", "开始", "最后", "中国",
    }
    dedup = []
    for token in tokens:
        t = token.strip()
        if not t or t in stop or len(t) < 2:
            continue
        if t not in dedup:
            dedup.append(t)
    core = dedup[:10]
    matched = [t for t in core if t.lower() in prompt_l or t in prompt]
    min_match = 1 if len(core) <= 3 else 2
    pass_flag = len(matched) >= min_match or not core
    return {
        "scene": idx + 1,
        "pass": pass_flag,
        "text": text[:160],
        "core_terms": core,
        "matched_terms": matched,
        "match_count": len(matched),
        "required_match_count": min_match,
        "prompt_excerpt": prompt[:260],
        "reason": "" if pass_flag else "dialogue_core_terms_not_reflected_in_visual_prompt",
    }


def _write_text_visual_alignment_qa(script: list[dict]) -> dict:
    records = [_scene_text_visual_alignment(scene, i) for i, scene in enumerate(script)]
    failed = [r for r in records if not r.get("pass")]
    payload = {
        "mode": ADSD_MODE_NAME if ADS_DIALOGUE_MODE else ("VDAR" if IS_VERTICAL else "HDAR"),
        "policy": "warn_on_dialogue_visual_prompt_mismatch",
        "total": len(records),
        "failed_count": len(failed),
        "failed_scenes": [r.get("scene") for r in failed],
        "pass": len(failed) == 0,
        "records": records,
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }
    try:
        (OUTPUT_DIR / "text_visual_alignment_qa.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except Exception as e:
        log(f"text_visual_alignment_qa.json 写入失败: {e}")
    return payload


def _scene_motion_action_plan(scene: dict, idx: int) -> dict:
    """Build a reusable action beat for storyboard, motion prompt, and QA."""
    if not MOTION_ACTION_STORYBOARD:
        return {}
    text = re.sub(r"\s+", " ", str(scene.get("text") or "")).strip()
    visual = re.sub(r"\s+", " ", str(scene.get("shot") or scene.get("prompt") or "")).strip()
    src = f"{text} {visual}"
    lowered = src.lower()

    def has(*words: str) -> bool:
        return any(w in src or w.lower() in lowered for w in words)

    if _is_action_scene(text, visual) or has(
        "剑", "刀", "战", "军", "冲", "杀", "追", "火", "爆", "危", "怒", "纷争", "恩怨",
        "龙", "龙影", "巨龙", "龙吟", "掌劲", "气浪", "冲击波", "龟裂", "光墙", "风暴",
    ):
        action = "the figure snaps into a decisive martial or confrontational gesture, fabric and dust reacting as tension rises"
        camera = "handheld push-in, short whip-pan into a low-angle parallax slide, then rack focus to the weapon or hand"
        speed = "fast"
        energy = 0.9
        sfx = "cloth snap, footstep hit, blade air, tense room tone"
    elif has("无人机", "拖拉机", "机器人", "工厂", "农机", "导弹", "汽车", "压铸", "AGV", "生产线"):
        action = "machines move through frame with one clear operational beat, arms, vehicles, belts, or drones completing a visible task"
        camera = "tracking move alongside the machine, foreground parallax, quick rack focus from operator interface to moving hardware"
        speed = "medium-fast"
        energy = 0.82
        sfx = "servo motors, engine hum, conveyor rhythm, pneumatic hits"
    elif has("说", "讲", "问", "知道", "意味着", "道路", "本心", "逍遥", "智慧", "未来"):
        action = "the speaker changes posture, raises a hand, points to a meaningful object, or turns toward the listener on the key phrase"
        camera = "medium close tracking push with over-the-shoulder parallax and a clean rack focus to hands, eyes, or a prop"
        speed = "medium"
        energy = 0.68
        sfx = "breath, sleeve movement, ambient room tone"
    elif has("看", "记忆", "历史", "时代", "开朗", "释然", "平和"):
        action = "the subject shifts from stillness into a readable reveal, turning or stepping as the environment responds subtly"
        camera = "controlled pull-back reveal with side parallax and a soft rack focus from detail to full composition"
        speed = "medium-slow"
        energy = 0.58
        sfx = "wind, distant ambience, fabric movement"
    else:
        action = "the main subject performs one clear readable gesture or movement beat instead of remaining still"
        camera = "motivated dolly-in with foreground parallax and a brief rack focus to the key prop or face"
        speed = "medium"
        energy = 0.65
        sfx = "location ambience, cloth and object movement"
    return {
        "motion_action_beat": action,
        "motion_camera": camera,
        "motion_speed": speed,
        "motion_energy": energy,
        "motion_sfx": sfx,
    }


def _ensure_motion_action_plan(script: list[dict]) -> None:
    if not MOTION_ACTION_STORYBOARD:
        return
    for idx, scene in enumerate(script):
        plan = _scene_motion_action_plan(scene, idx)
        for key, value in plan.items():
            scene.setdefault(key, value)


def _motion_action_block(scene: dict, limit: int = 700) -> str:
    if not MOTION_ACTION_STORYBOARD:
        return ""
    action = _short_board_text(scene.get("motion_action_beat"), 220)
    camera = _short_board_text(scene.get("motion_camera"), 220)
    speed = _short_board_text(scene.get("motion_speed"), 60)
    sfx = _short_board_text(scene.get("motion_sfx"), 140)
    energy = scene.get("motion_energy")
    parts = []
    if action:
        parts.append(f"Action beat: {action}")
    if camera:
        parts.append(f"Camera: {camera}")
    if speed:
        parts.append(f"Speed: {speed}")
    if energy is not None:
        parts.append(f"Motion energy target: {energy}")
    if sfx:
        parts.append(f"SFX: {sfx}")
    return _short_board_text(". ".join(parts), limit)


def _motion_plan_for_qa(scene: dict) -> dict:
    return {
        "motion_action_beat": scene.get("motion_action_beat"),
        "motion_camera": scene.get("motion_camera"),
        "motion_speed": scene.get("motion_speed"),
        "motion_energy_target": scene.get("motion_energy"),
        "motion_sfx": scene.get("motion_sfx"),
    }


def _write_motion_action_plan_qa(script: list[dict]) -> dict:
    records = []
    for idx, scene in enumerate(script, start=1):
        plan = _motion_plan_for_qa(scene)
        missing = [k for k, v in plan.items() if v in (None, "")]
        energy = float(plan.get("motion_energy_target") or 0)
        records.append({
            "scene": idx,
            "pass": not missing and energy >= 0.55,
            "missing": missing,
            **plan,
        })
    failed = [r for r in records if not r.get("pass")]
    payload = {
        "mode": "motion_action_storyboard_plan",
        "enabled": MOTION_ACTION_STORYBOARD,
        "total": len(records),
        "failed_count": len(failed),
        "failed_scenes": [r["scene"] for r in failed],
        "pass": len(failed) == 0,
        "records": records,
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }
    try:
        (OUTPUT_DIR / "motion_action_plan_qa.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as e:
        log(f"motion_action_plan_qa.json 写入失败: {e}")
    return payload


def _write_motion_bridge_refs_qa(payload: dict) -> None:
    try:
        (OUTPUT_DIR / "motion_bridge_refs_qa.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as e:
        log(f"motion_bridge_refs_qa.json 写入失败: {e}")


def _motion_bridge_ref_prompt(scene: dict, idx: int, total: int, topic: str, aspect: str) -> str:
    visual = _short_board_text(scene.get("prompt") or scene.get("shot") or scene.get("text"), 760)
    action = _short_board_text(scene.get("motion_action_beat"), 260)
    camera = _short_board_text(scene.get("motion_camera"), 220)
    speed = _short_board_text(scene.get("motion_speed"), 60)
    text = _short_board_text(scene.get("text"), 160)
    culture_guard = _topic_culture_guard(scene.get("topic_meta", {}))
    return f"""Create one single standalone cinematic END KEYFRAME for shot {idx + 1}/{total} of a Chinese documentary: {topic}.
{culture_guard}
Aspect ratio: {aspect}.

This image will be used as the second reference frame for image-to-video motion. It must look like the same shot a moment later, not a new scene.

Continuity lock:
- Same character identity, era, costume, hair, props, location, lighting, palette, and camera language as the visual source.
- No captions, no subtitles, no labels, no logos, no watermark, no comic panels, no storyboard layout, no text.
- Do not make a passive portrait. Show the action already happening or just completed.

Visual source:
{visual}

Dialogue/story beat:
{text}

Required end-frame action:
{action}

Camera/motion intention:
{camera}; speed {speed}.

Output only the clean final cinematic frame at the most readable end moment of the action."""


def generate_motion_bridge_refs_gpt_image2(script: list[dict], topic: str) -> dict | None:
    """Generate per-shot action end keyframes so WeryDance has start/end visual anchors."""
    if not MOTION_BRIDGE_REFS or ADS_DIALOGUE_MODE:
        return None
    # trailer-main 模式不跑单镜 motion，bridge refs 没消费方，跳过省 ~5min + 12 张 GPT Image 2 credits
    if STORYBOARD_TRAILER_MAIN:
        log("STORYBOARD_TRAILER_MAIN 开启，跳过 motion_bridge_refs（trailer 主路径不消费）")
        return None
    _model, aspect, extra = pick_image_model(ASPECT_RATIO)
    if _model != "GPT_IMAGE_2":
        return None
    max_refs = max(0, int(os.environ.get("ADR_MOTION_BRIDGE_REFS_MAX", "12")))
    poll_max = float(os.environ.get("ADR_MOTION_BRIDGE_REFS_POLL_MAX", "240"))
    energy_min = float(os.environ.get("ADR_MOTION_BRIDGE_REFS_MIN_ENERGY", "0.6"))
    submit_stagger_sec = max(0.0, float(os.environ.get("ADR_MOTION_BRIDGE_REFS_SUBMIT_STAGGER", "12")))
    poll_workers = max(1, min(20, int(os.environ.get("ADR_MOTION_BRIDGE_REFS_POLL_WORKERS", "20"))))
    candidates = [
        (i, scene)
        for i, scene in enumerate(script[:max_refs])
        if scene.get("img_path") and os.path.exists(scene.get("img_path")) and float(scene.get("motion_energy") or 0) >= energy_min
    ]
    qa = {
        "mode": "gpt_image2_motion_bridge_end_keyframes",
        "enabled": True,
        "model": "GPT_IMAGE_2",
        "aspect_ratio": aspect,
        "energy_min": energy_min,
        "requested_count": len(candidates),
        "records": [],
        "submit_stagger_sec": submit_stagger_sec,
        "poll_workers": poll_workers,
        "pass": False,
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }
    if not candidates:
        qa["reason"] = "no_candidate_scenes"
        _write_motion_bridge_refs_qa(qa)
        return qa
    tg(f"🎭 动作桥接关键帧启动：GPT Image 2 × {len(candidates)} 张 end keyframe")
    submitted: list[tuple[dict, int, dict, Path]] = []
    for submit_i, (idx, scene) in enumerate(candidates):
        out_path = OUTPUT_DIR / f"motion_bridge_ref_{idx}.jpg"
        rec = {
            "scene": idx + 1,
            "path": str(out_path),
            "motion_plan": _motion_plan_for_qa(scene),
            "pass": False,
        }
        qa["records"].append(rec)
        try:
            prompt = _motion_bridge_ref_prompt(scene, idx, len(script), topic, aspect)
            if len(prompt) > 18000:
                prompt = prompt[:18000]
                rec["prompt_truncated"] = True
            if submit_i > 0 and submit_stagger_sec > 0:
                log(f"GPT Image 2 motion bridge ref 错峰提交等待 {submit_stagger_sec:.1f}s（{submit_i+1}/{len(candidates)}）")
                time.sleep(submit_stagger_sec)
            r = submit_text_to_image({
                "model": "GPT_IMAGE_2",
                "prompt": prompt,
                "aspect_ratio": aspect,
                "image_number": 1,
                **extra,
            }, f"GPT Image 2 motion bridge ref {idx+1}/{len(script)}", timeout=45, max_attempts=3)
            task_id = (r.get("data", {}).get("task_ids") or [r.get("data", {}).get("task_id") or None])[0]
            rec["task_id"] = task_id
            if not task_id:
                rec.update({"reason": "submit_without_task_id", "response": r})
                continue
            submitted.append((rec, idx, scene, out_path))
        except Exception as e:
            rec.update({"pass": False, "reason": str(e)[:300]})
        _write_motion_bridge_refs_qa(qa)

    def poll_motion_bridge(entry: tuple[dict, int, dict, Path]) -> dict:
        rec, idx, scene, out_path = entry
        try:
            task_id = rec.get("task_id")
            data = poll_storyboard_task(task_id, f"GPT Image 2 motion bridge ref {idx+1}/{len(script)}", poll_max)
            urls = _extract_img_urls(data)
            if not urls:
                rec["reason"] = "succeed_without_image_url"
                return rec
            urllib.request.urlretrieve(urls[0], out_path)
            contact_check = _detect_contact_sheet_like_image(str(out_path))
            rec["contact_sheet_check"] = contact_check
            rec["bytes"] = out_path.stat().st_size if out_path.exists() else 0
            rec["pass"] = out_path.exists() and out_path.stat().st_size > 100000 and not contact_check.get("contact_sheet")
            if rec["pass"]:
                scene["motion_bridge_ref_paths"] = [str(out_path)]
        except Exception as e:
            rec.update({"pass": False, "reason": str(e)[:300]})
        return rec

    if submitted:
        with ThreadPoolExecutor(max_workers=min(poll_workers, len(submitted))) as ex:
            futs = [ex.submit(poll_motion_bridge, entry) for entry in submitted]
            for fut in as_completed(futs):
                fut.result()
                _write_motion_bridge_refs_qa(qa)
    ok_count = sum(1 for r in qa["records"] if r.get("pass"))
    qa.update({
        "success_count": ok_count,
        "pass": ok_count >= max(1, math.ceil(len(candidates) * 0.7)),
    })
    _write_motion_bridge_refs_qa(qa)
    if ok_count:
        tg(f"✅ 动作桥接关键帧完成：{ok_count}/{len(candidates)} 张可用")
    else:
        tg("⚠️ 动作桥接关键帧全部失败，本次仍使用单帧 motion")
    return qa


def generate_image(scene: dict, idx: int, _max_retries: int = 3) -> int:
    last_err = None
    for attempt in range(_max_retries):
        try:
            _m, _ar, _extra = pick_image_model(ASPECT_RATIO)
            r = submit_text_to_image({
                "model":        _m,
                "prompt":       scene["prompt"],
                "aspect_ratio": _ar,
                "image_number": 1,
                **_extra,
            }, f"图片 {idx+1}", timeout=30)

            data_part = r.get("data", {})
            task_ids = data_part.get("task_ids") or (
                [data_part["task_id"]] if data_part.get("task_id") else []
            )
            if not task_ids:
                raise RuntimeError(f"图片 {idx+1} 提交失败（无 task_id）: {json.dumps(r, ensure_ascii=False)[:200]}")

            data = poll(task_ids[0], f"图片 {idx+1}")
            img_url = _extract_img_url(data)
            if not img_url:
                raise RuntimeError(f"图片 {idx+1} 无 URL，data={json.dumps(data, ensure_ascii=False)[:300]}")

            urllib.request.urlretrieve(img_url, scene["img_path"])
            break  # 成功
        except Exception as e:
            last_err = e
            if attempt < _max_retries - 1:
                if _is_rate_limited_error(e):
                    wait_s = IMAGE_RATE_LIMIT_BACKOFF * (attempt + 1)
                else:
                    wait_s = 3 * (attempt + 1)
                log(f"图片 {idx+1} 失败（第 {attempt+1} 次）：{e}，{wait_s:.1f}s 后重试...")
                time.sleep(wait_s)
                continue
            raise RuntimeError(f"图片 {idx+1} 重试 {_max_retries} 次仍失败：{last_err}")

    # ★ timeout=30s：单图转视频段超过 30s 即视为图损坏（如 img_13 PNG header 错误让 parser 死循环）
    # ★ ffmpeg 失败 → generate_image 抛 RuntimeError → step6 fallback 用相邻图顶替（不卡管线）
    _render_still_segment(scene)
    dur = scene["vid_duration"]
    tg(f"🖼 图片 {idx+1} 生成完毕（{scene['emotion']}）→ 转视频 {dur:.2f}s ✓")
    return idx


def generate_storyboard_images_gpt_image2(script: list[dict], topic: str) -> bool:
    """Primary ADR/ADS image path: GPT_IMAGE_2 storyboard batches, old per-scene path as fallback.

    If anything is incomplete, return False so step6 can fall back to per-scene generation.
    """
    if not GPT_IMAGE2_STORYBOARD:
        return False
    n = len(script)
    if n <= 0:
        return False
    max_n = int(os.environ.get("ADR_GPT_IMAGE2_STORYBOARD_MAX", "24"))
    if n > max_n:
        log(f"GPT Image 2 storyboard 跳过：分镜数 {n} 超过上限 {max_n}")
        return False

    _model, _aspect, _extra = pick_image_model(ASPECT_RATIO)
    if _model != "GPT_IMAGE_2":
        log(f"GPT Image 2 storyboard 跳过：当前图片模型为 {_model}")
        return False

    qa = {
        "mode": "gpt_image2_storyboard",
        "enabled": True,
        "used": False,
        "fallback": False,
        "model": "GPT_IMAGE_2",
        "aspect_ratio": _aspect,
        "requested_count": n,
        "batch_size": min(4, int(os.environ.get("ADR_GPT_IMAGE2_STORYBOARD_BATCH", "1"))),
        "batch_poll_timeout_sec": float(os.environ.get("ADR_GPT_IMAGE2_STORYBOARD_POLL_MAX", "240")),
        "submit_stagger_sec": max(0.0, float(os.environ.get("ADR_GPT_IMAGE2_STORYBOARD_SUBMIT_STAGGER", "12"))),
        "poll_workers": max(1, min(20, int(os.environ.get("ADR_GPT_IMAGE2_STORYBOARD_POLL_WORKERS", "20")))),
        "batches": [],
        "downloaded_count": 0,
        "rendered_count": 0,
        "contact_sheet_checks": [],
        "issues": [],
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }

    try:
        batch_size = max(1, min(4, int(qa["batch_size"])))
        total_batches = math.ceil(n / batch_size)
        submitted_batches: list[dict] = []
        for batch_idx, start in enumerate(range(0, n, batch_size), start=1):
            end = min(n, start + batch_size)
            batch_script = script[start:end]
            culture_guard = _topic_culture_guard(batch_script[0].get("topic_meta", {}) if batch_script else {})
            scene_lines = []
            for local_i, scene in enumerate(batch_script, start=start + 1):
                prompt = re.sub(r"\s+", " ", str(scene.get("prompt") or "")).strip()
                text = re.sub(r"\s+", " ", str(scene.get("text") or "")).strip()
                action_block = _motion_action_block(scene, 520)
                scene_lines.append(
                    f"{local_i}. Visual prompt: {prompt[:760]}\n"
                    f"   Internal story beat: {text[:150]}\n"
                    f"   Motion plan: {action_block}"
                )
            batch_count = len(batch_script)
            if batch_count == 1:
                storyboard_prompt = (
                    f"Create one single full-frame cinematic storyboard image for scene {start+1} "
                    f"of one short video about: {topic}.\n"
                    f"{culture_guard}\n"
                    f"Aspect ratio: {ASPECT_RATIO}. This is scene {start+1}/{n}; keep the same visual identity as a continuous series. "
                    "The entire output must be one uninterrupted shot, not a layout. "
                    "Strictly forbidden: collage, contact sheet, grid, comic page, split screen, panels, frames, borders, white divider lines, captions, subtitles, watermarks, random text. "
                    "Keep consistent palette, lighting, era, costumes, and subject continuity. "
                    "Pose the frame at the most dynamic readable moment of the action beat, not a passive still.\n\n"
                    "Scene:\n" + "\n".join(scene_lines)
                )
            else:
                storyboard_prompt = (
                    f"Create exactly {batch_count} separate storyboard images for scenes {start+1}-{end} "
                    f"of one short video about: {topic}.\n"
                    f"{culture_guard}\n"
                    f"Aspect ratio: {ASPECT_RATIO}. This is batch {batch_idx}/{total_batches}; keep the same visual identity as a continuous series. "
                    "Do NOT create a collage, contact sheet, grid, comic page, split screen, panels, frames, borders, or multi-panel image. Return separate standalone full-frame images, "
                    "one image per numbered scene. Keep consistent palette, lighting, era, costumes, and subject continuity. "
                    "Each frame must show the most dynamic readable moment of its action beat, not a passive still. "
                    "No watermarks, no captions, no subtitles, no random text.\n\n"
                    "Scenes:\n" + "\n".join(scene_lines)
                )
            if len(storyboard_prompt) > 18000:
                storyboard_prompt = storyboard_prompt[:18000]
                qa.setdefault("warnings", []).append(f"batch_{batch_idx}_prompt_truncated")

            if batch_idx > 1 and qa["submit_stagger_sec"] > 0:
                log(f"GPT Image 2 storyboard fallback 错峰提交等待 {qa['submit_stagger_sec']:.1f}s（{batch_idx}/{total_batches}）")
                time.sleep(float(qa["submit_stagger_sec"]))
            r = submit_text_to_image({
                "model": "GPT_IMAGE_2",
                "prompt": storyboard_prompt,
                "aspect_ratio": _aspect,
                "image_number": batch_count,
                **_extra,
            }, f"GPT Image 2 storyboard batch {batch_idx}/{total_batches}", timeout=45)
            data_part = r.get("data", {})
            task_ids = data_part.get("task_ids") or ([data_part["task_id"]] if data_part.get("task_id") else [])
            batch_qa = {
                "batch": batch_idx,
                "scene_start": start + 1,
                "scene_end": end,
                "requested_count": batch_count,
                "task_ids": task_ids,
                "image_count": 0,
            }
            qa["batches"].append(batch_qa)
            if not task_ids:
                qa["issues"].append(f"batch_{batch_idx}_submit_without_task_id: {json.dumps(r, ensure_ascii=False)[:200]}")
                raise RuntimeError(f"storyboard batch {batch_idx} returned no task_id")
            submitted_batches.append({
                "batch_qa": batch_qa,
                "batch_count": batch_count,
            })

        def poll_storyboard_batch(entry: dict) -> tuple[int, list[str]]:
            batch_qa = entry["batch_qa"]
            batch_urls: list[str] = []
            task_ids = batch_qa.get("task_ids") or []
            for j, tid in enumerate(task_ids):
                data = poll_storyboard_task(
                    tid,
                    f"GPT Image 2 storyboard batch {batch_qa['batch']}/{total_batches} task {j+1}/{len(task_ids)}",
                    qa["batch_poll_timeout_sec"],
                )
                batch_urls.extend(_extract_img_urls(data))
            batch_qa["image_count"] = len(batch_urls)
            batch_count = int(entry["batch_count"])
            if len(batch_urls) < batch_count:
                qa["issues"].append(f"batch_{batch_qa['batch']}_image_count_mismatch: got {len(batch_urls)}, need {batch_count}")
                raise RuntimeError(f"storyboard batch {batch_qa['batch']} image count mismatch: got {len(batch_urls)}, need {batch_count}")
            return int(batch_qa["scene_start"]) - 1, batch_urls[:batch_count]

        img_urls: list[str | None] = [None] * n
        if submitted_batches:
            with ThreadPoolExecutor(max_workers=min(int(qa["poll_workers"]), len(submitted_batches))) as ex:
                futs = [ex.submit(poll_storyboard_batch, entry) for entry in submitted_batches]
                for fut in as_completed(futs):
                    start_idx, urls = fut.result()
                    for offset, url in enumerate(urls):
                        if start_idx + offset < n:
                            img_urls[start_idx + offset] = url

        if any(not u for u in img_urls):
            missing = [i + 1 for i, u in enumerate(img_urls) if not u]
            qa["issues"].append(f"image_count_mismatch: missing {missing}")
            raise RuntimeError(f"storyboard image count mismatch: missing {missing}")

        for i, url in enumerate(img_urls[:n]):
            path = script[i]["img_path"]
            urllib.request.urlretrieve(str(url), path)
            qa["downloaded_count"] += 1
            contact_check = _detect_contact_sheet_like_image(path)
            contact_check["scene"] = i + 1
            qa["contact_sheet_checks"].append(contact_check)
            if contact_check.get("contact_sheet"):
                qa["issues"].append(f"scene_{i+1}_contact_sheet_detected")
                raise RuntimeError(f"scene {i+1} storyboard looks like a contact sheet/grid: {contact_check}")
            script[i]["storyboard_mode"] = True
            script[i]["storyboard_source_url"] = str(url)
            _render_still_segment(script[i])
            qa["rendered_count"] += 1

        qa["used"] = True
        qa["pass"] = True
        tg(f"🖼 GPT Image 2 一次性分镜成功：{qa['downloaded_count']}/{n} 张，已转视频")
        return True
    except Exception as e:
        qa["fallback"] = True
        qa["pass"] = False
        qa["issues"].append(str(e))
        log(f"GPT Image 2 storyboard 失败，回退逐张生成：{e}")
        tg(f"⚠️ GPT Image 2 一次性分镜失败，自动回退逐张生成：{str(e)[:160]}")
        return False
    finally:
        try:
            (OUTPUT_DIR / "storyboard_qa.json").write_text(
                json.dumps(qa, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except Exception as e:
            log(f"storyboard_qa.json 写入失败: {e}")


def _storyboard_grid_aspect() -> str:
    override = os.environ.get("ADR_GPT_IMAGE2_STORYBOARD_GRID_ASPECT", "").strip()
    if override:
        return override
    return "9:16(4k)" if IS_VERTICAL else "16:9(4k)"


def _storyboard_grid_cols_rows(count: int) -> tuple[int, int]:
    if IS_VERTICAL:
        if count <= 4:
            return 2, 2
        if count <= 6:
            return 2, 3
        if count <= 9:
            return 3, 3
        if count <= 12:
            return 3, 4
        return 4, 4
    if count <= 4:
        return 2, 2
    if count <= 6:
        return 3, 2
    if count <= 9:
        return 3, 3
    if count <= 12:
        return 4, 3
    return 4, 4


def _storyboard_grid_prompt(batch_script: list[dict], start: int, total: int, topic: str, cols: int, rows: int, aspect: str) -> str:
    lines = []
    visual_limit = max(120, int(os.environ.get("ADR_STORYBOARD_GRID_VISUAL_CHARS", "220")))
    beat_limit = max(40, int(os.environ.get("ADR_STORYBOARD_GRID_BEAT_CHARS", "64")))
    motion_limit = max(80, int(os.environ.get("ADR_STORYBOARD_GRID_MOTION_CHARS", "180")))
    for local_i, scene in enumerate(batch_script, start=start + 1):
        prompt = re.sub(r"\s+", " ", str(scene.get("prompt") or scene.get("text") or "")).strip()
        text = re.sub(r"\s+", " ", str(scene.get("text") or "")).strip()
        action = _motion_action_block(scene, motion_limit)
        lines.append(f"{local_i:02d}. Visual: {prompt[:visual_limit]}\n    Beat: {text[:beat_limit]}\n    Motion: {action}")
    count = len(batch_script)
    culture_guard = _topic_culture_guard(batch_script[0].get("topic_meta", {}) if batch_script else {})
    return f"""Create one single {aspect} cinematic storyboard grid for a documentary sequence.
Topic: {topic}
{culture_guard}
Grid: exact {cols} columns x {rows} rows, {count} panels filled in reading order left-to-right then top-to-bottom. Leave unused panels empty only if the grid has more cells than requested.

Panel rules:
- Each panel is a clean cinematic frame, not a text card.
- No shot numbers, no labels, no captions, no subtitles, no speech bubbles, no watermarks, no logos.
- No arrows or motion graphics; motion will be handled separately.
- Thin panel separators are acceptable, but keep every panel visually clean so it can be cropped into a standalone reference image.
- Pose every panel at an active moment from its Motion plan; avoid static portrait/key art unless the Motion plan says reveal.
- Keep one consistent era, palette, lighting, location logic, costume design, and subject identity across all panels.
- Cultural accuracy is mandatory; if the topic is Western/British/European, never use Chinese/East-Asian visual language.
- Each panel must be distinct and readable at 4K.

Shot beats:
{chr(10).join(lines)}"""


def _storyboard_grid_prompt_limit() -> int:
    return max(4000, int(os.environ.get("ADR_GPT_IMAGE2_STORYBOARD_GRID_PROMPT_LIMIT", "9500")))


def _is_prompt_limit_response(response: object) -> bool:
    text = json.dumps(response, ensure_ascii=False) if not isinstance(response, str) else response
    text_l = text.lower()
    return "prompt length exceeds" in text_l or "exceeds the limit" in text_l or "10000 characters" in text_l


def _production_storyboard_prompt(script: list[dict], topic: str, aspect: str) -> str:
    lines = []
    for i, scene in enumerate(script, start=1):
        visual = re.sub(r"\s+", " ", str(scene.get("prompt") or scene.get("text") or "")).strip()
        beat = re.sub(r"\s+", " ", str(scene.get("text") or "")).strip()
        action = _motion_action_block(scene, 300)
        lines.append(f"{i:02d}. VISUAL: {visual[:300]} | STORY BEAT: {beat[:90]} | MOTION: {action}")
    return f"""Create one single {aspect} AI animation production storyboard board.
Topic: {topic}

Purpose:
- This is a director-facing production board for an AI animation pipeline, not a final cinematic frame.
- It should look like a professional hand-drawn animation workflow board: clear, structured, dense, and readable.
- It will be used as a reference for a 10-15 second trailer, so include enough sequencing, cast, camera, action, and mood information.

Board layout requirements:
- Title band: short production title and visual tone.
- Concept block: core world, mood, visual style, era/location logic.
- Cast/design block: key character or subject silhouettes, costume/prop notes, expression references.
- Main storyboard block: {len(script)} numbered shot panels in reading order, each with a small cinematic sketch/keyframe.
- Motion/camera block: concise notes for camera moves, action beats, speed, transitions, SFX/music cues.
- Palette/style block: color chips, lighting notes, texture/material cues.
- QA checklist block: continuity, character consistency, reusable assets, industrialized pipeline, no random drift.

Style:
- Whiteboard / production notebook / animation previsualization sheet.
- Hand-drawn ink, pencil, marker accents, clean typography, readable micro-layout.
- Keep all panels visually connected and consistent, like an animation studio production sheet.
- Do not make one huge poster illustration; make a structured production board with multiple useful sections.

Shot plan:
{chr(10).join(lines)}"""


def _write_production_storyboard_page_qa(payload: dict) -> None:
    try:
        (OUTPUT_DIR / "production_storyboard_page_qa.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except Exception as e:
        log(f"production_storyboard_page_qa.json 写入失败: {e}")


def _character_sheet_prompt(script: list[dict], topic: str, aspect: str) -> str:
    beats = []
    speakers = []
    for i, scene in enumerate(script[:12], start=1):
        visual = re.sub(r"\s+", " ", str(scene.get("prompt") or scene.get("text") or "")).strip()
        speaker = re.sub(r"\s+", " ", str(scene.get("speaker") or "")).strip()
        if speaker and speaker not in speakers:
            speakers.append(speaker)
        beats.append(f"{i:02d}. {visual[:280]}")
    if ADS_DIALOGUE_MODE:
        if any(s.get("injected_script") for s in script):
            on_camera = []
            for scene in script:
                sp = str(scene.get("speaker") or "").strip()
                if sp and scene.get("needs_lip_sync", True) and sp not in on_camera:
                    on_camera.append(sp)
            if not on_camera:
                on_camera = [s for s in speakers if s and "旁白" not in s][:4] or speakers[:4]

            def _short_role(sp: str) -> str:
                if any(k in sp for k in ("黄仁勋", "Jensen")):
                    return "Asian male tech CEO, black leather jacket, short gray hair, rimless glasses, confident restrained expression, GPU keynote props."
                if any(k in sp for k in ("特朗普", "川普", "Trump")):
                    return "older blond American president-like politician, navy suit, white shirt, red tie, assertive hand gesture, White House corridor props."
                if "旁白" in sp:
                    return "male voice-over only; use B-roll visuals, no recurring on-camera narrator face."
                return "distinct documentary speaker, period-accurate face, costume, hair, props, neutral talking expression."

            role_block = "\n".join(f"- {sp}: {_short_role(sp)}" for sp in on_camera[:4])
            short_beats = []
            for i, scene in enumerate(script[:6], start=1):
                beat = re.sub(r"\s+", " ", str(scene.get("text") or "")).strip()
                short_beats.append(f"{i:02d}. {beat[:70]}")
            return f"""Create one single {aspect} concise dialogue cast model sheet.
Topic: US-China chip negotiation documentary.

Use this as identity reference for WeryDance lip-sync only.
Draw clean reusable speaker references, not a poster and not a storyboard.

Speakers:
{role_block}

Layout:
- One row per on-camera speaker.
- Front view, 3/4 view, side view, neutral talking expression.
- Large clear face, consistent costume, reusable props, coherent modern geopolitical documentary style.
- No subtitles, no dialogue text, no watermarks, no comic panels.

Context beats:
{chr(10).join(short_beats)}"""
        role_lines = []
        for speaker in speakers[:8]:
            first = next((s for s in script if s.get("speaker") == speaker), {})
            subject = re.sub(r"\s+", " ", str(first.get("visual_subject") or first.get("speaker_visual_contract") or "")).strip()
            role_lines.append(f"- {speaker}: {subject[:320]}")
        role_block = "\n".join(role_lines) or "- Active historical dialogue speakers must be visually distinct and reusable."
        return f"""Create one single {aspect} cinematic dialogue cast model sheet for an AI historical documentary.
Topic: {topic}

Purpose:
- This sheet will be reused as a visual identity reference for ADSD lip-sync shots.
- It must lock each dialogue speaker's face, age, gender, costume, hair, silhouette, props, and period role.
- It is a reference sheet only; do not make a poster, comic page, subtitle card, or final video frame.
- Cultural and period accuracy must match the topic and every embedded shot prompt.

Dialogue speaker designs:
{role_block}

Layout requirements:
- One clean row or column per speaker, each with front view, 3/4 view, side view, and a neutral talking expression.
- Keep speakers visually distinct but in one coherent historical production style.
- Include period-accurate costume and prop callouts for each speaker.
- Small role labels are acceptable on the sheet; keep faces large and reusable as references.
- No subtitles, no dialogue text, no watermarks.

Story context:
{chr(10).join(beats)}"""
    return f"""Create one single {aspect} cinematic character and creature model sheet for an AI animation trailer.
Topic: {topic}

Purpose:
- This sheet will be reused as a visual identity reference for every video shot.
- It must lock the recurring hero/subject identity, costume, face, palette, props, and any creature/vehicle/companion design.
- It should look like a professional animation production character sheet, not a poster and not a storyboard.

Layout requirements:
- Main hero/subject: front view, 3/4 view, side view, back view.
- Face/expression row: neutral, wonder, determination, action intensity, calm ending.
- Costume/prop callouts: key fabrics, accessories, tools, silhouette, scale.
- Companion/creature/vehicle/object design if implied by the story; include full body, head closeup, material/texture closeups, scale relation to hero.
- Palette chips and lighting notes.
- Small text labels are acceptable on the sheet, but keep the characters and objects large, clean, and reusable as references.
- Maintain one coherent visual style and avoid random alternate designs.

Story context:
{chr(10).join(beats)}"""


def _write_character_sheet_qa(payload: dict) -> None:
    try:
        (OUTPUT_DIR / "character_sheet_qa.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except Exception as e:
        log(f"character_sheet_qa.json 写入失败: {e}")


def generate_character_sheet_gpt_image2(script: list[dict], topic: str) -> dict | None:
    """Sidecar: GPT Image 2 model sheet for identity-locked character trailer shots."""
    flow_character_sheet = (
        STORYBOARD_GRID_MULTIREF_MAIN
        and _needs_storyboard_flow_character_sheet(script, topic)
    )
    adsd_character_sheet = (
        ADS_DIALOGUE_MODE
        and ADSD_LIP_SYNC_EXPERIMENT
        and os.environ.get("ADR_ADSD_CHARACTER_SHEET", "1").strip().lower() not in ("0", "false", "no", "off")
    )
    ads_character_sheet = (
        ADS_REPORTER_MODE
        and not ADS_DIALOGUE_MODE
        and ADS_CHARACTER_SHEET_REQUESTED
    )
    if not (CHARACTER_TRAILER_MODE or flow_character_sheet or adsd_character_sheet or ads_character_sheet):
        return None
    external = os.environ.get("ADR_CHARACTER_SHEET", "").strip()
    qa = {
        "mode": "gpt_image2_character_sheet",
        "enabled": True,
        "model": "GPT_IMAGE_2",
        "path": str(OUTPUT_DIR / "character_sheet.png"),
        "pass": False,
        "policy": "identity_reference_for_storyboard_flow_or_character_trailer_or_adsd_lip_sync_not_clean_panel_crop",
        "manual_visual_checks_required": [
            "recurring_character_identity_is_clear",
            "costume_palette_and_props_are_reusable",
            "adsd_speaker_roles_are_distinct_if_dialogue_mode",
            "creature_or_companion_design_is_consistent_if_present",
            "sheet_is_used_as_reference_not_rendered_in_final_video",
        ],
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }
    if external:
        qa["external_path"] = external
        if os.path.exists(external) and os.path.getsize(external) > 10000:
            target = OUTPUT_DIR / "character_sheet.png"
            try:
                from shutil import copyfile
                copyfile(external, target)
                qa.update({"path": str(target), "bytes": target.stat().st_size, "pass": True, "source": "external"})
            except Exception as e:
                qa.update({"reason": f"external_copy_failed:{e}"})
        else:
            qa.update({"reason": "external_character_sheet_missing"})
        _write_character_sheet_qa(qa)
        return qa
    aspect = os.environ.get("ADR_CHARACTER_SHEET_ASPECT", "").strip() or _storyboard_grid_aspect()
    qa["aspect_ratio"] = aspect
    try:
        prompt = _character_sheet_prompt(script, topic, aspect)
        if len(prompt) > 18000:
            prompt = prompt[:18000]
            qa.setdefault("warnings", []).append("prompt_truncated")
        r = submit_text_to_image({
            "model": "GPT_IMAGE_2",
            "prompt": prompt,
            "aspect_ratio": aspect,
            "image_number": 1,
            "quality": "high",
        }, "GPT Image 2 character sheet", timeout=45)
        task_id = (r.get("data", {}).get("task_ids") or [r.get("data", {}).get("task_id") or None])[0]
        qa["task_id"] = task_id
        if not task_id:
            qa.update({"reason": "submit_without_task_id", "response": r})
            return qa
        data = poll_storyboard_task(task_id, "GPT Image 2 character sheet", float(os.environ.get("ADR_CHARACTER_SHEET_POLL_MAX", "300")))
        urls = _extract_img_urls(data)
        if not urls:
            qa["reason"] = "succeed_without_image_url"
            return qa
        out_path = OUTPUT_DIR / "character_sheet.png"
        urllib.request.urlretrieve(urls[0], out_path)
        qa.update({
            "path": str(out_path),
            "bytes": out_path.stat().st_size if out_path.exists() else 0,
            "pass": out_path.exists() and out_path.stat().st_size > 100000,
        })
        if qa["pass"]:
            if adsd_character_sheet:
                target = "ADSD 口型/身份锁定"
            elif ads_character_sheet:
                target = "ADS 单人 POV 身份锁定（记者+受访者+道具跨镜一致）"
            elif flow_character_sheet:
                target = "storyboard flow 主路径身份锁定（character sheet + clean refs）"
            else:
                target = "逐镜身份锁定 trailer"
            tg(f"🧬 GPT Image 2 character sheet 已生成（用于{target}）")
        else:
            qa["reason"] = "output_too_small_or_missing"
    except Exception as e:
        qa.update({"pass": False, "reason": str(e)})
        tg(f"⚠️ character sheet 生成失败：{str(e)[:160]}")
    finally:
        _write_character_sheet_qa(qa)
    return qa


def generate_production_storyboard_page_gpt_image2(script: list[dict], topic: str) -> dict | None:
    """Sidecar: GPT Image 2 director-facing production board for trailer/previs."""
    if ADS_DIALOGUE_MODE or not STORYBOARD_TRAILER_MODE:
        return None
    aspect = os.environ.get("ADR_PRODUCTION_STORYBOARD_ASPECT", "").strip() or _storyboard_grid_aspect()
    qa = {
        "mode": "gpt_image2_production_storyboard_page",
        "enabled": True,
        "model": "GPT_IMAGE_2",
        "aspect_ratio": aspect,
        "requested_count": len(script),
        "path": str(OUTPUT_DIR / "production_storyboard_page.png"),
        "pass": False,
        "policy": "director_facing_board_for_short_trailer_not_for_clean_panel_crops",
        "manual_visual_checks_required": [
            "shot_order_is_readable",
            "cast_and_scene_design_are_consistent",
            "camera_motion_and_sfx_notes_are_present",
            "board_is_not_used_as_clean_longform_mainline_reference",
        ],
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }
    try:
        prompt = _production_storyboard_prompt(script, topic, aspect)
        if len(prompt) > 18000:
            prompt = prompt[:18000]
            qa.setdefault("warnings", []).append("prompt_truncated")
        r = submit_text_to_image({
            "model": "GPT_IMAGE_2",
            "prompt": prompt,
            "aspect_ratio": aspect,
            "image_number": 1,
            "quality": "high",
        }, "GPT Image 2 production storyboard page", timeout=45)
        task_id = (r.get("data", {}).get("task_ids") or [r.get("data", {}).get("task_id") or None])[0]
        qa["task_id"] = task_id
        if not task_id:
            qa.update({"reason": "submit_without_task_id", "response": r})
            return qa
        data = poll_storyboard_task(task_id, "GPT Image 2 production storyboard page", float(os.environ.get("ADR_PRODUCTION_STORYBOARD_POLL_MAX", "300")))
        urls = _extract_img_urls(data)
        if not urls:
            qa["reason"] = "succeed_without_image_url"
            return qa
        out_path = OUTPUT_DIR / "production_storyboard_page.png"
        urllib.request.urlretrieve(urls[0], out_path)
        qa.update({
            "path": str(out_path),
            "bytes": out_path.stat().st_size if out_path.exists() else 0,
            "pass": out_path.exists() and out_path.stat().st_size > 100000,
        })
        if qa["pass"]:
            tg("🧾 GPT Image 2 production storyboard page 已生成（用于 trailer/previs，不进长片 clean refs）")
        else:
            qa["reason"] = "output_too_small_or_missing"
    except Exception as e:
        qa.update({"pass": False, "reason": str(e)})
        tg(f"⚠️ production storyboard page 生成失败：{str(e)[:160]}")
    finally:
        _write_production_storyboard_page_qa(qa)
    return qa


def _qa_clean_storyboard_panel(path: Path) -> dict:
    """Lightweight QA for cropped grid panels before they become motion references."""
    qa = {
        "panel_qa": "clean_ref_crop",
        "pass": False,
        "issues": [],
    }
    try:
        from PIL import Image
        im = Image.open(path).convert("L")
        W, H = im.size
        qa["width"] = W
        qa["height"] = H
        if W != VIDEO_W or H != VIDEO_H:
            qa["issues"].append(f"size_mismatch:{W}x{H}")

        pix = im.load()

        def dark_ratio(box: tuple[int, int, int, int]) -> float:
            x1, y1, x2, y2 = box
            total = max(1, (x2 - x1) * (y2 - y1))
            dark = 0
            for y in range(y1, y2):
                for x in range(x1, x2):
                    if pix[x, y] < 8:
                        dark += 1
            return dark / total

        def bright_ratio(box: tuple[int, int, int, int]) -> float:
            x1, y1, x2, y2 = box
            total = max(1, (x2 - x1) * (y2 - y1))
            bright = 0
            for y in range(y1, y2):
                for x in range(x1, x2):
                    if pix[x, y] > 238:
                        bright += 1
            return bright / total

        def bright_component_summary(box: tuple[int, int, int, int]) -> dict:
            x1, y1, x2, y2 = box
            bw = max(1, x2 - x1)
            bh = max(1, y2 - y1)
            bright = bytearray(bw * bh)
            for yy, y in enumerate(range(y1, y2)):
                row = yy * bw
                for xx, x in enumerate(range(x1, x2)):
                    if pix[x, y] > 238:
                        bright[row + xx] = 1
            seen = bytearray(bw * bh)
            largest = 0
            marker_ratio = 0.0
            marker_aspect = 0.0
            marker_fill = 0.0
            for pos, val in enumerate(bright):
                if not val or seen[pos]:
                    continue
                stack = [pos]
                seen[pos] = 1
                size = 0
                min_x = bw
                min_y = bh
                max_x = 0
                max_y = 0
                while stack:
                    cur = stack.pop()
                    size += 1
                    cx = cur % bw
                    cy = cur // bw
                    min_x = min(min_x, cx)
                    min_y = min(min_y, cy)
                    max_x = max(max_x, cx)
                    max_y = max(max_y, cy)
                    for nx, ny in ((cx - 1, cy), (cx + 1, cy), (cx, cy - 1), (cx, cy + 1)):
                        if nx < 0 or ny < 0 or nx >= bw or ny >= bh:
                            continue
                        npos = ny * bw + nx
                        if bright[npos] and not seen[npos]:
                            seen[npos] = 1
                            stack.append(npos)
                largest = max(largest, size)
                comp_w = max(1, max_x - min_x + 1)
                comp_h = max(1, max_y - min_y + 1)
                area_ratio = size / max(1, bw * bh)
                aspect = max(comp_w / comp_h, comp_h / comp_w)
                fill = size / max(1, comp_w * comp_h)
                # Storyboard motion arrows are usually compact, thin, high-contrast marks.
                # Natural highlights in cups/windows/skin tend to be broad blobs or dense glare.
                if 0.0002 <= area_ratio <= 0.008 and aspect >= 2.2 and fill <= 0.5:
                    if area_ratio > marker_ratio:
                        marker_ratio = area_ratio
                        marker_aspect = aspect
                        marker_fill = fill
            total = max(1, bw * bh)
            return {
                "largest_ratio": largest / total,
                "marker_ratio": marker_ratio,
                "marker_aspect": marker_aspect,
                "marker_fill": marker_fill,
            }

        edge_h = max(8, int(H * 0.025))
        edge_w = max(8, int(W * 0.025))
        qa["top_black_ratio"] = round(dark_ratio((0, 0, W, edge_h)), 4)
        qa["bottom_black_ratio"] = round(dark_ratio((0, H - edge_h, W, H)), 4)
        qa["left_black_ratio"] = round(dark_ratio((0, 0, edge_w, H)), 4)
        qa["right_black_ratio"] = round(dark_ratio((W - edge_w, 0, W, H)), 4)
        corner_box = (0, 0, int(W * 0.14), int(H * 0.16))
        lower_center_box = (int(W * 0.25), int(H * 0.55), int(W * 0.75), H)
        corner_components = bright_component_summary(corner_box)
        lower_components = bright_component_summary(lower_center_box)
        qa["top_left_bright_ratio"] = round(bright_ratio(corner_box), 4)
        qa["top_left_bright_component_ratio"] = round(corner_components["largest_ratio"], 4)
        qa["lower_center_bright_ratio"] = round(bright_ratio(lower_center_box), 4)
        qa["lower_center_marker_component_ratio"] = round(lower_components["marker_ratio"], 4)
        qa["lower_center_marker_aspect"] = round(lower_components["marker_aspect"], 2)
        qa["lower_center_marker_fill"] = round(lower_components["marker_fill"], 2)
        small_w = 320
        small_h = max(1, int(round(small_w * H / max(W, 1))))
        small = im.resize((small_w, small_h))
        spix = small.load()
        vertical_separator_columns = []
        for x in range(int(small_w * 0.08), int(small_w * 0.92)):
            bright = 0
            dark = 0
            for y in range(int(small_h * 0.06), int(small_h * 0.94)):
                v = spix[x, y]
                if v > 242:
                    bright += 1
                elif v < 13:
                    dark += 1
            denom = max(1, int(small_h * 0.88))
            if max(bright, dark) / denom > 0.72:
                vertical_separator_columns.append(x)
        horizontal_separator_rows = []
        for y in range(int(small_h * 0.08), int(small_h * 0.92)):
            bright = 0
            dark = 0
            for x in range(int(small_w * 0.06), int(small_w * 0.94)):
                v = spix[x, y]
                if v > 242:
                    bright += 1
                elif v < 13:
                    dark += 1
            denom = max(1, int(small_w * 0.88))
            if max(bright, dark) / denom > 0.72:
                horizontal_separator_rows.append(y)

        def compact_runs(vals: list[int]) -> list[tuple[int, int]]:
            if not vals:
                return []
            runs = []
            start = prev = vals[0]
            for val in vals[1:]:
                if val <= prev + 1:
                    prev = val
                    continue
                runs.append((start, prev))
                start = prev = val
            runs.append((start, prev))
            return runs

        qa["interior_vertical_separator_runs"] = compact_runs(vertical_separator_columns)
        qa["interior_horizontal_separator_runs"] = compact_runs(horizontal_separator_rows)
        if min(qa["top_black_ratio"], qa["bottom_black_ratio"]) > 0.42:
            qa["issues"].append("possible_horizontal_letterbox")
        if min(qa["left_black_ratio"], qa["right_black_ratio"]) > 0.42:
            qa["issues"].append("possible_vertical_letterbox")
        if qa["interior_vertical_separator_runs"]:
            qa["issues"].append("possible_vertical_panel_separator_bleed")
        if qa["interior_horizontal_separator_runs"]:
            qa["issues"].append("possible_horizontal_panel_separator_bleed")
        if 0.002 <= qa["top_left_bright_component_ratio"] <= 0.09 and qa["top_left_bright_ratio"] > 0.015:
            qa["issues"].append("possible_shot_number_residue")
        if qa["lower_center_bright_ratio"] > 0.015 and qa["lower_center_marker_component_ratio"] > 0.0015:
            qa["issues"].append("possible_arrow_or_motion_marker_residue")
        qa["pass"] = not qa["issues"]
    except Exception as e:
        qa["issues"].append(f"qa_exception:{e}")
    return qa


def _crop_storyboard_grid_panels(grid_path: Path, batch_script: list[dict], start: int, cols: int, rows: int, qa_batch: dict) -> None:
    from PIL import Image, ImageOps
    im = Image.open(grid_path).convert("RGB")
    W, H = im.size
    cell_w = W / cols
    cell_h = H / rows
    inset_x = max(16, int(cell_w * float(os.environ.get("ADR_STORYBOARD_GRID_CROP_INSET_X", "0.075"))))
    inset_top = max(16, int(cell_h * float(os.environ.get("ADR_STORYBOARD_GRID_CROP_INSET_TOP", "0.16"))))
    inset_bottom = max(16, int(cell_h * float(os.environ.get("ADR_STORYBOARD_GRID_CROP_INSET_BOTTOM", "0.075"))))
    qa_batch["grid_width"] = W
    qa_batch["grid_height"] = H
    qa_batch["crop_inset_x"] = inset_x
    qa_batch["crop_inset_top"] = inset_top
    qa_batch["crop_inset_bottom"] = inset_bottom
    qa_batch["panel_records"] = []
    for local_i, scene in enumerate(batch_script):
        panel_idx = local_i
        row = panel_idx // cols
        col = panel_idx % cols
        left = int(col * cell_w) + inset_x
        top = int(row * cell_h) + inset_top
        right = int((col + 1) * cell_w) - inset_x
        bottom = int((row + 1) * cell_h) - inset_bottom
        crop_box = (left, top, right, bottom)
        crop = im.crop((left, top, right, bottom))
        target_w = VIDEO_W
        target_h = VIDEO_H
        canvas = ImageOps.fit(crop, (target_w, target_h), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))
        panel_path = Path(scene["img_path"])
        canvas.save(panel_path, "JPEG", quality=94, optimize=True)
        qa = _qa_clean_storyboard_panel(panel_path)
        scene["storyboard_grid_mode"] = True
        scene["storyboard_grid_source"] = str(grid_path)
        scene["storyboard_grid_panel"] = start + local_i + 1
        _render_still_segment(scene)
        qa_batch["panel_records"].append({
            "scene": start + local_i + 1,
            "row": row + 1,
            "col": col + 1,
            "crop_box": crop_box,
            "path": str(panel_path),
            "bytes": panel_path.stat().st_size if panel_path.exists() else 0,
            **qa,
            "pass": panel_path.exists() and panel_path.stat().st_size > 10000 and qa.get("pass"),
        })


def generate_storyboard_grid_gpt_image2(script: list[dict], topic: str) -> bool:
    """Optional 4K multi-shot storyboard grid path.

    It uses GPT_IMAGE_2 to make 4K grids, then crops clean panels into normal img_N references.
    This is a safer production primitive than feeding a whole grid directly into WERYDANCE.
    """
    if not GPT_IMAGE2_STORYBOARD_GRID:
        return False
    n = len(script)
    if n <= 0:
        return False
    max_n = int(os.environ.get("ADR_GPT_IMAGE2_STORYBOARD_GRID_MAX", "32"))
    if n > max_n:
        log(f"GPT Image 2 storyboard grid 跳过：分镜数 {n} 超过上限 {max_n}")
        return False
    aspect = _storyboard_grid_aspect()
    batch_size = max(1, min(16, int(os.environ.get("ADR_GPT_IMAGE2_STORYBOARD_GRID_BATCH", "12"))))
    prompt_limit = _storyboard_grid_prompt_limit()
    poll_max = float(os.environ.get("ADR_GPT_IMAGE2_STORYBOARD_GRID_POLL_MAX", "300"))
    submit_stagger_sec = max(0.0, float(os.environ.get("ADR_GPT_IMAGE2_STORYBOARD_GRID_SUBMIT_STAGGER", "12")))
    poll_workers = max(1, min(20, int(os.environ.get("ADR_GPT_IMAGE2_STORYBOARD_GRID_POLL_WORKERS", "20"))))
    qa = {
        "mode": "gpt_image2_storyboard_grid_4k",
        "enabled": True,
        "used": False,
        "model": "GPT_IMAGE_2",
        "aspect_ratio": aspect,
        "batch_size": batch_size,
        "prompt_limit": prompt_limit,
        "requested_count": n,
        "rendered_count": 0,
        "batches": [],
        "issues": [],
        "submit_stagger_sec": submit_stagger_sec,
        "poll_workers": poll_workers,
        "policy": "adaptive_multi_4k_grid_generate_then_crop_clean_panels_for_motion_refs",
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }
    try:
        batch_idx = 0
        passed_scenes: set[int] = set()

        def make_jobs(range_start: int, range_end: int, max_size: int, reason: str) -> list[dict]:
            jobs = []
            cur = range_start
            while cur < range_end:
                current_size = min(max(1, max_size), range_end - cur)
                while current_size >= 1:
                    end = min(range_end, cur + current_size)
                    batch_script = script[cur:end]
                    cols, rows = _storyboard_grid_cols_rows(len(batch_script))
                    prompt = _storyboard_grid_prompt(batch_script, cur, n, topic, cols, rows, aspect)
                    if len(prompt) > prompt_limit and current_size > 1:
                        next_size = max(1, current_size // 2)
                        qa.setdefault("adaptive_splits", []).append({
                            "scene_start": cur + 1,
                            "scene_end": end,
                            "from_size": current_size,
                            "to_size": next_size,
                            "reason": f"prompt_too_long:{len(prompt)}>{prompt_limit}",
                        })
                        current_size = next_size
                        continue
                    if len(prompt) > 10000:
                        prompt = prompt[:10000]
                        qa.setdefault("warnings", []).append(f"scene_{cur+1}_{end}_prompt_hard_truncated")
                    jobs.append({
                        "start": cur,
                        "end": end,
                        "batch_script": batch_script,
                        "cols": cols,
                        "rows": rows,
                        "prompt": prompt,
                        "reason": reason,
                    })
                    cur = end
                    break
                else:
                    raise RuntimeError(f"storyboard grid prompt split failed at scene {cur + 1}")
            return jobs

        def poll_and_materialize(entry: dict) -> tuple[dict, list[dict], list[int]]:
            batch_qa = entry["batch_qa"]
            job = entry["job"]
            task_id = batch_qa["task_id"]
            data = poll_storyboard_task(task_id, f"GPT Image 2 storyboard grid {batch_qa['batch']}", poll_max)
            urls = _extract_img_urls(data)
            if not urls:
                batch_qa["reason"] = "succeed_without_image_url"
                qa["issues"].append(f"batch_{batch_qa['batch']}_without_image_url")
                raise RuntimeError(batch_qa["reason"])
            grid_path = OUTPUT_DIR / f"storyboard_grid_{batch_qa['batch']:02d}.png"
            urllib.request.urlretrieve(urls[0], grid_path)
            batch_qa["grid_path"] = str(grid_path)
            batch_qa["grid_bytes"] = grid_path.stat().st_size if grid_path.exists() else 0
            _crop_storyboard_grid_panels(
                grid_path,
                job["batch_script"],
                job["start"],
                job["cols"],
                job["rows"],
                batch_qa,
            )
            rendered = sum(1 for r in batch_qa.get("panel_records", []) if r.get("pass"))
            materialized = sum(
                1
                for r in batch_qa.get("panel_records", [])
                if r.get("bytes", 0) > 10000
            )
            batch_qa["rendered_count"] = rendered
            batch_qa["materialized_count"] = materialized
            batch_qa["pass"] = rendered == len(job["batch_script"])
            if batch_qa["pass"]:
                return batch_qa, [], list(range(job["start"] + 1, job["end"] + 1))

            batch_qa["reason"] = "crop_incomplete"
            failed_panels = [
                {
                    "scene": r.get("scene"),
                    "issues": r.get("issues", []),
                    "crop_box": r.get("crop_box"),
                }
                for r in batch_qa.get("panel_records", [])
                if not r.get("pass")
            ]
            batch_qa["failed_panels"] = failed_panels
            current_size = job["end"] - job["start"]
            if current_size > 1:
                next_size = max(1, current_size // 2)
                batch_qa["retry_with_smaller_grid"] = next_size
                qa.setdefault("adaptive_splits", []).append({
                    "scene_start": job["start"] + 1,
                    "scene_end": job["end"],
                    "from_size": current_size,
                    "to_size": next_size,
                    "reason": "crop_incomplete_or_panel_bleed",
                    "failed_panels": failed_panels,
                })
                return batch_qa, make_jobs(job["start"], job["end"], next_size, "crop_retry"), []
            qa["issues"].append(f"batch_{batch_qa['batch']}_crop_incomplete")
            raise RuntimeError(f"storyboard grid batch {batch_qa['batch']} crop incomplete")

        pending_jobs = make_jobs(0, n, batch_size, "initial")
        wave_no = 0
        while pending_jobs:
            wave_no += 1
            qa.setdefault("waves", []).append({
                "wave": wave_no,
                "job_count": len(pending_jobs),
                "submit_stagger_sec": submit_stagger_sec,
            })
            submitted = []
            for job_i, job in enumerate(pending_jobs):
                batch_idx += 1
                batch_qa = {
                    "batch": batch_idx,
                    "wave": wave_no,
                    "scene_start": job["start"] + 1,
                    "scene_end": job["end"],
                    "grid": f"{job['cols']}x{job['rows']}",
                    "panel_count": len(job["batch_script"]),
                    "prompt_chars": len(job["prompt"]),
                    "submit_stagger_sec": submit_stagger_sec if job_i > 0 else 0.0,
                    "source_reason": job.get("reason"),
                    "task_id": None,
                    "pass": False,
                }
                qa["batches"].append(batch_qa)
                if job_i > 0 and submit_stagger_sec > 0:
                    log(f"GPT Image 2 storyboard grid 错峰提交等待 {submit_stagger_sec:.1f}s（{job_i+1}/{len(pending_jobs)}）")
                    time.sleep(submit_stagger_sec)
                r = submit_text_to_image({
                    "model": "GPT_IMAGE_2",
                    "prompt": job["prompt"],
                    "aspect_ratio": aspect,
                    "image_number": 1,
                    "quality": "high",
                }, f"GPT Image 2 storyboard grid {batch_idx}", timeout=45)
                task_id = (r.get("data", {}).get("task_ids") or [r.get("data", {}).get("task_id") or None])[0]
                batch_qa["task_id"] = task_id
                if not task_id:
                    batch_qa["reason"] = f"submit_without_task_id: {json.dumps(r, ensure_ascii=False)[:200]}"
                    current_size = job["end"] - job["start"]
                    if current_size > 1 and _is_prompt_limit_response(r):
                        next_size = max(1, current_size // 2)
                        batch_qa["retry_with_smaller_grid"] = next_size
                        qa.setdefault("adaptive_splits", []).append({
                            "scene_start": job["start"] + 1,
                            "scene_end": job["end"],
                            "from_size": current_size,
                            "to_size": next_size,
                            "reason": "api_prompt_limit",
                        })
                        submitted.extend({"job": retry_job, "batch_qa": None, "retry_without_task": True} for retry_job in make_jobs(job["start"], job["end"], next_size, "api_prompt_limit_retry"))
                        continue
                    qa["issues"].append(f"batch_{batch_idx}_submit_without_task_id")
                    raise RuntimeError(batch_qa["reason"])
                submitted.append({"job": job, "batch_qa": batch_qa})

            retry_jobs = [entry["job"] for entry in submitted if entry.get("retry_without_task")]
            poll_entries = [entry for entry in submitted if entry.get("batch_qa") and entry["batch_qa"].get("task_id")]
            if poll_entries:
                with ThreadPoolExecutor(max_workers=min(poll_workers, len(poll_entries))) as ex:
                    futs = [ex.submit(poll_and_materialize, entry) for entry in poll_entries]
                    for fut in as_completed(futs):
                        _batch_qa, more_retry_jobs, scenes = fut.result()
                        retry_jobs.extend(more_retry_jobs)
                        passed_scenes.update(scenes)
                        qa["rendered_count"] = len(passed_scenes)
            pending_jobs = retry_jobs
        qa["used"] = True
        qa["rendered_count"] = len(passed_scenes)
        qa["pass"] = qa["rendered_count"] == n
        tg(f"🧩 GPT Image 2 4K storyboard multi-grid 成功：{qa['rendered_count']}/{n} 格已裁成 clean refs（{batch_idx} 张 grid）")
        return qa["pass"]
    except Exception as e:
        qa["pass"] = False
        qa["issues"].append(str(e))
        log(f"GPT Image 2 storyboard grid 失败，回退单图 storyboard/逐张兜底：{e}")
        tg(f"⚠️ GPT Image 2 4K storyboard grid 重试后失败，自动回退单图 storyboard/逐张兜底：{str(e)[:160]}")
        return False
    finally:
        try:
            (OUTPUT_DIR / "storyboard_grid_qa.json").write_text(
                json.dumps(qa, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except Exception as e:
            log(f"storyboard_grid_qa.json 写入失败: {e}")


def _gpt_image2_direct_annotated_aspect() -> str:
    override = os.environ.get("ADR_GPT_IMAGE2_DIRECT_ANNOTATED_ASPECT", "").strip()
    if override:
        return override
    return "9:16(4k)" if IS_VERTICAL else "16:9(4k)"


def _gpt_image2_direct_annotated_prompt(scene: dict, idx: int, total: int, topic: str, aspect: str) -> str:
    visual = _short_board_text(scene.get("prompt") or scene.get("text"), 650)
    text = _short_board_text(scene.get("text"), 220)
    action = _short_board_text(scene.get("motion_action_beat") or visual, 160)
    camera = _short_board_text(scene.get("motion_camera") or "motivated camera move with foreground parallax and a clear action beat", 160)
    speed = _short_board_text(scene.get("motion_speed") or "medium", 40)
    sfx = _short_board_text(scene.get("motion_sfx") or "period ambience, cloth and object movement", 120)
    duration = int(round(max(1, float(scene.get("vid_duration") or scene.get("dur") or 5))))
    return f"""Create one single {aspect} high-resolution annotated cinematic storyboard board for a historical documentary shot.
Topic: {topic}
Shot: {idx + 1}/{total}
Visual source description: {visual}

Layout requirements:
- Output must be one finished director storyboard board, not multiple separate images.
- Use 4K-quality detail, crisp labels, clean typography, and professional film previsualization layout.
- Left/center: one large cinematic frame with the scene itself.
- Right side: a clean dark Director Notes panel with four short labeled sections: ACTION, CAMERA, DIALOGUE/VO, SFX.
- Top left: SHOT {idx + 1:02d} / {duration}s.
- Add one simple white camera direction arrow inside the image frame.
- Keep all text short, legible, and correctly spelled in English.
- No random extra text, no watermark, no logo, no comic panels, no contact sheet.

Director notes content:
ACTION: {action}
CAMERA: {camera}; speed {speed}.
DIALOGUE/VO: {_short_board_text(text, 120)}
SFX: {sfx}."""


def generate_gpt_image2_direct_annotated_storyboards(script: list[dict], topic: str) -> bool:
    """Optional 4K GPT_IMAGE_2 director boards for human QA only.

    These boards are intentionally not used as the default WERYDANCE reference because QA showed
    model-generated side panels can be preserved in the video. The motion path keeps using the
    programmatic board or clean keyframe.
    """
    if ADS_DIALOGUE_MODE or not GPT_IMAGE2_DIRECT_ANNOTATED_STORYBOARD:
        return False
    n = len(script)
    if n <= 0:
        return False
    max_n = max(1, int(os.environ.get("ADR_GPT_IMAGE2_DIRECT_ANNOTATED_MAX", "6")))
    take_n = min(n, max_n)
    aspect = _gpt_image2_direct_annotated_aspect()
    poll_max = float(os.environ.get("ADR_GPT_IMAGE2_DIRECT_ANNOTATED_POLL_MAX", "300"))
    qa = {
        "mode": "gpt_image2_direct_annotated_storyboard_4k",
        "enabled": True,
        "used": False,
        "model": "GPT_IMAGE_2",
        "aspect_ratio": aspect,
        "requested_count": take_n,
        "total_scene_count": n,
        "motion_input_allowed": False,
        "policy": "human_QA_director_board_only_not_default_werydance_input",
        "records": [],
        "issues": [],
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }
    try:
        for i, scene in enumerate(script[:take_n]):
            prompt = _gpt_image2_direct_annotated_prompt(scene, i, n, topic, aspect)
            if len(prompt) > 18000:
                prompt = prompt[:18000]
                qa.setdefault("warnings", []).append(f"scene_{i+1}_prompt_truncated")
            r = submit_text_to_image({
                "model": "GPT_IMAGE_2",
                "prompt": prompt,
                "aspect_ratio": aspect,
                "image_number": 1,
                "quality": "high",
            }, f"GPT Image 2 direct annotated storyboard {i+1}/{take_n}", timeout=45)
            task_id = (r.get("data", {}).get("task_ids") or [r.get("data", {}).get("task_id") or None])[0]
            rec = {
                "scene": i + 1,
                "task_id": task_id,
                "path": None,
                "pass": False,
            }
            qa["records"].append(rec)
            if not task_id:
                rec["reason"] = f"submit_without_task_id: {json.dumps(r, ensure_ascii=False)[:200]}"
                qa["issues"].append(f"scene_{i+1}_submit_without_task_id")
                continue
            data = poll_storyboard_task(
                task_id,
                f"GPT Image 2 direct annotated storyboard {i+1}/{take_n}",
                poll_max,
            )
            urls = _extract_img_urls(data)
            if not urls:
                rec["reason"] = "succeed_without_image_url"
                qa["issues"].append(f"scene_{i+1}_without_image_url")
                continue
            out_path = OUTPUT_DIR / f"annotated_storyboard_direct_{i}.png"
            urllib.request.urlretrieve(urls[0], out_path)
            rec["path"] = str(out_path)
            rec["bytes"] = out_path.stat().st_size if out_path.exists() else 0
            try:
                from PIL import Image
                with Image.open(out_path) as im:
                    rec["width"], rec["height"] = im.size
                    rec["resolution_pass"] = (im.size[1] >= 3840 if IS_VERTICAL else im.size[0] >= 3840)
            except Exception as e:
                rec["resolution_error"] = str(e)
                rec["resolution_pass"] = False
            rec["pass"] = bool(rec.get("bytes", 0) > 10000 and rec.get("resolution_pass"))
            scene["direct_annotated_storyboard_path"] = str(out_path)
        passed = sum(1 for r in qa["records"] if r.get("pass"))
        qa["used"] = passed > 0
        qa["pass"] = passed == take_n
        qa["pass_count"] = passed
        tg(f"🎞 GPT Image 2 4K annotated storyboard 看板完成：{passed}/{take_n}（仅QA看板，不直喂WERYDANCE）")
        return bool(qa["used"])
    except Exception as e:
        qa["pass"] = False
        qa["issues"].append(str(e))
        log(f"GPT Image 2 4K annotated storyboard 看板失败: {e}")
        tg(f"⚠️ GPT Image 2 4K annotated storyboard 看板失败：{str(e)[:160]}")
        return False
    finally:
        try:
            (OUTPUT_DIR / "direct_annotated_storyboard_qa.json").write_text(
                json.dumps(qa, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except Exception as e:
            log(f"direct_annotated_storyboard_qa.json 写入失败: {e}")


def _llm_bgm_description(topic: str, tone: str) -> str | None:
    """LLM 主路径：根据主题+基调直接产出 BGM 英文 prompt。失败/质量异常返回 None，由调用方退回硬编码。"""
    prompt = f"""为纪录片配乐生成 weryai 音乐 API 的英文 prompt（25-45 词）。

主题：{topic}
情感基调：{tone}

要求：
1. 必须包含 3-5 件具体乐器（如 low strings, muted piano, distant timpani, military snare, accordion）
2. 必须包含 2-3 个情绪关键词（如 solemn, restrained, contemplative, melancholic, triumphant, hopeful, tense, reverent）
3. 体现题材时代感（如 "1920s archival" / "post-WWI" / "Tang dynasty courtly" / "modern tech"），但不要直接抄具体片名/导演名
4. 严禁人声/合唱/lyrics
5. 不要包含 "starting at peak energy / minimal intro / no vocals"——这些由代码追加
6. 纯英文一行，无引号、无 Markdown、无解释

参考样式（仅供 vibe 参考，不要照抄措辞）：
- 历史悲剧：Solemn reflective documentary score, slow strings and piano, distant funeral march, restrained mournful atmosphere, 1920s archival cold
- 1919 战后：Restrained post-WWI score, low strings muted piano distant military snare, newspaper-press rhythm, cold archival grave
- 怀旧 80 年代：Nostalgic warm instrumental, solo piano harmonica accordion music box, slow waltz tempo, sentimental tender
- 航天史诗：Heroic epic orchestral, grand strings brass choir timpani, triumphant uplifting cosmic, cinematic exploration

直接输出英文描述（一行）："""
    try:
        out = chat("GEMINI_3_1_FLASH_LITE", "你是纪录片配乐导演，精通电影配乐风格与乐器编排。", prompt, max_tokens=1000, timeout=45).strip()
        out = out.strip('"').strip("'").strip()
        out = out.split('\n')[0].strip()
        word_count = len(out.split())
        if word_count < 12 or word_count > 80:
            log(f"BGM LLM 输出长度异常（{word_count} 词），退回硬编码")
            return None
        if not re.search(r'[a-zA-Z]', out):
            log("BGM LLM 输出无英文，退回硬编码")
            return None
        return out
    except Exception as e:
        log(f"BGM LLM 描述生成失败: {e}，退回硬编码")
        return None


def generate_bgm(topic: str, tone: str = "中性") -> str | None:
    bgm_path = str(OUTPUT_DIR / "bgm.mp3")
    MAX_BGM_RETRY = 3
    SUFFIX = ", starting directly at peak energy with minimal intro, no vocals"

    # 主路径：LLM 直接生成描述（覆盖任意长尾主题）
    llm_desc = _llm_bgm_description(topic, tone)
    if llm_desc:
        bgm_desc = f"{llm_desc}{SUFFIX}"
        log(f"BGM 描述: LLM ({len(llm_desc.split())} 词) → {llm_desc[:120]}...")
    elif tone == "轻松":
        bgm_desc = f"Cheerful upbeat children's background music for '{topic}', ukulele marimba glockenspiel whistle claps, warm playful hopeful mood, light and bouncy, family-friendly, starting directly at peak energy with minimal intro, no vocals"
    elif tone == "怀旧":
        bgm_desc = f"Nostalgic warm instrumental soundtrack for '{topic}', solo piano and harmonica and accordion and music box, slow waltz tempo, sentimental tender mood, like memories of 1980s China, starting directly at peak energy with minimal intro, no vocals"
    elif tone == "庄重":
        bgm_desc = f"Solemn reflective documentary soundtrack for '{topic}', slow strings and piano, restrained reverent atmosphere, starting directly at peak energy with minimal intro, no vocals"
    else:  # 中性 → 按主题关键词细分
        if is_1919_global_topic(topic):
            bgm_desc = (
                f"Restrained post World War I 1919 historical documentary score for '{topic}', "
                "low strings, muted piano, distant military snare, newspaper-press rhythm, cold archival atmosphere, "
                "grave but not triumphant, no guzheng, no erhu, no festive Chinese folk instruments, no heroic propaganda march, "
                "starting directly with a tense pulse and minimal intro, no vocals"
            )
            log("BGM 细分: 1919战后民族觉醒")
        elif any(k in topic for k in ("航天", "太空", "卫星", "火箭", "东方红", "神舟", "嫦娥", "北斗", "天宫", "宇宙", "星辰")):
            bgm_desc = f"Heroic epic orchestral soundtrack for '{topic}', grand strings brass choir and timpani, triumphant uplifting mood, space exploration cinematic like Interstellar and Apollo, starting directly at peak energy with minimal intro, no vocals"
            log("BGM 细分: 航天史诗")
        elif any(k in topic for k in ("AI", "人工智能", "科技", "互联网", "算法", "机器人", "智能")):
            bgm_desc = f"Modern cinematic electronic soundtrack for '{topic}', synth pad deep bass subtle percussion, futuristic thoughtful mood, tech documentary style, starting directly at peak energy with minimal intro, no vocals"
            log("BGM 细分: 科技未来")
        elif any(k in topic for k in ("读书", "书单", "书香", "文学", "文化", "诗词", "典籍", "阅读")):
            bgm_desc = f"Gentle contemplative piano soundtrack for '{topic}', solo piano with soft violin strings, bookish quiet reflective mood, literary documentary style, starting directly at peak energy with minimal intro, no vocals"
            log("BGM 细分: 文学书香")
        elif any(k in topic for k in ("历史", "朝代", "古代", "千年", "诞辰", "周年", "纪念")):
            bgm_desc = f"Warm cinematic historical soundtrack for '{topic}', piano strings and subtle Chinese elements, reflective dignified mood, history documentary style, starting directly at peak energy with minimal intro, no vocals"
            log("BGM 细分: 历史纪录")
        elif any(k in topic for k in ("美食", "旅行", "民俗", "节日", "风物")):
            bgm_desc = f"Upbeat acoustic soundtrack for '{topic}', acoustic guitar soft percussion, cheerful warm mood, lifestyle documentary, starting directly at peak energy with minimal intro, no vocals"
            log("BGM 细分: 生活风物")
        else:
            bgm_desc = f"Gentle contemplative Chinese documentary soundtrack for '{topic}', erhu guzheng pipa soft strings, calm thoughtful atmosphere, starting directly at peak energy with minimal intro, no vocals"
            log("BGM 细分: 默认传统纪录")
    for attempt in range(1, MAX_BGM_RETRY + 1):
        try:
            log(f"BGM 生成尝试 {attempt}/{MAX_BGM_RETRY}（tone={tone}）")
            r = req_post("/generation/music/generate", {
                "type":        "ONLY_MUSIC",
                "description": bgm_desc,
            }, timeout=30)
            if not r.get("success") and r.get("status", 1) != 0:
                log(f"BGM 提交失败: {r}")
                continue
            data = poll(r["data"]["task_id"], "BGM")
            bgm_url = (data.get("audios") or [None])[0]
            if not bgm_url:
                log("BGM URL 为空，重试...")
                continue
            urllib.request.urlretrieve(bgm_url, bgm_path)
            # 后处理：截掉前 intro，直奔高潮 + 加 1s fade-in（视频通常 < 60s，前奏浪费时长）
            try:
                _total = ffprobe_duration(bgm_path)
                if _total >= 30:
                    _skip = min(20.0, _total * 0.3)
                    _out = bgm_path + ".climax.mp3"
                    ffmpeg(
                        "-ss", str(_skip), "-i", bgm_path,
                        "-af", "afade=t=in:st=0:d=1",
                        "-c:a", "libmp3lame", "-q:a", "4",
                        _out,
                    )
                    import shutil
                    shutil.move(_out, bgm_path)
                    log(f"BGM 截掉前 {_skip:.1f}s intro（总 {_total:.1f}s），直奔高潮")
            except Exception as _e:
                log(f"BGM 截 intro 失败（保留原 BGM）：{_e}")
            if os.path.exists(bgm_path) and os.path.getsize(bgm_path) > 10000:
                tg(f"🎵 BGM 生成完毕 ✓（第{attempt}次尝试）")
                return bgm_path
            else:
                log("BGM 文件异常（不存在或太小），重试...")
                continue
        except Exception as e:
            log(f"BGM 生成失败（尝试 {attempt}）: {e}")
            if attempt < MAX_BGM_RETRY:
                import time as _t; _t.sleep(5)
            continue
    log("BGM 3次重试均失败")
    return None


def step6_parallel(script: list[dict], topic: str, pregenerated_bgm_path: str | None = None) -> str | None:
    _ensure_motion_action_plan(script)
    _write_motion_action_plan_qa(script)
    n = len(script)
    _approval_note = "图片生成即审批" if not SKIP_APPROVAL else "免审批"
    # storyboard_grid 启用时: 1 张 grid 4K 大图切 n panel + character_sheet + motion_bridge_refs
    # fallback: n 张单独 generate_image
    if GPT_IMAGE2_STORYBOARD_GRID:
        _gen_brief = f"storyboard grid (切 {n} panel) + character_sheet + motion_bridge_refs"
    else:
        _gen_brief = f"{n} 张图片"
    if pregenerated_bgm_path:
        tg(f"🚀 并行生成：{_gen_brief}（{_approval_note}，复用 BGM-driven 已生成音乐）...")
    else:
        tg(f"🚀 并行生成：{_gen_brief} + BGM（{_approval_note}，BGM 后台同步跑）...")

    MAX_REDO = 3
    bgm_tone = script[0].get("tone", "中性") if script else "中性"
    media_workers = max(2, min(20, int(os.environ.get("ADR_MEDIA_WORKERS", "20"))))
    # BGM 后台启动，不阻塞审批
    with ThreadPoolExecutor(max_workers=media_workers) as ex:
        bgm_fut = None if pregenerated_bgm_path else ex.submit(generate_bgm, topic, bgm_tone)

        completed = {}  # idx -> True
        approval_sent = set()  # 已推过审批的 idx，避免兜底重发
        generate_character_sheet_gpt_image2(script, topic)
        generate_production_storyboard_page_gpt_image2(script, topic)
        storyboard_used = generate_storyboard_grid_gpt_image2(script, topic) or generate_storyboard_images_gpt_image2(script, topic)
        if storyboard_used:
            completed = {i: True for i in range(n)}
            generate_motion_bridge_refs_gpt_image2(script, topic)
            if not SKIP_APPROVAL:
                for idx in range(n):
                    _send_for_approval(script[idx]["img_path"], idx, script[idx])
                    approval_sent.add(idx)
        else:
            # 图片：每张生成完立刻审批，不等全部完成
            img_futs = {ex.submit(generate_image, s, i): i for i, s in enumerate(script)}

            # ★ 每张图生成完立即推审批（不等所有 22 张完成才统一推）
            # SKIP_APPROVAL 模式跳过推送
            for f in as_completed(img_futs):
                idx = img_futs[f]
                try:
                    f.result()
                    completed[idx] = True
                    # ★ 立即推审批（图刚出来就让大哥审）
                    if not SKIP_APPROVAL:
                        _send_for_approval(script[idx]["img_path"], idx, script[idx])
                        approval_sent.add(idx)
                except Exception as e:
                    tg(f"⚠️ 图片 {idx+1} 生成失败：{e}")
                    completed[idx] = False

        # 检查是否有图片缺失 → 用最近成功的图兜底（审核拦截/其他失败都不再 raise 崩管线）
        missing = [i for i in range(n) if not completed.get(i)]
        if missing:
            import shutil
            for idx in missing:
                # 找最近的成功图（双向扫描）
                fallback_idx = None
                for offset in range(1, n):
                    for cand in (idx - offset, idx + offset):
                        if 0 <= cand < n and completed.get(cand):
                            fallback_idx = cand
                            break
                    if fallback_idx is not None:
                        break
                if fallback_idx is None:
                    raise RuntimeError(f"所有图片都失败，管线无法继续")
                src = str(OUTPUT_DIR / f"img_{fallback_idx}.jpg")
                dst = str(OUTPUT_DIR / f"img_{idx}.jpg")
                try:
                    shutil.copy(src, dst)
                    _render_still_segment(script[idx])
                    log(f"[fallback] img_{idx} 被审核/失败，复用 img_{fallback_idx} 兜底")
                    tg(f"⚠️ 图 {idx+1} 被审核拦截或失败，复用图 {fallback_idx+1} 兜底继续（主题建议避开敏感书名/人名/符号）")
                    completed[idx] = True
                    # ★ 兜底图也补推审批（如果之前没推过）
                    if not SKIP_APPROVAL and idx not in approval_sent:
                        _send_for_approval(dst, idx, script[idx])
                        approval_sent.add(idx)
                except Exception as e:
                    raise RuntimeError(f"图 {idx+1} 兜底失败: {e}")

        if not storyboard_used:
            generate_motion_bridge_refs_gpt_image2(script, topic)

        generate_gpt_image2_direct_annotated_storyboards(script, topic)
        if script:
            alignment_qa = _write_text_visual_alignment_qa(script)
            if alignment_qa.get("failed_count"):
                tg(
                    f"⚠️ 台词-分镜绑定 QA 提醒：{alignment_qa.get('failed_count')}/{alignment_qa.get('total')} 镜疑似不匹配，"
                    f"场次 {alignment_qa.get('failed_scenes')}；已记录 text_visual_alignment_qa.json"
                )
            _write_cultural_visual_qa(script, script[0].get("topic_meta", {}))
            _write_adsd_gender_voice_qa(script)

        # ── 审批流程 ────────────────────────────────────────────────────
        if SKIP_APPROVAL:
            # ★ v0.2 智能异常检测：用 Gemini Vision 批量审 22 张图
            # 免审核模式下只提醒和记录，不进入人工审批等待；人工审批只由 --with-approval 启用。
            tg(f"🔍 智能异常检测：Vision 扫描 {n} 张图...")
            anomaly_idxs = _llm_check_scenes_anomalies(script)
            qa_path = OUTPUT_DIR / "scene_qa.json"
            qa_payload = {
                "mode": ADSD_MODE_NAME if ADS_DIALOGUE_MODE else ("VDAR" if IS_VERTICAL else "HDAR"),
                "total": n,
                "anomaly_indices": sorted(int(i) for i in anomaly_idxs),
                "anomaly_scene_numbers": sorted(int(i) + 1 for i in anomaly_idxs),
                "policy": "warn_only_skip_approval",
                "created_at": datetime.now().isoformat(timespec="seconds"),
            }
            try:
                qa_path.write_text(json.dumps(qa_payload, ensure_ascii=False, indent=2), encoding="utf-8")
            except Exception as e:
                log(f"scene_qa.json 写入失败: {e}")
            if anomaly_idxs:
                mode_name = ADSD_MODE_NAME if ADS_DIALOGUE_MODE else ("VDAR" if IS_VERTICAL else "HDAR")
                tg(
                    f"⚠️ {mode_name} 场景 QA 提醒：Vision 标记 {len(anomaly_idxs)} 张疑似异常 "
                    f"{sorted(i+1 for i in anomaly_idxs)}，已记录 {qa_path.name}；免审核模式不等待人工确认，继续合成"
                )
            else:
                tg(f"✅ 场景 QA：全部 {n} 张未发现严重异常，自动进入合成阶段")
            bgm_path = pregenerated_bgm_path
            if bgm_path:
                tg(f"🎵 BGM-driven 复用 BGM: {bgm_path}")
            else:
                try:
                    bgm_path = bgm_fut.result(timeout=180)
                    if bgm_path:
                        tg(f"🎵 BGM 就绪: {bgm_path}")
                    else:
                        tg("⚠️ BGM generate_bgm 返回 None，尝试兜底...")
                        fallback = str(OUTPUT_DIR / "bgm.mp3")
                        if os.path.exists(fallback) and os.path.getsize(fallback) > 10000:
                            bgm_path = fallback
                            tg(f"🎵 BGM 兜底成功: {fallback}")
                        else:
                            tg("❌ BGM 兜底失败：文件不存在或太小")
                except Exception as e:
                    log(f"BGM 失败: {e}")
                    tg(f"⚠️ BGM future 异常: {e}，尝试兜底...")
                    fallback = str(OUTPUT_DIR / "bgm.mp3")
                    if os.path.exists(fallback) and os.path.getsize(fallback) > 10000:
                        bgm_path = fallback
                        tg(f"🎵 BGM 兜底成功: {fallback}")
                    else:
                        tg("❌ BGM 完全失败，视频将无背景音乐")
            return bgm_path

        # ★ 审批已在 as_completed 循环中每张图完成时即推（含兜底图），无需统一重发
        tg(f"📋 {n} 张图片已陆续推审批，等待你确认（每张 5 分钟超时自动通过）...")

        # ── 并行等待审批结果，被拒的后台重做再审 ─────────────────────────
        approved_set = set()
        redo_count = {i: 0 for i in range(n)}       # 同 prompt 重做次数
        prompt_rewrite_count = {i: 0 for i in range(n)}  # prompt 重写次数
        MAX_PROMPT_REWRITE = 2
        regen_futs = {}  # idx -> Future

        while len(approved_set) < n:
            time.sleep(2)
            for i in range(n):
                if i in approved_set:
                    continue

                # 如果正在重做，检查重做是否完成
                if i in regen_futs:
                    fut = regen_futs[i]
                    if not fut.done():
                        continue
                    try:
                        fut.result()
                        _send_for_approval(script[i]["img_path"], i, script[i])
                    except Exception as e:
                        tg(f"⚠️ 图 {i+1} 重做失败：{e}")
                    del regen_futs[i]
                    continue

                # 检查审批结果
                if (APPROVAL_DIR / f"{i}.approved").exists():
                    approved_set.add(i)
                    tg(f"✅ 图 {i+1}/{n} 已通过（{len(approved_set)}/{n}）")
                elif (APPROVAL_DIR / f"{i}.rejected").exists():
                    (APPROVAL_DIR / f"{i}.rejected").unlink(missing_ok=True)
                    redo_count[i] += 1

                    if redo_count[i] <= MAX_REDO:
                        # 同 prompt 重做
                        tg(f"🔄 图 {i+1}/{n} 被拒绝，同 prompt 重做（第 {redo_count[i]} 次）...")
                        regen_futs[i] = ex.submit(generate_image, script[i], i)
                    elif prompt_rewrite_count[i] < MAX_PROMPT_REWRITE:
                        # prompt 重写
                        prompt_rewrite_count[i] += 1
                        redo_count[i] = 0  # 重置重做计数
                        tg(f"✏️ 图 {i+1}/{n} 同 prompt {MAX_REDO} 次不过，重写提示词（第 {prompt_rewrite_count[i]} 次）...")
                        try:
                            hist = script[i].get("historical_context", "")
                            tone_active = script[i].get("tone", "中性")
                            almanac_active = get_almanac_data(topic) is not None
                            if almanac_active:
                                style_req = "中国传统美术风格，工笔画或水墨画质感，暖色调"
                            elif tone_active == "轻松":
                                style_req = "明亮鲜艳的卡通/插画风格，高饱和暖色调，阳光感、治愈系、适合儿童"
                            else:
                                style_req = "写实老照片风格，sepia tone"
                            if hist:
                                hist_block = f"【制片人准则（最高优先级，必须严格遵循）】\n{hist}\n\n"
                                ref_req = "• 严格遵守制片人准则中的 STYLE_KEY / PALETTE / LIGHTING_AND_CAMERA / SUBJECT_DETAILS / TABOOS，不得越界\n"
                            else:
                                hist_block = ""
                                ref_req = "• 场景与人物描述必须与台词内容直接相关\n"
                            new_prompt = chat("GEMINI_25_FLASH", "你是画面导演，只输出英文。",
                                f"上一个画面提示词生成的图片不符合要求，请重写一个完全不同的画面提示词。\n\n"
                                f"台词：{script[i]['text']}\n"
                                f"情绪：{script[i]['emotion']}\n"
                                f"旧提示词：{script[i]['prompt']}\n\n"
                                f"{hist_block}"
                                f"要求：\n"
                                f"• 50~80 词英文，{style_req}\n"
                                f"• 换一个完全不同的构图/视角/场景\n"
                                f"{ref_req}"
                                f"只输出提示词本身。")
                            script[i]["prompt"] = new_prompt.strip()
                            tg(f"✏️ 图 {i+1} 新提示词就绪，重新生成...")
                            regen_futs[i] = ex.submit(generate_image, script[i], i)
                        except Exception as e:
                            tg(f"⚠️ 图 {i+1} 提示词重写失败：{e}")
                    else:
                        tg(f"⚠️ 图 {i+1}/{n} 已重写 {MAX_PROMPT_REWRITE} 次提示词仍不过，强制通过")
                        approved_set.add(i)

            # 超时保护：总审批时间不超过 10 分钟
            # (由 _wait_approval 的单张超时 + 这里的循环共同保证)

        tg(f"✅ 全部 {n} 张图片审批完成")

        # 等 BGM（审批期间 BGM 已在后台跑完了）
        bgm_path = pregenerated_bgm_path
        if bgm_path:
            tg(f"🎵 BGM-driven 复用 BGM: {bgm_path}")
        else:
            try:
                bgm_path = bgm_fut.result(timeout=180)
                if bgm_path:
                    tg(f"🎵 BGM 就绪: {bgm_path}")
                else:
                    tg("⚠️ BGM generate_bgm 返回 None，尝试兜底...")
                    fallback = str(OUTPUT_DIR / "bgm.mp3")
                    if os.path.exists(fallback) and os.path.getsize(fallback) > 10000:
                        bgm_path = fallback
                        tg(f"🎵 BGM 兜底成功: {fallback}")
            except Exception as e:
                log(f"BGM 失败: {e}")
                tg(f"⚠️ BGM future 异常: {e}，尝试兜底...")
                fallback = str(OUTPUT_DIR / "bgm.mp3")
                if os.path.exists(fallback) and os.path.getsize(fallback) > 10000:
                    bgm_path = fallback
                    tg(f"🎵 BGM 兜底成功: {fallback}")

    return bgm_path


# ── 第 6.5 步：动态化（可选，--with-motion 开启）─────────────────────────────
# 把每个静态 seg_N.mp4 替换为 WERYDANCE_2_0 生成的带镜头运动的短视频
# 原则：per-scene 失败不中断，保留静态 seg 作为兜底
def _generate_motion_prompts(script: list[dict]) -> list[str]:
    """用 Gemini 为每个分镜生成英文 motion 描述（40-60 词）"""
    n = len(script)
    reporter_motion_guide = """
- ADS reporter mode is ON: make every motion feel like 1910s field-correspondent footage.
- Prefer handheld newsreel sway, first-person POV movement, shoulder-level walking, quick rack focus to telegram sheets, reporter notebook, newspaper extra, trench parapet, dock smoke, telephone switchboard.
- Use period-appropriate motion only; no smartphone livestream, no TV studio camera, no modern microphone, no LED screen.
- Keep it immersive but historically plausible: a staged dispatch/newsreel, not a real modern live broadcast.
""" if ADS_REPORTER_MODE else ""
    adsd_motion_guide = f"""
- ADSD dialogue mode is ON: each scene has one active speaker. Motion must keep the active speaker visually dominant for that turn.
- Support monologue, two-person dialogue, or ensemble scenes. Use medium close-up, over-the-shoulder, or group reaction timing according to the scene, while keeping the current active speaker unambiguous.
- {"Lip-sync experiment is ON: keep the mouth area visible and imply subtle natural lip movement, but avoid exaggerated dubbing or distorted teeth." if ADSD_LIP_SYNC_EXPERIMENT else "Production default: do not promise exact lip-sync; keep speaker focus stable with readable face, hands, documents, and listener reaction."}
{"- Onsite POV mode is ON: make the viewer feel physically present beside the speaker or at the crowd/door/table edge; judge immersion by the whole scene, not by fixed keywords." if ADSD_ONSITE_POV_MODE else ""}
""" if ADS_DIALOGUE_MODE else ""
    try:
        summary_lines = "\n".join(
            f"{i+1}. ({sc.get('dur', 5):.0f}s, speaker: {sc.get('speaker', '旁白')}, emotion: {sc.get('emotion', 'neutral')}) "
            f"{sc['text'][:80]} | {_motion_action_block(sc, 260)}"
            for i, sc in enumerate(script)
        )
        raw = chat(
            "GEMINI_25_FLASH",
            "You are an action-oriented cinematographer giving motion direction for still documentary frames. Output strict JSON only.",
            f"""Generate {n} motion prompts for a Chinese documentary. Each scene already has a static keyframe image; describe camera movement plus one clear in-frame action beat (40-60 words, English).

Scene summary:
{summary_lines}

Rules:
- Do not make every shot a slow zoom. Avoid overusing "slow", "gentle", "subtle", and "calm".
- Each prompt must include a dominant action verb: steps, turns, raises, draws, strikes, opens, points, kneels, reacts, rushes, crosses, reveals, or similar.
- Use a motivated camera move: handheld push, tracking move, whip-pan, rack focus, low-angle orbit, reveal, pull-back, parallax slide, or dolly move.
- Follow the Motion plan embedded in each scene summary; do not replace it with generic drifting or breathing motion.
- Match emotion: tense → sharper moves and faster reactions; reflective → controlled but still active; calm → restrained action, not static.
- Keep identities and costumes stable; action must be plausible from one keyframe and should not require a full choreography reset.
- End with ", cinematic atmosphere, smooth motion" for consistency.
- Do NOT describe what's in the frame (that's already fixed).
{reporter_motion_guide}
{adsd_motion_guide}

Output strict JSON array of {n} strings:
["motion1", "motion2", ...]"""
        )
        import re as _re
        m = _re.search(r'\[[\s\S]+\]', raw)
        if m:
            prompts = json.loads(m.group())
            if isinstance(prompts, list) and len(prompts) == n:
                return prompts
        log(f"motion prompts 数量不匹配: got {len(prompts) if 'prompts' in dir() else '?'}, need {n}")
    except Exception as e:
        log(f"motion prompts 生成失败: {e}")
    # 兜底：所有 scene 用通用 prompt
    fallback = [
        "handheld push-in with a clear foreground parallax slide as the main figure turns or raises a hand, cloth and dust reacting to the movement, quick rack focus to the key prop, cinematic atmosphere, smooth motion",
        "tracking move from side to front while the subject steps forward, gestures, or reacts decisively, background elements shift with visible depth, brief focus pull and controlled camera sway, cinematic atmosphere, smooth motion",
        "low-angle dolly-in followed by a short orbit as hands, fabric, smoke, or papers move with the action beat, the frame feels motivated and alive without changing identity, cinematic atmosphere, smooth motion",
        "pull-back reveal from a tight detail to the full scene while the character crosses frame or changes posture, secondary figures or environment respond naturally, cinematic atmosphere, smooth motion",
    ]
    return [fallback[i % len(fallback)] for i in range(n)]


_motion_tasks_lock = threading.Lock()
_motion_qa_lock = threading.Lock()


def _motion_tasks_file() -> Path:
    return OUTPUT_DIR / "motion_tasks.json"


def _motion_qa_file() -> Path:
    return OUTPUT_DIR / "motion_qa.json"


def _append_motion_qa(record: dict) -> None:
    """Append one motion-generation QA event without racing parallel workers."""
    payload = {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "storyboard_reference_motion_enabled": STORYBOARD_REFERENCE_MOTION,
        "storyboard_annotated_motion_enabled": STORYBOARD_ANNOTATED_MOTION,
        "records": [],
    }
    with _motion_qa_lock:
        p = _motion_qa_file()
        if p.exists():
            try:
                loaded = json.loads(p.read_text(encoding="utf-8"))
                if isinstance(loaded, dict):
                    payload.update(loaded)
                    payload.setdefault("records", [])
            except Exception:
                payload.setdefault("warnings", []).append("previous_motion_qa_unreadable")
        record = dict(record)
        record.setdefault("timestamp", datetime.now().isoformat(timespec="seconds"))
        payload["records"].append(record)
        p.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _finalize_motion_qa(total: int, success_count: int) -> None:
    with _motion_qa_lock:
        p = _motion_qa_file()
        payload = {
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "storyboard_reference_motion_enabled": STORYBOARD_REFERENCE_MOTION,
            "storyboard_annotated_motion_enabled": STORYBOARD_ANNOTATED_MOTION,
            "records": [],
        }
        if p.exists():
            try:
                loaded = json.loads(p.read_text(encoding="utf-8"))
                if isinstance(loaded, dict):
                    payload.update(loaded)
                    payload.setdefault("records", [])
            except Exception:
                payload.setdefault("warnings", []).append("motion_qa_finalize_read_failed")
        records = payload.get("records") or []
        reference_success = sum(1 for r in records if r.get("path") == "image-to-video" and r.get("pass"))
        annotated_success = sum(1 for r in records if r.get("reference_mode") == "annotated_storyboard" and r.get("pass"))
        text_success = sum(1 for r in records if r.get("path") == "text-to-video" and r.get("pass"))
        generated_audio_success = sum(
            1 for r in records
            if r.get("pass") and r.get("video_has_audio") and r.get("generated_audio_from_prompt_dialogue")
        )
        voice_timbre_manual_required = sum(
            1 for r in records
            if r.get("pass") and r.get("path") == "almighty-reference-audio-dub" and not r.get("voice_timbre_auto_verified")
        )
        werydance_caption_success = sum(
            1 for r in records
            if r.get("pass") and r.get("werydance_captions_requested") and not r.get("ass_fallback_required")
        )
        embedded_voice_audio_ready = generated_audio_success == total and generated_audio_success > 0
        embedded_voice_audio_partial_ready = (
            VOICE_ASSET_AUDIO_DUB_PARTIAL_OK
            and total > 0
            and generated_audio_success > 0
            and generated_audio_success / max(total, 1) >= VOICE_ASSET_AUDIO_DUB_MIN_COVERAGE
        )
        payload.update({
            "total": total,
            "success_count": success_count,
            "success_rate": round(success_count / max(total, 1), 4),
            "reference_success_count": reference_success,
            "annotated_reference_success_count": annotated_success,
            "text_fallback_success_count": text_success,
            "generated_audio_segment_count": generated_audio_success,
            "embedded_voice_audio_ready": embedded_voice_audio_ready,
            "embedded_voice_audio_partial_ready": embedded_voice_audio_partial_ready,
            "embedded_voice_audio_coverage": round(generated_audio_success / max(total, 1), 4),
            "motion_action_storyboard_enabled": MOTION_ACTION_STORYBOARD,
            "motion_visual_qa_enabled": MOTION_VISUAL_QA,
            "motion_visual_min_score": MOTION_VISUAL_MIN_SCORE,
            "motion_visual_sample_fps": MOTION_VISUAL_SAMPLE_FPS,
            "motion_visual_ignore_bottom_ratio": MOTION_VISUAL_IGNORE_BOTTOM_RATIO,
            "voice_timbre_auto_verification": "not_available",
            "voice_timbre_manual_required_count": voice_timbre_manual_required,
            "voice_repair_enabled": MOTION_VOICE_REPAIR,
            "voice_repair_turns": sorted(_load_motion_voice_repair_turns()) if MOTION_VOICE_REPAIR else [],
            "voice_strict_lock_prompt_enabled": MOTION_VOICE_STRICT_LOCK,
            "werydance_captions_enabled": WERYDANCE_CAPTIONS,
            "werydance_caption_segment_count": werydance_caption_success,
            "ass_caption_fallback_count": max(0, total - werydance_caption_success) if WERYDANCE_CAPTIONS else total,
            "voice_asset_audio_dub_experiment": VOICE_ASSET_AUDIO_DUB_EXPERIMENT,
            "voice_asset_audio_dub_partial_ok": VOICE_ASSET_AUDIO_DUB_PARTIAL_OK,
            "voice_asset_audio_dub_min_coverage": VOICE_ASSET_AUDIO_DUB_MIN_COVERAGE,
            "default_voice_assets": {
                "male": DEFAULT_MALE_VOICE_ASSET,
                "female": DEFAULT_FEMALE_VOICE_ASSET,
                "default": DEFAULT_VOICE_ASSET or None,
            },
            "static_fallback_count": max(0, total - success_count),
            "pass": success_count >= max(1, math.ceil(total * 0.7)),
            "policy": "voice_asset_audio_dub_first_clean_keyframe_image_to_video_text_to_video_static_last",
            "master_audio_mux_required": not (embedded_voice_audio_ready or embedded_voice_audio_partial_ready),
            "finalized_at": datetime.now().isoformat(timespec="seconds"),
        })
        p.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


_lip_sync_tasks_lock = threading.Lock()


def _lip_sync_tasks_file() -> Path:
    return OUTPUT_DIR / "lip_sync_tasks.json"


def _load_motion_tasks() -> dict:
    p = _motion_tasks_file()
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_motion_task(idx: int, task_id: str):
    """线程安全地持久化某个分镜的 task_id（覆盖已有值）"""
    with _motion_tasks_lock:
        tasks = _load_motion_tasks()
        tasks[str(idx)] = task_id
        _motion_tasks_file().write_text(json.dumps(tasks, ensure_ascii=False, indent=2), encoding="utf-8")


def _remove_motion_task(idx: int):
    with _motion_tasks_lock:
        tasks = _load_motion_tasks()
        tasks.pop(str(idx), None)
        _motion_tasks_file().write_text(json.dumps(tasks, ensure_ascii=False, indent=2), encoding="utf-8")


def _load_lip_sync_tasks() -> dict:
    p = _lip_sync_tasks_file()
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_lip_sync_task(idx: int, task_id: str):
    with _lip_sync_tasks_lock:
        tasks = _load_lip_sync_tasks()
        tasks[str(idx)] = task_id
        _lip_sync_tasks_file().write_text(json.dumps(tasks, ensure_ascii=False, indent=2), encoding="utf-8")


def _remove_lip_sync_task(idx: int):
    with _lip_sync_tasks_lock:
        tasks = _load_lip_sync_tasks()
        tasks.pop(str(idx), None)
        _lip_sync_tasks_file().write_text(json.dumps(tasks, ensure_ascii=False, indent=2), encoding="utf-8")


def _video_visual_motion_qa(path: str) -> dict:
    qa = {
        "enabled": MOTION_VISUAL_QA,
        "sample_fps": MOTION_VISUAL_SAMPLE_FPS,
        "sample_width": MOTION_VISUAL_SAMPLE_WIDTH,
        "ignore_bottom_ratio": MOTION_VISUAL_IGNORE_BOTTOM_RATIO,
        "min_score": MOTION_VISUAL_MIN_SCORE,
        "sample_frames": 0,
        "score": None,
        "p90_score": None,
        "pass": True,
        "issues": [],
    }
    if not MOTION_VISUAL_QA:
        return qa
    if not os.path.exists(path) or os.path.getsize(path) < 10000:
        qa.update({"pass": False})
        qa["issues"].append("missing_or_too_small")
        return qa
    w, h = ffprobe_video_size(path)
    if not w or not h:
        qa.update({"pass": False})
        qa["issues"].append("missing_video_dimensions")
        return qa
    sample_w = MOTION_VISUAL_SAMPLE_WIDTH
    sample_h = max(36, int(round(sample_w * h / max(1, w))))
    usable_h = max(1, int(sample_h * (1.0 - MOTION_VISUAL_IGNORE_BOTTOM_RATIO)))
    frame_size = sample_w * sample_h
    max_frames = max(8, min(90, MOTION_VISUAL_SAMPLE_FPS * 18))
    try:
        proc = subprocess.run(
            [
                "ffmpeg", "-v", "error", "-i", path,
                "-vf", f"fps={MOTION_VISUAL_SAMPLE_FPS},scale={sample_w}:{sample_h},format=gray",
                "-frames:v", str(max_frames),
                "-f", "rawvideo", "-",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=90,
        )
    except Exception as e:
        qa.update({"pass": False})
        qa["issues"].append(f"motion_probe_failed:{e}")
        return qa
    raw = proc.stdout or b""
    frames = [raw[i:i + frame_size] for i in range(0, len(raw) - frame_size + 1, frame_size)]
    qa["sample_frames"] = len(frames)
    if len(frames) < 2:
        qa.update({"pass": False, "score": 0.0, "p90_score": 0.0})
        qa["issues"].append("insufficient_motion_frames")
        return qa
    usable_size = sample_w * usable_h
    diffs = []
    for prev, cur in zip(frames, frames[1:]):
        total = 0
        for row in range(usable_h):
            start = row * sample_w
            end = start + sample_w
            total += sum(abs(a - b) for a, b in zip(prev[start:end], cur[start:end]))
        diffs.append(total / usable_size)
    diffs.sort()
    score = sum(diffs) / len(diffs) if diffs else 0.0
    p90 = diffs[min(len(diffs) - 1, int(len(diffs) * 0.9))] if diffs else 0.0
    qa["score"] = round(score, 3)
    qa["p90_score"] = round(p90, 3)
    if score < MOTION_VISUAL_MIN_SCORE:
        qa["pass"] = False
        qa["issues"].append(f"visual_motion_too_low:{score:.3f}<min:{MOTION_VISUAL_MIN_SCORE:.3f}")
    return qa


def _motion_output_qa(path: str, target_dur: float | None = None) -> dict:
    qa = {
        "path": path,
        "exists": os.path.exists(path),
        "bytes": os.path.getsize(path) if os.path.exists(path) else 0,
        "width": None,
        "height": None,
        "duration": None,
        "duration_delta": None,
        "decode_pass": False,
        "pass": False,
        "issues": [],
    }
    if not qa["exists"]:
        qa["issues"].append("missing_file")
        return qa
    if qa["bytes"] < 10000:
        qa["issues"].append("file_too_small")
    w, h = ffprobe_video_size(path)
    qa["width"], qa["height"] = w, h
    if not w or not h:
        qa["issues"].append("missing_video_dimensions")
    elif w != VIDEO_W or h != VIDEO_H:
        qa["issues"].append(f"unexpected_dimensions:{w}x{h}_target:{VIDEO_W}x{VIDEO_H}")
    try:
        dur = ffprobe_duration(path)
        qa["duration"] = round(dur, 3)
        if target_dur is not None:
            qa["duration_delta"] = round(abs(dur - target_dur), 3)
            if abs(dur - target_dur) > 0.35:
                qa["issues"].append(f"duration_mismatch:{dur:.3f}_target:{target_dur:.3f}")
    except Exception as e:
        qa["issues"].append(f"duration_probe_failed:{e}")
    qa["decode_pass"] = _video_decode_probe(path)
    if not qa["decode_pass"]:
        qa["issues"].append("decode_probe_failed")
    visual_motion = _video_visual_motion_qa(path)
    qa["visual_motion"] = visual_motion
    qa["visual_motion_score"] = visual_motion.get("score")
    if not visual_motion.get("pass", True):
        qa["issues"].extend(f"visual_{x}" for x in visual_motion.get("issues", []))
    qa["pass"] = not qa["issues"]
    return qa


def _has_audio_stream(path: str) -> bool:
    try:
        probe = subprocess.check_output([
            "ffprobe", "-v", "error", "-select_streams", "a",
            "-show_entries", "stream=codec_type", "-of", "json", path,
        ], stderr=subprocess.DEVNULL)
        return bool(json.loads(probe.decode()).get("streams"))
    except Exception:
        return False


def _normalize_motion_video(src_path: str, dst_path: str, target_dur: float) -> dict:
    qa = {
        "source": src_path,
        "target": dst_path,
        "target_duration": round(float(target_dur), 3),
        "source_duration": None,
        "postprocess_pass": False,
        "issues": [],
    }
    if not os.path.exists(src_path) or os.path.getsize(src_path) < 10000:
        qa["issues"].append("source_missing_or_too_small")
        return qa
    try:
        src_dur = ffprobe_duration(src_path)
        qa["source_duration"] = round(src_dur, 3)
    except Exception as e:
        qa["issues"].append(f"source_duration_probe_failed:{e}")
        return qa
    tmp_out = dst_path + ".normalized.mp4"
    pad = max(0.0, float(target_dur) - src_dur)
    vf = (
        f"scale={VIDEO_W}:{VIDEO_H}:force_original_aspect_ratio=increase,"
        f"crop={VIDEO_W}:{VIDEO_H},setsar=1"
    )
    if pad > 0.04:
        vf += f",tpad=stop_mode=clone:stop_duration={pad:.3f}"
    vf += f",trim=duration={float(target_dur):.3f},setpts=PTS-STARTPTS"
    try:
        ffmpeg(
            "-i", src_path,
            "-vf", vf,
            "-an",
            "-c:v", "libx264", "-crf", "20", "-preset", "medium",
            "-pix_fmt", "yuv420p",
            tmp_out,
            timeout=180,
        )
    except Exception as e:
        qa["issues"].append(f"ffmpeg_normalize_failed:{e}")
        return qa
    out_qa = _motion_output_qa(tmp_out, target_dur)
    qa["output_qa"] = out_qa
    if not out_qa.get("pass"):
        qa["issues"].extend(f"output_{x}" for x in out_qa.get("issues", []))
        return qa
    os.replace(tmp_out, dst_path)
    qa["postprocess_pass"] = True
    return qa


def _motion_poll_and_download(idx: int, task_id: str, vid_path: str, target_dur: float | None = None) -> bool:
    """对已有 task_id 轮询 → 下载 → 替换。超时不删持久化记录（下次重跑可复用）"""
    # 先看任务当前状态（不必等 5s）
    err_counts = {}  # {错误类型: 次数}
    for iteration in range(121):
        try:
            s = req_get(f"/generation/{task_id}/status")
        except Exception as e:
            # P2: 不再静默吞；但为避免刷屏，同类错误聚合汇报
            key = type(e).__name__ + ":" + str(e)[:80]
            err_counts[key] = err_counts.get(key, 0) + 1
            if err_counts[key] in (1, 10, 50, 100):  # 第 1/10/50/100 次时 log
                log(f"[motion {idx}] req_get 异常 第 {err_counts[key]} 次: {key}")
            time.sleep(5)
            continue
        st = s.get("data", {}).get("task_status", "")
        if st == "succeed":
            vid_url = _extract_video_url(s.get("data", {}))
            if not vid_url:
                log(f"[motion {idx}] 成功但无视频 URL")
                return False
            tmp_path = vid_path + ".motion.mp4"
            try:
                urllib.request.urlretrieve(vid_url, tmp_path)
            except Exception as e:
                log(f"[motion {idx}] 下载异常: {e}")
                return False
            if os.path.exists(tmp_path) and os.path.getsize(tmp_path) > 10000:
                if target_dur is None:
                    os.replace(tmp_path, vid_path)
                    _remove_motion_task(idx)  # 成功后清记录
                    return True
                normalize_qa = _normalize_motion_video(tmp_path, vid_path, target_dur)
                if normalize_qa.get("postprocess_pass"):
                    _remove_motion_task(idx)  # 成功后清记录
                    return True
                log(f"[motion {idx}] 输出 QA/归一化失败: {json.dumps(normalize_qa, ensure_ascii=False)[:500]}")
                return False
            log(f"[motion {idx}] 下载文件异常（<10KB）")
            return False
        if st == "failed":
            log(f"[motion {idx}] WERYDANCE failed: {s}")
            _remove_motion_task(idx)  # 任务永久失败，下次不必重查
            return False
        # 其他状态（waiting/processing）继续 poll
        time.sleep(5)
    # 超时：保留 task_id，下次 rerun 可复用查询
    log(f"[motion {idx}] 轮询 10min 超时 · task_id={task_id}（已持久化到 motion_tasks.json，下次可复用）")
    return False


def _build_motion_video_prompt(scene: dict, motion_prompt: str, safe_retry: bool = False) -> str:
    action_block = _motion_action_block(scene, 520)
    if ADS_DIALOGUE_MODE:
        speaker = scene.get("speaker", "")
        contract = _adsd_visual_contract(speaker)
        shot = scene.get("shot", "")
        if safe_retry or not ADSD_RICH_MOTION_PROMPT:
            role = f"onsite historical character labelled {speaker}" if speaker else "onsite speaker"
            pov = " First-person onsite observer POV, viewer stands beside the speaker or at the crowd edge." if ADSD_ONSITE_POV_MODE else ""
            return (
                "Neutral period spoken scene with one or more adult historical onsite characters, "
                f"active {role} is clearly speaking while any other characters only listen or react. "
                f"{action_block}. Natural light, realistic motion.{pov} "
                "Keep the scene immersive for its topic era, no famous style, no branded references, no movie references, no text, no logos, no watermark."
            )
        return (
            "Historically grounded period dialogue scene, neutral archival realism, "
            "warm sepia paper tones, period clothing and topic-accurate props. "
            f"{contract}. "
            f"Scene action: {shot}. "
            f"{action_block}. "
            f"Camera motion: {motion_prompt}. "
            "Avoid branded style references, artist names, movie-title references, copyrighted characters, modern devices, subtitles, logos, watermarks."
        )
    scene_prompt = scene.get("prompt", "")
    if scene_prompt:
        return f"{scene_prompt}. {action_block}. Camera motion: {motion_prompt}"
    return f"{action_block}. Camera motion: {motion_prompt}" if action_block else motion_prompt


def _short_board_text(value: object, limit: int = 170) -> str:
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 3)].rstrip() + "..."


def _wrap_board_text(draw, text: str, font, max_width: int, max_lines: int) -> list[str]:
    if not text:
        return []
    tokens = text.split(" ")
    if len(tokens) <= 1:
        tokens = list(text)
        joiner = ""
    else:
        joiner = " "
    lines: list[str] = []
    current = ""
    for token in tokens:
        candidate = token if not current else current + joiner + token
        bbox = draw.textbbox((0, 0), candidate, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current = candidate
            continue
        if current:
            lines.append(current)
        current = token
        if len(lines) >= max_lines:
            break
    if current and len(lines) < max_lines:
        lines.append(current)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
    if lines and len(lines) == max_lines and len("".join(tokens)) > len("".join(lines)):
        lines[-1] = lines[-1].rstrip(". ") + "..."
    return lines


def _storyboard_font(size: int, bold: bool = False):
    from PIL import ImageFont
    paths = [
        "/System/Library/Fonts/STHeiti Medium.ttc" if bold else "/System/Library/Fonts/Hiragino Sans GB.ttc",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
    ]
    for path in paths:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            pass
    return ImageFont.load_default()


def _draw_storyboard_arrow(draw, frame_box: tuple[int, int, int, int]) -> None:
    x1, y1, x2, y2 = frame_box
    sx = x1 + int((x2 - x1) * 0.64)
    sy = y1 + int((y2 - y1) * 0.24)
    ex = x1 + int((x2 - x1) * 0.50)
    ey = y1 + int((y2 - y1) * 0.42)
    draw.line([(sx, sy), (ex, ey)], fill=(255, 255, 255, 230), width=max(5, (x2 - x1) // 210))
    head = max(18, (x2 - x1) // 55)
    draw.polygon(
        [(ex, ey), (ex + head, ey - head // 3), (ex + head // 3, ey + head)],
        fill=(255, 255, 255, 230),
    )


def _build_annotated_storyboard_reference(scene: dict, idx: int, motion_prompt: str, dur: int) -> str:
    """Create an experimental director board; production motion uses clean keyframes by default."""
    if not STORYBOARD_ANNOTATED_MOTION or ADS_DIALOGUE_MODE:
        return scene.get("img_path", "")
    img_path = scene.get("img_path")
    if not img_path or not os.path.exists(img_path):
        return img_path or ""
    out_path = str(OUTPUT_DIR / f"annotated_storyboard_{idx}.png")
    try:
        from PIL import Image, ImageDraw
        src = Image.open(img_path).convert("RGB")
        W, H = src.size
        board = Image.new("RGB", (W, H), (246, 246, 242))
        draw = ImageDraw.Draw(board)
        margin = max(24, W // 44)
        top_h = max(70, int(H * 0.075))
        right_w = max(360, int(W * 0.22))
        gutter = max(18, W // 110)
        frame_x1 = margin
        frame_y1 = top_h
        frame_x2 = W - margin - right_w - gutter
        frame_y2 = H - margin
        frame_w = frame_x2 - frame_x1
        frame_h = frame_y2 - frame_y1
        src_copy = src.copy()
        src_copy.thumbnail((frame_w, frame_h), Image.Resampling.LANCZOS)
        ox = frame_x1 + (frame_w - src_copy.size[0]) // 2
        oy = frame_y1 + (frame_h - src_copy.size[1]) // 2
        draw.rectangle([frame_x1 - 4, frame_y1 - 4, frame_x2 + 4, frame_y2 + 4], fill=(18, 18, 18))
        board.paste(src_copy, (ox, oy))
        draw.rectangle([ox, oy, ox + src_copy.size[0], oy + src_copy.size[1]], outline=(255, 255, 255), width=max(2, W // 520))
        _draw_storyboard_arrow(draw, (ox, oy, ox + src_copy.size[0], oy + src_copy.size[1]))

        title_font = _storyboard_font(max(26, W // 46), bold=True)
        label_font = _storyboard_font(max(20, W // 70), bold=True)
        body_font = _storyboard_font(max(18, W // 92))
        small_font = _storyboard_font(max(15, W // 120))
        slate = f"SHOT {idx + 1:02d} / {dur}s"
        draw.text((margin, max(14, top_h // 4)), slate, fill=(20, 20, 20), font=title_font)
        header = "ADR DIRECTOR BOARD"
        hb = draw.textbbox((0, 0), header, font=label_font)
        draw.text((W - margin - right_w + (right_w - (hb[2] - hb[0])) // 2, max(18, top_h // 3)), header, fill=(80, 80, 80), font=label_font)

        panel_x1 = W - margin - right_w
        panel_x2 = W - margin
        panel_y1 = top_h
        panel_y2 = H - margin
        draw.rounded_rectangle(
            [panel_x1, panel_y1, panel_x2, panel_y2],
            radius=max(10, W // 180),
            fill=(18, 18, 18),
        )
        draw.text((panel_x1 + 24, panel_y1 + 24), "DIRECTOR NOTES", fill=(245, 245, 238), font=label_font)
        draw.text((panel_x1 + 24, panel_y1 + 24 + max(26, W // 70)), "read as instructions, not final pixels", fill=(150, 150, 142), font=small_font)

        text_x = panel_x1 + 24
        y = panel_y1 + max(92, int(H * 0.085))
        max_w = right_w - 48
        rows = [
            ("ACTION", _short_board_text(scene.get("motion_action_beat") or scene.get("prompt") or scene.get("text"), 210), 3),
            ("CAMERA", _short_board_text(scene.get("motion_camera") or motion_prompt, 210), 3),
            ("SPEED", _short_board_text(scene.get("motion_speed") or "medium", 80), 1),
            ("DIALOGUE/VO", _short_board_text(scene.get("text"), 150), 2),
            ("SFX", _short_board_text(scene.get("motion_sfx") or "period ambience, crowd bed, cloth and paper movement", 180), 2),
        ]
        card_gap = max(14, H // 90)
        for label, value, max_lines in rows:
            label_h = draw.textbbox((0, 0), label, font=label_font)[3]
            lines = _wrap_board_text(draw, value, body_font, max_w, max_lines)
            line_step = max(32, int(H * 0.028))
            card_h = max(96, 28 + label_h + 12 + len(lines) * line_step + 18)
            draw.rounded_rectangle(
                [panel_x1 + 14, y, panel_x2 - 14, y + card_h],
                radius=max(7, W // 260),
                fill=(35, 35, 35),
                outline=(78, 78, 72),
                width=1,
            )
            draw.text((text_x, y + 14), label, fill=(245, 245, 238), font=label_font)
            ty = y + 14 + max(28, int(H * 0.035))
            for line in lines:
                draw.text((text_x, ty), line, fill=(220, 220, 210), font=body_font)
                ty += line_step
            y += card_h + card_gap

        footer = "VISUAL SOURCE = CENTER FRAME"
        fb = draw.textbbox((0, 0), footer, font=small_font)
        draw.text(
            (panel_x1 + (right_w - (fb[2] - fb[0])) // 2, panel_y2 - max(36, H // 34)),
            footer,
            fill=(145, 145, 138),
            font=small_font,
        )
        board.save(out_path, "PNG", optimize=True)
        scene["annotated_storyboard_path"] = out_path
        return out_path
    except Exception as e:
        log(f"[motion {idx}] annotated storyboard 生成失败，改用 clean keyframe: {e}")
        return img_path


def _plain_caption_text(scene: dict) -> str:
    text = re.sub(r"\s+", "", str(scene.get("text") or "")).strip()
    speaker = str(scene.get("speaker") or "").strip()
    if speaker:
        text = re.sub(rf"^{re.escape(speaker)}[：:]", "", text).strip()
    return text


def _werydance_caption_request(scene: dict) -> dict:
    text = _plain_caption_text(scene)
    info = {
        "enabled": WERYDANCE_CAPTIONS,
        "requested": False,
        "text": text,
        "max_chars": WERYDANCE_CAPTION_MAX_CHARS,
        "ass_fallback_required": True,
        "reason": "",
    }
    if not WERYDANCE_CAPTIONS:
        info["reason"] = "disabled"
        return info
    if not text:
        info["reason"] = "empty_text"
        return info
    if len(text) > WERYDANCE_CAPTION_MAX_CHARS:
        info["reason"] = f"text_too_long:{len(text)}>{WERYDANCE_CAPTION_MAX_CHARS}"
        return info
    info.update({
        "requested": True,
        "ass_fallback_required": False,
        "reason": "eligible_short_caption",
    })
    return info


def _werydance_caption_instruction(scene: dict) -> str:
    info = _werydance_caption_request(scene)
    if not info.get("requested"):
        return " No subtitles, no captions, no text overlay, no written dialogue."
    caption = str(info.get("text") or "")
    return (
        " Add one bottom-centered Chinese subtitle exactly: "
        f"「{caption}」. Keep it readable for the full shot, white text with a subtle dark shadow, "
        "inside the title-safe lower area. Do not add any other text, labels, watermarks, or logos."
    )


def _werydance_negative_prompt(scene: dict) -> str:
    if _werydance_caption_request(scene).get("requested"):
        return "watermark, logo, extra text, misspelled text, garbled characters, duplicate captions"
    # 强化：WERYDANCE 模型偶尔会自作主张在画面下方烧中文字幕，跟我们的 ASS 字幕双重叠
    # 用多重否定关键词压制 (single negative prompt 力度不够，扩到所有 text-related artifact)
    return (
        "no subtitles, no captions, no on-screen text, no burned-in text, no Chinese subtitles, "
        "no English subtitles, no text overlay, no caption bar, no chyron, no lower-third graphic, "
        "no speech bubbles, no thought bubbles, no signage text, no UI labels, no character name tags, "
        "no watermark, no logo, no studio mark, no copyright mark, "
        "no random Chinese characters anywhere in the frame, no garbled glyphs, no floating text"
    )


def _motion_reference_prompt(scene: dict, motion_prompt: str, safe_retry: bool = False, annotated: bool = False) -> str:
    base = _build_motion_video_prompt(scene, motion_prompt, safe_retry=safe_retry)
    if annotated:
        prefix = (
            "Read the uploaded annotated storyboard as a director board. Use the central frame as "
            "the visual reference for character identity, costume, era, composition, lighting, and "
            "scene geography. Treat the right-side director notes, arrows, camera labels, action notes, "
            "dialogue/VO, and SFX as production instructions only. The final video must be only the "
            "cinematic scene, not a storyboard page; remove or ignore all side panels, borders, labels, "
            "arrows, notes, and UI text. "
        )
    else:
        prefix = (
            "Use the uploaded storyboard frame as the strict visual reference for character identity, "
            "costume, era, composition, lighting, and scene geography. Add a clear motivated action beat "
            "and camera move that can plausibly start from this frame; do not redesign the shot. "
        )
    suffix = _werydance_caption_instruction(scene) + (
        " No storyboard annotations. Preserve faces, clothing, props, color palette, and historical setting from the reference image."
    )
    return (prefix + base[: max(0, 2000 - len(prefix) - len(suffix))] + suffix)[:2000]


def _motion_audio_dub_prompt(scene: dict, motion_prompt: str, safe_retry: bool = False, strict_voice: bool = False) -> str:
    narration = re.sub(r"\s+", " ", str(scene.get("text") or "")).strip()[:260]
    visual = _build_motion_video_prompt(scene, motion_prompt, safe_retry=safe_retry)
    caption_instruction = _werydance_caption_instruction(scene)
    voice_lock = (
        "Voice lock is mandatory: match the uploaded reference speaker's timbre, gender impression, pitch range, pace, breath, and delivery style as closely as possible. "
        "Do not substitute a generic narrator or a different speaker. "
        if strict_voice else ""
    )
    if safe_retry:
        prompt = (
            "Create a realistic Chinese documentary video from the uploaded image. "
            "Use the uploaded audio only as a voice timbre and speaking-style reference, then generate new Mandarin narration. "
            f"{voice_lock}"
            f"Speak exactly this Chinese line and nothing else: 「{narration}」. "
            "The narration may be off-screen unless a clear speaker is visible. "
            "Visible motion is mandatory: include a readable body, object, or camera movement beat; do not output a static portrait, freeze-frame, or only lip/subtitle movement. "
        )
        return (prompt[: max(0, 1000 - len(caption_instruction) - 24)] + caption_instruction + " No logos or watermarks.")[:1000]
    prompt = (
        "Create a cinematic Chinese documentary shot with generated voice audio. "
        "Use the uploaded image as the strict visual reference for era, character identity, costume, composition, lighting, and geography. "
        "Use the uploaded audio only as a lawful voice/timbre reference: preserve tone color, gender impression, pace, and delivery style; do not use it as music. "
        f"{voice_lock}"
        f"Generate clear Mandarin narration speaking exactly this line and nothing else: 「{narration}」. "
        "If no speaker face is visible, treat the voice as off-screen narration; if a speaker is visible, keep mouth motion natural and understated. "
        "Visible visual motion is mandatory: the subject, a prop, machinery, crowd, or the camera must complete a clear start-middle-end movement beat. "
        "Do not create a static talking-photo, freeze-frame, or a shot where only subtitles or mouth pixels change. "
        f"Camera/action instruction: {visual}. "
    )
    tail = caption_instruction + " No on-screen labels, logos, watermarks, or storyboard pages."
    return (prompt[: max(0, 2000 - len(tail))] + tail)[:2000]


def _motion_audio_dub_poll_and_download(idx: int, task_id: str, scene: dict, target_dur: float) -> tuple[bool, dict]:
    info = {
        "turn": idx + 1,
        "task_id": task_id,
        "source_audio": scene.get("_motion_reference_audio"),
        "source_audio_role": scene.get("_motion_reference_audio_role") or "voice_asset_reference",
        "voice_asset_reference": scene.get("_motion_voice_asset_reference"),
        "target_duration": round(target_dur, 3),
        "pass": False,
    }
    err_counts = {}
    for iteration in range(121):
        try:
            s = req_get(f"/generation/{task_id}/status")
        except Exception as e:
            key = type(e).__name__ + ":" + str(e)[:80]
            err_counts[key] = err_counts.get(key, 0) + 1
            if err_counts[key] in (1, 10, 50, 100):
                log(f"[motion-audio-dub {idx}] req_get 异常 第 {err_counts[key]} 次: {key}")
            time.sleep(5)
            continue
        data = s.get("data", {})
        st = data.get("task_status", "")
        if iteration == 0 or iteration % 12 == 0 or st in ("succeed", "failed"):
            log(f"[motion-audio-dub {idx}] poll #{iteration+1}: {st}")
        if st == "succeed":
            vid_url = _extract_video_url(data)
            if not vid_url:
                info.update({"reason": "succeed_without_video_url", "response": data})
                return False, info
            raw_path = str(OUTPUT_DIR / f"motion_audio_dub_raw_{idx}.mp4")
            try:
                urllib.request.urlretrieve(vid_url, raw_path)
            except Exception as e:
                info.update({"reason": f"download_failed: {e}"})
                return False, info
            if not os.path.exists(raw_path) or os.path.getsize(raw_path) < 10000:
                info.update({"reason": "download_file_too_small"})
                return False, info
            ok = _postprocess_audio_dub_segment(raw_path, scene, target_dur)
            output_qa = _motion_output_qa(scene["vid_path"], target_dur) if ok else None
            has_audio = _has_audio_stream(scene["vid_path"]) if ok else False
            info.update({
                "pass": bool(ok and has_audio),
                "candidate": "almighty_reference_voice_asset_audio_dub",
                "raw_path": raw_path,
                "video_has_audio": has_audio,
                "generated_audio_from_prompt_dialogue": has_audio,
                "needs_master_audio_mux": not has_audio,
                "output_qa": output_qa,
            })
            if ok and has_audio:
                _remove_motion_task(idx)
                return True, info
            info.setdefault("reason", "postprocess_missing_generated_audio")
            return False, info
        if st == "failed":
            _remove_motion_task(idx)
            info.update({"reason": "task_failed", "response": s})
            return False, info
        time.sleep(5)
    info.update({"reason": "poll_timeout_reusable"})
    return False, info


def _try_motion_audio_dub_video(idx: int, scene: dict, motion_prompt: str, aspect_ratio: str, dur: int, target_dur: float | None = None, safe_retry: bool = False) -> tuple[bool, bool]:
    if ADS_DIALOGUE_MODE or not VOICE_ASSET_AUDIO_DUB_EXPERIMENT or safe_retry:
        return False, False
    img_path = scene.get("img_path")
    if not img_path or not os.path.exists(img_path):
        return False, False
    voice_repair_turns = _load_motion_voice_repair_turns()
    repair_requested = MOTION_VOICE_REPAIR and ((idx + 1) in voice_repair_turns)
    ref_offset = 1 if repair_requested else 0
    voice_asset_ref = _select_voice_asset_reference(scene, mode="motion", ref_offset=ref_offset)
    if not voice_asset_ref:
        _append_motion_qa({
            "turn": idx + 1,
            "path": "almighty-reference-audio-dub",
            "pass": False,
            "fallback_to_reference_motion": True,
            "reason": "missing_voice_asset_reference",
        })
        return False, False
    source_audio = voice_asset_ref.get("path")
    if not source_audio or not os.path.exists(source_audio):
        return False, False
    scene["_motion_reference_audio"] = source_audio
    scene["_motion_reference_audio_role"] = "voice_asset_reference"
    scene["_motion_voice_asset_reference"] = voice_asset_ref
    bridge_paths = [
        str(p)
        for p in (scene.get("motion_bridge_ref_paths") or [])
        if p and os.path.exists(str(p)) and os.path.getsize(str(p)) > 10000
    ]
    try:
        image_urls = [_upload_to_weryai(img_path)]
        for bridge_path in bridge_paths[:2]:
            image_urls.append(_upload_to_weryai(bridge_path))
        image_url = image_urls[0]
        audio_url = _upload_to_weryai(source_audio)
    except Exception as e:
        log(f"[motion-audio-dub {idx}] reference 上传失败，回退 motion: {e}")
        _append_motion_qa({
            "turn": idx + 1,
            "path": "almighty-reference-audio-dub",
            "pass": False,
            "fallback_to_reference_motion": True,
            "reason": f"upload_failed: {e}",
            "voice_asset_reference": voice_asset_ref,
        })
        return False, False

    strict_voice = bool(MOTION_VOICE_STRICT_LOCK or repair_requested)
    prompt = _motion_audio_dub_prompt(scene, motion_prompt, safe_retry=safe_retry, strict_voice=strict_voice)
    if len(image_urls) > 1:
        bridge_instruction = (
            " Treat the uploaded images as ordered motion keyframes: image 1 is the start frame, "
            "image 2 is the end/action frame. Create a visible motivated transition between them; "
            "the subject must not just stare or hold a pose. "
        )
        prompt = (bridge_instruction + prompt)[:2000]
    caption_info = _werydance_caption_request(scene)
    task_id = None
    response = None
    for submit_attempt in range(3):
        try:
            _wait_motion_submit_slot(f"motion audio-dub {idx+1}")
            response = req_post("/generation/almighty-reference-to-video", {
                "model": "WERYDANCE_2_0",
                "images": image_urls,
                "audios": [audio_url],
                "prompt": prompt,
                "negative_prompt": _werydance_negative_prompt(scene),
                "duration": dur,
                "aspect_ratio": aspect_ratio,
                "resolution": VOICE_ASSET_AUDIO_DUB_RESOLUTION,
                "generate_audio": "true",
                "video_number": 1,
            }, timeout=30)
            task_id = response.get("data", {}).get("task_id") or (response.get("data", {}).get("task_ids") or [None])[0]
            if task_id:
                break
        except Exception as e:
            if submit_attempt < 2:
                wait_s = 5 * (submit_attempt + 1)
                log(f"[motion-audio-dub {idx}] submit 失败（第 {submit_attempt+1}/3 次）：{e}，{wait_s}s 后重试")
                time.sleep(wait_s)
                continue
            response = {"exception": str(e)}
    if not task_id:
        _append_motion_qa({
            "turn": idx + 1,
            "path": "almighty-reference-audio-dub",
            "pass": False,
            "fallback_to_reference_motion": True,
            "reason": "submit_without_task_id",
            "response": response,
            "voice_asset_reference": voice_asset_ref,
        })
        return False, False

    _save_motion_task(idx, task_id)
    ok, info = _motion_audio_dub_poll_and_download(idx, task_id, scene, float(target_dur or dur))
    timed_out_or_reusable = str(idx) in _load_motion_tasks()
    info.update({
        "path": "almighty-reference-audio-dub",
        "model": "WERYDANCE_2_0",
        "submit_duration": dur,
        "target_duration": round(float(target_dur or dur), 3),
        "aspect_ratio": aspect_ratio,
        "resolution": VOICE_ASSET_AUDIO_DUB_RESOLUTION,
        "image_path": img_path,
        "reference_image_count": len(image_urls),
        "motion_bridge_ref_paths": bridge_paths,
        "audio_url": audio_url,
        "image_url": image_url,
        "image_urls": image_urls,
        "motion_plan": _motion_plan_for_qa(scene),
        "fallback_to_reference_motion": not ok and not timed_out_or_reusable,
        "timed_out_or_reusable": timed_out_or_reusable,
        "voice_asset_reference": voice_asset_ref,
        "voice_repair_requested": repair_requested,
        "voice_repair_turns": sorted(voice_repair_turns) if MOTION_VOICE_REPAIR else [],
        "voice_reference_variant": "alternate_reference_strict" if repair_requested else "primary_reference_strict" if strict_voice else "primary_reference",
        "voice_timbre_auto_verified": False,
        "voice_timbre_qa": "manual_required",
        "werydance_captions_enabled": WERYDANCE_CAPTIONS,
        "werydance_captions_requested": caption_info.get("requested"),
        "werydance_caption_text": caption_info.get("text") if caption_info.get("requested") else None,
        "ass_fallback_required": caption_info.get("ass_fallback_required"),
        "caption_reason": caption_info.get("reason"),
        "voice_reference_policy": "use owned, licensed, consented, or otherwise lawful voice references; avoid undisclosed real-person impersonation",
    })
    _append_motion_qa(info)
    if not ok and timed_out_or_reusable:
        return True, False
    return ok, ok


def _try_motion_reference_video(idx: int, scene: dict, motion_prompt: str, aspect_ratio: str, dur: int, target_dur: float | None = None, safe_retry: bool = False) -> tuple[bool, bool]:
    """Try storyboard image-to-video first.

    Returns (handled, ok). handled=True means a reference-video task was submitted or conclusively attempted;
    handled=False lets the caller use the legacy text-to-video path without treating this as a failure.
    """
    if (ADS_DIALOGUE_MODE and ADSD_LIP_SYNC_EXPERIMENT) or not STORYBOARD_REFERENCE_MOTION:
        return False, False
    img_path = scene.get("img_path")
    if not img_path or not os.path.exists(img_path):
        _append_motion_qa({
            "turn": idx + 1,
            "path": "image-to-video",
            "pass": False,
            "fallback_to_text": True,
            "reason": "missing_storyboard_image",
        })
        return False, False

    reference_path = _build_annotated_storyboard_reference(scene, idx, motion_prompt, dur)
    reference_mode = "annotated_storyboard" if reference_path and reference_path != img_path else "clean_keyframe"
    if reference_mode == "annotated_storyboard" and not STORYBOARD_ANNOTATED_MOTION:
        reference_path = img_path
        reference_mode = "clean_keyframe"
    full_prompt = _motion_reference_prompt(
        scene,
        motion_prompt,
        safe_retry=safe_retry,
        annotated=(reference_mode == "annotated_storyboard"),
    )
    caption_info = _werydance_caption_request(scene)
    try:
        image_url = _upload_to_weryai(reference_path or img_path)
    except Exception as e:
        log(f"[motion {idx}] storyboard image upload 失败，回退 text-to-video: {e}")
        _append_motion_qa({
            "turn": idx + 1,
            "path": "image-to-video",
            "pass": False,
            "fallback_to_text": True,
            "reference_mode": reference_mode,
            "reason": f"upload_failed: {e}",
        })
        return False, False

    task_id = None
    response = None
    for submit_attempt in range(3):
        try:
            _wait_motion_submit_slot(f"motion reference {idx+1}")
            response = req_post("/generation/image-to-video", {
                "model": "WERYDANCE_2_0",
                "image": image_url,
                "prompt": full_prompt,
                "negative_prompt": _werydance_negative_prompt(scene),
                "duration": dur,
                "aspect_ratio": aspect_ratio,
                "resolution": "1080p",
                "generate_audio": "false",
            }, timeout=30)
            task_id = response.get("data", {}).get("task_id") or (response.get("data", {}).get("task_ids") or [None])[0]
            if task_id:
                break
        except Exception as e:
            if submit_attempt < 2:
                wait_s = 5 * (submit_attempt + 1)
                log(f"[motion {idx}] image-to-video submit 失败（第 {submit_attempt+1}/3 次）：{e}，{wait_s}s 后重试")
                time.sleep(wait_s)
                continue
            response = {"exception": str(e)}

    if not task_id:
        log(f"[motion {idx}] image-to-video 无 task_id，回退 text-to-video: {response}")
        _append_motion_qa({
            "turn": idx + 1,
            "path": "image-to-video",
            "pass": False,
            "fallback_to_text": True,
            "reference_mode": reference_mode,
            "reason": "submit_without_task_id",
            "response": response,
        })
        return False, False

    _save_motion_task(idx, task_id)
    ok = _motion_poll_and_download(idx, task_id, scene["vid_path"], target_dur=target_dur)
    timed_out_or_reusable = str(idx) in _load_motion_tasks()
    output_qa = _motion_output_qa(scene["vid_path"], target_dur) if ok else None
    _append_motion_qa({
        "turn": idx + 1,
        "path": "image-to-video",
        "model": "WERYDANCE_2_0",
        "task_id": task_id,
        "pass": ok,
        "fallback_to_text": (not ok and not timed_out_or_reusable),
        "timed_out_or_reusable": timed_out_or_reusable,
        "reference_mode": reference_mode,
        "storyboard_mode": bool(scene.get("storyboard_mode")),
        "image_path": reference_path or img_path,
        "clean_image_path": img_path,
        "motion_plan": _motion_plan_for_qa(scene),
        "submit_duration": dur,
        "target_duration": round(float(target_dur), 3) if target_dur is not None else None,
        "aspect_ratio": aspect_ratio,
        "werydance_captions_enabled": WERYDANCE_CAPTIONS,
        "werydance_captions_requested": caption_info.get("requested"),
        "werydance_caption_text": caption_info.get("text") if caption_info.get("requested") else None,
        "ass_fallback_required": caption_info.get("ass_fallback_required"),
        "caption_reason": caption_info.get("reason"),
        "output_qa": output_qa,
    })
    if not ok and timed_out_or_reusable:
        return True, False
    return ok, ok


def _motion_one_scene(idx: int, scene: dict, motion_prompt: str, aspect_ratio: str, safe_retry: bool = False) -> bool:
    """对单个 scene 调 WERYDANCE_2_0 生成 motion 版 seg_N.mp4；成功返回 True"""
    img_path = scene["img_path"]
    vid_path = scene["vid_path"]  # 静态 seg_N.mp4 的路径，成功就覆盖它
    # WERYDANCE 支持 5-10s；字段名统一用 vid_duration（step345_timeline 里的 key）
    _raw_dur = scene.get("vid_duration") or scene.get("dur") or 5
    target_dur = float(_raw_dur)
    dur = int(round(max(5, min(10, _raw_dur))))

    # ★ 持久化：检查这个 scene 是否有未完成的历史 task_id，有则先查状态，避免重复提交烧钱
    existing_tasks = _load_motion_tasks()
    existing_tid = existing_tasks.get(str(idx))
    if existing_tid:
        log(f"[motion {idx}] 发现历史 task_id={existing_tid}，先查 WeryAI 后台状态...")
        try:
            s = req_get(f"/generation/{existing_tid}/status")
            st = s.get("data", {}).get("task_status", "")
            if st == "succeed":
                # 后台已完成，直接下载复用
                log(f"[motion {idx}] 历史任务 {existing_tid} 已完成，直接下载复用")
                return _motion_poll_and_download(idx, existing_tid, vid_path, target_dur=target_dur)
            if st == "failed":
                log(f"[motion {idx}] 历史任务 {existing_tid} 已 failed，移除记录，重新提交")
                _remove_motion_task(idx)
            elif st in ("waiting", "processing"):
                log(f"[motion {idx}] 历史任务 {existing_tid} 仍 {st}，继续轮询")
                return _motion_poll_and_download(idx, existing_tid, vid_path, target_dur=target_dur)
            # 其他状态：走新提交流程
        except Exception as e:
            log(f"[motion {idx}] 查历史任务失败: {e}，走新提交")

    try:
        handled_audio_dub, audio_dub_ok = _try_motion_audio_dub_video(
            idx, scene, motion_prompt, aspect_ratio, dur, target_dur=target_dur, safe_retry=safe_retry
        )
        if audio_dub_ok:
            return True
        if handled_audio_dub:
            log(f"[motion {idx}] voice-asset audio-dub 已提交但未完成/未通过，保留现有静态片段，不重复烧其他 motion")
            return False

        handled_reference, reference_ok = _try_motion_reference_video(
            idx, scene, motion_prompt, aspect_ratio, dur, target_dur=target_dur, safe_retry=safe_retry
        )
        if reference_ok:
            return True
        if handled_reference:
            log(f"[motion {idx}] image-to-video 已提交但未完成/未通过，保留现有静态片段，不重复烧 text-to-video")
            return False

        # 兜底：直接 text-to-video（Seedance 2.0），绕过"照片晃动"，走真正摄影机运动
        # ADSD 使用降噪 prompt，避免把上游静帧 prompt 的风格词带入 WERYDANCE 触发版权拦截。
        full_prompt = _build_motion_video_prompt(scene, motion_prompt, safe_retry=safe_retry)
        caption_info = _werydance_caption_request(scene)
        caption_instruction = _werydance_caption_instruction(scene)
        full_prompt = (full_prompt[: max(0, 2000 - len(caption_instruction))] + caption_instruction)[:2000]
        if ADS_DIALOGUE_MODE and not ADSD_RICH_MOTION_PROMPT and not safe_retry:
            log(f"[motion {idx}] ADSD 使用默认安全 prompt")
        if safe_retry:
            log(f"[motion {idx}] 使用极简安全 prompt 重试")
        # text-to-video 限 2000 字符
        if len(full_prompt) > 2000:
            full_prompt = full_prompt[:2000]

        task_id = None
        for submit_attempt in range(3):
            _wait_motion_submit_slot(f"motion {idx+1}")
            r = req_post("/generation/text-to-video", {
                "model": "WERYDANCE_2_0",
                "prompt": full_prompt,
                "negative_prompt": _werydance_negative_prompt(scene),
                "duration": dur,
                "aspect_ratio": aspect_ratio,
                "resolution": "1080p",
            }, timeout=30)
            task_id = r.get("data", {}).get("task_id") or (r.get("data", {}).get("task_ids") or [None])[0]
            if task_id:
                break
            if _is_rate_limited_error(RuntimeError(r)):
                wait_s = MOTION_RATE_LIMIT_BACKOFF * (submit_attempt + 1)
                log(f"[motion {idx}] text-to-video submit 频率限制，退避 {wait_s:.1f}s 后重试: {r}")
                time.sleep(wait_s)
                continue
            log(f"[motion {idx}] text-to-video 提交失败: {r}")
            return False
        if not task_id:
            log(f"[motion {idx}] text-to-video 3 次提交仍失败")
            _append_motion_qa({
                "turn": idx + 1,
                "path": "text-to-video",
                "pass": False,
                "reason": "submit_without_task_id",
            })
            return False

        # ★ 立即持久化：轮询任何阶段失败/超时，下次 rerun 都能复用
        _save_motion_task(idx, task_id)

        # 轮询 + 下载
        ok = _motion_poll_and_download(idx, task_id, vid_path, target_dur=target_dur)
        output_qa = _motion_output_qa(vid_path, target_dur) if ok else None
        _append_motion_qa({
            "turn": idx + 1,
            "path": "text-to-video",
            "model": "WERYDANCE_2_0",
            "task_id": task_id,
            "pass": ok,
            "submit_duration": dur,
            "target_duration": round(target_dur, 3),
            "aspect_ratio": aspect_ratio,
            "fallback_path": True,
            "motion_plan": _motion_plan_for_qa(scene),
            "werydance_captions_enabled": WERYDANCE_CAPTIONS,
            "werydance_captions_requested": caption_info.get("requested"),
            "werydance_caption_text": caption_info.get("text") if caption_info.get("requested") else None,
            "ass_fallback_required": caption_info.get("ass_fallback_required"),
            "caption_reason": caption_info.get("reason"),
            "output_qa": output_qa,
        })
        return ok
    except Exception as e:
        log(f"[motion {idx}] 异常: {type(e).__name__}: {e}")
        return False


_grid_multiref_tasks_lock = threading.Lock()
_previs_page_tasks_lock = threading.Lock()


def _grid_multiref_tasks_file() -> Path:
    return OUTPUT_DIR / "grid_multiref_motion_tasks.json"


def _previs_page_tasks_file() -> Path:
    return OUTPUT_DIR / "previs_page_motion_tasks.json"


def _load_grid_multiref_tasks() -> dict:
    p = _grid_multiref_tasks_file()
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _load_previs_page_tasks() -> dict:
    p = _previs_page_tasks_file()
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_grid_multiref_task(group_key: str, task_id: str) -> None:
    with _grid_multiref_tasks_lock:
        tasks = _load_grid_multiref_tasks()
        tasks[group_key] = task_id
        _grid_multiref_tasks_file().write_text(json.dumps(tasks, ensure_ascii=False, indent=2), encoding="utf-8")


def _save_previs_page_task(group_key: str, task_id: str) -> None:
    with _previs_page_tasks_lock:
        tasks = _load_previs_page_tasks()
        tasks[group_key] = task_id
        _previs_page_tasks_file().write_text(json.dumps(tasks, ensure_ascii=False, indent=2), encoding="utf-8")


def _remove_grid_multiref_task(group_key: str) -> None:
    with _grid_multiref_tasks_lock:
        tasks = _load_grid_multiref_tasks()
        tasks.pop(group_key, None)
        _grid_multiref_tasks_file().write_text(json.dumps(tasks, ensure_ascii=False, indent=2), encoding="utf-8")


def _remove_previs_page_task(group_key: str) -> None:
    with _previs_page_tasks_lock:
        tasks = _load_previs_page_tasks()
        tasks.pop(group_key, None)
        _previs_page_tasks_file().write_text(json.dumps(tasks, ensure_ascii=False, indent=2), encoding="utf-8")


def _poll_video_task_download(task_id: str, out_path: Path, label: str, max_iterations: int = 121) -> tuple[bool, dict]:
    info = {
        "task_id": task_id,
        "path": str(out_path),
        "pass": False,
    }
    for iteration in range(max_iterations):
        try:
            s = req_get(f"/generation/{task_id}/status")
            data = s.get("data", {})
            st = data.get("task_status", "")
            if iteration == 0 or iteration % 12 == 0 or st in ("succeed", "failed"):
                log(f"[{label}] poll #{iteration+1}: {st}")
            if st == "succeed":
                vid_url = _extract_video_url(data)
                if not vid_url:
                    info.update({"reason": "succeed_without_video_url", "response": data})
                    return False, info
                tmp_path = out_path.with_suffix(out_path.suffix + ".tmp")
                urllib.request.urlretrieve(vid_url, tmp_path)
                if not tmp_path.exists() or tmp_path.stat().st_size < 10000:
                    info.update({"reason": "download_file_too_small"})
                    return False, info
                os.replace(tmp_path, out_path)
                w, h = ffprobe_video_size(str(out_path))
                try:
                    dur = ffprobe_duration(str(out_path))
                except Exception:
                    dur = None
                info.update({
                    "pass": True,
                    "video_url": vid_url,
                    "bytes": out_path.stat().st_size,
                    "width": w,
                    "height": h,
                    "duration": round(dur, 3) if dur is not None else None,
                })
                return True, info
            if st == "failed":
                info.update({"reason": "task_failed", "response": data})
                return False, info
        except Exception as e:
            if iteration in (0, 12, 60, 120):
                log(f"[{label}] poll 异常: {type(e).__name__}: {e}")
        time.sleep(5)
    info.update({"reason": "poll_timeout"})
    return False, info


def _grid_multiref_group_size() -> int:
    try:
        raw = int(os.environ.get("ADR_STORYBOARD_GRID_MULTIREF_GROUP", "4"))
    except Exception:
        raw = 4
    return max(2, min(12, raw))


def _grid_multiref_duration(group: list[dict]) -> int:
    override = os.environ.get("ADR_STORYBOARD_GRID_MULTIREF_DURATION", "").strip()
    if override:
        try:
            return max(5, min(10, int(round(float(override)))))
        except Exception:
            pass
    total = 0.0
    for scene in group:
        try:
            total += float(scene.get("vid_duration") or scene.get("dur") or 1.25)
        except Exception:
            total += 1.25
    return max(5, min(10, int(round(total))))


def _grid_multiref_segment_max_stretch() -> float:
    try:
        raw = float(os.environ.get("ADR_GRID_MULTIREF_SEGMENT_MAX_STRETCH", "2.5"))
    except Exception:
        raw = 2.5
    return max(1.0, min(4.0, raw))


def _grid_multiref_prompt(
    group: list[dict],
    start_idx: int,
    motion_prompts: list[str],
    has_character_sheet: bool = False,
) -> str:
    lines = []
    action_mode = False
    for offset, scene in enumerate(group):
        idx = start_idx + offset
        visual = _short_board_text(scene.get("prompt") or scene.get("text"), 180)
        motion = _short_board_text(motion_prompts[idx] if idx < len(motion_prompts) else "", 120)
        if _is_action_scene(scene.get("text", ""), scene.get("prompt", "")):
            action_mode = True
        lines.append(f"{offset + 1}. Scene {idx + 1}: {visual} Camera: {motion}")
    if action_mode:
        style = (
            "Create one coherent high-energy cinematic action video that treats the uploaded references as a "
            "choreography board. Follow the images in order as key poses and action beats: preparation, acceleration, "
            "impact, reaction, recovery, and final pose. Preserve the same hero identity, costume, weapon/prop logic, "
            "environment, lighting, color palette, and screen direction across all beats. Add strong physical motion: "
            "full-body weight shift, footwork, torso rotation, arm follow-through, cloth snap, debris, sparks, smoke, "
            "shockwaves, rain or dust interaction, fast push-in, whip pan, orbit, slow-motion impact, and clear end pose. "
            "No idle posing, no frozen tableau, no slideshow, no gentle-only motion."
        )
    else:
        style = (
            "Create one coherent cinematic video that moves through these shots in order, preserving character "
            "identity, costume, period setting, lighting, color palette, and scene geography. Animate plausible motion: "
            "camera push, handheld drift, cloth, paper, rain, crowd, smoke, and natural human movements."
        )
    character_rule = (
        "The first uploaded image is a character/model sheet only. Use it to lock the hero/subject identity, "
        "face, costume, props, creature/vehicle design, palette, and scale; never render the sheet itself. "
        "All remaining uploaded images are the sequential shot/key-pose references. "
        if has_character_sheet else ""
    )
    return (
        "Use the uploaded clean storyboard reference images as a sequential shot plan. "
        f"{character_rule}"
        "Each shot reference image is one shot or key action pose, in the same order as the shot references array. "
        f"{style} "
        "Do not render the storyboard grid, panel borders, shot numbers, labels, captions, subtitles, arrows, "
        "director notes, UI text, watermarks, logos, or any burned-in text. "
        f"Shot plan: {' '.join(lines)}"
    )[:2000]


def _write_grid_multiref_motion_qa(payload: dict) -> None:
    try:
        (OUTPUT_DIR / "grid_multiref_motion_qa.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except Exception as e:
        log(f"grid_multiref_motion_qa.json 写入失败: {e}")


def _write_previs_page_motion_qa(payload: dict) -> None:
    try:
        (OUTPUT_DIR / "previs_page_motion_qa.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except Exception as e:
        log(f"previs_page_motion_qa.json 写入失败: {e}")


def _write_storyboard_trailer_qa(payload: dict) -> None:
    try:
        (OUTPUT_DIR / "storyboard_trailer_qa.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except Exception as e:
        log(f"storyboard_trailer_qa.json 写入失败: {e}")


def _write_character_trailer_qa(payload: dict) -> None:
    try:
        (OUTPUT_DIR / "character_trailer_qa.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except Exception as e:
        log(f"character_trailer_qa.json 写入失败: {e}")


def _write_grid_multiref_segment_qa(payload: dict) -> None:
    try:
        (OUTPUT_DIR / "grid_multiref_segment_qa.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except Exception as e:
        log(f"grid_multiref_segment_qa.json 写入失败: {e}")


def _motion_compare_record(name: str, qa: dict | None, artifact_key: str = "path") -> dict:
    qa = qa if isinstance(qa, dict) else None
    records = (qa or {}).get("records") or []
    passed = [r for r in records if r.get("pass")]
    artifacts = [r.get(artifact_key) for r in passed if r.get(artifact_key)]
    if not artifacts:
        for record in records:
            for segment in record.get("segments", []) if isinstance(record, dict) else []:
                if segment.get("pass") and segment.get(artifact_key):
                    artifacts.append(segment.get(artifact_key))
    return {
        "name": name,
        "enabled": bool((qa or {}).get("enabled")),
        "pass": bool((qa or {}).get("pass")),
        "total_groups": (qa or {}).get("total_groups") or len(records),
        "success_count": (qa or {}).get("success_count") or len(passed),
        "artifacts": artifacts,
        "policy": (qa or {}).get("policy"),
        "manual_visual_checks_required": (qa or {}).get("manual_visual_checks_required") or [],
    }


def _write_storyboard_motion_compare_qa(
    clean_refs_qa: dict | None = None,
    previs_page_qa: dict | None = None,
    segment_qa: dict | None = None,
    trailer_qa: dict | None = None,
    character_trailer_qa: dict | None = None,
) -> dict:
    clean = _motion_compare_record("clean_refs_multiref", clean_refs_qa)
    previs = _motion_compare_record("previs_page", previs_page_qa)
    segment = _motion_compare_record("grid_multiref_segments", segment_qa, artifact_key="target_path")
    trailer = _motion_compare_record("storyboard_trailer", trailer_qa)
    character_trailer = _motion_compare_record("character_trailer", character_trailer_qa)
    payload = {
        "mode": "storyboard_motion_compare",
        "recommendation": "clean_refs_multiref_segments" if segment.get("pass") else "character_trailer_sidecar" if character_trailer.get("pass") else "storyboard_trailer_sidecar" if trailer.get("pass") else "clean_refs_multiref_sidecar" if clean.get("pass") else "previs_page_sidecar" if previs.get("pass") else "static_or_text_motion_fallback",
        "default_policy": "do_not_enable_by_default_until_three_topic_smokes_pass",
        "records": [clean, previs, segment, trailer, character_trailer],
        "notes": [
            "clean_refs_multiref is the current safer production experiment because panel borders and storyboard text are cropped before motion.",
            "previs_page is a sidecar comparison path for whole-page storyboard understanding; do not route into final timeline yet.",
            "grid_multiref_segments is allowed only behind --use-grid-multiref-segments; excessive stretch is rejected and failed groups fall back to per-shot motion.",
            "storyboard_trailer is a short sidecar trailer path from a production storyboard page; never stretch it into the longform timeline.",
            "character_trailer uses one character sheet plus clean per-shot references, then concatenates short generated shots; it is the safer path for 45s identity-locked trailers.",
        ],
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }
    try:
        (OUTPUT_DIR / "storyboard_motion_compare_qa.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except Exception as e:
        log(f"storyboard_motion_compare_qa.json 写入失败: {e}")
    return payload


def _scene_segment_duration(scene: dict) -> float:
    vid_path = scene.get("vid_path")
    if vid_path and os.path.exists(vid_path):
        try:
            dur = ffprobe_duration(vid_path)
            if dur > 0:
                return dur
        except Exception:
            pass
    for key in ("vid_duration", "dur"):
        try:
            dur = float(scene.get(key) or 0)
            if dur > 0:
                return dur
        except Exception:
            pass
    return 1.25


def _apply_grid_multiref_segments(script: list[dict], motion_qa: dict | None) -> dict | None:
    """Experimental mainline: split successful multi-ref chunks back into seg_N.mp4 files."""
    if not STORYBOARD_GRID_MULTIREF_SEGMENTS or ADS_DIALOGUE_MODE:
        return None
    if os.environ.get("ADR_UNSAFE_ALLOW_GRID_MULTIREF_PROPORTIONAL_SPLIT", "").strip().lower() not in ("1", "true", "yes", "on"):
        qa = {
            "mode": "grid_multiref_video_split_to_main_segments",
            "enabled": True,
            "pass": False,
            "reason": "disabled_by_default_proportional_split_can_mix_adjacent_storyboard_shots",
            "policy": "do_not_replace_main_timeline_without_verified_shot_boundaries",
            "records": [],
            "manual_visual_checks_required": [
                "shot_boundary_timestamps_verified",
                "each_output_segment_contains_only_its_own_storyboard_panel",
                "no_adjacent_panel_bleed",
                "segment_start_end_match_script_timeline",
            ],
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "finalized_at": datetime.now().isoformat(timespec="seconds"),
        }
        _write_grid_multiref_segment_qa(qa)
        tg("⚠️ Grid multi-ref 主线切片已阻断：比例切分会混入相邻分镜，改走逐镜 WeryDance/静态兜底")
        return qa
    records = (motion_qa or {}).get("records") or []
    qa = {
        "mode": "grid_multiref_video_split_to_main_segments",
        "enabled": True,
        "policy": "replace_only_safe_speed_segments_dynamic_fallback_for_failures",
        "target_width": VIDEO_W,
        "target_height": VIDEO_H,
        "max_stretch_ratio": _grid_multiref_segment_max_stretch(),
        "records": [],
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }
    for record in records:
        if not record.get("pass"):
            qa["records"].append({
                "group": record.get("group"),
                "scene_indices": record.get("scene_indices"),
                "pass": False,
                "reason": "motion_group_not_passed",
            })
            continue
        src_path = record.get("path")
        if not src_path or not os.path.exists(src_path):
            qa["records"].append({
                "group": record.get("group"),
                "scene_indices": record.get("scene_indices"),
                "pass": False,
                "reason": "missing_multiref_video",
                "path": src_path,
            })
            continue
        raw_indices = record.get("scene_indices") or []
        scene_indices = []
        for value in raw_indices:
            try:
                idx = int(value) - 1
                if 0 <= idx < len(script):
                    scene_indices.append(idx)
            except Exception:
                pass
        if not scene_indices:
            qa["records"].append({
                "group": record.get("group"),
                "scene_indices": raw_indices,
                "pass": False,
                "reason": "empty_scene_indices",
                "path": src_path,
            })
            continue
        try:
            raw_dur = ffprobe_duration(src_path)
        except Exception as e:
            qa["records"].append({
                "group": record.get("group"),
                "scene_indices": raw_indices,
                "pass": False,
                "reason": f"ffprobe_source_failed:{e}",
                "path": src_path,
            })
            continue
        target_durations = [max(0.2, _scene_segment_duration(script[i])) for i in scene_indices]
        total_target = sum(target_durations)
        group_record = {
            "group": record.get("group"),
            "source_path": src_path,
            "source_duration": round(raw_dur, 3),
            "target_total_duration": round(total_target, 3),
            "scene_indices": [i + 1 for i in scene_indices],
            "segments": [],
            "pass": False,
        }
        cursor = 0.0
        for local_i, idx in enumerate(scene_indices):
            scene = script[idx]
            target_dur = target_durations[local_i]
            source_start = raw_dur * (cursor / total_target) if total_target > 0 else 0.0
            source_dur = raw_dur * (target_dur / total_target) if total_target > 0 else raw_dur / max(len(scene_indices), 1)
            source_dur = max(0.05, min(source_dur, max(0.05, raw_dur - source_start)))
            ratio = target_dur / source_dur if source_dur > 0 else 1.0
            tmp_path = str(OUTPUT_DIR / f"seg_{idx}.grid_multiref.tmp.mp4")
            final_path = scene.get("vid_path") or str(OUTPUT_DIR / f"seg_{idx}.mp4")
            seg_record = {
                "scene": idx + 1,
                "target_path": final_path,
                "target_duration": round(target_dur, 3),
                "source_start": round(source_start, 3),
                "source_duration": round(source_dur, 3),
                "speed_ratio": round(ratio, 4),
                "pass": False,
            }
            if ratio > qa["max_stretch_ratio"]:
                seg_record["reason"] = "excessive_stretch_would_stutter"
                group_record["segments"].append(seg_record)
                cursor += target_dur
                continue
            try:
                vf = (
                    f"trim=start={source_start:.4f}:duration={source_dur:.4f},"
                    f"setpts=(PTS-STARTPTS)*{ratio:.8f},"
                    f"scale={VIDEO_W}:{VIDEO_H}:force_original_aspect_ratio=increase,"
                    f"crop={VIDEO_W}:{VIDEO_H},setsar=1,fps=24,format=yuv420p"
                )
                ffmpeg(
                    "-i", src_path,
                    "-vf", vf,
                    "-an",
                    "-t", f"{target_dur:.4f}",
                    "-c:v", "libx264",
                    "-preset", "veryfast",
                    "-crf", "18",
                    "-pix_fmt", "yuv420p",
                    "-movflags", "+faststart",
                    tmp_path,
                    timeout=120,
                )
                if os.path.exists(tmp_path) and os.path.getsize(tmp_path) > 10000:
                    os.replace(tmp_path, final_path)
                out_dur = ffprobe_duration(final_path) if os.path.exists(final_path) else None
                out_w, out_h = ffprobe_video_size(final_path) if os.path.exists(final_path) else (None, None)
                delta = abs((out_dur or 0.0) - target_dur) if out_dur is not None else None
                seg_record.update({
                    "output_duration": round(out_dur, 3) if out_dur is not None else None,
                    "duration_delta": round(delta, 3) if delta is not None else None,
                    "width": out_w,
                    "height": out_h,
                    "bytes": os.path.getsize(final_path) if os.path.exists(final_path) else 0,
                    "pass": (
                        out_dur is not None
                        and delta is not None
                        and delta <= 0.25
                        and out_w == VIDEO_W
                        and out_h == VIDEO_H
                        and os.path.getsize(final_path) > 10000
                    ),
                })
                if seg_record["pass"]:
                    scene["grid_multiref_segment_mode"] = True
                    scene["grid_multiref_source"] = src_path
                else:
                    seg_record.setdefault("reason", "segment_qa_failed")
            except Exception as e:
                seg_record.update({"pass": False, "reason": str(e)})
            finally:
                try:
                    if os.path.exists(tmp_path):
                        os.remove(tmp_path)
                except Exception:
                    pass
            group_record["segments"].append(seg_record)
            cursor += target_dur
        group_record["pass"] = all(s.get("pass") for s in group_record["segments"])
        qa["records"].append(group_record)
        _write_grid_multiref_segment_qa(qa)

    segment_records = [s for g in qa["records"] for s in g.get("segments", [])]
    success_count = sum(1 for s in segment_records if s.get("pass"))
    qa.update({
        "total_segments": len(segment_records),
        "success_count": success_count,
        "success_rate": round(success_count / max(len(segment_records), 1), 4),
        "pass": success_count > 0 and success_count == len(segment_records),
        "finalized_at": datetime.now().isoformat(timespec="seconds"),
    })
    _write_grid_multiref_segment_qa(qa)
    if qa["pass"]:
        tg(f"✅ Grid multi-ref 主时间线切片 QA 通过：{success_count}/{len(segment_records)} 段")
    else:
        tg(f"⚠️ Grid multi-ref 主时间线切片 QA 未全通过：{success_count}/{len(segment_records)} 段，失败段保留兜底")
    return qa


def _previs_page_duration(group: list[dict]) -> int:
    override = os.environ.get("ADR_PREVIS_PAGE_DURATION", "").strip()
    if override:
        try:
            return max(5, min(10, int(round(float(override)))))
        except Exception:
            pass
    return _grid_multiref_duration(group)


def _previs_page_group_prompt(group: list[dict], scene_indices: list[int], motion_prompts: list[str], has_character_sheet: bool) -> str:
    lines = []
    for local_i, (idx, scene) in enumerate(zip(scene_indices, group), start=1):
        visual = _short_board_text(scene.get("prompt") or scene.get("shot") or scene.get("text"), 180)
        motion = _short_board_text(motion_prompts[idx] if idx < len(motion_prompts) else "", 110)
        lines.append(f"{local_i}. Scene {idx + 1}: {visual} Motion motivation: {motion}")
    character_sheet_rule = (
        "Use the second uploaded image as a character/style sheet. Lock character identity, face, clothing, era, and palette to it. "
        if has_character_sheet else ""
    )
    return (
        "INTENT: Turn the uploaded previs storyboard page into one coherent cinematic documentary sequence. "
        "STYLE: historically grounded cinematic realism, readable compositions, controlled camera movement, no random jump cuts. "
        "WORLD: preserve the era, location logic, props, costumes, lighting, and documentary mood shown in the storyboard. "
        "REFERENCES: Use the first uploaded image as a previs storyboard page, not as a single still frame. "
        "Do not treat the page as one single image. Treat its panels as sequential shot keyframes in reading order, "
        "left-to-right then top-to-bottom, and expand them into a continuous short scene with clear continuity. "
        f"{character_sheet_rule}"
        "VISUAL APPROACH: Match the storyboard's spatial variety, emotional pacing, screen direction, and action continuity. "
        "Prioritize clear shot order, motivated camera movement, and continuity across beats. Keep motion calm and intentional. "
        "The final video must be a fully immersive scene, not a storyboard document. Do not render the page, panel borders, "
        "grid lines, captions, labels, shot numbers, arrows, UI text, watermarks, logos, subtitles, or any burned-in text. "
        f"SHOT PLAN: {' '.join(lines)}"
    )[:2000]


def _previs_page_groups(script: list[dict]) -> list[tuple[str, list[int], list[dict]]]:
    grouped: dict[str, list[tuple[int, dict]]] = {}
    for i, scene in enumerate(script):
        grid_path = scene.get("storyboard_grid_source")
        if not grid_path or not os.path.exists(grid_path):
            continue
        grouped.setdefault(str(grid_path), []).append((i, scene))
    groups = []
    for grid_path, pairs in grouped.items():
        pairs.sort(key=lambda p: p[0])
        groups.append((grid_path, [i for i, _ in pairs], [scene for _, scene in pairs]))
    groups.sort(key=lambda item: item[1][0] if item[1] else 10**9)
    return groups


def _storyboard_trailer_duration() -> int:
    override = os.environ.get("ADR_STORYBOARD_TRAILER_DURATION", "").strip()
    if override:
        try:
            return max(5, min(15, int(round(float(override)))))
        except Exception:
            pass
    return 10


def _storyboard_trailer_prompt(script: list[dict], motion_prompts: list[str], has_character_sheet: bool) -> str:
    lines = []
    for i, scene in enumerate(script):
        visual = _short_board_text(scene.get("prompt") or scene.get("shot") or scene.get("text"), 130)
        motion = _short_board_text(motion_prompts[i] if i < len(motion_prompts) else "", 80)
        lines.append(f"{i + 1}. {visual} Motion: {motion}")
    character_sheet_rule = (
        "Use the second uploaded image as a character/style sheet and lock identity, costume, face, palette, and era. "
        if has_character_sheet else ""
    )
    return (
        "Create a smooth 10-15 second cinematic trailer from the uploaded AI animation production storyboard board. "
        "The first uploaded image is a director board, not a final frame. Read it as a production plan with cast, "
        "storyboard panels, camera notes, motion notes, palette, and continuity rules. "
        f"{character_sheet_rule}"
        "Do not show the production board itself in the final video. Do not render paper, panel borders, handwriting, "
        "captions, labels, UI text, shot numbers, arrows, checklists, logos, or subtitles. "
        # ★ 关键文字禁令：实测 WERYDANCE 会把故事板里的中英文标注当画面元素重新渲染，导致乱码涂鸦
        "ABSOLUTELY NO TEXT IN THE OUTPUT VIDEO: no Chinese characters, no English letters, no numbers, "
        "no glyphs, no inscriptions on signs/walls/papers/screens, no calligraphy strokes resembling text, "
        "no garbled pseudo-text. The output must be purely visual cinematic footage with zero readable or unreadable text overlays. "
        "If a scene has paper/signs/banners/screens visible, leave them BLANK or with abstract texture only, never with letters or characters. "
        "Translate the board into immersive cinematic shots in order, with motivated camera movement, clear action, "
        "continuous style, consistent characters, and no freeze-frame stretching. Keep pacing brisk and trailer-like. "
        f"SHOT ORDER: {' '.join(lines)}"
    )[:2000]


def _character_trailer_max_shots() -> int:
    try:
        raw = int(os.environ.get("ADR_CHARACTER_TRAILER_MAX_SHOTS", "9"))
    except Exception:
        raw = 9
    return max(1, min(12, raw))


def _character_trailer_shot_duration(scene: dict) -> int:
    override = os.environ.get("ADR_CHARACTER_TRAILER_SHOT_DURATION", "").strip()
    if override:
        try:
            return max(5, min(10, int(round(float(override)))))
        except Exception:
            pass
    try:
        raw = float(scene.get("vid_duration") or scene.get("dur") or 5)
    except Exception:
        raw = 5
    return max(5, min(10, int(round(raw))))


def _character_trailer_prompt(scene: dict, idx: int, motion_prompt: str) -> str:
    visual = _short_board_text(scene.get("prompt") or scene.get("shot") or scene.get("text"), 420)
    beat = _short_board_text(scene.get("text"), 180)
    motion = _short_board_text(motion_prompt, 180)
    return (
        "Create one cinematic trailer shot using the uploaded references. "
        "Image 1 is the character/creature model sheet and must lock identity, face, costume, palette, scale, "
        "materials, and companion/creature design. Image 2 is the clean shot keyframe and must lock composition, "
        "location, lighting, and action. Do not render either reference sheet/page as paper or a document. "
        "No text, no labels, no borders, no UI, no watermark, no subtitles. "
        f"Shot {idx + 1}: {visual}. Story beat: {beat}. Camera/action: {motion}. "
        "Keep motion smooth, physically plausible, emotionally clear, and continuous with the shared character design."
    )[:2000]


def _concat_character_trailer_segments(records: list[dict]) -> tuple[bool, dict]:
    passed = [r for r in records if r.get("pass") and r.get("path") and os.path.exists(r.get("path"))]
    info = {"segment_count": len(passed), "path": str(OUTPUT_DIR / "character_trailer.mp4"), "pass": False}
    if not passed:
        info["reason"] = "no_passed_segments"
        return False, info
    concat_path = OUTPUT_DIR / "character_trailer_concat.txt"
    try:
        with open(concat_path, "w", encoding="utf-8") as f:
            for record in passed:
                f.write(f"file '{record['path']}'\n")
        out_path = OUTPUT_DIR / "character_trailer.mp4"
        ffmpeg(
            "-f", "concat", "-safe", "0", "-i", str(concat_path),
            "-c", "copy",
            str(out_path),
            timeout=180,
        )
        if not out_path.exists() or out_path.stat().st_size < 10000:
            info["reason"] = "concat_output_missing_or_small"
            return False, info
        w, h = ffprobe_video_size(str(out_path))
        dur = ffprobe_duration(str(out_path))
        info.update({
            "path": str(out_path),
            "bytes": out_path.stat().st_size,
            "width": w,
            "height": h,
            "duration": round(dur, 3),
            "pass": w == VIDEO_W and h == VIDEO_H and dur >= 4.5,
        })
        if not info["pass"]:
            info["reason"] = "concat_video_qa_failed"
        return info["pass"], info
    except Exception as e:
        info["reason"] = str(e)
        return False, info


def _generate_character_trailer_motion(script: list[dict], motion_prompts: list[str], aspect_ratio: str) -> dict | None:
    """Sidecar: one character sheet + clean shot refs -> multi-shot identity-locked trailer."""
    if not CHARACTER_TRAILER_MODE or ADS_DIALOGUE_MODE:
        return None
    sheet_path = OUTPUT_DIR / "character_sheet.png"
    max_shots = _character_trailer_max_shots()
    refs = [
        (i, scene)
        for i, scene in enumerate(script[:max_shots])
        if scene.get("img_path") and os.path.exists(scene.get("img_path"))
    ]
    qa = {
        "mode": "character_sheet_plus_clean_refs_to_trailer",
        "enabled": True,
        "interface": "almighty-reference-to-video",
        "model": "WERYDANCE_2_0",
        "aspect_ratio": aspect_ratio,
        "resolution": os.environ.get("ADR_CHARACTER_TRAILER_RESOLUTION", "720p"),
        "character_sheet": str(sheet_path),
        "max_shots": max_shots,
        "records": [],
        "policy": "per_shot_identity_locked_segments_concat_no_stretch",
        "manual_visual_checks_required": [
            "character_identity_consistent_across_shots",
            "creature_or_companion_design_consistent_if_present",
            "no_character_sheet_or_storyboard_page_rendered_as_document",
            "no_text_labels_borders_or_watermarks",
            "motion_is_smooth_no_freeze_frame_stretching",
            "shot_order_matches_script",
        ],
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }
    if not sheet_path.exists() or sheet_path.stat().st_size < 100000:
        qa.update({"pass": False, "reason": "missing_character_sheet"})
        _write_character_trailer_qa(qa)
        return qa
    if not refs:
        qa.update({"pass": False, "reason": "missing_clean_shot_refs"})
        _write_character_trailer_qa(qa)
        return qa
    try:
        sheet_url = _upload_to_weryai(str(sheet_path))
        qa["character_sheet_url"] = sheet_url
    except Exception as e:
        qa.update({"pass": False, "reason": f"character_sheet_upload_failed:{e}"})
        _write_character_trailer_qa(qa)
        return qa

    tg(f"🧬 Character trailer 启动：character sheet + clean refs × {len(refs)} 镜")
    for local_no, (idx, scene) in enumerate(refs, start=1):
        out_path = OUTPUT_DIR / f"character_trailer_seg_{idx:02d}.mp4"
        record = {
            "scene": idx + 1,
            "shot": local_no,
            "image_path": scene.get("img_path"),
            "path": str(out_path),
            "duration_requested": _character_trailer_shot_duration(scene),
            "pass": False,
        }
        qa["records"].append(record)
        try:
            shot_url = _upload_to_weryai(scene["img_path"])
            prompt = _character_trailer_prompt(scene, idx, motion_prompts[idx] if idx < len(motion_prompts) else "")
            _wait_motion_submit_slot(f"character trailer shot {idx+1}")
            r = req_post("/generation/almighty-reference-to-video", {
                "model": "WERYDANCE_2_0",
                "images": [sheet_url, shot_url],
                "prompt": prompt,
                "duration": record["duration_requested"],
                "aspect_ratio": aspect_ratio,
                "resolution": qa["resolution"],
                "generate_audio": "false",
                "video_number": 1,
            }, timeout=30)
            task_id = r.get("data", {}).get("task_id") or (r.get("data", {}).get("task_ids") or [None])[0]
            record.update({"image_urls": [sheet_url, shot_url], "task_id": task_id})
            if not task_id:
                record.update({"reason": "submit_without_task_id", "response": r})
                _write_character_trailer_qa(qa)
                continue
            ok, info = _poll_video_task_download(task_id, out_path, f"character trailer shot {idx+1}")
            record.update(info)
            record["pass"] = bool(ok and record.get("width") == VIDEO_W and record.get("height") == VIDEO_H)
            if not record["pass"]:
                record.setdefault("reason", "shot_video_qa_failed")
            _write_character_trailer_qa(qa)
        except Exception as e:
            record.update({"pass": False, "reason": str(e)})
            _write_character_trailer_qa(qa)

    success_count = sum(1 for r in qa["records"] if r.get("pass"))
    concat_ok, concat_info = _concat_character_trailer_segments(qa["records"])
    qa.update({
        "success_count": success_count,
        "total_groups": len(qa["records"]),
        "concat": concat_info,
        "path": concat_info.get("path"),
        "pass": bool(concat_ok and success_count == len(qa["records"]) and success_count > 0),
        "finalized_at": datetime.now().isoformat(timespec="seconds"),
    })
    _write_character_trailer_qa(qa)
    if qa["pass"]:
        tg(f"✅ Character trailer 完成：{success_count}/{len(qa['records'])} 镜，{qa.get('path')}")
    else:
        tg(f"⚠️ Character trailer 未全通过：{success_count}/{len(qa['records'])} 镜")
    return qa


def _multi_trailer_prompt_for_group(script: list[dict], start_idx: int, end_idx: int, has_character_sheet: bool) -> str:
    """构造单段 trailer 的 prompt，限定 panel 范围 + 强禁止文字渲染。"""
    panels_text = []
    for i in range(start_idx, end_idx + 1):
        s = script[i]
        visual = _short_board_text(s.get("prompt") or s.get("shot") or s.get("text"), 130)
        panels_text.append(f"{i+1}. {visual}")
    character_rule = (
        "Use the second uploaded image as character/style sheet to lock identity, costume, palette, and era consistent with prior segments. "
        if has_character_sheet else ""
    )
    return (
        f"Create a smooth cinematic segment covering ONLY storyboard panels {start_idx+1} through {end_idx+1} of the uploaded production board. "
        "The first uploaded image is a director board; ignore panels outside the requested range. "
        f"{character_rule}"
        "Do not render the production board itself. Do not show paper, panel borders, handwriting, captions, labels, UI text, shot numbers, arrows, or any subtitles. "
        "ABSOLUTELY NO TEXT IN THE OUTPUT VIDEO: no Chinese characters, no English letters, no numbers, no glyphs, no garbled pseudo-text. "
        "Paper/signs/banners/screens visible in scene must be BLANK or abstract texture only. "
        "Translate the selected panels into immersive cinematic shots in order, with motivated camera movement, clear action, continuous style, consistent characters, no freeze-frame stretching. "
        f"PANEL ORDER: {' '.join(panels_text)}"
    )[:2000]


def _generate_multi_trailer_segments(script: list[dict], aspect_ratio: str) -> str | None:
    """STORYBOARD_TRAILER_MAIN 主路径：把脚本按旁白时长贪心装箱成 N 组，
    每组提交一次 WERYDANCE，并发等全部完成，ffmpeg concat 拼成 storyboard_trailer.mp4。
    成功返回最终 mp4 路径；任一段失败返回 None，让 step7 fallback 到单 trailer 循环或逐镜。"""
    if not STORYBOARD_TRAILER_MAIN or ADS_DIALOGUE_MODE:
        return None
    board_path = OUTPUT_DIR / "production_storyboard_page.png"
    if not board_path.exists() or board_path.stat().st_size < 100000:
        tg("⚠️ multi-trailer: production_storyboard_page.png 缺失，跳过")
        return None

    # 1. 贪心装箱：每组 panels 旁白总时长 ≤ max_dur
    max_dur = int(os.environ.get("ADR_TRAILER_MAX_DURATION", "15"))
    min_dur = int(os.environ.get("ADR_TRAILER_MIN_DURATION", "5"))
    groups: list[dict] = []
    cur_panels: list[int] = []
    cur_dur = 0.0
    for i, s in enumerate(script):
        pdur = float(s.get("vid_duration") or s.get("dur") or 5.0)
        if cur_panels and cur_dur + pdur > max_dur:
            d = int(round(min(max(cur_dur, min_dur), max_dur)))
            groups.append({"start": cur_panels[0], "end": cur_panels[-1], "duration": d})
            cur_panels, cur_dur = [], 0.0
        cur_panels.append(i)
        cur_dur += pdur
    if cur_panels:
        d = int(round(min(max(cur_dur, min_dur), max_dur)))
        groups.append({"start": cur_panels[0], "end": cur_panels[-1], "duration": d})

    n = len(groups)
    if n == 0:
        return None
    tg(f"🎬 multi-trailer 分组：{n} 段 × {[g['duration'] for g in groups]}s 覆盖 panels {[(g['start']+1, g['end']+1) for g in groups]}")

    # 2. 上传公共素材
    try:
        board_url = _upload_to_weryai(str(board_path))
    except Exception as e:
        log(f"multi-trailer board upload failed: {e}")
        return None
    sheet_path = OUTPUT_DIR / "character_sheet.png"
    sheet_url = None
    if sheet_path.exists() and sheet_path.stat().st_size > 100000:
        try:
            sheet_url = _upload_to_weryai(str(sheet_path))
        except Exception as e:
            log(f"multi-trailer character_sheet upload skipped: {e}")

    # 3. 并发提交 N 段
    has_sheet = sheet_url is not None
    poll_iters = int(os.environ.get("ADR_TRAILER_SEG_POLL_ITERS", "360"))

    def _gen_segment(gi: int, group: dict) -> tuple[int, str | None, str]:
        prompt = _multi_trailer_prompt_for_group(script, group["start"], group["end"], has_sheet)
        images = [board_url] + ([sheet_url] if sheet_url else [])
        try:
            _wait_motion_submit_slot(f"multi-trailer seg {gi+1}")
            r = req_post("/generation/almighty-reference-to-video", {
                "model": "WERYDANCE_2_0",
                "images": images,
                "prompt": prompt,
                "duration": group["duration"],
                "aspect_ratio": aspect_ratio,
                "resolution": os.environ.get("ADR_STORYBOARD_TRAILER_RESOLUTION", "720p"),
                "generate_audio": "false",
                "video_number": 1,
            }, timeout=30)
            task_id = r.get("data", {}).get("task_id") or (r.get("data", {}).get("task_ids") or [None])[0]
            if not task_id:
                return gi, None, "submit_no_task_id"
            out_path = OUTPUT_DIR / f"trailer_seg_{gi:02d}.mp4"
            ok, info = _poll_video_task_download(task_id, out_path, f"multi-trailer seg {gi+1}/{n}", max_iterations=poll_iters)
            return gi, (str(out_path) if ok else None), str(info)
        except Exception as e:
            return gi, None, str(e)[:200]

    results: dict[int, tuple[str | None, str]] = {}
    # weryai 并发上限 20，trailer 分段通常 4-8 段，远低于上限，直接放开
    max_concurrent = min(n, int(os.environ.get("ADR_TRAILER_SEG_MAX_CONCURRENT", "20")))
    with ThreadPoolExecutor(max_workers=max_concurrent) as ex:
        futs = [ex.submit(_gen_segment, gi, g) for gi, g in enumerate(groups)]
        for f in as_completed(futs):
            gi, path, info = f.result()
            results[gi] = (path, info)
            tg(f"{'✓' if path else '⚠️'} multi-trailer seg {gi+1}/{n} {'完成' if path else '失败: ' + info[:80]}")

    seg_paths = [results[i][0] for i in range(n)]
    if any(p is None for p in seg_paths):
        tg(f"⚠️ multi-trailer 有 {sum(1 for p in seg_paths if p is None)}/{n} 段失败，降级")
        return None

    # 4. concat（先标准化 fps 再合并）
    concat_list = OUTPUT_DIR / "trailer_segs_concat.txt"
    with open(concat_list, "w") as f:
        for p in seg_paths:
            f.write(f"file '{p}'\n")
    final_path = OUTPUT_DIR / "storyboard_trailer.mp4"
    try:
        ffmpeg("-f", "concat", "-safe", "0", "-i", str(concat_list),
               "-c:v", "libx264", "-crf", "20", "-preset", "medium",
               "-vf", "fps=24",
               "-an",
               str(final_path), timeout=240)
    except Exception as e:
        log(f"multi-trailer concat failed: {e}")
        return None
    total_dur = ffprobe_duration(str(final_path))
    tg(f"✅ multi-trailer 拼接完成：{n} 段 → {total_dur:.1f}s @24fps CFR")
    return str(final_path)


def _generate_storyboard_trailer_motion(script: list[dict], motion_prompts: list[str], aspect_ratio: str) -> dict | None:
    """Sidecar: production storyboard page -> short trailer. Never replaces the main timeline."""
    if not STORYBOARD_TRAILER_MODE or ADS_DIALOGUE_MODE:
        return None
    board_path = OUTPUT_DIR / "production_storyboard_page.png"
    character_sheet = os.environ.get("ADR_PREVIS_CHARACTER_SHEET", "").strip()
    has_character_sheet = bool(character_sheet and os.path.exists(character_sheet))
    qa = {
        "mode": "production_storyboard_page_to_trailer",
        "enabled": True,
        "interface": "almighty-reference-to-video",
        "model": "WERYDANCE_2_0",
        "aspect_ratio": aspect_ratio,
        "resolution": os.environ.get("ADR_STORYBOARD_TRAILER_RESOLUTION", "720p"),
        "storyboard_page": str(board_path),
        "duration_requested": _storyboard_trailer_duration(),
        "path": str(OUTPUT_DIR / "storyboard_trailer.mp4"),
        "pass": False,
        "policy": "short_sidecar_trailer_only_never_stretch_into_longform_timeline",
        "manual_visual_checks_required": [
            "does_not_render_storyboard_page_or_paper",
            "no_panel_borders_labels_arrows_or_checklists",
            "shot_order_follows_board",
            "motion_is_smooth_no_freeze_frame_stretching",
            "character_and_style_consistency",
        ],
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }
    if not board_path.exists() or board_path.stat().st_size < 100000:
        qa.update({"reason": "missing_production_storyboard_page"})
        _write_storyboard_trailer_qa(qa)
        return qa
    try:
        image_urls = [_upload_to_weryai(str(board_path))]
        if has_character_sheet:
            image_urls.append(_upload_to_weryai(character_sheet))
            qa["character_sheet"] = character_sheet
        prompt = _storyboard_trailer_prompt(script, motion_prompts, has_character_sheet)
        _wait_motion_submit_slot("storyboard trailer")
        r = req_post("/generation/almighty-reference-to-video", {
            "model": "WERYDANCE_2_0",
            "images": image_urls,
            "prompt": prompt,
            "duration": qa["duration_requested"],
            "aspect_ratio": aspect_ratio,
            "resolution": qa["resolution"],
            "generate_audio": "false",
            "video_number": 1,
        }, timeout=30)
        task_id = r.get("data", {}).get("task_id") or (r.get("data", {}).get("task_ids") or [None])[0]
        qa.update({"image_urls": image_urls, "task_id": task_id})
        if not task_id:
            qa.update({"reason": "submit_without_task_id", "response": r})
            _write_storyboard_trailer_qa(qa)
            return qa
        out_path = OUTPUT_DIR / "storyboard_trailer.mp4"
        # storyboard trailer 整张多 panel 大图喂 WERYDANCE，实测 ~13min 才完成
        # 用 30min（360 iterations × 5s）避免 false-negative timeout
        trailer_poll_iters = int(os.environ.get("ADR_STORYBOARD_TRAILER_POLL_ITERS", "360"))
        ok, info = _poll_video_task_download(task_id, out_path, "storyboard trailer", max_iterations=trailer_poll_iters)
        qa.update(info)
        qa["pass"] = bool(ok)
        if ok:
            tg(f"🎞 Storyboard trailer 生成完成：{out_path}")
        else:
            tg(f"⚠️ Storyboard trailer 生成失败：{qa.get('reason')}")
    except Exception as e:
        qa.update({"pass": False, "reason": str(e)})
        tg(f"⚠️ Storyboard trailer 异常：{str(e)[:120]}")
    finally:
        qa["finalized_at"] = datetime.now().isoformat(timespec="seconds")
        _write_storyboard_trailer_qa(qa)
    return qa


def _generate_previs_page_motion_segments(script: list[dict], motion_prompts: list[str], aspect_ratio: str) -> dict | None:
    """Sidecar QA path: whole storyboard page -> WERYDANCE previs-page video."""
    if not PREVIS_PAGE_MOTION or ADS_DIALOGUE_MODE:
        return None
    groups = _previs_page_groups(script)
    character_sheet = os.environ.get("ADR_PREVIS_CHARACTER_SHEET", "").strip()
    has_character_sheet = bool(character_sheet and os.path.exists(character_sheet))
    qa = {
        "mode": "storyboard_previs_page_to_werydance",
        "enabled": True,
        "interface": "almighty-reference-to-video",
        "model": "WERYDANCE_2_0",
        "aspect_ratio": aspect_ratio,
        "resolution": os.environ.get("ADR_PREVIS_PAGE_RESOLUTION", "720p"),
        "total_pages": len(groups),
        "character_sheet": character_sheet if has_character_sheet else None,
        "records": [],
        "policy": "sidecar_previs_page_motion_qa_only_not_used_for_final_concat",
        "manual_visual_checks_required": [
            "page_is_not_rendered_as_document",
            "panel_order_is_followed",
            "no_grid_lines_or_panel_borders",
            "no_shot_numbers_labels_arrows_or_captions",
            "continuity_matches_storyboard_pacing",
        ],
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }
    if not groups:
        qa.update({"pass": False, "reason": "no_storyboard_grid_pages"})
        _write_previs_page_motion_qa(qa)
        return qa

    tg(f"🎞 Previs page motion QA 启动：storyboard page × {len(groups)}")
    for group_no, (grid_path, scene_indices, group) in enumerate(groups, start=1):
        group_key = f"{scene_indices[0] + 1:02d}_{scene_indices[-1] + 1:02d}"
        out_path = OUTPUT_DIR / f"previs_page_{group_key}.mp4"
        record = {
            "group": group_no,
            "scene_start": scene_indices[0] + 1,
            "scene_end": scene_indices[-1] + 1,
            "scene_indices": [i + 1 for i in scene_indices],
            "storyboard_page": grid_path,
            "pass": False,
        }
        qa["records"].append(record)
        try:
            existing_tid = _load_previs_page_tasks().get(group_key)
            if existing_tid:
                record.update({"task_id": existing_tid, "resumed_task": True})
                ok, info = _poll_video_task_download(existing_tid, out_path, f"previs page {group_no}")
                record.update(info)
                record["pass"] = ok
                if ok or record.get("reason") == "task_failed":
                    _remove_previs_page_task(group_key)
                _write_previs_page_motion_qa(qa)
                continue

            image_urls = [_upload_to_weryai(grid_path)]
            if has_character_sheet:
                image_urls.append(_upload_to_weryai(character_sheet))
            duration = _previs_page_duration(group)
            prompt = _previs_page_group_prompt(group, scene_indices, motion_prompts, has_character_sheet)
            _wait_motion_submit_slot(f"previs page {group_no}")
            r = req_post("/generation/almighty-reference-to-video", {
                "model": "WERYDANCE_2_0",
                "images": image_urls,
                "prompt": prompt,
                "duration": duration,
                "aspect_ratio": aspect_ratio,
                "resolution": qa["resolution"],
                "generate_audio": "false",
                "video_number": 1,
            }, timeout=30)
            task_id = r.get("data", {}).get("task_id") or (r.get("data", {}).get("task_ids") or [None])[0]
            record.update({
                "image_urls": image_urls,
                "submit_duration": duration,
                "task_id": task_id,
            })
            if not task_id:
                record.update({"reason": "submit_without_task_id", "response": r})
                continue
            _save_previs_page_task(group_key, task_id)
            ok, info = _poll_video_task_download(task_id, out_path, f"previs page {group_no}")
            record.update(info)
            record["pass"] = ok
            if ok or record.get("reason") == "task_failed":
                _remove_previs_page_task(group_key)
            if ok:
                tg(f"🎞 Previs page {record['scene_start']}-{record['scene_end']} ✓")
            else:
                tg(f"⚠️ Previs page {record['scene_start']}-{record['scene_end']} 失败：{record.get('reason')}")
        except Exception as e:
            record.update({"pass": False, "reason": str(e)})
            tg(f"⚠️ Previs page {record['scene_start']}-{record['scene_end']} 异常：{str(e)[:120]}")
        _write_previs_page_motion_qa(qa)

    success_count = sum(1 for r in qa["records"] if r.get("pass"))
    qa.update({
        "success_count": success_count,
        "total_groups": len(qa["records"]),
        "pass": success_count == len(qa["records"]) and success_count > 0,
        "finalized_at": datetime.now().isoformat(timespec="seconds"),
    })
    _write_previs_page_motion_qa(qa)
    if qa["pass"]:
        tg(f"✅ Previs page motion QA 完成：{success_count}/{len(qa['records'])} 组通过")
    else:
        tg(f"⚠️ Previs page motion QA 未全通过：{success_count}/{len(qa['records'])} 组")
    return qa


def _generate_grid_multiref_motion_segments(script: list[dict], motion_prompts: list[str], aspect_ratio: str) -> dict | None:
    """Sidecar QA path: clean grid panels -> WERYDANCE multi-reference video chunks.

    It intentionally does not replace seg_N.mp4 because one multi-reference video spans
    multiple narration beats and needs separate timing policy before entering the main cut.
    """
    if not STORYBOARD_GRID_MULTIREF_MOTION or (ADS_DIALOGUE_MODE and ADSD_LIP_SYNC_EXPERIMENT):
        return None
    refs = [
        (i, scene)
        for i, scene in enumerate(script)
        if scene.get("storyboard_grid_mode") and scene.get("img_path") and os.path.exists(scene.get("img_path"))
    ]
    qa = {
        "mode": "storyboard_grid_clean_refs_to_werydance_multiref",
        "enabled": True,
        "interface": "almighty-reference-to-video",
        "model": "WERYDANCE_2_0",
        "aspect_ratio": aspect_ratio,
        "resolution": os.environ.get("ADR_STORYBOARD_GRID_MULTIREF_RESOLUTION", "720p"),
        "group_size": _grid_multiref_group_size(),
        "total_refs": len(refs),
        "records": [],
        "policy": "main_path_when_STORYBOARD_GRID_MULTIREF_MAIN_else_sidecar_qa",
        "manual_visual_checks_required": [
            "shot_order_matches_reference_order",
            "no_shot_numbers_or_arrows",
            "no_grid_or_panel_borders",
            "no_captions_or_subtitles",
            "character_and_setting_consistency",
        ],
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }
    if len(refs) < 2:
        qa.update({"pass": False, "reason": "not_enough_grid_refs"})
        _write_grid_multiref_motion_qa(qa)
        return qa

    sheet_url = None
    sheet_path = OUTPUT_DIR / "character_sheet.png"
    if (
        STORYBOARD_GRID_MULTIREF_MAIN
        and sheet_path.exists()
        and sheet_path.stat().st_size > 100000
        and os.environ.get("ADR_GRID_MULTIREF_USE_CHARACTER_SHEET", "1").strip().lower() not in ("0", "false", "no", "off")
    ):
        try:
            sheet_url = _upload_to_weryai(str(sheet_path))
            qa["character_sheet"] = str(sheet_path)
            qa["character_sheet_url"] = sheet_url
            qa["reference_order"] = "character_sheet_first_then_storyboard_clean_refs"
            tg("🧬 Grid multi-ref 已加入 character sheet 身份参考")
        except Exception as e:
            qa.setdefault("warnings", []).append(f"character_sheet_upload_failed:{e}")
            log(f"grid_multiref character_sheet upload skipped: {e}")

    tg(f"🧪 Grid multi-ref motion QA 启动：clean refs {len(refs)} 张，每组 {qa['group_size']} 张")
    group_size = qa["group_size"]
    for group_no, start in enumerate(range(0, len(refs), group_size), start=1):
        group_pairs = refs[start:start + group_size]
        if len(group_pairs) < 2:
            continue
        scene_indices = [i for i, _ in group_pairs]
        group = [scene for _, scene in group_pairs]
        record = {
            "group": group_no,
            "scene_start": scene_indices[0] + 1,
            "scene_end": scene_indices[-1] + 1,
            "scene_indices": [i + 1 for i in scene_indices],
            "image_paths": [scene.get("img_path") for scene in group],
            "pass": False,
        }
        qa["records"].append(record)
        group_key = f"{scene_indices[0] + 1:02d}_{scene_indices[-1] + 1:02d}"
        try:
            existing_tid = _load_grid_multiref_tasks().get(group_key)
            out_path = OUTPUT_DIR / f"grid_multiref_{group_key}.mp4"
            if existing_tid:
                record.update({"task_id": existing_tid, "resumed_task": True})
                ok, info = _poll_video_task_download(existing_tid, out_path, f"grid multi-ref {group_no}")
                record.update(info)
                record["pass"] = ok
                if ok or record.get("reason") == "task_failed":
                    _remove_grid_multiref_task(group_key)
                if ok:
                    tg(f"🧪 Grid multi-ref {record['scene_start']}-{record['scene_end']} ✓ (resumed)")
                else:
                    tg(f"⚠️ Grid multi-ref {record['scene_start']}-{record['scene_end']} 未完成：{record.get('reason')}")
                _write_grid_multiref_motion_qa(qa)
                continue
            image_urls = ([sheet_url] if sheet_url else []) + [_upload_to_weryai(scene["img_path"]) for scene in group]
            duration = _grid_multiref_duration(group)
            prompt = _grid_multiref_prompt(group, scene_indices[0], motion_prompts, has_character_sheet=bool(sheet_url))
            _wait_motion_submit_slot(f"grid multi-ref {group_no}")
            r = req_post("/generation/almighty-reference-to-video", {
                "model": "WERYDANCE_2_0",
                "images": image_urls,
                "prompt": prompt,
                "duration": duration,
                "aspect_ratio": aspect_ratio,
                "resolution": qa["resolution"],
                "generate_audio": "false",
                "video_number": 1,
            }, timeout=30)
            task_id = r.get("data", {}).get("task_id") or (r.get("data", {}).get("task_ids") or [None])[0]
            record.update({
                "image_urls": image_urls,
                "submit_duration": duration,
                "task_id": task_id,
            })
            if not task_id:
                record.update({"reason": "submit_without_task_id", "response": r})
                continue
            _save_grid_multiref_task(group_key, task_id)
            ok, info = _poll_video_task_download(task_id, out_path, f"grid multi-ref {group_no}")
            record.update(info)
            record["pass"] = ok
            if ok or record.get("reason") == "task_failed":
                _remove_grid_multiref_task(group_key)
            if ok:
                tg(f"🧪 Grid multi-ref {record['scene_start']}-{record['scene_end']} ✓")
            else:
                tg(f"⚠️ Grid multi-ref {record['scene_start']}-{record['scene_end']} 失败：{record.get('reason')}")
        except Exception as e:
            record.update({"pass": False, "reason": str(e)})
            tg(f"⚠️ Grid multi-ref {record['scene_start']}-{record['scene_end']} 异常：{str(e)[:120]}")
        _write_grid_multiref_motion_qa(qa)

    success_count = sum(1 for r in qa["records"] if r.get("pass"))
    qa.update({
        "success_count": success_count,
        "total_groups": len(qa["records"]),
        "pass": success_count == len(qa["records"]) and success_count > 0,
        "finalized_at": datetime.now().isoformat(timespec="seconds"),
    })
    _write_grid_multiref_motion_qa(qa)
    if qa["pass"]:
        tg(f"✅ Grid multi-ref motion QA 完成：{success_count}/{len(qa['records'])} 组通过")
    else:
        tg(f"⚠️ Grid multi-ref motion QA 未全通过：{success_count}/{len(qa['records'])} 组")
    # P1：若开主路径模式 → concat 成功组成 grid_multiref_combined.mp4，step7 会用作 raw_concat
    # 容错策略：要求 ≥ MIN_PASS_RATIO 通过（默认 0.75），不要求全 pass
    # （poll_timeout 等 transient 失败常见，3/4 通过应允许进入 main 路径）
    if STORYBOARD_GRID_MULTIREF_MAIN:
        total = len(qa["records"])
        min_ratio = float(os.environ.get("ADR_GRID_MULTIREF_MAIN_MIN_PASS_RATIO", "0.75"))
        pass_ratio = (success_count / total) if total > 0 else 0.0
        if pass_ratio >= min_ratio and success_count >= 1:
            try:
                combined_path = _grid_multiref_concat_groups_partial(qa["records"])
                if combined_path:
                    qa["combined_path"] = combined_path
                    qa["combined_duration"] = round(ffprobe_duration(combined_path), 3)
                    qa["combined_groups_used"] = success_count
                    qa["combined_groups_skipped"] = total - success_count
                    qa["combined_pass_ratio"] = round(pass_ratio, 3)
                    _write_grid_multiref_motion_qa(qa)
                    tg(f"🎬 Grid multi-ref main: {success_count}/{total} 组 → grid_multiref_combined.mp4 "
                       f"({qa['combined_duration']}s, 跳过 {total - success_count} 失败组)")
                else:
                    tg("⚠️ Grid multi-ref main concat 失败，step7 将回退逐镜拼接")
            except Exception as e:
                log(f"grid_multiref concat 异常：{e}")
                tg(f"⚠️ Grid multi-ref main concat 异常：{str(e)[:120]}")
        else:
            tg(f"⚠️ Grid multi-ref main 跳过 concat：通过率 {pass_ratio:.0%} < 阈值 {min_ratio:.0%} "
               f"(或仅 {success_count} 组通过)，step7 回退逐镜拼接")
    return qa


def _grid_multiref_concat_groups(records: list[dict]) -> str | None:
    """严格模式：全 pass 才返回 combined。保留兼容性。"""
    if not records:
        return None
    paths: list[str] = []
    for rec in sorted(records, key=lambda r: int(r.get("scene_start") or 0)):
        if not rec.get("pass"):
            return None
        p = rec.get("path")
        if not p or not os.path.exists(p):
            return None
        paths.append(p)
    if not paths:
        return None
    return _grid_multiref_concat_paths(paths)


def _grid_multiref_concat_groups_partial(records: list[dict]) -> str | None:
    """宽松模式：只 concat pass 的 group，跳过失败的。
    保留场景顺序：scene_start 排序后只挑 pass 的；失败 group 直接跳过（视频帧上是 jump cut）。"""
    if not records:
        return None
    paths: list[str] = []
    for rec in sorted(records, key=lambda r: int(r.get("scene_start") or 0)):
        if not rec.get("pass"):
            continue
        p = rec.get("path")
        if not p or not os.path.exists(p):
            continue
        paths.append(p)
    if not paths:
        return None
    return _grid_multiref_concat_paths(paths)


def _grid_multiref_concat_paths(paths: list[str]) -> str | None:
    """统一 fps + 编码再 concat，避免不同组帧率/码率差异。"""
    if not paths:
        return None
    out_path = str(OUTPUT_DIR / "grid_multiref_combined.mp4")
    concat_list = OUTPUT_DIR / "grid_multiref_concat.txt"
    with open(concat_list, "w", encoding="utf-8") as f:
        for p in paths:
            f.write(f"file '{p}'\n")
    # 统一 fps + 编码再 concat，避免不同组帧率/码率差异导致 concat demuxer 拒绝
    normalized: list[str] = []
    for i, p in enumerate(paths):
        np_path = str(OUTPUT_DIR / f"grid_multiref_norm_{i:02d}.mp4")
        ffmpeg(
            "-i", p,
            "-vf", "fps=24",
            "-c:v", "libx264", "-crf", "20", "-preset", "medium",
            "-an",
            np_path,
            timeout=180,
        )
        normalized.append(np_path)
    norm_list = OUTPUT_DIR / "grid_multiref_concat_norm.txt"
    with open(norm_list, "w", encoding="utf-8") as f:
        for p in normalized:
            f.write(f"file '{p}'\n")
    ffmpeg("-f", "concat", "-safe", "0", "-i", str(norm_list),
           "-c", "copy", out_path, timeout=120)
    return out_path


def _lip_sync_slot_duration(script: list[dict], idx: int) -> float:
    scene = script[idx]
    if idx < len(script) - 1:
        return max(1.0, float(script[idx + 1].get("audio_start", scene.get("audio_end", 0))) - float(scene.get("audio_start", 0)))
    return max(1.0, float(scene.get("audio_end", scene.get("audio_start", 0) + scene.get("dur", 1))) - float(scene.get("audio_start", 0)))


def _adsd_lip_sync_prompt(scene: dict, safe_retry: bool = False) -> str:
    speaker = scene.get("speaker") or "speaker"
    role = f"historical onsite character internally identified as {speaker}"
    pov = (
        " First-person onsite observer POV: viewer stands beside the active speaker or at the crowd/door/table edge, "
        "close enough to see the face and mouth, with framing chosen by topic-era immersion."
        if ADSD_ONSITE_POV_MODE else ""
    )
    expr = _emotion_expression_phrase(scene.get("emotion"))
    _no_text_ban = (
        "ABSOLUTELY NO TEXT IN FRAME: do not burn in subtitles, do not render Chinese/English captions, "
        "do not draw chyron / lower-thirds / speech bubbles / character name tags / on-screen typography. "
        "The frame must be PURELY cinematic image — no text of any kind. "
    )
    if safe_retry:
        return (
            f"{_no_text_ban}"
            "Period dialogue scene with authentic emotional expression. "
            "If a character sheet reference is provided, use it only to preserve the active speaker identity; do not render the sheet itself. "
            f"{_adsd_gender_lock_phrase(scene.get('voice_gender'))} "
            f"Active speaker is the {role}; any other onsite characters listen silently. "
            "The active speaker follows the provided Chinese audio reference with natural mouth movement. "
            f"Expression: {expr}. "
            f"Visible mouth with mood-matching face (NOT a frozen documentary mask), natural micro head movement.{pov} "
            f"Keep the scene immersive for its topic era.{_werydance_caption_instruction(scene)} "
            "No speaker name labels, no logos, no watermark, no branded style references."
        )
    shot = scene.get("shot", "")
    return (
        f"{_no_text_ban}"
        "Historically grounded period dialogue scene with authentic emotional expression. "
        "If a character sheet reference is provided, use it only to preserve the active speaker identity; do not render the sheet itself. "
        f"{_adsd_gender_lock_phrase(scene.get('voice_gender'))} "
        f"Active speaker is the {role}; any other people only listen or react. Do not display the speaker name. "
        "Use the uploaded Chinese audio reference as the only dialogue source. "
        f"Mouth movement must synchronize with the audio reference; keep mouth visible with natural jaw motion.{pov} "
        f"Active speaker expression: {expr}. Avoid generic neutral documentary mask — let mood read on the face. "
        f"Scene action: {shot}. "
        "Camera style: handheld documentary realism — subtle organic shake, slight breathing in framing, natural lens micro-drift, gentle parallax. "
        "Lighting: practical real-world lighting with motivated shadows; mild film grain; subtle lens vignette. "
        "Avoid synthetic-looking smooth interpolation; let small imperfections (eye blinks, micro head adjustments, breath movement, cloth ripple) read as real-world capture. "
        "Keep the same face and period clothing, keep framing immersive for its topic era. "
        f"{_werydance_caption_instruction(scene)} No speaker labels, logos, or watermarks."
    )[:2000]


def _adsd_broll_motion_prompt(scene: dict, safe_retry: bool = False) -> str:
    """B-roll / voice-over 模式：不传 audio，让 WERYDANCE 走 motion 模式，画面全员可动。
    用于旁白等不需要说话人正脸 lip-sync 的 turn。
    动作题材（武侠/修真/打斗）自动追加 action prompt 强化镜头。"""
    shot = scene.get("shot", "")
    text = scene.get("text", "")
    pov = (
        " First-person onsite observer POV: viewer stands within the scene, observing as the moment unfolds; no character speaks directly to camera."
        if ADSD_ONSITE_POV_MODE else ""
    )
    action_boost = _action_motion_fragment() if _is_action_scene(text, shot) else ""
    expr = _emotion_expression_phrase(scene.get("emotion"))
    _no_text_ban = (
        "ABSOLUTELY NO TEXT IN FRAME: do not burn in subtitles, do not render Chinese/English captions, "
        "no chyron / lower-thirds / speech bubbles / on-screen typography. Purely cinematic image. "
    )
    base = (
        f"{_no_text_ban}"
        "Cinematic documentary B-roll, voice-over scene — real-world cinematography style with authentic emotional expression. "
        "If a character sheet reference is provided, use it only to preserve character identity across panels; do not render the sheet itself. "
        f"{_adsd_gender_lock_phrase(scene.get('voice_gender'))} "
        "No character speaks directly to camera; no lip-sync needed; no mouth animation prioritized. "
        f"Character expression and body language matching mood: {expr}. Avoid blank serious face — let mood read in eyes, brow, posture. "
        "Camera style: handheld documentary realism with organic shake and breathing framing; or smooth gimbal dolly when emphasizing motion direction. "
        "Subjects move with full-body engagement: walking, gesturing, working, reacting — NOT subtle micro-twitches alone. "
        "Lighting: practical real-world sources with motivated shadows; film grain; mild lens vignette; depth of field. "
        "All visible elements (characters, objects, environment) carry kinetic life: garment ripple, hair flow, ambient particles, foliage drift, water ripple. "
        "Avoid synthetic smooth interpolation — let small imperfections read as real capture. "
        f"{action_boost}"
    )
    if safe_retry:
        return (base +
            f"Scene unfolds naturally without dialogue.{pov} "
            "No speaker name labels, no logos, no watermark, no branded style references."
        )[:2000]
    return (base +
        f"Scene action: {shot or text[:120]}.{pov} "
        "Keep the same face and period clothing across panels; immersive for its topic era. "
        "No speaker labels, no logos, no watermark, no branded style references."
    )[:2000]


def _adsd_silent_b_motion_prompt(scene: dict, safe_retry: bool = False) -> str:
    """silent_b 专属 prompt：氛围呼吸位，无人说话，画面呼吸。

    与 broll_motion 区别：
      broll_motion (narrated_b) 是「有人但无嘴」(剪影/远景/群像/雕像)
      silent_b 是「呼吸位」(空镜/物件/环境/远景人影渺小)
    """
    shot = scene.get("shot", "")
    broll_rule = (scene.get("broll_rule") or "").strip().lower()
    rule_emphasis = {
        "empty_scene": "Empty scene composition: architecture, sky, water, light shafts. No human as primary subject.",
        "object_close_up": "Object close-up: hero object centered, shallow depth of field, slow pull / push, no human face.",
        "environmental": "Environmental atmosphere: weather, light, time-of-day, ambient particles, no character speaking.",
        "distant_figure": "Distant figure(s) in wide shot: silhouettes / tiny humans against landscape, viewer cannot read mouth or face.",
    }.get(broll_rule, "Atmospheric breath shot: contemplative pacing, no dialogue, no character looking at camera.")
    _no_text_ban = (
        "ABSOLUTELY NO TEXT IN FRAME: no subtitles, no captions, no chyron, no on-screen typography. "
    )
    base = (
        f"{_no_text_ban}"
        "Cinematic documentary breathing shot — pure atmospheric mood, no spoken dialogue, no lip-sync, no character close-up. "
        f"{rule_emphasis} "
        "Slow contemplative camera move (glide / slow push / hold). "
        "Lighting: practical real-world sources with motivated shadows; mild film grain; lens vignette; soft depth of field. "
        "Ambient kinetic life: dust motes, light flicker, water ripple, foliage drift, fabric breath, particles in air. "
        "No synthetic smoothness — let it read as captured reality. "
    )
    if safe_retry:
        return (base + "Scene unfolds without people speaking. No logos, no watermark.")[:2000]
    return (base +
        f"Scene: {shot or 'environmental cutaway, mood setting'}. "
        "No speaker labels, no logos, no watermark, no branded style references."
    )[:2000]


def _adsd_almighty_audio_dub_prompt(scene: dict, safe_retry: bool = False) -> str:
    """Experimental: let Almighty Reference generate spoken audio from prompt text using uploaded audio as voice reference."""
    speaker = scene.get("speaker") or "speaker"
    dialogue = re.sub(r"\s+", " ", str(scene.get("text") or "")).strip()
    dialogue = dialogue[:220]
    role = f"active onsite character internally identified as {speaker}"
    pov = (
        " First-person onsite observer POV, camera close enough to see face and mouth."
        if ADSD_ONSITE_POV_MODE else ""
    )
    if safe_retry:
        return (
            "Create a realistic Chinese spoken documentary scene. "
            "Use uploaded image references only for speaker identity, costume, era, lighting, and composition. "
            "Use uploaded audio only as voice timbre and speaking-style reference, then generate new synchronized speech. "
            f"{_adsd_gender_lock_phrase(scene.get('voice_gender'))} "
            f"The {role} speaks exactly this Chinese line: 「{dialogue}」. "
            f"Natural lip sync, stable face, subtle head motion.{pov} "
            f"{_werydance_caption_instruction(scene)} No speaker labels, logos, or watermarks."
        )[:1000]
    shot = scene.get("shot", "")
    return (
        "Create a historically grounded Chinese spoken documentary scene with generated audio. "
        "Use the uploaded audio as a voice/timbre reference only: preserve the same gender, tone color, age impression, "
        "pace, emotional delivery, and speaking style. Do not use it as background music. "
        "Generate clear Mandarin speech and synchronize the mouth movement to the generated speech. "
        "Use uploaded image references only to lock identity, costume, era, location, lighting, and composition; "
        "do not render reference sheets or storyboard pages. "
        f"{_adsd_gender_lock_phrase(scene.get('voice_gender'))} "
        f"The {role} speaks exactly this Chinese dialogue and nothing else: 「{dialogue}」. "
        f"Scene action: {shot}. Visible mouth, stable face, natural jaw motion, realistic human timing.{pov} "
        f"{_werydance_caption_instruction(scene)} No speaker labels, logos, or watermarks."
    )[:1000]


def _postprocess_lip_sync_segment(src_video: str, scene: dict, target_dur: float) -> bool:
    """Normalize Werydance silent lip video to ADR segment size and exact timeline duration.

    HADSD timed 模式下 target_dur 远大于 WERYDANCE 实际产出（slot 包含 silence pad），
    原 tpad=clone 会冻末帧 5-9s → 人脸僵住。
    改用当前 panel still + 缓慢 zoom（Ken Burns）做 pad，视觉像 cutaway 而非死帧。
    """
    vid_path = scene["vid_path"]
    src_dur = ffprobe_duration(src_video)
    pad = max(0.0, target_dur - src_dur)
    panel_path = scene.get("img_path", "")
    use_panel_pad = (
        pad > 0.04
        and panel_path
        and os.path.exists(panel_path)
        and os.environ.get("ADR_ADSD_PAD_WITH_PANEL", "1").strip().lower() not in ("0", "false", "no", "off")
    )
    if use_panel_pad:
        zoompan_frames = max(1, int(pad * 24))
        # 双输入：[0]werydance video + [1]panel still 循环 pad 秒
        # Ken Burns: zoom 从 1.0 缓慢推到 1.06，居中
        filter_complex = (
            f"[0:v]scale={VIDEO_W}:{VIDEO_H}:force_original_aspect_ratio=increase,"
            f"crop={VIDEO_W}:{VIDEO_H},setsar=1[werynorm];"
            f"[1:v]scale={VIDEO_W*2}:{VIDEO_H*2}:force_original_aspect_ratio=increase,"
            f"crop={VIDEO_W*2}:{VIDEO_H*2},"
            f"zoompan=z='min(1.0+0.0008*on,1.06)':"
            f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
            f"d={zoompan_frames}:s={VIDEO_W}x{VIDEO_H}:fps=24,"
            f"setsar=1[panel];"
            f"[werynorm][panel]concat=n=2:v=1:a=0,"
            f"trim=duration={target_dur:.3f},setpts=PTS-STARTPTS[out]"
        )
        try:
            ffmpeg(
                "-i", src_video,
                "-loop", "1", "-t", f"{pad:.3f}", "-i", panel_path,
                "-filter_complex", filter_complex,
                "-map", "[out]",
                "-an",
                "-c:v", "libx264", "-crf", "20", "-preset", "medium",
                "-pix_fmt", "yuv420p",
                vid_path,
                timeout=240,
            )
            return os.path.exists(vid_path) and os.path.getsize(vid_path) > 10000
        except Exception as e:
            log(f"[lip-sync postprocess] panel-pad Ken Burns 失败回退 tpad clone: {e}")
    # 回退 / 短 pad / 无 panel 路径：原 tpad clone
    vf = (
        f"scale={VIDEO_W}:{VIDEO_H}:force_original_aspect_ratio=increase,"
        f"crop={VIDEO_W}:{VIDEO_H},setsar=1"
    )
    if pad > 0.04:
        vf += f",tpad=stop_mode=clone:stop_duration={pad:.3f}"
    vf += f",trim=duration={target_dur:.3f},setpts=PTS-STARTPTS"
    ffmpeg(
        "-i", src_video,
        "-vf", vf,
        "-an",
        "-c:v", "libx264", "-crf", "20", "-preset", "medium",
        "-pix_fmt", "yuv420p",
        vid_path,
        timeout=180,
    )
    return os.path.exists(vid_path) and os.path.getsize(vid_path) > 10000


def _postprocess_audio_dub_segment(src_video: str, scene: dict, target_dur: float) -> bool:
    """Normalize Almighty audio-dub video while preserving generated segment audio for QA sidecars.

    关键：WERYDANCE 输出 ~5s 完整克隆语音，master_voice TTS 时长往往更短。
    若按 target_dur 硬 atrim 会截断克隆语音 → 改成 effective_dur = max(target_dur, src_dur)
    保留完整克隆，后续 retiming 把真实时长写回 scene 让 timeline 同步拉长。

    pad 段视频用 panel still + Ken Burns 替代 tpad clone（解决冻人脸 bug）；
    pad 段音频仍走 apad 静音填充。
    """
    vid_path = scene["vid_path"]
    src_dur = ffprobe_duration(src_video)
    # 不 trim raw audio：克隆语音可能比 master_voice TTS 长，硬截会切掉尾部
    effective_dur = max(target_dur, src_dur)
    pad = max(0.0, effective_dur - src_dur)
    scene["_audio_dub_effective_dur"] = effective_dur
    panel_path = scene.get("img_path", "")
    use_panel_pad = (
        pad > 0.04
        and panel_path
        and os.path.exists(panel_path)
        and os.environ.get("ADR_ADSD_PAD_WITH_PANEL", "1").strip().lower() not in ("0", "false", "no", "off")
    )
    if use_panel_pad:
        zoompan_frames = max(1, int(pad * 24))
        # 三个 stream：[0:v] wery video, [0:a] wery audio, [1:v] panel still
        # 视频：normalize wery + concat panel Ken Burns，trim 到 effective_dur
        # 音频：apad 填静音到 effective_dur（不 atrim raw 部分）
        filter_complex = (
            f"[0:v]scale={VIDEO_W}:{VIDEO_H}:force_original_aspect_ratio=increase,"
            f"crop={VIDEO_W}:{VIDEO_H},setsar=1[werynorm];"
            f"[1:v]scale={VIDEO_W*2}:{VIDEO_H*2}:force_original_aspect_ratio=increase,"
            f"crop={VIDEO_W*2}:{VIDEO_H*2},"
            f"zoompan=z='min(1.0+0.0008*on,1.06)':"
            f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
            f"d={zoompan_frames}:s={VIDEO_W}x{VIDEO_H}:fps=24,"
            f"setsar=1[panel];"
            f"[werynorm][panel]concat=n=2:v=1:a=0,"
            f"trim=duration={effective_dur:.3f},setpts=PTS-STARTPTS[vout];"
            f"[0:a]apad=pad_dur={pad:.3f},atrim=duration={effective_dur:.3f},asetpts=PTS-STARTPTS[aout]"
        )
        try:
            ffmpeg(
                "-i", src_video,
                "-loop", "1", "-t", f"{pad:.3f}", "-i", panel_path,
                "-filter_complex", filter_complex,
                "-map", "[vout]",
                "-map", "[aout]",
                "-c:v", "libx264", "-crf", "20", "-preset", "medium",
                "-c:a", "aac", "-b:a", "128k",
                "-pix_fmt", "yuv420p",
                vid_path,
                timeout=240,
            )
            return os.path.exists(vid_path) and os.path.getsize(vid_path) > 10000
        except Exception as e:
            log(f"[audio-dub postprocess] panel-pad Ken Burns 失败回退 tpad clone: {e}")
    # 回退 / 短 pad / 无 panel 路径：原 tpad clone（仍按 effective_dur 处理）
    vf = (
        f"scale={VIDEO_W}:{VIDEO_H}:force_original_aspect_ratio=increase,"
        f"crop={VIDEO_W}:{VIDEO_H},setsar=1"
    )
    if pad > 0.04:
        vf += f",tpad=stop_mode=clone:stop_duration={pad:.3f}"
    vf += f",trim=duration={effective_dur:.3f},setpts=PTS-STARTPTS"
    af = f"apad=pad_dur={pad:.3f},atrim=duration={effective_dur:.3f},asetpts=PTS-STARTPTS"
    try:
        ffmpeg(
            "-i", src_video,
            "-vf", vf,
            "-af", af,
            "-c:v", "libx264", "-crf", "20", "-preset", "medium",
            "-c:a", "aac", "-b:a", "128k",
            "-pix_fmt", "yuv420p",
            vid_path,
            timeout=180,
        )
    except Exception as e:
        log(f"audio-dub postprocess 保留音频失败，回退静音视频处理: {e}")
        return _postprocess_lip_sync_segment(src_video, scene, target_dur)
    return os.path.exists(vid_path) and os.path.getsize(vid_path) > 10000


def _lips_change_repair_segment(idx: int, scene: dict, target_dur: float) -> tuple[bool, dict]:
    """Second-stage lips repair using WeryAI video-lips-change on an existing segment."""
    info = {
        "enabled": ADSD_LIPS_CHANGE_REPAIR,
        "interface": "video-lips-change",
        "turn": idx + 1,
        "speaker": scene.get("speaker"),
        "source_video": scene.get("vid_path"),
        "source_audio": scene.get("dialogue_audio_mp3") or scene.get("dialogue_audio"),
    }
    if not ADSD_LIPS_CHANGE_REPAIR:
        return False, info
    source_video = scene.get("vid_path")
    source_audio = scene.get("dialogue_audio_mp3") or scene.get("dialogue_audio")
    if not source_video or not os.path.exists(source_video):
        info.update({"pass": False, "reason": "missing_source_video"})
        return False, info
    if not source_audio or not os.path.exists(source_audio):
        info.update({"pass": False, "reason": "missing_source_audio"})
        return False, info
    try:
        video_url = _upload_to_weryai(source_video)
        audio_url = _upload_to_weryai(source_audio)
        task_id = None
        response = None
        for attempt in range(3):
            try:
                _wait_motion_submit_slot(f"lips-change {idx+1}")
                response = req_post("/generation/video-lips-change", {
                    "video_url": video_url,
                    "audio_url": audio_url,
                }, timeout=30)
                task_id = response.get("data", {}).get("task_id") or (response.get("data", {}).get("task_ids") or [None])[0]
                if task_id:
                    break
            except Exception as e:
                if attempt < 2:
                    wait_s = 5 * (attempt + 1)
                    log(f"[lips-change {idx}] submit 失败（第 {attempt+1}/3 次）：{e}，{wait_s}s 后重试")
                    time.sleep(wait_s)
                    continue
                raise
        if not task_id:
            info.update({"pass": False, "reason": "submit_without_task_id", "response": response})
            return False, info
        for iteration in range(181):
            try:
                s = req_get(f"/generation/{task_id}/status")
                data = s.get("data", {})
                st = data.get("task_status", "")
                if iteration == 0 or iteration % 12 == 0 or st in ("succeed", "failed"):
                    log(f"[lips-change {idx}] poll #{iteration+1}: {st}")
                if st == "succeed":
                    vid_url = _extract_video_url(data)
                    if not vid_url:
                        info.update({"pass": False, "task_id": task_id, "reason": "succeed_without_video_url"})
                        return False, info
                    raw_path = str(OUTPUT_DIR / f"lips_change_raw_{idx}.mp4")
                    urllib.request.urlretrieve(vid_url, raw_path)
                    ok = _postprocess_lip_sync_segment(raw_path, scene, target_dur)
                    final_dur = ffprobe_duration(scene["vid_path"]) if ok else None
                    info.update({
                        "pass": ok,
                        "task_id": task_id,
                        "raw_video_path": raw_path,
                        "final_segment_path": scene["vid_path"],
                        "final_segment_duration": final_dur,
                        "duration_delta": abs((final_dur or 0) - target_dur) if final_dur is not None else None,
                        "clip_duration_match_pass": final_dur is not None and abs(final_dur - target_dur) <= 0.25,
                    })
                    return ok, info
                if st == "failed":
                    info.update({"pass": False, "task_id": task_id, "reason": "task_failed", "response": data})
                    return False, info
            except Exception as e:
                if iteration in (0, 12, 60, 120):
                    log(f"[lips-change {idx}] poll 异常: {e}")
            time.sleep(5)
        info.update({"pass": False, "task_id": task_id, "reason": "poll_timeout"})
        return False, info
    except Exception as e:
        info.update({"pass": False, "reason": str(e)})
        return False, info


def _load_lips_change_requested_turns() -> set[int]:
    """1-based turn indexes requested by manual QA for lips-change repair."""
    p = Path("/tmp/adr_lips_repair_turns.json")
    if not p.exists():
        return set()
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return {int(x) for x in data if int(x) > 0}
        if isinstance(data, dict):
            vals = data.get("turns") or data.get("repair_turns") or []
            return {int(x) for x in vals if int(x) > 0}
    except Exception as e:
        log(f"读取 lips-change 指定 turn 失败: {e}")
    return set()


def _parse_turn_set(value) -> set[int]:
    turns: set[int] = set()
    if value is None:
        return turns
    if isinstance(value, dict):
        value = value.get("turns") or value.get("repair_turns") or value.get("voice_repair_turns") or []
    if isinstance(value, str):
        parts = re.split(r"[\s,，;；]+", value.strip())
    elif isinstance(value, (list, tuple, set)):
        parts = list(value)
    else:
        parts = [value]
    for part in parts:
        try:
            turn = int(part)
        except Exception:
            continue
        if turn > 0:
            turns.add(turn)
    return turns


def _load_motion_voice_repair_turns() -> set[int]:
    """1-based turn indexes requested by manual QA for voice-timbre repair."""
    turns = _parse_turn_set(os.environ.get("ADR_VOICE_REPAIR_TURNS") or os.environ.get("ADR_MOTION_VOICE_REPAIR_TURNS"))
    p = Path("/tmp/adr_voice_repair_turns.json")
    if p.exists():
        try:
            turns |= _parse_turn_set(json.loads(p.read_text(encoding="utf-8")))
        except Exception as e:
            log(f"读取 motion voice-repair 指定 turn 失败: {e}")
    return turns


def _voice_assets_file() -> Path:
    return Path(__file__).resolve().parent / "voice_assets" / "voice_assets.json"


_VOICE_ASSETS_CACHE: dict | None = None


def _load_voice_assets() -> dict:
    global _VOICE_ASSETS_CACHE
    if _VOICE_ASSETS_CACHE is not None:
        return _VOICE_ASSETS_CACHE
    p = _voice_assets_file()
    if not p.exists():
        _VOICE_ASSETS_CACHE = {"assets": []}
        return _VOICE_ASSETS_CACHE
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            data = {"assets": []}
    except Exception as e:
        log(f"voice_assets.json 读取失败: {e}")
        data = {"assets": []}
    _VOICE_ASSETS_CACHE = data
    return data


def _select_voice_asset_reference(scene: dict, *, mode: str = "adsd", ref_offset: int = 0) -> dict | None:
    if mode == "adsd":
        if not ADSD_ALMIGHTY_AUDIO_DUB_EXPERIMENT:
            return None
        male_asset = ADSD_DEFAULT_MALE_VOICE_ASSET
        female_asset = ADSD_DEFAULT_FEMALE_VOICE_ASSET
        default_asset = ""
    else:
        if not VOICE_ASSET_AUDIO_DUB_EXPERIMENT:
            return None
        male_asset = DEFAULT_MALE_VOICE_ASSET
        female_asset = DEFAULT_FEMALE_VOICE_ASSET
        default_asset = DEFAULT_VOICE_ASSET
    explicit_asset = str(scene.get("voice_asset_id") or scene.get("voice_id") or "").strip()
    if explicit_asset:
        asset_id = explicit_asset
    elif default_asset:
        asset_id = default_asset
    else:
        gender = str(scene.get("voice_gender") or "").strip().lower()
        asset_id = female_asset if gender == "female" else male_asset
    if not asset_id:
        return None
    data = _load_voice_assets()
    asset = next((a for a in data.get("assets", []) if a.get("voice_id") == asset_id), None)
    if not asset:
        log(f"[voice-asset] 默认音色 {asset_id} 不存在，回退 turn TTS")
        return None
    refs = asset.get("reference_audios") or []
    if not refs:
        log(f"[voice-asset] 默认音色 {asset_id} 无 reference audio，回退 turn TTS")
        return None
    def _voice_ref_sort_key(ref: dict) -> tuple[float, float]:
        return (
            float(ref.get("priority") or ref.get("reference_priority") or 0),
            float(ref.get("clean_score") or 0),
        )

    refs = sorted(refs, key=_voice_ref_sort_key, reverse=True)
    root = Path(__file__).resolve().parent
    valid_refs = []
    for ref in refs:
        path = root / str(ref.get("path", ""))
        if path.exists() and path.stat().st_size > 10000:
            valid_refs.append((ref, path))
    if valid_refs:
        ref_index = max(0, min(int(ref_offset or 0), len(valid_refs) - 1))
        ref, path = valid_refs[ref_index]
        return {
            "asset_id": asset_id,
            "display_name": asset.get("display_name"),
            "identified_person": asset.get("identified_person"),
            "license_status": asset.get("license_status"),
            "allowed_use": asset.get("allowed_use", []),
            "forbidden_use": asset.get("forbidden_use", []),
            "quality_flags": asset.get("quality_flags", []),
            "path": str(path),
            "sha256": ref.get("sha256"),
            "duration": ref.get("duration"),
            "reference_index": ref_index,
            "reference_count": len(valid_refs),
        }
    log(f"[voice-asset] 默认音色 {asset_id} reference 文件缺失，回退 turn TTS")
    return None


def _lip_sync_poll_download_and_process(idx: int, task_id: str, scene: dict, target_dur: float) -> tuple[bool, dict]:
    caption_info = _werydance_caption_request(scene)
    info = {
        "turn": idx + 1,
        "speaker": scene.get("speaker"),
        "task_id": task_id,
        "source_audio": scene.get("_almighty_reference_audio") or scene.get("dialogue_audio_mp3") or scene.get("dialogue_audio"),
        "source_audio_role": scene.get("_almighty_reference_audio_role") or "turn_dialogue_audio",
        "voice_asset_reference": scene.get("_almighty_voice_asset_reference"),
        "werydance_captions_enabled": WERYDANCE_CAPTIONS,
        "werydance_captions_requested": caption_info.get("requested"),
        "werydance_caption_text": caption_info.get("text") if caption_info.get("requested") else None,
        "ass_fallback_required": caption_info.get("ass_fallback_required"),
        "caption_reason": caption_info.get("reason"),
        "target_duration": round(target_dur, 3),
    }
    for iteration in range(181):
        try:
            s = req_get(f"/generation/{task_id}/status")
            data = s.get("data", {})
            st = data.get("task_status", "")
            if iteration == 0 or iteration % 12 == 0 or st in ("succeed", "failed"):
                log(f"[lip-sync {idx}] poll #{iteration+1}: {st}")
            if st == "succeed":
                vid_url = _extract_video_url(data)
                if not vid_url:
                    info.update({"pass": False, "reason": "succeed_without_video_url"})
                    return False, info
                raw_path = str(OUTPUT_DIR / f"lip_sync_raw_{idx}.mp4")
                urllib.request.urlretrieve(vid_url, raw_path)
                raw_dur = ffprobe_duration(raw_path)
                audio_dub = bool(scene.get("_almighty_audio_dub_attempt"))
                ok = _postprocess_audio_dub_segment(raw_path, scene, target_dur) if audio_dub else _postprocess_lip_sync_segment(raw_path, scene, target_dur)
                final_dur = ffprobe_duration(scene["vid_path"]) if ok else None
                source_audio = scene.get("_almighty_reference_audio") or scene.get("dialogue_audio_mp3") or scene.get("dialogue_audio")
                audio_dur = ffprobe_duration(source_audio) if source_audio and os.path.exists(source_audio) else None
                info.update({
                    "pass": ok,
                    "candidate": "almighty_reference_audio_dub" if audio_dub else "almighty_reference_image_audio",
                    "raw_video_path": raw_path,
                    "raw_video_duration": raw_dur,
                    "final_segment_path": scene["vid_path"],
                    "final_segment_duration": final_dur,
                    "source_audio_duration": audio_dur,
                    "video_has_audio": audio_dub,
                    "duration_delta": abs((final_dur or 0) - target_dur) if final_dur is not None else None,
                    "clip_duration_match_pass": final_dur is not None and abs(final_dur - target_dur) <= 0.25,
                    "needs_master_audio_mux": not audio_dub,
                    "generated_audio_from_prompt_dialogue": audio_dub,
                })
                _remove_lip_sync_task(idx)
                return ok, info
            if st == "failed":
                info.update({"pass": False, "reason": "task_failed", "response": data})
                _remove_lip_sync_task(idx)
                return False, info
        except Exception as e:
            if iteration in (0, 12, 60, 120):
                log(f"[lip-sync {idx}] poll 异常: {e}")
        time.sleep(5)
    info.update({"pass": False, "reason": "poll_timeout"})
    return False, info


def _lip_sync_one_scene(idx: int, scene: dict, target_dur: float, aspect_ratio: str) -> tuple[int, bool, dict]:
    # 三类 turn 分发：a_roll lip-sync / narrated_b 旁白克隆 (有 audio 但无嘴特写) / silent_b 纯 motion
    needs_lip = bool(scene.get("needs_lip_sync", True))
    is_narrated = _is_narrated_b(scene)
    is_silent = _is_silent_b(scene)
    turn_audio = scene.get("dialogue_audio_mp3") or scene.get("dialogue_audio")
    # silent_b 不需要 audio；a_roll / narrated_b 需要 TTS 音频做 audio_ref fallback
    if (needs_lip or is_narrated) and (not turn_audio or not os.path.exists(turn_audio)):
        return idx, False, {"turn": idx + 1, "pass": False, "reason": "missing_turn_audio"}
    if needs_lip or is_narrated:
        # a_roll 和 narrated_b 都走 voice_asset 克隆音色（narrated_b 也用 LLM 挑的旁白音色）
        voice_asset_ref = _select_voice_asset_reference(scene)
        source_audio = voice_asset_ref["path"] if voice_asset_ref else turn_audio
    else:
        voice_asset_ref = None
        source_audio = None
    caption_info = _werydance_caption_request(scene)
    # B-roll 路径 prompt 不要求 WERYDANCE 烧字幕，必须强制走 ASS 兜底，否则字幕真空
    if not needs_lip:
        caption_info = dict(caption_info)
        caption_info["requested"] = False
        caption_info["ass_fallback_required"] = True
        caption_info["reason"] = "b_roll_motion_mode_use_ass"
    scene["_almighty_reference_audio"] = source_audio
    scene["_almighty_reference_audio_role"] = (
        "voice_asset_timbre_reference" if voice_asset_ref
        else ("turn_dialogue_audio" if needs_lip else ("narrated_voice_clone" if is_narrated else "broll_no_audio"))
    )
    scene["_almighty_voice_asset_reference"] = voice_asset_ref
    scene["_b_roll_mode"] = not needs_lip
    scene["_narrated_b_mode"] = is_narrated
    manual_repair_turns = _load_lips_change_requested_turns()
    repair_requested = ADSD_LIPS_CHANGE_REPAIR and ((idx + 1) in manual_repair_turns)
    repair_all = ADSD_LIPS_CHANGE_REPAIR and ADSD_LIPS_CHANGE_ALL
    existing_tid = _load_lip_sync_tasks().get(str(idx))
    if existing_tid:
        ok, info = _lip_sync_poll_download_and_process(idx, existing_tid, scene, target_dur)
        return idx, ok, info
    try:
        image_url = _upload_to_weryai(scene["img_path"])
        # multi-ref 在 audio_dub mode 下默认 OFF：silentb2 测试发现开启后 a_roll task_failed (rate limit)
        # 需要进一步排查 ref_images 顺序 / alt_panel 选图问题，先回滚保稳定
        # 想恢复 → export ADR_MULTI_REF_DEFAULT=1
        multi_ref_default = os.environ.get("ADR_MULTI_REF_DEFAULT", "0").strip().lower() in ("1", "true", "yes", "on")
        broll_use_sheet = (
            multi_ref_default
            or os.environ.get("ADR_ADSD_BROLL_USE_CHARACTER_SHEET", "0").strip().lower() in ("1", "true", "yes", "on")
        )
        broll_use_alt_panels = os.environ.get("ADR_ADSD_BROLL_ALT_PANELS", "0").strip().lower() in ("1", "true", "yes", "on")
        sheet_path = OUTPUT_DIR / "character_sheet.png"
        sheet_url = None
        # silent_b 不用 character_sheet（没主体角色）；a_roll/narrated_b 默认带 sheet
        if (needs_lip or (is_narrated and broll_use_sheet)) and sheet_path.exists() and sheet_path.stat().st_size > 10000:
            try:
                sheet_url = _upload_to_weryai(str(sheet_path))
            except Exception as e:
                log(f"[lip-sync {idx}] character sheet upload skipped: {e}")
        # alt_panels 只给 a_roll（同 speaker 跨 turn 一致性）；narrated_b/silent_b 不需要
        alt_panel_urls: list[str] = []
        for alt_path in (scene.get("_alt_speaker_panels", [])[:2] if (needs_lip or broll_use_alt_panels) else []):
            if not (alt_path and os.path.exists(alt_path)):
                continue
            try:
                alt_panel_urls.append(_upload_to_weryai(alt_path))
            except Exception as e:
                log(f"[lip-sync {idx}] alt-speaker panel upload skipped: {e}")
        # a_roll 和 narrated_b 都上传 audio_ref；silent_b 不传
        audio_url = _upload_to_weryai(source_audio) if ((needs_lip or is_narrated) and source_audio) else None
        # 顺序约定: [character_sheet(身份锚)?, alt_panel(同speaker场景示例)..., image_url(当前帧)]
        # WERYDANCE 把最后一张视为渲染目标，前面的作 identity / consistency 提示
        ref_images: list[str] = []
        if sheet_url:
            ref_images.append(sheet_url)
        ref_images.extend(alt_panel_urls)
        ref_images.append(image_url)
        # duration 计算：TTS 时长可能因 prosody 波动偏短，导致 WERYDANCE 被强制加速朗读 (~2x)
        # 用 ceil(字数/6) 做最小值兜底（6 字/秒是中文播报舒适上限）
        # 最终 cap 在 WERYDANCE 硬上限 15s
        _tts_dur = float(scene.get("dur") or target_dur)
        _text = str(scene.get("text") or "")
        _char_min = math.ceil(len(_text) / 6.0) if _text else 0
        api_dur = int(round(min(15, max(5, _char_min, _tts_dur))))
        fast_fallback_enabled = os.environ.get("ADR_WERYDANCE_FAST_FALLBACK", "1").strip().lower() not in ("0", "false", "no", "off")
        if not needs_lip:
            if is_silent:
                # silent_b：纯 motion，无 audio，呼吸位 prompt
                variants = [
                    ("silent_b_motion", "WERYDANCE_2_0", _adsd_silent_b_motion_prompt(scene, safe_retry=False), "false"),
                    ("silent_b_motion_safe", "WERYDANCE_2_0", _adsd_silent_b_motion_prompt(scene, safe_retry=True), "false"),
                ]
                if fast_fallback_enabled:
                    variants.append(("silent_b_motion_fast", "WERYDANCE_2_0_FAST", _adsd_silent_b_motion_prompt(scene, safe_retry=True), "false"))
            elif is_narrated and ADSD_ALMIGHTY_AUDIO_DUB_EXPERIMENT and audio_url:
                # narrated_b：走 audio_dub 拿克隆旁白音色，画面用 broll prompt (无嘴部特写)
                variants = [
                    ("narrated_b_audio_dub", "WERYDANCE_2_0", _adsd_broll_motion_prompt(scene, safe_retry=False), "true"),
                    ("narrated_b_motion_fallback", "WERYDANCE_2_0", _adsd_broll_motion_prompt(scene, safe_retry=True), "false"),
                ]
                if fast_fallback_enabled:
                    variants.insert(1, ("narrated_b_audio_dub_safe", "WERYDANCE_2_0_FAST", _adsd_broll_motion_prompt(scene, safe_retry=True), "true"))
            else:
                # 兜底（旧 narrated_b 行为）：纯 motion 无 audio
                variants = [
                    ("broll_motion", "WERYDANCE_2_0", _adsd_broll_motion_prompt(scene, safe_retry=False), "false"),
                    ("broll_motion_safe", "WERYDANCE_2_0", _adsd_broll_motion_prompt(scene, safe_retry=True), "false"),
                ]
                if fast_fallback_enabled:
                    variants.append(("broll_motion_fast", "WERYDANCE_2_0_FAST", _adsd_broll_motion_prompt(scene, safe_retry=True), "false"))
        elif ADSD_ALMIGHTY_AUDIO_DUB_EXPERIMENT:
            variants = [
                ("audio_dub_primary", "WERYDANCE_2_0", _adsd_almighty_audio_dub_prompt(scene, safe_retry=False), "true"),
                ("silent_lips_fallback", "WERYDANCE_2_0", _adsd_lip_sync_prompt(scene, safe_retry=True), "false"),
            ]
            if fast_fallback_enabled:
                variants.insert(1, ("audio_dub_safe", "WERYDANCE_2_0_FAST", _adsd_almighty_audio_dub_prompt(scene, safe_retry=True), "true"))
        else:
            variants = [
                ("primary", "WERYDANCE_2_0", _adsd_lip_sync_prompt(scene, safe_retry=False), "false"),
                ("safe_prompt", "WERYDANCE_2_0", _adsd_lip_sync_prompt(scene, safe_retry=True), "false"),
            ]
            if fast_fallback_enabled:
                variants.append(("fast_safe_prompt", "WERYDANCE_2_0_FAST", _adsd_lip_sync_prompt(scene, safe_retry=True), "false"))
        attempts: list[dict] = []
        for variant_name, model, prompt, generate_audio in variants:
            r = None
            task_id = None
            scene["_almighty_audio_dub_attempt"] = generate_audio == "true"
            for submit_attempt in range(3):
                try:
                    _wait_motion_submit_slot(f"lip-sync {idx+1}")
                    payload = {
                        "model": model,
                        "images": ref_images,
                        "prompt": prompt,
                        "negative_prompt": _werydance_negative_prompt(scene),
                        "duration": api_dur,
                        "aspect_ratio": aspect_ratio,
                        "resolution": "720p",
                        "generate_audio": generate_audio,
                        "video_number": 1,
                    }
                    # B-roll 模式不传 audios；A-roll 才传
                    if audio_url:
                        payload["audios"] = [audio_url]
                    r = req_post("/generation/almighty-reference-to-video", payload, timeout=30)
                    task_id = r.get("data", {}).get("task_id") or (r.get("data", {}).get("task_ids") or [None])[0]
                    if task_id:
                        break
                except Exception as e:
                    if submit_attempt < 2:
                        wait_s = 5 * (submit_attempt + 1)
                        log(f"[lip-sync {idx}] submit {variant_name}/{model} 失败（第 {submit_attempt+1}/3 次）：{e}，{wait_s}s 后重试")
                        time.sleep(wait_s)
                        continue
                    attempts.append({"variant": variant_name, "model": model, "pass": False, "reason": f"submit_exception: {e}"})
            if task_id is None:
                if r is not None:
                    attempts.append({"variant": variant_name, "model": model, "pass": False, "reason": "submit_without_task_id", "response": r})
                continue
            _save_lip_sync_task(idx, task_id)
            ok, info = _lip_sync_poll_download_and_process(idx, task_id, scene, target_dur)
            info.update({
                "variant": variant_name,
                "submit_model": model,
                "submit_duration": api_dur,
                "generate_audio": generate_audio,
                "audio_dub_experiment": ADSD_ALMIGHTY_AUDIO_DUB_EXPERIMENT,
                "image_url": image_url,
                "character_sheet_url": sheet_url,
                "alt_speaker_panel_urls": alt_panel_urls,
                "alt_speaker_panel_count": len(alt_panel_urls),
                "reference_image_count": len(ref_images),
                "audio_url": audio_url,
                "reference_audio_role": scene.get("_almighty_reference_audio_role"),
                "voice_asset_reference": voice_asset_ref,
                "turn_dialogue_audio": turn_audio,
                "werydance_captions_enabled": WERYDANCE_CAPTIONS,
                "werydance_captions_requested": caption_info.get("requested"),
                "werydance_caption_text": caption_info.get("text") if caption_info.get("requested") else None,
                "ass_fallback_required": caption_info.get("ass_fallback_required"),
                "caption_reason": caption_info.get("reason"),
            })
            if ok and (repair_all or repair_requested):
                repair_ok, repair_info = _lips_change_repair_segment(idx, scene, target_dur)
                repair_info["reason"] = "all_turns" if repair_all else "manual_requested_turn"
                info["lips_change_repair"] = repair_info
                ok = repair_ok
                info["pass"] = ok
                if ok:
                    info["candidate"] = "almighty_reference_then_video_lips_change"
            attempts.append({k: v for k, v in info.items() if k not in ("image_url", "audio_url", "response")})
            if ok:
                info["attempts"] = attempts
                return idx, ok, info
        final = dict(attempts[-1]) if attempts else {"turn": idx + 1, "pass": False, "reason": "no_attempts"}
        final.update({
            "turn": idx + 1,
            "pass": False,
            "attempts": attempts,
            "image_url": image_url,
            "character_sheet_url": sheet_url,
            "reference_image_count": len(ref_images),
            "audio_url": audio_url,
            "audio_dub_experiment": ADSD_ALMIGHTY_AUDIO_DUB_EXPERIMENT,
            "reference_audio_role": scene.get("_almighty_reference_audio_role"),
            "voice_asset_reference": voice_asset_ref,
            "turn_dialogue_audio": turn_audio,
            "werydance_captions_enabled": WERYDANCE_CAPTIONS,
            "werydance_captions_requested": caption_info.get("requested"),
            "werydance_caption_text": caption_info.get("text") if caption_info.get("requested") else None,
            "ass_fallback_required": caption_info.get("ass_fallback_required"),
            "caption_reason": caption_info.get("reason"),
        })
        if ADSD_LIPS_CHANGE_REPAIR:
            repair_ok, repair_info = _lips_change_repair_segment(idx, scene, target_dur)
            repair_info["reason"] = "almighty_failed_fallback"
            final["lips_change_repair"] = repair_info
            if repair_ok:
                final.update({
                    "pass": True,
                    "candidate": "video_lips_change_fallback",
                    "reason": "almighty_failed_repaired_by_lips_change",
                })
                return idx, True, final
        return idx, False, final
    except Exception as e:
        log(f"[lip-sync {idx}] 异常: {type(e).__name__}: {e}")
        return idx, False, {"turn": idx + 1, "speaker": scene.get("speaker"), "pass": False, "reason": str(e)}


def step66_adsd_lip_sync(script: list[dict]):
    """Experimental ADSD real lip-sync path using Werydance Almighty Reference."""
    if not (ADS_DIALOGUE_MODE and ADSD_LIP_SYNC_EXPERIMENT):
        return
    n = len(script)
    aspect = "9:16" if IS_VERTICAL else "16:9"
    mode_note = "audio-dub 音色直配" if ADSD_ALMIGHTY_AUDIO_DUB_EXPERIMENT else "静音口型同步"
    tg(f"👄 {ADSD_MODE_NAME} 口型同步启动：WERYDANCE_2_0 Almighty Reference × {n} turn（{mode_note}）")
    target_durs = [_lip_sync_slot_duration(script, i) for i in range(n)]
    # P2 分析：识别"连续同 speaker"分组（潜在 batching 机会）
    # 当前实施分析层 + QA log，实际 batching 留 TODO（涉及 ThreadPoolExecutor 重构）
    try:
        consecutive_groups: list[list[int]] = []
        cur_group: list[int] = []
        cur_speaker: str | None = None
        cur_dur = 0.0
        for _i, _s in enumerate(script):
            _sp = (_s.get("speaker") or "").strip()
            _d = float(target_durs[_i])
            # 同 speaker 且累计 + 本 turn 不超 batch 上限 → 加入当前 group
            if _sp == cur_speaker and cur_group and (cur_dur + _d) <= ADSD_SPEAKER_BATCH_MAX_DURATION:
                cur_group.append(_i)
                cur_dur += _d
            else:
                if cur_group:
                    consecutive_groups.append(cur_group)
                cur_group = [_i]
                cur_speaker = _sp
                cur_dur = _d
        if cur_group:
            consecutive_groups.append(cur_group)
        multi_turn_groups = [g for g in consecutive_groups if len(g) > 1]
        potential_call_savings = sum(len(g) - 1 for g in multi_turn_groups)
        p2_qa = {
            "mode": "adsd_consecutive_speaker_grouping_analysis",
            "policy": "analysis_only_actual_batching_gated_by_ADR_ADSD_SPEAKER_BATCH",
            "batching_active": ADSD_CONSECUTIVE_SPEAKER_BATCHING,
            "batch_max_duration_seconds": ADSD_SPEAKER_BATCH_MAX_DURATION,
            "total_turns": n,
            "total_groups": len(consecutive_groups),
            "multi_turn_groups": len(multi_turn_groups),
            "potential_werydance_call_savings": potential_call_savings,
            "groups": [
                {
                    "group_idx": gi + 1,
                    "turn_indices": [i + 1 for i in g],
                    "speaker": (script[g[0]].get("speaker") or "").strip(),
                    "total_dur_seconds": round(sum(target_durs[i] for i in g), 3),
                    "fits_werydance_15s_cap": sum(target_durs[i] for i in g) <= 15.0,
                }
                for gi, g in enumerate(consecutive_groups)
            ],
            "manual_visual_checks_required": [
                "if_batching_enabled_check_no_face_drift_between_turns_in_a_group",
                "if_batching_enabled_check_no_audio_misalignment_at_split_boundaries",
            ],
            "created_at": datetime.now().isoformat(timespec="seconds"),
        }
        (OUTPUT_DIR / "adsd_speaker_grouping_analysis_qa.json").write_text(
            json.dumps(p2_qa, ensure_ascii=False, indent=2), encoding="utf-8")
        if potential_call_savings > 0:
            tg(f"📊 ADSD 同 speaker 连续分组分析：{len(consecutive_groups)} 组 "
               f"({len(multi_turn_groups)} 多 turn 组) → 启用 batching 可省 {potential_call_savings} 次 WERYDANCE 调用 "
               f"({'已启用' if ADSD_CONSECUTIVE_SPEAKER_BATCHING else '未启用，需 --adsd-speaker-batch'})")
    except Exception as e:
        log(f"P2 speaker grouping analysis 失败: {e}")
    # 跨 turn 一致性：为每个 turn 预先准备同 speaker 的其它 panel 路径列表，传入 _lip_sync_one_scene 作 multi-ref
    # WERYDANCE 看到同一角色在多个场景的镜头，能更稳地维持脸型/服装/造型，减少跨 turn 漂移
    _speaker_to_panel_paths: dict[str, list[str]] = {}
    for _i, _s in enumerate(script):
        _sp = (_s.get("speaker") or "").strip()
        _p = _s.get("img_path")
        if _sp and _p and os.path.exists(_p):
            _speaker_to_panel_paths.setdefault(_sp, []).append(_p)
    _alt_attach_log: list[dict] = []
    for _i, _s in enumerate(script):
        _sp = (_s.get("speaker") or "").strip()
        _p = _s.get("img_path")
        _alts = [pp for pp in _speaker_to_panel_paths.get(_sp, []) if pp and pp != _p]
        _s["_alt_speaker_panels"] = _alts[:2]
        _alt_attach_log.append({
            "turn": _i + 1,
            "speaker": _sp,
            "alt_panel_count": len(_s["_alt_speaker_panels"]),
            "alt_panel_paths": _s["_alt_speaker_panels"],
        })
    try:
        (OUTPUT_DIR / "adsd_lipsync_multiref_attach_qa.json").write_text(
            json.dumps({"per_turn": _alt_attach_log,
                        "policy": "same_speaker_alt_panels_up_to_2_inserted_between_character_sheet_and_current_panel",
                        "created_at": datetime.now().isoformat(timespec='seconds')},
                       ensure_ascii=False, indent=2),
            encoding="utf-8")
    except Exception as e:
        log(f"adsd_lipsync_multiref_attach_qa.json 写入失败: {e}")
    _attach_total = sum(r["alt_panel_count"] for r in _alt_attach_log)
    tg(f"🧪 ADSD lip-sync multi-ref attach: {_attach_total}/{n*2} alt-panel slot 已挂载 (同 speaker 跨 turn 一致性)")
    # A-roll / B-roll 分布
    a_roll = sum(1 for _s in script if _s.get("needs_lip_sync", True))
    b_roll = n - a_roll
    if b_roll > 0:
        tg(f"🎬 A-roll / B-roll 分布：{a_roll} 个 lip-sync 镜头 + {b_roll} 个 motion 镜头（B-roll 全员可动，audio 走主轨）")
    results: dict[int, bool] = {}
    records: list[dict] = []
    # weryai 并发上限 20，贴顶以便长 ADR (>10 turn) 不会排队跑成串行
    max_workers = min(int(os.environ.get("ADR_LIP_SYNC_MAX_CONCURRENT", "20")), n)
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futs = {ex.submit(_lip_sync_one_scene, i, script[i], target_durs[i], aspect): i for i in range(n)}
        for fut in as_completed(futs):
            i = futs[fut]
            try:
                idx, ok, info = fut.result()
            except Exception as e:
                idx, ok, info = i, False, {"turn": i + 1, "pass": False, "reason": str(e)}
            results[idx] = ok
            records.append(info)
            if ok:
                tg(f"👄 Turn {idx+1}/{n} 口型同步 ✓")
            else:
                tg(f"⚠️ Turn {idx+1}/{n} 口型同步失败，保留原静态/motion片段")
    records.sort(key=lambda x: int(x.get("turn", 0)))
    success_cnt = sum(1 for v in results.values() if v)
    generated_audio_cnt = sum(1 for r in records if r.get("pass") and r.get("video_has_audio") and r.get("generated_audio_from_prompt_dialogue"))
    embedded_audio_ready = generated_audio_cnt == n and generated_audio_cnt > 0
    werydance_caption_cnt = sum(1 for r in records if r.get("pass") and r.get("werydance_captions_requested") and not r.get("ass_fallback_required"))
    sheet_path = OUTPUT_DIR / "character_sheet.png"
    multiref_alt_attach_total = sum(r.get("alt_panel_count", 0) for r in _alt_attach_log)
    # 区分 A-roll (需口型同步) vs B-roll (motion 模式，无口型要求)
    # 之前 success_rate 把两类混在一起算 → B-roll 失败拉低 lip-sync 阈值；B-roll 成功又水分掩盖 A-roll 真问题
    a_roll_idxs = [i for i, s in enumerate(script) if s.get("needs_lip_sync", True)]
    b_roll_idxs = [i for i, s in enumerate(script) if not s.get("needs_lip_sync", True)]
    a_roll_success = sum(1 for i in a_roll_idxs if results.get(i))
    b_roll_success = sum(1 for i in b_roll_idxs if results.get(i))
    a_roll_total = len(a_roll_idxs)
    b_roll_total = len(b_roll_idxs)
    a_roll_pass = a_roll_total == 0 or a_roll_success >= max(1, math.ceil(a_roll_total * 0.8))
    b_roll_pass = b_roll_total == 0 or b_roll_success >= max(1, math.ceil(b_roll_total * 0.8))
    qa = {
        "mode": ADSD_MODE_NAME,
        "interface": "almighty-reference-to-video+video-lips-change-fallback" if ADSD_LIPS_CHANGE_REPAIR else "almighty-reference-to-video",
        "model": "WERYDANCE_2_0",
        "character_sheet_reference": str(sheet_path) if sheet_path.exists() else None,
        "character_sheet_reference_exists": sheet_path.exists() and sheet_path.stat().st_size > 10000,
        "multiref_alt_speaker_panels_enabled": True,
        "multiref_alt_speaker_panels_attached_total": multiref_alt_attach_total,
        "multiref_alt_speaker_panels_per_turn_cap": 2,
        "multiref_attach_log": "adsd_lipsync_multiref_attach_qa.json",
        "lips_change_repair_enabled": ADSD_LIPS_CHANGE_REPAIR,
        "lips_change_all_enabled": ADSD_LIPS_CHANGE_ALL,
        "almighty_audio_dub_experiment": ADSD_ALMIGHTY_AUDIO_DUB_EXPERIMENT,
        "default_voice_assets": {
            "male": ADSD_DEFAULT_MALE_VOICE_ASSET,
            "female": ADSD_DEFAULT_FEMALE_VOICE_ASSET,
        },
        "generated_audio_segment_count": generated_audio_cnt,
        "embedded_dialogue_audio_ready": embedded_audio_ready,
        "werydance_captions_enabled": WERYDANCE_CAPTIONS,
        "werydance_caption_segment_count": werydance_caption_cnt,
        "ass_caption_fallback_count": max(0, n - werydance_caption_cnt) if WERYDANCE_CAPTIONS else n,
        "lips_change_requested_turns": sorted(_load_lips_change_requested_turns()),
        "onsite_pov_mode": ADSD_ONSITE_POV_MODE,
        "total": n,
        "success_count": success_cnt,
        "success_rate": round(success_cnt / max(n, 1), 4),
        # A-roll / B-roll 分轨统计
        "a_roll_total": a_roll_total,
        "a_roll_success": a_roll_success,
        "a_roll_success_rate": round(a_roll_success / max(a_roll_total, 1), 4) if a_roll_total else 1.0,
        "a_roll_pass": a_roll_pass,
        "b_roll_total": b_roll_total,
        "b_roll_success": b_roll_success,
        "b_roll_success_rate": round(b_roll_success / max(b_roll_total, 1), 4) if b_roll_total else 1.0,
        "b_roll_pass": b_roll_pass,
        # pass 判定: A-roll 口型成功率 ≥80% (B-roll 不进口型阈值)
        "pass": a_roll_pass,
        "lip_sync_metric_policy": "a_roll_only_for_lip_sync_threshold_b_roll_separate_motion_track",
        "policy": "failed_turns_keep_existing_segments",
        "master_audio_mux_required": not embedded_audio_ready,
        "final_audio_offset_required": 0.0,
        "voice_reference_policy": "use owned, licensed, consented, or otherwise lawful voice references; avoid undisclosed real-person impersonation",
        "manual_visual_checks_required": {
            "a_roll": [
                "mouth_visible",
                "active_speaker_correct",
                "no_face_drift",
                "mouth_motion_matches_syllable_timing",
                "voice_timbre_matches_authorized_reference",
                "no_undisclosed_real_person_impersonation",
            ],
            "b_roll": [
                "scene_matches_voice_over_narration",
                "no_mouth_lip_sync_attempted",
                "ambient_motion_natural",
                "no_active_speaker_lock",
            ],
        },
        "records": records,
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }
    # 这个 QA 本质是 WERYDANCE 渲染成功率 (API hard-fail 监控)，不验证真实口型质量
    # 主存盘改名 render_success_qa.json；同时写 lip_sync_qa.json 兼容旧 reader
    qa["qa_type_clarification"] = "werydance_render_success_not_actual_lip_sync_quality"
    qa["interpretation_note"] = (
        "pass=True 仅代表 N 个 turn 都从 WERYDANCE 拿到了有效视频并通过 ffmpeg postprocess。"
        "不验证嘴是否真在动 / 张嘴时机是否对得上音频。真实口型质量需要 vision 帧分析或人工抽检 manual_visual_checks。"
    )
    _qa_json_text = json.dumps(qa, ensure_ascii=False, indent=2)
    (OUTPUT_DIR / "render_success_qa.json").write_text(_qa_json_text, encoding="utf-8")
    # 旧名兼容: delivery_qa / werydance_caption_covered_turns 等下游仍读 lip_sync_qa.json
    (OUTPUT_DIR / "lip_sync_qa.json").write_text(_qa_json_text, encoding="utf-8")
    if qa["pass"]:
        tg(f"✅ {ADSD_MODE_NAME} WERYDANCE 渲染 QA 通过：A-roll {a_roll_success}/{a_roll_total} ✓ · B-roll {b_roll_success}/{b_roll_total} (motion only) · 注：本 QA 仅监控渲染 hard-fail，真实口型对错需人工抽检")
    else:
        tg(f"⚠️ {ADSD_MODE_NAME} WERYDANCE 渲染 QA 未达标：A-roll {a_roll_success}/{a_roll_total}（阈值 80%），可静态/motion兜底成片")


def step65_motion(script: list[dict]):
    """把静态 seg_N.mp4 替换为 WERYDANCE_2_0 动态版本（并发 + 单轮内失败自动重试 1 次）"""
    _ensure_motion_action_plan(script)
    _write_motion_action_plan_qa(script)
    n = len(script)
    reporter_tag = " · ADS拟现场记者" if ADS_REPORTER_MODE else ""
    if STORYBOARD_REFERENCE_MOTION and STORYBOARD_ANNOTATED_MOTION and not ADS_DIALOGUE_MODE:
        mode_tag = "实验 annotated storyboard 图生视频"
    elif STORYBOARD_REFERENCE_MOTION and not ADS_DIALOGUE_MODE:
        mode_tag = "clean keyframe 图生视频优先"
    else:
        mode_tag = "文本生视频"
    tg(f"🎬 动态化启动{reporter_tag}：WERYDANCE_2_0 × {n} 分镜并发生成运动视频（{mode_tag}）...")

    # 1. 生成每个分镜的 motion prompt
    motion_prompts = _generate_motion_prompts(script)
    tg(f"✅ Motion prompts 就绪（{n} 条）")

    aspect = "9:16" if IS_VERTICAL else "16:9"
    results: dict[int, bool] = {}
    character_trailer_qa = _generate_character_trailer_motion(script, motion_prompts, aspect)
    trailer_qa = _generate_storyboard_trailer_motion(script, motion_prompts, aspect)
    previs_qa = _generate_previs_page_motion_segments(script, motion_prompts, aspect)
    grid_motion_qa = _generate_grid_multiref_motion_segments(script, motion_prompts, aspect)
    seg_qa = None
    if STORYBOARD_GRID_MULTIREF_SEGMENTS:
        seg_qa = _apply_grid_multiref_segments(script, grid_motion_qa)
        _write_storyboard_motion_compare_qa(grid_motion_qa, previs_qa, seg_qa, trailer_qa, character_trailer_qa)
        success_cnt = int((seg_qa or {}).get("success_count") or 0)
        if (seg_qa or {}).get("pass"):
            tg(f"✅ Grid multi-ref 实验动态化完成：{success_cnt}/{n} 段替换，主时间线 QA 通过")
            return
        tg(f"⚠️ Grid multi-ref 切片未达主线标准：{success_cnt}/{n} 段可用，继续逐镜动态化补齐")
    else:
        _write_storyboard_motion_compare_qa(grid_motion_qa, previs_qa, None, trailer_qa, character_trailer_qa)

    def _run_batch(indices: list[int], round_label: str, safe_retry: bool = False):
        """跑一批 indices，更新 results。task_id 持久化保证重试时已成功的分镜不会重复烧钱。"""
        if not indices:
            return
        with ThreadPoolExecutor(max_workers=min(20, len(indices))) as ex:
            futs = {
                ex.submit(_motion_one_scene, i, script[i], motion_prompts[i], aspect, safe_retry): i
                for i in indices
            }
            for fut in as_completed(futs):
                i = futs[fut]
                try:
                    ok = fut.result()
                except Exception as e:
                    log(f"[motion {i}] future 异常 ({round_label}): {e}")
                    ok = False
                results[i] = ok
                if ok:
                    tg(f"🎬 分镜 {i+1}/{n} 动态化 ✓ ({round_label})")
                elif round_label == "round 1":
                    log(f"[motion {i}] round 1 失败，等待重试")
                else:
                    tg(f"⚠️ 分镜 {i+1}/{n} 动态化失败（重试后仍失败，保留静态版）")

    # Round 1：全量并发；已通过 grid multi-ref 主线切片的镜头不重复烧钱。
    initial_indices = [i for i in range(n) if not script[i].get("grid_multiref_segment_mode")]
    for i in range(n):
        if script[i].get("grid_multiref_segment_mode"):
            results[i] = True
    _run_batch(initial_indices, "round 1")

    # Round 2：失败的自动重试 1 次（task_id 持久化下已成功的不会重复烧钱）
    failed_r1 = [i for i, ok in results.items() if not ok]
    if failed_r1:
        tg(f"🔄 第一轮失败 {len(failed_r1)}/{n}，自动用极简安全 prompt 重试 1 次...")
        _run_batch(failed_r1, "round 2", safe_retry=True)

    success_cnt = sum(1 for v in results.values() if v)
    _finalize_motion_qa(n, success_cnt)
    if ADS_DIALOGUE_MODE:
        speaker_qa = _write_adsd_speaker_focus_qa(script, results)
        if speaker_qa and not speaker_qa.get("pass"):
            tg(f"⚠️ {ADSD_MODE_NAME} 说话人镜头同步 QA 未通过：failed={speaker_qa.get('failed_count')}")
    tg(f"✅ 动态化完成：{success_cnt}/{n} 成功 · {n - success_cnt} 保留静态兜底（含重试后仍失败）")


def step65_grid_multiref_motion_qa(script: list[dict]):
    """Run only the 4K storyboard-grid multi-reference motion QA sidecar."""
    _ensure_motion_action_plan(script)
    _write_motion_action_plan_qa(script)
    n = len(script)
    aspect = "9:16" if IS_VERTICAL else "16:9"

    # STORYBOARD_TRAILER_MAIN：优先 multi-trailer 分段，每段对应一组 panels 的旁白时长
    # 成功则覆盖 storyboard_trailer.mp4，step7 拿来作 raw_concat
    # 失败 fall through 到原单 trailer 路径 + step7 的循环兜底
    if STORYBOARD_TRAILER_MAIN:
        tg(f"🧪 STORYBOARD_TRAILER_MAIN 启动：multi-trailer 分段并发")
        multi_path = _generate_multi_trailer_segments(script, aspect)
        if multi_path:
            # 成功，跳过 sidecar 单 trailer 调用避免重复消耗 credits
            return
        tg("⚠️ multi-trailer 失败，回退到单 trailer + 循环 fallback")

    tg(f"🧪 Grid multi-ref motion QA-only 启动：{n} 分镜")
    motion_prompts = _generate_motion_prompts(script)
    character_trailer_qa = _generate_character_trailer_motion(script, motion_prompts, aspect)
    trailer_qa = _generate_storyboard_trailer_motion(script, motion_prompts, aspect)
    previs_qa = _generate_previs_page_motion_segments(script, motion_prompts, aspect)
    grid_motion_qa = _generate_grid_multiref_motion_segments(script, motion_prompts, aspect)
    seg_qa = _apply_grid_multiref_segments(script, grid_motion_qa)
    _write_storyboard_motion_compare_qa(grid_motion_qa, previs_qa, seg_qa, trailer_qa, character_trailer_qa)


# ── audio_dub retiming：按 seg 真实长度重算 timeline，避免克隆语音被截 ─────────
def _retime_after_audio_dub(script: list[dict]) -> int:
    """audio_dub 跑完后，用 seg_N.mp4 真实时长重算每个 turn 的 timeline。

    场景：WERYDANCE 克隆语音可能比 master_voice TTS 长。
    postprocess 已经把 seg_N.mp4 时长设为 max(target_dur, src_dur)，
    现在按真实时长重排 cursor，让 audio_start/sub_start/vid_duration 同步拉长。
    返回时长被拉长的 turn 数。
    """
    if not (ADS_DIALOGUE_MODE and ADSD_ALMIGHTY_AUDIO_DUB_EXPERIMENT and ADSD_LIP_SYNC_EXPERIMENT):
        return 0
    cursor = 0.0
    extended = 0
    for i, scene in enumerate(script):
        seg_path = scene.get("vid_path") or ""
        if not seg_path or not os.path.exists(seg_path):
            continue
        seg_dur = ffprobe_duration(seg_path)
        if seg_dur <= 0:
            continue
        old_start = float(scene.get("audio_start", 0.0) or 0.0)
        old_dur = float(scene.get("vid_duration", 0.0) or 0.0)
        # 保存原 master_voice 上的位置：hybrid B-roll fallback 切 master_voice 时要用
        # 否则 retiming 后 cursor 移位，按新 audio_start 切 master_voice 会越界（master_voice 时长未变）
        scene["_master_voice_start"] = old_start
        scene["_master_voice_dur"] = old_dur
        if seg_dur > old_dur + 0.05:
            extended += 1
        scene["audio_start"] = cursor
        scene["audio_end"] = cursor + seg_dur
        scene["vid_duration"] = seg_dur
        scene["sub_start"] = cursor + SUB_DELAY
        scene["sub_end"] = cursor + seg_dur + SUB_DELAY
        cursor += seg_dur
    log(f"audio_dub retiming: {extended} turn 时长被拉长，总片长 → {cursor:.2f}s")
    return extended


# ── audio_dub voice-clone splice：把 A-roll seg 里的克隆音色拼回主音轨 ─────────
def _build_voice_clone_hybrid_audio(script: list[dict], master_voice_path: str) -> str | None:
    """ADSD audio_dub 模式专用：A-roll seg_N.mp4 里 WERYDANCE 生成的克隆音色
    会被 step9 默认主音轨 mux 流程覆盖（master_voice = weryai 默认 TTS）。
    本函数构造混合主音轨：
      - A-roll turn → 抽 seg_N.mp4 的音轨（克隆音色）
      - B-roll turn → 切 master_voice 的对应区间（默认 TTS）
    返回新 mp3 路径，供 step9 替换 voice_path。失败返回 None。
    """
    if not (ADS_DIALOGUE_MODE and ADSD_ALMIGHTY_AUDIO_DUB_EXPERIMENT and ADSD_LIP_SYNC_EXPERIMENT):
        return None
    if not master_voice_path or not os.path.exists(master_voice_path):
        return None
    a_roll_count = 0
    parts: list[str] = []
    work_dir = OUTPUT_DIR / "hybrid_audio_parts"
    work_dir.mkdir(exist_ok=True)
    master_voice_dur = ffprobe_duration(master_voice_path)
    silent_b_count = 0
    narrated_clone_count = 0
    for i, scene in enumerate(script):
        needs_lip = bool(scene.get("needs_lip_sync", True))
        is_narrated = _is_narrated_b(scene)
        seg_path = scene.get("vid_path") or ""
        vid_dur = float(scene.get("vid_duration", 0.0) or 0.0)
        if vid_dur <= 0:
            continue
        part_wav = str(work_dir / f"part_{i:02d}.wav")
        # a_roll 和 narrated_b（已跑 audio_dub）都用 seg 内嵌克隆音色
        seg_has_clone_audio = (
            (needs_lip or is_narrated)
            and seg_path and os.path.exists(seg_path) and _has_audio_stream(seg_path)
        )
        try:
            if _is_silent_b(scene):
                # silent_b 直接生成 vid_dur 长度静音段（不切 master_voice，因为本就无对白）
                ffmpeg(
                    "-f", "lavfi", "-i", f"anullsrc=channel_layout=mono:sample_rate=44100",
                    "-t", f"{vid_dur:.3f}",
                    "-c:a", "pcm_s16le",
                    part_wav,
                    timeout=30,
                )
                silent_b_count += 1
            elif seg_has_clone_audio:
                ffmpeg(
                    "-i", seg_path,
                    "-vn", "-ac", "1", "-ar", "44100",
                    "-c:a", "pcm_s16le",
                    part_wav,
                    timeout=60,
                )
                if needs_lip:
                    a_roll_count += 1
                else:
                    narrated_clone_count += 1
            else:
                # B-roll fallback：必须用原 master_voice 上的位置（retiming 前），
                # 否则 retiming 把 cursor 推过 master_voice 总长，-ss 越界读空
                mv_start = float(scene.get("_master_voice_start", scene.get("audio_start", 0.0)) or 0.0)
                mv_dur = float(scene.get("_master_voice_dur", vid_dur) or vid_dur)
                # 越界保护：mv_start 不能超 master_voice 总长，mv_dur 截到剩余可用区间
                if master_voice_dur > 0:
                    mv_start = min(mv_start, max(0.0, master_voice_dur - 0.1))
                    mv_dur = min(mv_dur, master_voice_dur - mv_start)
                if mv_dur <= 0:
                    log(f"hybrid audio part {i} master_voice 越界，用静音填补 {vid_dur:.2f}s")
                    ffmpeg(
                        "-f", "lavfi", "-i", f"anullsrc=channel_layout=mono:sample_rate=44100",
                        "-t", f"{vid_dur:.3f}",
                        "-c:a", "pcm_s16le",
                        part_wav,
                        timeout=30,
                    )
                else:
                    # 切 master_voice 区间，长度可能 < vid_dur，用 apad 补到 vid_dur 对齐 timeline
                    ffmpeg(
                        "-ss", f"{mv_start:.3f}", "-t", f"{mv_dur:.3f}",
                        "-i", master_voice_path,
                        "-af", f"apad=whole_dur={vid_dur:.3f}",
                        "-ac", "1", "-ar", "44100",
                        "-c:a", "pcm_s16le",
                        part_wav,
                        timeout=60,
                    )
            if not os.path.exists(part_wav) or os.path.getsize(part_wav) < 1000:
                log(f"hybrid audio part {i} 抽取异常，跳过")
                continue
            parts.append(part_wav)
        except Exception as e:
            log(f"hybrid audio part {i} 异常：{e}")
            continue
    if not parts or a_roll_count == 0:
        log("hybrid audio: 无可用 A-roll 克隆音轨，跳过 splice")
        return None
    concat_list = work_dir / "concat.txt"
    concat_list.write_text(
        "\n".join(f"file '{p}'" for p in parts),
        encoding="utf-8",
    )
    out_wav = str(OUTPUT_DIR / "hybrid_master_voice.wav")
    out_mp3 = str(OUTPUT_DIR / "hybrid_master_voice.mp3")
    try:
        ffmpeg(
            "-f", "concat", "-safe", "0",
            "-i", str(concat_list),
            "-ac", "1", "-ar", "44100",
            "-c:a", "pcm_s16le",
            out_wav,
            timeout=120,
        )
        # loudnorm 统一响度：WERYDANCE 克隆 audio 比 weryai TTS 响很多，
        # 不归一化会导致 A-roll 段把 BGM 听感压扁。-16 LUFS 是流媒体标准目标。
        ffmpeg(
            "-i", out_wav,
            "-af", "loudnorm=I=-16:LRA=11:TP=-1.5",
            "-c:a", "libmp3lame", "-b:a", "192k",
            out_mp3,
            timeout=60,
        )
    except Exception as e:
        log(f"hybrid audio concat 失败：{e}")
        return None
    if not os.path.exists(out_mp3) or os.path.getsize(out_mp3) < 1000:
        return None
    fallback_count = len(parts) - a_roll_count - silent_b_count - narrated_clone_count
    log(f"hybrid voice-clone master audio built ({a_roll_count} A-roll cloned, {narrated_clone_count} narrated_b cloned, {silent_b_count} silent_b 静音, {fallback_count} fallback)：{out_mp3}")
    return out_mp3


# ── silent_b BGM 动态浮起：silent_b 区间 BGM 音量 +40%（让 BGM 接管呼吸位）───
def _build_dynamic_bgm(script: list[dict], bgm_path: str | None) -> str | None:
    """收集 silent_b 时间区间，在这些区间把 BGM 音量从基础 0.6 提升到 0.85。

    实现：用 ffmpeg volume filter 的 timeline 表达式，按 between(t,T0,T1) 叠加 boost。
    基础音量 0.6（保持 step9 mux 时还会乘 step9 自己的 0.6 → 总 0.36，差不多 BGM 背景级别）
    silent_b 区间 0.85（step9 再乘 0.6 → 0.51，明显高于背景级别）
    返回 hybrid_bgm.mp3 路径；无 silent_b 或失败返回 None（让 step9 用原 bgm_path）。
    """
    if not bgm_path or not os.path.exists(bgm_path):
        return None
    silent_ranges: list[tuple[float, float]] = []
    for scene in script:
        if not _is_silent_b(scene):
            continue
        t0 = float(scene.get("audio_start", 0.0) or 0.0)
        dur = float(scene.get("vid_duration", scene.get("dur", 0.0)) or 0.0)
        if dur <= 0:
            continue
        silent_ranges.append((t0, t0 + dur))
    if not silent_ranges:
        return None
    # 构造 between(t,T0_i,T1_i) 叠加表达式
    base = 1.0
    boost = 0.4  # silent_b 区 BGM 整体 +40%
    expr_terms = [f"{base:.3f}"] + [f"{boost:.3f}*between(t,{t0:.3f},{t1:.3f})" for t0, t1 in silent_ranges]
    vol_expr = "+".join(expr_terms)
    out_path = str(OUTPUT_DIR / "hybrid_bgm.mp3")
    try:
        ffmpeg(
            "-i", bgm_path,
            "-af", f"volume='{vol_expr}':eval=frame",
            "-c:a", "libmp3lame", "-b:a", "192k",
            out_path,
            timeout=90,
        )
    except Exception as e:
        log(f"dynamic BGM 构建失败（回退原 BGM）：{e}")
        return None
    if not os.path.exists(out_path) or os.path.getsize(out_path) < 1000:
        return None
    log(f"dynamic BGM built ({len(silent_ranges)} silent_b 区间浮起 +{int(boost*100)}%)：{out_path}")
    return out_path


# ── 第七步：拼接视频轨 ────────────────────────────────────────────────────────
def step7_concat(script: list[dict]) -> str:
    # P1：grid_multiref 主路径：N 组 group videos concat 成 grid_multiref_combined.mp4 → raw_concat
    # 同 trailer-main 套路：循环到 master_voice 时长，24fps CFR
    if STORYBOARD_GRID_MULTIREF_MAIN:
        combined_path = OUTPUT_DIR / "grid_multiref_combined.mp4"
        if combined_path.exists() and combined_path.stat().st_size > 100000:
            raw_path = str(OUTPUT_DIR / "raw_concat.mp4")
            try:
                src_dur = ffprobe_duration(str(combined_path))
                voice_path = OUTPUT_DIR / "master_voice.mp3"
                if voice_path.exists() and voice_path.stat().st_size > 10000:
                    target_dur = ffprobe_duration(str(voice_path)) + 0.5
                else:
                    target_dur = max(
                        (s.get("audio_start", 0) + s.get("vid_duration", s.get("dur", 0))) for s in script
                    ) + 0.5
                pad_dur = max(0.0, target_dur - src_dur)
                if pad_dur > 0.2:
                    loops_est = int(target_dur / src_dur) + 1
                    ffmpeg(
                        "-stream_loop", "-1",
                        "-i", str(combined_path),
                        "-t", f"{target_dur:.3f}",
                        "-vf", "fps=24",
                        "-c:v", "libx264", "-crf", "20", "-preset", "medium",
                        "-an",
                        raw_path,
                        timeout=300,
                    )
                    tg(f"🎬 step7 grid_multiref_main: combined ({src_dur:.1f}s) 循环 ~{loops_est}× 填到 {target_dur:.1f}s @24fps CFR")
                else:
                    ffmpeg(
                        "-i", str(combined_path),
                        "-vf", "fps=24",
                        "-c:v", "libx264", "-crf", "20", "-preset", "medium",
                        "-an",
                        raw_path,
                        timeout=180,
                    )
                    tg(f"🎬 step7 grid_multiref_main: combined ({src_dur:.1f}s) 直作 raw 视频 (CFR 24fps)")
                log(f"step7 STORYBOARD_GRID_MULTIREF_MAIN: raw_concat <- grid_multiref_combined (target={target_dur:.2f}s, pad={pad_dur:.2f}s)")
                return raw_path
            except Exception as e:
                tg(f"⚠️ grid_multiref combined 拉伸失败：{str(e)[:120]}，回退到下一路径")
                log(f"step7 STORYBOARD_GRID_MULTIREF_MAIN extend failed: {e}")
        else:
            tg("⚠️ STORYBOARD_GRID_MULTIREF_MAIN 开启但 grid_multiref_combined.mp4 不存在/过小，回退到下一路径")

    # 故事板 trailer 主路径：直接用 storyboard_trailer.mp4 作为 raw 视频
    # 用 tpad+fps 把 trailer 拉伸到旁白长度并强制 24fps CFR（关键：避免后端通过拉 PTS 凑长度导致播放卡顿）
    if STORYBOARD_TRAILER_MAIN:
        trailer_path = OUTPUT_DIR / "storyboard_trailer.mp4"
        if trailer_path.exists() and trailer_path.stat().st_size > 100000:
            raw_path = str(OUTPUT_DIR / "raw_concat.mp4")
            try:
                trailer_dur = ffprobe_duration(str(trailer_path))
                # 目标时长：优先 master_voice.mp3 实际时长（最准），其次用 script 时间轴
                voice_path = OUTPUT_DIR / "master_voice.mp3"
                if voice_path.exists() and voice_path.stat().st_size > 10000:
                    target_dur = ffprobe_duration(str(voice_path)) + 0.5
                else:
                    target_dur = max(
                        (s.get("audio_start", 0) + s.get("vid_duration", s.get("dur", 0))) for s in script
                    ) + 0.5
                pad_dur = max(0.0, target_dur - trailer_dur)
                if pad_dur > 0.2:
                    # 循环 trailer 填充到 target_dur（避免 tpad clone 末帧定格）
                    # -stream_loop -1 + -t 让 trailer 循环到精确目标时长，fps=24 强制 CFR
                    loops_est = int(target_dur / trailer_dur) + 1
                    ffmpeg(
                        "-stream_loop", "-1",
                        "-i", str(trailer_path),
                        "-t", f"{target_dur:.3f}",
                        "-vf", "fps=24",
                        "-c:v", "libx264", "-crf", "20", "-preset", "medium",
                        "-an",
                        raw_path,
                        timeout=300,
                    )
                    tg(f"🎬 step7: trailer ({trailer_dur:.1f}s) 循环 ~{loops_est}× 填到 {target_dur:.1f}s @24fps CFR")
                else:
                    # 即使不需要拉伸也重编码到 CFR，避免源 VFR 引发后续播放问题
                    ffmpeg(
                        "-i", str(trailer_path),
                        "-vf", "fps=24",
                        "-c:v", "libx264", "-crf", "20", "-preset", "medium",
                        "-an",
                        raw_path,
                        timeout=180,
                    )
                    tg(f"🎬 step7: trailer ({trailer_dur:.1f}s) 直作 raw 视频 (CFR 24fps 转码)")
                log(f"step7 STORYBOARD_TRAILER_MAIN: raw_concat <- storyboard_trailer (target={target_dur:.2f}s, pad={pad_dur:.2f}s, fps=24)")
                return raw_path
            except Exception as e:
                tg(f"⚠️ trailer 拉伸失败：{str(e)[:120]}，回退到逐镜拼接")
                log(f"step7 STORYBOARD_TRAILER_MAIN extend failed: {e}")
        else:
            tg("⚠️ STORYBOARD_TRAILER_MAIN 开启但 storyboard_trailer.mp4 不存在/过小，回退到逐镜拼接")
            log("step7 STORYBOARD_TRAILER_MAIN fallback: trailer missing, using per-scene concat")
    concat_txt = OUTPUT_DIR / "concat.txt"
    segment_paths = [str(s["vid_path"]) for s in script]
    audio_flags = [_has_audio_stream(p) for p in segment_paths]
    prefer_embedded_partial_audio = (
        any(audio_flags)
        and not all(audio_flags)
        and (
            (WITH_MOTION and VOICE_ASSET_AUDIO_DUB_EXPERIMENT and VOICE_ASSET_AUDIO_DUB_PARTIAL_OK)
            or (ADS_DIALOGUE_MODE and ADSD_ALMIGHTY_AUDIO_DUB_EXPERIMENT)
        )
    )
    if prefer_embedded_partial_audio:
        log("视频片段音轨混合：部分片段含段内语音，缺音片段补静音，保留 WeryDance 段内音色")
        filled_paths: list[str] = []
        for i, src in enumerate(segment_paths):
            if audio_flags[i]:
                filled_paths.append(src)
                continue
            dur = ffprobe_duration(src)
            dst = str(OUTPUT_DIR / f"seg_{i}_concat_silence_audio.mp4")
            ffmpeg(
                "-f", "lavfi", "-t", f"{dur:.3f}",
                "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
                "-i", src,
                "-map", "1:v",
                "-map", "0:a",
                "-c:v", "copy",
                "-c:a", "aac", "-b:a", "128k",
                "-shortest",
                dst,
                timeout=120,
            )
            filled_paths.append(dst)
        segment_paths = filled_paths
    elif any(audio_flags) and not all(audio_flags):
        log("视频片段音轨混合：部分片段含段内语音，拼接前剥离为静音视频，最终回退主音轨")
        stripped_paths: list[str] = []
        for i, src in enumerate(segment_paths):
            if not audio_flags[i]:
                stripped_paths.append(src)
                continue
            dst = str(OUTPUT_DIR / f"seg_{i}_concat_noaudio.mp4")
            ffmpeg(
                "-i", src,
                "-map", "0:v",
                "-c:v", "copy",
                "-an",
                dst,
                timeout=120,
            )
            stripped_paths.append(dst)
        segment_paths = stripped_paths
    with open(concat_txt, "w") as f:
        for path in segment_paths:
            f.write(f"file '{path}'\n")

    raw_path = str(OUTPUT_DIR / "raw_concat.mp4")
    ffmpeg(
        "-f", "concat", "-safe", "0", "-i", str(concat_txt),
        "-c", "copy", raw_path,
    )
    dur = ffprobe_duration(raw_path)
    actual_w, actual_h = ffprobe_video_size(raw_path)
    if actual_w and actual_h:
        tg(f"✅ 视频轨拼接完成，总时长 {dur:.2f}s，分辨率 {actual_w}×{actual_h}")
    else:
        tg(f"✅ 视频轨拼接完成，总时长 {dur:.2f}s，分辨率未知（目标 {VIDEO_W}×{VIDEO_H}）")
    return raw_path


# ── 第八步：生成 ASS 字幕 ────────────────────────────────────────────────────
def _werydance_caption_covered_turns() -> set[int]:
    covered: set[int] = set()
    for qa_name in ("motion_qa.json", "lip_sync_qa.json"):
        p = OUTPUT_DIR / qa_name
        if not p.exists():
            continue
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            records = data.get("records") if isinstance(data, dict) else []
        except Exception:
            records = []
        for record in records or []:
            try:
                turn = int(record.get("turn") or 0)
            except Exception:
                turn = 0
            if (
                turn > 0
                and record.get("pass")
                and record.get("werydance_captions_requested")
                and not record.get("ass_fallback_required")
            ):
                covered.add(turn)
    return covered


def step8_subtitles(script: list[dict]) -> str:
    werydance_caption_turns = _werydance_caption_covered_turns() if WERYDANCE_CAPTIONS else set()
    ass_fallback_turns: list[int] = []
    werydance_captioned_turns: list[int] = []

    def ass_time(sec: float) -> str:
        h  = int(sec // 3600)
        m  = int((sec % 3600) // 60)
        s  = int(sec % 60)
        cs = int((sec % 1) * 100)
        return f"{h}:{m:02d}:{s:02d}.{cs:02d}"

    # ── 字幕分段：LLM 智能语义断句 ──
    def _llm_split_subtitles(all_lines: list[str], max_chars: int) -> list[list[str]] | None:
        """用 LLM 对所有台词做语义断句，返回每句台词的分行列表"""
        numbered = "\n".join(f"{i+1}. {l}" for i, l in enumerate(all_lines))
        prompt = f"""你是专业字幕编辑。把以下台词按语义断成短行，用于视频字幕逐行显示。

规则：
1. 每行 5~{max_chars} 个中文字（严格，不能少于 5 个字，不能超过 {max_chars} 个字）
2. 在语义完整的地方断行，不要把词语或成语拆开
3. 虚词（的、了、在、与、和、把、被）不能单独出现在行首或行尾
4. 去掉所有逗号、顿号、句号、冒号，只保留问号和感叹号
5. 每行必须是一个完整的语义单元，读起来通顺
6. 宁可让一行接近上限，也不要拆成太多碎片短行

台词：
{numbered}

输出格式（严格 JSON，每句台词对应一个数组）：
[["第1句第1行", "第1句第2行"], ["第2句第1行"], ...]
只输出 JSON，不加任何说明。"""
        try:
            raw = chat("GEMINI_25_FLASH", "你是专业字幕编辑，只输出 JSON。", prompt)
            arr_start = raw.find('[')
            arr_end = raw.rfind(']')
            if arr_start >= 0 and arr_end > arr_start:
                result = json.loads(raw[arr_start:arr_end + 1])
                if len(result) == len(all_lines):
                    log(f"LLM 字幕断句成功，{len(result)} 句")
                    return result
                log(f"LLM 字幕断句数量不匹配（{len(result)} vs {len(all_lines)}），回退规则断句")
            else:
                log("LLM 字幕断句 JSON 解析失败，回退规则断句")
        except Exception as e:
            log(f"LLM 字幕断句失败: {e}，回退规则断句")
        return None

    # 单字虚词：不应独立出现在行首或行尾
    _STICKY_WORDS = {"的", "地", "得", "与", "和", "或", "要", "在", "把", "被", "让", "从", "向", "往", "对", "是", "了", "着", "过"}
    _PROTECTED_TERMS = [
        "狸猫换太子", "宋仁宗", "仁宗盛治", "包拯", "范仲淹", "欧阳修",
        "千古名篇", "黄金时代", "真天子", "大宋", "正史", "仁政",
        "民间传说", "被后世误解", "心理防线",
    ]
    _BREAK_BEFORE = ("因为", "但是", "却", "可", "谁想", "原以为", "所有人", "历史", "所谓")
    _BREAK_AFTER = ("才是", "不是", "而是", "换来的是", "留给历史的", "靠", "把")

    def _jieba_split(text: str, max_len: int) -> list[str]:
        """jieba 分词 + 虚词保护断行"""
        if len(text) <= max_len:
            return [text]
        import jieba
        words = list(jieba.cut(text))
        parts, buf_words, buf_len = [], [], 0
        for w in words:
            if buf_len > 0 and buf_len + len(w) > max_len:
                if w in _STICKY_WORDS and buf_len + len(w) <= max_len + 1:
                    buf_words.append(w); buf_len += len(w); continue
                if buf_words and buf_words[-1] in _STICKY_WORDS and buf_len <= max_len + 1:
                    buf_words.append(w); buf_len += len(w); continue
                parts.append("".join(buf_words))
                buf_words = [w]; buf_len = len(w)
            else:
                buf_words.append(w); buf_len += len(w)
        if buf_words:
            parts.append("".join(buf_words))
        return [p for p in parts if p.strip()]

    def _rule_split(text: str, max_chars: int) -> list[str]:
        """规则兜底：标点断句 → 贪心合并 → jieba 分词断行 → 碎片合并"""
        # 1. 标点断句
        clauses = re.split(r'([，。！？；、：])', text)
        result, buf = [], ""
        for part in clauses:
            if re.match(r'^[，。！？；、：]$', part):
                buf += part
            else:
                if buf: result.append(buf)
                buf = part
        if buf: result.append(buf)
        clauses = [c for c in result if c.strip()]
        # 2. 贪心合并短句
        merge_max = max_chars + 4
        merged, buf = [], ""
        for c in clauses:
            if not buf: buf = c
            elif len(buf) + len(c) <= merge_max: buf += c
            else: merged.append(buf); buf = c
        if buf: merged.append(buf)
        # 3. jieba 分词断行
        segments = []
        for m in merged:
            segments.extend(_jieba_split(m, merge_max))
        # 4. 碎片合并
        cleaned = []
        for seg in segments:
            if cleaned and len(seg) <= 3 and len(cleaned[-1]) + len(seg) <= merge_max:
                cleaned[-1] += seg
            else:
                cleaned.append(seg)
        return cleaned

    def _clean_display(text: str) -> str:
        """去掉逗号、顿号、句号、冒号；只保留问号、感叹号"""
        return re.sub(r'[，、：。]', '', text).strip()

    def _visual_width(text: str) -> float:
        width = 0.0
        for ch in text:
            if ch in "!?！？":
                width += 0.55
            elif ch.isascii():
                width += 0.55 if ch.isalnum() else 0.35
            else:
                width += 1.0
        return width

    def _tokenize_subtitle(text: str) -> list[str]:
        """Tokenize for subtitle wrapping while keeping names/allusions intact."""
        text = text.strip()
        if not text:
            return []
        protected = sorted(_PROTECTED_TERMS, key=len, reverse=True)
        spans: list[tuple[int, int, str]] = []
        pos = 0
        while pos < len(text):
            match = next((term for term in protected if text.startswith(term, pos)), None)
            if match:
                spans.append((pos, pos + len(match), match))
                pos += len(match)
            else:
                pos += 1
        if spans:
            tokens: list[str] = []
            cursor = 0
            for start, end, term in spans:
                if start > cursor:
                    tokens.extend(_tokenize_subtitle(text[cursor:start]))
                tokens.append(term)
                cursor = end
            if cursor < len(text):
                tokens.extend(_tokenize_subtitle(text[cursor:]))
            return [t for t in tokens if t.strip()]
        try:
            import jieba
            words = [w for w in jieba.cut(text) if w.strip()]
        except Exception:
            words = list(text)
        tokens: list[str] = []
        for w in words:
            tokens.extend(ch for ch in w if ch.strip()) if len(w) > 6 else tokens.append(w)
        return [t for t in tokens if t.strip()]

    def _split_long_token(token: str, max_width: float) -> list[str]:
        if _visual_width(token) <= max_width:
            return [token]
        chunks, buf = [], ""
        for ch in token:
            if buf and _visual_width(buf + ch) > max_width:
                chunks.append(buf)
                buf = ch
            else:
                buf += ch
        if buf:
            chunks.append(buf)
        return chunks

    def _rebalance_two_lines(lines: list[str], max_width: float) -> list[str]:
        if len(lines) != 2:
            return lines
        a, b = lines
        # If the second line is tiny, move the last token from line 1 down when it still fits.
        if _visual_width(b) < 4 and _visual_width(a) > 5:
            toks = _tokenize_subtitle(a)
            if len(toks) >= 2:
                moved = toks[-1] + b
                kept = "".join(toks[:-1])
                if _visual_width(moved) <= max_width and kept:
                    return [kept, moved]
        return lines

    def _wrap_card(text: str, max_width: float | None = None, max_lines: int = 2) -> list[str]:
        """Wrap into one subtitle card: semantic tokens, max two display lines."""
        max_width = max_width or (9.0 if IS_VERTICAL else 14.5)
        text = _clean_display(text)
        if not text:
            return []
        for marker in _BREAK_BEFORE:
            text = text.replace(marker, f"|{marker}")
        for marker in _BREAK_AFTER:
            text = text.replace(marker, f"{marker}|")
        clauses = [c for c in text.split("|") if c.strip()]
        lines: list[str] = []
        current = ""
        for clause in clauses:
            for token in _tokenize_subtitle(clause):
                for piece in _split_long_token(token, max_width):
                    candidate = current + piece
                    if not current or _visual_width(candidate) <= max_width:
                        current = candidate
                    else:
                        if current:
                            lines.append(current)
                        current = piece
        if current:
            lines.append(current)

        lines = _rebalance_two_lines(lines, max_width)

        cards: list[str] = []
        for i in range(0, len(lines), max_lines):
            card_lines = lines[i:i + max_lines]
            if card_lines:
                cards.append(r"\N".join(card_lines))
        return cards

    ass_path = OUTPUT_DIR / "subs.ass"
    margin_l = 50 if IS_VERTICAL else 40
    margin_r = 50 if IS_VERTICAL else 40
    margin_v = 180 if IS_VERTICAL else 50
    header = f"""\
[Script Info]
ScriptType: v4.00+
PlayResX: {VIDEO_W}
PlayResY: {VIDEO_H}
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial Unicode MS,{SUBTITLE_FONTSIZE},&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,4,1,2,{margin_l},{margin_r},{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    # LLM 智能断句（一次调用处理所有台词），失败则规则兜底
    # silent_b 不出字幕：text 为空，不进 LLM 断句也不写 dialogue 行
    subtitled_idxs = [i for i, s in enumerate(script) if not _is_silent_b(s) and str(s.get('text', '')).strip()]
    all_texts = [script[i]['text'] for i in subtitled_idxs]
    llm_result_compact = _llm_split_subtitles(all_texts, SUBTITLE_MAX_CHARS) if all_texts else None
    # llm_result 按全 script idx 对齐：silent_b 对应位置填 None
    llm_result: list | None = None
    if llm_result_compact is not None:
        llm_result = [None] * len(script)
        for compact_i, orig_i in enumerate(subtitled_idxs):
            if compact_i < len(llm_result_compact):
                llm_result[orig_i] = llm_result_compact[compact_i]

    with open(ass_path, "w", encoding="utf-8") as f:
        f.write(header)
        SUB_GAP = 0.10
        FADE_TAG = r"{\fad(150,100)}"

        for idx, s in enumerate(script):
            turn = idx + 1
            if _is_silent_b(s) or not str(s.get('text', '')).strip():
                # silent_b / 空 text：跳过字幕行
                continue
            if turn in werydance_caption_turns:
                werydance_captioned_turns.append(turn)
                continue
            ass_fallback_turns.append(turn)
            t_start, t_end = s['sub_start'], s['sub_end']
            if llm_result and idx < len(llm_result) and llm_result[idx]:
                segments = [_clean_display(line) for line in llm_result[idx]]
            else:
                segments = [_clean_display(line) for line in _rule_split(s['text'], SUBTITLE_MAX_CHARS)]
            segments = [seg for seg in segments if seg.strip()]
            if not segments:
                segments = [_clean_display(s['text'])]
            # 短行合并：< 5 字的行合并到前一行或后一行
            merged_segs = []
            for seg in segments:
                if merged_segs and len(seg) < 5 and len(merged_segs[-1]) + len(seg) <= SUBTITLE_MAX_CHARS + 2:
                    merged_segs[-1] += seg
                elif len(seg) < 5 and not merged_segs:
                    merged_segs.append(seg)  # 第一行先放着，等后面合并
                else:
                    # 检查前一行是否太短，吸入当前行
                    if merged_segs and len(merged_segs[-1]) < 5 and len(merged_segs[-1]) + len(seg) <= SUBTITLE_MAX_CHARS + 2:
                        merged_segs[-1] += seg
                    else:
                        merged_segs.append(seg)
            segments = merged_segs if merged_segs else segments
            segments = [
                chunk
                for seg in segments
                for chunk in _wrap_card(seg)
            ]

            total_chars = sum(len(c.replace(r"\N", "")) for c in segments) or 1
            duration = t_end - t_start
            total_gaps = max(0, len(segments) - 1) * SUB_GAP
            content_dur = max(duration - total_gaps, duration * 0.5)
            cursor = t_start
            # 跨 turn 边界保护：紧凑模式 pause=0 时本 turn 末尾 segment 跟下 turn 首段会贴死
            # 末段 seg_end 收 SUB_GAP，确保跨 turn 也有 SUB_GAP 间隙
            has_next_turn = (idx + 1) < len(script)
            for seg_i, seg in enumerate(segments):
                seg_dur = max(content_dur * len(seg.replace(r"\N", "")) / total_chars, 0.8)
                is_last_seg = (seg_i == len(segments) - 1)
                cap_end = (t_end - SUB_GAP) if (is_last_seg and has_next_turn) else t_end
                seg_end = min(cursor + seg_dur, cap_end)
                if seg.strip():
                    f.write(
                        f"Dialogue: 0,{ass_time(cursor)},{ass_time(seg_end)},"
                        f"Default,,0,0,0,,{FADE_TAG}{seg}\n"
                    )
                cursor = seg_end + SUB_GAP

    caption_qa = {
        "enabled": WERYDANCE_CAPTIONS,
        "policy": "werydance_caption_first_ass_per_turn_fallback",
        "total": len(script),
        "werydance_captioned_turns": werydance_captioned_turns,
        "ass_fallback_turns": ass_fallback_turns,
        "werydance_caption_count": len(werydance_captioned_turns),
        "ass_fallback_count": len(ass_fallback_turns),
        "ass_has_dialogue": len(ass_fallback_turns) > 0,
        "manual_visual_checks_required": [
            "werydance_caption_text_exact",
            "no_garbled_or_extra_text",
            "caption_not_occluding_subject",
            "ass_fallback_turns_have_no_duplicate_werydance_caption",
        ],
        "pass": True,
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }
    try:
        (OUTPUT_DIR / "werydance_caption_qa.json").write_text(
            json.dumps(caption_qa, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except Exception as e:
        log(f"werydance_caption_qa 写入失败: {e}")

    if ADS_DIALOGUE_MODE:
        try:
            ass_text = ass_path.read_text(encoding="utf-8", errors="replace")
            speakers = sorted({str(s.get("speaker", "")).strip() for s in script if s.get("speaker")})
            leaked = [sp for sp in speakers if f"{sp}：" in ass_text or f"{sp}:" in ass_text]
            subtitle_qa = {
                "mode": ADSD_MODE_NAME,
                "policy": "speaker_labels_internal_only",
                "speaker_label_leak_count": len(leaked),
                "leaked_speaker_labels": leaked,
                "pass": len(leaked) == 0,
                "created_at": datetime.now().isoformat(timespec="seconds"),
            }
            (OUTPUT_DIR / "subtitle_qa.json").write_text(
                json.dumps(subtitle_qa, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            if leaked:
                tg(f"⚠️ {ADSD_MODE_NAME} 字幕 QA：发现角色身份泄露 {leaked}")
            else:
                log(f"{ADSD_MODE_NAME} 字幕 QA 通过：未泄露对白者身份标签")
        except Exception as e:
            log(f"ADSD subtitle_qa 写入失败: {e}")

    if WERYDANCE_CAPTIONS:
        tg(
            f"✅ 字幕策略完成：WeryDance {len(werydance_captioned_turns)}/{len(script)} 镜，"
            f"ASS 兜底 {len(ass_fallback_turns)}/{len(script)} 镜"
        )
    else:
        tg(f"✅ ASS 字幕文件已生成，共 {len(script)} 行对白")
    return str(ass_path)


def _read_output_json(name: str) -> dict | list | None:
    try:
        p = OUTPUT_DIR / name
        if not p.exists():
            return None
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        log(f"读取 QA 文件失败 {name}: {e}")
        return None


def _qa_file_pass(name: str) -> bool | None:
    data = _read_output_json(name)
    if isinstance(data, dict) and "pass" in data:
        return bool(data.get("pass"))
    return None


def _ass_has_dialogue(ass_path: str | None) -> bool:
    if not ass_path:
        return False
    try:
        text = Path(ass_path).read_text(encoding="utf-8", errors="replace")
        return any(line.startswith("Dialogue:") for line in text.splitlines())
    except Exception:
        return False


def _write_adsd_delivery_qa(final_path: str) -> dict | None:
    """Final ADSD gate before Telegram delivery. Failed QA blocks publishing the finished video."""
    if not ADS_DIALOGUE_MODE:
        return None

    issues: list[str] = []
    warnings: list[str] = []

    final = Path(final_path)
    if not final.exists() or final.stat().st_size < 10000:
        issues.append(f"final video missing or too small: {final_path}")

    qa_summary = _read_output_json("qa_summary.json")
    audio_video_delta = None
    if isinstance(qa_summary, dict):
        audio_video_delta = qa_summary.get("audio_video_delta")
        if audio_video_delta is None:
            issues.append("qa_summary.audio_video_delta missing")
        elif float(audio_video_delta) > 0.25:
            issues.append(f"audio_video_delta too large: {audio_video_delta:.3f}s")
    else:
        issues.append("qa_summary.json missing")

    required_files = [
        ("subtitle_qa.json", "subtitle labels"),
        ("speaker_focus_qa.json", "speaker focus"),
        ("gender_voice_qa.json", "voice visual gender"),
    ]
    if ADSD_LIP_SYNC_EXPERIMENT:
        required_files.append(("lip_sync_qa.json", "lip sync"))

    for name, label in required_files:
        passed = _qa_file_pass(name)
        if passed is None:
            issues.append(f"{label} QA missing: {name}")
        elif not passed:
            issues.append(f"{label} QA failed: {name}")

    asr_passed = _qa_file_pass("asr_qa.json")
    if asr_passed is None:
        warnings.append("ASR text match QA missing: asr_qa.json")
    elif not asr_passed:
        asr_qa = _read_output_json("asr_qa.json")
        if isinstance(asr_qa, dict):
            warnings.append(
                "ASR text match QA failed: "
                f"similarity={asr_qa.get('similarity')}, missing={asr_qa.get('missing_count')}"
            )
        else:
            warnings.append("ASR text match QA failed: asr_qa.json")

    subtitle_qa = _read_output_json("subtitle_qa.json")
    if isinstance(subtitle_qa, dict) and subtitle_qa.get("leaked_speaker_labels"):
        issues.append(f"subtitle speaker label leak: {subtitle_qa.get('leaked_speaker_labels')}")

    timeline = _read_output_json("turn_timeline.json")
    dialogue_shape = None
    speaker_count = 0
    if isinstance(timeline, list):
        speakers = [str(t.get("speaker", "")).strip() for t in timeline if isinstance(t, dict)]
        speaker_count = len([s for s in dict.fromkeys(speakers) if s])
        shapes = [str(t.get("dialogue_shape", "")).strip() for t in timeline if isinstance(t, dict) and t.get("dialogue_shape")]
        dialogue_shape = shapes[0] if shapes else None
        if not speakers:
            issues.append("turn_timeline has no speakers")
        elif speaker_count > 4:
            issues.append(f"too many ADSD speakers: {speaker_count}")
        if dialogue_shape not in {"monologue", "dialogue", "ensemble"}:
            issues.append(f"invalid or missing dialogue_shape: {dialogue_shape}")
        elif dialogue_shape == "monologue" and speaker_count != 1:
            issues.append(f"monologue speaker_count mismatch: {speaker_count}")
        elif dialogue_shape == "dialogue" and speaker_count != 2:
            issues.append(f"dialogue speaker_count mismatch: {speaker_count}")
        elif dialogue_shape == "ensemble" and not (3 <= speaker_count <= 4):
            issues.append(f"ensemble speaker_count mismatch: {speaker_count}")
    else:
        issues.append("turn_timeline.json missing")

    lip_sync_qa = _read_output_json("lip_sync_qa.json")
    if ADSD_LIP_SYNC_EXPERIMENT and isinstance(lip_sync_qa, dict):
        # 只查 A-roll 口型成功率 — B-roll motion turn 不进 lip-sync 阈值
        a_roll_total = int(lip_sync_qa.get("a_roll_total", 0) or 0)
        a_roll_success = int(lip_sync_qa.get("a_roll_success", 0) or 0)
        if a_roll_total > 0:
            a_rate = a_roll_success / a_roll_total
            if a_rate < 0.8:
                issues.append(f"A-roll lip_sync success_rate below 0.8: {a_rate:.4f} ({a_roll_success}/{a_roll_total})")
            elif a_roll_success != a_roll_total:
                warnings.append(f"A-roll lip_sync partial success: {a_roll_success}/{a_roll_total}")
        # B-roll motion 失败单独 warning (不阻塞)
        b_roll_total = int(lip_sync_qa.get("b_roll_total", 0) or 0)
        b_roll_success = int(lip_sync_qa.get("b_roll_success", 0) or 0)
        if b_roll_total > 0 and b_roll_success != b_roll_total:
            warnings.append(f"B-roll motion partial: {b_roll_success}/{b_roll_total} (not lip-sync gated)")

    payload = {
        "mode": ADSD_MODE_NAME,
        "onsite_pov_mode": ADSD_ONSITE_POV_MODE,
        "lip_sync_experiment": ADSD_LIP_SYNC_EXPERIMENT,
        "lips_change_repair_enabled": ADSD_LIPS_CHANGE_REPAIR,
        "lips_change_all_enabled": ADSD_LIPS_CHANGE_ALL,
        "final_path": final_path,
        "pass": len(issues) == 0,
        "issues": issues,
        "warnings": warnings,
        "checks": {
            "subtitle_qa": _qa_file_pass("subtitle_qa.json"),
            "speaker_focus_qa": _qa_file_pass("speaker_focus_qa.json"),
            "gender_voice_qa": _qa_file_pass("gender_voice_qa.json"),
            # lip_sync_qa 已改名为 render_success_qa（本质是 WERYDANCE 渲染成功率，不验真实口型）
            # 仍保留旧 key 兼容下游 reader；file 双写
            "render_success_qa": _qa_file_pass("render_success_qa.json"),
            "lip_sync_qa": _qa_file_pass("lip_sync_qa.json"),
            "asr_qa": asr_passed,
            "audio_video_delta": audio_video_delta,
            "dialogue_shape": dialogue_shape,
            "speaker_count": speaker_count,
            "lips_change_repair_enabled": ADSD_LIPS_CHANGE_REPAIR,
            "lips_change_all_enabled": ADSD_LIPS_CHANGE_ALL,
        },
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }
    (OUTPUT_DIR / "delivery_qa.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return payload


def _write_bgm_only_qa(final_path: str, script: list[dict]) -> dict:
    """Gate ADR/ADS BGM-only delivery: final audio must be BGM, not silence/TTS."""
    issues: list[str] = []
    warnings: list[str] = []
    final = Path(final_path)
    bgm = OUTPUT_DIR / "bgm.mp3"
    timeline = _read_output_json("bgm_only_timeline.json")
    min_shot = float(os.environ.get("ADR_BGM_ONLY_MIN_SHOT", "2.5"))
    max_shot = float(os.environ.get("ADR_BGM_ONLY_MAX_SHOT", "8.0"))

    if not final.exists() or final.stat().st_size < 10000:
        issues.append(f"final video missing or too small: {final_path}")
    if not bgm.exists() or bgm.stat().st_size < 10000:
        issues.append("BGM missing or too small")
    for forbidden in ("master_voice.mp3", "dialogue_master.mp3"):
        if (OUTPUT_DIR / forbidden).exists():
            issues.append(f"unexpected TTS master exists in BGM-only mode: {forbidden}")
    if (OUTPUT_DIR / "subs.ass").exists():
        issues.append("unexpected subtitle file exists in BGM-only mode: subs.ass")

    video_dur = audio_dur = final_dur = None
    mean_volume = None
    try:
        final_dur = ffprobe_duration(final_path)
        probe = subprocess.check_output([
            "ffprobe", "-v", "error",
            "-show_entries", "stream=codec_type,duration",
            "-of", "json",
            final_path,
        ], stderr=subprocess.DEVNULL)
        streams = json.loads(probe.decode()).get("streams", [])
        video_dur = next((float(s["duration"]) for s in streams if s.get("codec_type") == "video" and s.get("duration")), None)
        audio_dur = next((float(s["duration"]) for s in streams if s.get("codec_type") == "audio" and s.get("duration")), None)
        if video_dur is None or audio_dur is None:
            issues.append("final video/audio stream duration missing")
        elif abs(video_dur - audio_dur) > 0.35:
            issues.append(f"audio_video_delta too large: {abs(video_dur - audio_dur):.3f}s")
    except Exception as e:
        issues.append(f"ffprobe failed: {e}")

    try:
        result = subprocess.run([
            "ffmpeg", "-hide_banner", "-nostats", "-i", final_path,
            "-af", "volumedetect", "-f", "null", "-"
        ], capture_output=True, text=True, timeout=45)
        m = re.search(r"mean_volume:\s*(-?\d+(?:\.\d+)?) dB", result.stderr)
        if m:
            mean_volume = float(m.group(1))
            if mean_volume < -55:
                issues.append(f"final audio appears silent: mean_volume={mean_volume}dB")
        else:
            warnings.append("mean_volume unavailable")
    except Exception as e:
        warnings.append(f"volumedetect failed: {e}")

    timeline_rows = []
    snap_rate = 0.0
    energy_candidate_count = 0
    if isinstance(timeline, dict) and isinstance(timeline.get("timeline"), list):
        timeline_rows = timeline.get("timeline") or []
        snap_rate = float(timeline.get("snap_rate") or 0.0)
        energy_candidate_count = int(timeline.get("energy_candidate_count") or 0)
    else:
        issues.append("bgm_only_timeline.json missing")
    if energy_candidate_count <= 0:
        warnings.append("BGM energy cut analysis produced no candidates")
    elif len(timeline_rows) > 1 and snap_rate < 0.15:
        warnings.append(f"BGM energy snap rate low: {snap_rate:.3f}")

    bad_duration = []
    for row in timeline_rows:
        try:
            dur = float(row.get("duration") or 0)
        except Exception:
            continue
        if dur < min_shot * 0.8 or dur > max_shot * 1.2:
            bad_duration.append(row.get("scene"))
    if bad_duration:
        warnings.append(f"shot duration outside soft range at scenes: {bad_duration[:8]}")

    payload = {
        "mode": "BGM_ONLY",
        "final_path": final_path,
        "bgm_path": str(bgm),
        "pass": len(issues) == 0,
        "issues": issues,
        "warnings": warnings,
        "checks": {
            "final_duration": final_dur,
            "video_duration": video_dur,
            "audio_duration": audio_dur,
            "audio_video_delta": abs(video_dur - audio_dur) if video_dur is not None and audio_dur is not None else None,
            "mean_volume_db": mean_volume,
            "scene_count": len(script),
            "timeline_scene_count": len(timeline_rows),
            "energy_candidate_count": energy_candidate_count,
            "snap_rate": round(snap_rate, 4),
            "subtitle_file_absent": not (OUTPUT_DIR / "subs.ass").exists(),
            "subtitles_rendered": False,
            "bgm_exists": bgm.exists(),
            "silent_voice_exists": (OUTPUT_DIR / "silent_voice.mp3").exists(),
            "tts_master_absent": not (OUTPUT_DIR / "master_voice.mp3").exists() and not (OUTPUT_DIR / "dialogue_master.mp3").exists(),
        },
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }
    (OUTPUT_DIR / "bgm_only_qa.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return payload


# ── 第九步：最终合成 ─────────────────────────────────────────────────────────
def step9_render(raw_path: str, voice_path: str, bgm_path: str | None, ass_path: str, topic: str) -> str:
    # 兜底：如果 bgm_path 为 None 但 bgm.mp3 文件实际存在且有效，强制补读
    if not bgm_path:
        fallback_bgm = str(OUTPUT_DIR / "bgm.mp3")
        if os.path.exists(fallback_bgm) and os.path.getsize(fallback_bgm) > 10000:
            bgm_path = fallback_bgm
            log(f"BGM 兜底生效：bgm_path 为 None 但文件存在，强制使用 {fallback_bgm}")
            tg(f"🎵 step9 BGM 最终兜底生效，使用 {fallback_bgm}")
        else:
            tg("❌ step9 BGM 最终兜底也失败：bgm.mp3 不存在或太小，视频将无BGM")
    else:
        tg(f"🎵 step9 BGM 正常传入: {bgm_path}")
    if NO_VOICE and not bgm_path:
        raise RuntimeError("ADR/ADS BGM-only 模式要求必须有 BGM；BGM 生成失败，阻断静音成片交付")
    use_embedded_dialogue_audio = False
    embedded_audio_mode = ""
    if ADS_DIALOGUE_MODE and ADSD_ALMIGHTY_AUDIO_DUB_EXPERIMENT:
        try:
            lip_qa = _read_output_json("lip_sync_qa.json")
            records = lip_qa.get("records") or []
            generated_count = sum(1 for r in records if r.get("pass") and r.get("video_has_audio") and r.get("generated_audio_from_prompt_dialogue"))
            has_raw_audio = _has_audio_stream(raw_path)
            expected_count = int(lip_qa.get("total") or len(records) or 0)
            use_embedded_dialogue_audio = has_raw_audio and generated_count == expected_count and generated_count > 0
            if use_embedded_dialogue_audio:
                embedded_audio_mode = "adsd_almighty_audio_dub"
        except Exception as e:
            log(f"Almighty audio-dub embedded audio 检测失败，继续使用主音轨: {e}")
    elif WITH_MOTION and VOICE_ASSET_AUDIO_DUB_EXPERIMENT:
        try:
            motion_qa = _read_output_json("motion_qa.json")
            records = motion_qa.get("records") or []
            generated_count = sum(1 for r in records if r.get("pass") and r.get("video_has_audio") and r.get("generated_audio_from_prompt_dialogue"))
            expected_count = int(motion_qa.get("total") or len({int(r.get("turn", 0)) for r in records if r.get("turn")}) or len(records) or 0)
            has_raw_audio = _has_audio_stream(raw_path)
            coverage = generated_count / max(expected_count, 1)
            full_ready = generated_count == expected_count and generated_count > 0
            partial_ready = (
                VOICE_ASSET_AUDIO_DUB_PARTIAL_OK
                and generated_count > 0
                and coverage >= VOICE_ASSET_AUDIO_DUB_MIN_COVERAGE
            )
            use_embedded_dialogue_audio = has_raw_audio and (full_ready or partial_ready)
            if use_embedded_dialogue_audio:
                embedded_audio_mode = "motion_voice_asset_audio_dub" if full_ready else f"motion_voice_asset_audio_dub_partial_{generated_count}_of_{expected_count}"
        except Exception as e:
            log(f"motion voice-asset audio-dub embedded audio 检测失败，继续使用主音轨: {e}")
    render_audio_offset = 0.0 if (ADS_DIALOGUE_MODE and ADSD_LIP_SYNC_EXPERIMENT) else AUDIO_DELAY
    if NO_VOICE:
        sync_note = "BGM-only 模式：无旁白 TTS、无字幕，静音轨仅用于时间轴占位"
        audio_note = "BGM-only ✓"
    elif use_embedded_dialogue_audio:
        sync_note = f"{embedded_audio_mode or 'audio-dub'} 模式：使用视频段内生成语音，不叠加 TTS 主音轨"
        audio_note = "WERYDANCE 段内语音 ✓" + (" BGM ✓" if bgm_path else "")
    else:
        sync_note = "口型同步模式：音频不延迟" if render_audio_offset == 0 else "画面 → +{:.1f}s 字幕 → +{:.1f}s 配音".format(SUB_DELAY, render_audio_offset)
        audio_note = "主音轨 ✓" + (" BGM ✓" if bgm_path else "")
    ass_dialogue_ready = _ass_has_dialogue(ass_path)
    caption_qa = _read_output_json("werydance_caption_qa.json") if WERYDANCE_CAPTIONS else None
    if NO_VOICE:
        subtitle_note = "无字幕 ✓"
    elif isinstance(caption_qa, dict) and caption_qa.get("werydance_caption_count", 0) > 0:
        subtitle_note = (
            f"WeryDance 字幕 {caption_qa.get('werydance_caption_count')}/{caption_qa.get('total')} "
            f"+ ASS兜底 {caption_qa.get('ass_fallback_count')}/{caption_qa.get('total')} ✓"
        )
    else:
        subtitle_note = "字幕烧录 ✓"
    tg(f"🎬 最终合成中... 视频轨 ✓ {audio_note} {subtitle_note}\n{sync_note}")

    # ★ 音画同步修正：WERYDANCE 每段固定 5s × N，但配音总时长 ≠ 5N（往往更长）
    # 若配音比视频长 > 1s，整体用 setpts 拉伸视频到配音时长，避免 -shortest 截断尾部内容
    if use_embedded_dialogue_audio:
        log("音画同步修正跳过：当前使用 WERYDANCE 段内生成语音，不按 TTS 主音轨拉伸视频")
    else:
        try:
            voice_dur_chk = ffprobe_duration(voice_path)
            video_dur_chk = ffprobe_duration(raw_path)
            # 目标视频时长 = 配音时长 + AUDIO_DELAY 偏移 + 0.3s 收尾缓冲（保证配音完整不被 -shortest 截）
            target_video_dur = voice_dur_chk + render_audio_offset + 0.3
            if abs(target_video_dur - video_dur_chk) > 1.0:
                # 双向同步：视频长→压缩，视频短→拉伸
                ratio = target_video_dur / video_dur_chk
                direction = "拉伸" if ratio > 1 else "压缩"
                log(f"音画同步修正：video {video_dur_chk:.2f}s → 目标 {target_video_dur:.2f}s（配音 {voice_dur_chk:.2f}s + offset {render_audio_offset:.1f}s + 缓冲 0.3s）setpts ×{ratio:.3f} · {direction}")
                tg(f"🔧 音画同步修正：视频 {video_dur_chk:.1f}s → {direction}到 {target_video_dur:.1f}s")
                synced_raw = str(OUTPUT_DIR / "raw_concat_synced.mp4")
                ffmpeg(
                    "-i", raw_path,
                    "-filter:v", f"setpts={ratio:.4f}*PTS",
                    "-an",
                    "-c:v", "libx264", "-crf", "20", "-preset", "medium",
                    synced_raw,
                )
                raw_path = synced_raw
        except Exception as e:
            log(f"音画同步修正失败（使用原视频）：{e}")

    fmt_tag = ADSD_MODE_NAME if ADS_DIALOGUE_MODE else ("VDAR" if IS_VERTICAL else "HDAR")
    final_path = str(OUTPUT_DIR / f"ADR_V8_{fmt_tag}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4")
    ass_escaped = ass_path.replace("\\", "/").replace(":", "\\:") if ass_path else ""
    vf_base = f"scale={VIDEO_W}:{VIDEO_H},setsar=1,setdar={ASPECT_RATIO},tpad=stop_mode=clone:stop_duration=1.5"
    vf_with_subtitles = f"{vf_base},ass={ass_escaped}" if ass_dialogue_ready else vf_base

    # -itsoffset AUDIO_DELAY 延迟音频，画面先出
    # 非 BGM-only 字幕已在 step8 中加了 SUB_DELAY 偏移，在画面和配音之间
    offset = str(render_audio_offset)

    if bgm_path:
        if NO_VOICE:
            ffmpeg(
                "-i", raw_path,
                "-itsoffset", offset, "-i", bgm_path,
                "-filter_complex", "[1:a]volume=0.85[aout]",
                "-map", "0:v",
                "-map", "[aout]",
                "-vf", vf_base,
                "-c:v", "libx264", "-crf", "20", "-preset", "medium",
                "-c:a", "aac", "-b:a", "128k",
                "-aspect", ASPECT_RATIO,
                "-movflags", "+faststart",
                "-shortest",
                final_path,
            )
        elif use_embedded_dialogue_audio:
            ffmpeg(
                "-i", raw_path,
                "-i", bgm_path,
                "-filter_complex",
                "[0:a]apad=pad_dur=1.5,volume=1.2[va];[1:a]volume=0.45[ba];[va][ba]amix=inputs=2:duration=first[aout]",
                "-map", "0:v",
                "-map", "[aout]",
                "-vf", vf_with_subtitles,
                "-c:v", "libx264", "-crf", "20", "-preset", "medium",
                "-c:a", "aac", "-b:a", "128k",
                "-aspect", ASPECT_RATIO,
                "-movflags", "+faststart",
                "-shortest",
                final_path,
            )
        else:
            ffmpeg(
                "-i", raw_path,
                "-itsoffset", offset, "-i", voice_path,
                "-itsoffset", offset, "-i", bgm_path,
                "-filter_complex",
                "[1:a]apad=pad_dur=1.5,volume=1.5[va];[2:a]volume=0.6[ba];[va][ba]amix=inputs=2:duration=first[aout]",
                "-map", "0:v",
                "-map", "[aout]",
                "-vf", vf_with_subtitles,
                "-c:v", "libx264", "-crf", "20", "-preset", "medium",
                "-c:a", "aac", "-b:a", "128k",
                "-aspect", ASPECT_RATIO,
                "-movflags", "+faststart",
                "-shortest",
                final_path,
            )
    else:
        if use_embedded_dialogue_audio:
            ffmpeg(
                "-i", raw_path,
                "-filter_complex", "[0:a]apad=pad_dur=1.5[aout]",
                "-map", "0:v",
                "-map", "[aout]",
                "-vf", vf_with_subtitles,
                "-c:v", "libx264", "-crf", "20", "-preset", "medium",
                "-c:a", "aac", "-b:a", "128k",
                "-aspect", ASPECT_RATIO,
                "-movflags", "+faststart",
                "-shortest",
                final_path,
            )
        else:
            ffmpeg(
                "-i", raw_path,
                "-itsoffset", offset, "-i", voice_path,
                "-filter_complex", "[1:a]apad=pad_dur=1.5[aout]",
                "-map", "0:v",
                "-map", "[aout]",
                "-vf", vf_with_subtitles,
                "-c:v", "libx264", "-crf", "20", "-preset", "medium",
                "-c:a", "aac", "-b:a", "128k",
                "-aspect", ASPECT_RATIO,
                "-movflags", "+faststart",
                "-shortest",
                final_path,
            )

    size_mb = os.path.getsize(final_path) / (1024 * 1024)
    dur     = ffprobe_duration(final_path)
    if ADS_DIALOGUE_MODE:
        try:
            import subprocess as _sp
            probe = _sp.check_output([
                "ffprobe", "-v", "error",
                "-show_entries", "stream=codec_type,duration",
                "-of", "json",
                final_path,
            ], stderr=subprocess.DEVNULL)
            streams = json.loads(probe.decode()).get("streams", [])
            video_dur = next((float(s["duration"]) for s in streams if s.get("codec_type") == "video" and s.get("duration")), None)
            audio_dur = next((float(s["duration"]) for s in streams if s.get("codec_type") == "audio" and s.get("duration")), None)
            qa_summary = {
                "mode": ADSD_MODE_NAME,
                "onsite_pov_mode": ADSD_ONSITE_POV_MODE,
                "final_path": final_path,
                "format_duration": dur,
                "video_duration": video_dur,
                "audio_duration": audio_dur,
                "audio_video_delta": abs(video_dur - audio_dur) if video_dur is not None and audio_dur is not None else None,
                "turn_timeline_exists": (OUTPUT_DIR / "turn_timeline.json").exists(),
                "asr_result_exists": (OUTPUT_DIR / "speech_recognize_result.json").exists(),
                "asr_qa_exists": (OUTPUT_DIR / "asr_qa.json").exists(),
                "scene_qa_exists": (OUTPUT_DIR / "scene_qa.json").exists(),
                "speaker_focus_qa_exists": (OUTPUT_DIR / "speaker_focus_qa.json").exists(),
                "lip_sync_qa_exists": (OUTPUT_DIR / "lip_sync_qa.json").exists(),
                "subtitle_qa_exists": (OUTPUT_DIR / "subtitle_qa.json").exists(),
                "asr_qa_pass": _qa_file_pass("asr_qa.json"),
                "speaker_focus_qa_pass": _qa_file_pass("speaker_focus_qa.json"),
                "lip_sync_qa_pass": _qa_file_pass("lip_sync_qa.json"),
                "subtitle_qa_pass": _qa_file_pass("subtitle_qa.json"),
                "subtitle_exists": Path(ass_path).exists(),
                "created_at": datetime.now().isoformat(timespec="seconds"),
            }
            (OUTPUT_DIR / "qa_summary.json").write_text(
                json.dumps(qa_summary, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            if qa_summary["audio_video_delta"] is not None and qa_summary["audio_video_delta"] > 0.25:
                tg(f"⚠️ {ADSD_MODE_NAME} QA：音视频时长差 {qa_summary['audio_video_delta']:.3f}s，需复查")
            else:
                tg(f"✅ {ADSD_MODE_NAME} QA：音视频时长差 {qa_summary.get('audio_video_delta', 0):.3f}s")
        except Exception as e:
            log(f"ADSD qa_summary 写入失败: {e}")
    tg(f"✅ 成片输出完毕，文件大小 {size_mb:.1f} MB，时长 {dur:.2f}s")
    return final_path


# ── 第十步：推送 Telegram ────────────────────────────────────────────────────
def _generate_caption(topic: str, script: list[dict]) -> tuple[str, str, str]:
    """用 LLM 生成 (文案主体, 短标题, 热门标签串)。按 tone 切爆款方法论。
    文案主体不含标签；标签串独立，便于 step10 分两条发送，绕过 Telegram 一键复制 256 字符限制。"""
    lines = "\n".join(s["text"] for s in script)
    display_topic = _strip_topic_modifiers(topic)
    caption = f"ADR V8 — {display_topic}"
    short_title = display_topic[:16]
    hashtags = f"#{display_topic} #每日话题 #涨知识"
    tone = script[0].get("tone", "中性") if script else "中性"
    producer_brief = script[0].get("historical_context", "") if script else ""

    # ★ 题材检测：黄历/万年历/宜忌题材用专属"运势指南派" caption persona（最优先）
    is_almanac = any(k in topic for k in ("黄历", "万年历", "宜忌", "彭祖百忌"))

    # 按 tone 切受众 + 钩子套路 + 示例
    if is_almanac:
        # 黄历专属：中老年视频号最吃的运势指南派
        audience_block = "【受众】50-75 岁中老年为主（视频号主力），关心今日运势、家人平安、转发保佑；延伸 35-55 岁爱看每日运势的年轻人"
        caption_examples = (
            "示例 1（警示型）：'今天4月25日这事您可千万别做！老黄历一翻，今日不宜动土、作灶，属鼠的朋友尤其要注意。"
            "但要问今儿宜什么？—— 宜祭祀、宜纳采，准备订婚的年轻人可挑今天！财神爷今儿在正南方，出门请向南行。"
            "记得转发给家里老人，让他们也知道避开忌讳、踩准吉时～平安顺遂才是福。'"
            "\n示例 2（护佑型）：'4月25日是个好日子！庚午日冲鼠煞北，家中有属鼠的家人今儿多念叨几句平安。"
            "今日宜安香出火、宜订盟纳采。年轻人想求个好姻缘，今天拜拜观音是灵的。转发给孩子们看看，咱一家老小都平平安安～'"
        )
        title_hook_rules = (
            "钩子方法论（黄历专属，任选 1~2 种组合）：\n"
            "   • 警示钩子：'今天千万别做这事' / '4月25日忌XX，您知道吗' / '属X的今天注意'\n"
            "   • 吉时利益：'今日财神在正南' / '黄道吉日该干这事' / '4月25日宜结婚订婚'\n"
            "   • 护佑钩子：'转发给家人保平安' / '一家老小都顺遂' / '今日转运必看'\n"
            "   • 日期 + 悬念：'4月25日这天不简单' / '黄历一翻惊呆了'\n"
            "   允许使用：？ ！ 数字 中文标点（，、：）；禁止 emoji、英文半角、#号、书名号"
        )
        title_examples = (
            "示例：'4月25日千万别动土' / '今日财神在正南方' / '属鼠的今天看过来' / "
            "'黄道吉日宜订婚纳采' / '这天转发保一家平安'"
        )
        caption_struct = (
            "结构（爆款黄历配方）：警示/吉时钩子开头（一句抓住注意力）→ 具体宜忌 2-3 项（必须说人话，不用典）"
            "→ 生肖冲煞提醒（属X的注意）→ 吉时/财神方位（具体到东南西北）→ 号召转发家人（情感绑定）→ 不含标签（标签单独放）\n"
            "★ 时间词铁律：视频在当日发布，文案视角=当日观看。**严禁**用'明天/明日/后天'等相对时间词；统一用'今天'或绝对日期'4月29日'。"
            "示例：✅ '今天可得注意啦' / '4月29日是个好日子' / '今日冲兔煞东'；❌ '明天4月29日'（错位 1 天）"
        )
    elif tone == "怀旧":
        audience_block = "【受众】50-75 岁中老年为主；延伸到 35-55 岁怀旧族；对老物件/旧时光/集体记忆强共鸣"
        caption_examples = "示例：'咱这一辈人谁没读过这几本书？🥹 泛黄的《钢铁是怎样炼成的》《青春之歌》《红岩》……翻一页就是一段青春。现在的孩子再也不会体会那种一灯如豆、一书在手的感觉了。您最难忘的是哪一本？评论区说说～ #读书日 #那些年 #老一辈的回忆 #怀旧书单'"
        title_hook_rules = (
            "钩子方法论（从 4 种套路任选 1~2 种组合）：\n"
            "   • 集体记忆：'咱这一辈' / '那些年' / '一代人的回忆'\n"
            "   • 反问唤醒：'您还记得吗' / '谁家没有过…'\n"
            "   • 时光对比：'几十年过去了，X 变了吗' / '那时候 vs 现在'\n"
            "   • 物件情感：'一本书 一个时代' / '这东西 勾起多少回忆'\n"
            "   允许使用：？ 数字 中文标点（，、：）；禁止 emoji、英文半角、#号、书名号、！（保持温柔怀旧感）"
        )
        title_examples = "示例：'那些年我们读过的老书' / '咱这一辈人的青春书架' / '您还记得一灯如豆的日子吗'"
        caption_struct = "结构：情感钩子开头（一句唤起共鸣）→ 具体老物件/老书名列 2-3 个 → 反问邀请分享 → 3~5 个话题标签"
    elif tone == "轻松":
        audience_block = "【受众】视频号/抖音泛用户，对有趣/反差/治愈内容敏感；如果主题涉及校园/儿童，封面受众还包含学生家长、老师"
        caption_examples = "示例：'食堂居然能认识每个娃！这波 AI 操作直接封神 😍 小朋友上学吃饭再也不用操心挑食和过敏了，老师和家长都能实时看到孩子吃了啥。转发给你家娃看看吧～ #AI教育 #智慧食堂 #校园黑科技'"
        title_hook_rules = (
            "钩子方法论（从 5 种套路任选 1~2 种组合）：\n"
            "   • 反差悬念：'居然 / 没想到 / 你敢信'\n"
            "   • 数字利益：'3 招学会…' / '1 分钟看懂…'\n"
            "   • 情绪冲击：'太酷了！' / '这也行？！'\n"
            "   • 身份共鸣：'小学生都在玩的…' / '二年级孩子的黑科技'\n"
            "   • 警示钩子（少用）：'家长注意：…'\n"
            "   允许使用：？ ！ 数字 中文标点（，、：）；禁止 emoji、英文半角、#号、书名号"
        )
        title_examples = "示例：'食堂居然能认识你？' / 'AI 魔法食堂太绝了！' / '这才是小学该有的样子' / '二年级孩子的黑科技'"
        caption_struct = "结构：反差钩子开头（1 句）→ 核心亮点 3 点（可用数字列点）→ 号召转发（1 句）→ 3~5 个话题标签"
    elif tone == "庄重":
        audience_block = "【受众】视频号/抖音对历史/时政/警示类内容感兴趣的用户，含中老年与泛历史爱好者"
        caption_examples = "示例：'XXXX 年 X 月 X 日，这一天改变了 XXX 的命运。翻开那段尘封历史…逝者已矣，后人当记。#历史回顾 #XXX事件 #不能忘记'"
        title_hook_rules = (
            "钩子方法论：\n"
            "   • 日期通告：'2026 年 X 月 X 日 + 关键事件/人物'\n"
            "   • 警示钩子：'这一天…' / '铭记…'\n"
            "   允许使用：数字 中文标点（，、：）；禁止 emoji、英文半角、#号、书名号、？！（保持庄重）"
        )
        title_examples = "示例：'2026 年 4 月 21 日泰戈尔访华' / '那一夜上海沦陷' / '1976 年唐山大地震'"
        caption_struct = "结构：日期或关键信息开头 → 事件核心 → 意义点题 → 3~5 个话题标签"
    else:  # 中性
        audience_block = "【受众】视频号/抖音泛知识用户，对科普/人物/现象分析类内容感兴趣"
        caption_examples = "示例：'你真的了解 X 吗？3 个要点讲清楚…从 Y 到 Z，一次看懂这背后的逻辑。#科普 #X #涨知识'"
        title_hook_rules = (
            "钩子方法论：\n"
            "   • 数字利益：'3 个要点看懂 X' / '一次说清 X 的前世今生'\n"
            "   • 反差悬念：'为什么 X 值得关注？'\n"
            "   允许使用：？ 数字 中文标点（，、：）；禁止 emoji、英文半角、#号、书名号、！（保持克制）"
        )
        title_examples = "示例：'3 个要点看懂 AI 革命' / '为什么 X 值得关注' / '从 Y 到 Z 的 30 年'"
        caption_struct = "结构：悬念开头 → 核心信息（可用数字列点）→ 升华/引发思考 → 3~5 个话题标签"

    producer_block = f"\n【制片人准则（参考其 TITLE_HOOK 字段定调方向）】\n{producer_brief}\n" if producer_brief else ""

    try:
        best_score = -1
        best = (caption, short_title, hashtags)  # 默认兜底
        for _try_i in range(3):
            raw = chat("GEMINI_25_FLASH", "你是能出爆款的短视频文案策划师，熟悉视频号/抖音/小红书的点击钩子规律，会根据题材基调灵活切换受众和套路。",
                f"为以下短视频生成文案 + 短标题：\n\n"
                f"主题：{display_topic}\n"
                f"基调：{tone}\n"
                f"台词摘要：\n{lines}\n"
                f"{producer_block}\n"
                f"{audience_block}\n"
                f"【平台】视频号 / 抖音 / 小红书\n\n"
                f"1. 社媒文案主体（100~200 字，不用 Markdown，⚠️ 禁止在 CAPTION 里出现任何 # 号话题标签）：\n"
                f"   {caption_struct}\n"
                f"   语气：自然口语，不端着，带情绪感染力\n"
                f"   {caption_examples}\n\n"
                f"2. 短标题（封面大字，理想 10-13 个中文字，硬上限 14 字）：\n"
                f"   {title_hook_rules}\n"
                f"   {title_examples}\n"
                f"   出 3 个候选，挑最吸引人的那个输出（只输出最终一个）\n\n"
                f"3. 热门话题标签（⚠️ 必须 8~10 个，按以下算法友好度组合）：\n"
                f"   • 时效节点 × 1~2（今日/本周的节气/纪念日/热点）\n"
                f"   • 主题相关 × 3~4（具体到典籍名/作品名/概念名）\n"
                f"   • 情绪/立意 × 2~3（文化自信/怀旧杀/涨知识等正向钩子）\n"
                f"   • 算法助推 × 1~2（#涨知识 #每日话题 #每天学一点 #生活小知识 这类通用热门）\n"
                f"   输出格式：所有标签一行空格隔开，每个以 # 开头，禁止书名号\n\n"
                f"输出格式（严格遵守，三行各一项）：\n"
                f"CAPTION: 文案主体（纯文案，无任何 # 号）\n"
                f"TITLE: 短标题\n"
                f"HASHTAGS: #标签1 #标签2 #标签3 ...（8-10 个）")
            # 局部变量每次重置
            _c, _t, _h = caption, short_title, hashtags
            for line in raw.strip().splitlines():
                s = line.lstrip("- *#•·>").strip()
                low = s.upper()
                if low.startswith("CAPTION:") or low.startswith("CAPTION："):
                    c = s.split(":", 1)[-1].split("：", 1)[-1].strip()
                    c = re.sub(r'#\S+', '', c).strip()
                    if c: _c = c
                elif low.startswith("HASHTAGS:") or low.startswith("HASHTAGS："):
                    h = s.split(":", 1)[-1].split("：", 1)[-1].strip()
                    tags = re.findall(r'#\S+', h)
                    if tags: _h = " ".join(tags[:12])
                elif low.startswith("TITLE:") or low.startswith("TITLE："):
                    t = s.split(":", 1)[-1].split("：", 1)[-1].strip()
                    if tone == "轻松" or is_almanac:
                        t = re.sub(r"[#《》【】\"'()（）\[\]]", '', t)
                        t = re.sub(r'[a-zA-Z]', '', t)
                    elif tone == "庄重":
                        t = re.sub(r"[#《》【】\"'()（）\[\]!?！？]", '', t)
                        t = re.sub(r'[a-zA-Z]', '', t)
                    else:
                        t = re.sub(r"[#《》【】\"'()（）\[\]!！]", '', t)
                        t = re.sub(r'[a-zA-Z]', '', t)
                    t = _strip_topic_modifiers(t).strip()
                    if t: _t = t[:14]

            # 质量评分
            cap_len = len(_c) if _c and not _c.startswith("ADR V8") else 0
            tag_count = len(_h.split()) if _h else 0
            title_ok = 4 <= len(_t) <= 12 and not _t.startswith(topic[:6])
            score = (1 if cap_len >= 80 else 0) + (1 if tag_count >= 6 else 0) + (1 if title_ok else 0)
            log(f"[caption 尝试 {_try_i+1}/3] title='{_t}' ({len(_t)}) caption={cap_len}字 tags={tag_count} score={score}/3")

            # 满分直接用
            if score >= 3:
                best = (_c, _t, _h); break
            # 否则挑最高分
            if score > best_score:
                best = (_c, _t, _h); best_score = score

        caption, short_title, hashtags = best
        if SHORT_TITLE_OVERRIDE:
            short_title = re.sub(r"[#《》【】\"'()（）\[\]!！?？]", '', SHORT_TITLE_OVERRIDE).strip()[:16]
            log(f"短标题 override → '{short_title}'")
        log(f"社媒文案最终选定：title_len={len(short_title)}, caption_len={len(caption)}, hashtag_count={len(hashtags.split())}")
    except Exception as e:
        log(f"社媒文案生成失败: {e}")

    # ★ 黄历题材强制结构化（短标题 + caption 全部用 lunar_python 真实数据替代 LLM）
    # 短标题模板：「{月日} {干支}冲{冲生肖}煞{煞方位}」
    # caption 模板：黄历原文（公历/农历/干支/宜/忌/冲煞/吉神/凶神/彭祖百忌/五行纳音/二十八星宿）
    if is_almanac:
        m = re.search(r'(\d{4})\D*(\d{1,2})\D*(\d{1,2})', topic)
        if m:
            try:
                from lunar_python import Solar
                y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
                l = Solar.fromYmd(y, mo, d).getLunar()

                # 短标题
                short_title = f"{mo}月{d}日 {l.getDayInGanZhi()}冲{l.getDayChongShengXiao()}煞{l.getDaySha()}"
                log(f"黄历短标题 override → '{short_title}'")

                # caption 黄历原文（完整版含 15 个核心字段，与 22 分镜板块对齐）
                yi_list = " ".join(l.getDayYi()[:6])
                ji_list = " ".join(l.getDayJi()[:6])
                ji_shen = " ".join(l.getDayJiShen()[:4]) if l.getDayJiShen() else ""
                xiong_sha = " ".join(l.getDayXiongSha()[:4]) if l.getDayXiongSha() else ""
                fang_wei = f"喜神{l.getDayPositionXi()} 财神{l.getDayPositionCai()} 福神{l.getDayPositionFu()}"
                jie_qi_now = l.getJieQi() or ""
                jie_qi_str = jie_qi_now if jie_qi_now else f"{l.getPrevJieQi()}→{l.getNextJieQi()}"
                # 黄道吉时（12 时辰中黄道吉的）
                _zhi_to_h = {"子": 0, "丑": 2, "寅": 4, "卯": 6, "辰": 8, "巳": 10, "午": 12, "未": 14, "申": 16, "酉": 18, "戌": 20, "亥": 22}
                ji_shi_chars = []
                for zhi, h in _zhi_to_h.items():
                    try:
                        from lunar_python import Solar as _S
                        _t = _S.fromYmdHms(y, mo, d, h, 0, 0).getLunar().getTime()
                        if _t.getTianShenType() == "黄道":
                            ji_shi_chars.append(zhi)
                    except Exception:
                        pass
                ji_shi_str = "".join(ji_shi_chars) + "时" if ji_shi_chars else ""
                raw_caption = (
                    f"{y}年{mo}月{d}日\n"
                    f"农历{l.getMonthInChinese()}月{l.getDayInChinese()} "
                    f"{l.getYearInGanZhi()}年 {l.getMonthInGanZhi()}月 {l.getDayInGanZhi()}日\n\n"
                    f"【宜】{yi_list}\n"
                    f"【忌】{ji_list}\n"
                    f"【冲煞】冲{l.getDayChongShengXiao()}煞{l.getDaySha()}\n"
                    f"【方位】{fang_wei}\n"
                    f"【建星】{l.getZhiXing()}\n"
                    f"【天神】{l.getDayTianShen()}（{l.getDayTianShenType()}{l.getDayTianShenLuck()}）\n"
                    f"【吉神】{ji_shen}\n"
                    f"【凶神】{xiong_sha}\n"
                    f"【彭祖】{l.getPengZuGan()} {l.getPengZuZhi()}\n"
                    f"【胎神】{l.getDayPositionTai()}\n"
                    f"【星宿】{l.getXiu()}（{l.getXiuLuck()}）\n"
                    f"【纳音】{l.getDayNaYin()}\n"
                    f"【九宫】{l.getDayNineStar()}\n"
                    f"【吉时】{ji_shi_str}\n"
                    f"【节气】{jie_qi_str}\n\n"
                    f"宜趋避，顺时令。"
                )
                log(f"黄历 caption override → 黄历原文 ({len(raw_caption)} 字)")
                caption = raw_caption
            except Exception as e:
                log(f"黄历结构化失败（保留 LLM 版）: {e}")

    return caption, short_title, hashtags


def _overlay_title_on_cover(cover_path: str, title: str, tone: str) -> str:
    """在底图上按 tone 叠加中文大字标题（TIME/BBC/儿童杂志三套模板）。覆盖 cover_path。"""
    if not title:
        return cover_path
    try:
        from PIL import Image, ImageDraw, ImageFont
    except Exception as e:
        log(f"Pillow 不可用，跳过叠字：{e}")
        return cover_path
    try:
        im = Image.open(cover_path).convert("RGB")
    except Exception as e:
        log(f"封面叠字：打开失败 {e}")
        return cover_path

    W, H = im.size
    # 用 RGBA overlay 画半透明
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay, "RGBA")

    FONT_HEITI_MEDIUM = "/System/Library/Fonts/STHeiti Medium.ttc"
    FONT_HIRAGINO = "/System/Library/Fonts/Hiragino Sans GB.ttc"
    FONT_SONGTI = "/System/Library/Fonts/Supplemental/Songti.ttc"

    title_len = len(title)
    # 自适应字号：字越多字号越小
    if title_len <= 8:
        font_size = int(H * 0.10)
    elif title_len <= 12:
        font_size = int(H * 0.085)
    elif title_len <= 16:
        font_size = int(H * 0.072)
    else:
        font_size = int(H * 0.062)

    def _font(path, size):
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            return ImageFont.truetype(FONT_HIRAGINO, size)

    def _outline_text(d, xy, text, font, fill, outline_fill, outline_w):
        x, y = xy
        for dx in range(-outline_w, outline_w + 1):
            for dy in range(-outline_w, outline_w + 1):
                if dx or dy:
                    d.text((x + dx, y + dy), text, font=font, fill=outline_fill)
        d.text((x, y), text, font=font, fill=fill)

    if tone == "轻松":
        # 儿童杂志风：底部黄色圆角色块 + 白字 + 粗黑描边
        font = _font(FONT_HEITI_MEDIUM, font_size)
        bbox = draw.textbbox((0, 0), title, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        block_h = int(th * 1.8)
        block_y = H - block_h - int(H * 0.04)
        # 黄色圆角底块
        draw.rounded_rectangle(
            [int(W * 0.05), block_y, W - int(W * 0.05), block_y + block_h],
            radius=int(H * 0.02), fill=(255, 210, 0, 245),
        )
        tx = (W - tw) // 2 - bbox[0]
        ty = block_y + (block_h - th) // 2 - bbox[1]
        _outline_text(draw, (tx, ty), title, font, (255, 255, 255, 255), (0, 0, 0, 255), 3)

    elif tone == "庄重":
        # TIME 风：底部黑色半透明带 + 白字 + 右上角红色 TIME 风小标签
        font = _font(FONT_HEITI_MEDIUM, font_size)
        bbox = draw.textbbox((0, 0), title, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        block_h = int(th * 1.9)
        block_y = H - block_h - int(H * 0.03)
        # 黑色半透明带
        draw.rectangle([0, block_y, W, block_y + block_h], fill=(0, 0, 0, 210))
        tx = (W - tw) // 2 - bbox[0]
        ty = block_y + (block_h - th) // 2 - bbox[1]
        draw.text((tx, ty), title, font=font, fill=(255, 255, 255, 255))
        # 右上角红色 TIME 风小标签
        label = "ADR"
        label_font = _font(FONT_HEITI_MEDIUM, int(font_size * 0.45))
        lb = draw.textbbox((0, 0), label, font=label_font)
        lw, lh = lb[2] - lb[0], lb[3] - lb[1]
        pad = int(font_size * 0.22)
        lx = W - lw - pad * 2 - int(W * 0.04)
        ly = int(H * 0.03)
        draw.rectangle([lx, ly, lx + lw + pad * 2, ly + lh + pad * 2], fill=(220, 30, 30, 255))
        draw.text((lx + pad - lb[0], ly + pad - lb[1]), label, font=label_font, fill=(255, 255, 255, 255))

    else:  # 中性：BBC 风
        font = _font(FONT_HEITI_MEDIUM, font_size)
        bbox = draw.textbbox((0, 0), title, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        # 顶部红条（BBC 标志性）
        red_h = max(int(H * 0.035), 24)
        draw.rectangle([0, 0, W, red_h], fill=(187, 28, 28, 255))
        # 底部白色半透明带叠黑字
        block_h = int(th * 1.7)
        block_y = H - block_h - int(H * 0.04)
        draw.rectangle([0, block_y, W, block_y + block_h], fill=(255, 255, 255, 230))
        tx = int(W * 0.05) - bbox[0]
        ty = block_y + (block_h - th) // 2 - bbox[1]
        draw.text((tx, ty), title, font=font, fill=(25, 25, 25, 255))

    # 合成并保存
    out = Image.alpha_composite(im.convert("RGBA"), overlay).convert("RGB")
    out.save(cover_path, "JPEG", quality=92, optimize=True)
    log(f"封面叠字完成：tone={tone}, title_len={title_len}, font_size={font_size}")
    return cover_path


def _prepare_tg_photo(path: str, max_bytes: int = 9 * 1024 * 1024) -> str:
    """Telegram sendPhoto 对尺寸/体积敏感；保留原图，必要时生成轻量预览图。"""
    try:
        if os.path.getsize(path) <= max_bytes:
            return path
        from PIL import Image

        src = Path(path)
        preview = src.with_name(f"{src.stem}_tg_preview.jpg")
        im = Image.open(path).convert("RGB")
        im.thumbnail((1080, 1920), Image.Resampling.LANCZOS)
        im.save(preview, "JPEG", quality=88, optimize=True)
        return str(preview)
    except Exception as e:
        log(f"Telegram 封面预览压缩失败，尝试发送原图: {e}")
        return path


# ═══ Pantone 节气色卡系统（24 节气 × 专属色）═══════════════════════════════
# 每个节气从当天起到下个节气前一天都用这个色；给封面右上角做 Pantone 风色卡条签名
PANTONE_JIEQI = {
    "立春": {"code": "LC-2.04",  "name": "早春青", "hex": "#A8C990"},
    "雨水": {"code": "YS-2.19",  "name": "春水碧", "hex": "#8FBCA0"},
    "惊蛰": {"code": "JZ-3.06",  "name": "惊雷绿", "hex": "#9CCD7A"},
    "春分": {"code": "CF-3.21",  "name": "嫩柳黄", "hex": "#C8DD60"},
    "清明": {"code": "QM-4.05",  "name": "清明灰", "hex": "#B8C4B0"},
    "谷雨": {"code": "GY-4.20",  "name": "新笋绿", "hex": "#AFDD22"},
    "立夏": {"code": "LX-5.05",  "name": "石榴火", "hex": "#D43A2F"},
    "小满": {"code": "XM-5.20",  "name": "麦芒金", "hex": "#D4A642"},
    "芒种": {"code": "MZ-6.05",  "name": "芒种黄", "hex": "#E8C547"},
    "夏至": {"code": "XZ-6.21",  "name": "荷花粉", "hex": "#F2A6B3"},
    "小暑": {"code": "XS-7.07",  "name": "荷风青", "hex": "#4A8B5C"},
    "大暑": {"code": "DS-7.22",  "name": "蝉声红", "hex": "#C84A3A"},
    "立秋": {"code": "LQ-8.07",  "name": "桐叶黄", "hex": "#D9A74A"},
    "处暑": {"code": "CS-8.23",  "name": "暮秋橘", "hex": "#D87341"},
    "白露": {"code": "BL-9.07",  "name": "素瓷白", "hex": "#E8E0D0"},
    "秋分": {"code": "QF-9.23",  "name": "霜枫红", "hex": "#B23A48"},
    "寒露": {"code": "HL-10.08", "name": "寒露青", "hex": "#6A7B8B"},
    "霜降": {"code": "SJ-10.23", "name": "柿染橘", "hex": "#D87341"},
    "立冬": {"code": "LD-11.07", "name": "冬藏蓝", "hex": "#4A5D7E"},
    "小雪": {"code": "XX-11.22", "name": "雪青灰", "hex": "#9BA5AE"},
    "大雪": {"code": "DX-12.07", "name": "墨松绿", "hex": "#2F4F3E"},
    "冬至": {"code": "DZ-12.21", "name": "松墨黑", "hex": "#1C2E2B"},
    "小寒": {"code": "XH-1.05",  "name": "梅骨红", "hex": "#8B3A3A"},
    "大寒": {"code": "DH-1.20",  "name": "寒松翠", "hex": "#3A5F4A"},
}
# 默认兜底（查询失败时用当季通用色）
PANTONE_FALLBACK = {"code": "ADR-2026", "name": "中华青", "hex": "#AFDD22"}


def _get_pantone_for_date(year: int, month: int, day: int) -> dict:
    """根据公历日期查所属节气的 Pantone 色卡。找不到返回默认色卡。"""
    try:
        from lunar_python import Solar
        s = Solar.fromYmd(year, month, day)
        l = s.getLunar()
        # 先查是不是节气当天
        jq_today = l.getJieQi() if hasattr(l, "getJieQi") else ""
        if jq_today and jq_today in PANTONE_JIEQI:
            return PANTONE_JIEQI[jq_today]
        # 否则找最近一个已过节气
        try:
            prev = l.getPrevJieQi()
            prev_name = prev.getName() if prev and hasattr(prev, "getName") else str(prev)
            # prev_name 可能像 "谷雨"，也可能含其他前缀，取后两字匹配
            for jq in PANTONE_JIEQI:
                if jq in prev_name:
                    return PANTONE_JIEQI[jq]
        except Exception:
            pass
    except Exception:
        pass
    return PANTONE_FALLBACK


def _llm_bottom_note(topic: str, script_texts: list) -> str:
    """用 Gemini Flash 为当期主题生成一条 7-15 字的古典雅致封面注脚。"""
    lines_hint = "\n".join(script_texts[:2]) if script_texts else "（无台词，纯主题）"
    prompt = (
        f"为一张视频号封面设计底部文化注脚。\n\n"
        f"主题：{topic}\n"
        f"台词首 2 句：\n{lines_hint}\n\n"
        f"要求：\n"
        f"• 7-15 个中文字符（严格）\n"
        f"• 古典雅致，必须包含以下至少一项：典籍名（如齐民要术、月令、岁时记）、节气名（如谷雨、立夏）、"
        f"地域文化（如江南、中原）、时令物象（如雨燕、桐花、新笋）、人物大背景（如千年耕读）\n"
        f"• 用中点 · 分隔 2-3 个短语，例：雨生百谷 · 齐民要术 / 一灯如豆 · 青春书卷\n"
        f"• 纯文本，禁止标点（除中点）、emoji、英文、引号、书名号、#号\n\n"
        f"只输出注脚本身一行，不加任何解释。"
    )
    try:
        raw = chat("GEMINI_25_FLASH", "你是中国古典编辑，擅长从典籍节气物象里提炼诗意注脚。", prompt).strip()
        raw = raw.split("\n")[0].strip()
        # 清洗：去掉标点 / 英文 / 特殊字符（保留中点 · 和中文）
        raw = re.sub(r"[《》\"'【】\[\]()（）!?！？#。，、；：—…-]", '', raw)
        raw = re.sub(r'[a-zA-Z0-9]', '', raw)
        raw = raw.strip()
        if 5 <= len(raw) <= 20:
            return raw
    except Exception as e:
        log(f"LLM 底部注脚生成失败: {e}")
    return ""


def _get_bottom_note(topic: str, script: list | None = None) -> str:
    """返回封面底部文化注脚，4 级优先级：
    1. CLI --bottom-note / env ADR_BOTTOM_NOTE（最高，一次性覆盖）
    2. /Users/wekoidubai/ADR/bottom_notes.json 用户配置（exact_topic / by_date / by_keyword）
    3. LLM 动态生成（默认路径，诗意灵动）
    4. 硬编码关键词匹配（兜底，LLM 挂了才用）
    """
    # 1. CLI / env 覆盖
    if BOTTOM_NOTE_OVERRIDE:
        return BOTTOM_NOTE_OVERRIDE

    # 2. 用户配置文件
    try:
        cfg_path = Path("/Users/wekoidubai/ADR/bottom_notes.json")
        if cfg_path.exists():
            cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
            # 2a. 精确 topic 匹配
            if topic in cfg.get("exact_topic", {}):
                return cfg["exact_topic"][topic]
            # 2b. 精确日期（从 topic 提取 YYYY-MM-DD）
            m = re.search(r'(\d{4})\D*(\d{1,2})\D*(\d{1,2})', topic)
            if m:
                date_key = f"{int(m.group(1))}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"
                if date_key in cfg.get("by_date", {}):
                    return cfg["by_date"][date_key]
            # 2c. 关键词模糊匹配（顺序重要，越具体的 key 放前面）
            for kw, note in cfg.get("by_keyword", {}).items():
                if kw in topic:
                    return note
    except Exception as e:
        log(f"bottom_notes.json 加载失败（降级到 LLM）: {e}")

    # 3. LLM 动态生成（默认）
    script_texts = [s.get("text", "") for s in (script or [])][:3]
    llm_note = _llm_bottom_note(topic, script_texts)
    if llm_note:
        return llm_note

    # 4. 硬编码关键词兜底
    if "读书日" in topic or "书单" in topic or "怀旧书" in topic:
        return "世界读书日 · 阅读启智"
    if "地球日" in topic or "生态" in topic or "可持续" in topic:
        return "齐民要术 · 月令 · 中国生态智慧"
    if any(k in topic for k in ("黄历", "万年历", "宜忌", "彭祖百忌")):
        return "齐民要术 · 月令 · 二十四节气"
    for jq in PANTONE_JIEQI:
        if jq in topic:
            return f"{jq} · 物候时令"
    if any(k in topic for k in ("诞辰", "周年", "纪念")):
        return "岁月长河 · 人物记"
    if any(k in topic for k in ("小学", "校园", "演讲")):
        return "中华万年历 · 校园时光"
    return "中华万年历 · 时令智慧"


# 节日关键词 → 点题副标题映射（用于封面副标题"点题"）
FESTIVAL_DATE_TAG = {
    "世界读书日": "四月二十三 读书日",
    "读书日": "四月二十三 读书日",
    "世界地球日": "四月二十二 地球日",
    "地球日": "四月二十二 地球日",
    "妇女节": "三月初八 妇女节",
    "劳动节": "五月初一 劳动节",
    "植树节": "三月十二 植树节",
    "青年节": "五月初四 青年节",
    "儿童节": "六月初一 儿童节",
    "护士节": "五月十二 护士节",
    "教师节": "九月初十 教师节",
    "国庆": "十月初一 国庆节",
    "建党": "七月初一 建党节",
    "建军": "八月初一 建军节",
    "记者节": "十一月初八 记者节",
    "航天日": "四月廿四 航天日",
    "中国航天日": "四月廿四 航天日",
    "东方红": "四月廿四 航天日",
}


def _get_date_tag(topic: str) -> str:
    """从 topic 推断封面副标题的'点题日期'字符串。
    1) 匹配国际日/纪念日关键词（硬表）
    2) 匹配具体日期 YYYY-M-D
    3) 都没命中返回空串
    """
    for kw, tag in FESTIVAL_DATE_TAG.items():
        if kw in topic:
            return tag
    m = re.search(r'(\d{4})\D*(\d{1,2})\D*(\d{1,2})', topic)
    if m:
        _zh_num = ["零","一","二","三","四","五","六","七","八","九","十"]
        def _to_zh(n):
            if n <= 10: return _zh_num[n]
            if n < 20: return "十" + (_zh_num[n-10] if n > 10 else "")
            tens = n // 10
            units = n % 10
            return _zh_num[tens] + "十" + (_zh_num[units] if units else "")
        return f"{_to_zh(int(m.group(2)))}月{_to_zh(int(m.group(3)))}日"
    return ""


def _shrink_to_b64(img_path: str, max_width: int = 720) -> str:
    """v0.5 公共函数：缩图到 max_width 后 base64（避免 chat completion API 413 Too Large）。
    原图 12MB+ PNG → 缩到 720 宽 JPEG ~150-300K → base64 ~200-400K << API 上限
    """
    import base64
    from PIL import Image
    import io
    img = Image.open(img_path).convert("RGB")
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=85)
    return base64.b64encode(buf.getvalue()).decode()


def _llm_check_scenes_anomalies(script: list) -> set:
    """v0.2 智能异常检测：22 张分镜并发独立 Vision call（绕过 ffmpeg tile filter 的多 input 限制）。
    返回需要审批的 idx 集合（0-indexed）。
    异常类型：① 文字渲染错（数字/日期/中文乱字）② 内容严重偏离板块主题
    """
    n = len(script)
    if n == 0:
        return set()

    def _check_one(i_scene):
        i, scene = i_scene
        try:
            b64 = _shrink_to_b64(scene["img_path"])  # v0.5 缩图避 413
            payload = {
                "model": "GEMINI_25_FLASH",
                "messages": [{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": (
                            f"这是一张自动生成短视频的分镜图，题材可能是历史、文化、现实寓言、黄历或纯画面 BGM 视频。\n"
                            f"对应台词：\"{scene['text']}\"\n\n"
                            f"请保守宽容地判断这张图是否有以下两类**严重**异常：\n"
                            "1. 文字明显错误：图里渲染的中文字/数字/日期严重错乱（出现伪汉字、不存在的成语、错字明显）\n"
                            "2. 内容严重偏离：画面主体和台词/主题完全无关，或出现明显时代/文化错位（如晚清题材出现现代手机、古代中国题材画成欧洲宫廷）\n\n"
                            "宽容原则：色调差异、镜头角度差异、风格细微差异、抽象隐喻、无字幕画面都算正常，不要标记。\n"
                            "只回答 OK 或 ANOMALY 一个词，不加解释。"
                        )},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
                    ]
                }],
                "max_tokens": 10,
            }
            resp = req_post("/chat/completions", payload, timeout=60)
            verdict = resp.get("choices", [{}])[0].get("message", {}).get("content", "").strip().upper()
            return (i, "ANOMALY" in verdict)
        except Exception as e:
            log(f"[异常检测] 图 {i+1} 检测失败 ({e})，假设 OK")
            return (i, False)

    anomalies = set()
    with ThreadPoolExecutor(max_workers=8) as ex:
        results = list(ex.map(_check_one, list(enumerate(script))))
    for i, is_anomaly in results:
        if is_anomaly:
            anomalies.add(i)

    if not anomalies:
        log(f"[异常检测] 全部 {n} 张正常通过 ✓")
    else:
        log(f"[异常检测] 发现 {len(anomalies)} 张异常: {sorted(i+1 for i in anomalies)}")
    return anomalies


def _llm_check_cover_unique(cover_path: str) -> bool:
    """用 Gemini Vision 判断封面主标题是否唯一（未重复）。True=OK, False=重复需重做。"""
    try:
        b64 = _shrink_to_b64(cover_path)  # v0.5 缩图避 413
        payload = {
            "model": "GEMINI_25_FLASH",
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "text", "text": (
                        "看这张封面的中心主标题（画面正中大字、粗宋体 2x2 排列，共 4 个汉字如 '戊 辰 宜 忌'）。\n\n"
                        "主标题在整张封面上出现了几次？\n"
                        "- UNIQUE：干净的 2x2 布局，主标题 4 字各出现 1 次，没有任何字被重复画到其他行或位置\n"
                        "- DUPLICATED：某字被画了 2 次（如 '宜忌' 出现两行），或主标题整体被复制到其他位置\n\n"
                        "只回答 UNIQUE 或 DUPLICATED 一个词，不加解释。"
                    )},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
                ]
            }],
            "max_tokens": 10,
        }
        resp = req_post("/chat/completions", payload, timeout=60)
        verdict = resp.get("choices", [{}])[0].get("message", {}).get("content", "").strip().upper()
        log(f"[OCR 检测] 主标题: {verdict}")
        return "UNIQUE" in verdict
    except Exception as e:
        log(f"[OCR 检测] 失败，假设 OK：{e}")
        return True


def _llm_check_cover_quality(cover_path: str, expected_footer: str = "") -> dict:
    """v0.3 一次 Vision call 同时判断封面 4 维度质量：
    - unique: 主标题（如"庚午宜忌"）是否唯一无重复
    - has_footer: 底部是否有清晰可读的文化注脚
    返回 dict {unique: bool, has_footer: bool}
    """
    try:
        b64 = _shrink_to_b64(cover_path)  # v0.5 缩图避 413
        footer_hint = f"（应为 \"{expected_footer}\"）" if expected_footer else ""
        payload = {
            "model": "GEMINI_25_FLASH",
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "text", "text": (
                        "审查这张黄历封面的两个质量维度，输出严格 JSON。\n\n"
                        "1. unique：主标题（画面正中粗宋体 2x2 大字 4 个汉字）是否每字仅出现 1 次？没有重复或镜像？true / false\n"
                        f"2. has_footer：画面**最底部中心**是否有一行清晰可读的小字文化注脚（毛笔书法风格 sepia 棕色）{footer_hint}？两侧应有红色印章圆点装饰。true / false\n\n"
                        "只输出 JSON：{\"unique\": true/false, \"has_footer\": true/false}\n"
                        "不加任何解释。"
                    )},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
                ]
            }],
            "max_tokens": 60,
        }
        resp = req_post("/chat/completions", payload, timeout=60)
        raw = resp.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        s_idx = raw.find("{")
        e_idx = raw.rfind("}")
        if s_idx == -1:
            return {"unique": True, "has_footer": False}
        d = json.loads(raw[s_idx:e_idx+1])
        unique = bool(d.get("unique", True))
        has_footer = bool(d.get("has_footer", False))
        log(f"[封面质检] unique={unique} has_footer={has_footer}")
        return {"unique": unique, "has_footer": has_footer}
    except Exception as e:
        log(f"[封面质检] 失败: {e}")
        return {"unique": True, "has_footer": False}


def _try_almanac_cover(topic: str, script: list | None = None) -> str | None:
    """黄历日报专用封面：自动填真实 lunar 数据 + Kinfolk 季节模板。
    script 传入可让底部注脚 LLM 基于当期台词生成更贴切的诗意文案。"""
    if not any(k in topic for k in ("黄历", "万年历", "宜忌", "彭祖百忌")):
        return None
    m = re.search(r'(\d{4})\D*(\d{1,2})\D*(\d{1,2})', topic)
    if not m:
        return None
    year, month, day = int(m.group(1)), int(m.group(2)), int(m.group(3))
    try:
        from lunar_python import Solar
        s = Solar.fromYmd(year, month, day)
        l = s.getLunar()
        date_str = f"{year}年{month}月{day}日"
        lunar_str = f"农历{l.getMonthInChinese()}月{l.getDayInChinese()}"
        lunar_month_zh = f"{l.getMonthInChinese()}月"
        lunar_day_zh = l.getDayInChinese()
        chong_sha_short = f"{l.getDayChongShengXiao()}煞{l.getDaySha()}"
        gz_2 = l.getDayInGanZhi()  # 干支日 2 字（如"丁卯"）
        gz_str = f"{l.getDayInGanZhi()}日"
        yi_str = " · ".join(l.getDayYi()[:4])
        ji_str = " · ".join(l.getDayJi()[:4])
        chong_sha = f"冲{l.getDayChongShengXiao()} · 煞{l.getDaySha()}"
    except Exception as e:
        log(f"黄历封面：lunar 数据提取失败 {e}")
        return None

    # 季节植物元素 + 节气 icon（按月份粗粒度）
    if month in (3, 4, 5):
        botanical = "willow branches drooping upper-left, Paulownia tung-flower petals scattered"
        season_icon = "small green leaf"
    elif month in (6, 7, 8):
        botanical = "lotus pond ripples, bamboo shadows, cicada silhouettes"
        season_icon = "small bamboo leaf"
    elif month in (9, 10, 11):
        botanical = "maple leaves, ripe rice stalks, persimmons"
        season_icon = "small maple leaf"
    else:
        botanical = "plum blossoms, bare branches, light snow"
        season_icon = "small plum blossom"

    # Pantone 节气色卡（精准到当期节气）+ 主题底部注脚
    pantone = _get_pantone_for_date(year, month, day)
    p_hex, p_code, p_name = pantone["hex"], pantone["code"], pantone["name"]
    bottom_note = _get_bottom_note(topic, script)

    # ★ footer 指令前置（最关键的渲染要求放最前面，避免被后续大段 prompt 淹没）
    prompt = (
        'A 3:4 vertical Chinese ink-wash watercolor almanac cover, Kinfolk editorial aesthetic. '
        f'★★★ ABSOLUTE CRITICAL — render this first and never omit: At the very BOTTOM CENTER of the cover (within the bottom 10% of the frame), there MUST be a clearly visible warm sepia-brown Chinese brush calligraphy line "{bottom_note}" (about 4-5% of frame height, small but readable). Flank this calligraphy with two small painted red seal-stamp dots, one on the LEFT and one on the RIGHT of the text. This bottom calligraphy line is the MOST IMPORTANT element of the cover — without it the cover is rejected and unusable. ★★★ '
        f'Background: cream #F7EFD6 fading to pale sage. Botanical: {botanical}. '
        'Illustration (middle 45%): ink-wash of a wooden desk with an unrolled bamboo scroll, a Chinese calligraphy brush laid across, a small red seal stamp, glowing warm light, soft Jiangnan atmosphere. '
        'At the very top edge of the frame, HORIZONTALLY CENTERED (pill at exactly 50% frame width, NOT top-left, NOT offset): a single dark-charcoal iPhone Dynamic Island pill (solid dark fill) with white Chinese text "中华万年历" + a tiny ' + season_icon + ' icon. '
        f'Top-right corner: a PANTONE-style color swatch chip (compact rectangular card, thin cream border) — upper 60% solid color block {p_hex}; lower 40% cream strip with 3 small lines "PANTONE" / "{p_code}" / "{p_name}", side percentages "12%" "70%" "30%". '
        f'Center (rows 2-3, 85% width): a 2x2 title grid — top-left "{gz_2[0]}", top-right "{gz_2[1]}", bottom-left "宜", bottom-right "忌". Each character ONCE. Heavy-bold Chinese Song-ti serif, deep ink, soft cream outline. '
        f'Directly below: a small cream pill containing "{month}月{day}日 · {lunar_month_zh}{lunar_day_zh} · {gz_2}" in bold dark sepia-brown Chinese characters. '
        f'Below that: three compact info strips — sage-green "宜 {yi_str}"; muted-red #8B3A3A "忌 {ji_str}"; charcoal "{chong_sha}". '
        '★ Critical Chinese character distinction: 巳 has fully closed top loop, 己 has open top-left notch. 戊 simple slash, 戌 extra dot inside, 戍 short diagonal. 甲 extends bottom, 由 extends top, 申 extends both. 壬 has short top bar, 王 has three equal strokes. Each title character must be unique. '
        'Strict single-instance rule: every Chinese title/subtitle/strip appears EXACTLY ONCE — never duplicate or echo. Every Chinese character sharp and complete. 8% safe margin. No watermarks. High detail editorial. '
        '★★★ FINAL REMINDER: do not forget the BOTTOM CALLIGRAPHY LINE described at the very top of this prompt — it is mandatory. ★★★'
    )
    if len(prompt) > 1900:
        prompt = prompt[:1900]
    log(f"黄历封面：触发日报专用模板 ({date_str} · {gz_str}) · batch_4 + 坐标 prompt")

    # 🚀 真 batch_4：4 个独立 submit（错峰 + 3 次重试，确保穿越 SSL 抖动）
    _m, _ar, _extra = pick_image_model("3:4")
    def _submit_one(idx):
        time.sleep(idx * 1.5)  # 错峰 0/1.5/3/4.5s 避免并发 burst 撞 SSL
        for attempt in range(3):
            try:
                r = submit_text_to_image({
                    "model": _m,
                    "prompt": prompt,
                    "aspect_ratio": _ar,
                    "image_number": 1,
                    **_extra,
                }, f"黄历封面候选 {idx+1}", timeout=30, max_attempts=3)
                d = r.get("data", {})
                tid = d.get("task_id") or (d.get("task_ids") or [None])[0]
                if tid:
                    return tid
            except Exception as e:
                log(f"黄历封面 submit_{idx} 第 {attempt+1}/3 次失败: {type(e).__name__}")
            if attempt < 2:
                time.sleep(3 * (attempt + 1))
        return None
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=4) as ex:
        task_ids = list(ex.map(_submit_one, range(4)))
    task_ids = [t for t in task_ids if t]
    if not task_ids:
        log(f"黄历封面 4 个 submit 全失败")
        return None
    log(f"黄历封面 真 batch_4：4 个独立 submit 拿到 {len(task_ids)} 个 task_ids: {task_ids}")

    # 并发 poll + 下载 4 张候选
    from concurrent.futures import ThreadPoolExecutor
    def _poll_one(idx_tid):
        idx, tid = idx_tid
        cand_path = str(OUTPUT_DIR / f"cover_cand_{idx}.jpg")
        for _ in range(36):
            time.sleep(5)
            try:
                s = req_get(f"/generation/{tid}/status")
            except Exception:
                continue
            st = s.get("data", {}).get("task_status", "")
            if st == "succeed":
                imgs = s.get("data", {}).get("images") or []
                if not imgs:
                    return None
                try:
                    urllib.request.urlretrieve(imgs[0], cand_path)
                    from PIL import Image
                    Image.open(cand_path).convert("RGB").save(cand_path, "JPEG", quality=92, optimize=True)
                    return cand_path
                except Exception:
                    return None
            if st == "failed":
                return None
        return None

    with ThreadPoolExecutor(max_workers=4) as ex:
        candidates = list(ex.map(_poll_one, list(enumerate(task_ids))))
    candidates = [c for c in candidates if c]
    log(f"黄历封面 batch 得到 {len(candidates)}/{len(task_ids)} 张候选")
    if not candidates:
        return None

    # v0.3 双维度质检：先扫描 4 张候选的 unique + has_footer，按优先级挑
    cover_path = str(OUTPUT_DIR / "cover.jpg")
    import shutil
    cand_quality = []  # [(idx, cand_path, unique, has_footer)]
    for i, cand in enumerate(candidates):
        q = _llm_check_cover_quality(cand, expected_footer=bottom_note)
        cand_quality.append((i, cand, q["unique"], q["has_footer"]))

    # 优先级：unique + has_footer > unique > has_footer > 任何
    chosen = None
    for tier, label in [
        (lambda u, f: u and f, "unique + has_footer"),
        (lambda u, f: u, "unique only"),
        (lambda u, f: f, "has_footer only"),
        (lambda u, f: True, "fallback"),
    ]:
        for i, cand, u, f in cand_quality:
            if tier(u, f):
                chosen = cand
                log(f"黄历封面：候选 {i+1}/{len(candidates)} 通过 [{label}] 检测，采用")
                if label == "fallback":
                    tg(f"⚠️ 封面候选全部不达标，用第 {i+1} 张兜底（人工审视）")
                break
        if chosen:
            break

    shutil.copy(chosen, cover_path)
    # 清理候选（保留最终 cover.jpg）
    for cand in candidates:
        if cand != chosen:
            try: os.remove(cand)
            except: pass
    if chosen != cover_path:
        try: os.remove(chosen)
        except: pass
    return cover_path


COVER_LAST_REASON = ""


def _generate_cover_image(topic: str, short_title: str, script: list[dict]) -> str | None:
    """
    按 tone + 制片人准则生成专用封面图。
    不再写死红金大字报；儿童/科普/历史按各自视觉语言走。
    杂志封面级：先 AI 出底图（严格留出叠字干净区），再 Pillow 叠中文大字标题（TIME/BBC/儿童杂志三套模板）。
    返回本地 jpg 路径，失败返回 None。
    """
    global COVER_LAST_REASON
    COVER_LAST_REASON = ""
    cover_started = time.time()

    # ★ 黄历日报专用模板短路（含"黄历/万年历/宜忌" + 日期时自动走季节 Kinfolk 模板）
    almanac_cover = _try_almanac_cover(topic, script)
    if almanac_cover:
        return almanac_cover

    # 万年历视频号统一 3:4 + Kinfolk Pantone 时令封面结构（所有非 1919 题材共用，不再按 tone 分支）
    aspect = "3:4"
    tone = script[0].get("tone", "中性") if script else "中性"
    producer_brief = script[0].get("historical_context", "") if script else ""
    producer_block = f"【制片人准则（请重点参考其 STYLE_KEY / PALETTE / THUMBNAIL_ANCHOR 字段）】\n{producer_brief}\n\n" if producer_brief else ""

    # 通用变量：节气植物 / Pantone 色卡 / 日期 pill / 底部毛笔注脚
    _now = datetime.now()
    _m = _now.month
    if _m in (3, 4, 5):
        _botanical_hint = "willow branches, Paulownia tung-flower petals, early butterflies, young green leaves"
    elif _m in (6, 7, 8):
        _botanical_hint = "lotus pond ripples, cicada silhouettes, bamboo shadows, summer afternoon light"
    elif _m in (9, 10, 11):
        _botanical_hint = "maple leaves, ripe rice stalks, persimmons, autumn haze"
    else:
        _botanical_hint = "plum blossoms, bare branches, light snow, misty mountain"

    _pm = re.search(r'(\d{4})\D*(\d{1,2})\D*(\d{1,2})', topic)
    if _pm:
        _py, _pmo, _pd = int(_pm.group(1)), int(_pm.group(2)), int(_pm.group(3))
    else:
        _py, _pmo, _pd = _now.year, _now.month, _now.day
    # tone 优先：庄重 / 怀旧 用调性专属深色，避免节气色卡（如谷雨嫩芽绿）与悲剧题材冲突
    _pantone = _TONE_PANTONE_OVERRIDE.get(tone) or _get_pantone_for_date(_py, _pmo, _pd)
    _p_hex, _p_code, _p_name = _pantone["hex"], _pantone["code"], _pantone["name"]
    _bottom_note = _get_bottom_note(topic, script)
    _date_tag = _get_date_tag(topic) or ""

    # tone → 插画视觉调性映射（让 LLM 写匹配情绪的插画 + 也写进 Python 硬拼 prompt）
    _tone_aesthetic = {
        "庄重": "mournful and somber, low-key dark sepia ink-wash, restrained composition with negative space, gravitas",
        "怀旧": "warm aged sepia tone, vintage paper texture, sentimental tender atmosphere",
        "轻松": "bright pastel ink-wash, gentle hopeful palette, airy composition",
        "中性": "contemplative kinfolk editorial, balanced soft tones",
    }.get(tone, "contemplative kinfolk editorial, balanced soft tones")

    if ADS_DIALOGUE_MODE:
        dialogue_hint = " / ".join(
            f"{s.get('speaker','角色')}:{s.get('text','')[:18]}"
            for s in (script or [])[:4]
        )
        date_exact = f"{_py}年{_pmo}月{_pd}日" if _pm else (_date_tag or "")
        subtitle_rule = (
            f'Directly below main title: a small cream rounded pill with exact subtitle "{date_exact}" — '
            f'use Arabic digits exactly, never convert to Chinese numerals.'
        ) if date_exact else "Directly below main title: a small cream rounded pill with a short factual subtitle, exactly once."
        pov_cover = (
            "Composition feels like an onsite observer standing just inside the scene, with foreground document edge or doorway framing. "
            if ADSD_ONSITE_POV_MODE else ""
        )
        cover_prompt = (
            f'3:4 vertical Chinese historical dialogue-drama cover for a video account, fully model-rendered typography. '
            f'{_tone_aesthetic}. One to four historical onsite characters from the actual topic era appear according to the script structure; active discussion or solemn testimony, side profiles or three-quarter views, no mouth-closeup lip-sync pressure. '
            f'{pov_cover}Background: historically accurate location, period documents and objects directly tied to the topic, sepia ink-wash watercolor mixed with historical realism. '
            f'Top edge centered: dark-charcoal rounded pill with white Chinese "中华万年历". '
            f'Top-right: compact PANTONE swatch, English/Pantone only. '
            f'Center upper-middle: main title "{short_title}" in heavy-bold Chinese Song-ti serif, deep ink with cream outline, exactly once. '
            f'{subtitle_rule} '
            f'Bottom center: small warm sepia brush note "{_bottom_note}" flanked by two red seal dots, exactly once. '
            f'Dialogue clue in illustration: onsite character or characters clearly appear to be discussing or testifying about period documents or objects; visual anchor from script: {dialogue_hint}. '
            f'Strict text rule: render only these Chinese text blocks, no random signs, no duplicated title, no mirrored text, no extra subtitles in the illustration. '
            f'Every Chinese character sharp and complete, 8% safe margin, no watermark.'
        )
        log(f"ADSD 对话版封面 prompt 由 Python 硬拼完成（长度 {len(cover_prompt)} 字符）")
        if len(cover_prompt) > 1900:
            cut = cover_prompt[:1900]
            for sep in (". ", ", ", " and "):
                idx = cut.rfind(sep)
                if idx > 1900 * 0.7:
                    cut = cut[:idx + 1]
                    break
            cover_prompt = cut.rstrip() + ' No watermarks. Every Chinese character sharp and complete.'
            log(f"ADSD 封面 prompt 超长已截断：{len(cover_prompt)} 字符")
    elif is_1919_global_topic(topic):
        cover_prompt = build_1919_global_cover_prompt(short_title)
        log(f"1919 万年历结构专用封面 prompt 由 Python 硬拼完成，长度 {len(cover_prompt)} 字符")
    else:
        # LLM 只给插画描述（ILLUSTRATION + BOTANICAL），结构其余部分 100% 由 Python 硬锁
        first_line = script[0]["text"] if script else ""
        try:
            _raw_ill = chat(
                "GEMINI_25_FLASH",
                "你是中国水墨插画师，只按严格格式输出两行。",
                (
                    f"为短视频封面插画场景写英文描述。\n"
                    f"主题：{topic}\n"
                    f"基调：{tone}（视觉调性：{_tone_aesthetic}）\n"
                    f"短标题：{short_title}\n"
                    f"台词首句：{first_line}\n"
                    f"{producer_block}"
                    f"插画情绪必须严格匹配上述视觉调性，禁与基调冲突的色彩或元素。\n"
                    f"只输出两行，不加任何解释：\n"
                    f"ILLUSTRATION: <60-90 词英文插画场景描述，Kinfolk/ink-wash 风格，具体场景，匹配视觉调性，不要提主标题文字>\n"
                    f"BOTANICAL: <2-3 个英文植物名，逗号分隔，从这些挑 [{_botanical_hint}]>"
                ),
            )
            _illustration = "soft Chinese ink-wash watercolor scene"
            _botanical = _botanical_hint.split(",")[0].strip() if "," in _botanical_hint else _botanical_hint
            for _line in _raw_ill.strip().splitlines():
                _s = _line.lstrip("- *#•·>").strip()
                if _s.upper().startswith("ILLUSTRATION:") or _s.upper().startswith("ILLUSTRATION："):
                    _illustration = _s.split(":", 1)[-1].split("：", 1)[-1].strip() or _illustration
                elif _s.upper().startswith("BOTANICAL:") or _s.upper().startswith("BOTANICAL："):
                    _botanical = _s.split(":", 1)[-1].split("：", 1)[-1].strip() or _botanical
        except Exception as _e:
            log(f"Gemini 插画描述生成失败，用默认: {_e}")
            _illustration = "soft Chinese ink-wash watercolor scene reflecting the topic"
            _botanical = _botanical_hint.split(",")[0].strip() if "," in _botanical_hint else _botanical_hint

        cover_prompt = (
            f'A 3:4 vertical Chinese ink-wash watercolor magazine cover, Kinfolk editorial, {_tone_aesthetic}. '
            f'Background cream #F7EFD6 to pale sage bottom, {_botanical} scattered. '
            f'Illustration (middle 50%): {_illustration}. '
            f'At the top edge HORIZONTALLY CENTERED (pill at exactly 50% frame width, NOT top-left): a single dark-charcoal iPhone Dynamic Island pill (solid dark fill, small horizontal pill shape) with white Chinese "中华万年历" + green-leaf icon. '
            f'Top-right: a PANTONE swatch chip (compact rectangular card, thin cream border) — upper 60% color block {_p_hex}, lower 40% cream strip with 3 small lines "PANTONE" / "{_p_code}" / "{_p_name}", side percentages "12%" "70%" "30%". '
            f'Center (row 5, 85% width): main title "{short_title}" in heavy-bold Chinese Song-ti serif #1A1A1A with cream outline — render exactly once here, never anywhere else. '
            f'Directly below main title: a small cream pill with "{_date_tag}" in bold dark sepia-brown Chinese characters — once only. '
            f'Very bottom center: SMALL (2.8% frame height, smaller than subtitle), flanked by two small red seal dots (one LEFT, one RIGHT) as decoration, hand-drawn in warm sepia-brown tone "{_bottom_note}" in semi-cursive brushstroke. '
            f'Strict rule: each Chinese title/subtitle/tagline appears exactly once, never mirrored or echoed in illustration or scrolls. '
            f'Every Chinese character sharp and complete, 8% safe margin. '
            f'No R1/R2/REGION labels. English and percentages only inside Pantone card. No watermarks.'
        )
        log(f"万年历统一封面 prompt 由 Python 硬拼完成（tone={tone}，长度 {len(cover_prompt)} 字符）")
        if len(cover_prompt) > 1900:
            cut = cover_prompt[:1900]
            for sep in (". ", ", ", " and "):
                idx = cut.rfind(sep)
                if idx > 1900 * 0.7:
                    cut = cut[:idx + 1]
                    break
            cover_prompt = cut.rstrip() + ' No watermarks. Every Chinese character sharp and complete.'
            log(f"万年历封面 prompt 超长已截断：{len(cover_prompt)} 字符")

    # 调 WeryAI text-to-image
    try:
        _m, _ar, _extra = pick_image_model(aspect)
        _wait_image_submit_slot("封面")
        resp = req_post(
            "/generation/text-to-image",
            {
                "model": _m,
                "prompt": cover_prompt,
                "aspect_ratio": _ar,
                "image_number": 1,
                **_extra,
            },
            timeout=30,
        )
        data = resp.get("data", {})
        task_id = data.get("task_id") or (data.get("task_ids") or [None])[0]
        if not task_id:
            log(f"封面任务提交失败: {resp}")
            COVER_LAST_REASON = "submit_failed"
            return None
        log(f"封面任务已提交 task_id={task_id}")
    except Exception as e:
        log(f"封面 API 提交失败: {e}")
        COVER_LAST_REASON = "submit_failed"
        return None

    # 封面图常比正片慢，实测可超过 220s；默认最多等 10 分钟，避免误判失败。
    cover_timeout = int(os.environ.get("ADR_COVER_TIMEOUT", "600"))
    poll_interval = 5
    polls = max(1, cover_timeout // poll_interval)
    last_status_log = 0.0
    for poll_i in range(polls):
        time.sleep(poll_interval)
        elapsed = time.time() - cover_started
        try:
            s = req_get(f"/generation/{task_id}/status")
        except Exception as e:
            if elapsed - last_status_log >= 30:
                log(f"封面轮询异常，已等待 {elapsed:.1f}s: {e}")
                last_status_log = elapsed
            continue
        st = s.get("data", {}).get("task_status", "")
        if elapsed - last_status_log >= 30:
            log(f"封面生成中：poll {poll_i+1}/{polls}, status={st or 'unknown'}, elapsed={elapsed:.1f}s")
            last_status_log = elapsed
        if st == "succeed":
            imgs = s.get("data", {}).get("images") or []
            if not imgs:
                COVER_LAST_REASON = "no_image"
                return None
            cover_path = str(OUTPUT_DIR / "cover.jpg")
            try:
                urllib.request.urlretrieve(imgs[0], cover_path)
            except Exception as e:
                log(f"封面下载失败: {e}")
                COVER_LAST_REASON = "download_failed"
                return None
            # 转真 JPG（weryai 默认 PNG；WeChat CDN 对大 PNG 上传差）
            try:
                from PIL import Image
                Image.open(cover_path).convert("RGB").save(
                    cover_path, "JPEG", quality=92, optimize=True
                )
            except Exception:
                pass
            # 默认信任 Nano Banana 2 直出的中文标题。
            # 兜底：环境变量 ADR_COVER_FORCE_PILLOW=1 时强制走 Pillow 叠字覆盖 AI 输出
            if os.environ.get("ADR_COVER_FORCE_PILLOW") == "1":
                try:
                    cover_path = _overlay_title_on_cover(cover_path, short_title, tone)
                    log("封面走 Pillow 叠字兜底（ADR_COVER_FORCE_PILLOW=1）")
                except Exception as e:
                    log(f"封面 Pillow 兜底失败（不致命，发送 AI 直出版）: {e}")
            log(f"封面生成成功，耗时 {time.time() - cover_started:.1f}s → {cover_path}")
            return cover_path
        if st == "failed":
            log(f"封面生成 failed: {s}")
            COVER_LAST_REASON = "failed"
            return None
    COVER_LAST_REASON = "timeout"
    log(f"封面轮询超时（{cover_timeout}s），task_id={task_id} 可能仍在后台继续生成")
    return None


# ── 异步封面 + caption（与 step6-9 并发）────────────────────────────────
# 默认 ~3 min 的封面生成原本卡在 step10 最后串行，改成 step1 完成后立即 kickoff，
# 跟 step6 storyboard / step66 lip-sync / step7-9 拼接合成并发跑。
_ASYNC_COVER_LOCK = threading.Lock()
_ASYNC_COVER_RESULT: dict = {"started": False, "done": False}


def _async_kickoff_cover_caption(topic: str, script: list[dict]) -> None:
    """step1 完成后立即调用。在后台线程内顺序跑 caption LLM + 封面图生成。
    step10_deliver 时 _await_async_cover_caption() 取结果，省去串行 200+s 等封面。"""
    def _worker():
        try:
            caption, short_title, hashtags = _generate_caption(topic, script)
            with _ASYNC_COVER_LOCK:
                _ASYNC_COVER_RESULT["caption"] = caption
                _ASYNC_COVER_RESULT["short_title"] = short_title
                _ASYNC_COVER_RESULT["hashtags"] = hashtags
                _ASYNC_COVER_RESULT["caption_done_ts"] = time.time()
            cover_path = _generate_cover_image(topic, short_title, script)
            with _ASYNC_COVER_LOCK:
                _ASYNC_COVER_RESULT["cover_path"] = cover_path
                _ASYNC_COVER_RESULT["done"] = True
                _ASYNC_COVER_RESULT["cover_done_ts"] = time.time()
        except Exception as e:
            with _ASYNC_COVER_LOCK:
                _ASYNC_COVER_RESULT["error"] = str(e)
                _ASYNC_COVER_RESULT["done"] = True
            log(f"异步封面+caption worker 异常: {type(e).__name__}: {e}")
    with _ASYNC_COVER_LOCK:
        if _ASYNC_COVER_RESULT.get("started"):
            return
        _ASYNC_COVER_RESULT["started"] = True
        _ASYNC_COVER_RESULT["started_ts"] = time.time()
    threading.Thread(target=_worker, daemon=True).start()
    log("异步封面+caption worker 已 kick off（与 step6-9 并发）")


def _await_async_cover_caption(timeout_seconds: float = 600.0) -> tuple | None:
    """阻塞等异步 worker 完成。返回 (caption, short_title, hashtags, cover_path) 或 None。"""
    with _ASYNC_COVER_LOCK:
        if not _ASYNC_COVER_RESULT.get("started"):
            return None
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        with _ASYNC_COVER_LOCK:
            if _ASYNC_COVER_RESULT.get("done"):
                started_ts = _ASYNC_COVER_RESULT.get("started_ts", 0)
                cover_ts = _ASYNC_COVER_RESULT.get("cover_done_ts", 0)
                if started_ts and cover_ts:
                    log(f"step10 复用异步 worker 结果（封面耗时 {cover_ts - started_ts:.1f}s 已与主流程并发）")
                return (
                    _ASYNC_COVER_RESULT.get("caption"),
                    _ASYNC_COVER_RESULT.get("short_title"),
                    _ASYNC_COVER_RESULT.get("hashtags"),
                    _ASYNC_COVER_RESULT.get("cover_path"),
                )
        time.sleep(1)
    log("step10 等异步 worker 超时，回退内联生成")
    return None


def step10_deliver(final_path: str, topic: str, script: list[dict]):
    if NO_VOICE:
        bgm_qa = _write_bgm_only_qa(final_path, script)
        hard_block = os.environ.get("ADR_ADSD_QA_HARD_BLOCK", "0").strip().lower() in ("1", "true", "yes", "on")
        if not bgm_qa.get("pass"):
            issues = "\n".join(f"• {x}" for x in bgm_qa.get("issues", [])[:8])
            if hard_block:
                tg(
                    "🛑 ADR/ADS BGM-only 发布已阻断（ADR_ADSD_QA_HARD_BLOCK=1）：QA 未通过\n\n"
                    f"{issues}\n\n"
                    f"成片保留在本地：{final_path}\n"
                    f"QA：{OUTPUT_DIR / 'bgm_only_qa.json'}"
                )
                log(f"BGM-only QA hard-blocked: {bgm_qa.get('issues')}")
                return
            else:
                tg(
                    "⚠️ ADR/ADS BGM-only QA 未通过（继续推送，仅作提醒）：\n\n"
                    f"{issues}\n\n"
                    f"详细 QA：{OUTPUT_DIR / 'bgm_only_qa.json'}"
                )
                log(f"BGM-only QA warning (not blocked): {bgm_qa.get('issues')}")
        else:
            warn_lines = "\n".join(f"• {x}" for x in bgm_qa.get("warnings", [])[:5])
            warn_note = f"\n\n提示：\n{warn_lines}" if warn_lines else ""
            tg(f"✅ ADR/ADS BGM-only 发布门禁通过：BGM 音轨/时长/字幕节奏 QA OK{warn_note}")

    if ADS_DIALOGUE_MODE:
        delivery_qa = _write_adsd_delivery_qa(final_path)
        # QA 改为"提醒"而非"阻断" — 大哥要求继续推送即使 QA 不全过，问题以警告呈现
        # 需要重新启用阻断时 set ADR_ADSD_QA_HARD_BLOCK=1
        hard_block = os.environ.get("ADR_ADSD_QA_HARD_BLOCK", "0").strip().lower() in ("1", "true", "yes", "on")
        if delivery_qa and not delivery_qa.get("pass"):
            issues = "\n".join(f"• {x}" for x in delivery_qa.get("issues", [])[:8])
            if hard_block:
                tg(
                    f"🛑 {ADSD_MODE_NAME} 发布已阻断（ADR_ADSD_QA_HARD_BLOCK=1）：QA 未通过\n\n"
                    f"{issues}\n\n"
                    f"成片保留在本地：{final_path}\n"
                    f"QA：{OUTPUT_DIR / 'delivery_qa.json'}"
                )
                log(f"{ADSD_MODE_NAME} delivery QA hard-blocked: {delivery_qa.get('issues')}")
                return
            else:
                tg(
                    f"⚠️ {ADSD_MODE_NAME} QA 未全通过（继续推送，仅作提醒）：\n\n"
                    f"{issues}\n\n"
                    f"详细 QA：{OUTPUT_DIR / 'delivery_qa.json'}"
                )
                log(f"{ADSD_MODE_NAME} delivery QA warning (not blocked): {delivery_qa.get('issues')}")
        elif delivery_qa:
            warn_lines = "\n".join(f"• {x}" for x in delivery_qa.get("warnings", [])[:5])
            warn_note = f"\n\n提示：\n{warn_lines}" if warn_lines else ""
            tg(f"✅ {ADSD_MODE_NAME} 发布门禁通过：字幕/口型/音画同步 QA OK{warn_note}")

    # 优先取异步 worker 结果（与 step6-9 并发已跑完）；不可用则现场生成
    _async = _await_async_cover_caption(timeout_seconds=600)
    _async_cover_path = None
    if _async:
        caption, short_title, hashtags, _async_cover_path = _async
    else:
        caption, short_title, hashtags = _generate_caption(topic, script)
    tg(f"📝 社媒文案 + 短标题 + 热门标签已生成\n\n📤 正在发送...")

    # 1. 短标题（一键复制）
    try:
        requests.post(
            f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage",
            json={
                "chat_id": TG_CHAT_ID,
                "text": f"🏷 短标题：{short_title}",
                "reply_markup": {
                    "inline_keyboard": [[{
                        "text": "📋 复制短标题",
                        "copy_text": {"text": short_title},
                    }]]
                },
            },
            timeout=(10, 15),
        )
    except Exception as e:
        log(f"短标题发送失败: {e}")

    # 2. 社媒文案主体（一键复制按钮；Telegram copy_text 上限 256 字符，长文案智能拆分）
    try:
        if len(caption) <= 256:
            # 短文案：完整加复制按钮
            requests.post(
                f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage",
                json={
                    "chat_id": TG_CHAT_ID,
                    "text": f"📋 社媒文案主体（点按钮一键复制；标签见下一条）：\n\n{caption}",
                    "reply_markup": {
                        "inline_keyboard": [[{
                            "text": "📋 复制文案",
                            "copy_text": {"text": caption},
                        }]]
                    },
                },
                timeout=(10, 15),
            )
        else:
            # 长文案 > 256：先发完整文案（消息正文，长按可复制全部），再发短切片版按钮
            requests.post(
                f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage",
                json={
                    "chat_id": TG_CHAT_ID,
                    "text": f"📋 社媒文案主体（长按消息整段复制；按钮限 256 字内片段）：\n\n{caption}",
                },
                timeout=(10, 15),
            )
            # 拆成 ≤256 字片段，每段带复制按钮
            chunks = []
            buf = ""
            for line in caption.split("\n"):
                if len(buf) + len(line) + 1 > 256:
                    if buf:
                        chunks.append(buf)
                    # 单行也可能超 256 → 强制按字符切
                    while len(line) > 256:
                        chunks.append(line[:256])
                        line = line[256:]
                    buf = line
                else:
                    buf = (buf + "\n" + line) if buf else line
            if buf:
                chunks.append(buf)
            for i, chunk in enumerate(chunks):
                try:
                    requests.post(
                        f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage",
                        json={
                            "chat_id": TG_CHAT_ID,
                            "text": f"📋 文案片段 {i+1}/{len(chunks)}（点按钮复制此段）：\n\n{chunk}",
                            "reply_markup": {
                                "inline_keyboard": [[{
                                    "text": f"📋 复制片段 {i+1}",
                                    "copy_text": {"text": chunk},
                                }]]
                            },
                        },
                        timeout=(10, 15),
                    )
                except Exception:
                    pass
    except Exception as e:
        log(f"社媒文案发送失败: {e}")

    # 2.5 热门标签串（独立一条带一键复制；方便直接粘到视频号发布框末尾）
    if hashtags:
        try:
            _tag_count = len(hashtags.split())
            requests.post(
                f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage",
                json={
                    "chat_id": TG_CHAT_ID,
                    "text": f"🏷 热门话题标签（{_tag_count} 个，可一键复制粘到发布框末尾）：\n\n{hashtags}",
                    "reply_markup": {
                        "inline_keyboard": [[{
                            "text": "📋 复制全部标签",
                            "copy_text": {"text": hashtags},
                        }]]
                    },
                },
                timeout=(10, 15),
            )
        except Exception as e:
            log(f"热门标签发送失败: {e}")

    # 3. 专用封面图：按 tone 切受众与风格
    _tone = script[0].get("tone", "中性") if script else "中性"
    _style_tag = {
        "轻松": "明亮卡通 · 家长/学生/年轻用户友好",
        "庄重": "红金大字报 · 历史/警示向设计",
        "中性": "信息图风 · 泛知识用户友好",
    }.get(_tone, "主题专属封面")
    if _async_cover_path:
        tg(f"🎨 主题专属封面已就绪（{_style_tag}） — 异步预生成 ✓")
        cover_path = _async_cover_path
    else:
        tg(f"🎨 正在生成主题专属封面（{_style_tag}）...")
        cover_path = _generate_cover_image(topic, short_title, script)

    def _upload_cover_photo(send_path: str, caption: str) -> dict:
        """单次 sendPhoto 调用，包成 _tg_upload_with_probe_gap 期望的 result 格式。"""
        def _do_post() -> dict:
            try:
                with open(send_path, "rb") as img_f:
                    rp = requests.post(
                        f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendPhoto",
                        data={"chat_id": TG_CHAT_ID, "caption": caption},
                        files={"photo": img_f},
                        timeout=30,
                    )
                if rp.status_code == 200:
                    return {"ok": True, "message_id": rp.json().get("result", {}).get("message_id")}
                return {"ok": False, "exception": RuntimeError(f"sendPhoto HTTP {rp.status_code}")}
            except Exception as e:
                return {"ok": False, "exception": e}
        return _tg_upload_with_probe_gap(_do_post, probe_label_prefix="cover", max_attempts=2)

    if cover_path:
        cover_send_path = _prepare_tg_photo(cover_path)
        cover_caption = (
            f"🖼 专属封面（建议叠标题：{short_title}）\n"
            f"{_style_tag}"
        )
        cover_result = _upload_cover_photo(cover_send_path, cover_caption)
        if not cover_result.get("ok"):
            log(f"专属封面发送失败 attempts={cover_result.get('attempts')}: {cover_result.get('last_exception')}")
        elif cover_result.get("source") == "probe_gap_detected":
            log("专属封面 SSL 假阴性识别成功，跳过重复推送")
    else:
        # 封面兜底：只有接口明确 failed 才叫失败；timeout 只是后台未及时完成。
        if COVER_LAST_REASON == "timeout":
            tg("⚠️ 专属封面仍在生成但已超过等待上限，先使用首张分镜图兜底；封面任务可能稍后在后台完成")
        else:
            tg(f"⚠️ 专属封面生成未完成（reason={COVER_LAST_REASON or 'unknown'}），使用首张分镜图兜底")
        fallback = str(OUTPUT_DIR / "img_0.jpg")
        try:
            fallback_send_path = _prepare_tg_photo(fallback)
            fb_result = _upload_cover_photo(fallback_send_path, "🖼 封面（兜底 · 首张分镜）")
            if not fb_result.get("ok"):
                log(f"兜底封面发送失败: {fb_result.get('last_exception')}")
        except Exception as e:
            log(f"兜底封面准备失败: {e}")

    # 4. 上传视频（先 requests，失败 fallback curl）
    # ★ 自动压缩兜底：Telegram Bot API sendVideo 限 50MB；超 48MB 自动 ffmpeg 重编码一份 lite 版
    try:
        _size_mb = os.path.getsize(final_path) / (1024 * 1024)
        if _size_mb > 48:
            tg(f"🗜 成片 {_size_mb:.1f}MB 超 Telegram 50MB 上限，自动压缩（crf 28 + slow preset）...")
            _lite_path = final_path.rsplit(".", 1)[0] + "_lite.mp4"
            ffmpeg(
                "-i", final_path,
                "-c:v", "libx264", "-crf", "28", "-preset", "slow",
                "-c:a", "aac", "-b:a", "96k",
                "-movflags", "+faststart",
                _lite_path,
            )
            _new_size = os.path.getsize(_lite_path) / (1024 * 1024)
            log(f"成片压缩完成：{_size_mb:.1f}MB → {_new_size:.1f}MB")
            tg(f"✅ 压缩完成：{_size_mb:.1f}MB → {_new_size:.1f}MB")
            if _new_size > 48:
                tg(f"⚠️ 压缩后仍超限（{_new_size:.1f}MB），Telegram 可能仍 413；继续尝试上传")
            final_path = _lite_path
    except Exception as e:
        log(f"自动压缩兜底失败，用原片尝试上传: {e}")

    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendVideo"
    delivery_tag = ADSD_MODE_NAME if ADS_DIALOGUE_MODE else "ADR V8"
    short_caption = f"{short_title} — {delivery_tag}"
    video_ok = False

    # ── SSL 假阴性防护：见模块级 _tg_probe_send / _tg_probe_delete ──
    # 局部 alias，保留原变量名以最小化 diff
    _send_probe = _tg_probe_send
    _delete_probe = _tg_probe_delete

    # ── 尝试 1：requests（timeout 放大到 600s），前后 probe 跳号检测 ──
    probe_before = _send_probe("up-start")
    for attempt in range(2):
        try:
            with open(final_path, "rb") as f:
                r = requests.post(url, data={
                    "chat_id":           TG_CHAT_ID,
                    "caption":           short_caption,
                    "supports_streaming": "true",
                    "width":             str(VIDEO_W),
                    "height":            str(VIDEO_H),
                }, files={"video": (os.path.basename(final_path), f, "video/mp4")}, timeout=(30, 600))
            if r.status_code == 200:
                video_ok = True
                break
            else:
                log(f"requests 上传失败（{r.status_code}），第 {attempt+1} 次")
        except Exception as e:
            log(f"requests 上传异常（第 {attempt+1} 次）：{type(e).__name__}: {e}")
            # 关键：客户端 SSL 异常 ≠ 服务器端失败。用 probe 跳号检测真实结果
            time.sleep(3)
            probe_after = _send_probe("up-check")
            if probe_before is not None and probe_after is not None:
                gap = probe_after - probe_before
                if gap >= 2:
                    log(f"probe 跳号检测：message_id 间隔 {gap} → 视频已落到 chat，本地 SSL 异常为假阴性，跳过重传")
                    tg("ℹ️ 上传已成功（SSL 假阴性已自动识别，避免重复推送）")
                    video_ok = True
                    _delete_probe(probe_after)
                    _delete_probe(probe_before)
                    break
                else:
                    log(f"probe 跳号检测：间隔 {gap} → 视频未到 chat，准备重传")
                    _delete_probe(probe_after)
                    # 重传前刷新 probe_before 为最后一次 probe
                    probe_before = _send_probe("up-retry")
            else:
                log("probe 跳号检测不可用（probe 发送失败），按原逻辑重试")
        if attempt < 1:
            time.sleep(5)
    _delete_probe(probe_before)

    # ── 尝试 2：curl fallback（更稳定，不受 httpx/urllib3 限制），同样跳号检测 ──
    if not video_ok:
        tg("⚠️ requests 上传未确认成功，切换 curl 重试...")
        for attempt in range(3):
            probe_before = _send_probe(f"curl-start-{attempt+1}")
            try:
                import subprocess as _sp
                curl_cmd = [
                    "curl", "-s", "-X", "POST", url,
                    "-F", f"chat_id={TG_CHAT_ID}",
                    "-F", f"caption={short_caption}",
                    "-F", "supports_streaming=true",
                    "-F", f"width={VIDEO_W}",
                    "-F", f"height={VIDEO_H}",
                    "-F", f"video=@{final_path}",
                    "--max-time", "600",
                    "--connect-timeout", "30",
                ]
                result = _sp.run(curl_cmd, capture_output=True, text=True, timeout=660)
                if result.returncode == 0 and '"ok":true' in result.stdout:
                    video_ok = True
                    log(f"curl 上传成功（第 {attempt+1} 次）")
                    _delete_probe(probe_before)
                    break
                else:
                    log(f"curl 上传失败（第 {attempt+1} 次），stdout: {result.stdout[:200]}")
                    # 跳号检测
                    time.sleep(3)
                    probe_after = _send_probe(f"curl-check-{attempt+1}")
                    if probe_before is not None and probe_after is not None:
                        gap = probe_after - probe_before
                        if gap >= 2:
                            log(f"curl probe 跳号检测：间隔 {gap} → 视频已落到 chat，跳过后续重传")
                            tg("ℹ️ 上传已成功（curl 阶段 SSL 假阴性自动识别）")
                            video_ok = True
                            _delete_probe(probe_after)
                            _delete_probe(probe_before)
                            break
                        else:
                            _delete_probe(probe_after)
            except Exception as e:
                log(f"curl 异常（第 {attempt+1} 次）：{type(e).__name__}: {e}")
            _delete_probe(probe_before)
            if attempt < 2:
                time.sleep(10)

    # ── 尝试 3：小土伯/TG 文件兜底。视频上传链路 SSL 抖动时，压 lite/micro 后用 sendDocument 发文件。 ──
    if (
        not video_ok
        and os.environ.get("ADR_TG_FILE_FALLBACK", "1").strip().lower() not in ("0", "false", "no", "off")
    ):
        tg("⚠️ sendVideo 未确认成功，启动小土伯文件兜底：lite/micro → sendDocument")
        fallback_profiles = [
            ("lite", "854:-2", "24", "30", "80k", "200k"),
            ("micro", "426:-2", "18", "38", "32k", "120k"),
        ]
        for label, scale, fps, crf, audio_br, limit_rate in fallback_profiles:
            fb_path = final_path.rsplit(".", 1)[0] + f"_tg_{label}.mp4"
            try:
                if not os.path.exists(fb_path) or os.path.getsize(fb_path) < 10000:
                    ffmpeg(
                        "-i", final_path,
                        "-vf", f"scale={scale},fps={fps}",
                        "-c:v", "libx264", "-crf", crf, "-preset", "veryfast",
                        "-c:a", "aac", "-b:a", audio_br,
                        "-movflags", "+faststart",
                        fb_path,
                        timeout=180,
                    )
                fb_size_mb = os.path.getsize(fb_path) / (1024 * 1024)
                log(f"TG fallback {label} ready: {fb_size_mb:.1f}MB -> {fb_path}")
            except Exception as e:
                log(f"TG fallback {label} 压缩失败: {e}")
                continue

            doc_url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendDocument"
            for attempt in range(2):
                probe_before = _send_probe(f"doc-{label}-start-{attempt+1}")
                try:
                    import subprocess as _sp
                    curl_cmd = [
                        "curl", "--ipv4", "--http1.1", "--tlsv1.2", "-sS",
                        "--connect-timeout", "30", "--max-time", "600",
                        "--limit-rate", limit_rate,
                        "-X", "POST", doc_url,
                        "-F", f"chat_id={TG_CHAT_ID}",
                        "-F", f"caption={short_caption} · TG {label} fallback",
                        "-F", f"document=@{fb_path}",
                    ]
                    result = _sp.run(curl_cmd, capture_output=True, text=True, timeout=660)
                    if result.returncode == 0 and '"ok":true' in result.stdout:
                        video_ok = True
                        log(f"TG sendDocument fallback 成功：{label} 第 {attempt+1} 次")
                        _delete_probe(probe_before)
                        break
                    log(f"TG sendDocument fallback 失败：{label} 第 {attempt+1} 次 rc={result.returncode} stdout={result.stdout[:160]} stderr={result.stderr[:160]}")
                    time.sleep(3)
                    probe_after = _send_probe(f"doc-{label}-check-{attempt+1}")
                    if probe_before is not None and probe_after is not None:
                        gap = probe_after - probe_before
                        if gap >= 2:
                            video_ok = True
                            log(f"TG sendDocument fallback probe 跳号：{label} 间隔 {gap} → 文件已落到 chat")
                            _delete_probe(probe_after)
                            _delete_probe(probe_before)
                            break
                        _delete_probe(probe_after)
                except Exception as e:
                    log(f"TG sendDocument fallback 异常：{label} 第 {attempt+1} 次 {type(e).__name__}: {e}")
                _delete_probe(probe_before)
                if attempt < 1:
                    time.sleep(6)
            if video_ok:
                tg(f"✅ TG 文件兜底成功：{label} 版已发送")
                break

    if video_ok:
        log("step10 deliver 完成：视频上传成功")
        tg("✅ 全流程完成！")
    else:
        log(f"step10 deliver 失败：视频上传全部失败，文件保留在 {final_path}")
        tg(f"❌ 视频上传全部失败（含跳号检测均未确认），文件在：{final_path}\n社媒文案已发送")


# ── 主流程 ───────────────────────────────────────────────────────────────────
def _print_execution_plan() -> None:
    """启动时打印本次 run 会激活哪些可选模块 + 预估时间/credits。
    目的：开 mode flag 时让"无消费方但仍激活的浪费"立刻可见，避免我（PM）忘记 short-circuit。"""
    fmt = "VDAR 9:16" if IS_VERTICAL else "HDAR 16:9"
    # (模块名, 是否激活, 预估时间 min, 预估 credits, 说明)
    plan: list[tuple[str, bool, str, str, str]] = [
        ("Step1 剧本+视觉规划", True, "1-2", "0", "LLM 链 (Gemini/Claude)"),
        ("Step2 text-to-audio 主音轨", not NO_VOICE and not ADS_DIALOGUE_MODE, "1-3", "~25", "主路径：text-to-audio per-line；失败降级 Podcast → OpenAI → Edge TTS"),
        ("Step2 BGM-only 静音轨", NO_VOICE, "0.1", "0", "ffmpeg 生成静音占位"),
        ("ADSD 逐句 text-to-audio", ADS_DIALOGUE_MODE, "2-3", "~25", "每 turn 一次 TTS"),
        ("Step6 character_sheet", CHARACTER_TRAILER_MODE or STORYBOARD_GRID_MULTIREF_MAIN or (ADS_DIALOGUE_MODE and ADSD_LIP_SYNC_EXPERIMENT) or (ADS_REPORTER_MODE and not ADS_DIALOGUE_MODE and ADS_CHARACTER_SHEET_REQUESTED), "2-3", "~60", "GPT Image 2 model sheet"),
        ("Step6 production_storyboard_page", True, "2-3", "~60", "GPT Image 2"),
        ("Step6 storyboard_grid", GPT_IMAGE2_STORYBOARD_GRID, "3-5", "~80", "GPT Image 2 多 panel 大图 + 切片"),
        ("Step6 per-scene 单图 (fallback)", not GPT_IMAGE2_STORYBOARD_GRID, "5-8", "~80", "weryai text-to-image 单张 × N"),
        ("Step6 motion_bridge_refs", MOTION_BRIDGE_REFS and not ADS_DIALOGUE_MODE and not STORYBOARD_TRAILER_MAIN, "3-5", "~60", "GPT Image 2 每镜转场参考"),
        ("BGM 主乐", not NO_VOICE, "0.5-3", "~5", "weryai 音乐生成 (LLM 自描述)"),
        ("Step65 per-scene motion", WITH_MOTION and not ADS_DIALOGUE_MODE, "10-30", "~180", "WERYDANCE × N，每镜 ~15 credits"),
        ("Step65 storyboard_trailer", STORYBOARD_TRAILER_MODE and not ADS_DIALOGUE_MODE, "7-15", "~105", "WERYDANCE 整张故事板 → trailer.mp4"),
        ("Step65 grid_multiref_motion", STORYBOARD_GRID_MULTIREF_MOTION and not ADS_DIALOGUE_MODE, "8-15", "~120", "实验性多参考切片"),
        ("Step65 previs_page_motion", PREVIS_PAGE_MOTION and not ADS_DIALOGUE_MODE, "5-10", "~80", "实验性 previs page"),
        ("Step65 character_trailer", CHARACTER_TRAILER_MODE, "10-15", "~150", "Character sheet + 干净参考 trailer"),
        ("Step66 ADSD lip-sync", ADS_DIALOGUE_MODE and ADSD_LIP_SYNC_EXPERIMENT, "10-20", "~150", "WERYDANCE × N turn"),
        ("Step7 视频拼接", True, "0.2-0.5", "0", "ffmpeg local"),
        ("Step8 字幕生成 (ASS)", not NO_VOICE or BGM_ONLY_REQUESTED, "0.5-1", "0", "LLM 断句 + ASS 生成"),
        ("Step9 最终合成", True, "0.5-1", "0", "ffmpeg 烧字幕 + 音轨"),
        ("Step10 推送 Telegram", True, "0.1-0.3", "0", "上传成片 + 封面"),
    ]
    active = [p for p in plan if p[1]]
    skipped = [p for p in plan if not p[1]]
    total_min_lo = sum(float(p[2].split("-")[0]) for p in active)
    total_min_hi = sum(float(p[2].split("-")[-1]) for p in active)
    total_credits = sum(int(p[3].replace("~", "").strip() or 0) for p in active)
    lines = ["", "═════ 本次 ADR 执行计划 ═════"]
    lines.append(f"画幅: {fmt}    主题: {TOPIC[:60]}{'...' if len(TOPIC) > 60 else ''}")
    lines.append(f"激活模块 {len(active)} 个 | 预估 {total_min_lo:.1f}-{total_min_hi:.1f} min | 预估 ~{total_credits} credits")
    lines.append("")
    for name, _on, t_est, c_est, desc in active:
        lines.append(f"  ✓ {name:<32} {t_est:>6} min  {c_est:>6} credits  -- {desc}")
    if skipped:
        lines.append("")
        lines.append("跳过的可选模块（标志位关闭）：")
        for name, _on, t_est, c_est, desc in skipped:
            lines.append(f"  · {name}")
    lines.append("════════════════════════════")
    for line in lines:
        log(line)


def main():
    topic = TOPIC
    log(f"开始处理：{topic}")
    log(f"输出目录：{OUTPUT_DIR}")
    _print_execution_plan()

    t_start = time.time()
    timings = {}

    try:
        t = time.time(); script, spk_id, spk_name = step1_script(topic);       timings["剧本+制片人准则+画面提示词+音色"] = time.time() - t
        # 异步 kickoff：caption LLM + 封面图（GPT Image 2 ~180s）跟 step6/66/7/8/9 并发跑
        _async_kickoff_cover_caption(topic, script)
        bgm_path = None
        if NO_VOICE:
            t = time.time()
            bgm_tone = script[0].get("tone", "中性") if script else "中性"
            bgm_path = generate_bgm(topic, bgm_tone)
            if not bgm_path:
                raise RuntimeError("ADR/ADS BGM-only 模式 BGM 生成失败，停止交付")
            timings["BGM-only BGM 生成"] = time.time() - t

            t = time.time()
            bgm_dur = ffprobe_duration(bgm_path)
            max_total = float(os.environ.get("ADR_BGM_ONLY_MAX_DURATION", "90"))
            est_dur = min(bgm_dur, max_total)
            voice_path = str(OUTPUT_DIR / "silent_voice.mp3")
            subprocess.run([
                "ffmpeg", "-y", "-f", "lavfi",
                "-i", f"anullsrc=channel_layout=mono:sample_rate=44100",
                "-t", f"{est_dur}",
                "-c:a", "libmp3lame", "-b:a", "64k",
                voice_path,
            ], capture_output=True, timeout=30, check=True)
            tg(f"🔇 ADR/ADS BGM-only：跳过旁白 TTS，生成 {est_dur:.1f}s 静音时间轴占位（最终音轨只保留 BGM）")
            timings["BGM-only 静音时间轴"] = time.time() - t
        else:
            if ADS_DIALOGUE_MODE:
                t = time.time(); voice_path = step2_dialogue_voice(script); timings["ADSD TTS 音轨+ASR"] = time.time() - t
            else:
                t = time.time(); voice_path = step2_master_voice(script, spk_id, spk_name); timings["Podcast 音轨"] = time.time() - t
        if NO_VOICE:
            t = time.time(); script = step345_bgm_only_timeline(script, bgm_path, voice_path); timings["BGM-driven 时间轴计算"] = time.time() - t
        else:
            t = time.time(); script = step345_timeline(script, voice_path);   timings["时间轴计算"] = time.time() - t
        t = time.time(); bgm_path   = step6_parallel(script, topic, bgm_path if NO_VOICE else None); timings["图片+BGM 并发"] = time.time() - t
        if ADS_DIALOGUE_MODE and ADSD_LIP_SYNC_EXPERIMENT:
            t = time.time(); step66_adsd_lip_sync(script);                    timings["ADSD 口型同步"] = time.time() - t
            # audio_dub retiming：按 seg_N.mp4 真实时长重算 timeline，
            # 防 master_voice TTS 短于克隆语音时 hybrid voice 被截尾
            try:
                t = time.time()
                extended = _retime_after_audio_dub(script)
                timings["audio_dub timeline 重算"] = time.time() - t
                if extended > 0:
                    tg(f"🕐 audio_dub timeline 重算：{extended} turn 按克隆真实长度拉长")
            except Exception as e:
                log(f"audio_dub retiming 异常（保留原 timeline）：{e}")
            # audio_dub 克隆音色 splice：A-roll seg 内的克隆音色拼成混合主音轨，
            # 否则 step9 默认主音轨 mux 会用 weryai 默认 TTS 覆盖掉真克隆。
            try:
                t = time.time()
                hybrid_voice = _build_voice_clone_hybrid_audio(script, voice_path)
                timings["audio_dub 克隆音色 splice"] = time.time() - t
                if hybrid_voice:
                    voice_path = hybrid_voice
                    tg("🎙 audio_dub 克隆音色已 splice 进主音轨（A-roll=克隆，B-roll=默认 TTS，loudnorm 已统一响度）")
                else:
                    tg("⚠️ audio_dub 克隆 splice 跳过：A-roll 全部缺音，回退默认主音轨")
            except Exception as e:
                log(f"hybrid voice-clone splice 异常（回退默认主音轨）：{e}")
                tg(f"⚠️ audio_dub splice 异常（回退默认主音轨）：{e}")
        elif WITH_MOTION:
            t = time.time(); step65_motion(script);                            timings["动态化 (WERYDANCE)"] = time.time() - t
        elif STORYBOARD_GRID_MULTIREF_MOTION or PREVIS_PAGE_MOTION or STORYBOARD_TRAILER_MODE or CHARACTER_TRAILER_MODE:
            t = time.time(); step65_grid_multiref_motion_qa(script);            timings["Storyboard motion QA"] = time.time() - t
        t = time.time(); raw_path   = step7_concat(script);                   timings["视频拼接"] = time.time() - t
        if NO_VOICE:
            ass_path = ""
            timings["字幕生成"] = 0.0
            tg("⏭️ BGM-only 模式：跳过字幕生成与字幕烧录")
        else:
            t = time.time(); ass_path = step8_subtitles(script);              timings["字幕生成"] = time.time() - t
        # silent_b BGM 动态浮起：在 silent_b 区间 BGM 音量 +40%
        if ADS_DIALOGUE_MODE and bgm_path:
            try:
                dyn_bgm = _build_dynamic_bgm(script, bgm_path)
                if dyn_bgm:
                    bgm_path = dyn_bgm
                    tg(f"🎵 BGM 动态浮起：silent_b 区间音量 +40%（呼吸位 BGM 接管）")
            except Exception as e:
                log(f"动态 BGM 构建异常（保留原 BGM）：{e}")
        t = time.time(); final_path = step9_render(raw_path, voice_path, bgm_path, ass_path, topic); timings["最终合成"] = time.time() - t
        t = time.time(); step10_deliver(final_path, topic, script);           timings["TG 推送"] = time.time() - t

        total_min = (time.time() - t_start) / 60
        summary = "\n".join(f"  {k}：{v/60:.1f} min" for k, v in timings.items())
        tg(f"⏱ 耗时统计（总计 {total_min:.1f} min）\n\n{summary}")

    except Exception as e:
        import traceback
        err = traceback.format_exc()
        total_min = (time.time() - t_start) / 60
        log(f"管线异常:\n{err}")
        tg(f"❌ ADR V8 管线异常（已运行 {total_min:.1f} min）\n节点：{e}\n\n详情已写入日志")
        sys.exit(1)


if __name__ == "__main__":
    main()
