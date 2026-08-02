from __future__ import annotations

import html
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

CANONICAL_HOST = "https://alo186.com"
CONFIG_PATH = Path(__file__).with_name("canonical-aliases.json")
SITEMAP_NAMESPACE = "http://www.sitemaps.org/schemas/sitemap/0.9"
XHTML_NAMESPACE = "http://www.w3.org/1999/xhtml"


def normalize_path(value: Any) -> str:
    raw = str(value or "").strip()
    if not raw:
        raise ValueError("Canonical alias yolu boş olamaz")
    path = "/" + raw.strip("/")
    if raw.endswith("/") and path != "/":
        path += "/"
    if "//" in path or not path.startswith("/"):
        raise ValueError(f"Canonical alias yolu geçersiz: {raw!r}")
    return path


def load_alias_map(path: Path = CONFIG_PATH) -> dict[str, str]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if int(payload.get("schemaVersion", 0)) != 1:
        raise ValueError("canonical-aliases.json schemaVersion=1 olmalıdır")
    if str(payload.get("canonicalHost", "")).rstrip("/") != CANONICAL_HOST:
        raise ValueError("canonical-aliases.json canonicalHost apex origin olmalıdır")

    clusters = payload.get("clusters")
    if not isinstance(clusters, list) or not clusters:
        raise ValueError("canonical-aliases.json en az bir küme taşımalıdır")

    alias_map: dict[str, str] = {}
    canonical_paths: set[str] = set()
    for index, cluster in enumerate(clusters, start=1):
        if not isinstance(cluster, dict):
            raise ValueError(f"Canonical küme object olmalıdır: sıra={index}")
        canonical = normalize_path(cluster.get("canonicalPath"))
        aliases = cluster.get("aliases")
        if not isinstance(aliases, list) or not aliases:
            raise ValueError(f"Canonical küme alias taşımıyor: {canonical}")
        if canonical in canonical_paths:
            raise ValueError(f"Yinelenen canonical küme: {canonical}")
        canonical_paths.add(canonical)
        for raw_alias in aliases:
            alias = normalize_path(raw_alias)
            if alias == canonical:
                raise ValueError(f"Alias canonical ile aynı olamaz: {alias}")
            if alias in alias_map:
                raise ValueError(f"Yinelenen canonical alias: {alias}")
            alias_map[alias] = canonical

    overlap = canonical_paths & set(alias_map)
    if overlap:
        raise ValueError("Bir canonical yol başka kümede alias olamaz: " + ", ".join(sorted(overlap)))
    return alias_map


def filtered_manifest(manifest: dict[str, Any], aliases: dict[str, str]) -> dict[str, Any]:
    filtered = dict(manifest)
    filtered["routes"] = [
        route for route in manifest.get("routes", [])
        if str(route.get("canonicalPath")) not in aliases
    ]
    return filtered


def render_alias_redirect(alias_path: str, canonical_path: str) -> str:
    alias_path = normalize_path(alias_path)
    canonical_path = normalize_path(canonical_path)
    canonical_url = CANONICAL_HOST + canonical_path
    canonical_html = html.escape(canonical_url, quote=True)
    canonical_json = json.dumps(canonical_url, ensure_ascii=False)
    return f'''<!doctype html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>İçerik güncel adrese taşındı | ALO186</title>
<meta name="description" content="Bu teknik rehber aynı arama niyetini karşılayan güncel ve kapsamlı ALO186 sayfasında birleştirildi.">
<meta name="robots" content="noindex,follow">
<meta http-equiv="refresh" content="0; url={canonical_html}">
<link rel="canonical" href="{canonical_html}">
<style>body{{margin:0;font:16px/1.6 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;background:#f5f7fb;color:#10213d}}main{{max-width:720px;margin:10vh auto;padding:28px;background:#fff;border:1px solid #dce3ed;border-radius:18px;box-shadow:0 12px 36px rgba(16,33,61,.08)}}a{{color:#0757b2;font-weight:700}}small{{display:block;margin-top:24px;color:#59677a}}</style>
<script>location.replace({canonical_json});</script>
</head>
<body>
<main>
<h1>Teknik rehber güncel adreste birleştirildi</h1>
<p>Aynı kullanıcı görevini tekrar eden içerikler tek, daha güncel kanıt zincirinde toplandı. Otomatik yönlendirme çalışmazsa <a href="{canonical_html}">güncel rehberi açın</a>.</p>
<small>ALO186 bağımsız bir bilgi platformudur; EDAŞ, TEDAŞ, EMO veya herhangi bir kamu kurumu değildir. Bu yönlendirme ürün satın alma önerisi içermez.</small>
</main>
</body>
</html>
'''


def write_sitemap_without_aliases(
    output: Path,
    manifest: dict[str, Any],
    aliases: dict[str, str],
    language_pairs: list[dict[str, str]],
) -> None:
    links_by_route: dict[str, tuple[tuple[str, str], ...]] = {}
    for pair in language_pairs:
        tr_path = normalize_path(pair["turkishPath"])
        en_path = normalize_path(pair["englishPath"])
        x_default = normalize_path(pair["xDefaultPath"])
        links = (
            ("tr-TR", CANONICAL_HOST + tr_path),
            ("en", CANONICAL_HOST + en_path),
            ("x-default", CANONICAL_HOST + x_default),
        )
        links_by_route[tr_path] = links
        links_by_route[en_path] = links

    ET.register_namespace("", SITEMAP_NAMESPACE)
    ET.register_namespace("xhtml", XHTML_NAMESPACE)
    urlset = ET.Element(f"{{{SITEMAP_NAMESPACE}}}urlset")
    for route in manifest.get("routes", []):
        canonical_path = str(route["canonicalPath"])
        if canonical_path in aliases:
            continue
        url = ET.SubElement(urlset, f"{{{SITEMAP_NAMESPACE}}}url")
        loc = ET.SubElement(url, f"{{{SITEMAP_NAMESPACE}}}loc")
        loc.text = CANONICAL_HOST + canonical_path
        for hreflang, href in links_by_route.get(canonical_path, ()):
            ET.SubElement(
                url,
                f"{{{XHTML_NAMESPACE}}}link",
                {"rel": "alternate", "hreflang": hreflang, "href": href},
            )

    tree = ET.ElementTree(urlset)
    ET.indent(tree, space="  ")
    tree.write(output / "sitemap.xml", encoding="utf-8", xml_declaration=True)


def validate_alias_artifacts(output: Path, aliases: dict[str, str]) -> None:
    failures: list[str] = []
    for alias, canonical in aliases.items():
        path = output / alias.strip("/") / "index.html"
        if not path.is_file():
            failures.append(f"Canonical alias artifact eksik: {alias}")
            continue
        text = path.read_text(encoding="utf-8")
        canonical_url = CANONICAL_HOST + canonical
        required = (
            '<meta name="robots" content="noindex,follow">',
            f'<link rel="canonical" href="{canonical_url}">',
            f'<meta http-equiv="refresh" content="0; url={canonical_url}">',
            "location.replace(",
            "bağımsız bir bilgi platformudur",
        )
        missing = [token for token in required if token not in text]
        if missing:
            failures.append(f"Canonical alias sözleşmesi eksik ({alias}): {missing}")
    if failures:
        raise RuntimeError("Canonical alias artifact doğrulaması başarısız:\n- " + "\n- ".join(failures))
