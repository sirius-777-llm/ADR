#!/usr/bin/env python3
"""ADR 下游局部重跑工具

跳过 step1-step66（脚本生成/TTS/图片/lip-sync）直接跑下游：
  retiming → hybrid voice → step7 concat → step8 字幕 → 动态 BGM → step9 mux → step10 推 TG

适用场景：
  · 调字幕/音画同步 / step8 算法
  · 调 BGM mux 参数 / dynamic BGM
  · 调 step9 mux 公式
  · 调 hybrid voice 抽取/loudnorm
  · 改 ASR 字幕对齐

不适用：
  · 改 step66 prompt / WERYDANCE 生成行为（要重跑 lip-sync）
  · 改图片 (step6) 内容
  · 改 TTS (step2) 内容

依赖：
  目标 OUTPUT_DIR 必须含 pipeline_state.json
  （ADR 主流程 step66 之后自动保存，2026-05-20 之后的 run 都有）

用法：
  python3 tools/rerun_downstream.py /tmp/adr_v8_20260520_165927
"""
import json
import os
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <OUTPUT_DIR> [--regen-bgm]")
        return 1
    output_dir = Path(sys.argv[1]).resolve()
    if not output_dir.is_dir():
        print(f"OUTPUT_DIR 不存在: {output_dir}")
        return 1
    regen_bgm = "--regen-bgm" in sys.argv

    state_path = output_dir / "pipeline_state.json"
    if not state_path.exists():
        print(f"未找到 pipeline_state.json: {state_path}")
        print("（仅 2026-05-20 之后 ADR step66 完成的 run 自动保存这个文件）")
        return 1

    # 必须在 import run_adr_v8 之前设置 OUTPUT_DIR env var，因为它在 module 顶层被读取
    os.environ["OUTPUT_DIR"] = str(output_dir)
    # 也要传环境变量给 weryai / TG（兜底从 telegram-claude-bot/.env 读）
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
    # 兼容字段
    if "TG_BOT_TOKEN" not in os.environ and "TELEGRAM_TOKEN" in os.environ:
        os.environ["TG_BOT_TOKEN"] = os.environ["TELEGRAM_TOKEN"]
    if "TG_CHAT_ID" not in os.environ and "OWNER_CHAT_ID" in os.environ:
        os.environ["TG_CHAT_ID"] = os.environ["OWNER_CHAT_ID"]

    # 关键：sys.argv 必须含 ADSD 标志，因为 run_adr_v8.py module 顶层会读 sys.argv
    # 决定 ADS_DIALOGUE_MODE / ADSD_LIP_SYNC_EXPERIMENT / ADSD_ALMIGHTY_AUDIO_DUB_EXPERIMENT
    # 不设的话这些 global 都 False，_build_voice_clone_hybrid_audio 直接 return None
    state_preview = json.loads(state_path.read_text(encoding="utf-8"))
    if state_preview.get("ads_dialogue_mode"):
        sys.argv = ["run_adr_v8.py", state_preview.get("topic", "resume"), "h", "--adsd"]
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    import run_adr_v8 as adr
    # 兜底：state 标记了但 module 没 pick up（sys.argv 顺序敏感）→ 手动 patch
    if state_preview.get("ads_dialogue_mode") and not getattr(adr, "ADS_DIALOGUE_MODE", False):
        adr.ADS_DIALOGUE_MODE = True
    if state_preview.get("adsd_lip_sync_experiment") and not getattr(adr, "ADSD_LIP_SYNC_EXPERIMENT", False):
        adr.ADSD_LIP_SYNC_EXPERIMENT = True
    if state_preview.get("adsd_almighty_audio_dub_experiment") and not getattr(adr, "ADSD_ALMIGHTY_AUDIO_DUB_EXPERIMENT", False):
        adr.ADSD_ALMIGHTY_AUDIO_DUB_EXPERIMENT = True

    state = json.loads(state_path.read_text(encoding="utf-8"))
    script = state["script"]
    voice_path = state["voice_path"]
    bgm_path = state.get("bgm_path")
    topic = state["topic"]

    print(f"\n=== resume from {output_dir.name} ===")
    print(f"topic: {topic}")
    print(f"turn count: {len(script)}")
    print(f"voice_path: {voice_path}")
    print(f"bgm_path: {bgm_path}")
    print(f"regen_bgm: {regen_bgm}")
    print()

    if regen_bgm:
        print("[--regen-bgm] 强制重新生成 BGM (含 vocal 检测 retry)...")
        tone = "中性"
        new_bgm = adr.generate_bgm(topic, tone)
        if new_bgm:
            bgm_path = new_bgm
            print(f"  新 BGM: {bgm_path}")
        else:
            print(f"  BGM 重生成失败，沿用原 bgm_path: {bgm_path}")

    # 跑下游
    print("[1/6] audio_dub retiming...")
    try:
        extended = adr._retime_after_audio_dub(script)
        print(f"  retiming: {extended} turn 拉长")
    except Exception as e:
        print(f"  retiming 异常（保留原 timeline）：{e}")

    print("[2/6] hybrid voice-clone splice...")
    try:
        hybrid_voice = adr._build_voice_clone_hybrid_audio(script, voice_path)
        if hybrid_voice:
            voice_path = hybrid_voice
            print(f"  hybrid_voice: {voice_path}")
        else:
            print("  hybrid 跳过，沿用原 voice_path")
    except Exception as e:
        print(f"  hybrid 异常（沿用原 voice_path）：{e}")

    print("[3/6] step7 concat...")
    raw_path = adr.step7_concat(script)
    print(f"  raw_path: {raw_path}")

    print("[4/6] step8 字幕...")
    ass_path = adr.step8_subtitles(script)
    print(f"  ass_path: {ass_path}")

    print("[5/6] dynamic BGM...")
    if bgm_path:
        try:
            dyn_bgm = adr._build_dynamic_bgm(script, bgm_path)
            if dyn_bgm:
                bgm_path = dyn_bgm
                print(f"  hybrid_bgm: {bgm_path}")
            else:
                print("  dynamic BGM 跳过 (没 silent_b 或失败)")
        except Exception as e:
            print(f"  dynamic BGM 异常（沿用原 bgm_path）：{e}")

    print("[6/6] step9 render + step10 deliver...")
    final_path = adr.step9_render(raw_path, voice_path, bgm_path, ass_path, topic)
    print(f"  final_path: {final_path}")
    adr.step10_deliver(final_path, topic, script)
    print("  TG 推送完成")

    print(f"\n=== resume done: {final_path} ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
