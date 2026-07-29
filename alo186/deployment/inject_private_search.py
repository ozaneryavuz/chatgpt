from __future__ import annotations

import argparse
import hashlib
import json
import re
from html import unescape
from pathlib import Path

CANONICAL_PATH = "/arama/"
SEARCH_DIR = Path("arama")
INDEX_FILE = SEARCH_DIR / "search-index.json"
PORTAL = Path("elektrik-portali/index.html")
GATEWAY = Path("index.html")
CARD_MARKER = 'data-alo186-search-card="true"'
INDEX_VERSION = 1
FEATURED_PATHS = {
    "/karar-motoru",
    "/edas-bul",
    "/hesaplama/",
    "/hesaplama/kesinti-gunlugu/",
    "/hesaplama/yedek-guc-cozum-secici/",
    "/hesaplama/gerilim-koruma-cozum-secici/",
    "/hesaplama/ev-sarj-uygunluk/",
    "/hesaplama/inverter-uygunluk/",
    "/hesaplama/elektrik-planim/",
    "/hesaplama/elektrik-kesintisi-kiti/",
    "/hesaplama/cozum-sonucu/",
    "/kurumsal-elektrik-surekliligi-on-degerlendirme",
}


def normalize_base_path(value: str) -> str:
    cleaned = str(value or "").strip()
    if not cleaned or cleaned == "/":
        return ""
    return "/" + cleaned.strip("/")


def public_url(base_path: str, route: str) -> str:
    route = "/" + route.lstrip("/")
    return f"{base_path}{route}" if base_path else route


def canonical_route_path(value: str, base_path: str) -> str:
    text = str(value or "").strip()
    trailing_slash = text.endswith("/") and text != "/"
    raw = "/" + text.strip("/")
    if raw == "/":
        return raw
    if base_path:
        if raw == base_path:
            return "/"
        if raw.startswith(base_path + "/"):
            raw = raw[len(base_path) :]
    if trailing_slash and raw != "/" and not raw.endswith("/"):
        raw += "/"
    return raw


def html_text(html: str, tag: str) -> str:
    match = re.search(fr"<{tag}\b[^>]*>(.*?)</{tag}>", html, re.I | re.S)
    if not match:
        return ""
    return clean_text(match.group(1))


def clean_text(value: str) -> str:
    no_tags = re.sub(r"<[^>]+>", " ", value)
    return re.sub(r"\s+", " ", unescape(no_tags)).strip()


def meta_description(html: str) -> str:
    patterns = [
        r'<meta\s+name=["\']description["\']\s+content=["\']([^"\']*)["\']',
        r'<meta\s+content=["\']([^"\']*)["\']\s+name=["\']description["\']',
    ]
    for pattern in patterns:
        match = re.search(pattern, html, re.I)
        if match:
            return clean_text(match.group(1))
    return ""


def first_excerpt(html: str) -> str:
    for pattern in [
        r'<p\b[^>]*class=["\'][^"\']*\blead\b[^"\']*["\'][^>]*>(.*?)</p>',
        r'<div\b[^>]*class=["\'][^"\']*\banswer\b[^"\']*["\'][^>]*>(.*?)</div>',
        r'<main\b[^>]*>(.*?)</main>',
    ]:
        match = re.search(pattern, html, re.I | re.S)
        if match:
            text = clean_text(match.group(1))
            if text:
                return text[:520]
    return ""


def collect_defined_terms(value, result: list[str]) -> None:
    if isinstance(value, dict):
        if value.get("@type") == "DefinedTerm" and value.get("name"):
            result.append(str(value["name"]).strip())
        for nested in value.values():
            collect_defined_terms(nested, result)
    elif isinstance(value, list):
        for nested in value:
            collect_defined_terms(nested, result)


def jsonld_topics(html: str) -> list[str]:
    topics: list[str] = []
    blocks = re.findall(r'<script\s+type=["\']application/ld\+json["\']>(.*?)</script>', html, re.I | re.S)
    for block in blocks:
        try:
            collect_defined_terms(json.loads(block), topics)
        except json.JSONDecodeError:
            continue
    unique: list[str] = []
    seen: set[str] = set()
    for topic in topics:
        key = topic.casefold()
        if not topic or key in seen:
            continue
        seen.add(key)
        unique.append(topic[:80])
    return unique[:12]


def bucket(route_type: str) -> str:
    if route_type == "article":
        return "article"
    if route_type == "calculator":
        return "calculator"
    if route_type in {"business-tool", "service", "partnership"}:
        return "business"
    if route_type == "collection":
        return "collection"
    return "tool"


def priority(route: dict) -> int:
    path = route.get("canonicalPath", "")
    if path == "/karar-motoru":
        return 120
    if path == "/edas-bul":
        return 115
    if path in FEATURED_PATHS:
        return 100
    return {"tool": 78, "calculator": 75, "business": 68, "collection": 65, "article": 50}.get(bucket(route.get("type", "")), 45)


def build_entry(site: Path, route: dict, base_path: str) -> dict | None:
    canonical_path = canonical_route_path(route.get("canonicalPath"), base_path)
    if not canonical_path or canonical_path == CANONICAL_PATH:
        return None
    target = site / canonical_path.strip("/") / "index.html"
    if not target.is_file():
        return None
    html = target.read_text(encoding="utf-8", errors="ignore")
    robots = re.search(r'<meta\s+name=["\']robots["\']\s+content=["\']([^"\']*)["\']', html, re.I)
    if robots and "noindex" in robots.group(1).casefold():
        return None
    title = html_text(html, "title").replace(" | ALO186", "").replace(" — ALO186", "").strip()
    h1 = html_text(html, "h1")
    if not title and not h1:
        return None
    description = meta_description(html) or first_excerpt(html)
    topics = jsonld_topics(html)
    normalized_route = {**route, "canonicalPath": canonical_path}
    return {
        "canonicalPath": canonical_path,
        "url": public_url(base_path, canonical_path),
        "type": route.get("type", "tool"),
        "bucket": bucket(route.get("type", "")),
        "title": title or h1,
        "h1": h1 or title,
        "description": description[:360],
        "excerpt": first_excerpt(html)[:520],
        "topics": topics,
        "priority": priority(normalized_route),
        "featured": canonical_path in FEATURED_PATHS,
    }


def generate_index(site: Path, base_path: str) -> dict:
    release_path = site / "alo186-release.json"
    release = json.loads(release_path.read_text(encoding="utf-8"))
    entries = []
    for route in release.get("routes", []):
        entry = build_entry(site, route, base_path)
        if entry:
            entries.append(entry)
    entries.sort(key=lambda item: (-int(item["priority"]), item["title"].casefold()))
    payload = {
        "version": INDEX_VERSION,
        "generatedAt": release.get("generatedAt") or release.get("commit") or "build",
        "entryCount": len(entries),
        "canonicalRouteCount": release.get("routeCount"),
        "privacy": "Arama sorgusu indekse, analitiğe veya yerel depolamaya yazılmaz; sıralama tarayıcıda yapılır.",
        "commercialRankingExcluded": ["price", "stock", "rating", "seller", "warranty", "affiliateCommission"],
        "entries": entries,
    }
    index_path = site / INDEX_FILE
    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    return payload


def insert_after_grid_open(text: str, card: str) -> tuple[str, bool]:
    if CARD_MARKER in text:
        return text, False
    for match in re.finditer(r'<section\b[^>]*>', text, re.I):
        classes = re.search(r'class=["\']([^"\']*)["\']', match.group(0), re.I)
        if classes and "grid" in classes.group(1).split():
            return text[: match.end()] + card + text[match.end() :], True
    return text, False


def search_card(base_path: str, gateway: bool) -> str:
    href = public_url(base_path, CANONICAL_PATH)
    if gateway:
        return f'<a class="card" {CARD_MARKER} href="{href}"><strong>Elektrik sorununu bütün ALO186 içinde arayın</strong><p>Rehber, hesaplayıcı ve karar araçlarını kişisel veri göndermeden tek ekranda bulun.</p><span>Teknik aramayı aç →</span></a>'
    return f'<a class="card" {CARD_MARKER} href="{href}"><span class="tag">Tarayıcı içi · acil niyet · teknik sıralama</span><h2>ALO186 Teknik Arama</h2><p>Rehberler, hesaplayıcılar ve karar araçları arasında arayın; ürün niyetinde önce uygunluk testine ilerleyin.</p><b>Teknik aramayı aç →</b></a>'


def inject_cards(site: Path, base_path: str) -> int:
    count = 0
    for relative, gateway in [(PORTAL, False), (GATEWAY, True)]:
        path = site / relative
        if not path.is_file():
            continue
        text, added = insert_after_grid_open(path.read_text(encoding="utf-8"), search_card(base_path, gateway))
        if added:
            path.write_text(text, encoding="utf-8")
            count += 1
    return count


def add_offline(site: Path, base_path: str) -> list[str]:
    path = site / "sw.js"
    if not path.is_file():
        return []
    text = path.read_text(encoding="utf-8")
    match = re.search(r"const CRITICAL=(\[.*?\]);", text, re.S)
    if not match:
        raise RuntimeError("Service worker CRITICAL rota dizisi bulunamadı")
    routes = json.loads(match.group(1))
    additions = [public_url(base_path, CANONICAL_PATH), public_url(base_path, "/arama/search-index.json")]
    added = []
    for url in additions:
        if url not in routes:
            routes.append(url)
            added.append(url)
    if added:
        path.write_text(text[: match.start(1)] + json.dumps(routes, ensure_ascii=False) + text[match.end(1) :], encoding="utf-8")
    return added


def update_manifest(site: Path, base_path: str) -> None:
    path = site / "manifest.webmanifest"
    if not path.is_file():
        return
    manifest = json.loads(path.read_text(encoding="utf-8"))
    shortcuts = manifest.setdefault("shortcuts", [])
    url = public_url(base_path, CANONICAL_PATH)
    if not any(isinstance(item, dict) and item.get("url") == url for item in shortcuts):
        shortcuts.append({"name": "ALO186 Teknik Arama", "short_name": "Teknik Arama", "url": url})
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def update_release(site: Path, base_path: str, payload: dict, cards: int, offline_added: list[str]) -> None:
    core_path = site / "alo186-release.json"
    core = json.loads(core_path.read_text(encoding="utf-8"))
    core["siteSearch"] = {
        "version": INDEX_VERSION,
        "route": CANONICAL_PATH,
        "entryCount": payload["entryCount"],
        "rawQueryStored": False,
        "commercialRankingUsed": False,
        "aliasesExcluded": True,
    }
    core_path.write_text(json.dumps(core, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    pages_path = site / "pages-release.json"
    if pages_path.is_file():
        pages = json.loads(pages_path.read_text(encoding="utf-8"))
        pages["siteSearch"] = {
            "version": INDEX_VERSION,
            "route": public_url(base_path, CANONICAL_PATH),
            "index": public_url(base_path, "/arama/search-index.json"),
            "entryCount": payload["entryCount"],
            "entryCardsInjected": cards,
            "offlineAssetsAdded": offline_added,
            "rawQueryStored": False,
        }
        pages["offlineCriticalRouteCount"] = int(pages.get("offlineCriticalRouteCount") or 0) + len(offline_added)
        pages_path.write_text(json.dumps(pages, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def recompute(site: Path) -> None:
    path = site / "checksums.sha256"
    if path.exists():
        path.unlink()
    lines = [
        f"{hashlib.sha256(item.read_bytes()).hexdigest()}  {item.relative_to(site).as_posix()}"
        for item in sorted(candidate for candidate in site.rglob("*") if candidate.is_file())
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(site: Path, base_path: str = "") -> dict:
    site = site.resolve()
    base_path = normalize_base_path(base_path)
    if not (site / SEARCH_DIR / "index.html").is_file():
        raise FileNotFoundError("Teknik arama rotası artifactta eksik")
    payload = generate_index(site, base_path)
    if payload["entryCount"] < 80:
        raise RuntimeError(f"Teknik arama indeksi beklenenden küçük: {payload['entryCount']}")
    cards = inject_cards(site, base_path)
    offline_added = add_offline(site, base_path)
    update_manifest(site, base_path)
    update_release(site, base_path, payload, cards, offline_added)
    recompute(site)
    return {
        "ok": True,
        "basePath": base_path,
        "route": public_url(base_path, CANONICAL_PATH),
        "entryCount": payload["entryCount"],
        "entryCardsInjected": cards,
        "offlineAssetsAdded": offline_added,
        "rawQueryStored": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="ALO186 canonical içeriklerinden kişisel verisiz tarayıcı içi teknik arama indeksi üretir.")
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--base-path", default="")
    args = parser.parse_args()
    print(json.dumps(run(args.site, args.base_path), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
