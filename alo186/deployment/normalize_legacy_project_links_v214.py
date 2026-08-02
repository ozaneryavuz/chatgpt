from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

VERSION = 214
LEGACY_PREFIX = "/chatgpt"
URL_ATTRIBUTES = ("href", "src", "action", "poster", "data-src", "data-href")

ATTRIBUTE_PATTERN = re.compile(
    r"(?P<prefix>\b(?:href|src|action|poster|data-src|data-href)\s*=\s*)"
    r"(?P<quote>[\"'])(?P<value>/chatgpt(?:[^\"']*)?)(?P=quote)",
    re.I,
)
SRCSET_PATTERN = re.compile(
    r"(?P<prefix>\bsrcset\s*=\s*)(?P<quote>[\"'])(?P<value>[^\"']*)(?P=quote)",
    re.I,
)
RESIDUAL_PATTERN = re.compile(
    r"\b(?:href|src|action|poster|data-src|data-href|srcset)\s*=\s*[\"'][^\"']*"
    r"(?:^|[\s,])/chatgpt(?:[/#?]|[\"'])",
    re.I,
)


def normalize_base_path(value: str) -> str:
    cleaned = str(value or "").strip()
    return "" if not cleaned or cleaned == "/" else "/" + cleaned.strip("/")


def rewrite_legacy_url(value: str) -> str:
    """Map only root-relative legacy project URLs to custom-domain root URLs."""
    if value == LEGACY_PREFIX:
        return "/"
    if value.startswith(LEGACY_PREFIX + "/"):
        return value[len(LEGACY_PREFIX) :]
    if value.startswith(LEGACY_PREFIX + "?") or value.startswith(LEGACY_PREFIX + "#"):
        return "/" + value[len(LEGACY_PREFIX) :]
    return value


def rewrite_srcset(value: str) -> tuple[str, int]:
    changed = 0
    entries: list[str] = []
    for raw_entry in value.split(","):
        entry = raw_entry.strip()
        if not entry:
            entries.append(entry)
            continue
        parts = entry.split()
        original = parts[0]
        updated = rewrite_legacy_url(original)
        if updated != original:
            parts[0] = updated
            changed += 1
        entries.append(" ".join(parts))
    return ", ".join(entries), changed


def normalize_html(text: str) -> tuple[str, int]:
    replacements = 0

    def replace_attribute(match: re.Match[str]) -> str:
        nonlocal replacements
        value = match.group("value")
        updated = rewrite_legacy_url(value)
        if updated == value:
            return match.group(0)
        replacements += 1
        return f"{match.group('prefix')}{match.group('quote')}{updated}{match.group('quote')}"

    updated = ATTRIBUTE_PATTERN.sub(replace_attribute, text)

    def replace_srcset(match: re.Match[str]) -> str:
        nonlocal replacements
        value, count = rewrite_srcset(match.group("value"))
        replacements += count
        if not count:
            return match.group(0)
        return f"{match.group('prefix')}{match.group('quote')}{value}{match.group('quote')}"

    updated = SRCSET_PATTERN.sub(replace_srcset, updated)
    return updated, replacements


def residual_references(text: str) -> list[str]:
    values: list[str] = []
    for match in re.finditer(
        r"\b(?:href|src|action|poster|data-src|data-href|srcset)\s*=\s*[\"']([^\"']*)[\"']",
        text,
        re.I,
    ):
        value = match.group(1)
        if value.startswith(LEGACY_PREFIX) or any(
            item.strip().split(" ", 1)[0].startswith(LEGACY_PREFIX)
            for item in value.split(",")
            if item.strip()
        ):
            values.append(value)
    return values


def run(site: Path, base_path: str = "") -> dict:
    site = site.resolve()
    normalized_base = normalize_base_path(base_path)
    if normalized_base:
        return {
            "ok": True,
            "version": VERSION,
            "basePath": normalized_base,
            "mode": "project-path-preserved",
            "htmlFilesChecked": 0,
            "changedFiles": 0,
            "rewrittenReferences": 0,
            "residualLegacyReferences": 0,
        }

    checked = 0
    changed_files = 0
    rewritten = 0
    residual: list[dict[str, object]] = []
    for path in sorted(site.rglob("*.html")):
        checked += 1
        original = path.read_text(encoding="utf-8", errors="strict")
        updated, count = normalize_html(original)
        if count:
            path.write_text(updated, encoding="utf-8")
            changed_files += 1
            rewritten += count
        remaining = residual_references(updated)
        if remaining:
            residual.append({
                "file": path.relative_to(site).as_posix(),
                "references": remaining[:10],
            })

    result = {
        "ok": not residual,
        "version": VERSION,
        "basePath": normalized_base,
        "mode": "custom-domain-normalized",
        "htmlFilesChecked": checked,
        "changedFiles": changed_files,
        "rewrittenReferences": rewritten,
        "residualLegacyReferences": sum(len(item["references"]) for item in residual),
        "residualExamples": residual[:20],
    }
    if residual:
        raise RuntimeError(
            "ALO186 legacy /chatgpt bağlantı normalizasyonu tamamlanamadı:\n- "
            + "\n- ".join(
                f"{item['file']}: {item['references']}" for item in residual[:20]
            )
        )
    return result


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Custom-domain artifactındaki eski /chatgpt HTML URL niteliklerini kök rotalara çevirir; "
            "project-path artifactına dokunmaz."
        )
    )
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--base-path", default="")
    args = parser.parse_args()
    print(json.dumps(run(args.site, args.base_path), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
