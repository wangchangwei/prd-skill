#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_site.py — Package PRD-writer outputs (.md files + prototype.html)
into a single self-contained site.html with a top navigation menu.

Usage:
    python3 scripts/build_site.py <input_dir> [--output PATH] [--title TITLE]

Examples:
    python3 scripts/build_site.py ./demo-output
    python3 scripts/build_site.py ./my-project --title "我的项目"
    python3 scripts/build_site.py . --output ./dist/index.html
"""

import argparse
import io
import json
import re
import sys
from pathlib import Path


# Human-readable labels for common prd-writer outputs
HUMANIZED_LABELS = {
    "01-requirements": "需求采集",
    "feature_list":    "Feature List",
    "PRD":             "PRD 主文",
    "05-qa-report":    "质检报告",
    "00-pm-analysis":  "PM 解读",
    "feature-detail":  "功能详细说明",
    "MASTER":          "设计系统",
    "README":          "说明文档",
    "SKILL":           "技能定义",
}

IGNORE_DIR_NAMES = {".omc", ".git", ".screenshots", "node_modules", ".cache", "__pycache__"}
TEMPLATE_REL = Path("references") / "site-template.html"


def humanize(stem: str, full_rel: Path) -> str:
    """Convert file stem to human label."""
    if stem in HUMANIZED_LABELS:
        # if nested inside design-system/<project>/, prefix with project
        parts = full_rel.parts
        if len(parts) >= 3 and parts[0] == "design-system":
            return f"设计系统 · {parts[1]}"
        return HUMANIZED_LABELS[stem]
    # strip leading digits + separator
    m = re.match(r"^(\d+)[-_](.+)$", stem)
    label = m.group(2) if m else stem
    # `kebab-case` / `snake_case` → human
    label = re.sub(r"[-_]+", " ", label).strip()
    return label[:1].upper() + label[1:] if label else stem


def sort_key(stem: str) -> int:
    m = re.match(r"^(\d+)", stem)
    return int(m.group(1)) if m else 9999


def slugify(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s or "section"


def scan(input_dir: Path):
    """Walk input_dir, collect .md files + the first prototype.html found."""
    md_items = []
    prototype = None
    extra_prototypes = []
    for path in sorted(input_dir.rglob("*")):
        # skip ignored directories
        if any(part in IGNORE_DIR_NAMES for part in path.parts):
            continue
        if not path.is_file():
            continue
        rel = path.relative_to(input_dir)
        if path.suffix.lower() == ".md":
            md_items.append((rel, path))
        elif path.name == "prototype.html":
            if prototype is None:
                prototype = (rel, path)
            else:
                extra_prototypes.append(rel)
    if extra_prototypes:
        chosen = prototype[0]
        ignored = ", ".join(str(p) for p in extra_prototypes)
        print(f"warn: multiple prototype.html found — using {chosen}, ignoring: {ignored}", file=sys.stderr)
    return md_items, prototype


def read_text(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return p.read_text(encoding="utf-8", errors="replace")


def build(input_dir: Path, output: Path, title: str, template_path: Path):
    if not input_dir.is_dir():
        print(f"error: input_dir {input_dir} is not a directory", file=sys.stderr)
        return 2
    if not template_path.is_file():
        print(f"error: template not found at {template_path}", file=sys.stderr)
        return 1

    md_items, prototype = scan(input_dir)
    if not md_items and not prototype:
        print(f"warn: no .md files or prototype.html found in {input_dir}", file=sys.stderr)

    nav = []
    seen_ids = set()

    # collect md tabs, ordered by numeric prefix then path
    md_sorted = sorted(md_items, key=lambda x: (sort_key(x[1].stem), str(x[0])))
    for rel, path in md_sorted:
        stem = path.stem
        label = humanize(stem, rel)
        id_base = slugify(str(rel.with_suffix("")))
        id_ = id_base
        n = 1
        while id_ in seen_ids:
            n += 1
            id_ = f"{id_base}-{n}"
        seen_ids.add(id_)
        nav.append({
            "id": id_,
            "label": label,
            "type": "md",
            "content": read_text(path),
            "_path": str(rel),
        })

    # prototype always last
    if prototype:
        rel, path = prototype
        nav.append({
            "id": "prototype",
            "label": "原型",
            "type": "html",
            "content": read_text(path),
            "_path": str(rel),
        })

    payload = {"title": title, "navItems": nav}
    payload_json = json.dumps(payload, ensure_ascii=False)
    # guard against `</script>` (case-insensitive — browsers tokenize tag names case-insensitively)
    payload_json = re.sub(r"</(script)", r"<\\/\1", payload_json, flags=re.IGNORECASE)

    template = template_path.read_text(encoding="utf-8")
    html = template.replace("{{TITLE}}", title).replace("{{PAYLOAD_JSON}}", payload_json)

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html, encoding="utf-8")

    size_kb = output.stat().st_size / 1024
    md_count = len([x for x in nav if x["type"] == "md"])
    has_proto = "yes" if prototype else "no"
    print(f"✅ Built {output} ({size_kb:.1f} KB, {md_count} md + prototype: {has_proto})")
    return 0


def main(argv=None):
    # Force UTF-8 stdout/stderr (mirrors search.py convention)
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    if sys.stderr.encoding and sys.stderr.encoding.lower() != "utf-8":
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Package PRD-writer outputs (.md + prototype.html) into a single self-contained site.html"
    )
    parser.add_argument("input_dir", help="Directory containing .md files and optional prototype.html")
    parser.add_argument("--output", "-o", default=None, help="Output path (default: <input_dir>/site.html)")
    parser.add_argument("--title", "-t", default=None, help="Site title (default: input dir basename)")
    parser.add_argument(
        "--template",
        default=None,
        help="Path to site-template.html (default: <repo>/references/site-template.html)",
    )
    args = parser.parse_args(argv)

    input_dir = Path(args.input_dir).resolve()
    title = args.title or input_dir.name
    output = Path(args.output).resolve() if args.output else (input_dir / "site.html").resolve()

    # template path: explicit arg > sibling of this script > repo root
    if args.template:
        template_path = Path(args.template).resolve()
    else:
        script_dir = Path(__file__).resolve().parent
        # scripts/build_site.py → ../references/site-template.html
        candidate = script_dir.parent / TEMPLATE_REL
        template_path = candidate

    return build(input_dir, output, title, template_path)


if __name__ == "__main__":
    sys.exit(main())
