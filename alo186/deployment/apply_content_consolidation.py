from __future__ import annotations

import argparse
import hashlib
import json
import re
import xml.etree.ElementTree as ET
from html import escape
from pathlib import Path

CANONICAL_HOST = "https://alo186.com"
DEFAULT_CONFIG = Path(__file__).with_name("content-consolidations.json")
MARKER_START = "# BEGIN ALO186 CONTENT CONSOLIDATIONS"
MARKER_END = "# END ALO186 CONTENT CONSOLIDATIONS"


def normalize_path(value: str) -> str:
    raw = "/" + str(value or "").strip().strip("/")
    if raw == "/":
        raise ValueError("İçerik birleştirme rotası kök dizin olamaz")
    if "//" in raw or not re.fullmatch(r"/[a-z0-9\-/]+", raw):
        raise ValueError(f"Geçersiz içerik birleştirme rotası: {value!r}")
    return raw


def normalize_canonical_path(value: str) -> str:
    text = str(value or "").strip()
    trailing = text.endswith("/") and text.strip("/") != ""
    raw = normalize_path(text)
    if trailing and not raw.endswith("/"):
        raw += "/"
    return raw


def normalize_base_path(value: str) -> str:
    cleaned = str(value or "").strip()
    if not cleaned or cleaned == "/":
        return ""
    return "/" + cleaned.strip("/")


def canonical_route_path(value: str, base_path: str) -> str:
    text = str(value or "").strip()
    trailing = text.endswith("/") and text != "/"
    raw = "/" + text.strip("/")
    if base_path:
        if raw == base_path:
            return "/"
        if raw.startswith(base_path + "/"):
            raw = raw[len(base_path) :]
    if trailing and raw != "/" and not raw.endswith("/"):
        raw += "/"
    return raw


def public_url(base_path: str, route: str) -> str:
    route = normalize_canonical_path(route)
    return f"{base_path}{route}" if base_path else route


def route_file(site: Path, route: str) -> Path:
    return site / normalize_path(route).lstrip("/") / "index.html"


def load_config(path: Path = DEFAULT_CONFIG) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if int(payload.get("version", 0)) < 1:
        raise ValueError("İçerik birleştirme sürümü geçersiz")
    items = payload.get("consolidations")
    if not isinstance(items, list) or not items:
        raise ValueError("İçerik birleştirme listesi boş")

    aliases: set[str] = set()
    canonicals: set[str] = set()
    intent_keys: set[str] = set()
    normalized: list[dict] = []
    for index, raw in enumerate(items, start=1):
        alias = normalize_path(raw.get("aliasPath"))
        canonical = normalize_canonical_path(raw.get("canonicalPath"))
        intent_key = str(raw.get("intentKey") or "").strip()
        if alias == canonical:
            raise ValueError(f"Alias ve canonical aynı olamaz: {alias}")
        if alias in aliases:
            raise ValueError(f"Yinelenen alias rota: {alias}")
        if canonical in aliases:
            raise ValueError(f"Canonical başka bir alias olamaz: {canonical}")
        if intent_key in intent_keys or not re.fullmatch(r"[a-z0-9\-]+", intent_key):
            raise ValueError(f"Geçersiz/yinelenen intentKey: {intent_key!r}")
        aliases.add(alias)
        canonicals.add(canonical)
        intent_keys.add(intent_key)
        normalized.append(
            {
                "intentKey": intent_key,
                "aliasPath": alias,
                "canonicalPath": canonical,
                "label": str(raw.get("label") or f"Birleştirme {index}").strip(),
                "reason": str(raw.get("reason") or "Aynı arama niyeti tek canonical rotada birleştirildi.").strip(),
            }
        )

    if aliases & canonicals:
        overlap = ", ".join(sorted(aliases & canonicals))
        raise ValueError(f"Birleştirme zinciri desteklenmez; rota hem alias hem canonical: {overlap}")
    return {"version": int(payload["version"]), "generatedAt": payload.get("generatedAt"), "consolidations": normalized}


def redirect_html(item: dict, base_path: str, include_service_worker: bool) -> str:
    target_public = public_url(base_path, item["canonicalPath"])
    canonical_absolute = f"{CANONICAL_HOST}{item['canonicalPath']}"
    title = escape(item["label"])
    reason = escape(item["reason"])
    target_attr = escape(target_public, quote=True)
    canonical_attr = escape(canonical_absolute, quote=True)
    target_js = json.dumps(target_public, ensure_ascii=False)
    sw_url = f"{base_path}/sw.js" if base_path else "/sw.js"
    sw_scope = f"{base_path}/" if base_path else "/"
    sw_registration = (
        f'<script data-alo186-pages-sw>if(\'serviceWorker\'in navigator){{addEventListener(\'load\',()=>navigator.serviceWorker.register({json.dumps(sw_url)},{{scope:{json.dumps(sw_scope)}}}).catch(()=>{{}}));}}</script>'
        if include_service_worker
        else ""
    )
    return f"""<!doctype html>
<html lang="tr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <meta name="robots" content="noindex,follow">
  <meta name="referrer" content="strict-origin-when-cross-origin">
  <meta http-equiv="refresh" content="0;url={target_attr}">
  <link rel="canonical" href="{canonical_attr}">
  <title>{title} — güncel rehbere taşındı | ALO186</title>
  <style>body{{font:17px/1.6 system-ui,-apple-system,Segoe UI,sans-serif;max-width:48rem;margin:4rem auto;padding:0 1.2rem;color:#132238}}a{{display:inline-flex;min-height:44px;align-items:center;color:#164fc4;font-weight:800}}code{{overflow-wrap:anywhere}}</style>
</head>
<body data-alo186-content-alias="true">
  <main>
    <h1>Bu rehber güncel canonical içeriğe taşındı</h1>
    <p>{reason}</p>
    <p><a href="{target_attr}">Güncel rehberi açın →</a></p>
    <p><small>ALO186 bağımsız bilgi platformudur; EDAŞ veya kamu kurumu değildir.</small></p>
  </main>
  <script>location.replace({target_js}+location.search+location.hash);</script>
  {sw_registration}
</body>
</html>
"""


def update_sitemap(site: Path, items: list[dict]) -> dict:
    sitemap_path = site / "sitemap.xml"
    if not sitemap_path.is_file():
        raise FileNotFoundError(f"Sitemap bulunamadı: {sitemap_path}")

    tree = ET.parse(sitemap_path)
    root = tree.getroot()
    namespace = root.tag.split("}")[0].strip("{") if "}" in root.tag else ""
    ns = f"{{{namespace}}}" if namespace else ""
    alias_urls = {f"{CANONICAL_HOST}{item['aliasPath']}" for item in items}
    canonical_urls = {f"{CANONICAL_HOST}{item['canonicalPath']}" for item in items}
    removed: list[str] = []
    present: set[str] = set()

    for node in list(root):
        loc = node.find(f"{ns}loc")
        if loc is None or not loc.text:
            continue
        url = loc.text.strip()
        if url in alias_urls:
            root.remove(node)
            removed.append(url)
        else:
            present.add(url)

    missing = canonical_urls - present
    if missing:
        raise ValueError("Canonical birleşim hedefleri sitemapte eksik: " + ", ".join(sorted(missing)))

    ET.register_namespace("", namespace)
    ET.indent(tree, space="  ")
    tree.write(sitemap_path, encoding="utf-8", xml_declaration=True)
    return {"removed": sorted(removed), "canonicalTargets": sorted(canonical_urls)}


def update_release(site: Path, payload: dict, base_path: str) -> dict:
    release_path = site / "alo186-release.json"
    if not release_path.is_file():
        raise FileNotFoundError(f"Release envanteri bulunamadı: {release_path}")
    release = json.loads(release_path.read_text(encoding="utf-8"))
    aliases = {item["aliasPath"] for item in payload["consolidations"]}
    routes = [
        item
        for item in release.get("routes", [])
        if canonical_route_path(item.get("canonicalPath"), base_path) not in aliases
    ]
    release["routes"] = routes
    release["routeCount"] = len(routes)
    release["articleCount"] = sum(1 for item in routes if item.get("type") == "article")
    release["contentConsolidation"] = {
        "version": payload["version"],
        "generatedAt": payload.get("generatedAt"),
        "aliasCount": len(payload["consolidations"]),
        "aliases": payload["consolidations"],
        "sitemapPolicy": "aliases-excluded-canonical-targets-only",
        "basePathAwareReleaseFiltering": True,
    }
    release_path.write_text(json.dumps(release, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    pages_release_path = site / "pages-release.json"
    if pages_release_path.is_file():
        pages = json.loads(pages_release_path.read_text(encoding="utf-8"))
        pages["routeCount"] = len(routes)
        pages["contentConsolidation"] = {
            "version": payload["version"],
            "aliasCount": len(payload["consolidations"]),
            "aliasesExcludedFromSitemap": True,
            "aliasesExcludedFromProjectRelease": True,
        }
        pages_release_path.write_text(json.dumps(pages, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"routeCount": len(routes), "articleCount": release["articleCount"]}


def update_htaccess(site: Path, items: list[dict]) -> bool:
    path = site / ".htaccess"
    if not path.is_file():
        return False
    text = path.read_text(encoding="utf-8")
    block_pattern = re.compile(re.escape(MARKER_START) + r".*?" + re.escape(MARKER_END), re.S)
    rules = [MARKER_START, "<IfModule mod_rewrite.c>", "  RewriteEngine On"]
    for item in items:
        source = item["aliasPath"].lstrip("/")
        destination = f"{CANONICAL_HOST}{item['canonicalPath']}"
        rules.append(f"  RewriteRule ^{source}/?$ {destination} [R=301,L,NE]")
    rules.extend(["</IfModule>", MARKER_END])
    block = "\n".join(rules)
    if block_pattern.search(text):
        text = block_pattern.sub(block, text)
    else:
        text = text.rstrip() + "\n\n" + block + "\n"
    path.write_text(text, encoding="utf-8")
    return True


def recompute_checksums(site: Path) -> None:
    checksum_path = site / "checksums.sha256"
    if checksum_path.exists():
        checksum_path.unlink()
    lines: list[str] = []
    for path in sorted(item for item in site.rglob("*") if item.is_file()):
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        lines.append(f"{digest}  {path.relative_to(site).as_posix()}")
    checksum_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def apply(site: Path, base_path: str = "", config_path: Path = DEFAULT_CONFIG) -> dict:
    site = site.resolve()
    base_path = normalize_base_path(base_path)
    payload = load_config(config_path.resolve())
    include_service_worker = (site / "sw.js").is_file()

    for item in payload["consolidations"]:
        canonical_file = route_file(site, item["canonicalPath"])
        alias_file = route_file(site, item["aliasPath"])
        if not canonical_file.is_file():
            raise FileNotFoundError(f"Canonical birleşim hedefi artifactta eksik: {canonical_file}")
        alias_file.parent.mkdir(parents=True, exist_ok=True)
        alias_file.write_text(redirect_html(item, base_path, include_service_worker), encoding="utf-8")

    sitemap = update_sitemap(site, payload["consolidations"])
    release = update_release(site, payload, base_path)
    apache_redirects = update_htaccess(site, payload["consolidations"])
    recompute_checksums(site)
    return {
        "ok": True,
        "basePath": base_path,
        "version": payload["version"],
        "aliasCount": len(payload["consolidations"]),
        "apacheRedirects": apache_redirects,
        "sitemap": sitemap,
        "release": release,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Aynı arama niyetindeki ALO186 içeriklerini tek canonical rotada birleştirir.")
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--base-path", default="")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    args = parser.parse_args()
    print(json.dumps(apply(args.site, args.base_path, args.config), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
