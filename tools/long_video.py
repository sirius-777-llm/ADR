#!/usr/bin/env python3
"""B69 (2026-05-30): 长文分段渲染 — 生产级 chunk 衔接编排器.

进化自 B66 tools/long_text_runner.py (裸 chunk 多 run + ffmpeg -c copy concat,
chunk 间叙事/视觉/听感断裂, 且无论长短都强切). B69 升级:

  1. 内容驱动 gate (铁律: 长度由内容决定) — 句数 <= SINGLE_RUN_MAX 走单 run 不切,
     仅真长文超单 run 容量才 chunk. 短题材绝不被切被注水.
  2. manifest (b69_manifest.json, Codex Stage 2 方案 B 的种子) — 每段声明句范围/
     资源策略/状态/验收, 原子写, 支持 resume + 完整性校验.
  3. BGM 连贯 — chunk1 先跑生成 bgm.mp3, chunk2..N 经 ADR_CHUNK_BGM_REUSE env 复用同轨.
  4. fail-loud + retry — 单 chunk 超时 + 重试, 仍失败则中止整片 (不静默丢部分, 古文缺段=bug).
  5. 边界守卫 (Codex Stage 1) — 跳空 chunk / 严格顺序 / 去重 / audit 留痕.
  6. concat — 默认 xfade+acrossfade 1s 平滑过渡 (A/V 同步), 失败回退 -c copy.

跨 chunk character_meta_grid 复用 (ROADMAP #1) 已由 run_adr_v8.py 的 speaker 级缓存
自动实现, 无需本工具处理. 字幕 (ROADMAP #3) 每 chunk 烧录, concat 自动保留, 无需重编号.

二期 (B69.x) 留: 并行 chunk / chunk_size 自适应 / LLM 衔接 prompt (仅生成台词题材).

usage:
  python3 tools/long_video.py "滕王阁序" /path/to/full_text.txt --fmt h
  python3 tools/long_video.py "滕王阁序" full.txt --dry-run          # 只出 manifest 计划, 不渲染
  python3 tools/long_video.py "滕王阁序" full.txt --resume           # 复用已完成 chunk
"""
import argparse
import json
import os
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools.long_text_split import split_long_text  # noqa: E402

ADR_SCRIPT = str(ROOT / "run_adr_v8.py")
PYTHON = "/opt/homebrew/bin/python3"
FFMPEG = "/opt/homebrew/bin/ffmpeg"
FFPROBE = "/opt/homebrew/bin/ffprobe"

MANIFEST_SCHEMA = "b69_long_video_manifest_v1"

# 内容驱动 gate / 分段默认 (env 可覆盖)
DEFAULT_SINGLE_RUN_MAX = int(os.environ.get("ADR_LONGVIDEO_SINGLE_RUN_MAX", "30"))
DEFAULT_CHUNK_SIZE = int(os.environ.get("ADR_LONGVIDEO_CHUNK_SIZE", "12"))
DEFAULT_CROSSFADE_SEC = float(os.environ.get("ADR_LONGVIDEO_CROSSFADE_SEC", "1.0"))
DEFAULT_TIMEOUT = int(os.environ.get("ADR_LONGVIDEO_CHUNK_TIMEOUT", "14400"))  # 4h: 12-scene grid_multiref + WERYDANCE 重试现实值 (E2E 实测 1h 太紧)
DEFAULT_RETRIES = int(os.environ.get("ADR_LONGVIDEO_RETRIES", "1"))


# ── manifest helpers ────────────────────────────────────────────────────────

def _atomic_write_json(path: Path, obj: dict) -> None:
    """原子写 (临时文件 + rename), 防写一半被读到坏 json."""
    tmp = path.with_suffix(path.suffix + f".tmp{os.getpid()}")
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.rename(path)


def _load_manifest(path: Path) -> dict | None:
    if path.exists():
        try:
            m = json.loads(path.read_text(encoding="utf-8"))
            if m.get("schema") == MANIFEST_SCHEMA:
                return m
        except Exception:
            pass
    return None


def _final_mp4_belongs(path: str | None, run_root: Path) -> bool:
    """final_mp4 必须存在且在 run_root 内 (防 resume manifest 注入外部/篡改路径 — Codex H1/H2)."""
    if not path or "\n" in path:
        return False
    try:
        rp = Path(path).resolve()
    except Exception:
        return False
    if not rp.is_file():
        return False
    return run_root.resolve() in rp.parents


def _outdir_belongs(out_dir: Path, run_root: Path) -> bool:
    """out_dir 必须是 run_root 的直接子目录且名为 out_* —— rmtree 前的安全校验，
    防篡改 manifest 把 output_dir 指向别处导致误删 (Codex review Med2)."""
    try:
        return out_dir.resolve().parent == run_root.resolve() and out_dir.name.startswith("out_")
    except Exception:
        return False


def build_plan(text: str, chunk_size: int, single_run_max: int) -> tuple[str, list[list[str]]]:
    """内容驱动 gate: 返回 (mode, chunks).

    - 句数 <= single_run_max → mode='single_run', chunks=[全部句] (单 run, 不 concat).
    - 否则 → mode='chunked', 按 chunk_size 切.

    复用 B66 split_long_text 做句切 (已处理末句无标点 + 空文本).
    """
    # 先整体当 1 段切出所有句子 (chunk_size 极大), 拿到干净句列表
    all_sentences_nested = split_long_text(text, chunk_size=10_000_000)
    sentences = all_sentences_nested[0] if all_sentences_nested else []
    # 边界守卫: 去掉空句 (Codex Stage 1)
    sentences = [s for s in (x.strip() for x in sentences) if s]
    if not sentences:
        return ("single_run", [])
    if len(sentences) <= single_run_max:
        return ("single_run", [sentences])
    chunks: list[list[str]] = []
    for i in range(0, len(sentences), chunk_size):
        chunk = sentences[i:i + chunk_size]
        if chunk:  # 边界守卫: 不产空 chunk
            chunks.append(chunk)
    return ("chunked", chunks)


def init_manifest(topic: str, fmt: str, mode: str, chunks: list[list[str]],
                  chunk_size: int, single_run_max: int, crossfade_sec: float,
                  run_root: Path, created_at: float) -> dict:
    segments = []
    cursor = 0
    for idx, chunk in enumerate(chunks):
        segments.append({
            "idx": idx,
            "sentence_start": cursor,
            "sentence_end": cursor + len(chunk),
            "sentences": chunk,
            "n_sentences": len(chunk),
            "status": "pending",
            "override_file": str(run_root / f"chunk_{idx:02d}.txt"),
            "output_dir": str(run_root / f"out_{idx:02d}"),
            "final_mp4": None,
            "render_seconds": None,
            "attempts": 0,
            "last_error": None,
        })
        cursor += len(chunk)
    return {
        "schema": MANIFEST_SCHEMA,
        "topic": topic,
        "fmt": fmt,
        "mode": mode,
        "created_at": created_at,
        "total_sentences": sum(len(c) for c in chunks),
        "chunk_size": chunk_size,
        "single_run_max": single_run_max,
        "crossfade_sec": crossfade_sec,
        "bgm_master": None,
        "run_root": str(run_root),
        "final_output": None,
        "segments": segments,
    }


# ── 单 chunk 渲染 ────────────────────────────────────────────────────────────

def _find_final_mp4(out_dir: str) -> str | None:
    cands = sorted(Path(out_dir).glob("ADR_V8_*.mp4"),
                   key=lambda p: p.stat().st_mtime, reverse=True)
    return str(cands[0]) if cands else None


def _kill_proc_group(proc: "subprocess.Popen", hard: bool = False) -> None:
    """杀掉 proc 所在进程组 (Popen start_new_session=True 建的), 连 ADR 派生的
    ffmpeg/curl 子进程一起杀, 防孤儿残留 (Codex High). 兜底单杀 proc."""
    sig = signal.SIGKILL if hard else signal.SIGTERM
    try:
        os.killpg(os.getpgid(proc.pid), sig)
    except Exception:
        try:
            proc.kill() if hard else proc.terminate()
        except Exception:
            pass


def run_one_chunk(seg: dict, topic: str, fmt: str, extra_args: list[str],
                  bgm_master: str | None, timeout: int, retries: int, run_root: Path) -> bool:
    """跑单段 ADR (含 retry). 直接更新 seg dict. 成功返回 True.

    用 per-chunk ADR_SCRIPT_OVERRIDE + OUTPUT_DIR env (确定性, 不靠 log 解析),
    chunk2..N 经 ADR_CHUNK_BGM_REUSE 复用 chunk1 BGM.
    """
    override_file = Path(seg["override_file"])
    out_dir = Path(seg["output_dir"])
    # 安全: out_dir 必须是 run_root/out_* (rmtree 前防篡改 manifest 误删别处 — Codex Med2)
    if not _outdir_belongs(out_dir, run_root):
        seg["last_error"] = f"output_dir 非法(非 run_root/out_*): {out_dir}"
        seg["status"] = "failed"
        print(f"   ❌ chunk {seg['idx']} output_dir 安全校验失败, 拒绝渲染/清理: {out_dir}", file=sys.stderr)
        return False
    override_file.parent.mkdir(parents=True, exist_ok=True)
    override_file.write_text("\n".join(seg["sentences"]) + "\n", encoding="utf-8")

    env = dict(os.environ)
    env["ADR_SCRIPT_OVERRIDE"] = str(override_file)
    env["OUTPUT_DIR"] = str(out_dir)
    env.setdefault("ADR_TG_PROGRESS_MODE", "silent")  # 抑制 per-chunk TG 刷屏 (可被外部 env 覆盖)
    if bgm_master and os.path.exists(bgm_master):
        env["ADR_CHUNK_BGM_REUSE"] = bgm_master

    cmd = [PYTHON, ADR_SCRIPT, topic, fmt] + extra_args
    log_path = str(out_dir.parent / f"chunk_{seg['idx']:02d}.log")

    max_attempts = max(1, 1 + retries)
    for attempt in range(1, max_attempts + 1):
        seg["attempts"] = attempt
        seg["status"] = "running"
        # 清空 out_dir 起干净 slate: 防上次失败/部分渲染的残片污染 ADR 本次 run (E2E fix)
        if out_dir.exists():
            shutil.rmtree(out_dir, ignore_errors=True)
            if out_dir.exists() and any(out_dir.iterdir()):  # 删不彻底要 fail-loud 不静默 (Codex Med1)
                print(f"   ⚠️ chunk {seg['idx']} out_dir 清理不彻底, 残片可能影响渲染: {out_dir}")
        out_dir.mkdir(parents=True, exist_ok=True)
        print(f"\n=== chunk {seg['idx']} (attempt {attempt}/{max_attempts}): "
              f"{seg['n_sentences']} 句 → {out_dir} ===")
        t0 = time.time()
        # E2E 实测: ADR 干完活(含成片)后因残留非守护线程/连接池(CLOSE_WAIT)不退出, 卡 ~1h.
        # subprocess.run 会死等退出 → 改 Popen + 轮询: 最终 mp4 生成且 ffprobe 有效且大小连续两轮稳定即收割.
        # start_new_session=True 建独立进程组, 收割时 killpg 连 ADR 派生的 ffmpeg/curl 一起杀 (Codex High).
        # mp4 在 step9 生成、step10 TG 推送之前 → 提前收割顺带跳过 per-chunk 推送(只让最终拼接片推 TG).
        try:
            lf = open(log_path, "w")
        except Exception as e:
            seg["last_error"] = f"日志打开失败: {e}"
            print(f"   ❌ chunk {seg['idx']} 日志打开失败: {e}")
            continue
        try:
            proc = subprocess.Popen(cmd, stdout=lf, stderr=subprocess.STDOUT,
                                    env=env, start_new_session=True)
        except Exception as e:
            lf.close()  # Codex Low: Popen 失败也要关 lf
            seg["last_error"] = f"启动失败 {type(e).__name__}: {e}"
            print(f"   ❌ chunk {seg['idx']} 启动失败: {e}")
            continue

        outcome, rc, final, last_size = None, None, None, -1
        try:
            while True:
                rc = proc.poll()
                if rc is not None:
                    outcome = "exited"; break
                if time.time() - t0 > timeout:
                    _kill_proc_group(proc)
                    outcome = "timeout"; break
                cand = _find_final_mp4(str(out_dir))
                if cand and _ffprobe_duration(cand):
                    sz = os.path.getsize(cand)
                    if sz > 0 and sz == last_size:  # 连续两轮大小稳定 = 写完, 防边写边探 race (Codex Med)
                        _kill_proc_group(proc)
                        final, outcome = cand, "reaped"; break
                    last_size = sz
                time.sleep(5)
        finally:
            try: lf.close()
            except Exception: pass
        # 统一收割兜底, 不留 zombie/orphan (Codex Med): SIGTERM 已发, wait 不掉则 SIGKILL 整组
        try:
            proc.wait(20)
        except Exception:
            _kill_proc_group(proc, hard=True)
            try: proc.wait(10)
            except Exception: pass

        seg["render_seconds"] = round(time.time() - t0, 1)

        if outcome == "timeout":
            seg["last_error"] = f"timeout {timeout}s (attempt {attempt})"
            # 超时不重试: 同 workload + 同 timeout 重跑必再超时, 白烧一个 timeout (E2E fix)
            print(f"   ⏱ chunk {seg['idx']} 超时 {timeout}s, 不重试, log: {log_path}")
            break

        # reaped 已有 final; exited 路径重新探一次 (rc 可非 0/负=被信号 → 成片已出也救回)
        if not final:
            cand = _find_final_mp4(str(out_dir))
            final = cand if (cand and _ffprobe_duration(cand)) else None
        if not final:
            seg["last_error"] = f"无有效成片 (outcome={outcome}, rc={rc}), log: {log_path}"
            print(f"   ❌ chunk {seg['idx']} 无有效成片 (outcome={outcome}, rc={rc})")
            continue  # 崩溃/无产出 可重试

        if outcome == "exited" and rc not in (0, None):  # Codex Low: 记 warning 便于追踪信号终止
            print(f"   ⚠️ chunk {seg['idx']} 进程 rc={rc}(疑被信号终止) 但成片有效, 救回")
        seg["final_mp4"] = final
        seg["status"] = "done"
        seg["last_error"] = None
        via = "提前收割·跳过step10推送" if outcome == "reaped" else f"进程自退rc={rc}"
        print(f"   ✅ chunk {seg['idx']} → {final} ({seg['render_seconds']}s · {via})")
        return True

    seg["status"] = "failed"
    return False


# ── concat (xfade+acrossfade 平滑 / -c copy 兜底) ────────────────────────────

def _ffprobe_duration(path: str) -> float | None:
    try:
        r = subprocess.run(
            [FFPROBE, "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", path],
            capture_output=True, text=True, timeout=60)
        if r.returncode == 0:
            d = float(r.stdout.strip())
            if d > 0 and d == d and d != float("inf"):  # 防 0/NaN/inf
                return d
    except Exception:
        pass
    return None


def _ffprobe_stream_duration(path: str, stream: str) -> float | None:
    """探单条流 (stream='v'/'a') 的时长. crossfade 需各段 video/audio 等长防 A/V 漂移."""
    try:
        r = subprocess.run(
            [FFPROBE, "-v", "error", "-select_streams", stream, "-show_entries",
             "stream=duration", "-of", "default=noprint_wrappers=1:nokey=1", path],
            capture_output=True, text=True, timeout=60)
        if r.returncode == 0:
            line = (r.stdout.strip().splitlines() or [""])[0].strip()
            if line and line not in ("N/A",):
                d = float(line)
                if d > 0 and d == d and d != float("inf"):
                    return d
    except Exception:
        pass
    return None


def build_crossfade_filter(durations: list[float], c: float) -> tuple[str, str, str]:
    """构造 N 段 xfade(视频)+acrossfade(音频) filter_complex.

    视频/音频每次合并都减 c 秒重叠 → A/V 始终同步. 返回 (filter, v_label, a_label).
    """
    n = len(durations)
    parts: list[str] = []
    prev_v = "[0:v]"
    prev_a = "[0:a]"
    running = durations[0]
    for k in range(1, n):
        off = max(0.0, running - c)
        vout = f"[v{k}]"
        aout = f"[a{k}]"
        parts.append(f"{prev_v}[{k}:v]xfade=transition=fade:duration={c}:offset={off:.3f}{vout}")
        parts.append(f"{prev_a}[{k}:a]acrossfade=d={c}{aout}")
        prev_v, prev_a = vout, aout
        running = running + durations[k] - c
    return ";".join(parts), prev_v, prev_a


def concat_segments(paths: list[str], out_path: str, crossfade_sec: float) -> bool:
    """合并多段. crossfade_sec>0 走 xfade+acrossfade 重编码, 失败/关闭回退 -c copy."""
    if not paths:
        return False
    if len(paths) == 1:
        shutil.copyfile(paths[0], out_path)
        return os.path.exists(out_path) and os.path.getsize(out_path) > 100_000

    if crossfade_sec and crossfade_sec > 0:
        # 用各段 video/audio 流时长 (非容器时长): 仅当每段 |v-a|<=0.3s 才 crossfade,
        # 否则 xfade(按 v offset)与 acrossfade(按 a)会累积 A/V 漂移 → 回退 -c copy (Codex M1)
        vdurs = [_ffprobe_stream_duration(p, "v") for p in paths]
        adurs = [_ffprobe_stream_duration(p, "a") for p in paths]
        av_ok = (all(d is not None for d in vdurs) and all(d is not None for d in adurs)
                 and all(abs(v - a) <= 0.3 for v, a in zip(vdurs, adurs)))  # type: ignore[arg-type]
        if av_ok:
            try:
                filt, vlab, alab = build_crossfade_filter(vdurs, crossfade_sec)  # type: ignore[arg-type]
                cmd = [FFMPEG, "-y"]
                for p in paths:
                    cmd += ["-i", p]
                cmd += [
                    "-filter_complex", filt,
                    "-map", vlab, "-map", alab,
                    "-c:v", "libx264", "-crf", "20", "-preset", "medium",
                    "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "192k",
                    out_path,
                ]
                r = subprocess.run(cmd, capture_output=True, timeout=1800)
                if r.returncode == 0 and os.path.exists(out_path) and os.path.getsize(out_path) > 100_000:
                    print(f"✅ crossfade concat ({crossfade_sec}s) ok")
                    return True
                print(f"⚠️ crossfade concat fail, 回退 -c copy: {r.stderr.decode()[-300:]}")
            except Exception as e:
                print(f"⚠️ crossfade concat 异常, 回退 -c copy: {e}")
        else:
            print("⚠️ A/V 流长不一致或探测失败, 跳过 crossfade 回退 -c copy concat")

    # 兜底: -c copy concat demuxer (要求各段同 codec, scout 已确认一致).
    # concat 格式单引号需转义为 '\'' (Codex H1); 路径已在 main 校验归属+无换行
    concat_list = Path(out_path).with_suffix(".concat.txt")
    concat_list.write_text(
        "\n".join("file '{}'".format(p.replace("'", "'\\''")) for p in paths),
        encoding="utf-8")
    cmd = [FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", str(concat_list), "-c", "copy", out_path]
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=600)
        if r.returncode != 0:
            print(f"❌ -c copy concat fail: {r.stderr.decode()[-300:]}")
            return False
        return os.path.exists(out_path) and os.path.getsize(out_path) > 100_000
    except Exception as e:
        print(f"❌ concat 异常: {e}")
        return False


def validate_output(out_path: str, manifest: dict) -> bool:
    """按 manifest 校验成片: 存在 + 时长 ≈ 各段和 (扣 crossfade 重叠), 容差 ±15%."""
    if not (os.path.exists(out_path) and os.path.getsize(out_path) > 100_000):
        print("❌ 校验: 成片不存在或过小")
        return False
    dur = _ffprobe_duration(out_path)
    seg_durs = [_ffprobe_duration(s["final_mp4"]) for s in manifest["segments"] if s.get("final_mp4")]
    if dur is None or not all(d is not None for d in seg_durs):
        print(f"⚠️ 校验: 时长探测失败 (成片 {dur}), 仅验存在性")
        return True
    n = len(seg_durs)
    expected = sum(seg_durs) - max(0, n - 1) * (manifest.get("crossfade_sec") or 0)  # type: ignore[operator]
    lo, hi = expected * 0.85, expected * 1.15
    ok = lo <= dur <= hi
    print(f"{'✅' if ok else '⚠️'} 校验: 成片 {dur:.1f}s vs 预期 ~{expected:.1f}s [{lo:.0f},{hi:.0f}]")
    return ok


def _tg_send_final(out_path: str, topic: str, manifest: dict) -> None:
    """best-effort 把成片推 TG (仅 keys 存在时). 无 key (如本机 design 环境) 直接跳过."""
    token = os.environ.get("TG_BOT_TOKEN", "").strip()
    chat = os.environ.get("TG_CHAT_ID", "").strip()
    if not (token and chat):
        print("ℹ️ 无 TG_BOT_TOKEN/TG_CHAT_ID, 跳过 TG 推送 (成片在上面路径)")
        return
    size_mb = os.path.getsize(out_path) / 1e6
    method = "sendVideo" if size_mb <= 48 else "sendDocument"
    field = "video" if method == "sendVideo" else "document"
    n_seg = len(manifest["segments"])
    caption = f"🎬 B69 长视频 · {topic}\n{n_seg} 段 · {manifest['mode']} · {size_mb:.0f}MB"
    try:
        subprocess.run(
            ["curl", "-sS", "-F", f"chat_id={chat}", "-F", f"caption={caption}",
             "-F", f"{field}=@{out_path}",
             f"https://api.telegram.org/bot{token}/{method}"],
            capture_output=True, timeout=600)
        print(f"📤 TG {method} 已尝试 ({size_mb:.0f}MB)")
    except Exception as e:
        print(f"⚠️ TG 推送异常 (不影响成片): {e}")


# ── main ─────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description="B69 长文分段渲染 (内容驱动 + manifest)")
    ap.add_argument("topic", help="ADR topic (e.g. 滕王阁序)")
    ap.add_argument("text_file", help="长文文件路径 (UTF-8)")
    ap.add_argument("--fmt", default="h", choices=["h", "v"], help="横屏 h / 竖屏 v")
    ap.add_argument("--chunk-size", type=int, default=DEFAULT_CHUNK_SIZE, help="每段句数")
    ap.add_argument("--single-run-max", type=int, default=DEFAULT_SINGLE_RUN_MAX,
                    help="句数 <= 此值走单 run 不切 (内容驱动 gate)")
    ap.add_argument("--crossfade-sec", type=float, default=DEFAULT_CROSSFADE_SEC,
                    help="chunk 间过渡秒数 (0=关, 走 -c copy)")
    ap.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT, help="单 chunk 超时秒")
    ap.add_argument("--retries", type=int, default=DEFAULT_RETRIES, help="单 chunk 失败重试次数")
    ap.add_argument("--run-root", default="", help="工作目录 (默认 /tmp/adr_b69_<topic>_<ts>)")
    ap.add_argument("--resume", action="store_true", help="复用已完成 chunk (读 manifest)")
    ap.add_argument("--dry-run", action="store_true", help="只出 manifest 计划, 不渲染")
    # ADR 透传 flag
    ap.add_argument("--skip-approval", action="store_true")
    ap.add_argument("--grid-multiref-primary", action="store_true")
    ap.add_argument("--ads-dialogue", action="store_true")
    args = ap.parse_args()

    # resume 必须指向原 run 目录, 否则会算出新时间戳目录 → 找不到旧 manifest → 静默重头跑
    if args.resume and not args.run_root:
        print("❌ --resume 需配合 --run-root <原run目录> (原 run 启动时打印的 run_root 路径)", file=sys.stderr)
        sys.exit(1)

    # 参数防御 clamp (Codex Low)
    args.chunk_size = max(1, args.chunk_size)
    args.single_run_max = max(1, args.single_run_max)
    args.crossfade_sec = max(0.0, args.crossfade_sec)
    args.timeout = max(1, args.timeout)
    args.retries = max(0, args.retries)

    text = Path(args.text_file).read_text(encoding="utf-8")
    created_at = time.time()
    topic_safe = "".join(ch for ch in args.topic if ch.isalnum() or "一" <= ch <= "鿿")[:30] or "topic"
    run_root = Path(args.run_root) if args.run_root else Path(f"/tmp/adr_b69_{topic_safe}_{int(created_at)}")
    run_root.mkdir(parents=True, exist_ok=True)
    manifest_path = run_root / "b69_manifest.json"

    # resume: 复用旧 manifest (须与当前 text 计划一致, 防 text 改了却复用旧段 — Codex H2)
    manifest = _load_manifest(manifest_path) if args.resume else None
    if manifest:
        # 比对句子**内容本身** (非仅句数, Codex Stage4): 同句数改文也要拒绝复用旧 chunk
        mode_now, chunks_now = build_plan(text, manifest["chunk_size"], manifest["single_run_max"])
        seg_sentences_old = [s.get("sentences") for s in manifest["segments"]]
        if mode_now != manifest["mode"] or chunks_now != seg_sentences_old:
            print("❌ resume: 当前 text 与 manifest 内容不一致 (text 已改?), 拒绝 resume 防错段", file=sys.stderr)
            sys.exit(1)
        print(f"♻️ resume: manifest 与 text 内容一致, 复用 {manifest_path} ({len(manifest['segments'])} 段)")
    else:
        mode, chunks = build_plan(text, args.chunk_size, args.single_run_max)
        if not chunks:
            print("❌ 空文本, 无可渲染内容", file=sys.stderr)
            sys.exit(1)
        manifest = init_manifest(args.topic, args.fmt, mode, chunks, args.chunk_size,
                                 args.single_run_max, args.crossfade_sec, run_root, created_at)
        _atomic_write_json(manifest_path, manifest)

    n_seg = len(manifest["segments"])
    print(f"=== B69 长文分段渲染 ===")
    print(f"topic: {manifest['topic']} · fmt: {manifest['fmt']} · mode: {manifest['mode']}")
    print(f"总句数: {manifest['total_sentences']} · 段数: {n_seg} · "
          f"单run阈值: {manifest['single_run_max']} · crossfade: {manifest['crossfade_sec']}s")
    for s in manifest["segments"]:
        print(f"  chunk {s['idx']:02d}: 句[{s['sentence_start']}:{s['sentence_end']}] "
              f"{s['n_sentences']} 句 · status={s['status']}")

    if manifest["mode"] == "single_run":
        print("ℹ️ 内容驱动 gate: 句数未超单 run 容量 → 单 run 渲染全文, 不切不 concat")

    if args.dry_run:
        print(f"\n🧪 --dry-run: 计划已写 {manifest_path}, 未渲染")
        return

    # ── 渲染: chunk0 先跑 (产 BGM master), 之后顺序跑并复用 BGM ──
    extra_args = []
    if args.skip_approval:
        extra_args.append("--skip-approval")
    if args.grid_multiref_primary:
        extra_args.append("--grid-multiref-primary")
    if args.ads_dialogue:
        extra_args.append("--ads-dialogue")

    for seg in manifest["segments"]:
        if args.resume and seg["status"] == "done" and _final_mp4_belongs(seg.get("final_mp4"), run_root):
            print(f"♻️ chunk {seg['idx']} 已完成, 跳过")
            continue
        ok = run_one_chunk(seg, manifest["topic"], manifest["fmt"], extra_args,
                           manifest.get("bgm_master"), args.timeout, args.retries, run_root)
        # chunk0 成功后锁定 BGM master 供后续复用
        if ok and seg["idx"] == 0 and not manifest.get("bgm_master"):
            bgm = Path(seg["output_dir"]) / "bgm.mp3"
            if bgm.exists():
                manifest["bgm_master"] = str(bgm)
                print(f"🎵 BGM master 锁定: {bgm} (chunk2..N 复用)")
            else:
                print("⚠️ chunk0 无 bgm.mp3 (NO_VOICE/bgm-only?), chunk2..N 各自生成 BGM, 整片 BGM 可能不一致")
        _atomic_write_json(manifest_path, manifest)
        # fail-loud: 任一段重试后仍失败 → 中止, 不静默丢 (古文缺段=correctness bug)
        if not ok:
            print(f"\n❌ chunk {seg['idx']} 重试后仍失败 (last_error: {seg['last_error']})", file=sys.stderr)
            print(f"   中止整片合并以防内容缺失. 修复后可 --resume 续跑. manifest: {manifest_path}", file=sys.stderr)
            sys.exit(2)

    final_paths = [s["final_mp4"] for s in manifest["segments"]]
    # 严格顺序 + 去重 + 归属守卫 (Codex H1/H2; 不用 assert, -O 会剥离)
    if not all(_final_mp4_belongs(p, run_root) for p in final_paths):
        print("❌ 有段 final_mp4 缺失/不在 run_root 内 (应已 fail-loud 或被篡改), 拒绝合并", file=sys.stderr)
        sys.exit(5)
    if len(set(final_paths)) != len(final_paths):
        print("❌ 检测到重复 chunk 路径, 拒绝合并", file=sys.stderr)
        sys.exit(3)

    out_long = str(run_root / f"ADR_V8_LONG_{topic_safe}_{int(created_at)}.mp4")
    print(f"\n=== 合并 {len(final_paths)} 段 → {out_long} ===")
    if not concat_segments(final_paths, out_long, manifest["crossfade_sec"]):
        print("❌ concat 失败", file=sys.stderr)
        sys.exit(4)

    manifest["final_output"] = out_long
    _atomic_write_json(manifest_path, manifest)
    valid = validate_output(out_long, manifest)  # Codex M2: 失败要让调用方知道
    print(f"{'✅' if valid else '⚠️'} 长视频{'' if valid else '(时长待核)'}: {out_long}")
    print(f"   manifest: {manifest_path}")
    _tg_send_final(out_long, manifest["topic"], manifest)
    if not valid:
        print("⚠️ 成片时长校验未通过, 退出码 6 (成片已生成, 请人工核对)", file=sys.stderr)
        sys.exit(6)


if __name__ == "__main__":
    main()
