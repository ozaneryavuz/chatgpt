from __future__ import annotations

import argparse
import json
import re
from html import unescape
from pathlib import Path
from urllib.parse import urlsplit

AFFILIATE_HOSTS = {
    "amazon.com.tr",
    "www.amazon.com.tr",
    "amzn.to",
    "www.amzn.to",
}
REQUIRED_REL = {"sponsored", "nofollow", "noopener"}
DISCLOSURE_PATTERN = re.compile(
    r"satış\s+ortaklığı|affiliate|nitelikli\s+satın\s+alımlardan\s+komisyon",
    re.I,
)
PROFESSIONAL_ONLY_PATTERN = re.compile(
    r"professional[- ]only|doğrudan\s+(?:amazon\s+veya\s+başka\s+)?mağaza\s+bağlantısı\s+(?:yok|kapalı|gösterilmez)|profesyonel\s+doğrulama",
    re.I,
)
NO_BUY_PATTERNS = (
    re.compile(
        r"mevcut.{0,150}(?:yeterli|uygun|güvenli).{0,180}(?:satın\s+alma|satın\s+almayın|yeni\s+ürün\s+alma)",
        re.I | re.S,
    ),
    re.compile(r"satın\s+almama\s+(?:seçeneği|sonucu|hakkı|koruması)", re.I),
    re.compile(r"yeni\s+ürün\s+almak\s+gerekmeyebilir", re.I),
    re.compile(r"ürün\s+satın\s+alma\s+zorunluluğu\s+yok", re.I),
    re.compile(r"(?:sipariş|satın\s+alma).{0,80}(?:vermeyin|durdurun)", re.I | re.S),
)
UNVERIFIED_COMMERCIAL_PATTERNS = (
    re.compile(r"\b\d[\d.]*\s*(?:TL|₺)\b", re.I),
    re.compile(r"\bstokta\s+\d+\b", re.I),
    re.compile(r"\b[1-5](?:[.,]\d)?\s*/\s*5\b"),
    re.compile(r"\b\d+\s*yıl\s+garanti\b", re.I),
    re.compile(r'"ratingValue"\s*:', re.I),
    re.compile(r'"price"\s*:', re.I),
    re.compile(r'"priceCurrency"\s*:', re.I),
)
HIGH_RISK_PATTERN = re.compile(
    r"\b(?:rccb|rcbo|mcb|kaçak\s+akım\s+rölesi|parafudr|\bspd\b|gerilim\s+koruma\s+rölesi|"
    r"kontaktör|dağıtım\s+panosu|wallbox|jeneratör|transfer\s+şalteri|sabit\s+inverter|"
    r"batarya\s+bankası|topraklama|harmonik\s+filtre|ges\s+inverter|pv\s+dc\s+sigorta)\b",
    re.I,
)
ANCHOR_PATTERN = re.compile(r"<a\b(?P<attrs>[^>]*)>(?P<body>.*?)</a>", re.I | re.S)
ATTR_PATTERN = re.compile(
    r"(?P<name>[a-zA-Z_:][-a-zA-Z0-9_:.]*)\s*=\s*(?P<quote>['\"])(?P<value>.*?)(?P=quote)",
    re.S,
)
CANONICAL_ORIGIN = "https://alo186.com"

COMMERCIAL_ROUTES = {
    "/amazon-elektrik-urunleri": {"direct": False, "affiliate": True, "professional_only": False},
    "/amazon-elektrik-urunleri/powerbank-usb-c-secimi": {"direct": True, "affiliate": True, "professional_only": False},
    "/amazon-elektrik-urunleri/akim-korumali-grup-priz-secimi": {"direct": False, "affiliate": True, "professional_only": False},
    "/amazon-elektrik-urunleri/modem-mini-ups-secimi": {"direct": False, "affiliate": True, "professional_only": False},
    "/amazon-elektrik-urunleri/acil-aydinlatma-duman-alarmi": {"direct": False, "affiliate": True, "professional_only": False},
    "/amazon-elektrik-urunleri/tasinabilir-guc-istasyonu-secimi": {"direct": False, "affiliate": True, "professional_only": False},
    "/amazon-elektrik-urunleri/akilli-priz-enerji-olcer-secimi": {"direct": False, "affiliate": True, "professional_only": False},
    "/amazon-elektrik-urunleri/ges-malzemeleri-secimi": {"direct": False, "affiliate": False, "professional_only": True},
}
SERVICE_ROUTES = {
    "/hizmetler/otel-elektrik-surekliligi-denetimi/",
    "/hizmetler/elektrik-teklif-teknik-inceleme/",
    "/hizmetler/ges-batarya-ev-sarj-fizibilitesi/",
}
DIRECT_CATEGORY_POLICIES = {
    "powerbank": {"risk": "consumer", "affiliate_policy": "verified_direct"},
    "usb_c_charger": {"risk": "consumer", "affiliate_policy": "verified_direct"},
    "usb_c_cable": {"risk": "consumer", "affiliate_policy": "verified_direct"},
    "usb_c_hub": {"risk": "consumer", "affiliate_policy": "verified_direct"},
    "display_cable": {"risk": "consumer", "affiliate_policy": "verified_direct"},
}


def attributes(raw: str) -> dict[str, str]:
    return {
        match.group("name").casefold(): unescape(match.group("value"))
        for match in ATTR_PATTERN.finditer(raw)
    }


def text_only(value: str) -> str:
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", value))).strip()


def is_affiliate_url(value: str) -> bool:
    parsed = urlsplit(value.strip())
    return parsed.scheme in {"http", "https"} and parsed.hostname in AFFILIATE_HOSTS


def has_no_buy(value: str) -> bool:
    return any(pattern.search(value) for pattern in NO_BUY_PATTERNS)


def has_independence(value: str) -> bool:
    folded = value.casefold()
    independent = "bağımsız" in folded
    institution = any(token in folded for token in ("edaş", "kamu kurumu", "resmî kurum", "ürün satıcısı"))
    boundary = "değildir" in folded or "değil" in folded
    return independent and institution and boundary


def route_file(site: Path, route: str) -> Path:
    return site / route.strip("/") / "index.html"


def canonical_expected(route: str) -> str:
    return f"{CANONICAL_ORIGIN}{route}"


def scan_affiliate_anchors(path: Path, site: Path) -> list[str]:
    html = path.read_text(encoding="utf-8", errors="ignore")
    relative = path.relative_to(site).as_posix()
    errors: list[str] = []
    has_disclosure = bool(DISCLOSURE_PATTERN.search(text_only(html)))
    for match in ANCHOR_PATTERN.finditer(html):
        attrs = attributes(match.group("attrs"))
        href = attrs.get("href", "")
        if not is_affiliate_url(href):
            continue
        rel = {token.casefold() for token in attrs.get("rel", "").split() if token}
        missing = REQUIRED_REL - rel
        if missing:
            errors.append(f"{relative}: affiliate bağlantısında eksik rel tokenları: {', '.join(sorted(missing))}")
        if not has_disclosure:
            errors.append(f"{relative}: affiliate bağlantısı var fakat görünür satış ortaklığı açıklaması yok")
        context = text_only(html[max(0, match.start() - 900): min(len(html), match.end() + 900)])
        risky = HIGH_RISK_PATTERN.search(context)
        if risky:
            errors.append(
                f"{relative}: yüksek riskli/sabit tesisat bağlamında doğrudan mağaza bağlantısı yasak: {risky.group(0)}"
            )
    return errors


def validate_commercial_pages(site: Path) -> tuple[list[str], dict]:
    errors: list[str] = []
    direct_pages = 0
    affiliate_pages = 0
    professional_only_pages = 0
    for route, policy in COMMERCIAL_ROUTES.items():
        path = route_file(site, route)
        if not path.is_file():
            errors.append(f"{route}: ticari sayfa artifactta eksik")
            continue
        html = path.read_text(encoding="utf-8", errors="ignore")
        visible = text_only(html)
        canonical = canonical_expected(route)
        if f'rel="canonical" href="{canonical}"' not in html:
            errors.append(f"{route}: canonical yanlış veya eksik")
        if policy["affiliate"]:
            affiliate_pages += 1
            if not DISCLOSURE_PATTERN.search(visible):
                errors.append(f"{route}: görünür satış ortaklığı açıklaması eksik")
        else:
            professional_only_pages += 1
            if not PROFESSIONAL_ONLY_PATTERN.search(visible):
                errors.append(f"{route}: professional-only mağaza sınırı görünür değil")
            if 'data-commercial-scope="professional-only"' not in html:
                errors.append(f"{route}: professional-only makine tarafından okunabilir işareti eksik")
        if not has_no_buy(visible):
            errors.append(f"{route}: mevcut ekipman yeterliyse satın almama sınırı eksik")
        if not has_independence(visible):
            errors.append(f"{route}: ALO186 bağımsızlık/resmî kurum sınırı eksik")
        if "<form" in html.casefold() or 'type="email"' in html.casefold() or 'type="tel"' in html.casefold():
            errors.append(f"{route}: ticari içerik sayfası kişisel veri formu içermemeli")
        for pattern in UNVERIFIED_COMMERCIAL_PATTERNS:
            if pattern.search(html):
                errors.append(f"{route}: doğrulanmamış fiyat/stok/puan/garanti iddiası bulundu: {pattern.pattern}")
        static_affiliate = any(
            is_affiliate_url(attributes(match.group("attrs")).get("href", ""))
            for match in ANCHOR_PATTERN.finditer(html)
        )
        if static_affiliate:
            errors.append(f"{route}: kaynak HTML statik affiliate bağlantısı içermemeli; runtime tazelik kapısı kullanılmalı")
        has_product_container = "data-fresh-products" in html
        has_product_center = "data-product-center" in html
        if policy["direct"]:
            direct_pages += 1
            if not has_product_container:
                errors.append(f"{route}: doğrudan kategori için taze katalog konteyneri eksik")
        elif has_product_container:
            errors.append(f"{route}: guide kategoride doğrudan ürün konteyneri bulunmamalı")
        if policy["professional_only"] and has_product_center:
            errors.append(f"{route}: professional-only sayfada ürün merkezine ticari CTA bulunmamalı")
    return errors, {
        "commercialPageCount": len(COMMERCIAL_ROUTES),
        "directCommercialPageCount": direct_pages,
        "affiliateCommercialPageCount": affiliate_pages,
        "professionalOnlyPageCount": professional_only_pages,
    }


def validate_service_pages(site: Path) -> tuple[list[str], dict]:
    errors: list[str] = []
    for route in SERVICE_ROUTES:
        path = route_file(site, route)
        if not path.is_file():
            errors.append(f"{route}: ücretli hizmet sayfası artifactta eksik")
            continue
        html = path.read_text(encoding="utf-8", errors="ignore")
        visible = text_only(html)
        if f'rel="canonical" href="{canonical_expected(route)}"' not in html:
            errors.append(f"{route}: canonical yanlış veya eksik")
        compact = html.replace(" ", "")
        for schema_type in ('"@type":"Service"', '"@type":"FAQPage"', '"@type":"BreadcrumbList"', '"@type":"OfferCatalog"'):
            if schema_type not in compact:
                errors.append(f"{route}: yapılandırılmış veri eksik: {schema_type}")
        if "amazon.com.tr" in html.casefold() or "amzn.to" in html.casefold():
            errors.append(f"{route}: ücretli mühendislik hizmetinde affiliate/mağaza bağlantısı olmamalı")
        if "<form" in html.casefold() or 'type="email"' in html.casefold() or 'type="tel"' in html.casefold():
            errors.append(f"{route}: hizmet sayfası doğrudan kişisel veri formu içermemeli")
        if not has_independence(visible):
            errors.append(f"{route}: resmî kurum/EDAŞ bağımsızlık açıklaması eksik")
        if not re.search(r"ücretli\s+(?:bağımsız\s+)?(?:profesyonel\s+)?hizmet|yazılı\s+(?:olarak\s+)?(?:kapsam|teyit)|teklif\s+edilir", visible, re.I):
            errors.append(f"{route}: ücretli hizmet ve yazılı kapsam sınırı görünür değil")
        if not has_no_buy(visible) and not re.search(r"mevcut.{0,180}(?:yeterli|ertelenebilir|korunur|sınırlı\s+iyileştirme)", visible, re.I | re.S):
            errors.append(f"{route}: yeni yatırım yerine mevcut sistem/sınırlı iyileştirme seçeneği eksik")
        for pattern in UNVERIFIED_COMMERCIAL_PATTERNS:
            if pattern.search(html):
                errors.append(f"{route}: doğrulanmamış ticari iddia bulundu: {pattern.pattern}")
    return errors, {"servicePageCount": len(SERVICE_ROUTES)}


def validate_runtime(site: Path) -> tuple[list[str], dict]:
    errors: list[str] = []
    runtime_path = site / "amazon-elektrik-urunleri" / "commercial.js"
    catalog_path = site / "akilli-urun-secimi" / "catalog.js"
    if not catalog_path.is_file():
        catalog_path = site / "urun-eslestirme" / "catalog.js"
    if not runtime_path.is_file():
        errors.append("amazon-elektrik-urunleri/commercial.js: ticari runtime eksik")
        return errors, {"directCategoryCount": 0}
    if not catalog_path.is_file():
        errors.append("catalog.js: ürün katalog runtimeı eksik")
        return errors, {"directCategoryCount": 0}

    runtime = runtime_path.read_text(encoding="utf-8", errors="ignore")
    catalog = catalog_path.read_text(encoding="utf-8", errors="ignore")
    for token in (
        "freshOnly: true",
        "verificationStatus",
        "sponsored nofollow noopener",
        "category.mode === 'direct'",
        "Fiyat, stok, satıcı, teslimat, puan ve garanti",
        "if (professionalOnly) return;",
    ):
        if token not in runtime:
            errors.append(f"commercial.js: güven/tazelik sözleşmesi eksik: {token}")
    for forbidden in (
        "product.price",
        "product.stock",
        "product.rating",
        "product.warranty",
        "affiliateCommission",
    ):
        if forbidden in runtime:
            errors.append(f"commercial.js: ticari sıralama veya doğrulanmamış alan kullanılıyor: {forbidden}")

    direct_ids = re.findall(r"\{id:'([^']+)'[^{}]*?mode:'direct'", catalog)
    direct_rows = re.findall(
        r"\{id:'([^']+)',name:'[^']+',mode:'direct',risk:'([^']+)',affiliatePolicy:'([^']+)'",
        catalog,
    )
    expected_ids = set(DIRECT_CATEGORY_POLICIES)
    found_ids = set(direct_ids)
    duplicate_ids = sorted({category_id for category_id in direct_ids if direct_ids.count(category_id) > 1})
    if duplicate_ids:
        errors.append(f"catalog.js: yinelenen doğrudan kategori kimliği bulundu: {duplicate_ids}")
    if found_ids != expected_ids:
        errors.append(
            "catalog.js: doğrulanmış düşük riskli doğrudan kategori allowlistiyle uyuşmuyor; "
            f"eksik={sorted(expected_ids - found_ids)}, beklenmeyen={sorted(found_ids - expected_ids)}"
        )
    metadata = {category_id: (risk, affiliate_policy) for category_id, risk, affiliate_policy in direct_rows}
    for category_id, policy in DIRECT_CATEGORY_POLICIES.items():
        actual = metadata.get(category_id)
        expected = (policy["risk"], policy["affiliate_policy"])
        if actual != expected:
            errors.append(
                f"catalog.js: {category_id} doğrudan kategori güven metadatası yanlış veya eksik; "
                f"beklenen={expected}, bulunan={actual}"
            )
    unexpected_metadata = sorted(set(metadata) - expected_ids)
    if unexpected_metadata:
        errors.append(f"catalog.js: allowlist dışı doğrudan kategori metadatası bulundu: {unexpected_metadata}")
    if "verificationMaxAgeDays=45" not in catalog:
        errors.append("catalog.js: 45 günlük katalog tazelik sınırı eksik")
    return errors, {
        "directCategoryCount": len(direct_ids),
        "directCategoryIds": direct_ids,
        "directCategoryPolicies": DIRECT_CATEGORY_POLICIES,
    }


def validate_site(site: Path) -> dict:
    site = site.resolve()
    if not site.is_dir():
        raise FileNotFoundError(f"Site artifactı bulunamadı: {site}")
    errors: list[str] = []
    for path in sorted(site.rglob("*.html")):
        errors.extend(scan_affiliate_anchors(path, site))
    commercial_errors, commercial = validate_commercial_pages(site)
    service_errors, services = validate_service_pages(site)
    runtime_errors, runtime = validate_runtime(site)
    errors.extend(commercial_errors)
    errors.extend(service_errors)
    errors.extend(runtime_errors)
    result = {
        "ok": not errors,
        "htmlFileCount": len(list(site.rglob("*.html"))),
        **commercial,
        **services,
        **runtime,
        "commercialPolicy": {
            "unverifiedPriceStockRatingWarranty": False,
            "staticAffiliateLinksInSourcePages": False,
            "directCategories": list(DIRECT_CATEGORY_POLICIES),
            "freshnessDays": 45,
            "highRiskDirectAffiliate": False,
            "professionalOnlyDirectAffiliate": False,
            "officialInstitutionImpression": False,
        },
        "errorCount": len(errors),
        "errors": errors,
    }
    if errors:
        raise AssertionError(json.dumps(result, ensure_ascii=False, indent=2))
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="ALO186 ticari kategori ve ücretli hizmet rotalarını fail-closed doğrular.")
    parser.add_argument("--site", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(validate_site(args.site), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
