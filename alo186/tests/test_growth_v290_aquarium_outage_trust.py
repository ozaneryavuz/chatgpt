#!/usr/bin/env python3
from __future__ import annotations
import json
import re
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARTICLE = ROOT / 'alo186/haberler/elektrik-kesilince-akvaryum-baligi-ne-yapilir/index.html'
TOOL = ROOT / 'alo186/hesaplama/akvaryum-elektrik-kesintisi-oksijen-sicaklik-plani/index.html'
SELECTOR = ROOT / 'alo186/amazon-elektrik-urunleri/akvaryum-kesinti-hava-pompasi-termometre-secici/index.html'
OVERLAY = ROOT / 'alo186/deployment/routing-overlays/growth-v290-aquarium-outage-trust.json'
DECISION = ROOT / 'alo186/deployment/affiliate-category-decisions/aquarium-outage-v290.json'
POLICY = ROOT / 'alo186/deployment/affiliate_route_risk_policy_v265.json'
ROUTES = {
    ARTICLE: 'https://alo186.com/haberler/elektrik-kesilince-akvaryum-baligi-ne-yapilir/',
    TOOL: 'https://alo186.com/hesaplama/akvaryum-elektrik-kesintisi-oksijen-sicaklik-plani/',
    SELECTOR: 'https://alo186.com/amazon-elektrik-urunleri/akvaryum-kesinti-hava-pompasi-termometre-secici/',
}

class AnchorParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.anchors: list[dict[str, str]] = []
    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.casefold() == 'a':
            self.anchors.append({k.casefold(): v or '' for k, v in attrs})

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
    for bad in ('https://www.alo186.com', '"@type":"Offer"', '"@type":"AggregateRating"', '"@type":"Review"', '"price":', '"availability":', '"warranty":'):
        assert bad not in html, (path, bad)
    return html

def main() -> None:
    article = check_page(ARTICLE, ROUTES[ARTICLE])
    tool = check_page(TOOL, ROUTES[TOOL])
    selector = check_page(SELECTOR, ROUTES[SELECTOR])

    for required in (
        'Kesintide öncelik ışık değil; güvenli oksijenlenme, kararlı sıcaklık ve su kalitesidir.',
        'Mevcut plan yeterliyse yeni ürün almayın',
        '/hesaplama/akvaryum-elektrik-kesintisi-oksijen-sicaklik-plani/',
        '/amazon-elektrik-urunleri/akvaryum-kesinti-hava-pompasi-termometre-secici/',
        'Bağımsız bilgilendirme platformudur; EDAŞ, veteriner kliniği, ürün üreticisi, satıcı veya kamu kurumu değildir.',
    ):
        assert required in article, required
    assert 'amazon.com.tr' not in article.casefold()

    for required in (
        'Ücretsiz · kişisel veri yok · mağaza bağlantısı yok',
        'Mevcut plan yeterli — yeni ürün almayın',
        '30 günlük akvaryum yedek kontrolü',
        '90 günlük kesinti provası',
        '180 günlük mevsimlik sıcaklık planı',
        'Bu araçta Amazon veya başka mağaza bağlantısı yoktur',
        'Ticari yol kapalı',
    ):
        assert required in tool, required
    for bad in ('fetch(', 'XMLHttpRequest', 'localStorage.', 'sessionStorage.', 'document.cookie', 'type="email"', 'type="tel"'):
        assert bad not in tool, bad
    assert 'amazon.com.tr' not in tool.casefold()

    for required in (
        'Amazon Türkiye satış ortaklığı',
        'Satın almama geçerli sonuçtur',
        'yeni ürün almayacağım',
        'Aktif tehlike veya canlı sıkıntısında mağaza yolu kapalıdır',
        'Bağlantılar kilitli',
        'rel="sponsored nofollow noopener"',
        'Fiyat, stok, satıcı, puan, yorum, teslimat ve garanti bilgisi ALO186 tarafından yayımlanmaz',
    ):
        assert required in selector, required
    assert 'href="https://www.amazon.com.tr' not in selector.casefold()
    assert 'data-url="https://www.amazon.com.tr' not in selector.casefold()
    parser = AnchorParser(); parser.feed(selector)
    product_ids = {'batteryLink', 'usbLink', 'tempLink'}
    product_anchors = [a for a in parser.anchors if a.get('id') in product_ids]
    assert len(product_anchors) == 3
    for anchor in product_anchors:
        assert not anchor.get('href')
        assert {'sponsored', 'nofollow', 'noopener'}.issubset(set(anchor.get('rel', '').split()))
        assert anchor.get('aria-disabled') == 'true'

    overlay = json.loads(txt(OVERLAY))
    assert overlay['version'] == 290
    assert overlay['name'] == 'growth-v290-aquarium-outage-trust'
    assert len(overlay['routes']) == 1
    assert overlay['routes'][0]['canonicalPath'] == '/haberler/elektrik-kesilince-akvaryum-baligi-ne-yapilir/'
    assert set(overlay['updatedExistingRoutes']) == {
        '/hesaplama/akvaryum-elektrik-kesintisi-oksijen-sicaklik-plani/',
        '/amazon-elektrik-urunleri/akvaryum-kesinti-hava-pompasi-termometre-secici/',
    }

    decision = json.loads(txt(DECISION))
    assert decision['version'] == 290
    assert decision['decision'] == 'guarded-low-risk-consumer-affiliate'
    expected = {
        'newMerchantLinks': True,
        'linksLockedByDefault': True,
        'noBuyOutcomeRequired': True,
        'activeHazardCommerceClosed': True,
        'animalDistressCommerceClosed': True,
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
    assert len(decision['excludedProfessionalOrHealthClasses']) >= 4
    assert [item['days'] for item in decision['repeatVisitReasons'] if 'days' in item] == [30, 90, 180]

    policy = json.loads(txt(POLICY))
    assert 'akvaryum-kesinti-hava-pompasi-termometre-secici' in policy['governedAffiliateRoutePatterns']

    print(json.dumps({
        'ok': True,
        'version': 290,
        'newRoutes': 1,
        'updatedRoutes': 2,
        'initialActiveMerchantLinks': 0,
        'guardedProductClasses': 3,
        'repeatVisitDays': [30, 90, 180],
        'actualSelectorGoverned': True,
    }, ensure_ascii=False))

if __name__ == '__main__':
    main()
