#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARTICLE = ROOT / 'alo186/haberler/elektrik-kesilince-bodrum-drenaj-pompasi-calisir-mi/index.html'
TOOL = ROOT / 'alo186/hesaplama/bodrum-drenaj-pompasi-elektrik-kesintisi-su-baskini-plani/index.html'
GUIDE = ROOT / 'alo186/sektor-rehberi/apartman-otel-bodrum-drenaj-pompasi-kesinti-surekliligi/index.html'
OVERLAY = ROOT / 'alo186/deployment/routing-overlays/growth-v298-drainage-pump-outage-trust.json'
DECISION = ROOT / 'alo186/deployment/affiliate-category-decisions/drainage-pump-outage-v298.json'
POLICY = ROOT / 'alo186/deployment/affiliate_route_risk_policy_v265.json'
ROUTES = {
    ARTICLE: 'https://alo186.com/haberler/elektrik-kesilince-bodrum-drenaj-pompasi-calisir-mi/',
    TOOL: 'https://alo186.com/hesaplama/bodrum-drenaj-pompasi-elektrik-kesintisi-su-baskini-plani/',
    GUIDE: 'https://alo186.com/sektor-rehberi/apartman-otel-bodrum-drenaj-pompasi-kesinti-surekliligi/',
}


def read(path: Path) -> str:
    assert path.is_file(), path
    return path.read_text(encoding='utf-8')


def check_page(path: Path, canonical: str) -> str:
    html = read(path)
    assert re.findall(r'<link\s+rel="canonical"\s+href="([^"]+)"', html, re.I) == [canonical]
    blocks = re.findall(r'<script\s+type="application/ld\+json">(.*?)</script>', html, re.I | re.S)
    assert blocks, path
    for block in blocks:
        json.loads(block)
    for bad in (
        '"@type":"Offer"', '"@type":"AggregateRating"', '"@type":"Review"',
        '"price":', '"priceCurrency":', '"availability":', '"warranty":', '"delivery":',
    ):
        assert bad not in html, (path, bad)
    return html


def main() -> None:
    article = check_page(ARTICLE, ROUTES[ARTICLE])
    tool = check_page(TOOL, ROUTES[TOOL])
    guide = check_page(GUIDE, ROUTES[GUIDE])

    for required in (
        'Pompanın enerjisini değil, suyun gerçekten tahliye edildiği bütün zinciri doğrulayın.',
        'Aktif su baskınında test veya alışveriş yapmayın',
        'Mevcut sistem yeterliyse yeni ürün almayın',
        'Bu rehberde Amazon veya başka mağaza bağlantısı yoktur',
        '/hesaplama/bodrum-drenaj-pompasi-elektrik-kesintisi-su-baskini-plani/',
        '/sektor-rehberi/apartman-otel-bodrum-drenaj-pompasi-kesinti-surekliligi/',
        'ALO186 bağımsız bilgilendirme platformudur.',
    ):
        assert required in article, required
    assert 'amazon.com.tr' not in article.casefold()

    for required in (
        'Ücretsiz · kişisel veri yok · mağaza bağlantısı yok',
        'Aktif su-elektrik tehlikesinde aracı kullanmayı bırakın',
        'Mevcut sistem yeterli — yeni ürün almayın',
        'Professional-only değerlendirme',
        'Bu araçta Amazon veya başka mağaza bağlantısı yoktur',
        '7', '30', '90',
    ):
        assert required in tool, required
    for bad in ('fetch(', 'XMLHttpRequest', 'localStorage.', 'sessionStorage.', 'document.cookie', 'type="email"', 'type="tel"'):
        assert bad not in tool, bad
    assert 'amazon.com.tr' not in tool.casefold()

    for required in (
        'Professional-only · sıfır tüketici affiliate',
        'Aktif taşkında ticari dönüşüm yoktur',
        'Süreklilik matrisi',
        'Tek hata noktasını bulun',
        'Gerçek kabul testi',
        'Dönüşüm noktaları',
        'Bu sayfada Amazon veya başka mağaza bağlantısı yoktur',
        'ALO186; EDAŞ, AFAD, belediye, itfaiye',
    ):
        assert required in guide, required
    assert 'amazon.com.tr' not in guide.casefold()

    overlay = json.loads(read(OVERLAY))
    assert overlay['version'] == 298
    assert overlay['name'] == 'growth-v298-drainage-pump-outage-trust'
    assert len(overlay['routes']) == 3
    assert {item['canonicalPath'] for item in overlay['routes']} == {
        '/haberler/elektrik-kesilince-bodrum-drenaj-pompasi-calisir-mi/',
        '/hesaplama/bodrum-drenaj-pompasi-elektrik-kesintisi-su-baskini-plani/',
        '/sektor-rehberi/apartman-otel-bodrum-drenaj-pompasi-kesinti-surekliligi/',
    }

    decision = json.loads(read(DECISION))
    assert decision['version'] == 298
    assert decision['decision'] == 'professional-lead-only'
    assert decision['newMerchantLinks'] == 0
    for key in (
        'activeFloodCommerceClosed', 'waterElectricalHazardCommerceClosed',
        'fixedPumpConsumerAffiliateClosed', 'generatorAndTransferConsumerAffiliateClosed',
        'sewageSystemConsumerAffiliateClosed', 'noBuyOutcomeRequired',
        'personalDataCollectionForbidden', 'noPriceStockRatingWarrantyClaims',
        'affiliateDisclosureRequiredBeforeAnyFutureMerchantLink',
        'officialInstitutionImpressionForbidden', 'professionalScopeForComplexSystems',
    ):
        assert decision['conversionPolicy'][key] is True, key
    assert len(decision['professionalClasses']) >= 8
    assert [item['days'] for item in decision['repeatVisitReasons']] == [7, 30, 180]

    policy = json.loads(read(POLICY))
    patterns = set(policy['professionalLeadOnlyRoutePatterns'])
    for pattern in ('pompa', 'sabit-tesisat', 'jenerator', 'ats'):
        assert pattern in patterns, pattern

    print(json.dumps({
        'ok': True,
        'version': 298,
        'newRoutes': 3,
        'newMerchantLinks': 0,
        'professionalClasses': len(decision['professionalClasses']),
        'repeatVisitDays': [7, 30, 180],
        'activeFloodCommerceClosed': True,
        'noBuyOutcomeRequired': True,
        'personalDataFields': 0,
    }, ensure_ascii=False))


if __name__ == '__main__':
    main()
