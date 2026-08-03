from __future__ import annotations

import argparse
import json
import urllib.parse
import xml.etree.ElementTree as ET
from copy import deepcopy
from pathlib import Path
from typing import Any

VERSION = 225
CANONICAL_ORIGIN = "https://alo186.com"
DEDICATED_SITEMAPS = (
    "sitemap-electric-project-v200.xml",
    "sitemap-growth-v207.xml",
)


def _namespace(root: ET.Element) -> tuple[str, str]:
    if root.tag.rsplit("}", 1)[-1] != "urlset":
        raise RuntimeError(f"Sitemap urlset olmalıdır: {root.tag}")
    namespace = root.tag.split("}", 1)[0].lstrip("{") if "}" in root.tag else ""
    return namespace, f"{{{namespace}}}" if namespace else ""


def _canonical_url(value: str) -> str:
    parsed = urllib.parse.urlsplit(str(value or "").strip())
    if parsed.scheme != "https" or (parsed.hostname or "").casefold().removeprefix("www.") != "alo186.com":
        raise RuntimeError(f"Canonical sitemap dışı URL: {value!r}")
    path = "/" + (parsed.path or "/").lstrip("/")
    return urllib.parse.urlunsplit(("https", "alo186.com", path, "", ""))


def _records(path: Path) -> tuple[ET.ElementTree, ET.Element, str, list[tuple[str, ET.Element]]]:
    try:
        tree = ET.parse(path)
    except ET.ParseError as exc:
        raise RuntimeError(f"Sitemap XML ayrıştırılamadı: {path}: {exc}") from exc
    root = tree.getroot()
    namespace, prefix = _namespace(root)
    records: list[tuple[str, ET.Element]] = []
    for node in root.findall(f"{prefix}url"):
        loc = node.find(f"{prefix}loc")
        if loc is None or not str(loc.text or "").strip():
            raise RuntimeError(f"Sitemap boş loc taşıyor: {path}")
        records.append((_canonical_url(str(loc.text)), node))
    return tree, root, namespace, records


def run(site: Path, source_root: Path) -> dict[str, Any]:
    site = site.resolve()
    source_root = source_root.resolve()
    main_path = site / "sitemap.xml"
    if not main_path.is_file():
        raise FileNotFoundError(main_path)

    tree, root, namespace, current_records = _records(main_path)
    if namespace:
        ET.register_namespace("", namespace)
    prefix = f"{{{namespace}}}" if namespace else ""
    existing = {url for url, _node in current_records}
    imported: list[str] = []
    per_source: dict[str, dict[str, int]] = {}

    for name in DEDICATED_SITEMAPS:
        source = source_root / name
        if not source.is_file():
            raise FileNotFoundError(source)
        _source_tree, _source_root, _source_namespace, records = _records(source)
        added = 0
        duplicate = 0
        for url, node in records:
            if url in existing:
                duplicate += 1
                continue
            clone = deepcopy(node)
            loc = clone.find(f"{{{_source_namespace}}}loc" if _source_namespace else "loc")
            if loc is None:
                raise RuntimeError(f"Sitemap loc kopyalanamadı: {source}: {url}")
            loc.text = url
            if _source_namespace != namespace:
                rebuilt = ET.Element(f"{prefix}url")
                for child in list(clone):
                    local = child.tag.rsplit("}", 1)[-1]
                    copied = ET.SubElement(rebuilt, f"{prefix}{local}")
                    copied.text = child.text
                clone = rebuilt
            root.append(clone)
            existing.add(url)
            imported.append(url)
            added += 1
        per_source[name] = {"declared": len(records), "added": added, "duplicate": duplicate}

    tree.write(main_path, encoding="utf-8", xml_declaration=True)
    # Parse the exact output and ensure the operation is idempotent and unique.
    _tree, _root, _namespace, final_records = _records(main_path)
    final_urls = [url for url, _node in final_records]
    if len(final_urls) != len(set(final_urls)):
        raise RuntimeError("Birleştirilmiş sitemap yinelenen URL taşıyor")
    for url in imported:
        if final_urls.count(url) != 1:
            raise RuntimeError(f"Birleştirilen URL tekil değil: {url}")

    report = {
        "version": VERSION,
        "canonicalOrigin": CANONICAL_ORIGIN,
        "sourceSitemaps": list(DEDICATED_SITEMAPS),
        "beforeUrlCount": len(current_records),
        "importedUrlCount": len(imported),
        "afterUrlCount": len(final_urls),
        "unique": True,
        "sources": per_source,
    }
    receipt = site / "sitemap-merge-v225.json"
    receipt.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="ALO186 dedicated sitemap URL'lerini canonical sitemap'e birleştirir")
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument(
        "--source-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
    )
    args = parser.parse_args()
    print(json.dumps(run(args.site, args.source_root), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
