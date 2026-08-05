#!/usr/bin/env python3
from __future__ import annotations
import json
import re
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARTICLE = ROOT / 'alo186/haberler/elektrik-kesilince-otomatik-sulama-programi-silinir-mi/index.html'
TOOL = ROOT / 'alo186/hesaplama/otomatik-sulama-elektrik-kesintisi-plani/index.html'
SELECTOR = ROOT / 'alo186/amazon-elektrik-urunleri/pilli-sulama-zamanlayici-nem-sensoru-secimi/index.html'
OVERLAY = ROOT / 'alo186/deployment/routing-overlays/growth-v291-irrigation-outage-trust.json'
DECISION = ROOT / 'alo186/deployment/affiliate-category-decisions/irrigation-outage-v291.json'
POLICY = ROOT / 'alo186/deployment/affiliate_route_risk_policy_v265.json'
ROUTES = {
    ARTICLE: 'https://alo186.com/haberler/elektrik-kesilince-otomatik-sulama-programi-silinir-mi/',
    TOOL: 'https://alo186.com/hesaplama/otomatik-sulama-elektrik-kesintisi-plani/',
    SELECTOR: 'https://alo186.com/amazon-elektrik-urunleri/pilli-sulama-zamanlayici-nem-sensoru-secimi/',
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
        'Program hafızası korunabilir; fakat saat, yarım kalan çevrim, vana ve pompa ayrı ayrı kontrol edilmelidir.',
        'Mevcut sistem yeterliyse yeni ürün almayın',
        '/hesaplama/otomatik-sulama-elektrik-kesintisi-plani/',
        '/amazon-elektrik-urunleri/pilli-sulama-zamanlayici-nem-sensoru-secimi/',
        'Bağımsız bilgilendirme platformudur; EDAŞ, su idaresi, belediye, üretici, satıcı veya kamu kurumu değildir.',
    ):
        assert required in article, required
    assert 'amazon.com.tr' not in article.casefold()

    for required in (
        'Ücretsiz · kişisel veri yok · mağaza bağlantısı yok',
        'Mevcut plan yeterli — yeni ürün almayın',
        '30 günlük pil, bağlantı ve sızıntı kontrolü',
        '90 günlük gerçek görev testi',
        '180 günlük mevsim planı gözden geçirmesi',
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
        'Aktif tehlike, sızıntı veya merkezi sistemde mağaza yolu kapalıdır',
        'Bağlantılar kilitli',
        'rel="sponsored nofollow noopener"',
        'Fiyat, stok, satıcı, puan, yorum, teslimat ve garanti bilgisi ALO186 tarafından yayımlanmaz',
    ):
        assert required in selector, required
    assert 'href="https://www.amazon.com.tr' not in selector.casefold()
    assert 'data-url="https://www.amazon.com.tr' not in selector.casefold()
    parser = AnchorParser(); parser.feed(selector)
    product_ids = {'timerLink', 'sensorLink', 'batteryLink'}
    product_anchors = [a for a in parser.anchors if a.get('id') in product_ids]
    assert len(product_anchors) == 3
    for anchor in product_anchors:
        assert not anchor.get('href')
        assert {'sponsored', 'nofollow', 'noopener'}.issubset(set(anchor.get('rel', '').split()))
        assert anchor.get('aria-disabled') == 'true'

    overlay = json.loads(txt(OVERLAY))
    assert overlay['version'] == 291
    assert overlay['name'] == 'growth-v291-irrigation-outage-trust'
    assert len(overlay['routes']) == 3
    assert {item['canonicalPath'] for item in overlay['routes']} == {
        '/haberler/elektrik-kesilince-otomatik-sulama-programi-silinir-mi/',
        '/hesaplama/otomatik-sulama-elektrik-kesintisi-plani/',
        '/amazon-elektrik-urunleri/pilli-sulama-zamanlayici-nem-sensoru-secimi/',
    }

    decision = json.loads(txt(DECISION))
    assert decision['version'] == 291
    assert decision['decision'] == 'guarded-low-risk-consumer-affiliate'
    expected = {
        'newMerchantLinks': True,
        'linksLockedByDefault': True,
        'noBuyOutcomeRequired': True,
        'activeHazardCommerceClosed': True,
        'activeLeakCommerceClosed': True,
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
    assert len(decision['excludedProfessionalOrSafetyClasses']) >= 5
    assert [item['days'] for item in decision['repeatVisitReasons']] == [30, 90, 180]

    policy = json.loads(txt(POLICY))
    assert 'pilli-sulama-zamanlayici-nem-sensoru' in policy['governedAffiliateRoutePatterns']
    for pattern in ('otomatik-sulama-kontroloru', 'solenoid-vana', 'peyzaj-sulama', 'merkezi-sulama', 'pompa-start'):
        assert pattern in policy['professionalLeadOnlyRoutePatterns']

    print(json.dumps({
        'ok': True,
        'version': 291,
        'newRoutes': 3,
        'initialActiveMerchantLinks': 0,
        'guardedProductClasses': 3,
        'repeatVisitDays': [30, 90, 180],
        'professionalBoundaries': 5,
    }, ensure_ascii=False))

if __name__ == '__main__':
    main()
