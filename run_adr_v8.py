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
NO_VOICE    = "--no-voice" in sys.argv    # 跳过 Podcast / TTS，用静音轨占位；成片只有画面 + 字幕 + BGM
ADS_DIALOGUE_MODE = (
    "--ads-dialogue" in sys.argv
    or "--adsd" in sys.argv
    or os.environ.get("ADR_ADS_DIALOGUE", "").strip().lower() in ("1", "true", "yes", "on")
)
ADSD_LIP_SYNC_EXPERIMENT = (
    "--adsd-lip-sync" in sys.argv
    or "--lip-sync" in sys.argv
    or os.environ.get("ADR_ADSD_LIP_SYNC", "").strip().lower() in ("1", "true", "yes", "on")
)
ADSD_RICH_MOTION_PROMPT = (
    "--adsd-rich-motion" in sys.argv
    or os.environ.get("ADR_ADSD_RICH_MOTION", "").strip().lower() in ("1", "true", "yes", "on")
)
ADSD_ONSITE_POV_MODE = (
    "--pov" in sys.argv
    or "--onsite-pov" in sys.argv
    or os.environ.get("ADR_ADSD_ONSITE_POV", "").strip().lower() in ("1", "true", "yes", "on")
)

# --ads-reporter：把 ADS 的"拟现场第一人称记者感"并入 ADR 动态化。
# 该模式自动开启 --with-motion，并约束剧本、分镜与 motion prompt；
# 注意它是"拟现场报道"，不是现代直播，严禁手机/电视台/现代麦克风穿帮。
ADS_REPORTER_MODE = (
    "--ads-reporter" in sys.argv
    or "--first-person-reporter" in sys.argv
    or os.environ.get("ADR_ADS_REPORTER", "").strip().lower() in ("1", "true", "yes", "on")
)
if ADS_REPORTER_MODE:
    WITH_MOTION = True

ADSD_MODE_NAME = ("VADSD" if IS_VERTICAL else "HADSD") if ADS_DIALOGUE_MODE else ""

ADSD_VOICES = {
    "记者": {"voice_id": 67, "voice_name": "Refreshing Young Man"},
    "职员": {"voice_id": 69, "voice_name": "Reliable Executive"},
    "旁白": {"voice_id": 76, "voice_name": "News Anchor"},
}

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


def tg(msg: str):
    """向 Telegram 推送状态消息。"""
    try:
        requests.post(
            f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage",
            json={"chat_id": TG_CHAT_ID, "text": msg},
            timeout=(10, 15),
        )
    except Exception as e:
        log(f"TG 推送失败: {e}")


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
MOTION_SUBMIT_MIN_INTERVAL = float(os.environ.get("ADR_MOTION_SUBMIT_INTERVAL", "10"))
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
            log(f"{label} text-to-video submit 节流等待 {wait_s:.1f}s")
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


def _voice_for_speaker(speaker: str) -> dict:
    if speaker in ADSD_VOICES:
        return ADSD_VOICES[speaker]
    if any(k in speaker for k in ("少年", "青年", "士人", "书生", "学生", "百姓", "船工", "兵士", "亲历者", "见证人")):
        return ADSD_VOICES["记者"]
    if any(k in speaker for k in ("职员", "官员", "朝臣", "僧", "长者", "将领", "书吏", "幕僚", "使者", "父老", "寺")):
        return ADSD_VOICES["职员"]
    return ADSD_VOICES["旁白"]


def _adsd_default_roles(topic: str) -> tuple[str, str]:
    roles = _adsd_role_candidates(topic)
    return roles[0], roles[1] if len(roles) > 1 else roles[0]


def _adsd_role_candidates(topic: str) -> list[str]:
    if any(k in topic for k in ("同泰寺", "佛", "僧", "梁武帝", "萧衍", "寺")):
        return ["寺中僧人", "朝廷官员", "梁朝文士", "寺外百姓"]
    if any(k in topic for k in ("公车上书", "康有为", "梁启超", "科举", "上书")):
        return ["上书士人", "旁观官员", "在京举人", "书吏"]
    if any(k in topic for k in ("郑成功", "鹿耳门", "台湾", "海", "潮")):
        return ["水师兵士", "海边百姓", "船上将领", "地方父老"]
    if any(k in topic for k in ("二十一条", "最后通牒", "外交", "条约")):
        return ["街头见证人", "衙署官员", "报馆学生", "电报员"]
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
    banned_speakers = {"记者", "主持人", "主播", "职员", "采访者"}
    known: list[str] = []
    turns: list[dict] = []
    for i, raw in enumerate(raw_lines):
        line = str(raw).strip()
        m = _re.match(r"^([^：:]{2,12})[：:]\s*(.+)$", line)
        if m:
            speaker = m.group(1).strip()
            text = m.group(2).strip()
        else:
            speaker = known[0] if known else fallback_role
            text = line
        if speaker in banned_speakers or not speaker:
            speaker = known[i % len(known)] if known else fallback_role
        if speaker not in known and len(known) < 4:
            known.append(speaker)
        elif speaker not in known:
            speaker = known[i % len(known)] if known else fallback_role
        if not text:
            raise RuntimeError(f"ADSD 注入脚本第 {i+1} 行为空")
        voice = _voice_for_speaker(speaker)
        turns.append({
            "dialogue_turn": i + 1,
            "speaker": speaker,
            "speaker_id": voice["voice_id"],
            "speaker_name": voice["voice_name"],
            "text": text,
            "shot": f"{speaker}在现场说出这一句，旁人只作倾听或反应",
            "emotion": "neutral",
            "injected_script": True,
        })
    return _finalize_adsd_turns(turns)


def _adsd_pov_contract() -> str:
    return (
        "Onsite observer POV: the viewer feels physically present in the historical scene, standing at eye level "
        "beside the speaker, near a doorway, table edge, pier, street crowd, temple hall, office corridor, or army tent. "
        "Use first-person documentary camera language such as over-the-shoulder from the crowd edge, shoulder-level handheld sway, "
        "foreground documents or doorframes, and nearby listener reactions. Keep the active speaker's face and mouth readable. "
        "No modern reporter, no host, no interview setup, no microphone, no livestream, no smartphone, no TV studio."
    )


def _generate_adsd_dialogue_turns(topic: str, num_turns: int, tone: str, style_guide: str) -> list[dict]:
    """Generate ADSD dialogue turns. Each turn becomes one TTS unit and one video segment."""
    num_turns = max(4, min(12, num_turns))
    role_candidates = _adsd_role_candidates(topic)
    role_hint = " / ".join(role_candidates)
    fallback_role = role_candidates[0]
    prompt = f"""你是 ADSD（ADS Dialogue）短剧化历史讲解编剧。

主题：「{topic}」
目标：生成 {num_turns} 句现场视角台词，用最适合剧情的说话结构把复杂历史讲给普通人听懂。

可用现场角色方向（可按题材微调，但必须是历史现场内的人）：
{role_hint}

你必须先在心里判断本题最适合哪种结构，但输出里不要解释：
- 独白：一个当事人/见证人连续讲述，适合内心独白、临终陈述、密信、回忆录、案前陈词。
- 双人对白：两个人一问一答，适合解释复杂背景、因果和专名。
- 多人群像：3~4 个角色轮流发言，适合朝堂、街头、船上、战场、书院、报馆等多方在场的剧情。

硬性要求：
1. 只输出 JSON 数组，不要 Markdown，不要解释。
2. 数组长度必须正好 {num_turns}。
3. 每项字段必须包含：speaker、text、shot、emotion。
4. speaker 必须是现场角色名；全片使用 1~4 个 speaker。根据剧情需要可独白、双人或多人，不强制交替。
5. text 是中文对白，每句 18~36 字，白话、直接、普通人能听懂。
6. shot 是中文画面说明，要具体到地点、道具、人物动作；必须让当前 speaker 成为画面里的说话主体；如有其他角色，只作为倾听/反应对象。
7. emotion 只能从 neutral / tense / solemn / explanatory 中选。
8. 严禁诗化表达、隐喻、金句、含蓄暗示、空泛大词。
9. 每 2~3 句必须解释一个专名或因果。
10. 结尾要把主题讲清楚，不要只煽情。
11. 不要出现「记者」「主持人」「主播」「采访」这些现代媒体身份，除非主题本身真实发生在现代新闻现场。
12. 这是“现场视角”，不是记者报道；镜头可以像观众站在现场旁听。
{"13. 已启用 POV 现场旁听模式：shot 必须写出观众仿佛站在人群边、门口、案前、船边、廊下或帐内近距离看见当前 speaker 说话；不要写成记者出镜、直播、采访。" if ADSD_ONSITE_POV_MODE else ""}
14. 不要为了凑人数而加角色；如果一个人讲最清楚，就用独白；如果多人在场更自然，才用多人。

语言风格：
{style_guide}

输出示例格式：
[
  {{"speaker":"{fallback_role}","text":"这张告示刚贴出来，街口的人全围过来了。","shot":"街口墙边，{fallback_role}指着新贴告示，旁人凝神看","emotion":"tense"}}
]"""
    raw = chat("GEMINI_3_1_FLASH_LITE", "你只输出严格 JSON 数组。", prompt, max_tokens=2600, timeout=180)
    arr = _extract_json_array(raw)
    if len(arr) != num_turns:
        raise RuntimeError(f"ADSD 对话句数不匹配：got {len(arr)}, need {num_turns}")
    turns = []
    speakers_seen: list[str] = []
    banned_speakers = {"记者", "主持人", "主播", "职员", "采访者"}
    for i, item in enumerate(arr):
        speaker = str(item.get("speaker", "")).strip()
        if speaker in banned_speakers or not speaker:
            speaker = speakers_seen[i % len(speakers_seen)] if speakers_seen else fallback_role
        if speaker not in speakers_seen and len(speakers_seen) < 4:
            speakers_seen.append(speaker)
        elif speaker not in speakers_seen:
            speaker = speakers_seen[i % len(speakers_seen)] if speakers_seen else fallback_role
        text = str(item.get("text", "")).strip()
        shot = str(item.get("shot", "")).strip()
        emotion = str(item.get("emotion", "neutral")).strip().lower()
        if emotion not in ("neutral", "tense", "solemn", "explanatory"):
            emotion = "neutral"
        if not text or len(text) > 80:
            raise RuntimeError(f"ADSD 第 {i+1} 句台词异常：{text}")
        voice = _voice_for_speaker(speaker)
        turns.append({
            "dialogue_turn": i + 1,
            "speaker": speaker,
            "speaker_id": voice["voice_id"],
            "speaker_name": voice["voice_name"],
            "text": text,
            "shot": shot or f"{speaker}在现场说明材料",
            "emotion": emotion,
        })
    speakers = [t["speaker"] for t in turns if t.get("speaker")]
    shape = _adsd_dialogue_shape(speakers)
    speaker_count = len(dict.fromkeys(speakers))
    for turn in turns:
        turn["dialogue_shape"] = shape
        turn["speaker_count"] = speaker_count
    return turns


def _adsd_visual_contract(speaker: str, lip_sync: bool | None = None) -> str:
    """Prompt contract for ADSD: keep the active speaker visually accountable."""
    if lip_sync is None:
        lip_sync = ADSD_LIP_SYNC_EXPERIMENT
    anchor = (
        f"Active speaker is the historical onsite character labelled '{speaker}'. "
        "Show this person as the clear speaking subject inside the period scene, face readable in three-quarter view, "
        "with any other onsite characters only listening or reacting nearby. No modern reporter, no TV host, no microphone"
    )
    pov = f". {_adsd_pov_contract()}" if ADSD_ONSITE_POV_MODE else ""
    if lip_sync:
        return (
            f"{anchor}. Talking-head friendly framing: medium close-up or over-shoulder two-shot, mouth area visible, "
            f"subtle natural lip movement implied, no extreme mouth close-up, no distorted teeth, no modern microphone{pov}"
        )
    return (
        f"{anchor}. Speaker-focus framing: medium close-up or over-shoulder two-shot, mouth can be visible but do not force exact lip sync, "
        f"use eyes, hands, documents and reaction timing to sell the dialogue, no extreme mouth close-up{pov}"
    )


def step1_script(topic: str) -> list[dict]:
    fmt_label = f"{ADSD_MODE_NAME} {'9:16' if IS_VERTICAL else '16:9'}" if ADS_DIALOGUE_MODE else ("VDAR 9:16" if IS_VERTICAL else "HDAR 16:9")
    tg(f"🎬 ADR V8 启动\n主题：{topic}\n格式：{fmt_label}\n\n斯皮尔伯格正在撰写台词...")
    log(f"开始处理：{topic} [{fmt_label}]")

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
    try:
        import json
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
    _OVERRIDE_FILE = Path("/tmp/adr_script_override.txt")
    _script_injected = False
    dialogue_turns: list[dict] = []
    if _OVERRIDE_FILE.exists() and _OVERRIDE_FILE.stat().st_size > 0:
        _override_lines = [l.strip() for l in _OVERRIDE_FILE.read_text(encoding="utf-8").splitlines() if l.strip()]
        if 6 <= len(_override_lines) <= 22:
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
            tg(f"📥 检测到外部脚本注入\n读取 {num_lines} 句台词，跳过 LLM 自动生成")
            _used_path = _OVERRIDE_FILE.with_suffix(f".used_{int(time.time())}")
            _OVERRIDE_FILE.rename(_used_path)
            log(f"外部脚本已重命名为 {_used_path.name}")
        else:
            log(f"⚠️ 外部脚本句数 {len(_override_lines)} 不在 6~22 范围内，忽略，走 LLM 生成")
            tg(f"⚠️ 外部脚本句数 {len(_override_lines)} 不在 6~22 范围内，已忽略")

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
            visual_contract = _adsd_visual_contract(dialogue_meta.get("speaker", ""))
            subject = (
                f"{dialogue_meta.get('shot', '')}. "
                f"Dialogue speaker: {dialogue_meta.get('speaker', '')}; "
                f"{visual_contract}. "
                f"{subject}"
            )
        # 硬拼接：导演 + 镜头模板 + 主体 + 情绪风格 + negative
        parts = [director_tag, shot_tmpl, subject]
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
        item = {"text": line, "emotion": emotion, "prompt": prompt, "historical_context": historical_context, "tone": tone}
        if dialogue_meta:
            item.update({
                "dialogue_mode": True,
                "dialogue_turn": dialogue_meta.get("dialogue_turn", i + 1),
                "speaker": dialogue_meta.get("speaker", ""),
                "speaker_id": dialogue_meta.get("speaker_id"),
                "speaker_name": dialogue_meta.get("speaker_name", ""),
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
    tg(f"✅ 画面提示词就绪，情绪标签分布：{emotion_summary}")

    # 音色选择：根据主题和情绪由 LLM 推荐最合适的音色
    voice_prompt = f"""你是纪录片音频导演。根据主题和情绪，从以下音色中选择最合适的一个。

主题：{topic}
情绪分布：{emotion_summary}
台词风格：{lines[0]} / {lines[4]} / {lines[-1]}

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

    return script, picked_id, picked_name


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


def step2_master_voice(script: list[dict], speaker_id: str = "liyan2-ef9401ec", speaker_name: str = "国栋") -> str:
    n = len(script)
    MAX_RETRIES = 5

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


def _asr_verify_dialogue_audio(audio_path: str) -> dict | None:
    """Upload ADSD master audio through Telegram and verify transcript with WeryAI ASR."""
    if os.environ.get("ADR_ADSD_SKIP_ASR", "").strip().lower() in ("1", "true", "yes", "on"):
        return None
    try:
        with open(audio_path, "rb") as f:
            r = requests.post(
                f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendAudio",
                data={"chat_id": TG_CHAT_ID, "caption": "ADSD QA audio for ASR"},
                files={"audio": (os.path.basename(audio_path), f, "audio/mpeg")},
                timeout=(30, 180),
            )
        r.raise_for_status()
        file_id = (r.json().get("result") or {}).get("audio", {}).get("file_id")
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
        data = poll_task_status(task_id, "ADSD ASR", max_wait=240)
        (OUTPUT_DIR / "speech_recognize_result.json").write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return data
    except Exception as e:
        log(f"ADSD ASR 校验失败（不阻断）：{e}")
        tg(f"⚠️ ADSD ASR 校验失败，不阻断成片：{e}")
        return None


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
        tolerant_pass = ratio >= 0.985 and len(missing_chunks) <= 2
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
            scenes.append({
                "turn": i + 1,
                "speaker": speaker,
                "dialogue_shape": scene.get("dialogue_shape"),
                "speaker_count": scene.get("speaker_count"),
                "audio_start": scene.get("audio_start"),
                "audio_end": scene.get("audio_end"),
                "duration": scene.get("dur"),
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
            or not s["prompt_has_active_speaker"]
            or not s["onsite_pov_prompt"]
            or s["audio_start"] is None
            or s["audio_end"] is None
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


def step2_dialogue_voice(script: list[dict]) -> str:
    """ADSD voice core: one TTS per dialogue turn, deterministic timeline."""
    pause = float(os.environ.get("ADR_ADSD_TURN_PAUSE", "0.22"))
    tg(f"🎭 {ADSD_MODE_NAME} TTS 启动：text-to-audio × {len(script)} turn，逐句生成确定性时间轴...")
    timeline = []
    wav_files: list[str] = []
    cursor = 0.0
    for i, turn in enumerate(script):
        wav_path, dur, meta = _tts_turn_to_audio(turn, i)
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
        if i < len(script) - 1:
            silence = str(OUTPUT_DIR / f"silence_{i+1:02d}.wav")
            ffmpeg(
                "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono",
                "-t", str(pause),
                "-c:a", "pcm_s16le",
                silence,
                timeout=30,
            )
            wav_files.append(silence)
            cursor += dur + pause
        else:
            cursor += dur
        log(f"ADSD turn {i+1}: {turn.get('speaker')} {dur:.3f}s [{turn['audio_start']:.3f}-{turn['audio_end']:.3f}]")
    timeline_path = OUTPUT_DIR / "turn_timeline.json"
    timeline_path.write_text(json.dumps(timeline, ensure_ascii=False, indent=2), encoding="utf-8")
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
            samples = [m.get("chunk") for m in asr_qa.get("missing_chunks", [])[:5]]
            tg(
                f"⚠️ ADSD ASR 文本一致性需复查：similarity={asr_qa.get('similarity')}, "
                f"missing={asr_qa.get('missing_count')}，样例：{', '.join(samples)}"
            )
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


def _calc_sentence_boundaries(voice_path: str, script: list[dict]) -> list[dict]:
    """
    三源融合方案：Whisper 语速曲线 + 字符数插值 + silencedetect 物理校准。

    第一层：Whisper segment 建立粗粒度"累积字数 → 时间"映射表
    第二层：用台词字符数在映射表上线性插值，精细化到每句边界
    第三层：silencedetect 提取音频中的物理静音点，对插值边界做吸附校准

    回退：Whisper 不可用时退化为纯字数比例（不做 silencedetect 校准）。
    """
    total_dur = ffprobe_duration(voice_path)
    n = len(script)
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


_weryai_upload_lock = threading.Lock()


def _upload_to_weryai(file_path: str) -> str:
    """Upload a local media file to WeryAI official storage and return its URL."""
    import mimetypes
    mime = mimetypes.guess_type(file_path)[0] or "application/octet-stream"
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


def _send_for_approval(img_path: str, idx: int, text: str) -> None:
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

    delays = [0, 5, 10, 20, 40, 80]  # 第 0-5 次尝试前的等待
    for attempt in range(6):
        if delays[attempt] > 0:
            time.sleep(delays[attempt])
        try:
            with open(upload_path, "rb") as f:
                resp = requests.post(url, data={
                    "chat_id": TG_CHAT_ID,
                    "caption": f"🖼 图 {idx+1} 审批\n\n{text}",
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


def generate_image(scene: dict, idx: int, _max_retries: int = 3) -> int:
    last_err = None
    for attempt in range(_max_retries):
        try:
            _m, _ar, _extra = pick_image_model(ASPECT_RATIO)
            _wait_image_submit_slot(f"图片 {idx+1}")
            r = req_post("/generation/text-to-image", {
                "model":        _m,
                "prompt":       scene["prompt"],
                "aspect_ratio": _ar,
                "image_number": 1,
                **_extra,
            }, timeout=30)

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


def step6_parallel(script: list[dict], topic: str) -> str | None:
    n = len(script)
    tg(f"🚀 并行生成：{n} 张图片 + BGM（图片生成即审批，BGM 后台同步跑）...")

    MAX_REDO = 3
    bgm_tone = script[0].get("tone", "中性") if script else "中性"
    media_workers = max(2, min(20, int(os.environ.get("ADR_MEDIA_WORKERS", "20"))))
    # BGM 后台启动，不阻塞审批
    with ThreadPoolExecutor(max_workers=media_workers) as ex:
        bgm_fut = ex.submit(generate_bgm, topic, bgm_tone)

        # 图片：每张生成完立刻审批，不等全部完成
        img_futs = {ex.submit(generate_image, s, i): i for i, s in enumerate(script)}

        # ★ 每张图生成完立即推审批（不等所有 22 张完成才统一推）
        # SKIP_APPROVAL 模式跳过推送
        completed = {}  # idx -> True
        approval_sent = set()  # 已推过审批的 idx，避免兜底重发
        for f in as_completed(img_futs):
            idx = img_futs[f]
            try:
                f.result()
                completed[idx] = True
                # ★ 立即推审批（图刚出来就让大哥审）
                if not SKIP_APPROVAL:
                    _send_for_approval(script[idx]["img_path"], idx, script[idx]["text"])
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
                        _send_for_approval(dst, idx, script[idx]["text"])
                        approval_sent.add(idx)
                except Exception as e:
                    raise RuntimeError(f"图 {idx+1} 兜底失败: {e}")

        # ── 审批流程 ────────────────────────────────────────────────────
        if SKIP_APPROVAL:
            # ★ v0.2 智能异常检测：用 Gemini Vision 批量审 22 张图
            # 异常张（文字错/风格离群/内容偏离）单独推审批；其他自动通过
            tg(f"🔍 智能异常检测：Vision 扫描 {n} 张图...")
            anomaly_idxs = _llm_check_scenes_anomalies(script)
            qa_path = OUTPUT_DIR / "scene_qa.json"
            qa_payload = {
                "mode": ADSD_MODE_NAME if ADS_DIALOGUE_MODE else ("VDAR" if IS_VERTICAL else "HDAR"),
                "total": n,
                "anomaly_indices": sorted(int(i) for i in anomaly_idxs),
                "anomaly_scene_numbers": sorted(int(i) + 1 for i in anomaly_idxs),
                "policy": "auto_approve_adsd" if ADS_DIALOGUE_MODE else "manual_review_anomalies",
                "created_at": datetime.now().isoformat(timespec="seconds"),
            }
            try:
                qa_path.write_text(json.dumps(qa_payload, ensure_ascii=False, indent=2), encoding="utf-8")
            except Exception as e:
                log(f"scene_qa.json 写入失败: {e}")
            if ADS_DIALOGUE_MODE:
                if anomaly_idxs:
                    tg(
                        f"⚠️ {ADSD_MODE_NAME} 场景 QA：Vision 标记 {len(anomaly_idxs)} 张疑似异常 "
                        f"{sorted(i+1 for i in anomaly_idxs)}，已记录 {qa_path.name} 并自动放行"
                    )
                else:
                    tg(f"✅ {ADSD_MODE_NAME} 场景 QA：全部 {n} 张通过，自动进入合成阶段")
                anomaly_idxs = set()
            if anomaly_idxs:
                tg(f"⚠️ 异常检测：{len(anomaly_idxs)} 张需要你审核：{sorted(i+1 for i in anomaly_idxs)}\n（其他 {n - len(anomaly_idxs)} 张自动通过）")
                # 推送异常张到 Telegram
                for idx in sorted(anomaly_idxs):
                    _send_for_approval(script[idx]["img_path"], idx, script[idx]["text"])
                # 等异常张审批（5min 超时自动通过）
                approved_anomalies = set()
                t0 = time.time()
                while len(approved_anomalies) < len(anomaly_idxs) and time.time() - t0 < 320:
                    for idx in anomaly_idxs:
                        if idx in approved_anomalies:
                            continue
                        if (APPROVAL_DIR / f"{idx}.approved").exists():
                            approved_anomalies.add(idx)
                            tg(f"✅ 图 {idx+1} 通过 ({len(approved_anomalies)}/{len(anomaly_idxs)})")
                        elif (APPROVAL_DIR / f"{idx}.rejected").exists():
                            # 拒绝 → 用相邻图顶替（兜底逻辑）
                            import shutil
                            for offset in range(1, n):
                                for cand in (idx - offset, idx + offset):
                                    if 0 <= cand < n and cand not in anomaly_idxs:
                                        shutil.copy(str(OUTPUT_DIR / f"img_{cand}.jpg"), str(OUTPUT_DIR / f"img_{idx}.jpg"))
                                        tg(f"🔄 图 {idx+1} 被拒，复用图 {cand+1} 顶替")
                                        approved_anomalies.add(idx)
                                        break
                                if idx in approved_anomalies:
                                    break
                    time.sleep(2)
                # 超时自动通过剩余
                for idx in anomaly_idxs:
                    if idx not in approved_anomalies:
                        approved_anomalies.add(idx)
                tg(f"✅ 异常张审核完成，进入合成阶段")
            else:
                tg(f"⏭️ 全部 {n} 张通过智能审核，自动进入合成阶段")
            bgm_path = None
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
                        _send_for_approval(script[i]["img_path"], i, script[i]["text"])
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
        bgm_path = None
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
{"- Onsite POV mode is ON: make the viewer feel physically present beside the speaker or at the crowd/door/table edge. This is not a reporter, host, interview, livestream, or broadcast setup." if ADSD_ONSITE_POV_MODE else ""}
""" if ADS_DIALOGUE_MODE else ""
    try:
        summary_lines = "\n".join(
            f"{i+1}. ({sc.get('dur', 5):.0f}s, speaker: {sc.get('speaker', '旁白')}, emotion: {sc.get('emotion', 'neutral')}) {sc['text'][:80]}"
            for i, sc in enumerate(script)
        )
        raw = chat(
            "GEMINI_25_FLASH",
            "You are a cinematographer giving motion direction for still documentary frames. Output strict JSON only.",
            f"""Generate {n} motion prompts for a Chinese documentary. Each scene already has a static keyframe image; you only describe camera movement and subtle motion within the frame (40-60 words, English).

Scene summary:
{summary_lines}

Rules:
- Describe camera moves (slow push-in, gentle pan, orbit, pull-back, dolly) + subtle in-frame motion (light drift, smoke, water ripples, leaves swaying).
- Match emotion: tense → sharper moves; calm → slow; historical → steady.
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
    return ["slow zoom in with gentle camera drift, subtle ambient motion, cinematic atmosphere, smooth motion"] * n


_motion_tasks_lock = threading.Lock()


def _motion_tasks_file() -> Path:
    return OUTPUT_DIR / "motion_tasks.json"


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


def _motion_poll_and_download(idx: int, task_id: str, vid_path: str) -> bool:
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
            videos = (
                s.get("data", {}).get("videos")
                or s.get("data", {}).get("task_result", {}).get("videos")
                or []
            )
            vid_url = videos[0] if videos else ""
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
                os.replace(tmp_path, vid_path)
                _remove_motion_task(idx)  # 成功后清记录
                return True
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
                f"Simple slow camera push, slight head movement, subtle paper movement, natural light, realistic motion.{pov} "
                "No modern reporter, no TV host, no microphone, no famous style, no branded references, no movie references, no text, no logos, no watermark."
            )
        return (
            "Historically grounded period dialogue scene, neutral archival realism, "
            "warm sepia paper tones, period clothing and topic-accurate props. "
            f"{contract}. "
            f"Scene action: {shot}. "
            f"Camera motion: {motion_prompt}. "
            "Avoid branded style references, artist names, movie-title references, copyrighted characters, modern devices, subtitles, logos, watermarks."
        )
    scene_prompt = scene.get("prompt", "")
    return f"{scene_prompt}. Camera motion: {motion_prompt}" if scene_prompt else motion_prompt


def _motion_one_scene(idx: int, scene: dict, motion_prompt: str, aspect_ratio: str, safe_retry: bool = False) -> bool:
    """对单个 scene 调 WERYDANCE_2_0 生成 motion 版 seg_N.mp4；成功返回 True"""
    img_path = scene["img_path"]
    vid_path = scene["vid_path"]  # 静态 seg_N.mp4 的路径，成功就覆盖它
    # WERYDANCE 支持 5-10s；字段名统一用 vid_duration（step345_timeline 里的 key）
    _raw_dur = scene.get("vid_duration") or scene.get("dur") or 5
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
                return _motion_poll_and_download(idx, existing_tid, vid_path)
            if st == "failed":
                log(f"[motion {idx}] 历史任务 {existing_tid} 已 failed，移除记录，重新提交")
                _remove_motion_task(idx)
            elif st in ("waiting", "processing"):
                log(f"[motion {idx}] 历史任务 {existing_tid} 仍 {st}，继续轮询")
                return _motion_poll_and_download(idx, existing_tid, vid_path)
            # 其他状态：走新提交流程
        except Exception as e:
            log(f"[motion {idx}] 查历史任务失败: {e}，走新提交")

    try:
        # Phase 1 改造：直接 text-to-video（Seedance 2.0），绕过"照片晃动"，走真正摄影机运动
        # ADSD 使用降噪 prompt，避免把上游静帧 prompt 的风格词带入 WERYDANCE 触发版权拦截。
        full_prompt = _build_motion_video_prompt(scene, motion_prompt, safe_retry=safe_retry)
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
                "negative_prompt": "no subtitles, no text overlay, no watermark, no captions, no burned-in text, no logo",
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
            return False

        # ★ 立即持久化：轮询任何阶段失败/超时，下次 rerun 都能复用
        _save_motion_task(idx, task_id)

        # 轮询 + 下载
        return _motion_poll_and_download(idx, task_id, vid_path)
    except Exception as e:
        log(f"[motion {idx}] 异常: {type(e).__name__}: {e}")
        return False


def _lip_sync_slot_duration(script: list[dict], idx: int) -> float:
    scene = script[idx]
    if idx < len(script) - 1:
        return max(1.0, float(script[idx + 1].get("audio_start", scene.get("audio_end", 0))) - float(scene.get("audio_start", 0)))
    return max(1.0, float(scene.get("audio_end", scene.get("audio_start", 0) + scene.get("dur", 1))) - float(scene.get("audio_start", 0)))


def _adsd_lip_sync_prompt(scene: dict, safe_retry: bool = False) -> str:
    speaker = scene.get("speaker") or "speaker"
    role = f"historical onsite character labelled {speaker}"
    pov = (
        " First-person onsite observer POV: viewer stands beside the active speaker or at the crowd/door/table edge, "
        "close enough to see the face and mouth, without reporter or interview framing."
        if ADSD_ONSITE_POV_MODE else ""
    )
    if safe_retry:
        return (
            "Neutral period dialogue scene. "
            f"Active speaker is the {role}; any other onsite characters listen silently. "
            "The active speaker follows the provided Chinese audio reference with natural mouth movement. "
            f"Visible mouth, stable face, subtle head motion, realistic lighting.{pov} "
            "No modern reporter, no TV host, no microphone, no subtitles, no text overlay, no logos, no watermark, no branded style references."
        )
    text = scene.get("text", "")
    shot = scene.get("shot", "")
    return (
        "Historically grounded period dialogue scene. "
        f"Active speaker is the {role}; any other people only listen or react. "
        f'台词:"{text}" The active speaker says exactly this line. '
        f"Mouth movement must synchronize with the provided audio reference; keep the mouth visible with natural jaw movement.{pov} "
        f"Scene action: {shot}. "
        "Keep the same face and period clothing, no modern reporter, no TV host, no microphone, no subtitles, no text overlay, no logo, no watermark."
    )[:2000]


def _postprocess_lip_sync_segment(src_video: str, scene: dict, target_dur: float) -> bool:
    """Normalize Werydance silent lip video to ADR segment size and exact timeline duration."""
    vid_path = scene["vid_path"]
    src_dur = ffprobe_duration(src_video)
    pad = max(0.0, target_dur - src_dur)
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


def _lip_sync_poll_download_and_process(idx: int, task_id: str, scene: dict, target_dur: float) -> tuple[bool, dict]:
    info = {
        "turn": idx + 1,
        "speaker": scene.get("speaker"),
        "task_id": task_id,
        "source_audio": scene.get("dialogue_audio_mp3") or scene.get("dialogue_audio"),
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
                ok = _postprocess_lip_sync_segment(raw_path, scene, target_dur)
                final_dur = ffprobe_duration(scene["vid_path"]) if ok else None
                source_audio = scene.get("dialogue_audio_mp3") or scene.get("dialogue_audio")
                audio_dur = ffprobe_duration(source_audio) if source_audio and os.path.exists(source_audio) else None
                info.update({
                    "pass": ok,
                    "candidate": "almighty_reference_image_audio",
                    "raw_video_path": raw_path,
                    "raw_video_duration": raw_dur,
                    "final_segment_path": scene["vid_path"],
                    "final_segment_duration": final_dur,
                    "source_audio_duration": audio_dur,
                    "video_has_audio": False,
                    "duration_delta": abs((final_dur or 0) - target_dur) if final_dur is not None else None,
                    "clip_duration_match_pass": final_dur is not None and abs(final_dur - target_dur) <= 0.25,
                    "needs_master_audio_mux": True,
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
    source_audio = scene.get("dialogue_audio_mp3") or scene.get("dialogue_audio")
    if not source_audio or not os.path.exists(source_audio):
        return idx, False, {"turn": idx + 1, "pass": False, "reason": "missing_turn_audio"}
    existing_tid = _load_lip_sync_tasks().get(str(idx))
    if existing_tid:
        ok, info = _lip_sync_poll_download_and_process(idx, existing_tid, scene, target_dur)
        return idx, ok, info
    try:
        image_url = _upload_to_weryai(scene["img_path"])
        audio_url = _upload_to_weryai(source_audio)
        api_dur = int(round(max(5, min(15, float(scene.get("dur") or target_dur)))))
        variants = [
            ("primary", "WERYDANCE_2_0", _adsd_lip_sync_prompt(scene, safe_retry=False)),
            ("safe_prompt", "WERYDANCE_2_0", _adsd_lip_sync_prompt(scene, safe_retry=True)),
            ("fast_safe_prompt", "WERYDANCE_2_0_FAST", _adsd_lip_sync_prompt(scene, safe_retry=True)),
        ]
        attempts: list[dict] = []
        for variant_name, model, prompt in variants:
            r = None
            task_id = None
            for submit_attempt in range(3):
                try:
                    _wait_motion_submit_slot(f"lip-sync {idx+1}")
                    r = req_post("/generation/almighty-reference-to-video", {
                        "model": model,
                        "images": [image_url],
                        "audios": [audio_url],
                        "prompt": prompt,
                        "duration": api_dur,
                        "aspect_ratio": aspect_ratio,
                        "resolution": "720p",
                        "generate_audio": "false",
                        "video_number": 1,
                    }, timeout=30)
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
                "image_url": image_url,
                "audio_url": audio_url,
            })
            attempts.append({k: v for k, v in info.items() if k not in ("image_url", "audio_url", "response")})
            if ok:
                info["attempts"] = attempts
                return idx, ok, info
        final = dict(attempts[-1]) if attempts else {"turn": idx + 1, "pass": False, "reason": "no_attempts"}
        final.update({"turn": idx + 1, "pass": False, "attempts": attempts, "image_url": image_url, "audio_url": audio_url})
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
    tg(f"👄 {ADSD_MODE_NAME} 口型同步启动：WERYDANCE_2_0 Almighty Reference × {n} turn")
    target_durs = [_lip_sync_slot_duration(script, i) for i in range(n)]
    results: dict[int, bool] = {}
    records: list[dict] = []
    max_workers = min(10, n)
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
    qa = {
        "mode": ADSD_MODE_NAME,
        "interface": "almighty-reference-to-video",
        "model": "WERYDANCE_2_0",
        "onsite_pov_mode": ADSD_ONSITE_POV_MODE,
        "total": n,
        "success_count": success_cnt,
        "success_rate": round(success_cnt / max(n, 1), 4),
        "pass": success_cnt >= max(1, math.ceil(n * 0.8)),
        "policy": "failed_turns_keep_existing_segments",
        "master_audio_mux_required": True,
        "final_audio_offset_required": 0.0,
        "manual_visual_checks_required": ["mouth_visible", "active_speaker_correct", "no_face_drift", "mouth_motion_matches_syllable_timing"],
        "records": records,
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }
    (OUTPUT_DIR / "lip_sync_qa.json").write_text(json.dumps(qa, ensure_ascii=False, indent=2), encoding="utf-8")
    if qa["pass"]:
        tg(f"✅ {ADSD_MODE_NAME} 口型同步 QA 通过：{success_cnt}/{n}")
    else:
        tg(f"⚠️ {ADSD_MODE_NAME} 口型同步 QA 未达标：{success_cnt}/{n}，本次仍可用静态/motion兜底成片")


def step65_motion(script: list[dict]):
    """把静态 seg_N.mp4 替换为 WERYDANCE_2_0 动态版本（并发 + 单轮内失败自动重试 1 次）"""
    n = len(script)
    reporter_tag = " · ADS拟现场记者" if ADS_REPORTER_MODE else ""
    tg(f"🎬 动态化启动{reporter_tag}：WERYDANCE_2_0 × {n} 分镜并发生成运动视频...")

    # 1. 生成每个分镜的 motion prompt
    motion_prompts = _generate_motion_prompts(script)
    tg(f"✅ Motion prompts 就绪（{n} 条）")

    aspect = "9:16" if IS_VERTICAL else "16:9"
    results: dict[int, bool] = {}

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

    # Round 1：全量并发
    _run_batch(list(range(n)), "round 1")

    # Round 2：失败的自动重试 1 次（task_id 持久化下已成功的不会重复烧钱）
    failed_r1 = [i for i, ok in results.items() if not ok]
    if failed_r1:
        tg(f"🔄 第一轮失败 {len(failed_r1)}/{n}，自动用极简安全 prompt 重试 1 次...")
        _run_batch(failed_r1, "round 2", safe_retry=True)

    success_cnt = sum(1 for v in results.values() if v)
    if ADS_DIALOGUE_MODE:
        speaker_qa = _write_adsd_speaker_focus_qa(script, results)
        if speaker_qa and not speaker_qa.get("pass"):
            tg(f"⚠️ {ADSD_MODE_NAME} 说话人镜头同步 QA 未通过：failed={speaker_qa.get('failed_count')}")
    tg(f"✅ 动态化完成：{success_cnt}/{n} 成功 · {n - success_cnt} 保留静态兜底（含重试后仍失败）")


# ── 第七步：拼接视频轨 ────────────────────────────────────────────────────────
def step7_concat(script: list[dict]) -> str:
    concat_txt = OUTPUT_DIR / "concat.txt"
    with open(concat_txt, "w") as f:
        for s in script:
            f.write(f"file '{s['vid_path']}'\n")

    raw_path = str(OUTPUT_DIR / "raw_concat.mp4")
    ffmpeg(
        "-f", "concat", "-safe", "0", "-i", str(concat_txt),
        "-c", "copy", raw_path,
    )
    dur = ffprobe_duration(raw_path)
    tg(f"✅ 视频轨拼接完成，总时长 {dur:.2f}s，分辨率 {VIDEO_W}×{VIDEO_H}")
    return raw_path


# ── 第八步：生成 ASS 字幕 ────────────────────────────────────────────────────
def step8_subtitles(script: list[dict]) -> str:
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
    all_texts = [s['text'] for s in script]
    llm_result = _llm_split_subtitles(all_texts, SUBTITLE_MAX_CHARS)

    with open(ass_path, "w", encoding="utf-8") as f:
        f.write(header)
        SUB_GAP = 0.10
        FADE_TAG = r"{\fad(150,100)}"

        for idx, s in enumerate(script):
            t_start, t_end = s['sub_start'], s['sub_end']
            if llm_result and idx < len(llm_result):
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
            for seg in segments:
                seg_dur = max(content_dur * len(seg.replace(r"\N", "")) / total_chars, 0.8)
                seg_end = min(cursor + seg_dur, t_end)
                if seg.strip():
                    f.write(
                        f"Dialogue: 0,{ass_time(cursor)},{ass_time(seg_end)},"
                        f"Default,,0,0,0,,{FADE_TAG}{seg}\n"
                    )
                cursor = seg_end + SUB_GAP

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
        ("asr_qa.json", "ASR text match"),
    ]
    if ADSD_LIP_SYNC_EXPERIMENT:
        required_files.append(("lip_sync_qa.json", "lip sync"))

    for name, label in required_files:
        passed = _qa_file_pass(name)
        if passed is None:
            issues.append(f"{label} QA missing: {name}")
        elif not passed:
            issues.append(f"{label} QA failed: {name}")

    subtitle_qa = _read_output_json("subtitle_qa.json")
    if isinstance(subtitle_qa, dict) and subtitle_qa.get("leaked_speaker_labels"):
        issues.append(f"subtitle speaker label leak: {subtitle_qa.get('leaked_speaker_labels')}")

    timeline = _read_output_json("turn_timeline.json")
    if isinstance(timeline, list):
        speakers = [str(t.get("speaker", "")).strip() for t in timeline if isinstance(t, dict)]
        speaker_count = len([s for s in dict.fromkeys(speakers) if s])
        banned = {"记者", "主持人", "主播", "采访者"}
        if not ADS_REPORTER_MODE:
            leaked_roles = sorted({s for s in speakers if s in banned})
            if leaked_roles:
                issues.append(f"modern media speaker roles leaked: {leaked_roles}")
        if not speakers:
            issues.append("turn_timeline has no speakers")
        elif speaker_count > 4:
            issues.append(f"too many ADSD speakers: {speaker_count}")
    else:
        issues.append("turn_timeline.json missing")

    lip_sync_qa = _read_output_json("lip_sync_qa.json")
    if ADSD_LIP_SYNC_EXPERIMENT and isinstance(lip_sync_qa, dict):
        rate = float(lip_sync_qa.get("success_rate") or 0)
        if rate < 0.8:
            issues.append(f"lip_sync success_rate below 0.8: {rate:.4f}")
        if lip_sync_qa.get("success_count") != lip_sync_qa.get("total"):
            warnings.append(
                f"lip_sync partial success: {lip_sync_qa.get('success_count')}/{lip_sync_qa.get('total')}"
            )

    payload = {
        "mode": ADSD_MODE_NAME,
        "onsite_pov_mode": ADSD_ONSITE_POV_MODE,
        "lip_sync_experiment": ADSD_LIP_SYNC_EXPERIMENT,
        "final_path": final_path,
        "pass": len(issues) == 0,
        "issues": issues,
        "warnings": warnings,
        "checks": {
            "subtitle_qa": _qa_file_pass("subtitle_qa.json"),
            "speaker_focus_qa": _qa_file_pass("speaker_focus_qa.json"),
            "lip_sync_qa": _qa_file_pass("lip_sync_qa.json"),
            "asr_qa": _qa_file_pass("asr_qa.json"),
            "audio_video_delta": audio_video_delta,
        },
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }
    (OUTPUT_DIR / "delivery_qa.json").write_text(
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
    render_audio_offset = 0.0 if (ADS_DIALOGUE_MODE and ADSD_LIP_SYNC_EXPERIMENT) else AUDIO_DELAY
    sync_note = "口型同步模式：音频不延迟" if render_audio_offset == 0 else "画面 → +{:.1f}s 字幕 → +{:.1f}s 配音".format(SUB_DELAY, render_audio_offset)
    tg("🎬 最终合成中... 视频轨 ✓ 主音轨 ✓" + (" BGM ✓" if bgm_path else "") + f" 字幕烧录 ✓\n{sync_note}")

    # ★ 音画同步修正：WERYDANCE 每段固定 5s × N，但配音总时长 ≠ 5N（往往更长）
    # 若配音比视频长 > 1s，整体用 setpts 拉伸视频到配音时长，避免 -shortest 截断尾部内容
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
    ass_escaped = ass_path.replace("\\", "/").replace(":", "\\:")

    # -itsoffset AUDIO_DELAY 延迟音频，画面先出
    # 字幕已在 step8 中加了 SUB_DELAY 偏移，在画面和配音之间
    offset = str(render_audio_offset)

    if bgm_path:
        ffmpeg(
            "-i", raw_path,
            "-itsoffset", offset, "-i", voice_path,
            "-itsoffset", offset, "-i", bgm_path,
            "-filter_complex",
            "[1:a]apad=pad_dur=1.5,volume=1.5[va];[2:a]volume=0.6[ba];[va][ba]amix=inputs=2:duration=first[aout]",
            "-map", "0:v",
            "-map", "[aout]",
            "-vf", f"scale={VIDEO_W}:{VIDEO_H},setsar=1,setdar={ASPECT_RATIO},tpad=stop_mode=clone:stop_duration=1.5,ass={ass_escaped}",
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
            "-vf", f"scale={VIDEO_W}:{VIDEO_H},setsar=1,setdar={ASPECT_RATIO},tpad=stop_mode=clone:stop_duration=1.5,ass={ass_escaped}",
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
                        t = re.sub(r'[\#《》【】""""''()（）\[\]]', '', t)
                        t = re.sub(r'[a-zA-Z]', '', t)
                    elif tone == "庄重":
                        t = re.sub(r'[\#《》【】""""''()（）\[\]!?！？]', '', t)
                        t = re.sub(r'[a-zA-Z]', '', t)
                    else:
                        t = re.sub(r'[\#《》【】""""''()（）\[\]!！]', '', t)
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
            short_title = re.sub(r'[\#《》【】""""''()（）\[\]!！?？]', '', SHORT_TITLE_OVERRIDE).strip()[:16]
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
        raw = re.sub(r'[《》""""''【】\[\]()（）!?！？#。，、；：\-—…]', '', raw)
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
                            f"这是一张抽卡黄历视频的分镜图（实体卡片样式，金/朱砂边 + 卡名 + 中央插画）。\n"
                            f"对应台词：\"{scene['text']}\"\n\n"
                            f"请保守宽容地判断这张图是否有以下两类**严重**异常：\n"
                            "1. 文字明显错误：图里渲染的中文字/数字/日期严重错乱（出现伪汉字、不存在的成语、错字明显）\n"
                            "2. 内容严重偏离：图主体物件和台词主题完全无关（如台词说'忌动土'但画了红喜字喜庆场景）\n\n"
                            "宽容原则：色调差异、角度差异、风格细微差异都算正常，不要标记。\n"
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
                _wait_image_submit_slot(f"黄历封面候选 {idx+1}")
                r = req_post("/generation/text-to-image", {
                    "model": _m,
                    "prompt": prompt,
                    "aspect_ratio": _ar,
                    "image_number": 1,
                    **_extra,
                }, timeout=30)
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
            "Composition feels like an onsite observer standing just inside the scene, with foreground document edge or doorway framing, not a reporter cover. "
            if ADSD_ONSITE_POV_MODE else ""
        )
        cover_prompt = (
            f'3:4 vertical Chinese historical dialogue-drama cover for a video account, fully model-rendered typography. '
            f'{_tone_aesthetic}. One to four historical onsite characters from the actual topic era appear according to the script structure; active discussion or solemn testimony, side profiles or three-quarter views, no modern reporter, no TV host, no microphone, no mouth-closeup lip-sync pressure. '
            f'{pov_cover}Background: historically accurate location, period documents and objects directly tied to the topic, sepia ink-wash watercolor mixed with historical realism. '
            f'Top edge centered: dark-charcoal rounded pill with white Chinese "中华万年历". '
            f'Top-right: compact PANTONE swatch, English/Pantone only. '
            f'Center upper-middle: main title "{short_title}" in heavy-bold Chinese Song-ti serif, deep ink with cream outline, exactly once. '
            f'{subtitle_rule} '
            f'Bottom center: small warm sepia brush note "{_bottom_note}" flanked by two red seal dots, exactly once. '
            f'Dialogue clue in illustration: onsite character or characters clearly appear to be discussing or testifying about period documents or objects; visual anchor from script: {dialogue_hint}. '
            f'Strict text rule: render only these Chinese text blocks, no random signs, no duplicated title, no mirrored text, no extra subtitles in the illustration. '
            f'Every Chinese character sharp and complete, 8% safe margin, no watermark, no modern devices, no microphones, no livestream.'
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


def step10_deliver(final_path: str, topic: str, script: list[dict]):
    if ADS_DIALOGUE_MODE:
        delivery_qa = _write_adsd_delivery_qa(final_path)
        if delivery_qa and not delivery_qa.get("pass"):
            issues = "\n".join(f"• {x}" for x in delivery_qa.get("issues", [])[:8])
            tg(
                f"🛑 {ADSD_MODE_NAME} 发布已阻断：QA 未通过\n\n"
                f"{issues}\n\n"
                f"成片已保留在本地：{final_path}\n"
                f"QA：{OUTPUT_DIR / 'delivery_qa.json'}"
            )
            log(f"{ADSD_MODE_NAME} delivery QA blocked: {delivery_qa.get('issues')}")
            return
        if delivery_qa:
            tg(f"✅ {ADSD_MODE_NAME} 发布门禁通过：字幕/口型/ASR/音画同步 QA OK")

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
    tg(f"🎨 正在生成主题专属封面（{_style_tag}）...")
    cover_path = _generate_cover_image(topic, short_title, script)
    if cover_path:
        try:
            cover_send_path = _prepare_tg_photo(cover_path)
            with open(cover_send_path, "rb") as img_f:
                requests.post(
                    f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendPhoto",
                    data={
                        "chat_id": TG_CHAT_ID,
                        "caption": (
                            f"🖼 专属封面（建议叠标题：{short_title}）\n"
                            f"{_style_tag}"
                        ),
                    },
                    files={"photo": img_f},
                    timeout=30,
                )
        except Exception as e:
            log(f"专属封面发送失败: {e}")
    else:
        # 封面兜底：只有接口明确 failed 才叫失败；timeout 只是后台未及时完成。
        if COVER_LAST_REASON == "timeout":
            tg("⚠️ 专属封面仍在生成但已超过等待上限，先使用首张分镜图兜底；封面任务可能稍后在后台完成")
        else:
            tg(f"⚠️ 专属封面生成未完成（reason={COVER_LAST_REASON or 'unknown'}），使用首张分镜图兜底")
        fallback = str(OUTPUT_DIR / "img_0.jpg")
        try:
            fallback_send_path = _prepare_tg_photo(fallback)
            with open(fallback_send_path, "rb") as img_f:
                requests.post(
                    f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendPhoto",
                    data={"chat_id": TG_CHAT_ID, "caption": "🖼 封面（兜底 · 首张分镜）"},
                    files={"photo": img_f},
                    timeout=30,
                )
        except Exception as e:
            log(f"兜底封面发送失败: {e}")

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

    # ── 尝试 1：requests（timeout 放大到 600s）──
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
        if attempt < 1:
            time.sleep(5)

    # ── 尝试 2：curl fallback（更稳定，不受 httpx/urllib3 限制）──
    if not video_ok:
        tg("⚠️ requests 上传失败，切换 curl 重试...")
        for attempt in range(3):
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
                    break
                else:
                    log(f"curl 上传失败（第 {attempt+1} 次），stdout: {result.stdout[:200]}")
            except Exception as e:
                log(f"curl 异常（第 {attempt+1} 次）：{type(e).__name__}: {e}")
            if attempt < 2:
                time.sleep(10)

    if video_ok:
        tg("✅ 全流程完成！")
    else:
        tg(f"❌ 视频上传全部失败（requests+curl），文件在：{final_path}\n社媒文案已发送")


# ── 主流程 ───────────────────────────────────────────────────────────────────
def main():
    topic = TOPIC
    log(f"开始处理：{topic}")
    log(f"输出目录：{OUTPUT_DIR}")

    t_start = time.time()
    timings = {}

    try:
        t = time.time(); script, spk_id, spk_name = step1_script(topic);       timings["剧本+制片人准则+画面提示词+音色"] = time.time() - t
        if NO_VOICE:
            t = time.time()
            # 生成静音轨占位：时长按中文 3 字/秒 估算；min 20s（避免太短），cap 300s
            total_chars = sum(len(s["text"]) for s in script)
            est_dur = max(20.0, min(300.0, total_chars / 3.0 + len(script) * 0.5))  # 每句留 0.5s 间隔
            voice_path = str(OUTPUT_DIR / "silent_voice.mp3")
            subprocess.run([
                "ffmpeg", "-y", "-f", "lavfi",
                "-i", f"anullsrc=channel_layout=mono:sample_rate=44100",
                "-t", f"{est_dur}",
                "-c:a", "libmp3lame", "-b:a", "64k",
                voice_path,
            ], capture_output=True, timeout=30, check=True)
            tg(f"🔇 无配音模式：已生成 {est_dur:.1f}s 静音轨（{total_chars} 字 ÷ 3/s + 间隔）")
            timings["静音轨生成"] = time.time() - t
        else:
            if ADS_DIALOGUE_MODE:
                t = time.time(); voice_path = step2_dialogue_voice(script); timings["ADSD TTS 音轨+ASR"] = time.time() - t
            else:
                t = time.time(); voice_path = step2_master_voice(script, spk_id, spk_name); timings["Podcast 音轨"] = time.time() - t
        t = time.time(); script     = step345_timeline(script, voice_path);   timings["时间轴计算"] = time.time() - t
        t = time.time(); bgm_path   = step6_parallel(script, topic);          timings["图片+BGM 并发"] = time.time() - t
        if ADS_DIALOGUE_MODE and ADSD_LIP_SYNC_EXPERIMENT:
            t = time.time(); step66_adsd_lip_sync(script);                    timings["ADSD 口型同步"] = time.time() - t
        elif WITH_MOTION:
            t = time.time(); step65_motion(script);                            timings["动态化 (WERYDANCE)"] = time.time() - t
        t = time.time(); raw_path   = step7_concat(script);                   timings["视频拼接"] = time.time() - t
        t = time.time(); ass_path   = step8_subtitles(script);                timings["字幕生成"] = time.time() - t
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
