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
    "docs/setup.md",
    "reference/BOOTSTRAP_PROMPT.md",
    "reference/README.md",
    "reference/adapters/AGENTS.md.example",
    "reference/adapters/CLAUDE.md.example",
    "reference/shared/memory/MEMORY.md",
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


def repository_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
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


def validate_markdown_links(files: list[Path], errors: list[str]) -> int:
    checked_links = 0

    for path in files:
        if path.suffix.lower() != ".md":
            continue

        text = path.read_text(encoding="utf-8")
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

    if errors:
        print("Repository validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    text_file_count = sum(is_text_file(path) for path in files)
    print(
        f"Repository validation passed: {text_file_count} text files and "
        f"{checked_links} relative Markdown links checked."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
