from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
GUIDE = ROOT / 'alo186/haberler/evde-voltaj-dusuyor-isiklar-karariyor-ne-yapmali/index.html'
TOOL = ROOT / 'alo186/hesaplama/ev-voltaj-dusmesi-dalgalanma-belirti-ayirici/index.html'
BIZ = ROOT / 'alo186/sektor-rehberi/otel-isletme-gerilim-dusmesi-guc-kalitesi-kabul/index.html'
ROUTES = ROOT / 'alo186/deployment/routing-overlays/voltage-sag-v383.json'
GOV = ROOT / 'alo186/deployment/affiliate-category-decisions/voltage-sag-v383.json'

for path in (GUIDE, TOOL, BIZ, ROUTES, GOV):
    assert path.is_file(), f'missing required file: {path}'

guide = GUIDE.read_text(encoding='utf-8')
tool = TOOL.read_text(encoding='utf-8')
biz = BIZ.read_text(encoding='utf-8')
all_html = '\n'.join((guide, tool, biz))
lower = all_html.casefold()

required_terms = (
    'alo186',
    'resmî',
    'affiliate',
    'yeni ürün almayın',
    'stabilizatör',
    'gerilim',
    'güç kalitesi',
)
for term in required_terms:
    assert term.casefold() in lower, f'missing trust/content term: {term}'

for merchant in ('amazon.com.tr', 'amzn.to'):
    assert merchant not in lower, f'merchant link leaked into no-commerce cluster: {merchant}'

for storage_or_network in ('fetch(', 'localstorage', 'sessionstorage', 'geolocation'):
    assert storage_or_network not in tool.casefold(), f'privacy/network primitive found: {storage_or_network}'

assert 'tek bir voltaj ölçümü' in guide.casefold(), 'single-reading warning missing'
assert 'ticari yolu durdurun' in tool.casefold(), 'active-hazard commercial closure missing'
assert 'saha ölçümü ve resmî kabul yerine geçmez' in biz.casefold(), 'professional acceptance disclaimer missing'
assert 'consumer affiliate' in biz.casefold(), 'consumer affiliate closure missing'

routes = json.loads(ROUTES.read_text(encoding='utf-8'))
assert routes.get('version') == 383
assert len(routes.get('routes', [])) == 3
expected_routes = {
    '/haberler/evde-voltaj-dusuyor-isiklar-karariyor-ne-yapmali/',
    '/hesaplama/ev-voltaj-dusmesi-dalgalanma-belirti-ayirici/',
    '/sektor-rehberi/otel-isletme-gerilim-dusmesi-guc-kalitesi-kabul/',
}
assert {r.get('canonicalPath') for r in routes['routes']} == expected_routes

gov = json.loads(GOV.read_text(encoding='utf-8'))
assert gov.get('version') == 383
assert gov.get('newAffiliateClasses') == 0
assert gov.get('newMerchantLinks') == 0
claims = set(gov.get('mustNotClaim', []))
for key in ('unverified-price', 'unverified-stock', 'unverified-rating', 'unverified-warranty'):
    assert key in claims, f'missing governance claim guard: {key}'

print({'ok': True, 'version': 383, 'routes': 3, 'merchantLinks': 0, 'newAffiliateClasses': 0})
