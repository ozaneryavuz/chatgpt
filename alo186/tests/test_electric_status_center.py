from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PAGE = ROOT / 'alo186/elektrik-durum-merkezi/index.html'
APP = ROOT / 'alo186/elektrik-durum-merkezi/app.js'
STYLE = ROOT / 'alo186/elektrik-durum-merkezi/styles.css'
OVERLAY = ROOT / 'alo186/deployment/routing-overlays/electric-status-center-run23.json'


def main():
    html = PAGE.read_text(encoding='utf-8')
    app = APP.read_text(encoding='utf-8')
    css = STYLE.read_text(encoding='utf-8')
    overlay = OVERLAY.read_text(encoding='utf-8')

    for token in [
        'rel="canonical" href="https://www.alo186.com/elektrik-durum-merkezi"',
        '"@type":"WebApplication"',
        '"@type":"FAQPage"',
        '"@type":"BreadcrumbList"',
        'ALO186 arıza kaydı almaz',
        'kişisel veri',
        '112',
        '186',
    ]:
        assert token in html, token

    for forbidden in ['type="email"', 'type="tel"', 'type="text"', 'amazon.com.tr', 'priceCurrency":"USD"']:
        assert forbidden not in html, forbidden

    for token in [
        'alo186.electricStatus.v1',
        'localStorage',
        'JSON.stringify',
        'tel:112',
        '/edas-bul',
        '/karar-motoru',
        '/hesaplama/kesinti-gunlugu/',
        '/kurumsal-elektrik-surekliligi-on-degerlendirme',
    ]:
        assert token in app, token

    assert 'max-width:760px' in css
    assert 'min-height:50px' in css
    assert '"version": 74' in overlay
    assert '"type": "tool"' in overlay
    assert '"canonicalPath": "/elektrik-durum-merkezi"' in overlay
    print('ALO186 Elektrik Durum Merkezi kalite sözleşmeleri başarılı.')


if __name__ == '__main__':
    main()
