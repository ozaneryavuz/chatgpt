from __future__ import annotations

import argparse
import hashlib
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

CANONICAL_ORIGIN = "https://alo186.com"
ALO186_HOSTS = {"alo186.com", "www.alo186.com"}


def _namespace(root: ET.Element) -> tuple[str, str]:
    if root.tag.startswith("{") and "}" in root.tag:
        namespace = root.tag[1:].split("}", 1)[0]
    else:
        namespace = ""
    return namespace, f"{{{namespace}}}" if namespace else ""


def _canonical_url(value: str) -> str:
    raw = value.strip()
    parsed = urlsplit(raw)
    if parsed.scheme in {"http", "https"} and parsed.hostname in ALO186_HOSTS:
        canonical = urlsplit(CANONICAL_ORIGIN)
        path = "/" + parsed.path.lstrip("/")
        return urlunsplit((canonical.scheme, canonical.netloc, path, parsed.query, parsed.fragment))
    return raw


def recompute_checksums(site: Path) -> None:
    checksum = site / "checksums.sha256"
    if checksum.exists():
        checksum.unlink()
    files = sorted(item for item in site.rglob("*") if item.is_file())
    checksum.write_text(
        "\n".join(
            f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.relative_to(site).as_posix()}"
            for path in files
        )
        + "\n",
        encoding="utf-8",
    )


def run(site: Path) -> dict[str, object]:
    site = site.resolve()
    sitemap = site / "sitemap.xml"
    if not sitemap.is_file():
        raise FileNotFoundError(f"Sitemap bulunamadı: {sitemap}")

    tree = ET.parse(sitemap)
    root = tree.getroot()
    if root.tag.rsplit("}", 1)[-1] != "urlset":
        raise ValueError("Sitemap kökü urlset değil")

    namespace, ns = _namespace(root)
    seen: set[str] = set()
    normalized = 0
    removed = 0

    for url_node in list(root.findall(f"{ns}url")):
        loc_node = url_node.find(f"{ns}loc")
        if loc_node is None or not loc_node.text:
            continue
        original = loc_node.text.strip()
        canonical = _canonical_url(original)
        if canonical != original:
            loc_node.text = canonical
            normalized += 1
        if canonical in seen:
            root.remove(url_node)
            removed += 1
            continue
        seen.add(canonical)

    if namespace:
        ET.register_namespace("", namespace)
    ET.indent(tree, space="  ")
    tree.write(sitemap, encoding="utf-8", xml_declaration=True)
    ET.parse(sitemap)

    remaining = []
    parsed = ET.parse(sitemap).getroot()
    _, final_ns = _namespace(parsed)
    for loc_node in parsed.findall(f"{final_ns}url/{final_ns}loc"):
        if loc_node.text:
            remaining.append(loc_node.text.strip())
    if len(remaining) != len(set(remaining)):
        raise RuntimeError("Final sitemapte yinelenen canonical URL kaldı")
    if any(urlsplit(value).hostname == "www.alo186.com" for value in remaining):
        raise RuntimeError("Final sitemapte www host kaldı")

    recompute_checksums(site)
    report = {
        "ok": True,
        "urlCount": len(remaining),
        "normalizedCount": normalized,
        "duplicateCountRemoved": removed,
        "canonicalOrigin": CANONICAL_ORIGIN,
        "policy": "final-apex-canonical-url-unique",
    }
    receipt = site / "pages-release.json"
    if receipt.is_file():
        payload = json.loads(receipt.read_text(encoding="utf-8"))
        payload["finalSitemapUniqueness"] = report
        receipt.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        recompute_checksums(site)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Final Pages sitemapini apex canonical ve URL tekilliği bakımından kapatır.")
    parser.add_argument("--site", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(run(args.site), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
