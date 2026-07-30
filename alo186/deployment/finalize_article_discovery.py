from __future__ import annotations

import html
import json
import re
import shutil
from pathlib import Path
from typing import Any


HUB_MARKER = "<!-- ALO186_ARTICLE_CARDS -->"
HUB_JSONLD_ID = "article-hub-jsonld"
ARTICLE_BACKLINK_MARKER = 'data-alo186-article-hub-link="true"'
ARTICLE_STYLE_MARKER = 'data-alo186-article-discovery-style="true"'
ARTICLE_STYLE_SOURCE = Path("alo186/assets/alo186-article-discovery.css")
PORTAL_CARD_MARKER = 'data-alo186-article-hub-card="true"'
CATEGORY_LABELS = {
    "outage-rights": "Kesinti ve haklar",
    "safety": "Elektrik güvenliği",
    "backup": "UPS ve yedek güç",
    "solar-ev": "GES ve EV",
    "power-quality": "Güç kalitesi",
    "maintenance": "Bakım ve işletme",
}


def public_url(base_path: str, route: str) -> str:
    prefix = "/" + str(base_path or "").strip("/") if str(base_path or "").strip("/") else ""
    path = "/" + str(route or "").lstrip("/")
    return (prefix + path).replace("//", "/")


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", value))).strip()


def first_match(source: str, patterns: tuple[str, ...]) -> str:
    for pattern in patterns:
        match = re.search(pattern, source, re.IGNORECASE | re.DOTALL)
        if match:
            return clean_text(match.group(1))
    return ""


def meta_description(source: str) -> str:
    return first_match(
        source,
        (
            r'<meta\s+name=["\']description["\']\s+content=["\']([^"\']+)["\']',
            r'<meta\s+content=["\']([^"\']+)["\']\s+name=["\']description["\']',
        ),
    )


def category_for(path: str, title: str, description: str) -> str:
    text = f"{path} {title} {description}".casefold()
    if any(term in text for term in ("tazmin", "cihaz-hasari", "sayaç", "sayac", "fatura", "edaş", "edas", "kesinti", "abonelik")):
        return "outage-rights"
    if any(term in text for term in ("kacak-akim", "kaçak akım", "toprak", "nötr", "notr", "yangın", "yangin", "parafudr", "spd", "elektrik çarp", "karbon-monoksit", "termal kamera")):
        return "safety"
    if any(term in text for term in ("ups", "jenerat", "inverter", "power-station", "güç istasyonu", "guc-istasyonu", "batarya", "akü", "aku", "yedek güç", "yedek-guc")):
        return "backup"
    if any(term in text for term in ("ges", "güneş", "gunes", "solar", "ev-sarj", "wallbox", "v2g", "v2h", "v2l", "vpp", "elektrikli araç", "elektrikli-arac")):
        return "solar-ev"
    if any(term in text for term in ("harmonik", "thd", "tdd", "faz denges", "faz-denges", "kompanzasyon", "reaktif", "rezonans", "k-faktor", "k-faktör", "trafo")):
        return "power-quality"
    return "maintenance"


def article_records(site: Path, canonical_release: dict[str, Any]) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    for route in canonical_release.get("routes", []):
        if route.get("type") != "article":
            continue
        canonical_path = str(route.get("canonicalPath") or "")
        target = site / canonical_path.strip("/") / "index.html"
        if not target.is_file():
            raise FileNotFoundError(f"Makale artifactı eksik: {canonical_path}")
        source = target.read_text(encoding="utf-8", errors="ignore")
        title = first_match(source, (r"<h1\b[^>]*>(.*?)</h1>", r"<title>(.*?)</title>"))
        description = meta_description(source) or first_match(
            source,
            (r'<p\b[^>]*class=["\'][^"\']*\blead\b[^"\']*["\'][^>]*>(.*?)</p>', r"<main\b[^>]*>(.*?)</main>"),
        )
        if not title:
            raise RuntimeError(f"Makale başlığı okunamadı: {canonical_path}")
        reading = first_match(source, (r"(\d+\s*dk(?:\s*okuma)?)", r"(\d+\s*dakika)")) or "Teknik rehber"
        category = category_for(canonical_path, title, description)
        records.append(
            {
                "path": canonical_path,
                "title": title,
                "description": description[:320],
                "reading": reading,
                "category": category,
                "categoryLabel": CATEGORY_LABELS[category],
            }
        )
    records.sort(key=lambda item: (item["categoryLabel"], item["title"].casefold()))
    return records


def install_discovery_asset(site: Path, base_path: str) -> str:
    repo_root = Path(__file__).resolve().parents[2]
    source = repo_root / ARTICLE_STYLE_SOURCE
    if not source.is_file():
        raise FileNotFoundError(f"Makale keşif stili eksik: {source}")
    assets = site / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, assets / source.name)
    return public_url(base_path, f"/assets/{source.name}")


def populate_hub(site: Path, base_path: str, records: list[dict[str, str]]) -> None:
    target = site / "haberler" / "index.html"
    if not target.is_file():
        raise FileNotFoundError("Teknik makale merkezi artifactta yok: /haberler/")
    source = target.read_text(encoding="utf-8")
    if HUB_MARKER not in source:
        raise RuntimeError("Teknik makale merkezi kart işareti bulunamadı.")
    cards = []
    for item in records:
        href = public_url(base_path, item["path"])
        search_text = clean_text(f"{item['title']} {item['description']} {item['categoryLabel']}")
        cards.append(
            '<article class="article-card" data-article-card '
            f'data-category="{html.escape(item["category"], quote=True)}" '
            f'data-search="{html.escape(search_text, quote=True)}">'
            '<div class="article-meta">'
            f'<span>{html.escape(item["categoryLabel"])}</span><span>{html.escape(item["reading"])}</span>'
            '</div>'
            f'<h3>{html.escape(item["title"])}</h3>'
            f'<p>{html.escape(item["description"])}</p>'
            f'<a href="{html.escape(href, quote=True)}">Makaleyi aç →</a>'
            '</article>'
        )
    source = source.replace(HUB_MARKER, "\n".join(cards), 1)
    source = re.sub(
        r'(<strong\s+data-article-count>).*?(</strong>)',
        rf'\g<1>{len(records)}\g<2>',
        source,
        count=1,
        flags=re.DOTALL,
    )
    item_list = [
        {
            "@type": "ListItem",
            "position": index,
            "name": item["title"],
            "url": f"https://alo186.com{item['path']}",
        }
        for index, item in enumerate(records, start=1)
    ]
    schema = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "CollectionPage",
                "name": "ALO186 Elektrik Teknik Makaleleri",
                "description": "Elektrik kesintisi, güvenlik, yedek güç, GES, EV, güç kalitesi ve bakım için kaynak doğrulamalı teknik makaleler.",
                "url": "https://alo186.com/haberler/",
                "inLanguage": "tr-TR",
                "mainEntity": {
                    "@type": "ItemList",
                    "numberOfItems": len(records),
                    "itemListElement": item_list,
                },
            },
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "ALO186", "item": "https://alo186.com/"},
                    {"@type": "ListItem", "position": 2, "name": "Teknik makaleler", "item": "https://alo186.com/haberler/"},
                ],
            },
        ],
    }
    schema_text = json.dumps(schema, ensure_ascii=False, separators=(",", ":"))
    pattern = rf'(<script\s+id=["\']{re.escape(HUB_JSONLD_ID)}["\'][^>]*>).*?(</script>)'
    source, replaced = re.subn(pattern, rf'\g<1>{schema_text}\g<2>', source, count=1, flags=re.IGNORECASE | re.DOTALL)
    if replaced != 1:
        raise RuntimeError("Teknik makale merkezi JSON-LD alanı bulunamadı.")
    target.write_text(source, encoding="utf-8")


def inject_article_backlinks(
    site: Path,
    base_path: str,
    records: list[dict[str, str]],
    style_url: str,
) -> int:
    hub_url = public_url(base_path, "/haberler/")
    search_url = public_url(base_path, "/arama/")
    injected = 0
    for item in records:
        target = site / item["path"].strip("/") / "index.html"
        source = target.read_text(encoding="utf-8")
        if ARTICLE_BACKLINK_MARKER in source:
            continue
        if "</head>" not in source:
            raise RuntimeError(f"Makale head alanı bulunamadı: {item['path']}")
        style = f'<link rel="stylesheet" href="{html.escape(style_url, quote=True)}" {ARTICLE_STYLE_MARKER}>'
        source = source.replace("</head>", style + "\n</head>", 1)
        navigation = (
            f'<nav class="article-hub-backlink" {ARTICLE_BACKLINK_MARKER} aria-label="Makale gezinme">'
            f'<a href="{html.escape(hub_url, quote=True)}">← Tüm teknik makaleler</a>'
            f'<a href="{html.escape(search_url, quote=True)}">Teknik aramada bul</a>'
            '</nav>'
        )
        match = re.search(r"<main\b[^>]*>", source, re.IGNORECASE)
        if not match:
            raise RuntimeError(f"Makale main alanı bulunamadı: {item['path']}")
        target.write_text(source[: match.end()] + navigation + source[match.end() :], encoding="utf-8")
        injected += 1
    return injected


def inject_portal_card(site: Path, base_path: str) -> bool:
    target = site / "elektrik-portali" / "index.html"
    if not target.is_file():
        return False
    source = target.read_text(encoding="utf-8")
    if PORTAL_CARD_MARKER in source:
        return False
    match = re.search(
        r'(<section\s+class=["\']grid["\'][^>]*aria-label=["\']ALO186 araçları ve teknik rehberleri["\'][^>]*>)',
        source,
        re.IGNORECASE,
    )
    if not match:
        raise RuntimeError("Portal ücretsiz kaynak kütüphanesi bulunamadı.")
    hub_url = public_url(base_path, "/haberler/")
    card = (
        f'<a class="card" {PORTAL_CARD_MARKER} href="{html.escape(hub_url, quote=True)}">'
        '<span class="tag">Bütün teknik makaleler · tarayıcı içi filtre</span>'
        '<h2>Elektrik Teknik Makaleleri</h2>'
        '<p>Kesinti, haklar, güvenlik, UPS, jeneratör, GES, EV, harmonik, topraklama ve bakım içeriklerini tek merkezde konuya göre bulun.</p>'
        '<b>Makale merkezini aç →</b></a>'
    )
    target.write_text(source[: match.end()] + card + source[match.end() :], encoding="utf-8")
    return True


def update_manifest(site: Path, base_path: str) -> bool:
    target = site / "manifest.webmanifest"
    if not target.is_file():
        return False
    manifest = json.loads(target.read_text(encoding="utf-8"))
    shortcuts = manifest.setdefault("shortcuts", [])
    url = public_url(base_path, "/haberler/")
    if any(isinstance(item, dict) and item.get("url") == url for item in shortcuts):
        return False
    shortcuts.append({"name": "Teknik Makaleler", "short_name": "Makaleler", "url": url})
    target.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return True


def run(site: Path, base_path: str, canonical_release: dict[str, Any]) -> dict[str, Any]:
    records = article_records(site, canonical_release)
    if len(records) < 50:
        raise RuntimeError(f"Teknik makale merkezi beklenenden küçük: {len(records)}")
    style_url = install_discovery_asset(site, base_path)
    populate_hub(site, base_path, records)
    backlinks = inject_article_backlinks(site, base_path, records, style_url)
    portal_card = inject_portal_card(site, base_path)
    manifest_shortcut = update_manifest(site, base_path)
    counts = {key: sum(1 for item in records if item["category"] == key) for key in CATEGORY_LABELS}
    if sum(counts.values()) != len(records) or any(value == 0 for value in counts.values()):
        raise RuntimeError(f"Makale kategori kapsamı eksik: {counts}")
    return {
        "route": public_url(base_path, "/haberler/"),
        "style": style_url,
        "articleCount": len(records),
        "categoryCounts": counts,
        "articleBacklinksInjected": backlinks,
        "portalCardInjected": portal_card,
        "manifestShortcutAdded": manifest_shortcut,
        "rawQueryStored": False,
        "commercialRankingUsed": False,
    }
