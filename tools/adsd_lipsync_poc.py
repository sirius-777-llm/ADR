#!/usr/bin/env python3
"""ADSD lip-sync proof-of-concept runner.

This script intentionally lives outside the production ADR path. It probes one
small Werydance 2.0 image+audio request, downloads the generated clip, and
writes a QA record that can decide whether real lip-sync is ready to integrate.
"""

from __future__ import annotations

import argparse
import difflib
import json
import mimetypes
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime
from typing import Any
import urllib.request

import requests


BASE_URL = "https://api.weryai.com/v1"
POLL_INTERVAL = 5


def log(msg: str) -> None:
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


def run(cmd: list[str], timeout: int = 120) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, text=True, capture_output=True, check=True, timeout=timeout)


def ffprobe_duration(path: Path, stream_type: str | None = None) -> float | None:
    if stream_type:
        args = [
            "ffprobe", "-v", "error", "-select_streams", f"{stream_type}:0",
            "-show_entries", "stream=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(path),
        ]
    else:
        args = [
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", str(path),
        ]
    try:
        out = run(args, timeout=30).stdout.strip()
        return float(out) if out and out != "N/A" else None
    except Exception:
        return None


def has_audio_stream(path: Path) -> bool:
    try:
        out = run([
            "ffprobe", "-v", "error", "-select_streams", "a",
            "-show_entries", "stream=index", "-of", "csv=p=0", str(path),
        ], timeout=30).stdout.strip()
        return bool(out)
    except Exception:
        return False


def req_post(path: str, payload: dict[str, Any], api_key: str, timeout: int = 30) -> dict[str, Any]:
    r = requests.post(
        f"{BASE_URL}{path}",
        json=payload,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        timeout=timeout,
    )
    try:
        data = r.json()
    except Exception:
        data = {"success": False, "status_code": r.status_code, "text": r.text[:500]}
    if r.status_code >= 500:
        raise RuntimeError(f"{path} HTTP {r.status_code}: {json.dumps(data, ensure_ascii=False)[:500]}")
    return data


def req_get(path: str, api_key: str, timeout: int = 15) -> dict[str, Any]:
    r = requests.get(f"{BASE_URL}{path}", headers={"Authorization": f"Bearer {api_key}"}, timeout=timeout)
    return r.json()


def upload_file(path: Path, api_key: str) -> str:
    mime = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
    with path.open("rb") as f:
        r = requests.post(
            f"{BASE_URL}/generation/upload-file",
            headers={"Authorization": f"Bearer {api_key}"},
            files={"file": (path.name, f, mime)},
            timeout=(30, 180),
        )
    r.raise_for_status()
    data = r.json()
    urls = (data.get("data") or {}).get("object_url_list") or []
    if not urls:
        raise RuntimeError(f"upload-file 无 object_url_list: {json.dumps(data, ensure_ascii=False)[:500]}")
    return urls[0]


def extract_task_id(resp: dict[str, Any]) -> str | None:
    data = resp.get("data") or {}
    task_id = data.get("task_id")
    if task_id:
        return str(task_id)
    task_ids = data.get("task_ids")
    if isinstance(task_ids, list) and task_ids:
        return str(task_ids[0])
    return None


def extract_video_url(data: dict[str, Any]) -> str | None:
    candidates: list[Any] = [
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


def poll_task(task_id: str, api_key: str, max_wait: int) -> dict[str, Any]:
    polls = max(1, max_wait // POLL_INTERVAL)
    for i in range(polls):
        time.sleep(POLL_INTERVAL)
        resp = req_get(f"/generation/{task_id}/status", api_key)
        data = resp.get("data") or {}
        status = data.get("task_status") or data.get("content_status")
        if i == 0 or (i + 1) % 6 == 0 or status in ("succeed", "success", "failed", "fail", "canceled"):
            log(f"poll #{i+1}: status={status}")
        if status in ("succeed", "success"):
            return data
        if status in ("failed", "fail", "canceled"):
            raise RuntimeError(f"task failed: {json.dumps(data, ensure_ascii=False)[:800]}")
    raise RuntimeError(f"poll timeout after {max_wait}s: {task_id}")


def compact_zh(text: str) -> str:
    return re.sub(r"[\s，。！？、；：,.!?;:'\"“”‘’（）()《》【】\[\]\-—…·]", "", text or "")


def asr_audio(audio_path: Path, api_key: str, tg_token: str, tg_chat_id: str, out_dir: Path) -> dict[str, Any] | None:
    try:
        with audio_path.open("rb") as f:
            sent = requests.post(
                f"https://api.telegram.org/bot{tg_token}/sendAudio",
                data={"chat_id": tg_chat_id, "caption": "ADSD lip-sync PoC audio for ASR"},
                files={"audio": (audio_path.name, f, "audio/mpeg")},
                timeout=(30, 180),
            )
        sent.raise_for_status()
        file_id = ((sent.json().get("result") or {}).get("audio") or {}).get("file_id")
        if not file_id:
            raise RuntimeError("Telegram sendAudio 无 file_id")
        got = requests.get(
            f"https://api.telegram.org/bot{tg_token}/getFile",
            params={"file_id": file_id},
            timeout=30,
        )
        got.raise_for_status()
        file_path = (got.json().get("result") or {}).get("file_path")
        if not file_path:
            raise RuntimeError("Telegram getFile 无 file_path")
        audio_url = f"https://api.telegram.org/file/bot{tg_token}/{file_path}"
        started = req_post("/generation/speech-recognize", {"audio_url": audio_url, "language": "zh"}, api_key)
        task_id = extract_task_id(started)
        if not task_id:
            raise RuntimeError(f"speech-recognize 无 task_id: {json.dumps(started, ensure_ascii=False)[:500]}")
        data = poll_task(task_id, api_key, max_wait=240)
        (out_dir / "speech_recognize_result.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return data
    except Exception as exc:
        log(f"ASR skipped/failed: {exc}")
        return None


def latest_adsd_dir() -> Path:
    roots = sorted(Path("/private/tmp").glob("adr_v8_*"), key=lambda p: p.stat().st_mtime, reverse=True)
    for root in roots:
        if (root / "turn_timeline.json").exists() and (root / "img_0.jpg").exists():
            return root
    raise RuntimeError("没有找到可复用的 ADR ADSD 临时素材目录")


def load_turn(workdir: Path, turn: int) -> dict[str, Any]:
    timeline = json.loads((workdir / "turn_timeline.json").read_text(encoding="utf-8"))
    for item in timeline:
        if int(item.get("turn", -1)) == turn:
            return item
    raise RuntimeError(f"turn_timeline.json 没有 turn={turn}")


def choose_audio(workdir: Path, turn: int, speaker: str) -> Path:
    safe_speaker = speaker or "*"
    candidates = sorted(workdir.glob(f"turn_{turn:02d}_{safe_speaker}.mp3"))
    if not candidates:
        candidates = sorted(workdir.glob(f"turn_{turn:02d}_*.mp3"))
    if not candidates:
        candidates = sorted(workdir.glob(f"turn_{turn:02d}_*.wav"))
    if not candidates:
        raise RuntimeError(f"没有找到 turn {turn} 的音频文件")
    return candidates[0]


def make_candidates(image_url: str, audio_url: str, prompt: str, duration: int, aspect_ratio: str) -> list[dict[str, Any]]:
    common = {
        "model": "WERYDANCE_2_0",
        "prompt": prompt,
        "duration": duration,
        "aspect_ratio": aspect_ratio,
        "resolution": "1080p",
    }
    return [
        {
            "name": "image_to_video_audio",
            "path": "/generation/image-to-video",
            "payload": {**common, "image": image_url, "audio": audio_url, "audio_visual_sync": True},
        },
        {
            "name": "image_to_video_audio_url",
            "path": "/generation/image-to-video",
            "payload": {**common, "image": image_url, "audio_url": audio_url, "audio_visual_sync": True},
        },
        {
            "name": "image_to_video_reference_audio",
            "path": "/generation/image-to-video",
            "payload": {**common, "image": image_url, "reference_audio": audio_url, "audio_visual_sync": True},
        },
        {
            "name": "video_lip_sync_image_audio",
            "path": "/generation/video-lip-sync",
            "payload": {"model": "WERYDANCE_2_0", "image": image_url, "audio": audio_url, "prompt": prompt},
        },
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workdir", type=Path, default=None)
    parser.add_argument("--turn", type=int, default=1)
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--max-wait", type=int, default=720)
    parser.add_argument("--aspect-ratio", default="16:9")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    api_key = os.environ.get("WERYAI_API_KEY", "")
    if not api_key:
        raise RuntimeError("缺少 WERYAI_API_KEY")

    workdir = args.workdir or latest_adsd_dir()
    turn = load_turn(workdir, args.turn)
    image_path = workdir / f"img_{args.turn - 1}.jpg"
    if not image_path.exists():
        image_path = workdir / "img_0.jpg"
    audio_path = choose_audio(workdir, args.turn, str(turn.get("speaker") or ""))
    out_dir = args.out or Path("/private/tmp") / f"adsd_lipsync_poc_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    text = str(turn.get("text") or "").strip()
    speaker = str(turn.get("speaker") or "说话人").strip()
    duration = int(round(max(5, min(15, ffprobe_duration(audio_path) or float(turn.get("duration", 8))))))
    prompt = (
        f'Historically grounded early-Republican China dialogue close-up. Active speaker is {speaker}. '
        f'台词:"{text}" The speaker says exactly this line; mouth movement must synchronize with the provided audio. '
        "Keep the same face, visible mouth, natural jaw movement, no subtitles, no text overlay, no logo, no watermark."
    )

    log(f"workdir={workdir}")
    log(f"image={image_path}")
    log(f"audio={audio_path} duration={duration}s")
    log(f"text={text}")

    image_url = upload_file(image_path, api_key)
    audio_url = upload_file(audio_path, api_key)
    candidates = make_candidates(image_url, audio_url, prompt, duration, args.aspect_ratio)
    request_log: list[dict[str, Any]] = []
    (out_dir / "input.json").write_text(json.dumps({
        "workdir": str(workdir),
        "turn": args.turn,
        "speaker": speaker,
        "text": text,
        "image_path": str(image_path),
        "audio_path": str(audio_path),
        "image_url": image_url,
        "audio_url": audio_url,
        "duration": duration,
        "prompt": prompt,
        "candidates": [{"name": c["name"], "path": c["path"], "payload_keys": list(c["payload"].keys())} for c in candidates],
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    if args.dry_run:
        log(f"dry-run complete: {out_dir}")
        return 0

    chosen: dict[str, Any] | None = None
    task_id: str | None = None
    for candidate in candidates:
        log(f"submit candidate={candidate['name']}")
        try:
            resp = req_post(candidate["path"], candidate["payload"], api_key, timeout=30)
            request_log.append({"candidate": candidate["name"], "path": candidate["path"], "response": resp})
            task_id = extract_task_id(resp)
            if task_id:
                chosen = candidate
                break
            log(f"candidate no task_id: {json.dumps(resp, ensure_ascii=False)[:300]}")
        except Exception as exc:
            request_log.append({"candidate": candidate["name"], "path": candidate["path"], "error": str(exc)})
            log(f"candidate failed before task: {exc}")
    (out_dir / "request_attempts.json").write_text(json.dumps(request_log, ensure_ascii=False, indent=2), encoding="utf-8")

    if not task_id or not chosen:
        qa = {
            "pass": False,
            "severity": "fail",
            "reason": "no_candidate_returned_task_id",
            "created_at": datetime.now().isoformat(timespec="seconds"),
        }
        (out_dir / "lip_sync_qa.json").write_text(json.dumps(qa, ensure_ascii=False, indent=2), encoding="utf-8")
        raise RuntimeError(f"没有候选请求拿到 task_id，详见 {out_dir / 'request_attempts.json'}")

    log(f"task_id={task_id} candidate={chosen['name']}")
    data = poll_task(task_id, api_key, args.max_wait)
    (out_dir / "task_result.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    video_url = extract_video_url(data)
    if not video_url:
        raise RuntimeError(f"任务成功但无视频 URL: {json.dumps(data, ensure_ascii=False)[:800]}")
    video_path = out_dir / "werydance_lipsync_poc.mp4"
    urllib.request.urlretrieve(video_url, video_path)

    src_audio = out_dir / audio_path.name
    if audio_path.resolve() != src_audio.resolve():
        shutil.copy2(audio_path, src_audio)
    video_has_audio = has_audio_stream(video_path)
    video_duration = ffprobe_duration(video_path)
    source_audio_duration = ffprobe_duration(src_audio)
    video_audio_duration = ffprobe_duration(video_path, "a") if video_has_audio else None

    qa_audio_path = src_audio
    extracted_audio = out_dir / "generated_video_audio.mp3"
    if video_has_audio:
        try:
            run(["ffmpeg", "-y", "-i", str(video_path), "-vn", "-acodec", "libmp3lame", str(extracted_audio)], timeout=120)
            qa_audio_path = extracted_audio
        except Exception as exc:
            log(f"extract generated audio failed: {exc}")

    tg_token = os.environ.get("TG_BOT_TOKEN") or os.environ.get("TELEGRAM_TOKEN") or ""
    tg_chat_id = os.environ.get("TG_CHAT_ID") or os.environ.get("OWNER_CHAT_ID") or ""
    asr = asr_audio(qa_audio_path, api_key, tg_token, tg_chat_id, out_dir) if tg_token and tg_chat_id else None
    recognized = str((asr or {}).get("speech_text") or "")
    similarity = difflib.SequenceMatcher(None, compact_zh(text), compact_zh(recognized)).ratio() if recognized else None
    duration_delta = abs((video_audio_duration or video_duration or 0) - (source_audio_duration or 0)) if source_audio_duration else None
    native_audio_ok = video_has_audio and duration_delta is not None and duration_delta <= 0.25
    asr_ok = similarity is not None and similarity >= 0.88
    qa = {
        "mode": "ADSD_LIP_SYNC_POC",
        "pass": bool(native_audio_ok and asr_ok),
        "severity": "ok" if native_audio_ok and asr_ok else "warn" if video_path.exists() else "fail",
        "candidate": chosen["name"],
        "task_id": task_id,
        "video_path": str(video_path),
        "source_audio_path": str(src_audio),
        "video_has_audio": video_has_audio,
        "video_duration": video_duration,
        "source_audio_duration": source_audio_duration,
        "video_audio_duration": video_audio_duration,
        "audio_duration_delta": duration_delta,
        "native_audio_sync_pass": native_audio_ok,
        "asr_similarity": round(similarity, 4) if similarity is not None else None,
        "asr_pass": asr_ok,
        "expected_text": text,
        "recognized_text": recognized,
        "manual_visual_checks_required": [
            "mouth_visible",
            "active_speaker_correct",
            "no_face_drift",
            "mouth_motion_matches_syllable_timing",
        ],
        "production_decision": "do_not_integrate_by_default" if not native_audio_ok else "eligible_for_visual_review",
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }
    (out_dir / "lip_sync_qa.json").write_text(json.dumps(qa, ensure_ascii=False, indent=2), encoding="utf-8")
    log(f"done: {out_dir}")
    log(f"qa pass={qa['pass']} severity={qa['severity']} native_audio_sync={native_audio_ok} asr={qa['asr_similarity']}")
    return 0 if qa["severity"] in ("ok", "warn") else 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
