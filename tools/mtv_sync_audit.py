#!/usr/bin/env python3
"""Audit ADR MTV sync artifacts.

Checks that MTV subtitles, source-song timing, and rendered video segments share
one timeline. New MTV runs write mtv_sync_qa.json; older runs are inspected with
mtv_qa.json + mtv_subtitle_qa.json + seg_*.mp4 and reported as legacy evidence.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def _ffprobe_duration(path: Path) -> float:
    if not path.exists():
        return 0.0
    proc = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nk=1:nw=1", str(path)],
        capture_output=True,
        text=True,
        check=False,
    )
    try:
        return float(proc.stdout.strip() or 0.0)
    except Exception:
        return 0.0


def _segment_at_time(seg_durs: list[float], t: float) -> int:
    cursor = 0.0
    for i, dur in enumerate(seg_durs, start=1):
        if cursor <= t < cursor + dur:
            return i
        cursor += dur
    return len(seg_durs)


def _audit_locked(out_dir: Path, qa: dict) -> tuple[bool, list[str]]:
    issues: list[str] = []
    records = qa.get("records") or []
    if not records:
        issues.append("mtv_sync_qa.records is empty")
        return False, issues
    prev_end = 0.0
    for rec in records:
        start = float(rec.get("timeline_start") or 0.0)
        end = float(rec.get("timeline_end") or 0.0)
        if abs(start - prev_end) > 0.08:
            issues.append(f"timeline gap/overlap before turn {rec.get('turn')}: prev_end={prev_end:.3f}, start={start:.3f}")
        if end <= start:
            issues.append(f"non-positive timeline duration at turn {rec.get('turn')}: {start:.3f}-{end:.3f}")
        if rec.get("subtitle"):
            ss = float(rec.get("subtitle_source_start") or rec.get("source_start") or start)
            se = float(rec.get("subtitle_source_end") or rec.get("source_end") or end)
            src_s = float(rec.get("source_start") or start)
            src_e = float(rec.get("source_end") or end)
            if ss < src_s - 0.08 or se > src_e + 0.08:
                issues.append(f"subtitle outside source segment at turn {rec.get('turn')}: subtitle={ss:.3f}-{se:.3f}, source={src_s:.3f}-{src_e:.3f}")
        vid_path = Path(str(rec.get("vid_path") or ""))
        if vid_path and not vid_path.is_absolute():
            vid_path = out_dir / vid_path
        vid_dur = _ffprobe_duration(vid_path) if str(vid_path) else 0.0
        if vid_dur and abs(vid_dur - (end - start)) > 0.35:
            issues.append(f"video duration mismatch at turn {rec.get('turn')}: video={vid_dur:.3f}, timeline={end-start:.3f}")
        prev_end = end
    song_dur = float(qa.get("song_duration") or 0.0)
    if song_dur and abs(prev_end - song_dur) > 0.35:
        issues.append(f"timeline total != song duration: timeline={prev_end:.3f}, song={song_dur:.3f}")
    if qa.get("lip_sync_enabled") and qa.get("vocal_segment_count"):
        vocal_count = int(qa.get("vocal_segment_count") or 0)
        lip_success = int(qa.get("lip_sync_success_count") or 0)
        if lip_success < vocal_count:
            issues.append(f"lip_sync incomplete: {lip_success}/{vocal_count} vocal segments succeeded")
        for rec in records:
            if rec.get("role") == "vocal" and rec.get("motion_path") != "song-audio-lip-sync":
                issues.append(f"vocal turn {rec.get('turn')} not rendered by song-audio-lip-sync: {rec.get('motion_path')}")
    return not issues, issues


def _audit_legacy(out_dir: Path) -> tuple[bool, list[str]]:
    issues: list[str] = []
    sub_qa = _read_json(out_dir / "mtv_subtitle_qa.json")
    mtv_qa = _read_json(out_dir / "mtv_qa.json")
    scene_count = int(mtv_qa.get("scene_count") or 0)
    if scene_count <= 0:
        issues.append("missing scene_count in mtv_qa.json")
        return False, issues
    seg_durs = [_ffprobe_duration(out_dir / f"seg_{i}.mp4") for i in range(scene_count)]
    if not all(d > 0 for d in seg_durs):
        issues.append("one or more seg_N.mp4 durations are missing")
    for rec in sub_qa.get("records") or []:
        sub_scene = int(rec.get("scene") or 0)
        visual_scene = _segment_at_time(seg_durs, float(rec.get("start") or 0.0))
        if sub_scene and visual_scene and sub_scene != visual_scene:
            issues.append(
                f"subtitle/visual mismatch at {float(rec.get('start') or 0.0):.3f}s: "
                f"subtitle_scene={sub_scene}, visual_scene={visual_scene}, text={str(rec.get('text') or '')[:32]}"
            )
    if not (out_dir / "mtv_sync_qa.json").exists():
        issues.append("missing mtv_sync_qa.json (legacy MTV run; no locked shared timeline evidence)")
    return not issues, issues


def main() -> int:
    out_dir = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    sync_qa = _read_json(out_dir / "mtv_sync_qa.json")
    if sync_qa:
        ok, issues = _audit_locked(out_dir, sync_qa)
        mode = "locked"
    else:
        ok, issues = _audit_legacy(out_dir)
        mode = "legacy"
    print(json.dumps({"ok": ok, "mode": mode, "issues": issues}, ensure_ascii=False, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
