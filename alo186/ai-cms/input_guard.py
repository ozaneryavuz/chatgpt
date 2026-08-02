#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit


EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)
PHONE_RE = re.compile(
    r"(?<!\d)(?:\+?90[\s().-]*)?(?:0[\s().-]*)?(?:[2-5]\d{2})[\s().-]*\d{3}[\s.-]*\d{2}[\s.-]*\d{2}(?!\d)"
)
IBAN_RE = re.compile(r"\bTR(?:[\s-]*\d){24}\b", re.I)
LABELED_IDENTIFIER_RE = re.compile(
    r"\b(?:tesisat|abonelik|abone|müşteri|musteri|sözleşme|sozlesme|sayaç|sayac|vergi|kimlik|tckn|tc)"
    r"(?:\s+(?:no|numarası|numarasi|kimlik))?\s*[:#-]?\s*\d{5,}\b",
    re.I,
)
TCKN_CANDIDATE_RE = re.compile(r"(?<!\d)\d{11}(?!\d)")
FORBIDDEN_KEYS = {
    "email",
    "e-mail",
    "phone",
    "telefon",
    "mobile",
    "cep",
    "address",
    "adres",
    "tckn",
    "tc_kimlik_no",
    "tcKimlikNo",
    "iban",
    "installationNumber",
    "tesisatNo",
    "subscriptionNumber",
    "abonelikNo",
    "customerNumber",
    "musteriNo",
}
URL_KEYS = {"url", "path"}


class GuardError(RuntimeError):
    pass


def tckn_valid(value: str) -> bool:
    if len(value) != 11 or not value.isdigit() or value[0] == "0":
        return False
    digits = [int(char) for char in value]
    tenth = ((sum(digits[0:9:2]) * 7) - sum(digits[1:8:2])) % 10
    eleventh = sum(digits[:10]) % 10
    return digits[9] == tenth and digits[10] == eleventh


def normalize_path(parts: tuple[str, ...]) -> str:
    return ".".join(parts) if parts else "$"


def scan_text(value: str, path: tuple[str, ...], *, url_field: bool = False) -> list[str]:
    violations: list[str] = []
    field = normalize_path(path)
    candidate = value.strip()

    if url_field:
        parsed = urlsplit(candidate)
        # URLs can legitimately contain @ in authority; only query/fragment are scanned.
        candidate = " ".join(filter(None, (parsed.path, parsed.query, parsed.fragment)))

    if EMAIL_RE.search(candidate):
        violations.append(f"{field}: kişisel e-posta kalıbı")
    if PHONE_RE.search(candidate):
        violations.append(f"{field}: telefon numarası kalıbı")
    if IBAN_RE.search(candidate.replace("-", " ")):
        violations.append(f"{field}: IBAN kalıbı")
    if LABELED_IDENTIFIER_RE.search(candidate):
        violations.append(f"{field}: abonelik/tesisat/müşteri kimliği kalıbı")
    if any(tckn_valid(match.group(0)) for match in TCKN_CANDIDATE_RE.finditer(candidate)):
        violations.append(f"{field}: geçerli T.C. kimlik numarası kalıbı")
    return violations


def scan(value: Any, path: tuple[str, ...] = ()) -> list[str]:
    violations: list[str] = []
    if isinstance(value, dict):
        for key, nested in value.items():
            key_text = str(key)
            child_path = (*path, key_text)
            if key_text in FORBIDDEN_KEYS and nested not in (None, "", [], {}):
                violations.append(f"{normalize_path(child_path)}: kişisel veri alanı yasak")
            violations.extend(scan(nested, child_path))
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            violations.extend(scan(nested, (*path, str(index))))
    elif isinstance(value, str):
        violations.extend(scan_text(value, path, url_field=bool(path and path[-1] in URL_KEYS)))
    return violations


def validate_brief_file(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise GuardError(f"Brief bulunamadı: {path}") from exc
    except json.JSONDecodeError as exc:
        raise GuardError(f"Brief JSON geçersiz: {exc}") from exc
    if not isinstance(payload, dict):
        raise GuardError("Brief kökü JSON nesnesi olmalıdır.")
    violations = sorted(set(scan(payload)))
    if violations:
        raise GuardError(
            "AI sağlayıcısına gönderim engellendi. Brief kişisel veya müşteri verisi kalıbı taşıyor:\n- "
            + "\n- ".join(violations)
        )
    return {
        "ok": True,
        "brief": str(path),
        "checkedFields": len(payload),
        "personalDataSent": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="ALO186 AI CMS briefini OpenAI çağrısından önce kişisel/müşteri verisi kalıplarına karşı denetler."
    )
    parser.add_argument("--brief", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = validate_brief_file(args.brief)
    except GuardError as exc:
        print(f"AI CMS input guard: {exc}", file=sys.stderr)
        raise SystemExit(1)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
