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
    print(f"\n=== all spikes done. outputs in {OUT_DIR}/ ===")


if __name__ == "__main__":
    main()
