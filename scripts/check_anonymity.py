#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

TEXT_SUFFIXES = {
    ".csv",
    ".json",
    ".jsonl",
    ".md",
    ".py",
    ".sh",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}
SKIP_DIRS = {
    ".git",
    ".ipynb_checkpoints",
    "__pycache__",
    "metadata/checksums",
}
PATTERNS = {
    "local_home_path": re.compile(r"/home/[A-Za-z0-9_.-]+/"),
    "raw_github_user_url": re.compile(r"github\.com/[A-Za-z0-9_.-]+/CityRep", re.IGNORECASE),
    "working_release_name": re.compile(r"urban_benchmark_(?:release|final_release)"),
    "executed_notebook_suffix": re.compile(r"\.executed\.ipynb\b"),
}
ALLOWLIST = {
    "metadata/anonymity_report.json",
    "scripts/check_anonymity.py",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scan release text files for local path or identity leaks.")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--json-out", type=Path, default=ROOT / "metadata" / "anonymity_report.json")
    parser.add_argument("--fail", action="store_true", help="Exit non-zero when leaks are found.")
    return parser.parse_args()


def should_skip(path: Path, root: Path) -> bool:
    rel = path.relative_to(root).as_posix()
    if rel in ALLOWLIST:
        return True
    parts = set(path.relative_to(root).parts)
    return bool(parts.intersection(SKIP_DIRS)) or path.suffix.lower() not in TEXT_SUFFIXES


def main() -> None:
    args = parse_args()
    findings: list[dict[str, object]] = []
    for path in args.root.rglob("*"):
        if not path.is_file() or should_skip(path, args.root):
            continue
        rel = path.relative_to(args.root).as_posix()
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for lineno, line in enumerate(text.splitlines(), 1):
            for name, pattern in PATTERNS.items():
                if pattern.search(line):
                    findings.append({"path": rel, "line": lineno, "pattern": name, "text": line[:240]})

    payload = {"status": "ok" if not findings else "findings", "finding_count": len(findings), "findings": findings}
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))
    if args.fail and findings:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
