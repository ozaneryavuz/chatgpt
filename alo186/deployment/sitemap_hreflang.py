from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

SITEMAP_NAMESPACE = "http://www.sitemaps.org/schemas/sitemap/0.9"
XHTML_NAMESPACE = "http://www.w3.org/1999/xhtml"
LANGUAGE_ALTERNATES_PATH = Path(__file__).with_name("language-alternates.json")


def normalize_route_path(value: Any) -> str:
    raw = str(value or "").strip()
    if not raw:
        raise ValueError("Dil alternatifi rota yolu boş olamaz")
    path = "/" + raw.strip("/")
    if raw.endswith("/") and path != "/":
        path += "/"
    if "//" in path:
        raise ValueError(f"Dil alternatifi rota yolu geçersiz: {raw!r}")
    return path


def validate_language_alternates(
    payload: dict[str, Any], manifest: dict[str, Any]
) -> list[dict[str, str]]:
    if int(payload.get("schemaVersion", 0)) != 1:
        raise ValueError("language-alternates.json schemaVersion=1 olmalıdır")

    route_paths = {str(route["canonicalPath"]) for route in manifest.get("routes", [])}
    pairs = payload.get("pairs")
    if not isinstance(pairs, list) or not pairs:
        raise ValueError("language-alternates.json en az bir dil çifti taşımalıdır")

    validated: list[dict[str, str]] = []
    seen_turkish: set[str] = set()
    seen_english: set[str] = set()

    for index, raw_pair in enumerate(pairs, start=1):
        if not isinstance(raw_pair, dict):
            raise ValueError(f"Dil çifti object olmalıdır: sıra={index}")

        turkish_path = normalize_route_path(raw_pair.get("turkishPath"))
        english_path = normalize_route_path(raw_pair.get("englishPath"))
        x_default_path = normalize_route_path(
            raw_pair.get("xDefaultPath", turkish_path)
        )

        if english_path == turkish_path:
            raise ValueError(f"Dil çifti aynı rotayı kullanamaz: {english_path}")
        if not english_path.startswith("/en/"):
            raise ValueError(f"İngilizce rota /en/ altında olmalıdır: {english_path}")
        if turkish_path.startswith("/en/"):
            raise ValueError(f"Türkçe rota /en/ altında olamaz: {turkish_path}")
        if x_default_path != turkish_path:
            raise ValueError(
                "x-default Türkçe ana rotayı göstermelidir: "
                f"{x_default_path} != {turkish_path}"
            )
        missing = sorted({turkish_path, english_path} - route_paths)
        if missing:
            raise ValueError(
                "Dil alternatifi routing manifestte bulunmuyor: " + ", ".join(missing)
            )
        if turkish_path in seen_turkish:
            raise ValueError(f"Yinelenen Türkçe dil rotası: {turkish_path}")
        if english_path in seen_english:
            raise ValueError(f"Yinelenen İngilizce dil rotası: {english_path}")

        seen_turkish.add(turkish_path)
        seen_english.add(english_path)
        validated.append(
            {
                "turkishPath": turkish_path,
                "englishPath": english_path,
                "xDefaultPath": x_default_path,
            }
        )

    expected_pair_count = int(payload.get("expectedPairCount", len(validated)))
    if len(validated) != expected_pair_count:
        raise ValueError(
            "Dil çifti sayısı yanlış: "
            f"bulunan={len(validated)}, beklenen={expected_pair_count}"
        )
    return validated


def load_language_alternates(
    manifest: dict[str, Any],
    path: Path = LANGUAGE_ALTERNATES_PATH,
) -> list[dict[str, str]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("language-alternates.json kök nesnesi object olmalıdır")
    return validate_language_alternates(payload, manifest)


def alternate_links_by_route(
    manifest: dict[str, Any],
    pairs: list[dict[str, str]],
) -> dict[str, tuple[tuple[str, str], ...]]:
    canonical_host = str(manifest.get("canonicalHost", "")).rstrip("/")
    if not canonical_host.startswith("https://"):
        raise ValueError(f"Canonical host HTTPS olmalıdır: {canonical_host!r}")

    result: dict[str, tuple[tuple[str, str], ...]] = {}
    for pair in pairs:
        turkish_url = canonical_host + pair["turkishPath"]
        english_url = canonical_host + pair["englishPath"]
        links = (
            ("tr-TR", turkish_url),
            ("en", english_url),
            ("x-default", canonical_host + pair["xDefaultPath"]),
        )
        result[pair["turkishPath"]] = links
        result[pair["englishPath"]] = links
    return result


def write_effective_sitemap(output: Path, manifest: dict[str, Any]) -> None:
    pairs = load_language_alternates(manifest)
    links_by_route = alternate_links_by_route(manifest, pairs)

    ET.register_namespace("", SITEMAP_NAMESPACE)
    ET.register_namespace("xhtml", XHTML_NAMESPACE)
    urlset = ET.Element(f"{{{SITEMAP_NAMESPACE}}}urlset")
    canonical_host = str(manifest["canonicalHost"]).rstrip("/")

    for route in manifest["routes"]:
        canonical_path = str(route["canonicalPath"])
        url = ET.SubElement(urlset, f"{{{SITEMAP_NAMESPACE}}}url")
        loc = ET.SubElement(url, f"{{{SITEMAP_NAMESPACE}}}loc")
        loc.text = canonical_host + canonical_path

        for hreflang, href in links_by_route.get(canonical_path, ()):
            ET.SubElement(
                url,
                f"{{{XHTML_NAMESPACE}}}link",
                {
                    "rel": "alternate",
                    "hreflang": hreflang,
                    "href": href,
                },
            )

    tree = ET.ElementTree(urlset)
    ET.indent(tree, space="  ")
    tree.write(output / "sitemap.xml", encoding="utf-8", xml_declaration=True)
