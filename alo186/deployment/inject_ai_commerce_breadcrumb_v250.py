from __future__ import annotations

import json
import re
from pathlib import Path

VERSION = 250
MARKER = 'data-alo186-ai-commerce-breadcrumb-v250="true"'
PRODUCT_GRAPH_ROUTE = Path(
    "amazon-elektrik-urunleri/akim-korumali-priz-yuk-uygunluk-secimi/index.html"
)

ROUTES: tuple[tuple[str, str, str], ...] = (
    (
        "hesaplama/yedek-guc-cozum-secici/index.html",
        "/hesaplama/yedek-guc-cozum-secici/",
        "UPS, taşınabilir güç istasyonu ve jeneratör çözüm haritası",
    ),
    (
        "hesaplama/yedek-guc-maliyet-karsilastirma/index.html",
        "/hesaplama/yedek-guc-maliyet-karsilastirma/",
        "Yedek güç ürün sınıfları maliyet ve kullanım karşılaştırması",
    ),
    (
        "hesaplama/modem-internet-yedekleme/index.html",
        "/hesaplama/modem-internet-yedekleme/",
        "Modem ve ONT için ürün çözüm ankrajları",
    ),
    (
        "hesaplama/akim-korumali-grup-priz-uygunluk/index.html",
        "/hesaplama/akim-korumali-grup-priz-uygunluk/",
        "Akım korumalı priz ve katmanlı aşırı gerilim çözüm haritası",
    ),
    (
        "hesaplama/gerilim-koruma-cozum-secici/index.html",
        "/hesaplama/gerilim-koruma-cozum-secici/",
        "Gerilim koruma çözüm sınıfları karar haritası",
    ),
    (
        "kesintiye-hazirlik-atolyesi/index.html",
        "/kesintiye-hazirlik-atolyesi",
        "Kesintiye hazırlık ürün sınıfları",
    ),
    (
        PRODUCT_GRAPH_ROUTE.as_posix(),
        "/amazon-elektrik-urunleri/akim-korumali-priz-yuk-uygunluk-secimi/",
        "Akım korumalı priz yük uygunluk seçimi",
    ),
)


def breadcrumb_payload(route: str, title: str) -> dict:
    is_product = route.startswith("/amazon-elektrik-urunleri/")
    parent_name = "Amazon Elektrik Ürünleri" if is_product else "Hesaplama ve Karar Araçları"
    parent_url = (
        "https://alo186.com/amazon-elektrik-urunleri"
        if is_product
        else "https://alo186.com/hesaplama/"
    )
    page_url = "https://alo186.com" + route
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "@id": page_url + "#breadcrumb",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": 1,
                "name": "ALO186",
                "item": "https://alo186.com/elektrik-portali",
            },
            {
                "@type": "ListItem",
                "position": 2,
                "name": parent_name,
                "item": parent_url,
            },
            {
                "@type": "ListItem",
                "position": 3,
                "name": title,
                "item": page_url,
            },
        ],
    }


def inject(html_text: str, route: str, title: str) -> tuple[str, bool]:
    if MARKER in html_text:
        return html_text, False
    payload = json.dumps(
        breadcrumb_payload(route, title),
        ensure_ascii=False,
        separators=(",", ":"),
    ).replace("</", "<\\/")
    script = f'<script type="application/ld+json" {MARKER}>{payload}</script>'
    updated, count = re.subn(
        r"</head\s*>",
        script + "\n</head>",
        html_text,
        count=1,
        flags=re.IGNORECASE,
    )
    if count != 1:
        raise RuntimeError(f"Breadcrumb JSON-LD için </head> bulunamadı: {route}")
    return updated, True


def json_ld_payloads(html_text: str) -> list[dict]:
    payloads: list[dict] = []
    for raw in re.findall(
        r'<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        html_text,
        flags=re.IGNORECASE | re.DOTALL,
    ):
        try:
            parsed = json.loads(raw.replace("<\\/", "</"))
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"JSON-LD ayrıştırılamadı: {exc}") from exc
        if isinstance(parsed, dict):
            payloads.append(parsed)
    return payloads


def collect_types(value: object) -> set[str]:
    found: set[str] = set()
    if isinstance(value, dict):
        type_value = value.get("@type")
        if isinstance(type_value, str):
            found.add(type_value)
        elif isinstance(type_value, list):
            found.update(str(item) for item in type_value)
        for nested in value.values():
            found.update(collect_types(nested))
    elif isinstance(value, list):
        for nested in value:
            found.update(collect_types(nested))
    return found


def validate_existing_product_graph(output: Path) -> dict[str, object]:
    path = output / PRODUCT_GRAPH_ROUTE
    if not path.is_file():
        raise FileNotFoundError(f"Doğrulanmış ürün grafiği rotası eksik: {path}")
    text = path.read_text(encoding="utf-8")
    payloads = json_ld_payloads(text)
    types: set[str] = set()
    for payload in payloads:
        types.update(collect_types(payload))
    required = {"Product", "Brand", "ItemList", "BreadcrumbList"}
    missing = sorted(required - types)
    if missing:
        raise RuntimeError("Ürün grafiği zorunlu tipleri eksik: " + ", ".join(missing))
    if "Offer" in types:
        raise RuntimeError("Doğrulanmış fiyat/stok/satıcı olmadan Offer yayımlanamaz.")
    for token in ("ASIN", "MPN", "additionalProperty"):
        if token not in text:
            raise RuntimeError(f"Ürün grafiği kimlik/özellik sözleşmesi eksik: {token}")
    return {
        "route": "/amazon-elektrik-urunleri/akim-korumali-priz-yuk-uygunluk-secimi/",
        "requiredTypes": sorted(required),
        "offerEmitted": False,
        "asinMpnIdentifiers": True,
        "additionalProperty": True,
    }


def apply(output: Path) -> dict[str, object]:
    injected = 0
    existing = 0
    for relative, route, title in ROUTES:
        path = output / relative
        if not path.is_file():
            raise FileNotFoundError(f"Breadcrumb hedef rotası eksik: {relative}")
        text = path.read_text(encoding="utf-8")
        updated, changed = inject(text, route, title)
        if changed:
            path.write_text(updated, encoding="utf-8")
            injected += 1
        else:
            existing += 1
    product_graph = validate_existing_product_graph(output)
    return {
        "ok": True,
        "version": VERSION,
        "breadcrumbRouteCount": len(ROUTES),
        "injected": injected,
        "alreadyPresent": existing,
        "productGraph": product_graph,
    }
