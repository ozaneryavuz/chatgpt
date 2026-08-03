from __future__ import annotations

import xml.etree.ElementTree as ET
from collections.abc import Iterable
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

CANONICAL_ORIGIN = "https://alo186.com"
LEGACY_HOSTS = {"www.alo186.com"}
SITEMAP_NAMESPACE = "http://www.sitemaps.org/schemas/sitemap/0.9"


def _canonicalize_url(value: str) -> str:
    raw = value.strip()
    parsed = urlsplit(raw)
    if parsed.scheme == "https" and parsed.hostname in LEGACY_HOSTS:
        netloc = "alo186.com"
        if parsed.port:
            netloc = f"{netloc}:{parsed.port}"
        return urlunsplit((parsed.scheme, netloc, parsed.path, parsed.query, parsed.fragment))
    return raw


def _namespace(root: ET.Element) -> tuple[str, str]:
    if root.tag.startswith("{") and "}" in root.tag:
        namespace = root.tag[1:].split("}", 1)[0]
    else:
        namespace = ""
    return namespace, f"{{{namespace}}}" if namespace else ""


def ensure_canonical_routes(path: Path, routes: Iterable[str]) -> dict[str, object]:
    """Add canonical routes and remove host-collapsed duplicates at the writer.

    The first matching URL node is retained with all of its metadata. Later nodes
    that normalize to the same apex URL are removed. Malformed XML and non-urlset
    documents fail closed instead of being rewritten heuristically.
    """

    tree = ET.parse(path)
    root = tree.getroot()
    if root.tag.rsplit("}", 1)[-1] != "urlset":
        raise ValueError("Sitemap kökü urlset değil")

    namespace, ns = _namespace(root)
    seen: set[str] = set()
    removed: list[str] = []
    normalized: list[str] = []

    for url_node in list(root.findall(f"{ns}url")):
        loc_node = url_node.find(f"{ns}loc")
        if loc_node is None or not loc_node.text:
            continue
        original = loc_node.text.strip()
        canonical = _canonicalize_url(original)
        if canonical != original:
            loc_node.text = canonical
            normalized.append(canonical)
        if canonical in seen:
            root.remove(url_node)
            removed.append(canonical)
            continue
        seen.add(canonical)

    added: list[str] = []
    for route in routes:
        normalized_route = "/" + str(route).strip().lstrip("/")
        canonical = f"{CANONICAL_ORIGIN}{normalized_route}"
        if canonical in seen:
            continue
        url_node = ET.SubElement(root, f"{ns}url")
        loc_node = ET.SubElement(url_node, f"{ns}loc")
        loc_node.text = canonical
        seen.add(canonical)
        added.append(canonical)

    if namespace:
        ET.register_namespace("", namespace)
    elif root.tag == "urlset":
        # Existing non-namespaced sitemaps remain non-namespaced; no silent schema
        # migration is performed by a route writer.
        pass

    ET.indent(tree, space="  ")
    tree.write(path, encoding="utf-8", xml_declaration=True)
    ET.parse(path)

    return {
        "urlCount": len(seen),
        "added": added,
        "normalized": normalized,
        "duplicatesRemoved": removed,
        "canonicalOrigin": CANONICAL_ORIGIN,
    }
