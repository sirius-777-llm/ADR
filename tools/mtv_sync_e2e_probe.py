#!/usr/bin/env python3
"""Build a small MTV sync proof artifact from an existing lip-sync probe.

The probe uses one song-audio-driven lip-sync segment, burns a locked-timeline
subtitle, muxes the same source audio, writes mtv_sync_qa.json, and runs the
strict MTV sync audit. It is intentionally small so it can be run after code
changes without re-rendering a full MTV.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _run(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, check=True, capture_output=True, text=True)


def _duration(path: Path) -> float:
    proc = _run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nk=1:nw=1", str(path)])
    return float(proc.stdout.strip())


def _video_size(path: Path) -> tuple[int, int]:
    proc = _run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=p=0:s=x", str(path)])
    w, h = proc.stdout.strip().split("x")
    return int(w), int(h)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe-dir", default="/tmp/adr_mtv_lips_probe_sudongpo")
    ap.add_argument("--out-dir", default="/tmp/adr_mtv_sync_e2e_probe")
    ap.add_argument("--text", default="大江东去浪淘尽\\N千古风流人物")
    args = ap.parse_args()

    probe_dir = Path(args.probe_dir)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    src_video = probe_dir / "seg_0.mp4"
    src_audio = probe_dir / "mtv_song_slice_0.mp3"
    src_qa = probe_dir / "mtv_lip_sync_probe_qa.json"
    if not src_video.exists() or not src_audio.exists() or not src_qa.exists():
        raise SystemExit(f"missing probe assets in {probe_dir}")

    os.environ.setdefault("WERYAI_API_KEY", "dummy")
    os.environ.setdefault("TG_BOT_TOKEN", "dummy")
    os.environ.setdefault("TG_CHAT_ID", "dummy")
    os.environ["OUTPUT_DIR"] = str(out_dir)
    sys.argv = ["mtv_sync_e2e_probe.py", "MTV sync e2e probe", "vmtv"]
    import run_adr_v8 as adr

    adr.OUTPUT_DIR = out_dir
    adr.tg = lambda *args, **kwargs: None

    video = out_dir / "seg_0.mp4"
    audio = out_dir / "mtv_song_slice_0.mp3"
    shutil.copy2(src_video, video)
    shutil.copy2(src_audio, audio)

    audio_dur = _duration(audio)
    target_dur = min(_duration(video), audio_dur)
    scene = {
        "vid_path": str(video),
        "timeline_start": 0.0,
        "timeline_end": round(target_dur, 3),
        "mtv_source_start": 0.0,
        "mtv_source_end": round(target_dur, 3),
        "mtv_subtitle_source_start": 0.0,
        "mtv_subtitle_source_end": round(target_dur, 3),
        "mtv_role": "vocal",
        "mtv_subtitle_text": args.text,
        "mtv_timeline_locked": True,
        "mtv_motion_path": "song-audio-lip-sync",
    }
    adr._mtv_normalize_segment_duration(scene, target_dur)
    video_dur = _duration(video)
    scene["timeline_end"] = round(target_dur, 3)
    scene["mtv_source_end"] = round(target_dur, 3)
    scene["mtv_subtitle_source_end"] = round(target_dur, 3)

    ass_path = adr._write_mtv_subtitles([scene], str(audio))
    final = out_dir / "final_mtv_sync_probe.mp4"
    vf = f"scale={adr.VIDEO_W}:{adr.VIDEO_H}:force_original_aspect_ratio=increase,crop={adr.VIDEO_W}:{adr.VIDEO_H},setsar=1,setdar={adr.ASPECT_RATIO},fps=24,ass={str(ass_path).replace(':', r'\\:')}"
    _run([
        "ffmpeg", "-hide_banner", "-y",
        "-i", str(video),
        "-i", str(audio),
        "-map", "0:v", "-map", "1:a",
        "-vf", vf,
        "-c:v", "libx264", "-crf", "20", "-preset", "medium",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest", "-aspect", adr.ASPECT_RATIO, "-movflags", "+faststart",
        str(final),
    ])

    lip_qa = json.loads(src_qa.read_text(encoding="utf-8"))
    w, h = _video_size(final)
    sync_qa = {
        "mode": adr.CURRENT_MODE_LABEL,
        "song_path": str(audio),
        "song_duration": round(audio_dur, 3),
        "timeline_locked": True,
        "alignment_mode": "mtv_e2e_probe_locked",
        "segment_count": 1,
        "vocal_segment_count": 1,
        "instrumental_segment_count": 0,
        "lip_sync_enabled": True,
        "lip_sync_success_count": 1,
        "lip_sync_attempt_count": 1,
        "final_path": str(final),
        "final_duration": round(_duration(final), 3),
        "final_width": w,
        "final_height": h,
        "records": [
            {
                "turn": 1,
                "role": "vocal",
                "timeline_start": 0.0,
                "timeline_end": round(target_dur, 3),
                "source_start": 0.0,
                "source_end": round(target_dur, 3),
                "subtitle_source_start": 0.0,
                "subtitle_source_end": round(target_dur, 3),
                "subtitle": args.text,
                "motion_path": "song-audio-lip-sync",
                "vid_path": str(video),
                "vid_duration": round(video_dur, 3),
            }
        ],
        "lip_sync_records": [lip_qa],
    }
    (out_dir / "mtv_sync_qa.json").write_text(json.dumps(sync_qa, ensure_ascii=False, indent=2), encoding="utf-8")
    audit = _run([sys.executable, str(ROOT / "tools" / "mtv_sync_audit.py"), str(out_dir)])
    result = json.loads(audit.stdout)
    print(json.dumps({"ok": result.get("ok"), "audit": result, "out_dir": str(out_dir), "final": str(final)}, ensure_ascii=False, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
