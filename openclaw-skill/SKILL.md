---
name: adr
description: Execute the ADR (Automated Documentary Rendering) V8.1 pipeline. Trigger when user says "执行ADR", "跑ADR", "生成ADR", or asks to create a documentary video on any topic.
---

# ADR V8.1 — Automated Documentary Rendering

Input a topic, output a cinematic short video with voiceover, subtitles, BGM, and social media copy.

## Execution

```bash
cd /Users/wekoidubai/ADR && nohup /opt/homebrew/bin/python3 run_adr_v8.py "主题" > /tmp/adr_v8.log 2>&1 &
```

Required env: WERYAI_API_KEY, TG_BOT_TOKEN, TG_CHAT_ID.
Self-reports to Telegram. Do NOT monitor or tail logs.

## Architecture

```
Topic -> Spielberg (Gemini 3.1 Flash Lite, 3x retry for 9 lines)
      -> Historian (Gemini 3.1 Flash, visual research)
      -> Jiang Wen (Gemini 3.1 Flash, image prompts)
      -> Voice Director (Gemini 3.1 Flash, speaker selection)
      -> WeryAI Podcast (single master voice track)
      -> Whisper ASR (base model, auto-download)
      -> Velocity-curve interpolation (char_time_map per sentence)
      -> 20-thread pool (9 AI images + 1 BGM)
      -> ffmpeg (concat demuxer + ASS subtitles + J-Cut + amix)
      -> Telegram (video + social copy + one-click copy)
```

Cinematic timing: image -> +0.2s subtitle -> +0.5s audio (J-Cut via -itsoffset)

## V8.1 Key Changes

- All LLM calls unified to Gemini family (no Claude dependency)
- Whisper alignment: velocity-curve interpolation replaces greedy-merge
- Script generation: 3x auto-retry if < 9 lines
- Env vars: graceful error + debug dump
- Whisper model: auto-download
