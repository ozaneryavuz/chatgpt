from __future__ import annotations

import xml.etree.ElementTree as ET
from collections.abc import Iterable
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

WRITER_ORIGIN = "https://www.alo186.com"
ALO186_HOSTS = {"alo186.com", "www.alo186.com"}


def _namespace(root: ET.Element) -> tuple[str, str]:
    if root.tag.startswith("{") and "}" in root.tag:
        namespace = root.tag[1:].split("}", 1)[0]
    else:
        namespace = ""
    return namespace, f"{{{namespace}}}" if namespace else ""


def _canonicalize_url(value: str) -> str:
    raw = value.strip()
    parsed = urlsplit(raw)
    if parsed.scheme == "https" and parsed.hostname in ALO186_HOSTS:
        preferred = urlsplit(WRITER_ORIGIN)
        return urlunsplit((preferred.scheme, preferred.netloc, parsed.path, parsed.query, parsed.fragment))
    return raw


def ensure_canonical_routes(path: Path, routes: Iterable[str]) -> dict[str, object]:
    """Add legacy growth routes without creating host-collapsed duplicates.

    The Pages pipeline intentionally keeps ``www`` until its legacy smoke gate
    completes. The final live-quality pass later rewrites the single remaining
    URL to the apex host. Therefore these route writers first collapse any apex
    and ``www`` copies to one ``www`` node, preserving the first node and all of
    its metadata. Malformed XML fails closed instead of being rewritten by text.
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
        canonical = f"{WRITER_ORIGIN}{normalized_route}"
        if canonical in seen:
            continue
        url_node = ET.SubElement(root, f"{ns}url")
        loc_node = ET.SubElement(url_node, f"{ns}loc")
        loc_node.text = canonical
        seen.add(canonical)
        added.append(canonical)

    if namespace:
        ET.register_namespace("", namespace)

    ET.indent(tree, space="  ")
    tree.write(path, encoding="utf-8", xml_declaration=True)
    ET.parse(path)

    return {
        "urlCount": len(seen),
        "added": added,
        "normalized": normalized,
        "duplicatesRemoved": removed,
        "writerOrigin": WRITER_ORIGIN,
        "policy": "legacy-www-writer-then-final-apex-canonical-path-unique",
    }
