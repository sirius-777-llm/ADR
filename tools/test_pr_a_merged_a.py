#!/usr/bin/env python3
"""PR-A merged_a unit test · 不依赖 LLM 随机性, 直接 mock WERYDANCE API 验 _lip_sync_one_group.

策略:
- mock req_post (submit) + req_get (poll succeed) + urlretrieve (fake video)
- 真跑 _concat_audio_files_for_group + _split_lip_sync_raw_by_durations (ffmpeg)
- 验证: 1 次 submit / audio 拼接产物 / 2 个 seg split / 全 ok
"""
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import MagicMock

# 设 mock env 防 ADR 启动崩
os.environ.setdefault("WERYAI_API_KEY", "test_dummy")
os.environ.setdefault("TG_BOT_TOKEN", "test_dummy")
os.environ.setdefault("TG_CHAT_ID", "test_dummy")
sys.argv = ["test_pr_a_merged_a.py", "test_topic_pr_a", "h", "--adsd"]

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import run_adr_v8 as adr  # noqa: E402

FFMPEG = "/opt/homebrew/bin/ffmpeg"


def _make_fake_audio(out_path: Path, duration: float) -> None:
    subprocess.run(
        [FFMPEG, "-y", "-f", "lavfi", "-i", f"sine=frequency=440:duration={duration}",
         "-c:a", "pcm_s16le", "-ar", "44100", "-ac", "1", str(out_path)],
        check=True, capture_output=True,
    )


def _make_fake_video(out_path: Path, duration: float) -> None:
    subprocess.run(
        [FFMPEG, "-y",
         "-f", "lavfi", "-i", f"testsrc=duration={duration}:size=1280x720:rate=24",
         "-f", "lavfi", "-i", f"sine=frequency=440:duration={duration}",
         "-c:v", "libx264", "-c:a", "aac", "-pix_fmt", "yuv420p",
         "-shortest", str(out_path)],
        check=True, capture_output=True,
    )


def _make_fake_image(out_path: Path) -> None:
    subprocess.run(
        [FFMPEG, "-y", "-f", "lavfi", "-i", "color=c=blue:s=1280x720:d=1",
         "-frames:v", "1", str(out_path)],
        check=True, capture_output=True,
    )


def _patch_adr_io(tmpdir: Path, fake_raw_video: Path):
    """Mock 所有外部 IO 让 _lip_sync_one_group 不真调 WERYDANCE."""
    adr.OUTPUT_DIR = tmpdir
    adr._upload_to_weryai = lambda p: f"https://fake.upload/{Path(p).name}"
    adr._wait_motion_submit_slot = lambda *a, **kw: None
    adr._select_voice_asset_reference = lambda *a, **kw: None

    submit_calls = MagicMock(return_value={"data": {"task_id": "fake_task_123"}})
    adr.req_post = submit_calls

    adr.req_get = MagicMock(return_value={
        "data": {
            "task_status": "succeed",
            "videos": [str(fake_raw_video)],
        }
    })
    adr._extract_video_url = lambda data: str(fake_raw_video)

    # urllib.request.urlretrieve 拷贝 fake video 到目标
    import urllib.request

    def _fake_urlretrieve(url, dest):
        shutil.copy(fake_raw_video, dest)
        return dest, None

    urllib.request.urlretrieve = _fake_urlretrieve

    # _postprocess_audio_dub_segment 真跑会走 ffmpeg leading silence detect 等,
    # 这里简化: 把 src 直接 copy 到 vid_path 当通过
    def _fake_postprocess(src, scene, target_dur):
        # _lip_sync_one_group 传 src = scene["vid_path"] (split 已写入), 同 file 无需 copy
        if Path(src).resolve() != Path(scene["vid_path"]).resolve():
            shutil.copy(src, scene["vid_path"])
        return True

    adr._postprocess_audio_dub_segment = _fake_postprocess
    return submit_calls


def _make_group_inputs(tmpdir: Path, count: int = 2, duration: float = 1.0):
    panel = tmpdir / "panel.png"
    _make_fake_image(panel)
    script = []
    target_durs = []
    for i in range(count):
        audio = tmpdir / f"turn_{i}.wav"
        _make_fake_audio(audio, duration)
        script.append({
            "speaker": "罗永浩",
            "text": f"turn {i}",
            "dialogue_audio_mp3": str(audio),
            "img_path": str(panel),
            "vid_path": str(tmpdir / f"seg_{i}.mp4"),
            "needs_lip_sync": True,
            "dialogue_turn": i + 1,
        })
        target_durs.append(duration)
    return script, target_durs


def test_two_turn_group_basic():
    tmpdir = Path(tempfile.mkdtemp(prefix="pr_a_unit_"))
    print(f"\n[case 1] basic 2-turn group, tmpdir={tmpdir}")
    try:
        audio_a = tmpdir / "turn_0.wav"
        audio_b = tmpdir / "turn_1.wav"
        _make_fake_audio(audio_a, 4.0)
        _make_fake_audio(audio_b, 3.0)
        panel_a = tmpdir / "panel_0.png"
        panel_b = tmpdir / "panel_1.png"
        _make_fake_image(panel_a)
        _make_fake_image(panel_b)
        fake_raw = tmpdir / "fake_werydance_raw.mp4"
        _make_fake_video(fake_raw, 7.0)

        submit_calls = _patch_adr_io(tmpdir, fake_raw)

        script = [
            {"speaker": "罗永浩", "text": "第一段台词",
             "dialogue_audio_mp3": str(audio_a), "img_path": str(panel_a),
             "vid_path": str(tmpdir / "seg_0.mp4"),
             "needs_lip_sync": True, "voice_gender": "male", "dialogue_turn": 1},
            {"speaker": "罗永浩", "text": "第二段台词",
             "dialogue_audio_mp3": str(audio_b), "img_path": str(panel_b),
             "vid_path": str(tmpdir / "seg_1.mp4"),
             "needs_lip_sync": True, "voice_gender": "male", "dialogue_turn": 2},
        ]
        target_durs = [4.0, 3.0]

        idxs, oks, infos = adr._lip_sync_one_group([0, 1], script, target_durs, "16:9")

        assert idxs == [0, 1], f"idxs mismatch: {idxs}"
        assert all(oks), f"some turn failed: {oks}"
        assert submit_calls.call_count == 1, f"expected 1 submit call, got {submit_calls.call_count}"
        assert submit_calls.call_args.args[1]["model"] == adr.ALMIGHTY_MODEL
        concat_audio = tmpdir / "merged_a_group_0_1.wav"
        assert concat_audio.exists(), "audio concat 文件未生成"
        seg_0 = tmpdir / "seg_0.mp4"
        seg_1 = tmpdir / "seg_1.mp4"
        assert seg_0.exists() and seg_1.exists(), "seg split 文件未生成"
        for i, info in enumerate(infos):
            assert info["pass"], f"info[{i}].pass=False reason={info.get('reason')}"
            assert info.get("merged_a_group") == "group_0_1"
            assert info.get("merged_a_group_size") == 2
        print(f"  ✅ basic: 1 submit, 2 seg, audio concat OK, group_label=group_0_1")
    finally:
        print(f"  tmpdir kept: {tmpdir}")


def test_group_exceeds_15s():
    tmpdir = Path(tempfile.mkdtemp(prefix="pr_a_15s_"))
    print(f"\n[case 2] group > 15s should reject, tmpdir={tmpdir}")
    try:
        a1 = tmpdir / "long_a.wav"
        a2 = tmpdir / "long_b.wav"
        _make_fake_audio(a1, 9.0)
        _make_fake_audio(a2, 8.0)
        panel = tmpdir / "panel.png"
        _make_fake_image(panel)
        fake_raw = tmpdir / "fake.mp4"
        _make_fake_video(fake_raw, 5.0)

        _patch_adr_io(tmpdir, fake_raw)

        script = [
            {"speaker": "罗永浩", "text": "long a",
             "dialogue_audio_mp3": str(a1), "img_path": str(panel),
             "vid_path": str(tmpdir / "seg_0.mp4"),
             "needs_lip_sync": True, "voice_gender": "male", "dialogue_turn": 1},
            {"speaker": "罗永浩", "text": "long b",
             "dialogue_audio_mp3": str(a2), "img_path": str(panel),
             "vid_path": str(tmpdir / "seg_1.mp4"),
             "needs_lip_sync": True, "voice_gender": "male", "dialogue_turn": 2},
        ]
        target_durs = [9.0, 8.0]  # 总 17s > 15s
        idxs, oks, infos = adr._lip_sync_one_group([0, 1], script, target_durs, "16:9")
        assert not any(oks), "应全失败"
        for info in infos:
            assert "exceeds_15s" in info.get("reason", ""), f"reason 应含 exceeds_15s: {info}"
        print(f"  ✅ 15s cap reject 正常")
    finally:
        print(f"  tmpdir kept: {tmpdir}")


def test_missing_turn_audio():
    tmpdir = Path(tempfile.mkdtemp(prefix="pr_a_missing_"))
    print(f"\n[case 3] missing turn audio should reject, tmpdir={tmpdir}")
    try:
        audio_a = tmpdir / "turn_0.wav"
        _make_fake_audio(audio_a, 4.0)
        panel = tmpdir / "panel.png"
        _make_fake_image(panel)
        fake_raw = tmpdir / "fake.mp4"
        _make_fake_video(fake_raw, 5.0)

        _patch_adr_io(tmpdir, fake_raw)

        script = [
            {"speaker": "罗永浩", "text": "ok",
             "dialogue_audio_mp3": str(audio_a), "img_path": str(panel),
             "vid_path": str(tmpdir / "seg_0.mp4"),
             "needs_lip_sync": True, "voice_gender": "male", "dialogue_turn": 1},
            {"speaker": "罗永浩", "text": "missing audio",
             "dialogue_audio_mp3": str(tmpdir / "DOES_NOT_EXIST.wav"),
             "img_path": str(panel),
             "vid_path": str(tmpdir / "seg_1.mp4"),
             "needs_lip_sync": True, "voice_gender": "male", "dialogue_turn": 2},
        ]
        target_durs = [4.0, 3.0]
        idxs, oks, infos = adr._lip_sync_one_group([0, 1], script, target_durs, "16:9")
        assert not any(oks), "应全失败"
        assert any("missing_turn_audio" in i.get("reason", "") for i in infos), f"infos={infos}"
        print(f"  ✅ missing audio reject 正常")
    finally:
        print(f"  tmpdir kept: {tmpdir}")


def test_three_turn_group():
    tmpdir = Path(tempfile.mkdtemp(prefix="pr_a_3turn_"))
    print(f"\n[case 4] 3-turn group, tmpdir={tmpdir}")
    try:
        audios = []
        for i in range(3):
            a = tmpdir / f"turn_{i}.wav"
            _make_fake_audio(a, 3.0)
            audios.append(a)
        panel = tmpdir / "panel.png"
        _make_fake_image(panel)
        fake_raw = tmpdir / "fake.mp4"
        _make_fake_video(fake_raw, 9.0)  # actual 总 = 9s

        submit_calls = _patch_adr_io(tmpdir, fake_raw)

        script = []
        for i in range(3):
            script.append({
                "speaker": "罗永浩", "text": f"t{i}",
                "dialogue_audio_mp3": str(audios[i]), "img_path": str(panel),
                "vid_path": str(tmpdir / f"seg_{i}.mp4"),
                "needs_lip_sync": True, "voice_gender": "male", "dialogue_turn": i + 1,
            })
        target_durs = [3.0, 3.0, 3.0]

        idxs, oks, infos = adr._lip_sync_one_group([0, 1, 2], script, target_durs, "16:9")
        assert all(oks), f"some failed: {oks}"
        assert submit_calls.call_count == 1, f"expected 1 submit, got {submit_calls.call_count}"
        assert submit_calls.call_args.args[1]["model"] == adr.ALMIGHTY_MODEL
        for i in range(3):
            assert (tmpdir / f"seg_{i}.mp4").exists(), f"seg_{i} 未生成"
        # saved_api_calls = 3 - 1 = 2
        print(f"  ✅ 3-turn: 1 submit, 3 seg, 节省 2 次 API")
    finally:
        print(f"  tmpdir kept: {tmpdir}")


def test_group_timeout_resumes_without_resubmit():
    tmpdir = Path(tempfile.mkdtemp(prefix="pr_a_resume_"))
    print(f"\n[case 5] group timeout resumes without resubmit, tmpdir={tmpdir}")
    try:
        audios = []
        panels = []
        for i in range(2):
            audio = tmpdir / f"turn_{i}.wav"
            panel = tmpdir / f"panel_{i}.png"
            _make_fake_audio(audio, 3.0)
            _make_fake_image(panel)
            audios.append(audio)
            panels.append(panel)
        fake_raw = tmpdir / "unused.mp4"
        _make_fake_video(fake_raw, 6.0)
        submit_calls = _patch_adr_io(tmpdir, fake_raw)
        adr.time.sleep = lambda *_args, **_kwargs: None
        adr.req_get = MagicMock(return_value={"data": {"task_status": "processing"}})
        script = [
            {
                "speaker": "罗永浩",
                "text": f"pending {i}",
                "dialogue_audio_mp3": str(audios[i]),
                "img_path": str(panels[i]),
                "vid_path": str(tmpdir / f"seg_{i}.mp4"),
                "needs_lip_sync": True,
                "dialogue_turn": i + 1,
            }
            for i in range(2)
        ]

        first = adr._lip_sync_one_group([0, 1], script, [3.0, 3.0], "16:9")
        second = adr._lip_sync_one_group([0, 1], script, [3.0, 3.0], "16:9")

        assert submit_calls.call_count == 1, "resume must not create a second paid task"
        assert not any(first[1]) and not any(second[1])
        assert all(info.get("timed_out_or_reusable") for info in first[2] + second[2])
        cached = adr._load_lip_sync_tasks()[adr._merged_lip_sync_task_key([0, 1])]
        assert cached["task_id"] == "fake_task_123"
        assert adr._find_merged_lip_sync_task(0) is not None
        print("  ✅ timeout task cached and resumed with one submit")
    finally:
        print(f"  tmpdir kept: {tmpdir}")


def test_terminal_success_without_url_releases_cache():
    tmpdir = Path(tempfile.mkdtemp(prefix="pr_a_terminal_"))
    print(f"\n[case 6] terminal success without URL releases cache, tmpdir={tmpdir}")
    try:
        audios = []
        panels = []
        for i in range(2):
            audio = tmpdir / f"turn_{i}.wav"
            panel = tmpdir / f"panel_{i}.png"
            _make_fake_audio(audio, 3.0)
            _make_fake_image(panel)
            audios.append(audio)
            panels.append(panel)
        fake_raw = tmpdir / "unused.mp4"
        _make_fake_video(fake_raw, 6.0)
        _patch_adr_io(tmpdir, fake_raw)
        adr.req_get = MagicMock(return_value={"data": {"task_status": "succeed"}})
        adr._extract_video_url = lambda data: None
        script = [
            {
                "speaker": "罗永浩",
                "text": f"terminal {i}",
                "dialogue_audio_mp3": str(audios[i]),
                "img_path": str(panels[i]),
                "vid_path": str(tmpdir / f"seg_{i}.mp4"),
                "needs_lip_sync": True,
                "dialogue_turn": i + 1,
            }
            for i in range(2)
        ]

        result = adr._lip_sync_one_group([0, 1], script, [3.0, 3.0], "16:9")

        assert not any(result[1])
        assert all(info.get("reason") == "succeed_without_video_url" for info in result[2])
        assert adr._merged_lip_sync_task_key([0, 1]) not in adr._load_lip_sync_tasks()
        print("  terminal unusable task removed from cache")
    finally:
        print(f"  tmpdir kept: {tmpdir}")


def test_overlapping_merged_group_blocks_submit():
    tmpdir = Path(tempfile.mkdtemp(prefix="pr_a_overlap_group_"))
    print(f"\n[case 7] overlapping merged group blocks submit, tmpdir={tmpdir}")
    try:
        adr.OUTPUT_DIR = tmpdir
        adr.req_post = MagicMock(side_effect=AssertionError("overlap must not submit"))
        script = [{}, {}, {}]

        # Legacy records may expose their turns only through the merged key.
        adr._atomic_write_json(adr._lip_sync_tasks_file(), {"merged:0_1": "paid-legacy-group"})
        result = adr._lip_sync_one_group([0, 1, 2], script, [3.0, 3.0, 3.0], "16:9")
        assert not any(result[1])
        assert all(info.get("timed_out_or_reusable") for info in result[2])
        assert all(info.get("overlapping_task_key") == "merged:0_1" for info in result[2])

        # Structured records can use group_indices even when the key is nonstandard.
        adr._atomic_write_json(adr._lip_sync_tasks_file(), {
            "legacy-batch-record": {
                "task_id": "paid-structured-group",
                "mode": "merged-a-group",
                "group_indices": [1, 2],
            }
        })
        result = adr._lip_sync_one_group([0, 1, 2], script, [3.0, 3.0, 3.0], "16:9")
        assert not any(result[1])
        assert all(info.get("overlapping_task_key") == "legacy-batch-record" for info in result[2])
        assert adr.req_post.call_count == 0
        print("  overlapping legacy/structured group records both block paid submit")
    finally:
        print(f"  tmpdir kept: {tmpdir}")


def test_overlapping_single_turn_blocks_group_submit():
    tmpdir = Path(tempfile.mkdtemp(prefix="pr_a_overlap_turn_"))
    print(f"\n[case 8] pending single turn blocks group submit, tmpdir={tmpdir}")
    try:
        adr.OUTPUT_DIR = tmpdir
        adr.req_post = MagicMock(side_effect=AssertionError("overlap must not submit"))
        adr._atomic_write_json(adr._lip_sync_tasks_file(), {"1": "paid-single-turn"})

        result = adr._lip_sync_one_group([0, 1, 2], [{}, {}, {}], [3.0, 3.0, 3.0], "16:9")

        assert not any(result[1])
        assert all(info.get("timed_out_or_reusable") for info in result[2])
        assert all(info.get("overlapping_task_key") == "1" for info in result[2])
        assert adr.req_post.call_count == 0
        print("  pending single-turn task blocks overlapping group submit")
    finally:
        print(f"  tmpdir kept: {tmpdir}")


def test_cache_write_failure_after_submit_is_unresolved():
    tmpdir = Path(tempfile.mkdtemp(prefix="pr_a_cache_failure_"))
    print(f"\n[case 9] cache write failure after submit is unresolved, tmpdir={tmpdir}")
    original_save = adr._save_lip_sync_task
    try:
        script, target_durs = _make_group_inputs(tmpdir)
        submit_calls = _patch_adr_io(tmpdir, tmpdir / "unused.mp4")
        adr._save_lip_sync_task = MagicMock(side_effect=OSError("simulated cache failure"))

        result = adr._lip_sync_one_group([0, 1], script, target_durs, "16:9")

        assert submit_calls.call_count == 1
        assert not any(result[1])
        assert all(info.get("reason") == "task_cache_write_failed_after_submit" for info in result[2])
        assert all(info.get("task_id") == "fake_task_123" for info in result[2])
        assert all(info.get("timed_out_or_reusable") for info in result[2])
        print("  one paid submit; cache failure cannot trigger per-turn fallback")
    finally:
        adr._save_lip_sync_task = original_save
        print(f"  tmpdir kept: {tmpdir}")


def test_split_failure_keeps_cache_and_reuses_raw_video():
    tmpdir = Path(tempfile.mkdtemp(prefix="pr_a_split_retry_"))
    print(f"\n[case 10] split failure keeps cache/raw for local retry, tmpdir={tmpdir}")
    original_split = adr._split_lip_sync_raw_by_durations
    try:
        script, target_durs = _make_group_inputs(tmpdir)
        fake_raw = tmpdir / "fake_remote_raw.mp4"
        _make_fake_video(fake_raw, 2.0)
        submit_calls = _patch_adr_io(tmpdir, fake_raw)
        status_calls = adr.req_get
        adr._split_lip_sync_raw_by_durations = MagicMock(return_value=False)

        first = adr._lip_sync_one_group([0, 1], script, target_durs, "16:9")
        second = adr._lip_sync_one_group([0, 1], script, target_durs, "16:9")

        cache_key = adr._merged_lip_sync_task_key([0, 1])
        raw_path = Path(adr._lip_sync_group_raw_path("group_0_1", "fake_task_123"))
        assert submit_calls.call_count == 1
        assert status_calls.call_count == 1, "second local retry must reuse downloaded raw video"
        assert cache_key in adr._load_lip_sync_tasks()
        assert raw_path.exists()
        for result in (first, second):
            assert not any(result[1])
            assert all(info.get("remote_task_succeeded") for info in result[2])
            assert all(info.get("local_retryable") for info in result[2])
            assert all(info.get("timed_out_or_reusable") for info in result[2])
        print("  split retry uses one submit/one poll and preserves raw video")
    finally:
        adr._split_lip_sync_raw_by_durations = original_split
        print(f"  tmpdir kept: {tmpdir}")


def test_postprocess_failure_keeps_cache_until_local_success():
    tmpdir = Path(tempfile.mkdtemp(prefix="pr_a_postprocess_retry_"))
    print(f"\n[case 11] postprocess failure keeps cache until local success, tmpdir={tmpdir}")
    try:
        script, target_durs = _make_group_inputs(tmpdir)
        fake_raw = tmpdir / "fake_remote_raw.mp4"
        _make_fake_video(fake_raw, 2.0)
        submit_calls = _patch_adr_io(tmpdir, fake_raw)
        status_calls = adr.req_get
        adr._postprocess_audio_dub_segment = MagicMock(side_effect=[True, False])

        first = adr._lip_sync_one_group([0, 1], script, target_durs, "16:9")
        cache_key = adr._merged_lip_sync_task_key([0, 1])
        assert first[1] == [True, False]
        assert cache_key in adr._load_lip_sync_tasks()
        assert all(info.get("remote_task_succeeded") for info in first[2])
        assert all(info.get("local_retryable") for info in first[2])
        assert all(info.get("timed_out_or_reusable") for info in first[2])

        adr._postprocess_audio_dub_segment = MagicMock(return_value=True)
        second = adr._lip_sync_one_group([0, 1], script, target_durs, "16:9")
        assert all(second[1])
        assert submit_calls.call_count == 1
        assert status_calls.call_count == 1, "local retry must not poll or resubmit"
        assert cache_key not in adr._load_lip_sync_tasks()
        assert Path(adr._lip_sync_group_raw_path("group_0_1", "fake_task_123")).exists()
        print("  cache clears only after all local postprocessing succeeds")
    finally:
        print(f"  tmpdir kept: {tmpdir}")


def test_stale_legacy_raw_does_not_bypass_cached_task_poll():
    tmpdir = Path(tempfile.mkdtemp(prefix="pr_a_stale_raw_"))
    print(f"\n[case 12] stale legacy raw cannot satisfy a newer cached task, tmpdir={tmpdir}")
    try:
        script, target_durs = _make_group_inputs(tmpdir)
        new_remote_raw = tmpdir / "new_remote_raw.mp4"
        _make_fake_video(new_remote_raw, 2.0)
        _patch_adr_io(tmpdir, new_remote_raw)
        no_submit = MagicMock(side_effect=AssertionError("cached task must not resubmit"))
        adr.req_post = no_submit
        adr._atomic_write_json(adr._lip_sync_tasks_file(), {
            "merged:0_1": {
                "task_id": "new-paid-task",
                "model": "WERYDANCE",
                "mode": "merged-a-group",
                "group_indices": [0, 1],
                "split_durations": [1.0, 1.0],
                "target_durations": [1.0, 1.0],
            }
        })

        stale_raw = tmpdir / "lip_sync_raw_group_0_1.mp4"
        _make_fake_video(stale_raw, 6.0)
        result = adr._lip_sync_one_group([0, 1], script, target_durs, "16:9")

        expected_raw = Path(adr._lip_sync_group_raw_path("group_0_1", "new-paid-task"))
        assert all(result[1])
        assert no_submit.call_count == 0
        assert adr.req_get.call_count == 1, "new cached task must be polled despite stale legacy raw"
        assert expected_raw.exists() and stale_raw.exists()
        assert expected_raw != stale_raw
        assert all(info.get("raw_video_path") == str(expected_raw) for info in result[2])
        print("  stale group raw ignored; cached task polled and downloaded to task-bound path")
    finally:
        print(f"  tmpdir kept: {tmpdir}")


def test_legacy_cache_without_durations_resumes_without_submit():
    tmpdir = Path(tempfile.mkdtemp(prefix="pr_a_legacy_resume_"))
    print(f"\n[case 13] legacy cached group derives split durations locally, tmpdir={tmpdir}")
    try:
        script, target_durs = _make_group_inputs(tmpdir)
        remote_raw = tmpdir / "legacy_remote_raw.mp4"
        _make_fake_video(remote_raw, 2.0)
        _patch_adr_io(tmpdir, remote_raw)
        no_submit = MagicMock(side_effect=AssertionError("legacy cached task must not resubmit"))
        adr.req_post = no_submit
        adr._atomic_write_json(adr._lip_sync_tasks_file(), {
            "merged:0_1": "legacy-paid-task",
        })

        result = adr._lip_sync_one_group([0, 1], script, target_durs, "16:9")

        assert all(result[1])
        assert no_submit.call_count == 0
        assert adr.req_get.call_count == 1
        assert Path(adr._lip_sync_group_raw_path("group_0_1", "legacy-paid-task")).exists()
        print("  legacy cache resumed with derived audio durations and zero paid submits")
    finally:
        print(f"  tmpdir kept: {tmpdir}")


def test_concurrent_group_submit_transaction_creates_one_paid_task():
    tmpdir = Path(tempfile.mkdtemp(prefix="pr_a_concurrent_submit_"))
    print(f"\n[case 14] concurrent group transaction creates one paid task, tmpdir={tmpdir}")
    try:
        adr.OUTPUT_DIR = tmpdir
        adr.req_post = MagicMock(return_value={"data": {"task_id": "single-paid-task"}})
        payload = {
            "model": "WERYDANCE",
            "images": ["https://example.invalid/panel.jpg"],
            "prompt": "offline concurrency test",
            "duration": 4,
            "resolution": "720p",
        }

        def submit_once():
            return adr._submit_lip_sync_task_transaction(
                "merged:0_1",
                [0, 1],
                payload,
                model="WERYDANCE",
                metadata={"mode": "merged-a-group", "group_indices": [0, 1]},
            )

        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda _value: submit_once(), range(2)))

        assert adr.req_post.call_count == 1, "concurrent callers must create only one paid task"
        assert sum(result.get("task_id") == "single-paid-task" for result in results) == 1
        assert sum(result.get("conflict_key") == "merged:0_1" for result in results) == 1
        cached = adr._load_lip_sync_tasks()["merged:0_1"]
        assert cached["task_id"] == "single-paid-task"
        print("  two concurrent callers produced one POST and one cached conflict")
    finally:
        print(f"  tmpdir kept: {tmpdir}")


def test_group_and_single_submit_share_overlap_transaction():
    tmpdir = Path(tempfile.mkdtemp(prefix="pr_a_group_single_race_"))
    print(f"\n[case 15] group and single transactions cannot both submit, tmpdir={tmpdir}")
    try:
        adr.OUTPUT_DIR = tmpdir
        task_counter = 0

        def post_once(*_args, **_kwargs):
            nonlocal task_counter
            task_counter += 1
            return {"data": {"task_id": f"paid-task-{task_counter}"}}

        adr.req_post = MagicMock(side_effect=post_once)
        payload = {
            "model": "WERYDANCE",
            "images": ["https://example.invalid/panel.jpg"],
            "prompt": "offline overlap test",
            "duration": 4,
            "resolution": "720p",
        }

        with ThreadPoolExecutor(max_workers=2) as pool:
            group_future = pool.submit(
                adr._submit_lip_sync_task_transaction,
                "merged:0_1", [0, 1], payload,
                model="WERYDANCE",
                metadata={"mode": "merged-a-group", "group_indices": [0, 1]},
            )
            scene_future = pool.submit(
                adr._submit_lip_sync_task_transaction,
                1, [1], payload,
                model="WERYDANCE",
                metadata={"variant": "single-turn"},
            )
            results = [group_future.result(), scene_future.result()]

        assert adr.req_post.call_count == 1
        assert sum(bool(result.get("task_id")) for result in results) == 1
        assert sum(bool(result.get("conflict_record")) for result in results) == 1
        assert len(adr._load_lip_sync_tasks()) == 1
        print("  overlapping group/single callers produced exactly one POST")
    finally:
        print(f"  tmpdir kept: {tmpdir}")


def test_submit_exception_is_unknown_and_not_retried():
    tmpdir = Path(tempfile.mkdtemp(prefix="pr_a_submit_unknown_"))
    print(f"\n[case 16] submit exception is outcome-unknown and never retried, tmpdir={tmpdir}")
    try:
        adr.OUTPUT_DIR = tmpdir
        adr.req_post = MagicMock(side_effect=TimeoutError("response lost after POST"))
        result = adr._submit_lip_sync_task_transaction(
            "merged:0_1",
            [0, 1],
            {
                "model": "WERYDANCE",
                "images": ["https://example.invalid/panel.jpg"],
                "prompt": "offline unknown-outcome test",
                "duration": 4,
                "resolution": "720p",
            },
            model="WERYDANCE",
            metadata={"mode": "merged-a-group", "group_indices": [0, 1]},
        )

        assert adr.req_post.call_count == 1
        assert result.get("outcome_unknown") is True
        assert isinstance(result.get("submit_error"), TimeoutError)
        assert result.get("task_id") is None
        reservation = adr._load_lip_sync_tasks()["merged:0_1"]
        assert adr._is_lip_sync_submission_reservation(reservation)
        print("  one POST attempt; timeout marked unknown for operator reconciliation")
    finally:
        print(f"  tmpdir kept: {tmpdir}")


def test_submission_reservation_is_not_polled_as_remote_task():
    tmpdir = Path(tempfile.mkdtemp(prefix="pr_a_reservation_resume_"))
    print(f"\n[case 17] persisted reservation blocks submit without fake polling, tmpdir={tmpdir}")
    try:
        script, target_durs = _make_group_inputs(tmpdir)
        adr.OUTPUT_DIR = tmpdir
        adr.req_get = MagicMock(side_effect=AssertionError("reservation is not a remote task_id"))
        adr.req_post = MagicMock(side_effect=AssertionError("reservation must block resubmit"))
        adr._atomic_write_json(adr._lip_sync_tasks_file(), {
            "merged:0_1": {
                "task_id": "submission-pending:unknown",
                "model": "WERYDANCE",
                "mode": "merged-a-group",
                "group_indices": [0, 1],
                "submission_state": "submitting",
                "split_durations": [1.0, 1.0],
            }
        })

        result = adr._lip_sync_one_group([0, 1], script, target_durs, "16:9")

        assert not any(result[1])
        assert all(info.get("reason") == "submit_outcome_unknown" for info in result[2])
        assert adr.req_get.call_count == 0
        assert adr.req_post.call_count == 0
        print("  reservation remains unresolved with zero GET/POST calls")
    finally:
        print(f"  tmpdir kept: {tmpdir}")


def main():
    print("=== PR-A merged_a unit test ===")
    test_two_turn_group_basic()
    test_group_exceeds_15s()
    test_missing_turn_audio()
    test_three_turn_group()
    test_group_timeout_resumes_without_resubmit()
    test_terminal_success_without_url_releases_cache()
    test_overlapping_merged_group_blocks_submit()
    test_overlapping_single_turn_blocks_group_submit()
    test_cache_write_failure_after_submit_is_unresolved()
    test_split_failure_keeps_cache_and_reuses_raw_video()
    test_postprocess_failure_keeps_cache_until_local_success()
    test_stale_legacy_raw_does_not_bypass_cached_task_poll()
    test_legacy_cache_without_durations_resumes_without_submit()
    test_concurrent_group_submit_transaction_creates_one_paid_task()
    test_group_and_single_submit_share_overlap_transaction()
    test_submit_exception_is_unknown_and_not_retried()
    test_submission_reservation_is_not_polled_as_remote_task()
    print("\n=== 17/17 PASSED ===")


if __name__ == "__main__":
    main()
