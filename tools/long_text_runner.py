#!/usr/bin/env python3
"""B66 (2026-05-30): 长文分段渲染 — 把长文 split → 各段单独跑 ADR → ffmpeg concat 成长视频.

适用滕王阁序 (770 字 35-40 句)/赤壁赋/醉翁亭记等.

usage:
  python3 tools/long_text_runner.py \
    "滕王阁序" \
    /path/to/full_text.txt \
    --fmt h \
    --chunk 9 \
    [--skip-approval] [--grid-multiref-primary]

流程:
1. split 长文成 N 段 (每段 9 句)
2. 各段: cp chunk_i.txt /tmp/adr_script_override.txt → 跑 run_adr_v8.py
3. 各段 run 完, 收集 final mp4
4. ffmpeg concat 成长视频
5. TG 推送
"""
import argparse
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools.long_text_split import split_long_text  # noqa: E402

ADR_SCRIPT = str(ROOT / "run_adr_v8.py")
ADR_OVERRIDE = "/tmp/adr_script_override.txt"
PYTHON = "/opt/homebrew/bin/python3"
FFMPEG = "/opt/homebrew/bin/ffmpeg"


def run_one_chunk(topic: str, chunk_lines: list[str], fmt: str, extra_args: list[str], chunk_idx: int) -> str | None:
    """跑单段 ADR, 返回 final mp4 路径或 None (失败)."""
    # 写 fixture override
    Path(ADR_OVERRIDE).write_text("\n".join(chunk_lines) + "\n", encoding="utf-8")

    cmd = [PYTHON, ADR_SCRIPT, topic, fmt] + extra_args
    print(f"\n=== chunk {chunk_idx}: {len(chunk_lines)} 句 ===")
    print(f"   cmd: {' '.join(cmd)}")

    log_path = f"/tmp/adr_long_text_chunk_{chunk_idx:02d}.log"
    try:
        with open(log_path, "w") as lf:
            r = subprocess.run(cmd, stdout=lf, stderr=subprocess.STDOUT, timeout=3600)
        if r.returncode != 0:
            print(f"   ❌ chunk {chunk_idx} 返回非 0: {r.returncode}, log: {log_path}")
            return None
    except subprocess.TimeoutExpired:
        print(f"   ❌ chunk {chunk_idx} 超时 (1h), log: {log_path}")
        return None
    except Exception as e:
        print(f"   ❌ chunk {chunk_idx} 异常: {e}, log: {log_path}")
        return None

    # 从 log 拿 OUTPUT_DIR
    log_content = Path(log_path).read_text()
    out_dir = None
    for line in log_content.splitlines():
        if "输出目录：" in line:
            out_dir = line.split("输出目录：", 1)[1].strip().split()[0]
            break
    if not out_dir or not os.path.exists(out_dir):
        print(f"   ❌ chunk {chunk_idx} 找不到 OUTPUT_DIR (log 解析失败)")
        return None

    # 找 final mp4 (ADR_V8_*.mp4 最新)
    candidates = sorted(Path(out_dir).glob("ADR_V8_*.mp4"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not candidates:
        print(f"   ❌ chunk {chunk_idx} OUTPUT_DIR 没 ADR_V8_*.mp4: {out_dir}")
        return None
    final = str(candidates[0])
    print(f"   ✅ chunk {chunk_idx} → {final}")
    return final


def concat_mp4s(paths: list[str], out_path: str) -> bool:
    """ffmpeg concat demuxer 把多段 mp4 拼成长视频. 要求各段同 codec/fps/aspect."""
    if not paths:
        return False
    concat_list = Path(out_path).with_suffix(".concat.txt")
    concat_list.write_text("\n".join(f"file '{p}'" for p in paths), encoding="utf-8")
    cmd = [
        FFMPEG, "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(concat_list),
        "-c", "copy",
        out_path,
    ]
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=300)
        if r.returncode != 0:
            print(f"❌ ffmpeg concat fail: {r.stderr.decode()[:500]}")
            return False
        return os.path.exists(out_path) and os.path.getsize(out_path) > 100000
    except Exception as e:
        print(f"❌ ffmpeg concat 异常: {e}")
        return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("topic", help="ADR topic (e.g. 滕王阁序)")
    ap.add_argument("text_file", help="长文文件路径")
    ap.add_argument("--fmt", default="h", choices=["h", "v"], help="横屏 h / 竖屏 v")
    ap.add_argument("--chunk", type=int, default=9, help="每段句数")
    ap.add_argument("--skip-approval", action="store_true", help="跳过图片审批")
    ap.add_argument("--grid-multiref-primary", action="store_true", help="启用 grid_multiref 主路径")
    ap.add_argument("--adsd", action="store_true", help="HADSD 多角色对话模式")
    args = ap.parse_args()

    text = Path(args.text_file).read_text(encoding="utf-8")
    chunks = split_long_text(text, chunk_size=args.chunk)
    if not chunks:
        print("❌ split 失败 (空文本?)", file=sys.stderr)
        sys.exit(1)

    print(f"=== B66 长文分段渲染 ===")
    print(f"topic: {args.topic}")
    print(f"total chunks: {len(chunks)}")
    print(f"total sentences: {sum(len(c) for c in chunks)}")

    extra_args = []
    if args.skip_approval:
        extra_args.append("--skip-approval")
    if args.grid_multiref_primary:
        extra_args.append("--grid-multiref-primary")
    if args.adsd:
        extra_args.append("--adsd")

    final_paths: list[str] = []
    failed_chunks: list[int] = []
    for i, chunk in enumerate(chunks, start=1):
        path = run_one_chunk(args.topic, chunk, args.fmt, extra_args, i)
        if path:
            final_paths.append(path)
        else:
            failed_chunks.append(i)

    if failed_chunks:
        print(f"\n⚠️ {len(failed_chunks)} chunk 失败: {failed_chunks}")
    if not final_paths:
        print("❌ 全部 chunk 失败, 无视频生成", file=sys.stderr)
        sys.exit(1)

    # concat
    out_long = f"/tmp/adr_long_text_{args.topic}_{int(time.time())}.mp4"
    print(f"\n=== 合并 {len(final_paths)} 段 → {out_long} ===")
    if concat_mp4s(final_paths, out_long):
        print(f"✅ 长视频: {out_long}")
        print(f"   段路径: {final_paths}")
    else:
        print("❌ concat 失败", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
