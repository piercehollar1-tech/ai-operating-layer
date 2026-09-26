#!/usr/bin/env python3
"""Validate the public reference repository without external dependencies."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_PATHS = (
    "LICENSE",
    "README.md",
    "docs/architecture.md",
    "docs/automation.md",
    "docs/context-delivery.md",
    "docs/delegation.md",
    "docs/enforcement.md",
    "docs/intake-security.md",
    "docs/operations.md",
    "docs/response-contract.md",
    "docs/setup.md",
    "docs/verification.md",
    "reference/BOOTSTRAP_PROMPT.md",
    "reference/README.md",
    "reference/adapters/AGENTS.md.example",
    "reference/adapters/CLAUDE.md.example",
    "reference/adapters/output-style.md.example",
    "reference/agents/task-packet.md.example",
    "reference/agents/worker.md.example",
    "reference/hooks/pre-publish-scan.py.example",
    "reference/hooks/routes.json.example",
    "reference/hooks/tests/pre-publish-scan-probes.py.example",
    "reference/shared/memory/MEMORY.md",
    "reference/shared/skill-notes/example-workflow.md",
    "reference/shared/skills/example-workflow/SKILL.md",
    "reference/shared/vault/index.md",
)

FORBIDDEN_FILENAMES = {".env", "AGENTS.md", "CLAUDE.md"}

SENSITIVE_PATTERNS = (
    ("macOS home path", re.compile("/" + r"Users/[^/\s]+/")),
    ("Linux home path", re.compile("/" + r"home/[^/\s]+/")),
    ("Windows home path", re.compile(r"[A-Za-z]:\\Users\\[^\\\s]+\\")),
    ("AWS access key", re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b")),
    ("GitHub token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b")),
    ("GitHub fine-grained token", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b")),
    ("OpenAI-style API key", re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b")),
    ("Slack token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b")),
    ("Google API key", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
    (
        "private key",
        re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    ),
    (
        "assigned credential",
        re.compile(
            r"(?i)\b(?:api[_-]?key|access[_-]?token|auth[_-]?token|client[_-]?secret)"
            r"\s*[:=]\s*['\"]?[A-Za-z0-9+/_.=-]{16,}"
        ),
    ),
)

MARKDOWN_LINK = re.compile(r"!?\[[^\]]+\]\(([^)]+)\)")
FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")  # 4+ spaces is an indented code block
INDENTED_CODE = re.compile(r"^( {4}|\t)")
TABLE_DELIMITER = re.compile(r"^\s*\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)*\|?\s*$")


def repository_files() -> list[Path]:
    # Tracked AND untracked (ignored excluded): content staged in the same command as a
    # push is still untracked when a pre-command check runs, so a tracked-only listing
    # validates a tree that is not the one about to ship.
    result = subprocess.run(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
    )
    return sorted(
        ROOT / relative_path
        for relative_path in result.stdout.decode("utf-8").split("\0")
        if relative_path and (ROOT / relative_path).is_file()
    )


def is_text_file(path: Path) -> bool:
    return path.name in {".gitignore", "LICENSE"} or path.suffix.lower() in {
        ".example",
        ".json",
        ".md",
        ".py",
        ".yaml",
        ".yml",
    }


def validate_required_paths(errors: list[str]) -> None:
    for relative_path in REQUIRED_PATHS:
        if not (ROOT / relative_path).is_file():
            errors.append(f"missing required file: {relative_path}")


def validate_filenames(files: list[Path], errors: list[str]) -> None:
    for path in files:
        relative_path = path.relative_to(ROOT)
        if path.name in FORBIDDEN_FILENAMES or path.name.startswith(".env."):
            errors.append(f"private configuration filename is not publishable: {relative_path}")


def validate_text(files: list[Path], errors: list[str]) -> None:
    for path in files:
        if not is_text_file(path):
            continue

        relative_path = path.relative_to(ROOT)
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            errors.append(f"text file is not valid UTF-8: {relative_path}")
            continue

        if text and not text.endswith("\n"):
            errors.append(f"missing final newline: {relative_path}")

        for line_number, line in enumerate(text.splitlines(), start=1):
            if line.endswith((" ", "\t")):
                errors.append(f"trailing whitespace: {relative_path}:{line_number}")

        for pattern_name, pattern in SENSITIVE_PATTERNS:
            for match in pattern.finditer(text):
                line_number = text.count("\n", 0, match.start()) + 1
                errors.append(
                    f"possible {pattern_name}: {relative_path}:{line_number}"
                )


def is_markdown(path: Path) -> bool:
    return path.suffix.lower() == ".md" or path.name.endswith(".md.example")


def split_cells(line: str) -> list[str]:
    # A pipe separates cells unless it is backslash-escaped or inside a code span.
    cells, current, code_ticks, i = [], "", 0, 0
    stripped = line.strip()
    while i < len(stripped):
        char = stripped[i]
        if char == "\\" and i + 1 < len(stripped):
            current += stripped[i:i + 2]
            i += 2
            continue
        if char == "`":
            run = len(stripped[i:]) - len(stripped[i:].lstrip("`"))
            if code_ticks == run:
                code_ticks = 0
            elif not code_ticks and re.search(rf"(?<!`)`{{{run}}}(?!`)", stripped[i + run:]):
                code_ticks = run  # a backtick run opens a code span only if it is closed later
            current += "`" * run
            i += run
            continue
        if char == "|" and not code_ticks:
            cells.append(current)
            current = ""
        else:
            current += char
        i += 1
    cells.append(current)
    if stripped.startswith("|"):
        cells = cells[1:]
    if stripped.endswith("|") and not stripped.endswith("\\|") and cells:
        cells = cells[:-1]
    return cells


def fenced_lines(lines: list[str], relative_path: Path, errors: list[str]) -> set[int]:
    # A fence closes only on the same character, at least as long, with nothing after it.
    inside: set[int] = set()
    opener: tuple[str, int, int] | None = None
    for index, line in enumerate(lines):
        match = FENCE.match(line)
        if opener is None:
            if match and not (match.group(1)[0] == "`" and "`" in match.group(2)):
                opener = (match.group(1)[0], len(match.group(1)), index)
                inside.add(index)
            continue
        inside.add(index)
        if (match and match.group(1)[0] == opener[0] and len(match.group(1)) >= opener[1]
                and not match.group(2).strip()):
            opener = None
    if opener is not None:
        errors.append(f"unclosed code fence opened at {relative_path}:{opener[2] + 1}")
    return inside


def validate_markdown_structure(files: list[Path], errors: list[str]) -> int:
    # Fence balance and table shape: a lost fence swallows the rest of a document, and a row
    # with a missing cell renders as a shifted table with no error anywhere.
    checked_tables = 0

    for path in files:
        if not is_markdown(path):
            continue

        relative_path = path.relative_to(ROOT)
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue  # already reported by validate_text
        fenced = fenced_lines(lines, relative_path, errors)

        for index in range(1, len(lines)):
            header = lines[index - 1]
            if (index in fenced or index - 1 in fenced or "|" not in lines[index]
                    or not TABLE_DELIMITER.match(lines[index]) or "|" not in header
                    or INDENTED_CODE.match(header) or INDENTED_CODE.match(lines[index])):
                continue
            checked_tables += 1
            expected = len(split_cells(header))
            row_index = index
            while row_index < len(lines):
                row = lines[row_index]
                if row_index in fenced or not row.strip() or "|" not in row:
                    break
                found = len(split_cells(row))
                if found != expected:
                    errors.append(
                        f"table row has {found} cells, header has {expected}: "
                        f"{relative_path}:{row_index + 1}"
                    )
                row_index += 1

    return checked_tables


def validate_markdown_links(files: list[Path], errors: list[str]) -> int:
    checked_links = 0

    for path in files:
        if path.suffix.lower() != ".md":
            continue

        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue  # already reported by validate_text
        for match in MARKDOWN_LINK.finditer(text):
            raw_target = match.group(1).strip()
            target = raw_target[1:-1] if raw_target.startswith("<") and raw_target.endswith(">") else raw_target
            target = target.split(maxsplit=1)[0]

            if not target or target.startswith(("#", "http://", "https://", "mailto:")):
                continue

            target = unquote(target.split("#", 1)[0].split("?", 1)[0])
            candidate = (path.parent / target).resolve()
            relative_path = path.relative_to(ROOT)
            checked_links += 1

            try:
                candidate.relative_to(ROOT)
            except ValueError:
                errors.append(f"link escapes repository: {relative_path} -> {raw_target}")
                continue

            if not candidate.exists():
                line_number = text.count("\n", 0, match.start()) + 1
                errors.append(
                    f"broken relative link: {relative_path}:{line_number} -> {raw_target}"
                )

    return checked_links


def main() -> int:
    errors: list[str] = []
    files = repository_files()

    validate_required_paths(errors)
    validate_filenames(files, errors)
    validate_text(files, errors)
    checked_links = validate_markdown_links(files, errors)
    checked_tables = validate_markdown_structure(files, errors)

    if errors:
        print("Repository validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    text_file_count = sum(is_text_file(path) for path in files)
    print(
        f"Repository validation passed: {text_file_count} text files, "
        f"{checked_links} relative Markdown links, and {checked_tables} tables checked."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
