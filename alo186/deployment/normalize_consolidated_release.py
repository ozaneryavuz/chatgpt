from __future__ import annotations

import json
from pathlib import Path


def normalize_base_path(value: str) -> str:
    cleaned = str(value or "").strip()
    if not cleaned or cleaned == "/":
        return ""
    return "/" + cleaned.strip("/")


def canonical_identity(value: str, base_path: str) -> str:
    text = str(value or "").strip()
    trailing = text.endswith("/") and text != "/"
    raw = "/" + text.strip("/")
    if base_path:
        if raw == base_path:
            raw = "/"
        elif raw.startswith(base_path + "/"):
            raw = raw[len(base_path) :]
    if trailing and raw != "/" and not raw.endswith("/"):
        raw += "/"
    return raw


def run(site: Path, base_path: str = "") -> dict:
    site = site.resolve()
    base_path = normalize_base_path(base_path)
    release_path = site / "alo186-release.json"
    release = json.loads(release_path.read_text(encoding="utf-8"))
    consolidation = release.get("contentConsolidation") or {}
    aliases = {
        canonical_identity(item.get("aliasPath"), "")
        for item in consolidation.get("aliases") or []
        if isinstance(item, dict) and item.get("aliasPath")
    }
    routes = release.get("routes") or []
    filtered = [
        route for route in routes
        if canonical_identity(route.get("canonicalPath"), base_path) not in aliases
    ]
    removed = len(routes) - len(filtered)
    release["routes"] = filtered
    release["routeCount"] = len(filtered)
    release["articleCount"] = sum(1 for route in filtered if route.get("type") == "article")
    release.setdefault("contentConsolidation", {})["projectReleaseAliasesRemoved"] = removed
    release_path.write_text(json.dumps(release, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    pages_path = site / "pages-release.json"
    if pages_path.is_file():
        pages = json.loads(pages_path.read_text(encoding="utf-8"))
        pages["routeCount"] = len(filtered)
        pages.setdefault("contentConsolidation", {})["projectReleaseAliasesRemoved"] = removed
        pages_path.write_text(json.dumps(pages, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    expected = len(aliases) if base_path else 0
    if base_path and removed != expected:
        raise RuntimeError(
            f"Project release alias normalizasyonu eksik: kaldırılan={removed}, beklenen={expected}"
        )
    return {
        "ok": True,
        "basePath": base_path,
        "aliasCount": len(aliases),
        "removedRoutes": removed,
        "routeCount": len(filtered),
        "articleCount": release["articleCount"],
    }
