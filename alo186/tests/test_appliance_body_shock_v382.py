from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
GUIDE = ROOT / 'alo186/haberler/cihaz-govdesi-elektrik-carpiyor-ne-yapmali/index.html'
TOOL = ROOT / 'alo186/hesaplama/cihaz-govdesi-elektrik-carpmasi-guvenlik-ayirici/index.html'
BIZ = ROOT / 'alo186/sektor-rehberi/otel-isletme-cihaz-topraklama-kacak-akim-kabul/index.html'
ROUTES = ROOT / 'alo186/deployment/routing-overlays/appliance-body-shock-v382.json'
GOV = ROOT / 'alo186/deployment/affiliate-category-decisions/appliance-body-shock-v382.json'

for path in (GUIDE, TOOL, BIZ, ROUTES, GOV):
    assert path.is_file(), path

guide = GUIDE.read_text(encoding='utf-8')
tool = TOOL.read_text(encoding='utf-8')
biz = BIZ.read_text(encoding='utf-8')
all_html = '\n'.join((guide, tool, biz))
lower = all_html.lower()

for phrase in (
    'ALO186 resmî kurum',
    'Affiliate',
    'yeni cihaz',
    '112',
    'koruyucu iletken',
):
    assert phrase.lower() in lower, phrase

for merchant in ('amazon.com.tr', 'amzn.to'):
    assert merchant not in lower, merchant

for storage_or_network in ('fetch(', 'localstorage', 'sessionstorage', 'geolocation'):
    assert storage_or_network not in tool.lower(), storage_or_network

assert 'tekrar dokunarak' in lower
assert 'daha büyük' not in tool.lower()
assert 'ürün önermiyor' in tool.lower()
assert 'saha ölçümü ve resmî kabul yerine geçmez' in biz.lower()

routes = json.loads(ROUTES.read_text(encoding='utf-8'))
assert routes['version'] == 382
assert len(routes['routes']) == 3
assert {r['canonicalPath'] for r in routes['routes']} == {
    '/haberler/cihaz-govdesi-elektrik-carpiyor-ne-yapmali/',
    '/hesaplama/cihaz-govdesi-elektrik-carpmasi-guvenlik-ayirici/',
    '/sektor-rehberi/otel-isletme-cihaz-topraklama-kacak-akim-kabul/',
}

gov = json.loads(GOV.read_text(encoding='utf-8'))
assert gov['version'] == 382
assert gov['newAffiliateClasses'] == 0
assert gov['newMerchantLinks'] == 0
for key in ('unverified-price', 'unverified-stock', 'unverified-rating', 'unverified-warranty'):
    assert key in gov['mustNotClaim']

print({'ok': True, 'version': 382, 'routes': 3, 'merchantLinks': 0, 'newAffiliateClasses': 0})
