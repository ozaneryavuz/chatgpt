#!/usr/bin/env python3
"""Prevent user-facing ALO186 content from publishing an incorrect device-damage deadline."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ALLOWED_SUFFIXES = {".html", ".htm", ".js", ".mjs", ".json", ".md", ".txt", ".xml"}
EXCLUDED_PARTS = {"audits", "reports", "artifacts", "node_modules", ".git"}

DAMAGE_TERMS = re.compile(r"\b(cihaz|teçhizat|techizat|hasar|zarar)\w*\b", re.IGNORECASE)
APPLICATION_TERMS = re.compile(r"\b(başvur|basvur|talep|tazmin|dağıtım şirket|dagitim sirket|edaş|edas)\w*", re.IGNORECASE)
WRONG_DEADLINE = re.compile(r"\b30\s*gün\b", re.IGNORECASE)
CORRECT_DEADLINE = re.compile(r"\b10\s*iş\s*gün(?:ü|lük|de|den|içinde|icerisinde|içerisinde)?\b", re.IGNORECASE)


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.replace("&nbsp;", " ")).strip()


def windows(text: str, pattern: re.Pattern[str], radius: int = 260):
    for match in pattern.finditer(text):
        start = max(0, match.start() - radius)
        end = min(len(text), match.end() + radius)
        yield match, text[start:end]


def is_user_facing(path: Path) -> bool:
    if path.suffix.lower() not in ALLOWED_SUFFIXES:
        return False
    relative_parts = set(path.relative_to(ROOT).parts)
    return not (relative_parts & EXCLUDED_PARTS)


def scan() -> tuple[list[str], list[str]]:
    violations: list[str] = []
    correct_locations: list[str] = []

    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or not is_user_facing(path):
            continue
        try:
            raw = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        text = normalize(raw)

        for match, context in windows(text, WRONG_DEADLINE):
            if DAMAGE_TERMS.search(context) and APPLICATION_TERMS.search(context):
                rel = path.relative_to(ROOT)
                excerpt = normalize(context)[:520]
                violations.append(f"{rel}:{match.start()} -> {excerpt}")

        for match, context in windows(text, CORRECT_DEADLINE):
            if DAMAGE_TERMS.search(context) and APPLICATION_TERMS.search(context):
                rel = path.relative_to(ROOT)
                correct_locations.append(f"{rel}:{match.start()}")

    return violations, correct_locations


def self_test() -> None:
    bad = "Cihaz hasarı için zararın doğduğu tarihten itibaren 30 gün içinde EDAŞ kaydı açın."
    good = "Cihaz hasarı için zararın doğduğu tarihten itibaren 10 iş günü içinde ilgili dağıtım şirketine başvurun."
    unrelated = "Bakım planınızı 30 gün içinde yeniden kontrol edin."

    assert WRONG_DEADLINE.search(bad)
    assert DAMAGE_TERMS.search(bad) and APPLICATION_TERMS.search(bad)
    assert CORRECT_DEADLINE.search(good)
    assert not (DAMAGE_TERMS.search(unrelated) and APPLICATION_TERMS.search(unrelated))


def main() -> int:
    self_test()
    violations, correct_locations = scan()

    print(f"ALO186 source root: {ROOT}")
    print(f"Verified correct device-damage deadline references: {len(correct_locations)}")
    for location in correct_locations[:20]:
        print(f"  OK  {location}")

    if violations:
        print("\nERROR: Device/equipment damage application context contains '30 gün'.")
        print("EPDK consumer guidance requires application to the distribution company within 10 business days from the date the damage arose.")
        for violation in violations:
            print(f"  BAD {violation}")
        return 1

    if not correct_locations:
        print("\nERROR: No source reference linking device damage application to '10 iş günü' was found.")
        return 1

    print("\nPASS: No incorrect 30-day device-damage application deadline was found in user-facing source files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
