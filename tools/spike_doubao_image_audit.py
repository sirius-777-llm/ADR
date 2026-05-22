#!/usr/bin/env python3
"""Spike: 验证 image-to-video 端点 + DOUBAO_1_LITE 是否能放行 WERYDANCE audit 拒掉的图。

用法:
  python3 tools/spike_doubao_image_audit.py /tmp/adr_v8_20260522_200447/meta_grid_科比.png
"""
import json
import os
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

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

real_args = list(sys.argv[1:])
sys.argv = ["spike", "spike_topic", "h", "--adsd"]
sys.path.insert(0, str(ROOT))
import run_adr_v8 as adr

img_path = real_args[0] if real_args else "/tmp/adr_v8_20260522_200447/meta_grid_科比.png"

print(f"=== Spike DOUBAO image-to-video audit ===")
print(f"image: {img_path}")
print(f"file exists: {os.path.exists(img_path)}")
print()

print("[1/3] uploading image to weryai...")
image_url = adr._upload_to_weryai(img_path)
print(f"  url: {image_url}")
print()

print("[2/3] submitting DOUBAO_1_LITE image-to-video task...")
payload = {
    "model": "DOUBAO_1_LITE",
    "image": image_url,
    "prompt": "Cinematic kinetic action scene. Camera dynamic movement. No text.",
    "duration": 5,
    "aspect_ratio": "16:9",
    "resolution": "720p",
}
r = adr.req_post("/generation/image-to-video", payload, timeout=30)
print(f"  response: {json.dumps(r, ensure_ascii=False)[:400]}")
data = r.get("data") or {}
task_id = data.get("task_id") or (data.get("task_ids") or [None])[0]
print(f"  task_id: {task_id}")
print()

if not task_id:
    print(f"❌ submit FAIL (no task_id)")
    sys.exit(1)

print("[3/3] polling status...")
for i in range(60):
    time.sleep(5)
    s = adr.req_get(f"/generation/{task_id}/status")
    data = s.get("data", {})
    st = data.get("task_status", "")
    msg = data.get("msg", "")
    print(f"  poll #{i+1}: status={st} msg={msg[:80]}")
    if st == "succeed":
        vid_url = adr._extract_video_url(data) if hasattr(adr, "_extract_video_url") else (data.get("video_url") or "")
        print(f"  ✅ SUCCESS! video_url: {vid_url}")
        out = "/tmp/spike_doubao_test.mp4"
        try:
            urllib.request.urlretrieve(vid_url, out)
            print(f"  downloaded: {out}")
        except Exception as e:
            print(f"  download failed: {e}")
        break
    if st == "failed":
        print(f"  ❌ FAIL: {msg}")
        print(f"  full response: {json.dumps(data, ensure_ascii=False)}")
        break
