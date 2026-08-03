from __future__ import annotations

import argparse
import json
import re
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

import inject_affiliate_aeo_v250 as aeo

LD_SCRIPT_RE = re.compile(
    r'''<script\b[^>]*type=["']application/ld\+json["'][^>]*data-alo186-affiliate-aeo-schema-v250=["']true["'][^>]*>(.*?)</script>''',
    re.I | re.S,
)
BLOCK_RE = re.compile(
    r'''<section\b[^>]*data-alo186-affiliate-aeo-v250=["']true["'][^>]*>.*?</section>''',
    re.I | re.S,
)


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: list[str] = []
        self.affiliate_links: list[tuple[str, set[str]]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        mapping = {name.casefold(): unescape(value or "") for name, value in attrs}
        if mapping.get("id"):
            self.ids.append(mapping["id"])
        if tag.casefold() == "a":
            href = mapping.get("href", "")
            parsed = urlsplit(href)
            host = parsed.netloc.casefold().split(":", 1)[0]
            if host in {"amazon.com.tr", "www.amazon.com.tr", "amzn.to"}:
                self.affiliate_links.append(
                    (href, {token.casefold() for token in mapping.get("rel", "").split() if token})
                )


def walk(value: object):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def schema_types(payload: object) -> set[str]:
    result: set[str] = set()
    for node in walk(payload):
        value = node.get("@type")
        if isinstance(value, str):
            result.add(value)
        elif isinstance(value, list):
            result.update(str(item) for item in value)
    return result


def validate_robots(text: str, errors: list[str]) -> None:
    folded = text.casefold()
    for crawler in aeo.AI_CRAWLERS:
        pattern = re.compile(
            rf"user-agent:\s*{re.escape(crawler)}\s*(?P<body>.*?)(?=\nuser-agent:|\Z)",
            re.I | re.S,
        )
        match = pattern.search(text)
        if not match:
            errors.append(f"robots.txt: {crawler} bloğu eksik")
            continue
        body = match.group("body").casefold()
        for path in ("/", "/rehber/", "/urunler/", "/haberler/", "/amazon-elektrik-urunleri/"):
            if f"allow: {path}" not in body:
                errors.append(f"robots.txt: {crawler} için Allow {path} eksik")
    if "disallow: /" in folded:
        errors.append("robots.txt: kök taramayı kapatan Disallow / bulundu")
    if "sitemap: https://alo186.com/sitemap.xml" not in folded:
        errors.append("robots.txt: canonical sitemap satırı eksik")


def validate_llms(text: str, errors: list[str]) -> None:
    required = (
        "# ALO186",
        "## Resmî ve acil kanallar",
        "## Teknik çözüm ve ekipman rehberleri",
        "### Ev ve ofis kesinti hazırlığı",
        "### Cihaz ve pano koruma ekipmanları",
        "### GES ve yedek enerji sistemleri",
        "https://alo186.com/hesaplama/yedek-guc-cozum-secici/#rehber-ups-mi-power-station-mi",
        "https://alo186.com/hesaplama/gerilim-koruma-cozum-secici/#rehber-gerilim-dalgalanmasinda-cihaz-koruma",
        "https://alo186.com/sitemap.xml",
    )
    for token in required:
        if token not in text:
            errors.append(f"llms.txt: eksik içerik {token}")
    if "www.alo186.com" in text:
        errors.append("llms.txt: legacy www origin bulundu")


def validate_target(site: Path, target: aeo.TargetSpec, base: str, errors: list[str]) -> dict[str, object]:
    path = site / target.file
    label = target.file.as_posix()
    if not path.is_file():
        errors.append(f"{label}: hedef sayfa eksik")
        return {"target": target.key, "ok": False}
    html = path.read_text(encoding="utf-8", errors="strict")
    if html.count(aeo.MARKER) != 1:
        errors.append(f"{label}: görünür v250 blok tekil değil")
    if html.count(aeo.SCHEMA_MARKER) != 1:
        errors.append(f"{label}: JSON-LD v250 tekil değil")
    if html.count(aeo.STYLE_MARKER) != 1:
        errors.append(f"{label}: stil v250 tekil değil")

    parser = PageParser()
    parser.feed(html)
    parser.close()
    duplicate_ids = sorted({value for value in parser.ids if parser.ids.count(value) > 1})
    if duplicate_ids:
        errors.append(f"{label}: yinelenen id: {', '.join(duplicate_ids[:10])}")
    expected_ids = {target.scenario_id, *(item.deep_id for item in target.recommendations)}
    expected_ids.update(item[0] for item in target.faq_items)
    missing_ids = sorted(expected_ids - set(parser.ids))
    if missing_ids:
        errors.append(f"{label}: deep-link id eksik: {', '.join(missing_ids)}")

    expected_asset = aeo.public_url(base, "/" + aeo.STYLE_TARGET.as_posix())
    if expected_asset not in html:
        errors.append(f"{label}: base-path uyumlu stil URL'si eksik: {expected_asset}")

    matches = LD_SCRIPT_RE.findall(html)
    payload: object = {}
    if len(matches) != 1:
        errors.append(f"{label}: işaretli JSON-LD sayısı {len(matches)}")
    else:
        try:
            payload = json.loads(unescape(matches[0]).strip())
        except json.JSONDecodeError as exc:
            errors.append(f"{label}: JSON-LD parse hatası: {exc}")
    types = schema_types(payload)
    required_types = {"Guide", "Product", "Recommendation", "ItemList"}
    missing_types = sorted(required_types - types)
    if missing_types:
        errors.append(f"{label}: JSON-LD tipleri eksik: {', '.join(missing_types)}")
    if target.faq_items and "FAQPage" not in types:
        errors.append(f"{label}: çözüm FAQPage eksik")
    if target.comparison_rows:
        matrices = [
            node for node in walk(payload)
            if node.get("@type") == "ItemList" and "karşılaştırma matrisi" in str(node.get("name", "")).casefold()
        ]
        if len(matrices) != 1:
            errors.append(f"{label}: karşılaştırma ItemList tekil değil")
        if "UPS ve taşınabilir güç istasyonu karşılaştırma matrisi" not in html:
            errors.append(f"{label}: görünür SSR karşılaştırma tablosu eksik")

    products = [node for node in walk(payload) if node.get("@type") == "Product"]
    recommendations = [node for node in walk(payload) if node.get("@type") == "Recommendation"]
    offers = [node for node in walk(payload) if node.get("@type") == "Offer"]
    if len(products) != len(target.recommendations):
        errors.append(f"{label}: Product sayısı {len(products)}; beklenen {len(target.recommendations)}")
    if len(recommendations) != len(target.recommendations):
        errors.append(f"{label}: Recommendation sayısı {len(recommendations)}; beklenen {len(target.recommendations)}")
    if offers:
        errors.append(f"{label}: doğrulanmış merchant payload olmadan Offer yayımlandı")

    blocks = BLOCK_RE.findall(html)
    if len(blocks) != 1:
        errors.append(f"{label}: SSR blok sayısı {len(blocks)}")
        block = ""
    else:
        block = blocks[0]
        if block.count('data-product-recommendation="') != len(target.recommendations):
            errors.append(f"{label}: SSR ürün kartı sayısı yanlış")
        for token in ("Kimler için?", "Uygun değil", "Önce kontrol et"):
            if token not in block:
                errors.append(f"{label}: SSR kart alanı eksik: {token}")
        if "amazon.com.tr/" in block.casefold() or "amzn.to/" in block.casefold():
            errors.append(f"{label}: SSR blok doğrudan mağaza bağlantısı içeriyor")
    if target.faq_items and block.count("İlgili Koruma Ekipmanını İnceleyin") != len(target.faq_items):
        errors.append(f"{label}: FAQ çözüm iç link sayısı yanlış")

    for href, rel in parser.affiliate_links:
        missing = aeo.REQUIRED_AFFILIATE_REL - rel
        if missing:
            errors.append(f"{label}: affiliate rel eksik ({href}): {', '.join(sorted(missing))}")

    return {
        "target": target.key,
        "file": label,
        "schemaTypes": sorted(types),
        "productCount": len(products),
        "recommendationCount": len(recommendations),
        "offerCount": len(offers),
        "deepLinkCount": len(expected_ids),
        "affiliateLinkCount": len(parser.affiliate_links),
    }


def validate(site: Path, base_path: str = "") -> dict[str, object]:
    site = site.resolve()
    base = aeo.normalize_base_path(base_path)
    errors: list[str] = []
    target_reports = [validate_target(site, target, base, errors) for target in aeo.TARGETS]

    robots_path = site / "robots.txt"
    llms_path = site / "llms.txt"
    if not robots_path.is_file():
        errors.append("robots.txt eksik")
    else:
        validate_robots(robots_path.read_text(encoding="utf-8"), errors)
    if not llms_path.is_file():
        errors.append("llms.txt eksik")
    else:
        validate_llms(llms_path.read_text(encoding="utf-8"), errors)

    global_affiliate_links = 0
    for path in sorted(site.rglob("*.html")):
        parser = PageParser()
        parser.feed(path.read_text(encoding="utf-8", errors="strict"))
        parser.close()
        for href, rel in parser.affiliate_links:
            global_affiliate_links += 1
            missing = aeo.REQUIRED_AFFILIATE_REL - rel
            if missing:
                errors.append(
                    f"{path.relative_to(site).as_posix()}: site geneli affiliate rel eksik ({href}): {', '.join(sorted(missing))}"
                )

    release_path = site / "pages-release.json"
    release_receipt: dict[str, object] = {}
    if release_path.is_file():
        payload = json.loads(release_path.read_text(encoding="utf-8"))
        value = payload.get("affiliateAeoV250")
        if isinstance(value, dict):
            release_receipt = value
        else:
            errors.append("pages-release.json: affiliateAeoV250 makbuzu eksik")
    else:
        errors.append("pages-release.json eksik")

    if release_receipt:
        if release_receipt.get("version") != aeo.VERSION:
            errors.append("affiliateAeoV250: sürüm yanlış")
        if release_receipt.get("emittedOfferCount") != 0:
            errors.append("affiliateAeoV250: doğrulanmamış Offer sayısı sıfır değil")
        if release_receipt.get("fakePriceOrStockPublished") is not False:
            errors.append("affiliateAeoV250: sahte fiyat/stok koruması yanlış")

    ok = not errors
    return {
        "ok": ok,
        "version": aeo.VERSION,
        "basePath": base,
        "targetCount": len(aeo.TARGETS),
        "targets": target_reports,
        "globalAffiliateLinkCount": global_affiliate_links,
        "schemaOrgLocalValidation": {
            "status": "PASS" if ok else "FAIL",
            "checks": [
                "JSON-LD syntax",
                "Guide/Product/Recommendation/ItemList graph",
                "visible-content parity",
                "unique deep-link identifiers",
                "SSR recommendation cards",
            ],
        },
        "googleRichResultsReadiness": {
            "status": "PASS_WITH_CONDITIONAL_PRODUCT_OFFER" if ok else "FAIL",
            "productMarkupPresent": True,
            "merchantOfferPublished": False,
            "merchantOfferReason": "Price, availability and validity are not emitted without a fresh verified Amazon payload.",
            "fakePriceUsed": False,
        },
        "robots": {"status": "PASS" if robots_path.is_file() and not any(error.startswith("robots.txt") for error in errors) else "FAIL"},
        "llms": {"status": "PASS" if llms_path.is_file() and not any(error.startswith("llms.txt") for error in errors) else "FAIL"},
        "errors": errors,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="ALO186 affiliate AEO v250 structured data validator")
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--base-path", default="")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    report = validate(args.site, args.base_path)
    text = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(text, encoding="utf-8")
    print(text, end="")
    if not report["ok"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
