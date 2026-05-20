#!/usr/bin/env python3
"""WERYDANCE almighty-reference-to-video Spike 探针工具

不改 ADR 主代码，直接调 weryai API 试探：
  1. audio_ref 长度对输出的影响 (9s vs 18s vs 27s)
  2. prompt 含多 turn dialogue 时的输出节奏
  3. 12-panel grid 当 multi-ref 的视觉行为

每个 spike 输出独立 mp4 文件 + 推 TG。
"""
import json
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# 复用 telegram-claude-bot/.env 加载 env vars
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

_real_args = list(sys.argv[1:])  # 先保存真实 spike args，等 ADR import 完恢复
sys.path.insert(0, str(ROOT))
sys.argv = ["spike_almighty.py", "spike", "h", "--adsd"]
import run_adr_v8 as adr  # noqa
sys.argv = ["spike_almighty.py"] + _real_args  # 恢复给 spike main() 用

OUT_DIR = Path("/tmp/spike_almighty")
OUT_DIR.mkdir(exist_ok=True)


def submit_almighty(images: list[str], audio: str | None, prompt: str, duration: int,
                    generate_audio: str = "true", aspect_ratio: str = "16:9") -> str | None:
    """提交一个 almighty 任务，返回 task_id。"""
    image_urls = [adr._upload_to_weryai(p) for p in images]
    audio_url = adr._upload_to_weryai(audio) if audio else None
    payload = {
        "model": "WERYDANCE_2_0",
        "images": image_urls,
        "prompt": prompt,
        "duration": duration,
        "aspect_ratio": aspect_ratio,
        "resolution": "720p",
        "generate_audio": generate_audio,
    }
    if audio_url:
        payload["audios"] = [audio_url]
    print(f"  submitting almighty: {len(image_urls)} images, audio={'yes' if audio else 'no'}, duration={duration}s")
    r = adr.req_post("/generation/almighty-reference-to-video", payload, timeout=30)
    task_id = r.get("data", {}).get("task_id") or (r.get("data", {}).get("task_ids") or [None])[0]
    if not task_id:
        print(f"  submit failed: {r}")
        return None
    print(f"  task_id={task_id}")
    return task_id


def poll_and_download(task_id: str, out_path: Path, max_iterations: int = 120) -> bool:
    """轮询任务直到 succeed 或 timeout，下载视频。"""
    base = "https://api.weryai.com/v1"
    headers = {"Authorization": f"Bearer {os.environ['WERYAI_API_KEY']}"}
    import requests
    for i in range(max_iterations):
        try:
            r = requests.get(f"{base}/generation/{task_id}/status", headers=headers, timeout=15).json()
        except Exception as e:
            print(f"  poll #{i+1}: exception {e}")
            time.sleep(5)
            continue
        st = r.get("data", {}).get("task_status", "")
        if i % 6 == 0:
            print(f"  poll #{i+1}: {st}")
        if st == "succeed":
            urls = r.get("data", {}).get("videos") or r.get("data", {}).get("video_urls") or []
            if not urls:
                urls = [r.get("data", {}).get("video_url")] if r.get("data", {}).get("video_url") else []
            if not urls:
                print(f"  no video url in response: {r}")
                return False
            urllib.request.urlretrieve(urls[0], out_path)
            print(f"  downloaded: {out_path}")
            return True
        if st == "failed":
            print(f"  failed: {r}")
            return False
        time.sleep(5)
    print(f"  timeout")
    return False


def push_tg(video_path: Path, caption: str) -> None:
    """curl 推到 TG。"""
    token = os.environ.get("TG_BOT_TOKEN") or os.environ.get("TELEGRAM_TOKEN")
    chat = os.environ.get("TG_CHAT_ID") or os.environ.get("OWNER_CHAT_ID")
    if not token or not chat:
        print(f"  TG env missing, skip push")
        return
    cmd = [
        "curl", "-s", "--max-time", "600",
        "-F", f"chat_id={chat}",
        "-F", f"caption={caption}",
        "-F", f"video=@{video_path}",
        f"https://api.telegram.org/bot{token}/sendVideo",
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=660)
    if '"ok":true' in r.stdout:
        print(f"  TG push 成功")
    else:
        print(f"  TG push 失败 stdout={r.stdout[:200]}")


def run_spec(spec: dict, out_path: Path) -> bool:
    """跑一个实验 spec。"""
    print(f"\n=== {spec['name']} ===")
    print(f"  {spec.get('desc', '')}")
    task_id = submit_almighty(
        images=spec["images"],
        audio=spec.get("audio"),
        prompt=spec["prompt"],
        duration=spec["duration"],
        generate_audio=spec.get("generate_audio", "true"),
        aspect_ratio=spec.get("aspect_ratio", "16:9"),
    )
    if not task_id:
        return False
    ok = poll_and_download(task_id, out_path)
    if ok:
        push_tg(out_path, f"Spike {spec['name']} | {spec.get('desc', '')}")
    return ok


# ── Spike 实验 spec 定义 ──────────────────────────────────────────────────────
# 用现成 voice_asset 和 panel 测试

VOICE_ASSETS = ROOT / "voice_assets" / "references"


def make_audio_concat(srcs: list[str], out_path: Path) -> Path:
    """ffmpeg concat 多个 wav 拼成长 audio。"""
    list_file = out_path.with_suffix(".concat.txt")
    list_file.write_text("\n".join(f"file '{s}'" for s in srcs), encoding="utf-8")
    subprocess.run(
        ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
         "-f", "concat", "-safe", "0", "-i", str(list_file),
         "-c:a", "pcm_s16le", "-ar", "44100", "-ac", "1",
         str(out_path)],
        check=True, timeout=60,
    )
    return out_path


def pick_voice_asset_ref() -> str:
    """挑一个稳定的 voice_asset reference (绫璟道人 ref_01)。"""
    candidates = [
        VOICE_ASSETS / "mushenji_lingjing" / "ref_01_010s.wav",
        VOICE_ASSETS / "xu_zhiyuan_xyma_001" / "ref_01_010s.wav",
    ]
    for c in candidates:
        if c.exists():
            return str(c)
    # 兜底：随便找一个
    for f in VOICE_ASSETS.rglob("ref_01_*.wav"):
        return str(f)
    raise RuntimeError("no voice_asset reference found")


def pick_test_panel() -> str:
    """挑一张已有 panel 当 image_ref。从最近 ADR run 找。"""
    candidates = sorted(Path("/tmp").glob("adr_v8_*/img_*.jpg"))
    if not candidates:
        candidates = sorted(Path("/tmp").glob("adr_v8_*/seg_*.mp4"))
    if not candidates:
        raise RuntimeError("no ADR panel found in /tmp/adr_v8_*")
    return str(candidates[-1])


def spike_1():
    """audio_ref 长度对输出影响：9s vs 18s vs 27s"""
    voice = pick_voice_asset_ref()
    panel = pick_test_panel()
    base_audio = Path(voice)
    # 18s = 2 × 9s，27s = 3 × 9s（拼接同一段）
    audio_18s = make_audio_concat([str(base_audio), str(base_audio)], OUT_DIR / "audio_18s.wav")
    audio_27s = make_audio_concat([str(base_audio), str(base_audio), str(base_audio)], OUT_DIR / "audio_27s.wav")

    prompt = (
        "Cinematic documentary scene. Generate Mandarin speech with the speaker saying exactly: "
        "「奉天子以令不臣」. Keep visible mouth, stable face, natural jaw motion."
    )

    specs = [
        {"name": "1A_audio_9s", "desc": "audio_ref=9s 标准长度",
         "images": [panel], "audio": str(base_audio), "prompt": prompt, "duration": 5},
        {"name": "1B_audio_18s", "desc": "audio_ref=18s 拼接",
         "images": [panel], "audio": str(audio_18s), "prompt": prompt, "duration": 5},
        {"name": "1C_audio_27s", "desc": "audio_ref=27s 拼接",
         "images": [panel], "audio": str(audio_27s), "prompt": prompt, "duration": 5},
    ]
    for spec in specs:
        run_spec(spec, OUT_DIR / f"{spec['name']}.mp4")


def spike_2():
    """prompt 多 turn dialogue 合并：1 vs 2 vs 3 句"""
    voice = pick_voice_asset_ref()
    panel = pick_test_panel()
    dialogues = [
        ("2A_dialogue_1turn",  "奉天子以令不臣", "8 字单 turn 标准"),
        ("2B_dialogue_2turn",  "奉天子以令不臣。从此孤不再只是将军", "2 turn 合并 16 字"),
        ("2C_dialogue_3turn",  "奉天子以令不臣。从此孤不再只是将军。孤是大汉司空", "3 turn 合并 24 字"),
    ]
    for name, dialogue, desc in dialogues:
        prompt = (
            "Cinematic documentary scene. Generate Mandarin speech speaking exactly: "
            f"「{dialogue}」. Use the uploaded audio as voice timbre reference only. "
            "Keep mouth visible, natural speaking pace, allow natural pauses between sentences."
        )
        spec = {
            "name": name, "desc": desc,
            "images": [panel], "audio": voice, "prompt": prompt,
            "duration": min(15, max(5, len(dialogue) // 6 + 2)),
        }
        run_spec(spec, OUT_DIR / f"{spec['name']}.mp4")


def spike_3():
    """12-panel grid 当 multi-ref：1 single vs 4 panels vs 12-panel grid"""
    voice = pick_voice_asset_ref()
    panel = pick_test_panel()
    # 从近期 ADR 找 storyboard_grid
    grids = sorted(Path("/tmp").glob("adr_v8_*/storyboard_grid_*.png"))
    if not grids:
        print("找不到 storyboard_grid_*.png，spike 3 跳过")
        return
    grid_full = str(grids[-1])

    # 找同 dir 切出的 panel
    grid_dir = Path(grid_full).parent
    panels_dir = sorted(grid_dir.glob("img_*.jpg"))[:5]
    panels_4 = [str(p) for p in panels_dir[:4]] if len(panels_dir) >= 4 else [panel] * 4

    prompt = (
        "Cinematic documentary continuous shot. "
        "Use the uploaded references as visual keyframes to drive a smooth 10-second sequence "
        "with natural camera motion and atmosphere. "
        "Speaker says: 「奉天子以令不臣」 in clear Mandarin."
    )

    specs = [
        {"name": "3A_single_panel", "desc": "1 张单 panel (baseline)",
         "images": [panel], "audio": voice, "prompt": prompt, "duration": 10},
        {"name": "3B_4panels", "desc": "4 张分散 panel (multi-ref 时间序列)",
         "images": panels_4, "audio": voice, "prompt": prompt, "duration": 10},
        {"name": "3C_grid_full", "desc": "整张 12-panel grid (空间序列)",
         "images": [grid_full], "audio": voice, "prompt": prompt, "duration": 10},
    ]
    for spec in specs:
        run_spec(spec, OUT_DIR / f"{spec['name']}.mp4")


def generate_labeled_grid(out_path: Path) -> str | None:
    """用 GPT_IMAGE_2 生成带文字标签的 4×3 人设融合 grid，返回 grid 文件路径。"""
    print("\n[5A] 生成带标签 12-panel grid...")
    grid_prompt = (
        "Create a 4 columns × 3 rows reference sheet (16:9), 12 separate cells with thin gold borders. "
        "Subject: a Chinese late Han era warlord, mid-40s, beard, sharp eyes (CaoCao archetype). "
        "Each cell must include a SMALL, CRISP, READABLE Latin-letter text label rendered in the upper-left corner of that cell "
        "(black serif, white outline, about 4% of cell height). Layout:\n"
        "Row 1: cell 1 'CaoCao | armor | speak' (medium shot, battle armor, mid-sentence, mouth visible). "
        "cell 2 'CaoCao | armor | command' (raising arm, commanding troops). "
        "cell 3 'CaoCao | court | speak' (court robe, palace pillar background). "
        "cell 4 'CaoCao | court | contemplate' (court robe, eyes downcast).\n"
        "Row 2: cell 5 'CaoCao | private | contemplate' (private silk wear, lit by oil lamp). "
        "cell 6 'CaoCao | private | write' (writing on bamboo scroll). "
        "cell 7 'CaoCao | armor | ride' (on horse, dust). "
        "cell 8 'CaoCao | armor | sword' (sword raised, battle).\n"
        "Row 3: cell 9 'scene | battlefield' (wide shot, banners, no faces). "
        "cell 10 'scene | palace' (interior, pillars, dim light). "
        "cell 11 'scene | night camp' (campfire, tents). "
        "cell 12 'prop | bamboo scroll' (close-up of scroll on table).\n"
        "Consistent character identity, costume continuity within each label group. "
        "Each cell is photoreal cinematic documentary style. "
        "Labels must be flat, sharp, unambiguous — they are functional metadata."
    )
    payload = {
        "model": "GPT_IMAGE_2",
        "prompt": grid_prompt,
        "aspect_ratio": "16:9(4k)",
        "image_number": 1,
        "quality": "high",
    }
    payload = adr._inject_image2_quality_suffix(payload)
    try:
        r = adr.submit_text_to_image(payload, "spike5 labeled grid", timeout=60)
    except Exception as e:
        print(f"  GPT_IMAGE_2 提交失败：{e}")
        return None
    task_id = r.get("data", {}).get("task_id") or (r.get("data", {}).get("task_ids") or [None])[0]
    if not task_id:
        print(f"  GPT_IMAGE_2 无 task_id: {r}")
        return None
    print(f"  GPT_IMAGE_2 task_id={task_id}, polling...")
    try:
        data = adr.poll_storyboard_task(task_id, "spike5 grid", 300)
    except Exception as e:
        print(f"  poll 失败：{e}")
        return None
    urls = adr._extract_img_urls(data) if hasattr(adr, "_extract_img_urls") else (data.get("images") or [])
    if isinstance(urls, list) and urls and isinstance(urls[0], dict):
        urls = [u.get("url") for u in urls if u.get("url")]
    if not urls:
        print(f"  no image url: {data}")
        return None
    urllib.request.urlretrieve(urls[0], out_path)
    print(f"  downloaded labeled grid: {out_path}")
    # 推 TG 让人眼检查标签是否清晰
    token = os.environ.get("TG_BOT_TOKEN") or os.environ.get("TELEGRAM_TOKEN")
    chat = os.environ.get("TG_CHAT_ID") or os.environ.get("OWNER_CHAT_ID")
    if token and chat:
        subprocess.run([
            "curl", "-s", "--max-time", "120",
            "-F", f"chat_id={chat}",
            "-F", "caption=Spike 5A 带标签人设融合 grid（人眼验证标签可读性）",
            "-F", f"photo=@{out_path}",
            f"https://api.telegram.org/bot{token}/sendPhoto",
        ], capture_output=True, text=True, timeout=130)
    return str(out_path)


def generate_labeled_grid_zh(out_path: Path) -> str | None:
    """中文标签人设融合 grid（spike 5b）。"""
    print("\n[5b-A] 生成中文标签 12-panel grid...")
    grid_prompt = (
        "生成 4 列 × 3 行 参考图（16:9），12 个独立 cell，细金色边框。\n"
        "主体：东汉末年大军阀，约 45 岁，蓄须，眼神锐利（曹操原型）。\n"
        "每个 cell 左上角必须有清晰可读的中文文字标签（黑色衬线字体，白色描边，约 cell 高度 4%）。\n"
        "布局：\n"
        "第 1 行：cell 1「曹操｜战袍｜说话」（中景，战甲，开口讲话，嘴部可见）；"
        "cell 2「曹操｜战袍｜发令」（举臂下令，指挥兵卒）；"
        "cell 3「曹操｜朝服｜说话」（朝服，宫殿柱旁）；"
        "cell 4「曹操｜朝服｜沉思」（朝服，低头沉思）。\n"
        "第 2 行：cell 5「曹操｜私服｜沉思」（私服丝绸便装，油灯光照）；"
        "cell 6「曹操｜私服｜书写」（在竹简上书写）；"
        "cell 7「曹操｜战袍｜骑马」（骑马，尘土飞扬）；"
        "cell 8「曹操｜战袍｜持剑」（举剑，战斗场面）。\n"
        "第 3 行：cell 9「场景｜战场」（远景，旗帜，无人脸特写）；"
        "cell 10「场景｜宫殿」（室内，柱子，昏暗）；"
        "cell 11「场景｜夜营」（营火，帐篷）；"
        "cell 12「道具｜竹简」（桌上竹简特写）。\n"
        "整体要求：同角色身份贯穿，同标签组服装连续；每个 cell 是纪录片风格电影质感；"
        "中文标签必须清晰锐利、不变形、明确可读——这是功能性元数据。"
    )
    payload = {
        "model": "GPT_IMAGE_2",
        "prompt": grid_prompt,
        "aspect_ratio": "16:9(4k)",
        "image_number": 1,
        "quality": "high",
    }
    payload = adr._inject_image2_quality_suffix(payload)
    try:
        r = adr.submit_text_to_image(payload, "spike5b labeled grid zh", timeout=60)
    except Exception as e:
        print(f"  GPT_IMAGE_2 提交失败：{e}")
        return None
    task_id = r.get("data", {}).get("task_id") or (r.get("data", {}).get("task_ids") or [None])[0]
    if not task_id:
        print(f"  no task_id: {r}")
        return None
    print(f"  GPT_IMAGE_2 task_id={task_id}, polling...")
    data = adr.poll_storyboard_task(task_id, "spike5b grid zh", 300)
    urls = adr._extract_img_urls(data) if hasattr(adr, "_extract_img_urls") else (data.get("images") or [])
    if isinstance(urls, list) and urls and isinstance(urls[0], dict):
        urls = [u.get("url") for u in urls if u.get("url")]
    if not urls:
        print(f"  no image url: {data}")
        return None
    urllib.request.urlretrieve(urls[0], out_path)
    print(f"  downloaded zh labeled grid: {out_path}")
    # 压 JPEG 推 TG (PNG 太大 TG 拒)
    jpg_path = str(out_path).replace(".png", ".jpg")
    subprocess.run(["ffmpeg", "-y", "-i", str(out_path), "-qscale:v", "4", jpg_path],
                   capture_output=True, timeout=60)
    token = os.environ.get("TG_BOT_TOKEN") or os.environ.get("TELEGRAM_TOKEN")
    chat = os.environ.get("TG_CHAT_ID") or os.environ.get("OWNER_CHAT_ID")
    if token and chat:
        subprocess.run([
            "curl", "-s", "--max-time", "120",
            "-F", f"chat_id={chat}",
            "-F", "caption=Spike 5b-A 中文标签人设融合 grid（人眼验证中文标签可读性）",
            "-F", f"photo=@{jpg_path}",
            f"https://api.telegram.org/bot{token}/sendPhoto",
        ], capture_output=True, text=True, timeout=130)
    return str(out_path)


def spike_5b():
    """中文标签人设符 grid 召唤对照 spike 5 (英文)。"""
    voice = pick_voice_asset_ref()
    labeled_grid = OUT_DIR / "5b_labeled_grid_zh.png"
    if not labeled_grid.exists():
        if not generate_labeled_grid_zh(labeled_grid):
            print("  5b-A 中文标签 grid 生成失败，spike 5b 中止")
            return
    else:
        print(f"  reuse existing zh labeled grid: {labeled_grid}")

    # 5b-B 召唤「战袍｜说话」
    prompt_armor = (
        "纪录片场景。使用上传的参考图作为视觉指引——"
        "重点关注标记为「曹操｜战袍｜说话」的 panel（讲话中，身穿战甲，嘴部可见）。"
        "生成普通话语音，演讲者准确说出：「奉天子以令不臣」。"
        "上传的音频仅作为音色、语速、年龄感参考。"
        "嘴部可见，面部稳定，嘴型自然同步，符合真人节奏。"
    )
    # 5b-C 召唤「私服｜沉思」
    prompt_private = (
        "纪录片场景。使用上传的参考图作为视觉指引——"
        "重点关注标记为「曹操｜私服｜沉思」的 panel（私服丝绸便装，油灯光下沉思）。"
        "生成普通话语音，演讲者低声自语：「孤一生求贤若渴」。"
        "上传的音频仅作为音色、语速、年龄感参考。"
        "嘴部可见，柔和打光，嘴型自然同步。"
    )

    specs = [
        {"name": "5bB_zh_call_armor_speak", "desc": "中文召唤 战袍+说话",
         "images": [str(labeled_grid)], "audio": voice, "prompt": prompt_armor, "duration": 5},
        {"name": "5bC_zh_call_private_contemplate", "desc": "中文召唤 私服+沉思",
         "images": [str(labeled_grid)], "audio": voice, "prompt": prompt_private, "duration": 5},
    ]
    for spec in specs:
        run_spec(spec, OUT_DIR / f"{spec['name']}.mp4")


def spike_5():
    """标签人设融合 grid 验证：almighty 能否按 prompt 召唤 grid 内特定 panel？"""
    voice = pick_voice_asset_ref()
    labeled_grid = OUT_DIR / "5_labeled_grid.png"
    if not labeled_grid.exists():
        grid_path = generate_labeled_grid(labeled_grid)
        if not grid_path:
            print("  5A 标签 grid 生成失败，spike 5 中止")
            return
    else:
        print(f"  reuse existing labeled grid: {labeled_grid}")

    # 5B 召唤 "armor | speak"
    prompt_armor = (
        "Cinematic documentary scene. Use the uploaded grid as visual reference — "
        "FOCUS on the panel labeled 'CaoCao | armor | speak' (mid-sentence, battle armor). "
        "Generate Mandarin speech with the speaker saying exactly: 「奉天子以令不臣」. "
        "Use uploaded audio as voice timbre reference only. "
        "Visible mouth, stable face, natural lip sync, realistic human timing."
    )
    # 5C 召唤 "private | contemplate"
    prompt_private = (
        "Cinematic documentary scene. Use the uploaded grid as visual reference — "
        "FOCUS on the panel labeled 'CaoCao | private | contemplate' (private silk wear, oil lamp, contemplating). "
        "Generate Mandarin speech with the speaker quietly thinking aloud: 「孤一生求贤若渴」. "
        "Use uploaded audio as voice timbre reference only. "
        "Visible mouth, soft lighting, natural lip sync."
    )

    specs = [
        {"name": "5B_call_armor_speak", "desc": "召唤 armor+speak panel",
         "images": [str(labeled_grid)], "audio": voice, "prompt": prompt_armor, "duration": 5},
        {"name": "5C_call_private_contemplate", "desc": "召唤 private+contemplate panel",
         "images": [str(labeled_grid)], "audio": voice, "prompt": prompt_private, "duration": 5},
    ]
    for spec in specs:
        run_spec(spec, OUT_DIR / f"{spec['name']}.mp4")


def spike_4():
    """a_roll 整 grid 当 ref vs 切片对比：能否取代当前主路径切 panel？"""
    voice = pick_voice_asset_ref()
    grids = sorted(Path("/tmp").glob("adr_v8_*/storyboard_grid_*.png"))
    sheets = sorted(Path("/tmp").glob("adr_v8_*/character_sheet.png"))
    panels = sorted(Path("/tmp").glob("adr_v8_*/img_*.jpg"))
    if not grids or not sheets or not panels:
        print(f"缺素材: grid={len(grids)} sheet={len(sheets)} panel={len(panels)}, spike 4 跳过")
        return
    grid_full = str(grids[-1])
    sheet = str(sheets[-1])
    single_panel = str(panels[-1])

    dialogue = "奉天子以令不臣"
    prompt = (
        "Cinematic documentary scene with generated Mandarin speech. "
        "Use uploaded audio purely as voice timbre, pace, age impression reference. "
        "Use uploaded image references for identity, costume, era, lighting. "
        f"The speaker says exactly this Chinese line: 「{dialogue}」 and nothing else. "
        "Natural lip sync, visible mouth, stable face, realistic human timing."
    )

    specs = [
        {"name": "4A_single_panel_baseline", "desc": "a_roll baseline: single panel only",
         "images": [single_panel], "audio": voice, "prompt": prompt, "duration": 5},
        {"name": "4B_sheet_plus_panel", "desc": "a_roll: character_sheet + single panel (current main)",
         "images": [sheet, single_panel], "audio": voice, "prompt": prompt, "duration": 5},
        {"name": "4C_sheet_plus_full_grid", "desc": "a_roll: character_sheet + 整 12-panel grid (new)",
         "images": [sheet, grid_full], "audio": voice, "prompt": prompt, "duration": 5},
    ]
    for spec in specs:
        run_spec(spec, OUT_DIR / f"{spec['name']}.mp4")


def main():
    args = sys.argv[1:] if len(sys.argv) > 1 else ["all"]
    if "1" in args or "all" in args:
        print("\n#### SPIKE 1 · audio_ref 长度 ####")
        spike_1()
    if "2" in args or "all" in args:
        print("\n#### SPIKE 2 · 多 turn dialogue 合并 ####")
        spike_2()
    if "3" in args or "all" in args:
        print("\n#### SPIKE 3 · 12-panel grid multi-ref ####")
        spike_3()
    if "4" in args or "all" in args:
        print("\n#### SPIKE 4 · a_roll 整 grid 当 ref ####")
        spike_4()
    if "5" in args or "all" in args:
        print("\n#### SPIKE 5 · 英文标签人设融合 grid ####")
        spike_5()
    if "5b" in args or "all" in args:
        print("\n#### SPIKE 5b · 中文标签人设融合 grid ####")
        spike_5b()
    print(f"\n=== all spikes done. outputs in {OUT_DIR}/ ===")


if __name__ == "__main__":
    main()
