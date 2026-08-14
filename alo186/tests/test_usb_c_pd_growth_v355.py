from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
ARTICLE = ROOT / 'haberler/usb-c-kablo-kac-watt-60w-240w-pd-farki/index.html'
TOOL = ROOT / 'hesaplama/usb-c-pd-sarj-kablo-uygunluk/index.html'
APP = ROOT / 'hesaplama/usb-c-pd-sarj-kablo-uygunluk/app.js'
OVERLAY = ROOT / 'deployment/routing-overlays/355-usb-c-pd-growth.json'
POLICY = ROOT / 'deployment/affiliate-category-decisions/usb-c-pd-v355.json'

article = ARTICLE.read_text(encoding='utf-8')
tool = TOOL.read_text(encoding='utf-8')
app = APP.read_text(encoding='utf-8')
overlay = json.loads(OVERLAY.read_text(encoding='utf-8'))
policy = json.loads(POLICY.read_text(encoding='utf-8'))

assert overlay['version'] == 355
assert len(overlay['routes']) == 2
assert 'https://alo186.com/haberler/usb-c-kablo-kac-watt-60w-240w-pd-farki/' in article
assert 'https://alo186.com/hesaplama/usb-c-pd-sarj-kablo-uygunluk/' in tool
assert '"@type":"Article"' in article
assert '"@type":"WebApplication"' in tool
assert '"@type":"BreadcrumbList"' in article and '"@type":"BreadcrumbList"' in tool
assert 'amazon.com.tr' not in article.lower()
assert 'amazon.com.tr' not in tool.lower()
assert 'amazon.com.tr' in app.lower()
assert 'alo186rehber-21' in app
assert 'sponsored nofollow noopener' in app
assert 'Mevcut güvenli çözüm ihtiyacınızı karşılıyorsa yeni şarj cihazı veya kablo almayın.' in app
assert 'Fiyat, stok, puan' in tool
assert 'fiyat' in json.dumps(policy, ensure_ascii=False).lower()
assert policy['defaultDecision'] == 'closed'
assert 'medical or life-safety use' in policy['alwaysClosedFor']
for banned in ('"@type":"Offer"', 'AggregateRating'):
    assert banned not in article
    assert banned not in tool
for claim in ('% indirim', 'en ucuz', 'stokta', 'yıldız'):
    assert claim not in article.lower()
    assert claim not in tool.lower()
print('ALO186 USB-C PD growth v355: PASS')
