#!/usr/bin/env python3
"""扫描 run_adr_v8.py 生成 INDEX.md — 章节 + 函数 + 行号目录。

用法:
    python3 tools/generate_index.py [path/to/run_adr_v8.py]

输出: ADR 根目录 INDEX.md

设计:
- 章节锚点用 `# ── 第N步：xxx ──` 这类区块注释
- 函数用 `^def funcname` 行号
- 每章节内列出该范围内所有 def
- 还单列 module-level helper（在第一个章节之前的 def）
- 标记常量大块（_EMOTION_KEYWORDS 等）
"""
import re
import sys
from pathlib import Path


SECTION_RE = re.compile(r"^\s*#\s*[─━]+\s*(.+?)\s*[─━]+\s*$")
SECTION_SIMPLE_RE = re.compile(r"^\s*#\s*[─━]{2,}\s*(.+)$")
DEF_RE = re.compile(r"^(async\s+)?def\s+(\w+)\s*\(")
CONST_RE = re.compile(r"^(_?[A-Z][A-Z0-9_]+)\s*=\s*[\[\{\(]")

# 主章节：包含"第N步"/"主流程"/"配置"等关键字的横线注释
MAIN_SECTION_KEYWORDS = (
    "第一步", "第二步", "第三步", "第四步", "第五步", "第六步", "第七步", "第八步", "第九步", "第十步",
    "第 6.5 步", "主流程", "配置",
)


def _is_main_section(name: str) -> bool:
    return any(kw in name for kw in MAIN_SECTION_KEYWORDS)


def scan(file_path: Path) -> dict:
    lines = file_path.read_text(encoding="utf-8").splitlines()
    total = len(lines)
    sections: list[dict] = []  # each: {name, start, end, kind: main|sub, defs, consts, subs: [{name,start,end}]}
    cur_main = {
        "name": "Module-level (header + global config)",
        "start": 1,
        "kind": "main",
        "defs": [],
        "consts": [],
        "subs": [],
    }
    sections.append(cur_main)
    cur_sub: dict | None = None

    def close_sub(end_line: int):
        nonlocal cur_sub
        if cur_sub is not None:
            cur_sub["end"] = end_line
            cur_sub = None

    for i, raw in enumerate(lines, start=1):
        m = SECTION_RE.match(raw) or SECTION_SIMPLE_RE.match(raw)
        if m and ("─" in raw or "━" in raw):
            name = m.group(1).strip().rstrip("─━ ").strip()
            if not name or len(name) >= 80:
                pass
            elif _is_main_section(name):
                close_sub(i - 1)
                cur_main["end"] = i - 1
                cur_main = {
                    "name": name,
                    "start": i,
                    "kind": "main",
                    "defs": [],
                    "consts": [],
                    "subs": [],
                }
                sections.append(cur_main)
                continue
            else:
                # 子区块（不是 main step）
                close_sub(i - 1)
                cur_sub = {"name": name, "start": i, "end": total}
                cur_main["subs"].append(cur_sub)
                continue
        m2 = DEF_RE.match(raw)
        if m2:
            cur_main["defs"].append((m2.group(2), i))
            continue
        m3 = CONST_RE.match(raw)
        if m3:
            cur_main["consts"].append((m3.group(1), i))
    close_sub(total)
    cur_main["end"] = total

    return {"total": total, "sections": sections}


def _slug(name: str) -> str:
    return re.sub(r"[^\w\-]", "-", name.lower()).strip("-")


def emit_index(data: dict, out_path: Path, src_name: str = "run_adr_v8.py") -> None:
    md = []
    md.append(f"# ADR Code Index")
    md.append("")
    md.append(f"Auto-generated. Source: `{src_name}` ({data['total']} lines). "
              f"Regenerate: `python3 tools/generate_index.py`.")
    md.append("")
    # TOC
    md.append("## Sections")
    md.append("")
    for s in data["sections"]:
        anchor = _slug(s["name"])
        md.append(f"- [`{s['name']}`](#{anchor}) — L{s['start']}-{s['end']} "
                  f"({s['end'] - s['start'] + 1} lines · {len(s['defs'])} fn · {len(s['subs'])} sub)")
    md.append("")
    md.append("---")
    md.append("")
    # Details
    for s in data["sections"]:
        md.append(f"### {s['name']}")
        md.append(f"Range: **L{s['start']} – L{s['end']}** ({s['end'] - s['start'] + 1} lines)")
        md.append("")
        if s["subs"]:
            md.append("**Sub-sections:**")
            for sub in s["subs"]:
                md.append(f"- _{sub['name']}_ — L{sub['start']}-{sub['end']} "
                          f"({sub['end'] - sub['start'] + 1} lines)")
            md.append("")
        if s["consts"]:
            md.append("**Top-level constants:**")
            for name, line in s["consts"]:
                md.append(f"- `{name}` — L{line}")
            md.append("")
        if s["defs"]:
            md.append("**Functions:**")
            for name, line in s["defs"]:
                md.append(f"- `{name}` — L{line}")
            md.append("")
        if not s["consts"] and not s["defs"] and not s["subs"]:
            md.append("_(empty)_")
            md.append("")
        md.append("---")
        md.append("")
    out_path.write_text("\n".join(md), encoding="utf-8")
    print(f"✓ INDEX written → {out_path}")
    print(f"  Main sections: {len(data['sections'])}")
    print(f"  Sub-sections : {sum(len(s['subs']) for s in data['sections'])}")
    print(f"  Functions    : {sum(len(s['defs']) for s in data['sections'])}")
    print(f"  Constants    : {sum(len(s['consts']) for s in data['sections'])}")


def main():
    here = Path(__file__).resolve().parent
    root = here.parent
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else (root / "run_adr_v8.py")
    if not src.exists():
        print(f"ERROR: {src} not found", file=sys.stderr)
        sys.exit(1)
    data = scan(src)
    out = root / "INDEX.md"
    emit_index(data, out, src.name)


if __name__ == "__main__":
    main()
