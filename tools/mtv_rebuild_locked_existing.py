#!/usr/bin/env python3
"""Rebuild an existing MTV run with the current locked sync timeline.

This is a lower-cost full-timeline verification path: it reuses an existing
mtv_plan.json, generated song, and source images, then regenerates all vocal
segments through song-audio lip-sync and all instrumental segments locally.
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


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src-dir", default="/tmp/adr_v8_20260606_131625")
    ap.add_argument("--out-dir", default="/tmp/adr_mtv_locked_rebuild_sudongpo")
    ap.add_argument("--singer", default="苏东坡")
    ap.add_argument("--topic", default="苏东坡的念奴娇·赤壁怀古")
    ap.add_argument("--mode", choices=["hmtv", "vmtv"], default="vmtv")
    args = ap.parse_args()

    src_dir = Path(args.src_dir)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    plan_path = src_dir / "mtv_plan.json"
    song_path = src_dir / "mtv_song_trimmed.mp3"
    if not song_path.exists():
        song_path = src_dir / "mtv_song.mp3"
    if not plan_path.exists() or not song_path.exists():
        raise SystemExit(f"missing plan/song in {src_dir}")

    os.environ["OUTPUT_DIR"] = str(out_dir)
    os.environ.setdefault("WERYAI_API_KEY", "dummy")
    os.environ.setdefault("TG_BOT_TOKEN", "dummy")
    os.environ.setdefault("TG_CHAT_ID", "dummy")
    sys.argv = ["mtv_rebuild_locked_existing.py", args.topic, args.mode, "--singer", args.singer]
    import run_adr_v8 as adr

    adr.OUTPUT_DIR = out_dir
    adr.tg = lambda *a, **k: None
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    shutil.copy2(plan_path, out_dir / "mtv_plan.json")
    shutil.copy2(song_path, out_dir / song_path.name)
    local_song = str(out_dir / song_path.name)
    song_dur = adr.ffprobe_duration(local_song)

    scenes = plan.get("scenes") or []
    seed = []
    for i, item in enumerate(scenes):
        src_img = src_dir / f"img_{i}.jpg"
        if not src_img.exists():
            raise SystemExit(f"missing source image: {src_img}")
        seed.append({
            "dialogue_turn": i + 1,
            "turn_type": "mtv",
            "speaker": args.singer,
            "text": str(item.get("lyric") or ""),
            "lyric": str(item.get("lyric") or ""),
            "shot": str(item.get("visual") or ""),
            "prompt": str(item.get("visual") or ""),
            "emotion": str(item.get("emotion") or "poetic"),
            "dur": 10,
            "vid_duration": 10,
            "img_path": str(src_img),
            "vid_path": str(src_dir / f"seg_{i}.mp4"),
            "mtv_motion": str(item.get("motion") or ""),
        })

    alignment = adr._mtv_alignment_from_script(seed, local_song)
    records = alignment.get("records") or []
    if not records:
        raise SystemExit("alignment produced no subtitle/vocal records")

    timeline: list[dict] = []

    def add_scene(src_idx: int, start: float, end: float, role: str, text: str = "", subtitle: str = "", sub_start: float | None = None, sub_end: float | None = None) -> None:
        src = seed[max(0, min(src_idx, len(seed) - 1))]
        idx = len(timeline)
        img = out_dir / f"img_{idx}.jpg"
        shutil.copy2(src["img_path"], img)
        dur = max(0.3, end - start)
        timeline.append({
            **src,
            "dialogue_turn": idx + 1,
            "text": text,
            "dur": dur,
            "vid_duration": dur,
            "img_path": str(img),
            "vid_path": str(out_dir / f"seg_{idx}.mp4"),
            "timeline_start": 0.0,
            "timeline_end": 0.0,
            "mtv_source_start": round(start, 3),
            "mtv_source_end": round(end, 3),
            "mtv_subtitle_source_start": round(sub_start if sub_start is not None else start, 3),
            "mtv_subtitle_source_end": round(sub_end if sub_end is not None else end, 3),
            "mtv_role": role,
            "mtv_subtitle_text": subtitle,
            "mtv_timeline_locked": True,
        })

    first = float(records[0]["start"])
    last = min(song_dur, max(float(records[-1]["end"]), float(alignment.get("asr_end") or 0.0)))
    for a, b in adr._mtv_split_span(0.0, first, max_dur=12.0):
        add_scene(0, a, b, "instrumental")
    for i, rec in enumerate(records):
        src_idx = max(0, int(rec.get("scene") or 1) - 1)
        start = float(rec["start"])
        end = float(records[i + 1]["start"]) if i < len(records) - 1 else last
        text = str(rec.get("text") or "").replace(r"\N", " ")
        add_scene(src_idx, start, end, "vocal", text=text, subtitle=str(rec.get("text") or ""), sub_start=float(rec["start"]), sub_end=float(rec["end"]))
    for a, b in adr._mtv_split_span(last, song_dur, max_dur=12.0):
        add_scene(len(seed) - 1, a, b, "instrumental")

    cursor = 0.0
    for s in timeline:
        dur = max(0.3, float(s.get("vid_duration") or s.get("dur") or 0.0))
        s["timeline_start"] = round(cursor, 3)
        s["timeline_end"] = round(cursor + dur, 3)
        cursor += dur

    lip_records = []
    for i, scene in enumerate(timeline):
        dur = float(scene.get("vid_duration") or scene.get("dur") or 0.0)
        if scene["mtv_role"] == "vocal":
            audio = adr._mtv_song_slice(local_song, float(scene["mtv_source_start"]), float(scene["mtv_source_end"]), i)
            ok, info = adr._mtv_lip_sync_segment(i, scene, audio, dur)
            lip_records.append(info)
            if not ok:
                scene["mtv_motion_path"] = "lip-sync-failed"
                raise SystemExit(f"lip-sync failed at timeline turn {i+1}: {info}")
            scene["mtv_motion_path"] = "song-audio-lip-sync"
        else:
            if not adr._mtv_static_fallback_segment(scene, dur):
                raise SystemExit(f"instrumental static segment failed at turn {i+1}")
            scene["mtv_motion_path"] = "instrumental-static"

    ass_path = adr._write_mtv_subtitles(timeline, local_song)
    concat = out_dir / "mtv_concat.txt"
    concat.write_text("".join(f"file '{s['vid_path']}'\n" for s in timeline), encoding="utf-8")
    raw = out_dir / "mtv_raw_concat.mp4"
    _run(["ffmpeg", "-hide_banner", "-y", "-f", "concat", "-safe", "0", "-i", str(concat), "-c", "copy", str(raw)])
    final = out_dir / "final_mtv.mp4"
    ass_filter = str(ass_path).replace(":", r"\:")
    vf = f"scale={adr.VIDEO_W}:{adr.VIDEO_H}:force_original_aspect_ratio=increase,crop={adr.VIDEO_W}:{adr.VIDEO_H},setsar=1,setdar={adr.ASPECT_RATIO},fps=24,ass={ass_filter}"
    _run([
        "ffmpeg", "-hide_banner", "-y",
        "-i", str(raw), "-i", local_song,
        "-map", "0:v", "-map", "1:a",
        "-vf", vf,
        "-c:v", "libx264", "-crf", "20", "-preset", "medium",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest", "-aspect", adr.ASPECT_RATIO, "-movflags", "+faststart",
        str(final),
    ])

    sync_qa = {
        "mode": adr.CURRENT_MODE_LABEL,
        "topic": args.topic,
        "song_path": local_song,
        "song_duration": round(song_dur, 3),
        "timeline_locked": True,
        "alignment_mode": alignment.get("alignment_mode"),
        "asr_vocal_start": round(alignment.get("asr_start") or 0.0, 3) if alignment.get("use_asr_span") else None,
        "asr_vocal_end": round(alignment.get("asr_end") or 0.0, 3) if alignment.get("use_asr_span") else None,
        "segment_count": len(timeline),
        "vocal_segment_count": sum(1 for s in timeline if s.get("mtv_role") == "vocal"),
        "instrumental_segment_count": sum(1 for s in timeline if s.get("mtv_role") == "instrumental"),
        "lip_sync_enabled": True,
        "lip_sync_success_count": sum(1 for r in lip_records if r.get("pass")),
        "lip_sync_attempt_count": len(lip_records),
        "final_path": str(final),
        "final_duration": round(adr.ffprobe_duration(str(final)), 3),
        "records": [
            {
                "turn": i + 1,
                "role": s.get("mtv_role"),
                "timeline_start": s.get("timeline_start"),
                "timeline_end": s.get("timeline_end"),
                "source_start": s.get("mtv_source_start"),
                "source_end": s.get("mtv_source_end"),
                "subtitle_source_start": s.get("mtv_subtitle_source_start"),
                "subtitle_source_end": s.get("mtv_subtitle_source_end"),
                "subtitle": s.get("mtv_subtitle_text"),
                "motion_path": s.get("mtv_motion_path"),
                "vid_path": s.get("vid_path"),
                "vid_duration": round(adr.ffprobe_duration(s.get("vid_path")), 3),
            }
            for i, s in enumerate(timeline)
        ],
        "lip_sync_records": lip_records,
    }
    (out_dir / "mtv_sync_qa.json").write_text(json.dumps(sync_qa, ensure_ascii=False, indent=2), encoding="utf-8")
    audit = _run([sys.executable, str(ROOT / "tools" / "mtv_sync_audit.py"), str(out_dir)])
    result = json.loads(audit.stdout)
    print(json.dumps({"ok": result.get("ok"), "audit": result, "out_dir": str(out_dir), "final": str(final)}, ensure_ascii=False, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
