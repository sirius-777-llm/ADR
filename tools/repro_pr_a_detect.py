#!/usr/bin/env python3
"""PR-A.1 复现脚本: 用罗永浩 v1 fixture 复现 step66 _batch_groups detect bug.

罗永浩 v1 run (120911) 的 grouping QA 显示:
  multi_turn_groups: 1, group_idx=5, turn_indices=[5, 6], dur=10.263, fits_15s_cap=True

但实际 run 没触发 PR-A. 这脚本直接 invoke step66 内的 _batch_groups detect 路径,
看 runtime 实际算出来是什么.
"""
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("WERYAI_API_KEY", "test_dummy")
os.environ.setdefault("TG_BOT_TOKEN", "test_dummy")
os.environ.setdefault("TG_CHAT_ID", "test_dummy")
sys.argv = ["repro_pr_a_detect.py", "test", "h", "--adsd", "--adsd-speaker-batch"]

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import run_adr_v8 as adr  # noqa: E402

FIXTURE_DIR = Path("/tmp/adr_v8_20260527_120911")
if not FIXTURE_DIR.exists():
    print(f"❌ fixture 不存在: {FIXTURE_DIR}")
    sys.exit(1)


def main():
    print("=== PR-A.1 复现脚本 ===")
    print(f"fixture: {FIXTURE_DIR}")

    # 加载 turn_timeline as script
    script = json.load(open(FIXTURE_DIR / "turn_timeline.json"))
    n = len(script)
    print(f"\nturn count: {n}")

    # 关键 runtime 状态
    print(f"\nruntime flags:")
    print(f"  ADS_DIALOGUE_MODE = {adr.ADS_DIALOGUE_MODE}")
    print(f"  ADSD_ALMIGHTY_AUDIO_DUB_EXPERIMENT = {adr.ADSD_ALMIGHTY_AUDIO_DUB_EXPERIMENT}")
    print(f"  ADSD_CONSECUTIVE_SPEAKER_BATCHING = {adr.ADSD_CONSECUTIVE_SPEAKER_BATCHING}")
    print(f"  ADSD_SPEAKER_BATCH_MAX_DURATION = {adr.ADSD_SPEAKER_BATCH_MAX_DURATION}")

    # 算 target_durs (跟 step66 一致)
    target_durs = [adr._lip_sync_slot_duration(script, i) for i in range(n)]
    print(f"\ntarget_durs: {[f'{d:.2f}' for d in target_durs]}")

    # 复现 P2 grouping detect
    consecutive_groups = []
    cur_group = []
    cur_speaker = None
    cur_dur = 0.0
    for i, s in enumerate(script):
        sp = (s.get("speaker") or "").strip()
        d = float(target_durs[i])
        if sp == cur_speaker and cur_group and (cur_dur + d) <= adr.ADSD_SPEAKER_BATCH_MAX_DURATION:
            cur_group.append(i)
            cur_dur += d
        else:
            if cur_group:
                consecutive_groups.append(cur_group)
            cur_group = [i]
            cur_speaker = sp
            cur_dur = d
    if cur_group:
        consecutive_groups.append(cur_group)

    print(f"\nconsecutive_groups (共 {len(consecutive_groups)}):")
    for gi, g in enumerate(consecutive_groups):
        speakers = [script[i].get("speaker", "?") for i in g]
        total = sum(target_durs[i] for i in g)
        nls = [script[i].get("needs_lip_sync", True) for i in g]
        marker = "⭐" if len(g) > 1 else "  "
        print(f"  {marker} group {gi+1}: idxs={g} speakers={speakers} total={total:.2f}s needs_lip={nls}")

    # 复现 PR-A 决定 _batch_groups
    print(f"\nPR-A detect:")
    print(f"  ADSD_CONSECUTIVE_SPEAKER_BATCHING = {adr.ADSD_CONSECUTIVE_SPEAKER_BATCHING}")
    print(f"  ADSD_ALMIGHTY_AUDIO_DUB_EXPERIMENT = {adr.ADSD_ALMIGHTY_AUDIO_DUB_EXPERIMENT}")
    _batch_groups = []
    if adr.ADSD_CONSECUTIVE_SPEAKER_BATCHING and adr.ADSD_ALMIGHTY_AUDIO_DUB_EXPERIMENT:
        for g in consecutive_groups:
            if len(g) <= 1:
                continue
            total = sum(target_durs[i] for i in g)
            all_a_roll = all(script[i].get("needs_lip_sync", True) for i in g)
            print(f"  check g={g}: total={total:.2f} all_a_roll={all_a_roll} fit_15s={total<=15.0}")
            if total <= 15.0 and all_a_roll:
                _batch_groups.append(g)
    print(f"\n_batch_groups: {_batch_groups}")
    if _batch_groups:
        print(f"✅ PR-A 应触发 {len(_batch_groups)} 个 group")
    else:
        print(f"❌ _batch_groups 为空 (跟实际 run 一致)")


if __name__ == "__main__":
    main()
