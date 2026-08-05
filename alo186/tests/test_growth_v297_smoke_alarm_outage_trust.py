#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARTICLE = ROOT / 'alo186/haberler/elektrik-kesilince-duman-dedektoru-calisir-mi/index.html'
TOOL = ROOT / 'alo186/hesaplama/duman-karbonmonoksit-alarmi-elektrik-kesintisi-kontrolu/index.html'
SELECTOR = ROOT / 'alo186/amazon-elektrik-urunleri/duman-alarmi-pil-yedegi-kesinti-hazirligi/index.html'
OVERLAY = ROOT / 'alo186/deployment/routing-overlays/growth-v297-smoke-alarm-outage-trust.json'
DECISION = ROOT / 'alo186/deployment/affiliate-category-decisions/smoke-alarm-outage-v297.json'
POLICY = ROOT / 'alo186/deployment/affiliate_route_risk_policy_v265.json'
ROUTES = {
    ARTICLE: 'https://alo186.com/haberler/elektrik-kesilince-duman-dedektoru-calisir-mi/',
    TOOL: 'https://alo186.com/hesaplama/duman-karbonmonoksit-alarmi-elektrik-kesintisi-kontrolu/',
    SELECTOR: 'https://alo186.com/amazon-elektrik-urunleri/duman-alarmi-pil-yedegi-kesinti-hazirligi/',
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
        'Alarmın güç türünü ayırın; ışığı veya uygulamayı değil, gerçek alarm işlevini test edin.',
        'Pille çalışan bağımsız duman alarmı',
        'Alarm çalıyorsa alışveriş veya test yapmayın',
        'Mevcut alarm yeterliyse yeni ürün almayın',
        '/hesaplama/duman-karbonmonoksit-alarmi-elektrik-kesintisi-kontrolu/',
        '/amazon-elektrik-urunleri/duman-alarmi-pil-yedegi-kesinti-hazirligi/',
        'ALO186 bağımsız bilgilendirme platformudur.',
    ):
        assert required in article, required
    assert 'amazon.com.tr' not in article.casefold()

    for required in (
        'Ücretsiz · kişisel veri yok · mağaza bağlantısı yok',
        'Mevcut alarm yeterli — yeni ürün almayın',
        'Aktif alarm, duman, gaz veya belirti varsa test ve ticari yol kapalıdır',
        'Bu araçta Amazon veya başka mağaza bağlantısı yoktur',
        '30 gün',
        '180 gün',
        '365 gün',
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
        'Aktif tehlike ve merkezi sistemde mağaza yolu kapalıdır',
        'Bağlantılar kilitli',
        'rel="sponsored nofollow noopener"',
        'Fiyat, stok, satıcı, puan, yorum, teslimat ve garanti bilgisi ALO186 tarafından yayımlanmaz',
        'yalnız gelecekteki hazırlık yapıyorum',
    ):
        assert required in selector, required
    assert 'href="https://www.amazon.com.tr' not in selector.casefold()
    assert 'data-url="https://www.amazon.com.tr' not in selector.casefold()
    parser = AnchorParser()
    parser.feed(selector)
    product_ids = {'opticalLink', 'sealedLink', 'batteryLink'}
    product_anchors = [anchor for anchor in parser.anchors if anchor.get('id') in product_ids]
    assert len(product_anchors) == 3
    for anchor in product_anchors:
        assert not anchor.get('href')
        assert {'sponsored', 'nofollow', 'noopener'}.issubset(set(anchor.get('rel', '').split()))
        assert anchor.get('aria-disabled') == 'true'

    overlay = json.loads(txt(OVERLAY))
    assert overlay['version'] == 297
    assert overlay['name'] == 'growth-v297-smoke-alarm-outage-trust'
    assert len(overlay['routes']) == 3
    assert {item['canonicalPath'] for item in overlay['routes']} == {
        '/haberler/elektrik-kesilince-duman-dedektoru-calisir-mi/',
        '/hesaplama/duman-karbonmonoksit-alarmi-elektrik-kesintisi-kontrolu/',
        '/amazon-elektrik-urunleri/duman-alarmi-pil-yedegi-kesinti-hazirligi/',
    }

    decision = json.loads(txt(DECISION))
    assert decision['version'] == 297
    assert decision['decision'] == 'guarded-low-risk-consumer-affiliate'
    expected = {
        'newMerchantLinks': True,
        'linksLockedByDefault': True,
        'futurePreparednessOnly': True,
        'noBuyOutcomeRequired': True,
        'activeHazardCommerceClosed': True,
        'centralSystemCommerceClosed': True,
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
    assert [item['days'] for item in decision['repeatVisitReasons']] == [30, 180, 365]

    policy = json.loads(txt(POLICY))
    assert 'duman-alarmi-pil-yedegi-kesinti-hazirligi' in policy['governedAffiliateRoutePatterns']
    for pattern in ('yangin-alarmi', 'yangin-algilama', 'yangin-paneli'):
        assert pattern in policy['professionalLeadOnlyRoutePatterns']

    print(json.dumps({
        'ok': True,
        'version': 297,
        'newRoutes': 3,
        'initialActiveMerchantLinks': 0,
        'guardedProductClasses': 3,
        'repeatVisitDays': [30, 180, 365],
        'futurePreparednessOnly': True,
        'activeHazardCommerceClosed': True,
        'centralSystemCommerceClosed': True,
    }, ensure_ascii=False))


if __name__ == '__main__':
    main()
