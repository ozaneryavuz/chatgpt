from __future__ import annotations

"""Fail-closed final sitemap canonical-origin normalizer.

Growth injectors may append a small number of legacy ``www`` URLs after the
initial Pages preparation. This finalizer converts only the known ALO186 www
host to the apex canonical host, preserves the first URL node and its metadata,
and removes duplicates created by that normalization. Unknown origins,
query strings, fragments and malformed XML stop the release.
"""

import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

CANONICAL_ORIGIN = "https://alo186.com"
ALLOWED_NETLOCS = {"alo186.com", "www.alo186.com"}


def normalize(site: Path) -> dict[str, object]:
    sitemap = site / "sitemap.xml"
    if not sitemap.is_file():
        raise FileNotFoundError(f"sitemap.xml bulunamadı: {sitemap}")

    try:
        tree = ET.parse(sitemap)
    except ET.ParseError as exc:
        raise RuntimeError(f"sitemap.xml parse edilemiyor: {exc}") from exc

    root = tree.getroot()
    seen: set[str] = set()
    normalized_count = 0
    removed: list[str] = []

    for url_node in list(root):
        loc = url_node.find("{*}loc")
        raw = (loc.text or "").strip() if loc is not None else ""
        if not raw:
            raise RuntimeError("Sitemap URL kaydı loc taşımıyor")

        parsed = urlsplit(raw)
        if parsed.scheme != "https" or parsed.netloc.casefold() not in ALLOWED_NETLOCS:
            raise RuntimeError(f"Sitemap origin izinli değil: {raw}")
        if parsed.username or parsed.password or parsed.port:
            raise RuntimeError(f"Sitemap URL kullanıcı bilgisi veya port taşıyor: {raw}")
        if parsed.query or parsed.fragment:
            raise RuntimeError(f"Sitemap URL query veya fragment taşıyor: {raw}")
        if not parsed.path.startswith("/"):
            raise RuntimeError(f"Sitemap path mutlak değil: {raw}")

        canonical = urlunsplit(("https", "alo186.com", parsed.path or "/", "", ""))
        if canonical in seen:
            root.remove(url_node)
            removed.append(canonical)
            continue
        seen.add(canonical)

        if raw != canonical:
            if loc is None:  # defensive; raw cannot be non-empty in this case
                raise RuntimeError("Sitemap loc düğümü beklenmedik biçimde eksik")
            loc.text = canonical
            normalized_count += 1

    changed = bool(normalized_count or removed)
    if changed:
        ET.register_namespace("", "http://www.sitemaps.org/schemas/sitemap/0.9")
        ET.register_namespace("xhtml", "http://www.w3.org/1999/xhtml")
        tree.write(sitemap, encoding="utf-8", xml_declaration=True)

    reparsed = ET.parse(sitemap).getroot()
    locations = [
        (node.text or "").strip()
        for node in reparsed.findall(".//{*}loc")
        if (node.text or "").strip()
    ]
    if len(locations) != len(set(locations)):
        raise RuntimeError("Sitemap canonical tekilleştirmesi başarısız")
    if any(not value.startswith(CANONICAL_ORIGIN + "/") for value in locations):
        raise RuntimeError("Sitemap final artifactında apex dışı origin kaldı")

    return {
        "ok": True,
        "version": 236,
        "canonicalOrigin": CANONICAL_ORIGIN,
        "normalizedWwwCount": normalized_count,
        "duplicateCountRemoved": len(removed),
        "remainingUrlCount": len(locations),
        "changed": changed,
    }
