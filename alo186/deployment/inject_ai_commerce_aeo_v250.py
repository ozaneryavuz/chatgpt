from __future__ import annotations

import argparse
import hashlib
import json
import re
import unicodedata
from datetime import datetime, timezone
from html import unescape
from pathlib import Path
from urllib.parse import urlsplit

VERSION = 250
CANONICAL_ORIGIN = "https://alo186.com"
PRODUCT_HUB_ROUTE = "/amazon-elektrik-urunleri/"
MATCHER_ROUTE = "/akilli-urun-secimi/"
SURGE_PRODUCTS_ROUTE = "/amazon-elektrik-urunleri/akim-korumali-priz-yuk-uygunluk-secimi/"
SURGE_GUIDE_ROUTE = "/amazon-elektrik-urunleri/akim-korumali-grup-priz-secimi/"
POWER_STATION_ROUTE = "/amazon-elektrik-urunleri/tasinabilir-guc-istasyonu-secimi/"
COMPARISON_ROUTE = "/haberler/ups-mi-tasinabilir-guc-istasyonu-mu/"
MARKER = 'data-alo186-ai-commerce-aeo-v250="true"'
REPORT_NAME = "ai-commerce-aeo-v250.json"
AFFILIATE_HOSTS = {"amazon.com.tr", "www.amazon.com.tr", "amzn.to"}
REQUIRED_REL = {"sponsored", "nofollow", "noopener"}

SSR_CHOICES = (
    {
        "id": "ups-kesintisiz-gecis",
        "title": "UPS: kesintisiz geçiş ve kontrollü kapanma",
        "description": "Bilgisayar, NAS, modem ve benzeri hassas yüklerde W/VA, geçiş davranışı, akü süresi ve haberleşme gereğini doğrulayın.",
        "route": "/haberler/ups-online-line-interactive-offline-farki",
        "tool": "/hesaplama/ups-suresi/",
    },
    {
        "id": "power-station-uzun-sure",
        "title": "Taşınabilir güç istasyonu: uzun süreli ve mobil enerji",
        "description": "Wh, sürekli W, kalkış tepe gücü, saf sinüs ve EPS sınırını yük listesiyle karşılaştırın.",
        "route": POWER_STATION_ROUTE,
        "tool": "/hesaplama/power-station-kapasite-eps-uygunluk/",
    },
    {
        "id": "mini-ups-internet",
        "title": "Mini UPS: modem ve ONT sürekliliği",
        "description": "Gerilim, polarite, konnektör, toplam W ve hedef süreyi operatör arızasından ayırın.",
        "route": "/amazon-elektrik-urunleri/modem-ont-mini-ups-yedekleme-secici/",
        "tool": "/hesaplama/modem-internet-yedekleme/",
    },
    {
        "id": "korumali-priz-son-katman",
        "title": "Akım korumalı priz: son katman darbe koruması",
        "description": "Toplam yük, anma akımı, joule, gösterge ve topraklı priz koşulunu pano tipi SPD'den ayrı değerlendirin.",
        "route": SURGE_PRODUCTS_ROUTE,
        "tool": "/hesaplama/akim-korumali-grup-priz-uygunluk/",
    },
    {
        "id": "acil-aydinlatma",
        "title": "Acil aydınlatma: süre, bakım ve yerleşim",
        "description": "Tüketici tipi hazırlık ürününü bina yaşam güvenliği sistemiyle karıştırmadan süre ve bakım ihtiyacını doğrulayın.",
        "route": "/amazon-elektrik-urunleri/acil-aydinlatma-duman-alarmi/",
        "tool": "/hesaplama/acil-aydinlatma-sure-uygunluk/",
    },
)

FAQ_LINK_RULES = (
    (
        re.compile(r"güç istasyonu ups yerine", re.I),
        "İlgili yedek güç çözümünü karşılaştırın",
        "/hesaplama/yedek-guc-cozum-secici/",
    ),
    (
        re.compile(r"1500 va ups kaç saat", re.I),
        "UPS çalışma süresini hesaplayın",
        "/hesaplama/ups-suresi/",
    ),
    (
        re.compile(r"power station buzdolabı", re.I),
        "İlgili güç istasyonu uygunluğunu inceleyin",
        "/hesaplama/power-station-kapasite-eps-uygunluk/",
    ),
    (
        re.compile(r"koruma ışığı söndüyse", re.I),
        "İlgili koruma ekipmanını inceleyin",
        SURGE_PRODUCTS_ROUTE,
    ),
    (
        re.compile(r"akım korumalı priz yıldırıma", re.I),
        "İlgili koruma ekipmanını inceleyin",
        SURGE_PRODUCTS_ROUTE,
    ),
    (
        re.compile(r"voltaj dalgalanmasında|gerilim dalgalanmasında", re.I),
        "İlgili koruma ekipmanını inceleyin",
        "/hesaplama/gerilim-koruma-cozum-secici/",
    ),
    (
        re.compile(r"bazı prizler çalışmıyorsa|bazı prizler çalışmıyor", re.I),
        "İlgili koruma ekipmanını inceleyin",
        "/elektrik-durum-merkezi/",
    ),
)


def normalize_base_path(value: str) -> str:
    value = (value or "").strip()
    if not value or value == "/":
        return ""
    return "/" + value.strip("/")


def public_path(base_path: str, route: str) -> str:
    base = normalize_base_path(base_path)
    path = "/" + route.lstrip("/")
    return f"{base}{path}" if base else path


def route_file(site: Path, route: str) -> Path:
    route = route.split("?", 1)[0].split("#", 1)[0]
    path = route.strip("/")
    return site / path / "index.html" if path else site / "index.html"


def slugify(value: str) -> str:
    value = unescape(re.sub(r"<[^>]+>", " ", value))
    value = unicodedata.normalize("NFKD", value)
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = value.casefold().replace("ı", "i")
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    return value[:80] or "bolum"


def add_or_merge_rel(attrs: str) -> str:
    rel_match = re.search(r"\brel\s*=\s*([\"'])(.*?)\1", attrs, re.I | re.S)
    if rel_match:
        current = {item.casefold() for item in rel_match.group(2).split() if item}
        merged = " ".join(sorted(current | REQUIRED_REL))
        return attrs[: rel_match.start()] + f'rel="{merged}"' + attrs[rel_match.end() :]
    return attrs.rstrip() + ' rel="sponsored nofollow noopener"'


def ensure_affiliate_rel(html: str) -> tuple[str, int]:
    changes = 0

    def repl(match: re.Match[str]) -> str:
        nonlocal changes
        attrs = match.group("attrs")
        href_match = re.search(r"\bhref\s*=\s*([\"'])(.*?)\1", attrs, re.I | re.S)
        href = unescape(href_match.group(2)) if href_match else ""
        host = urlsplit(href).hostname or ""
        is_affiliate = host.casefold() in AFFILIATE_HOSTS or bool(
            re.search(r"\bdata-affiliate-(?:asin|product|url)\b", attrs, re.I)
        )
        if not is_affiliate:
            return match.group(0)
        updated = add_or_merge_rel(attrs)
        if updated != attrs:
            changes += 1
        return "<a" + updated + ">"

    updated = re.sub(r"<a(?P<attrs>\s+[^>]*?)>", repl, html, flags=re.I | re.S)
    return updated, changes


def unique_id(candidate: str, used: set[str]) -> str:
    base = candidate
    index = 2
    while candidate in used:
        candidate = f"{base}-{index}"
        index += 1
    used.add(candidate)
    return candidate


def existing_ids(html: str) -> set[str]:
    return set(re.findall(r"\bid\s*=\s*[\"']([^\"']+)[\"']", html, re.I))


def assign_deep_ids(html: str) -> tuple[str, int]:
    used = existing_ids(html)
    changes = 0

    def section_repl(match: re.Match[str]) -> str:
        nonlocal changes
        attrs = match.group("attrs")
        body = match.group("body")
        if re.search(r"\bid\s*=", attrs, re.I):
            return match.group(0)
        heading = re.search(r"<h[1-3]\b[^>]*>(.*?)</h[1-3]>", body, re.I | re.S)
        if not heading:
            return match.group(0)
        section_id = unique_id("rehber-" + slugify(heading.group(1)), used)
        changes += 1
        return f'<section{attrs} id="{section_id}">{body}</section>'

    html = re.sub(
        r"<section(?P<attrs>\s[^>]*)>(?P<body>.*?)</section>",
        section_repl,
        html,
        flags=re.I | re.S,
    )

    def article_repl(match: re.Match[str]) -> str:
        nonlocal changes
        attrs = match.group("attrs")
        body = match.group("body")
        if re.search(r"\bid\s*=", attrs, re.I):
            return match.group(0)
        if not re.search(r"\bclass\s*=\s*[\"'][^\"']*(?:card|product)[^\"']*[\"']", attrs, re.I):
            return match.group(0)
        asin = re.search(r"\bASIN\s+([A-Z0-9]{10})\b", body, re.I)
        heading = re.search(r"<h[2-4]\b[^>]*>(.*?)</h[2-4]>", body, re.I | re.S)
        if heading:
            raw = slugify(heading.group(1))
        elif asin:
            raw = asin.group(1).casefold()
        else:
            return match.group(0)
        article_id = unique_id("urun-" + raw, used)
        changes += 1
        return f'<article{attrs} id="{article_id}">{body}</article>'

    html = re.sub(
        r"<article(?P<attrs>\s[^>]*)>(?P<body>.*?)</article>",
        article_repl,
        html,
        flags=re.I | re.S,
    )
    return html, changes


def jsonld_blocks(html: str) -> list[dict]:
    values: list[dict] = []
    for raw in re.findall(
        r'<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        html,
        re.I | re.S,
    ):
        parsed = json.loads(raw)
        if isinstance(parsed, dict):
            values.append(parsed)
    return values


def offer_config() -> dict:
    path = Path(__file__).with_name("ai-commerce-verified-offers-v250.json")
    data = json.loads(path.read_text(encoding="utf-8"))
    if int(data.get("version") or 0) != VERSION:
        raise RuntimeError("Offer config sürümü v250 değil")
    if not isinstance(data.get("offers"), list):
        raise RuntimeError("Offer config offers listesi değil")
    return data


def validated_offer_map(config: dict, html: str) -> dict[str, dict]:
    required = {
        "productId",
        "url",
        "price",
        "priceCurrency",
        "availability",
        "sellerName",
        "verifiedAt",
        "validThrough",
    }
    result: dict[str, dict] = {}
    now = datetime.now(timezone.utc)
    max_age_hours = int(config.get("maxAgeHours") or 24)
    for record in config["offers"]:
        if not isinstance(record, dict) or not required.issubset(record):
            raise RuntimeError("Eksik alanlı Offer kaydı fail-closed reddedildi")
        if record["productId"] in result:
            raise RuntimeError("Yinelenen Offer productId")
        parsed = urlsplit(str(record["url"]))
        if parsed.scheme != "https" or parsed.hostname not in AFFILIATE_HOSTS:
            raise RuntimeError("Offer URL Amazon Türkiye kaydı değil")
        verified = datetime.fromisoformat(str(record["verifiedAt"]).replace("Z", "+00:00"))
        age_hours = (now - verified).total_seconds() / 3600
        if age_hours < 0 or age_hours > max_age_hours:
            raise RuntimeError("Offer doğrulaması güncel değil")
        visible_price = f'{record["price"]} {record["priceCurrency"]}'
        if visible_price not in html or str(record["availability"]) not in html:
            raise RuntimeError("Offer verisi görünür HTML ile eşleşmiyor")
        result[str(record["productId"])] = record
    return result


def product_anchor_id(html: str, product: dict) -> str:
    identifiers: list[str] = []
    for item in product.get("identifier") or []:
        if isinstance(item, dict) and item.get("value"):
            identifiers.append(str(item["value"]))
    for value in identifiers:
        pattern = re.compile(
            r'<article\b(?=[^>]*\bid=["\']([^"\']+)["\'])[^>]*>.*?'
            + re.escape(value)
            + r'.*?</article>',
            re.I | re.S,
        )
        match = pattern.search(html)
        if match:
            return match.group(1)
    name = str(product.get("name") or "")
    if name:
        for match in re.finditer(
            r'<article\b(?=[^>]*\bid=["\']([^"\']+)["\'])[^>]*>(.*?)</article>',
            html,
            re.I | re.S,
        ):
            visible = unescape(re.sub(r"<[^>]+>", " ", match.group(2)))
            if name.casefold() in visible.casefold():
                return match.group(1)
    product_id = str(product.get("@id") or "")
    fragment = product_id.rsplit("#", 1)[-1] if "#" in product_id else slugify(name or "product")
    return "urun-" + slugify(fragment)


def augment_product_knowledge_graph(html: str, canonical: str) -> tuple[str, dict]:
    match = re.search(
        r'(<script\b(?=[^>]*\bid=["\']knowledge-graph["\'])(?=[^>]*type=["\']application/ld\+json["\'])[^>]*>)(.*?)(</script>)',
        html,
        re.I | re.S,
    )
    if not match:
        return html, {"products": 0, "recommendations": 0, "offers": 0}
    payload = json.loads(match.group(2))
    graph = payload.get("@graph")
    if not isinstance(graph, list):
        raise RuntimeError("knowledge-graph @graph listesi bulunamadı")
    products = [item for item in graph if isinstance(item, dict) and item.get("@type") == "Product"]
    existing_ids = {str(item.get("@id")) for item in graph if isinstance(item, dict) and item.get("@id")}
    offers = validated_offer_map(offer_config(), html)
    recommendation_count = 0
    offer_count = 0
    for product in products:
        product_id = str(product.get("@id") or "")
        fragment = product_id.rsplit("#", 1)[-1] if "#" in product_id else slugify(str(product.get("name") or "product"))
        anchor_id = product_anchor_id(html, product)
        product["url"] = canonical + "#" + anchor_id
        recommendation_id = canonical + "#onerilen-" + slugify(fragment)
        if recommendation_id not in existing_ids:
            recommendation = {
                "@type": "Recommendation",
                "@id": recommendation_id,
                "name": f'{product.get("name", "Ürün")} için koşullu teknik öneri',
                "author": {"@type": "Organization", "name": "ALO186", "url": CANONICAL_ORIGIN + "/"},
                "itemReviewed": {"@id": product_id},
                "reviewBody": "Yalnız görünür güvenlik, uyumluluk ve gerçek ihtiyaç kontrolleri tamamlandığında değerlendirilebilir. Mevcut güvenli çözüm ihtiyacı karşılıyorsa yeni ürün satın alınmamalıdır.",
                "url": canonical + "#" + anchor_id,
            }
            graph.append(recommendation)
            existing_ids.add(recommendation_id)
            recommendation_count += 1
        offer = offers.get(fragment) or offers.get(anchor_id)
        if offer:
            product["offers"] = {
                "@type": "Offer",
                "url": offer["url"],
                "price": str(offer["price"]),
                "priceCurrency": offer["priceCurrency"],
                "availability": offer["availability"],
                "seller": {"@type": "Organization", "name": offer["sellerName"]},
                "priceValidUntil": offer["validThrough"],
            }
            offer_count += 1
    rendered = json.dumps(payload, ensure_ascii=False, indent=2)
    updated = html[: match.start()] + match.group(1) + "\n" + rendered + "\n" + match.group(3) + html[match.end() :]
    total_recommendations = sum(
        1 for item in graph if isinstance(item, dict) and item.get("@type") == "Recommendation"
    )
    total_offers = sum(
        1 for item in products if isinstance(item.get("offers"), dict) and item["offers"].get("@type") == "Offer"
    )
    return updated, {
        "products": len(products),
        "recommendations": total_recommendations,
        "offers": total_offers,
        "recommendationsAdded": recommendation_count,
        "offersAdded": offer_count,
    }


def inject_jsonld_script(html: str, script_id: str, payload: dict) -> tuple[str, bool]:
    if f'id="{script_id}"' in html:
        return html, False
    script = (
        f'\n<script id="{script_id}" type="application/ld+json" {MARKER}>'
        + json.dumps(payload, ensure_ascii=False, indent=2)
        + "</script>\n"
    )
    if "</head>" not in html:
        raise RuntimeError("JSON-LD enjeksiyonu için </head> yok")
    return html.replace("</head>", script + "</head>", 1), True


def comparison_payload(canonical: str) -> dict:
    return {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "ItemList",
                "@id": canonical + "#karsilastirma-listesi",
                "name": "UPS ve taşınabilir güç istasyonu karşılaştırması",
                "numberOfItems": 2,
                "itemListElement": [
                    {
                        "@type": "ListItem",
                        "position": 1,
                        "name": "UPS",
                        "url": canonical + "#karsilastirma-ups-power-station",
                        "description": "Kesintisiz geçiş, W/VA kapasitesi ve kontrollü kapanma gerektiren sabit yükler için değerlendirilir.",
                    },
                    {
                        "@type": "ListItem",
                        "position": 2,
                        "name": "Taşınabilir güç istasyonu",
                        "url": canonical + "#karsilastirma-ups-power-station",
                        "description": "Wh kapasitesi, sürekli/tepe güç ve taşınabilir enerji ihtiyacı için değerlendirilir; EPS davranışı model bazında doğrulanır.",
                    },
                ],
            },
            {
                "@type": "Table",
                "@id": canonical + "#karsilastirma-tablosu",
                "name": "UPS ile taşınabilir güç istasyonu teknik karşılaştırma tablosu",
                "url": canonical + "#karsilastirma-ups-power-station",
                "about": [
                    {"@type": "DefinedTerm", "name": "UPS"},
                    {"@type": "DefinedTerm", "name": "Taşınabilir güç istasyonu"},
                    {"@type": "DefinedTerm", "name": "Geçiş süresi"},
                    {"@type": "DefinedTerm", "name": "Kullanılabilir Wh"},
                ],
            },
        ],
    }


def ensure_comparison_anchors(html: str) -> tuple[str, int]:
    changes = 0
    if 'id="karsilastirma-ups-power-station"' not in html:
        html, count = re.subn(r"<table\b(?![^>]*\bid=)", '<table id="karsilastirma-ups-power-station"', html, count=1, flags=re.I)
        changes += count
    return html, changes


def append_faq_solution_links(html: str, base_path: str) -> tuple[str, int]:
    changes = 0

    def details_repl(match: re.Match[str]) -> str:
        nonlocal changes
        whole = match.group(0)
        question = unescape(re.sub(r"<[^>]+>", " ", match.group("question"))).strip()
        for pattern, label, route in FAQ_LINK_RULES:
            if not pattern.search(question):
                continue
            href = public_path(base_path, route)
            marker = f'data-related-solution="{slugify(question)}"'
            if marker in whole:
                return whole
            link = f' <a class="related-solution" {marker} href="{href}">{label}</a>'
            updated, count = re.subn(r"</p>", link + "</p>", whole, count=1, flags=re.I)
            if count:
                changes += 1
                return updated
        return whole

    updated = re.sub(
        r"<details\b[^>]*>\s*<summary\b[^>]*>(?P<question>.*?)</summary>.*?</details>",
        details_repl,
        html,
        flags=re.I | re.S,
    )
    return updated, changes


def ssr_baseline(base_path: str) -> str:
    cards = []
    for index, item in enumerate(SSR_CHOICES, start=1):
        cards.append(
            f'<article id="urun-sinifi-{item["id"]}" class="ssr-choice-card">'
            f'<span>{index:02d}</span><h3>{item["title"]}</h3><p>{item["description"]}</p>'
            f'<p><a href="{public_path(base_path, item["tool"])}">Ücretsiz teknik kontrol</a> · '
            f'<a href="{public_path(base_path, item["route"])}">İlgili ürün rehberi</a></p></article>'
        )
    return (
        f'\n<section id="ssr-urun-secim-baslangici" class="content-section" {MARKER} data-alo186-ssr-products-v250="true">'
        '<div class="panel"><span class="eyebrow">JavaScript gerekmeden başlangıç seçenekleri</span>'
        '<h2>Temel ürün sınıfları ve ücretsiz doğrulama yolları</h2>'
        '<p>Dinamik filtreler çalışmasa bile botlar ve kullanıcılar aşağıdaki teknik ürün tiplerini, satın almama sınırlarını ve ilgili ücretsiz araçları görebilir.</p>'
        '<div class="ssr-choice-grid">' + "".join(cards) + "</div>"
        '<p><strong>Satın almama sonucu:</strong> Mevcut güvenli çözüm ihtiyacı karşılıyorsa yeni ürün önerilmez. Aktif tehlike, sabit tesisat veya profesyonel ölçüm gereğinde mağaza yolu kapalıdır.</p>'
        '</div></section>\n'
    )


def inject_ssr_baseline(html: str, base_path: str) -> tuple[str, bool]:
    if 'data-alo186-ssr-products-v250="true"' in html:
        return html, False
    if "</main>" not in html:
        raise RuntimeError("SSR baseline için </main> yok")
    style = (
        '<style id="alo186-ssr-products-v250">'
        '.ssr-choice-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px}'
        '.ssr-choice-card{border:1px solid #d8e1ef;border-radius:14px;padding:16px;background:#fff}'
        '.ssr-choice-card h3{margin:.35rem 0}.ssr-choice-card a{min-height:44px;display:inline-flex;align-items:center}'
        '</style>'
    )
    if "</head>" in html and 'id="alo186-ssr-products-v250"' not in html:
        html = html.replace("</head>", style + "</head>", 1)
    return html.replace("</main>", ssr_baseline(base_path) + "</main>", 1), True


def selector_payload(canonical: str) -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "@id": canonical + "#ssr-urun-siniflari",
        "name": "Elektrik kesintisi ve koruma için temel ürün sınıfları",
        "numberOfItems": len(SSR_CHOICES),
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": index,
                "name": item["title"],
                "url": canonical + "#urun-sinifi-" + item["id"],
                "description": item["description"],
            }
            for index, item in enumerate(SSR_CHOICES, start=1)
        ],
    }


def process_page(path: Path, base_path: str, *, deep_ids: bool = True, faq_links: bool = True) -> dict:
    if not path.is_file():
        return {"present": False, "changed": False, "affiliateRel": 0, "deepIds": 0, "faqLinks": 0}
    html = path.read_text(encoding="utf-8", errors="strict")
    original = html
    html, rel_count = ensure_affiliate_rel(html)
    deep_count = 0
    faq_count = 0
    if deep_ids:
        html, deep_count = assign_deep_ids(html)
    if faq_links:
        html, faq_count = append_faq_solution_links(html, base_path)
    if html != original:
        path.write_text(html, encoding="utf-8")
    return {
        "present": True,
        "changed": html != original,
        "affiliateRel": rel_count,
        "deepIds": deep_count,
        "faqLinks": faq_count,
    }


def validate_rel_across_site(site: Path) -> tuple[int, list[str]]:
    checked = 0
    errors: list[str] = []
    for path in site.rglob("*.html"):
        html = path.read_text(encoding="utf-8", errors="ignore")
        for match in re.finditer(r"<a(?P<attrs>\s+[^>]*?)>", html, re.I | re.S):
            attrs = match.group("attrs")
            href_match = re.search(r"\bhref\s*=\s*([\"'])(.*?)\1", attrs, re.I | re.S)
            href = unescape(href_match.group(2)) if href_match else ""
            host = (urlsplit(href).hostname or "").casefold()
            is_affiliate = host in AFFILIATE_HOSTS or bool(re.search(r"\bdata-affiliate-(?:asin|product|url)\b", attrs, re.I))
            if not is_affiliate:
                continue
            checked += 1
            rel_match = re.search(r"\brel\s*=\s*([\"'])(.*?)\1", attrs, re.I | re.S)
            rel = {item.casefold() for item in rel_match.group(2).split()} if rel_match else set()
            missing = REQUIRED_REL - rel
            if missing:
                errors.append(f"{path.relative_to(site)}: eksik rel {sorted(missing)}")
    return checked, errors


def update_release(site: Path, base_path: str, report: dict) -> None:
    path = site / "pages-release.json"
    if not path.is_file():
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    data["aiCommerceAeo"] = {
        "version": VERSION,
        "basePath": normalize_base_path(base_path),
        "report": REPORT_NAME,
        "productCount": report["structuredData"]["products"],
        "recommendationCount": report["structuredData"]["recommendations"],
        "offerCount": report["structuredData"]["offers"],
        "comparisonItemCount": report["structuredData"]["comparisonItems"],
        "deepLinkCount": report["deepLinks"],
        "affiliateRelChecked": report["affiliateRelChecked"],
        "ssrBaseline": report["ssrBaseline"],
        "llmsTxt": True,
        "aiCrawlerPolicy": True,
        "offerFailClosed": True,
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def recompute_checksums(site: Path) -> None:
    path = site / "checksums.sha256"
    if path.exists():
        path.unlink()
    lines = []
    for item in sorted(candidate for candidate in site.rglob("*") if candidate.is_file()):
        lines.append(f"{hashlib.sha256(item.read_bytes()).hexdigest()}  {item.relative_to(site).as_posix()}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def validate_root_files(site: Path) -> None:
    llms = (site / "llms.txt").read_text(encoding="utf-8")
    for token in (
        "## Resmî Kanallar",
        "## Teknik Çözüm ve Ekipman Rehberleri",
        "Ev/Ofis Kesinti Hazırlık Ekipmanları",
        "Cihaz ve Pano Koruma Ekipmanları",
        "GES ve Yedek Enerji Sistemleri",
        "Amazon Türkiye satış ortaklığı",
    ):
        if token not in llms:
            raise RuntimeError(f"llms.txt eksik: {token}")
    robots = (site / "robots.txt").read_text(encoding="utf-8")
    for agent in ("OAI-SearchBot", "GPTBot", "PerplexityBot", "ClaudeBot", "Bytespider", "Google-Extended"):
        if f"User-agent: {agent}" not in robots:
            raise RuntimeError(f"robots.txt AI agent eksik: {agent}")


def run(site: Path, base_path: str) -> dict:
    site = site.resolve()
    base_path = normalize_base_path(base_path)
    validate_root_files(site)
    global_rel_changes = 0
    for html_path in site.rglob("*.html"):
        source = html_path.read_text(encoding="utf-8", errors="strict")
        updated, count = ensure_affiliate_rel(source)
        if updated != source:
            html_path.write_text(updated, encoding="utf-8")
        global_rel_changes += count

    metrics = {
        "pages": {},
        "structuredData": {"products": 0, "recommendations": 0, "offers": 0, "comparisonItems": 0},
        "deepLinks": 0,
        "faqLinks": 0,
        "affiliateRelChanged": global_rel_changes,
        "affiliateRelChecked": 0,
        "ssrBaseline": False,
    }

    targets = (
        PRODUCT_HUB_ROUTE,
        MATCHER_ROUTE,
        SURGE_PRODUCTS_ROUTE,
        SURGE_GUIDE_ROUTE,
        POWER_STATION_ROUTE,
        COMPARISON_ROUTE,
    )
    for route in targets:
        result = process_page(route_file(site, route), base_path)
        metrics["pages"][route] = result
        metrics["deepLinks"] += result["deepIds"]
        metrics["faqLinks"] += result["faqLinks"]
        metrics["affiliateRelChanged"] += result["affiliateRel"]

    matcher_path = route_file(site, MATCHER_ROUTE)
    if not matcher_path.is_file():
        raise FileNotFoundError("Akıllı ürün seçimi artifactı bulunamadı")
    matcher = matcher_path.read_text(encoding="utf-8")
    matcher, ssr_added = inject_ssr_baseline(matcher, base_path)
    matcher, _ = inject_jsonld_script(
        matcher,
        "alo186-ssr-product-itemlist-v250",
        selector_payload(CANONICAL_ORIGIN + MATCHER_ROUTE),
    )
    matcher_path.write_text(matcher, encoding="utf-8")
    metrics["ssrBaseline"] = ssr_added or 'data-alo186-ssr-products-v250="true"' in matcher

    surge_path = route_file(site, SURGE_PRODUCTS_ROUTE)
    if not surge_path.is_file():
        raise FileNotFoundError("v249 akım korumalı priz ürün sayfası bulunamadı")
    surge = surge_path.read_text(encoding="utf-8")
    surge, kg_metrics = augment_product_knowledge_graph(
        surge,
        CANONICAL_ORIGIN + SURGE_PRODUCTS_ROUTE,
    )
    surge, rel_count = ensure_affiliate_rel(surge)
    surge, deep_count = assign_deep_ids(surge)
    surge_path.write_text(surge, encoding="utf-8")
    for key in ("products", "recommendations", "offers"):
        metrics["structuredData"][key] += kg_metrics[key]
    metrics["affiliateRelChanged"] += rel_count
    metrics["deepLinks"] += deep_count

    comparison_path = route_file(site, COMPARISON_ROUTE)
    if not comparison_path.is_file():
        raise FileNotFoundError("UPS / power station karşılaştırma sayfası bulunamadı")
    comparison = comparison_path.read_text(encoding="utf-8")
    comparison, anchor_changes = ensure_comparison_anchors(comparison)
    comparison, added = inject_jsonld_script(
        comparison,
        "alo186-product-comparison-v250",
        comparison_payload(CANONICAL_ORIGIN + COMPARISON_ROUTE.rstrip("/")),
    )
    comparison_path.write_text(comparison, encoding="utf-8")
    metrics["deepLinks"] += anchor_changes
    metrics["structuredData"]["comparisonItems"] = 2
    metrics["pages"][COMPARISON_ROUTE]["comparisonSchemaAdded"] = added

    checked, rel_errors = validate_rel_across_site(site)
    if rel_errors:
        raise RuntimeError("Affiliate rel sözleşmesi başarısız:\n" + "\n".join(rel_errors[:20]))
    metrics["affiliateRelChecked"] = checked
    touched_html = "\n".join(
        route_file(site, route).read_text(encoding="utf-8", errors="ignore")
        for route in targets
        if route_file(site, route).is_file()
    )
    metrics["deepLinks"] = len(
        set(re.findall(r'\bid=["\']((?:rehber|urun|ssr-urun)-[^"\']+)["\']', touched_html, re.I))
    )
    metrics["faqLinks"] = len(
        set(re.findall(r'\bdata-related-solution=["\']([^"\']+)["\']', touched_html, re.I))
    )

    types: set[str] = set()
    jsonld_count = 0
    for route in targets:
        path = route_file(site, route)
        if not path.is_file():
            continue
        for payload in jsonld_blocks(path.read_text(encoding="utf-8")):
            jsonld_count += 1
            stack = [payload]
            while stack:
                current = stack.pop()
                if isinstance(current, dict):
                    raw_type = current.get("@type")
                    if isinstance(raw_type, str):
                        types.add(raw_type)
                    elif isinstance(raw_type, list):
                        types.update(str(item) for item in raw_type)
                    stack.extend(current.values())
                elif isinstance(current, list):
                    stack.extend(current)

    report = {
        "ok": True,
        "version": VERSION,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "basePath": base_path,
        **metrics,
        "validation": {
            "jsonLdParseable": True,
            "jsonLdBlocks": jsonld_count,
            "schemaTypes": sorted(types),
            "schemaOrg": "local JSON-LD parse and visible-content contract passed",
            "googleRichResults": {
                "articleAndBreadcrumb": "types present; public Google eligibility is not asserted by local validation",
                "productSnippet": "not claimed; verified price/availability Offer feed is empty",
                "offerPolicy": "Offer emitted only from complete, visible and <=24h verified records",
            },
        },
        "offerGate": {
            "configuredRecords": len(offer_config()["offers"]),
            "emitted": metrics["structuredData"]["offers"],
            "reason": "Amazon price and availability are not published without a fresh server-side verified feed.",
        },
    }
    (site / REPORT_NAME).write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    update_release(site, base_path, report)
    recompute_checksums(site)
    return report


def validate(site: Path, base_path: str) -> dict:
    site = site.resolve()
    base_path = normalize_base_path(base_path)
    report_path = site / REPORT_NAME
    if not report_path.is_file():
        raise FileNotFoundError(REPORT_NAME)
    report = json.loads(report_path.read_text(encoding="utf-8"))
    if report.get("version") != VERSION or report.get("ok") is not True:
        raise RuntimeError("AEO report geçersiz")
    validate_root_files(site)
    matcher = route_file(site, MATCHER_ROUTE).read_text(encoding="utf-8")
    if 'data-alo186-ssr-products-v250="true"' not in matcher:
        raise RuntimeError("SSR ürün baseline eksik")
    if matcher.count('class="ssr-choice-card"') != len(SSR_CHOICES):
        raise RuntimeError("SSR ürün kart sayısı yanlış")
    comparison = route_file(site, COMPARISON_ROUTE).read_text(encoding="utf-8")
    if 'id="alo186-product-comparison-v250"' not in comparison or 'id="karsilastirma-ups-power-station"' not in comparison:
        raise RuntimeError("Karşılaştırma şeması veya deep-link eksik")
    surge = route_file(site, SURGE_PRODUCTS_ROUTE).read_text(encoding="utf-8")
    if '"@type": "Recommendation"' not in surge:
        raise RuntimeError("Recommendation JSON-LD eksik")
    if '"@type": "Offer"' in surge and not offer_config()["offers"]:
        raise RuntimeError("Doğrulanmış offer kaydı olmadan Offer yayımlandı")
    checked, errors = validate_rel_across_site(site)
    if errors:
        raise RuntimeError("Affiliate rel validation failed")
    return {"ok": True, "version": VERSION, "basePath": base_path, "affiliateRelChecked": checked}


def main() -> None:
    parser = argparse.ArgumentParser(description="ALO186 AI-commerce AEO ve affiliate semantik katmanı v250")
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--base-path", default="")
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()
    result = validate(args.site, args.base_path) if args.validate_only else run(args.site, args.base_path)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
