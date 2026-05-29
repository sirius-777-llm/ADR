#!/usr/bin/env python3
"""B66 (2026-05-30): 长文按句切分成 N 段, 每段 chunk_size 句 (default 9, ADR fixture cap).

适用滕王阁序 (35-40 句)/赤壁赋/醉翁亭记等长古文.

usage:
  python3 tools/long_text_split.py 输入文本.txt --chunk 9 --out /tmp/split/
"""
import argparse
import os
import re
import sys
from pathlib import Path


# 中文句末标点 (含全角)
_SENT_END = re.compile(r"([^。！？\?\!]+[。！？\?\!]+)")


def split_long_text(text: str, chunk_size: int = 9) -> list[list[str]]:
    """按句末标点 split, 每 chunk_size 句一段. 返回 [[句1, 句2, ...], ...]."""
    if not text or chunk_size < 1:
        return []
    # 先 normalize whitespace
    text = re.sub(r"\s+", " ", text.strip())
    if not text:
        return []
    # 句切: 含末标点
    sentences = [s.strip() for s in _SENT_END.findall(text) if s.strip()]
    # Stage 4 fix: 末尾无标点的尾句被 regex 漏掉, 手动补
    matched_concat = "".join(sentences)
    tail = text[len(matched_concat):].strip()
    if tail:
        sentences.append(tail)
    if not sentences:
        # fallback: 没标点全文当 1 句
        sentences = [text]
    chunks: list[list[str]] = []
    for i in range(0, len(sentences), chunk_size):
        chunk = sentences[i:i + chunk_size]
        if chunk:
            chunks.append(chunk)
    return chunks


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input", help="输入文本文件路径 (UTF-8)")
    ap.add_argument("--chunk", type=int, default=9, help="每段句数 (default 9 跟 ADR fixture cap 对齐)")
    ap.add_argument("--out", default="/tmp/long_text_split", help="输出目录")
    args = ap.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"❌ 输入文件不存在: {input_path}", file=sys.stderr)
        sys.exit(1)

    text = input_path.read_text(encoding="utf-8")
    chunks = split_long_text(text, chunk_size=args.chunk)
    if not chunks:
        print("❌ 没切出任何段 (空文本?)", file=sys.stderr)
        sys.exit(1)

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    for i, chunk in enumerate(chunks, start=1):
        chunk_path = out_dir / f"chunk_{i:02d}.txt"
        chunk_path.write_text("\n".join(chunk) + "\n", encoding="utf-8")
        print(f"  chunk_{i:02d}: {len(chunk)} 句 → {chunk_path}")

    print(f"\n✅ {len(chunks)} 段输出到 {out_dir}")
    print(f"   总句数 {sum(len(c) for c in chunks)}")


if __name__ == "__main__":
    main()
