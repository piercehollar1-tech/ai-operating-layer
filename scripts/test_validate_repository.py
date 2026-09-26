#!/usr/bin/env python3
"""Break-tests for validate_repository.py: each planted defect must turn it red.

The validator is a control, so it is unproven until it has been seen failing on
purpose. Every case copies the publishable tree into a scratch repository, plants
one defect, and runs the validator from the copy. The first case plants nothing
and must pass: a validator that fails everything would pass every other case.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = Path("scripts/validate_repository.py")
HOME_PATH = "/" + "Users/someone/notes.md"  # split so this file does not trip the validator

TABLE_OK = "| a | b |\n|---|---|\n| 1 | 2 |\n"


def append(rel: str, text: str):
    def plant(repo: Path) -> None:
        with (repo / rel).open("a", encoding="utf-8") as handle:
            handle.write(text)
    return plant


def write(rel: str, text: str):
    def plant(repo: Path) -> None:
        (repo / rel).parent.mkdir(parents=True, exist_ok=True)
        (repo / rel).write_text(text, encoding="utf-8")
    return plant


def write_bytes(rel: str, data: bytes):
    def plant(repo: Path) -> None:
        (repo / rel).write_bytes(data)
    return plant


def delete(rel: str):
    def plant(repo: Path) -> None:
        (repo / rel).unlink()
    return plant


CASES = (
    ("QUIET: unmodified tree passes", None, None),
    ("QUIET: a well-formed table and a closed fence pass", append("docs/setup.md", "\n" + TABLE_OK + "\n```text\nx\n```\n"), None),
    ("QUIET: a pipe inside inline code is not a cell", append("docs/setup.md", "\n| a | b |\n|---|---|\n| `x|y` | 2 |\n"), None),
    ("home path in a tracked doc", append("docs/setup.md", f"\nSee {HOME_PATH}\n"), "macOS home path"),
    ("secret in an UNTRACKED file", write("notes/scratch.md", "token: ghp_" + "a" * 30 + "\n"), "GitHub token"),
    ("forbidden instruction filename", write("reference/CLAUDE.md", "# live file\n"), "not publishable"),
    ("missing required file", delete("docs/operations.md"), "missing required file"),
    ("broken relative link", append("README.md", "\n[gone](docs/nope.md)\n"), "broken relative link"),
    ("trailing whitespace", append("docs/setup.md", "\ntrailing \n"), "trailing whitespace"),
    ("missing final newline", append("docs/setup.md", "\nno newline"), "missing final newline"),
    ("QUIET: an escaped pipe is not a cell", append("docs/setup.md", "\n| a | b |\n|---|---|\n| x \\| y | 2 |\n"), None),
    ("QUIET: a tilde fence closes", append("docs/setup.md", "\n~~~text\n| not | a table |\n~~~\n"), None),
    ("QUIET: a longer fence holds a shorter one", append("docs/setup.md", "\n````md\n```text\ninner\n```\n````\n"), None),
    ("QUIET: a table without outer pipes", append("docs/setup.md", "\na | b\n---|---\n1 | 2\n"), None),
    ("table row with a missing cell", append("docs/setup.md", "\n| a | b |\n|---|---|\n| 1 |\n"), "table row has"),
    ("missing cell, table without outer pipes", append("docs/setup.md", "\na | b | c\n---|---|---\n1 | 2\n"), "table row has"),
    ("delimiter row with the wrong cell count", append("docs/setup.md", "\n| a | b |\n|---|\n| 1 | 2 |\n"), "table row has"),
    ("unclosed code fence", append("docs/setup.md", "\n```text\nnever closed\n"), "unclosed code fence"),
    ("unclosed tilde fence", append("docs/setup.md", "\n~~~\nnever closed\n"), "unclosed code fence"),
    ("QUIET: indented code is neither a fence nor a table", append("docs/setup.md", "\n    ```\n    | a | b |\n    |---|---|\n    | 1 |\n"), None),
    ("QUIET: an unmatched backtick is plain text", append("docs/setup.md", "\n| a ` b | c |\n|---|---|\n| 1 | 2 |\n"), None),
    ("invalid UTF-8 is reported, not a crash", write_bytes("docs/broken.md", b"caf\xe9\n"), "not valid UTF-8"),
    ("shorter fence does not close a longer one", append("docs/setup.md", "\n````text\n```\n"), "unclosed code fence"),
)


def copy_tree(destination: Path) -> None:
    listing = subprocess.run(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        cwd=ROOT, check=True, stdout=subprocess.PIPE,
    ).stdout.decode("utf-8")
    for rel in filter(None, listing.split("\0")):
        source = ROOT / rel
        if source.is_file():
            target = destination / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
    subprocess.run(["git", "init", "-q"], cwd=destination, check=True)


def main() -> int:
    failed = 0
    for name, plant, expected_message in CASES:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            copy_tree(repo)
            if plant:
                plant(repo)
            result = subprocess.run([sys.executable, str(VALIDATOR)], cwd=repo,
                                    capture_output=True, text=True, timeout=60)
            if expected_message is None:
                ok = result.returncode == 0
                detail = result.stderr.strip()
            else:
                ok = result.returncode == 1 and expected_message in result.stderr
                detail = f"exit {result.returncode}; wanted '{expected_message}'"
            print(f"  {'PASS' if ok else 'FAIL'}  {name}" + ("" if ok else f"  ({detail})"))
            failed += not ok
    print(f"{len(CASES) - failed}/{len(CASES)} validator break-tests passed.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
