#!/usr/bin/env python3
"""Offline regression checks for MTV sync timeline helpers."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def _duration(path: Path) -> float:
    proc = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nk=1:nw=1", str(path)],
        capture_output=True,
        text=True,
        check=True,
    )
    return float(proc.stdout.strip())


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="adr_mtv_sync_regression_"))
    try:
        os.environ.setdefault("WERYAI_API_KEY", "dummy")
        os.environ.setdefault("TG_BOT_TOKEN", "dummy")
        os.environ.setdefault("TG_CHAT_ID", "dummy")
        os.environ["OUTPUT_DIR"] = str(tmp)
        import run_adr_v8 as adr

        adr.OUTPUT_DIR = tmp
        adr.tg = lambda *args, **kwargs: None
        long_seg = tmp / "seg_0.mp4"
        _run([
            "ffmpeg", "-hide_banner", "-y", "-f", "lavfi", "-i", "color=c=black:s=720x1280:r=24",
            "-t", "4.0", "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(long_seg),
        ])
        scene = {"vid_path": str(long_seg)}
        assert adr._mtv_normalize_segment_duration(scene, 1.35), "normalize returned false"
        dur = _duration(long_seg)
        assert abs(dur - 1.35) <= 0.12, f"normalized duration mismatch: {dur}"

        script = [
            {
                "vid_path": str(long_seg),
                "timeline_start": 0.0,
                "timeline_end": 1.35,
                "mtv_source_start": 0.0,
                "mtv_source_end": 1.35,
                "mtv_role": "instrumental",
                "mtv_timeline_locked": True,
            },
            {
                "vid_path": str(long_seg),
                "timeline_start": 1.35,
                "timeline_end": 3.35,
                "mtv_source_start": 10.0,
                "mtv_source_end": 12.0,
                "mtv_subtitle_source_start": 10.4,
                "mtv_subtitle_source_end": 11.6,
                "mtv_role": "vocal",
                "mtv_subtitle_text": "测试歌词",
                "mtv_timeline_locked": True,
            },
        ]
        ass_path = Path(adr._write_mtv_subtitles(script, None))
        ass = ass_path.read_text(encoding="utf-8")
        assert "Dialogue: 0,0:00:01.78,0:00:02.92" in ass, ass

        sync_qa = {
            "song_duration": 3.35,
            "timeline_locked": True,
            "lip_sync_enabled": False,
            "records": [
                {"turn": 1, "timeline_start": 0.0, "timeline_end": 1.35, "source_start": 0.0, "source_end": 1.35, "vid_path": str(long_seg)},
                {
                    "turn": 2,
                    "timeline_start": 1.35,
                    "timeline_end": 3.35,
                    "source_start": 10.0,
                    "source_end": 12.0,
                    "subtitle_source_start": 10.4,
                    "subtitle_source_end": 11.6,
                    "subtitle": "测试歌词",
                },
            ],
        }
        (tmp / "mtv_sync_qa.json").write_text(json.dumps(sync_qa, ensure_ascii=False, indent=2), encoding="utf-8")
        audit = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "mtv_sync_audit.py"), str(tmp)],
            capture_output=True,
            text=True,
            check=True,
        )
        result = json.loads(audit.stdout)
        assert result.get("ok") is True, result
        print(json.dumps({"ok": True, "tmp": str(tmp)}, ensure_ascii=False))
        return 0
    finally:
        if os.environ.get("ADR_KEEP_MTV_SYNC_REGRESSION_TMP", "").strip().lower() not in ("1", "true", "yes"):
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
