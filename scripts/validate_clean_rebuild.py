#!/usr/bin/env python3
"""Fail when deterministic builders leave tracked or untracked repository changes."""

import argparse
import subprocess
from pathlib import Path


def repository_changes(root):
    result = subprocess.run(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    return [line for line in result.stdout.splitlines() if line]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    changes = repository_changes(root)
    if changes:
        details = "\n".join(f"  {line}" for line in changes)
        raise SystemExit(f"Clean rebuild gate failed; generated outputs are stale:\n{details}")
    print("Clean rebuild gate passed: tracked generated outputs are current")


if __name__ == "__main__":
    main()
