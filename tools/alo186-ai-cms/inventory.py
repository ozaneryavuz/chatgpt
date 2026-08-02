from __future__ import annotations

import json
from pathlib import Path

from core import Finding, InventoryItem, collect_schema_types, extract_jsonld, first_match, normalize_route, strip_markup


def relative_route(repo: Path, path: Path) -> str:
    rel = path.relative_to(repo / "alo186").as_posix()
    if rel == "index.html":
        return "/"
    return normalize_route("/" + (rel[:-11] if rel.endswith("/index.html") else rel))


def build_inventory(repo: Path) -> tuple[list[InventoryItem], list[Finding]]:
    root = repo / "alo186"
    if not root.is_dir():
        return [], [Finding("error", "alo186_root_missing", str(root), "alo186 kaynak klasörü yok")]
    findings: list[Finding] = []
    items: list[InventoryItem] = []
    for path in sorted(root.rglob("*.html")):
        if any(part.startswith(".") for part in path.relative_to(root).parts):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="strict")
        except UnicodeDecodeError as exc:
            findings.append(Finding("error", "html_not_utf8", path.relative_to(repo).as_posix(), str(exc)))
            continue
        canonical_url = first_match(r'<link\b[^>]*rel=["\']canonical["\'][^>]*href=["\']([^"\']+)', text)
        route = relative_route(repo, path)
        types: set[str] = set()
        for payload in extract_jsonld(text):
            types.update(collect_schema_types(payload))
        items.append(InventoryItem(
            route=route,
            canonical=normalize_route(canonical_url) if canonical_url else route,
            title=first_match(r"<title>(.*?)</title>", text),
            h1=strip_markup(first_match(r"<h1\b[^>]*>(.*?)</h1>", text)),
            description=first_match(r'<meta\b[^>]*name=["\']description["\'][^>]*content=["\']([^"\']+)', text),
            source=path.relative_to(repo).as_posix(),
            schema_types=tuple(sorted(types)),
        ))

    routing = [root / "deployment/routing-manifest.json", *sorted((root / "deployment/routing-overlays").glob("*.json"))]
    seen: dict[str, str] = {}
    for path in routing:
        if not path.is_file():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            findings.append(Finding("error", "routing_json_invalid", path.relative_to(repo).as_posix(), str(exc)))
            continue
        routes = data.get("routes", []) if isinstance(data, dict) else []
        if not isinstance(routes, list):
            findings.append(Finding("error", "routing_routes_invalid", path.relative_to(repo).as_posix(), "routes dizi değil"))
            continue
        for raw in routes:
            if not isinstance(raw, dict):
                continue
            route = normalize_route(str(raw.get("canonicalPath") or raw.get("path") or ""))
            if not route:
                continue
            current = path.relative_to(repo).as_posix()
            if route in seen and seen[route] != current:
                findings.append(Finding("warning", "route_in_multiple_manifests", route, f"{seen[route]} | {current}"))
            seen[route] = current
            if not any(item.route == route or item.canonical == route for item in items):
                source = str(raw.get("source") or raw.get("file") or current)
                items.append(InventoryItem(route, route, "", "", "", source, ()))

    canonicals: dict[str, set[str]] = {}
    for item in items:
        if item.canonical and item.source.endswith(".html"):
            canonicals.setdefault(item.canonical, set()).add(item.source)
    for route, sources in canonicals.items():
        if len(sources) > 1:
            findings.append(Finding("warning", "duplicate_canonical_inventory", route, ", ".join(sorted(sources))))
    return items, findings
