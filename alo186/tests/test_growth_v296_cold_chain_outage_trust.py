#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARTICLE = ROOT / 'alo186/haberler/elektrik-kesilince-buzdolabi-kac-saat-soguk-kalir/index.html'
TOOL = ROOT / 'alo186/hesaplama/buzdolabi-derin-dondurucu-elektrik-kesintisi-gida-plani/index.html'
SELECTOR = ROOT / 'alo186/amazon-elektrik-urunleri/buzdolabi-dondurucu-termometre-soguk-zincir/index.html'
OVERLAY = ROOT / 'alo186/deployment/routing-overlays/growth-v296-cold-chain-outage-trust.json'
DECISION = ROOT / 'alo186/deployment/affiliate-category-decisions/cold-chain-outage-v296.json'
POLICY = ROOT / 'alo186/deployment/affiliate_route_risk_policy_v265.json'
ROUTES = {
    ARTICLE: 'https://alo186.com/haberler/elektrik-kesilince-buzdolabi-kac-saat-soguk-kalir/',
    TOOL: 'https://alo186.com/hesaplama/buzdolabi-derin-dondurucu-elektrik-kesintisi-gida-plani/',
    SELECTOR: 'https://alo186.com/amazon-elektrik-urunleri/buzdolabi-dondurucu-termometre-soguk-zincir/',
}


class AnchorParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.anchors: list[dict[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.casefold() == 'a':
            self.anchors.append({key.casefold(): value or '' for key, value in attrs})


def txt(path: Path) -> str:
    assert path.is_file(), path
    return path.read_text(encoding='utf-8')


def check_page(path: Path, canonical: str) -> str:
    html = txt(path)
    assert re.findall(r'<link\s+rel="canonical"\s+href="([^"]+)"', html, re.I) == [canonical]
    blocks = re.findall(r'<script\s+type="application/ld\+json">(.*?)</script>', html, re.I | re.S)
    assert blocks, path
    for block in blocks:
        json.loads(block)
    for bad in (
        'https://www.alo186.com',
        '"@type":"Offer"',
        '"@type":"AggregateRating"',
        '"@type":"Review"',
        '"price":',
        '"priceCurrency":',
        '"availability":',
        '"warranty":',
        '"delivery":',
    ):
        assert bad not in html, (path, bad)
    return html


def main() -> None:
    article = check_page(ARTICLE, ROUTES[ARTICLE])
    tool = check_page(TOOL, ROUTES[TOOL])
    selector = check_page(SELECTOR, ROUTES[SELECTOR])

    for required in (
        'Kapıyı kapalı tutun; süreyi tahmin etmek yerine sıcaklığı ve gıda türünü doğrulayın.',
        'yaklaşık <strong>4 saat</strong>',
        'yaklaşık <strong>48 saat</strong>',
        'yaklaşık <strong>24 saat</strong>',
        'Güvenliği tat veya kokuyla test etmeyin',
        'Mevcut hazırlık yeterliyse yeni ürün almayın',
        '/hesaplama/buzdolabi-derin-dondurucu-elektrik-kesintisi-gida-plani/',
        '/amazon-elektrik-urunleri/buzdolabi-dondurucu-termometre-soguk-zincir/',
        'ALO186 bağımsız bilgilendirme platformudur.',
    ):
        assert required in article, required
    assert 'amazon.com.tr' not in article.casefold()

    for required in (
        'Ücretsiz · kişisel veri yok · mağaza bağlantısı yok',
        'Mevcut plan yeterli — yeni ürün almayın',
        'Kontaminasyon veya hastalık şüphesinde ticari yol kapalıdır',
        'Bu araçta Amazon veya başka mağaza bağlantısı yoktur',
        '30 gün',
        '90 gün',
        '180 gün',
        'Professional-only değerlendirme',
    ):
        assert required in tool, required
    for bad in (
        'fetch(',
        'XMLHttpRequest',
        'localStorage.',
        'sessionStorage.',
        'document.cookie',
        'type="email"',
        'type="tel"',
    ):
        assert bad not in tool, bad
    assert 'amazon.com.tr' not in tool.casefold()

    for required in (
        'Amazon Türkiye satış ortaklığı',
        'Satın almama geçerli sonuçtur',
        'yeni ürün almayacağım',
        'Aktif kesinti, kontaminasyon veya özel soğuk zincirde mağaza yolu kapalıdır',
        'Bağlantılar kilitli',
        'rel="sponsored nofollow noopener"',
        'Fiyat, stok, satıcı, puan, yorum, teslimat ve garanti bilgisi ALO186 tarafından yayımlanmaz',
        'Yalnız gelecekteki elektrik kesintisi hazırlığı',
    ):
        assert required in selector, required
    assert 'href="https://www.amazon.com.tr' not in selector.casefold()
    assert 'data-url="https://www.amazon.com.tr' not in selector.casefold()
    parser = AnchorParser()
    parser.feed(selector)
    product_ids = {'thermometerLink', 'coolerLink', 'icePackLink'}
    product_anchors = [anchor for anchor in parser.anchors if anchor.get('id') in product_ids]
    assert len(product_anchors) == 3
    for anchor in product_anchors:
        assert not anchor.get('href')
        assert {'sponsored', 'nofollow', 'noopener'}.issubset(set(anchor.get('rel', '').split()))
        assert anchor.get('aria-disabled') == 'true'

    overlay = json.loads(txt(OVERLAY))
    assert overlay['version'] == 296
    assert overlay['name'] == 'growth-v296-cold-chain-outage-trust'
    assert len(overlay['routes']) == 3
    assert {item['canonicalPath'] for item in overlay['routes']} == {
        '/haberler/elektrik-kesilince-buzdolabi-kac-saat-soguk-kalir/',
        '/hesaplama/buzdolabi-derin-dondurucu-elektrik-kesintisi-gida-plani/',
        '/amazon-elektrik-urunleri/buzdolabi-dondurucu-termometre-soguk-zincir/',
    }

    decision = json.loads(txt(DECISION))
    assert decision['version'] == 296
    assert decision['decision'] == 'guarded-low-risk-consumer-affiliate'
    expected = {
        'newMerchantLinks': True,
        'linksLockedByDefault': True,
        'futurePreparednessOnly': True,
        'noBuyOutcomeRequired': True,
        'activeOutageCommerceClosed': True,
        'contaminationCommerceClosed': True,
        'specialColdChainCommerceClosed': True,
        'personalDataCollectionForbidden': True,
        'noPriceStockRatingWarrantyClaims': True,
        'affiliateDisclosureRequiredBeforeAnyMerchantLink': True,
        'officialInstitutionImpressionForbidden': True,
        'professionalScopeForComplexSystems': True,
    }
    for key, value in expected.items():
        assert decision['conversionPolicy'][key] is value, (key, decision['conversionPolicy'][key])
    assert decision['conversionPolicy']['merchant'] == 'Amazon Türkiye'
    assert len(decision['allowedLowRiskClasses']) == 3
    assert len(decision['excludedProfessionalOrSafetyClasses']) >= 7
    assert [item['days'] for item in decision['repeatVisitReasons']] == [30, 90, 180]

    policy = json.loads(txt(POLICY))
    assert 'buzdolabi-dondurucu-termometre-soguk-zincir' in policy['governedAffiliateRoutePatterns']
    for pattern in ('jenerator', 'ats', 'sabit-tesisat'):
        assert pattern in policy['professionalLeadOnlyRoutePatterns']

    print(json.dumps({
        'ok': True,
        'version': 296,
        'newRoutes': 3,
        'initialActiveMerchantLinks': 0,
        'guardedProductClasses': 3,
        'repeatVisitDays': [30, 90, 180],
        'futurePreparednessOnly': True,
        'activeOutageCommerceClosed': True,
    }, ensure_ascii=False))


if __name__ == '__main__':
    main()
