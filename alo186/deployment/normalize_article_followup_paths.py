from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

MARKER = 'data-alo186-article-next-step="true"'
ARTICLE_ROOT = "/haberler/"
DATA_PATH_PATTERN = re.compile(r'data-path=(["\'])(?:/chatgpt)?(/haberler/[^"\']+)\1', re.I)
ROOT_REFERENCE_PATTERN = re.compile(r'(["\'])/haberler/[^"\'\s<>]*', re.I)
NO_BUY_SOURCE = "tamamlayın; mevcut sistem yeterli"
NO_BUY_TARGET = "tamamlayın. Mevcut sistem yeterli"


def normalize_base_path(value: str) -> str:
    cleaned = str(value or "").strip()
    if not cleaned or cleaned == "/":
        return ""
    return "/" + cleaned.strip("/")


def recompute(site: Path) -> None:
    path = site / "checksums.sha256"
    if path.exists():
        path.unlink()
    lines = [
        f"{hashlib.sha256(item.read_bytes()).hexdigest()}  {item.relative_to(site).as_posix()}"
        for item in sorted(candidate for candidate in site.rglob("*") if candidate.is_file())
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def normalize_data_paths(text: str, base_path: str) -> str:
    def replacement(match: re.Match[str]) -> str:
        quote = match.group(1)
        canonical = match.group(2)
        public = f"{base_path}{canonical}" if base_path else canonical
        return f"data-path={quote}{public}{quote}"

    return DATA_PATH_PATTERN.sub(replacement, text)


def run(site: Path, base_path: str = "") -> dict:
    site = site.resolve()
    base_path = normalize_base_path(base_path)
    updated = 0
    checked = 0
    remaining: list[str] = []

    for path in sorted(site.glob("haberler/*/index.html")):
        text = path.read_text(encoding="utf-8", errors="ignore")
        if MARKER not in text:
            continue
        checked += 1
        original = text
        text = text.replace(NO_BUY_SOURCE, NO_BUY_TARGET)
        text = normalize_data_paths(text, base_path)
        if text != original:
            path.write_text(text, encoding="utf-8")
            updated += 1

        if base_path:
            panel = text.split(MARKER, 1)[1].split("</section>", 1)[0]
            if ROOT_REFERENCE_PATTERN.search(panel):
                remaining.append(path.relative_to(site).as_posix())

    recompute(site)
    if remaining:
        raise RuntimeError(
            "Project-path makale panelinde kök referansları kaldı: " + ", ".join(remaining[:20])
        )
    return {
        "ok": True,
        "basePath": base_path,
        "checkedPages": checked,
        "updatedPages": updated,
        "remainingRootReferences": 0,
        "checksumsRecomputed": True,
        "noBuySentenceNormalized": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Makale takip data-path değerlerini Pages base-path ile uyumlu hale getirir ve checksumları yeniler."
    )
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--base-path", default="")
    args = parser.parse_args()
    print(json.dumps(run(args.site, args.base_path), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
