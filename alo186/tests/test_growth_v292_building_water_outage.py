#!/usr/bin/env python3
from __future__ import annotations
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARTICLE = ROOT / 'alo186/haberler/elektrik-kesilince-apartmanda-su-kesilir-mi-hidrofor-calisir-mi/index.html'
TOOL = ROOT / 'alo186/hesaplama/apartman-hidrofor-elektrik-kesintisi-su-plani/index.html'
GUIDE = ROOT / 'alo186/sektor-rehberi/apartman-site-otel-hidrofor-su-surekliligi/index.html'
OVERLAY = ROOT / 'alo186/deployment/routing-overlays/growth-v292-building-water-outage.json'
DECISION = ROOT / 'alo186/deployment/affiliate-category-decisions/building-water-outage-v292.json'
POLICY = ROOT / 'alo186/deployment/affiliate_route_risk_policy_v265.json'

ROUTES = {
    ARTICLE: 'https://alo186.com/haberler/elektrik-kesilince-apartmanda-su-kesilir-mi-hidrofor-calisir-mi/',
    TOOL: 'https://alo186.com/hesaplama/apartman-hidrofor-elektrik-kesintisi-su-plani/',
    GUIDE: 'https://alo186.com/sektor-rehberi/apartman-site-otel-hidrofor-su-surekliligi/',
}

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
        '"availability":',
        '"warranty":',
        'href="https://www.amazon.com.tr',
        'href="https://amzn.to',
    ):
        assert bad not in html, (path, bad)
    return html

def main() -> None:
    article = check_page(ARTICLE, ROUTES[ARTICLE])
    tool = check_page(TOOL, ROUTES[TOOL])
    guide = check_page(GUIDE, ROUTES[GUIDE])

    for required in (
        'Hidrofor enerji olmadan basınç üretemez',
        'Mevcut sistem yeterliyse yeni ürün almayın',
        '/hesaplama/apartman-hidrofor-elektrik-kesintisi-su-plani/',
        '/sektor-rehberi/apartman-site-otel-hidrofor-su-surekliligi/',
        'Bu rehberde doğrudan mağaza bağlantısı yoktur',
        'Bağımsız bilgilendirme platformudur; EDAŞ, belediye, su idaresi, üretici, servis, satıcı veya kamu kurumu değildir.',
    ):
        assert required in article, required

    for required in (
        'Ücretsiz · kişisel veri yok · mağaza bağlantısı yok',
        'Mevcut plan yeterli — yeni ürün almayın',
        '30 günlük kaçak, alarm ve pano göstergesi kontrolü',
        '90 günlük kontrollü su sürekliliği testi',
        '365 günlük bakım ve enerji verimliliği incelemesi',
        'Bu araçta Amazon veya başka mağaza bağlantısı yoktur',
        'Ticari yol kapalı',
        'Hidroforu tüketici UPS’i',
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
        'type="text"',
    ):
        assert bad not in tool, bad

    for required in (
        'Professional-only süreklilik rehberi',
        'Hidrofor, pompa, pompa panosu, motor sürücüsü, kontaktör, basınç şalteri, sabit UPS, jeneratör ve transfer sistemi consumer affiliate kapsamına açılmadı.',
        'Mevcut sistem yeterliyse yeni ürün almayın',
        'Amazon Türkiye satış ortaklığı',
        'Aktif taşkın veya elektrik tehlikesinde test yapmayın',
    ):
        assert required in guide, required

    overlay = json.loads(txt(OVERLAY))
    assert overlay['version'] == 292
    assert overlay['name'] == 'growth-v292-building-water-outage'
    assert len(overlay['routes']) == 3
    assert {item['canonicalPath'] for item in overlay['routes']} == {
        '/haberler/elektrik-kesilince-apartmanda-su-kesilir-mi-hidrofor-calisir-mi/',
        '/hesaplama/apartman-hidrofor-elektrik-kesintisi-su-plani/',
        '/sektor-rehberi/apartman-site-otel-hidrofor-su-surekliligi/',
    }

    decision = json.loads(txt(DECISION))
    assert decision['version'] == 292
    assert decision['decision'] == 'decision-first-professional-led'
    assert decision['consumerAffiliateDecision']['newMerchantLinksAllowed'] is False
    expected = {
        'newMerchantLinks': False,
        'professionalScopeForHydrophoreAndFixedPower': True,
        'noBuyOutcomeRequired': True,
        'activeHazardCommerceClosed': True,
        'activeLeakCommerceClosed': True,
        'dryRunCommerceClosed': True,
        'personalDataCollectionForbidden': True,
        'noPriceStockRatingWarrantyClaims': True,
        'affiliateDisclosureRequiredBeforeAnyDownstreamMerchantLink': True,
        'officialInstitutionImpressionForbidden': True,
    }
    for key, value in expected.items():
        assert decision['conversionPolicy'][key] is value, (key, decision['conversionPolicy'][key])
    assert len(decision['professionalOnlyClasses']) >= 8
    assert [item['days'] for item in decision['repeatVisitReasons'] if 'days' in item] == [30, 90, 365]

    policy = json.loads(txt(POLICY))
    for pattern in ('hidrofor', 'pompa', 'jenerator', 'ats', 'sabit-tesisat'):
        assert pattern in policy['professionalLeadOnlyRoutePatterns'], pattern
    assert 'pilli-su-kacagi-alarmi' in policy['governedAffiliateRoutePatterns']

    print(json.dumps({
        'ok': True,
        'version': 292,
        'newRoutes': 3,
        'newMerchantLinks': 0,
        'professionalClasses': len(decision['professionalOnlyClasses']),
        'repeatVisitDays': [30, 90, 365],
        'personalDataFields': 0,
    }, ensure_ascii=False))

if __name__ == '__main__':
    main()
