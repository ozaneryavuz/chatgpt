from __future__ import annotations

import hashlib
from pathlib import Path

MARKER = 'data-alo186-article-next-step="true"'


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


def run(site: Path, base_path: str = "") -> dict:
    site = site.resolve()
    base_path = normalize_base_path(base_path)
    if not base_path:
        return {"ok": True, "basePath": "", "updatedPages": 0}
    updated = 0
    source = 'data-path="/'
    target = f'data-path="{base_path}/'
    for path in sorted(site.glob("haberler/*/index.html")):
        text = path.read_text(encoding="utf-8", errors="ignore")
        if MARKER not in text or source not in text:
            continue
        text = text.replace(source, target, 1)
        path.write_text(text, encoding="utf-8")
        updated += 1
    recompute(site)
    return {"ok": True, "basePath": base_path, "updatedPages": updated}
