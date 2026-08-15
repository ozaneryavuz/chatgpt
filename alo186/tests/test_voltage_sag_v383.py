from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
GUIDE = ROOT / 'alo186/haberler/evde-voltaj-dusuyor-isiklar-karariyor-ne-yapmali/index.html'
TOOL = ROOT / 'alo186/hesaplama/ev-voltaj-dusmesi-dalgalanma-belirti-ayirici/index.html'
BIZ = ROOT / 'alo186/sektor-rehberi/otel-isletme-gerilim-dusmesi-guc-kalitesi-kabul/index.html'
ROUTES = ROOT / 'alo186/deployment/routing-overlays/voltage-sag-v383.json'
GOV = ROOT / 'alo186/deployment/affiliate-category-decisions/voltage-sag-v383.json'

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
    'yeni ürün almayın',
    'stabilizatör',
    'gerilim',
    'güç kalitesi',
):
    assert phrase.lower() in lower, phrase

for merchant in ('amazon.com.tr', 'amzn.to'):
    assert merchant not in lower, merchant

for storage_or_network in ('fetch(', 'localstorage', 'sessionstorage', 'geolocation'):
    assert storage_or_network not in tool.lower(), storage_or_network

assert 'tek voltaj ölçümü' in guide.lower()
assert 'ticari yolu durdurun' in tool.lower()
assert 'saha ölçümü ve resmî kabul yerine geçmez' in biz.lower()
assert 'consumer affiliate' in biz.lower()

routes = json.loads(ROUTES.read_text(encoding='utf-8'))
assert routes['version'] == 383
assert len(routes['routes']) == 3
assert {r['canonicalPath'] for r in routes['routes']} == {
    '/haberler/evde-voltaj-dusuyor-isiklar-karariyor-ne-yapmali/',
    '/hesaplama/ev-voltaj-dusmesi-dalgalanma-belirti-ayirici/',
    '/sektor-rehberi/otel-isletme-gerilim-dusmesi-guc-kalitesi-kabul/',
}

gov = json.loads(GOV.read_text(encoding='utf-8'))
assert gov['version'] == 383
assert gov['newAffiliateClasses'] == 0
assert gov['newMerchantLinks'] == 0
for key in ('unverified-price', 'unverified-stock', 'unverified-rating', 'unverified-warranty'):
    assert key in gov['mustNotClaim']

print({'ok': True, 'version': 383, 'routes': 3, 'merchantLinks': 0, 'newAffiliateClasses': 0})
