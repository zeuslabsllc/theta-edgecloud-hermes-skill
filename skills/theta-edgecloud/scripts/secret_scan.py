#!/usr/bin/env python3
"""Small dependency-free secret scanner for release checks.

Scans files passed as arguments, or stdin if no arguments are given. It is tuned for
this repo: env var names, docs placeholders, and deliberate smoke-test dummy values
are allowed; high-confidence token-shaped material is reported.
"""

from __future__ import annotations

import pathlib
import re
import sys
from typing import Iterable

PATTERNS = [
    re.compile(r"gh[pousr]_[A-Za-z0-9_]{20,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
    re.compile(r"(?i)(api[_-]?key|token|secret|password|authorization|bearer)\s*[:=]\s*[\"']?([^\"'\s]{12,})"),
]

ALLOW_SUBSTRINGS = [
    "REPLACE_WITH_",
    "placeholder",
    "org_placeholder",
    "prj_demo",
    "img_demo",
    "base_demo",
    "stream_demo",
    "ingestor_demo",
    "supersecret",
    "regsecret",
    "toksecret",
    "validatorsecret",
    "should_redact",
    "urlsecret",
    "sigsecret",
    "streamsecret",
    "keysecret",
    "live_secret",
    "THETA_",
    "theta_bad_json",
    "Missing ",
    "required",
]

BINARY_SUFFIXES = {
    ".png",
    ".jpg",
    ".jpeg",
    ".mp4",
    ".ogg",
    ".mp3",
    ".pyc",
    ".zip",
    ".gz",
}


def iter_file_text(paths: Iterable[str]) -> Iterable[tuple[str, str]]:
    for raw in paths:
        path = pathlib.Path(raw)
        if not path.exists() or path.is_dir() or ".git" in path.parts:
            continue
        if path.suffix.lower() in BINARY_SUFFIXES:
            continue
        yield str(path), path.read_text(errors="ignore")


def allowed(line: str) -> bool:
    return any(item in line for item in ALLOW_SUBSTRINGS)


def scan_text(label: str, text: str) -> list[str]:
    findings: list[str] = []
    for line_no, line in enumerate(text.splitlines(), 1):
        if allowed(line):
            continue
        for pattern in PATTERNS:
            if pattern.search(line):
                findings.append(f"{label}:{line_no}: {line[:200]}")
                break
    return findings


def main(argv: list[str]) -> int:
    findings: list[str] = []
    if argv:
        for label, text in iter_file_text(argv):
            findings.extend(scan_text(label, text))
    else:
        findings.extend(scan_text("stdin", sys.stdin.read()))

    if findings:
        print("Potential secrets found:")
        print("\n".join(findings))
        return 1
    print("Secret scan passed: no high-confidence secrets found")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
