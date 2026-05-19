#!/usr/bin/env python3
"""批量从 YouTube/Bilibili/TikTok 抽音色入库。

输入: candidate JSON 文件 — 每条:
  {
    "url": "https://www.youtube.com/watch?v=...",
    "voice_id": "external_xxx_001",        # 主键，不可重复
    "display_name": "XXX 候选音色",
    "identified_person": "真名 / 角色",
    "gender": "male" | "female",
    "age_style": "young_adult|middle_aged|elderly|...",
    "tone_tags": ["..."],
    "scene_tags": ["..."],
    "accent": "mandarin|cantonese|...",
    "high_risk_public_figure": false,      # 默认 false；政治/争议人物 true
    "ref_offsets": [0, 60, 120, 180]       # 切片起点（秒），默认 [0,30,60,90]
  }

流程: yt-dlp → ffmpeg 抽 mp3 → whisper 转录（可选） → 切 4×9s ref → sha256 → 注册
不推 TG (避免刷屏)。注册时标 qa_status="auto_extracted_pending_human_review"。

完成后只发 1 条 TG 总结。
"""
import json
import hashlib
import os
import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime
import urllib.request

ROOT = Path(__file__).resolve().parent.parent
VOICE_ASSETS_JSON = ROOT / "voice_assets" / "voice_assets.json"
REFS_DIR = ROOT / "voice_assets" / "references"
TMP_DIR = Path("/tmp/bulk_voice_extract")
TMP_DIR.mkdir(exist_ok=True)


def log(msg: str) -> None:
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


def load_assets() -> dict:
    if not VOICE_ASSETS_JSON.exists():
        return {"schema": "adr_voice_assets_v1", "assets": []}
    return json.loads(VOICE_ASSETS_JSON.read_text(encoding="utf-8"))


def save_assets(data: dict) -> None:
    VOICE_ASSETS_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def voice_exists(data: dict, voice_id: str) -> bool:
    return any(a.get("voice_id") == voice_id for a in data.get("assets", []))


def yt_dlp_download(url: str, out_path: Path, max_attempts: int = 2) -> bool:
    """下载视频（用最小 size 格式，因为只要 audio）"""
    for attempt in range(max_attempts):
        try:
            # 选最小 h264 / 或者直接 bestaudio
            cmd = [
                "yt-dlp",
                "--no-warnings",
                "-q",
                "-f", "bestaudio/best",
                "--no-playlist",
                "-o", str(out_path),
                url,
            ]
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if r.returncode == 0 and out_path.exists() and out_path.stat().st_size > 100_000:
                return True
            log(f"  yt-dlp attempt {attempt+1} 失败: rc={r.returncode} stderr[:200]={r.stderr[:200]}")
        except Exception as e:
            log(f"  yt-dlp attempt {attempt+1} 异常: {e}")
        time.sleep(3)
    return False


def extract_mp3(src: Path, out_mp3: Path) -> bool:
    try:
        subprocess.run(
            ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
             "-i", str(src), "-vn", "-ac", "1", "-ar", "24000",
             str(out_mp3)],
            check=True, timeout=120,
        )
        return out_mp3.exists() and out_mp3.stat().st_size > 10_000
    except Exception as e:
        log(f"  ffmpeg 抽音失败: {e}")
        return False


def get_duration(path: Path) -> float:
    try:
        out = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=nw=1:nokey=1", str(path)],
            capture_output=True, text=True, timeout=15,
        ).stdout.strip()
        return float(out) if out else 0.0
    except Exception:
        return 0.0


def cut_ref(src: Path, out_path: Path, start: float, dur: float = 9.0) -> bool:
    try:
        subprocess.run(
            ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
             "-ss", str(start), "-t", str(dur),
             "-i", str(src), "-vn", "-ac", "1", "-ar", "24000",
             str(out_path)],
            check=True, timeout=60,
        )
        return out_path.exists() and out_path.stat().st_size > 5_000
    except Exception as e:
        log(f"  cut@{start}s 失败: {e}")
        return False


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def process_one(entry: dict, data: dict) -> tuple[bool, str]:
    """处理单条 candidate。返回 (success, reason)"""
    vid = entry.get("voice_id", "")
    url = entry.get("url", "")
    if not vid or not url:
        return False, "missing_voice_id_or_url"
    if voice_exists(data, vid):
        return False, "voice_id_already_exists"

    log(f"▶ {vid}")
    log(f"  source: {url}")

    # 1) yt-dlp 下载
    src_raw = TMP_DIR / f"{vid}_raw.mp4"
    if not yt_dlp_download(url, src_raw):
        return False, "download_failed"

    # 2) 抽 mp3
    src_mp3 = TMP_DIR / f"{vid}.mp3"
    if not extract_mp3(src_raw, src_mp3):
        return False, "mp3_extract_failed"
    total_dur = get_duration(src_mp3)
    log(f"  source duration: {total_dur:.1f}s")
    if total_dur < 30:
        return False, f"source_too_short_{total_dur:.1f}s"

    # 3) 切 4 个 ref（offsets 来自 entry 或默认 [10, 30, 60, 90]）
    offsets = entry.get("ref_offsets", [10, 30, 60, 90])
    # 截 offsets 在源时长范围内
    offsets = [o for o in offsets if o + 9 <= total_dur]
    if not offsets:
        # 实在太短，用 0
        offsets = [max(0, total_dur - 9 - 1)]

    refs_subdir = REFS_DIR / vid.replace("external_", "")
    refs_subdir.mkdir(parents=True, exist_ok=True)
    reference_audios = []
    for i, start in enumerate(offsets):
        ref_path = refs_subdir / f"ref_{i+1:02d}_{int(start):03d}s.wav"
        if cut_ref(src_mp3, ref_path, start):
            reference_audios.append({
                "path": str(ref_path.relative_to(ROOT)),
                "sha256": sha256_file(ref_path),
                "duration": 9.0,
                "source_start": float(start),
                "source_end": float(start) + 9.0,
                "variant": "auto_extracted_raw",
            })
        else:
            log(f"  ref cut at {start}s failed")

    if not reference_audios:
        return False, "no_refs_cut"

    # 4) 注册
    asset = {
        "voice_id": vid,
        "display_name": entry.get("display_name", vid),
        "identified_person": entry.get("identified_person", "未知"),
        "label_source": "bulk_auto_extract",
        "source_type": "youtube_bulk_extracted_candidate",
        "source_url": url,
        "source_duration": int(total_dur),
        "language": [entry.get("language", "zh-CN")],
        "accent": entry.get("accent", "mandarin"),
        "gender": entry.get("gender", "unknown"),
        "age_style": entry.get("age_style", ""),
        "tone_tags": entry.get("tone_tags", []),
        "scene_tags": entry.get("scene_tags", []),
        "audio_dub_ready": True,
        "license_status": "unverified_external_person_voice",
        "allowed_use": ["analysis", "internal_test"],
        "forbidden_use": ["commercial", "public_release", "impersonation"],
        "rights_review_required": True,
        "high_risk_public_figure": entry.get("high_risk_public_figure", False),
        "qa_status": "auto_extracted_pending_human_review",
        "quality_flags": entry.get("quality_flags", ["bulk_auto_extracted", "not_speaker_diarized"]),
        "reference_audios": reference_audios,
        "extracted_at": datetime.now().isoformat(timespec="seconds"),
    }
    data["assets"].append(asset)
    save_assets(data)
    log(f"  ✓ registered with {len(reference_audios)} refs")

    # 清理临时
    try:
        src_raw.unlink(missing_ok=True)
        src_mp3.unlink(missing_ok=True)
    except Exception:
        pass

    return True, "ok"


def push_summary_tg(success: list[str], failed: list[tuple[str, str]], skipped: list[str]) -> None:
    """完成后推 1 条 TG 总结"""
    try:
        import requests
        bot = os.environ.get("TELEGRAM_TOKEN") or os.environ.get("TG_BOT_TOKEN")
        chat = os.environ.get("OWNER_CHAT_ID") or os.environ.get("TG_CHAT_ID")
        if not bot or not chat:
            log("TG 总结跳过 (缺 env)")
            return
        m_ok = sum(1 for vid in success if "_male_" in vid or any(x in vid for x in ["luo_", "huang_", "xu_", "lin_"]))
        text = (
            f"🎙 bulk_voice_extract 完成\n"
            f"\n"
            f"✓ 成功: {len(success)}\n"
            f"✗ 失败: {len(failed)}\n"
            f"⏭ 跳过: {len(skipped)}\n"
            f"\n"
            f"失败原因 (前 10):\n"
        )
        for vid, reason in failed[:10]:
            text += f"  - {vid}: {reason}\n"
        requests.post(
            f"https://api.telegram.org/bot{bot}/sendMessage",
            data={"chat_id": chat, "text": text, "disable_notification": "false"},
            timeout=30,
        )
    except Exception as e:
        log(f"TG 总结推送失败 (不致命): {e}")


def main() -> None:
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} candidates.json")
        sys.exit(1)
    cand_path = Path(sys.argv[1])
    if not cand_path.exists():
        print(f"candidates 文件不存在: {cand_path}")
        sys.exit(1)
    candidates = json.loads(cand_path.read_text(encoding="utf-8"))
    log(f"加载 {len(candidates)} 条 candidates")

    data = load_assets()
    log(f"current voice library: {len(data['assets'])} 个 assets")

    success: list[str] = []
    failed: list[tuple[str, str]] = []
    skipped: list[str] = []

    for i, entry in enumerate(candidates, start=1):
        vid = entry.get("voice_id", "?")
        log(f"\n=== [{i}/{len(candidates)}] {vid} ===")
        if voice_exists(data, vid):
            log(f"  skip: 已注册")
            skipped.append(vid)
            continue
        try:
            ok, reason = process_one(entry, data)
            if ok:
                success.append(vid)
            else:
                failed.append((vid, reason))
                log(f"  ✗ failed: {reason}")
        except Exception as e:
            failed.append((vid, f"exception: {e}"))
            log(f"  ✗ exception: {e}")

    # 最终保存
    save_assets(data)
    log(f"\n=== DONE ===")
    log(f"success: {len(success)}  failed: {len(failed)}  skipped: {len(skipped)}")
    log(f"library now: {len(data['assets'])} assets")

    push_summary_tg(success, failed, skipped)


if __name__ == "__main__":
    main()
