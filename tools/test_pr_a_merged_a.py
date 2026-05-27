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
        for i in range(3):
            assert (tmpdir / f"seg_{i}.mp4").exists(), f"seg_{i} 未生成"
        # saved_api_calls = 3 - 1 = 2
        print(f"  ✅ 3-turn: 1 submit, 3 seg, 节省 2 次 API")
    finally:
        print(f"  tmpdir kept: {tmpdir}")


def main():
    print("=== PR-A merged_a unit test ===")
    test_two_turn_group_basic()
    test_group_exceeds_15s()
    test_missing_turn_audio()
    test_three_turn_group()
    print("\n=== 4/4 PASSED ===")


if __name__ == "__main__":
    main()
