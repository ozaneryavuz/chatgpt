from __future__ import annotations

import xml.etree.ElementTree as ET
from collections.abc import Iterable
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

DEFAULT_WRITER_ORIGIN = "https://www.alo186.com"
ALO186_HOSTS = {"alo186.com", "www.alo186.com"}


def _namespace(root: ET.Element) -> tuple[str, str]:
    if root.tag.startswith("{") and "}" in root.tag:
        namespace = root.tag[1:].split("}", 1)[0]
    else:
        namespace = ""
    return namespace, f"{{{namespace}}}" if namespace else ""


def _preferred_origin(root: ET.Element, ns: str) -> str:
    """Preserve the sitemap stage's current host contract.

    GitHub Pages preparation intentionally uses ``www`` until its legacy smoke
    gate finishes; the final live-quality pass then normalizes the artifact to
    apex. A growth writer must deduplicate without prematurely changing that
    stage contract.
    """

    for loc_node in root.findall(f"{ns}url/{ns}loc"):
        if not loc_node.text:
            continue
        parsed = urlsplit(loc_node.text.strip())
        if parsed.scheme == "https" and parsed.hostname in ALO186_HOSTS:
            return f"https://{parsed.netloc}"
    return DEFAULT_WRITER_ORIGIN


def _canonicalize_url(value: str, preferred_origin: str) -> str:
    raw = value.strip()
    parsed = urlsplit(raw)
    if parsed.scheme == "https" and parsed.hostname in ALO186_HOSTS:
        preferred = urlsplit(preferred_origin)
        return urlunsplit((preferred.scheme, preferred.netloc, parsed.path, parsed.query, parsed.fragment))
    return raw


def ensure_canonical_routes(path: Path, routes: Iterable[str]) -> dict[str, object]:
    """Add routes and remove host-collapsed duplicates at their writer source.

    The existing sitemap stage decides whether ``www`` or apex is authoritative.
    All ALO186 loc values are compared under that preferred origin, so an apex and
    a ``www`` node for the same path collapse before the finalizer runs. The first
    node and its metadata are retained. Malformed XML fails closed.
    """

    tree = ET.parse(path)
    root = tree.getroot()
    if root.tag.rsplit("}", 1)[-1] != "urlset":
        raise ValueError("Sitemap kökü urlset değil")

    namespace, ns = _namespace(root)
    preferred_origin = _preferred_origin(root, ns)
    seen: set[str] = set()
    removed: list[str] = []
    normalized: list[str] = []

    for url_node in list(root.findall(f"{ns}url")):
        loc_node = url_node.find(f"{ns}loc")
        if loc_node is None or not loc_node.text:
            continue
        original = loc_node.text.strip()
        canonical = _canonicalize_url(original, preferred_origin)
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
        canonical = f"{preferred_origin}{normalized_route}"
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
        "preferredOrigin": preferred_origin,
        "policy": "stage-host-preserved-canonical-path-unique",
    }
