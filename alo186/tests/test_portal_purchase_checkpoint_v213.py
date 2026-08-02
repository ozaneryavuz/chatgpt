from __future__ import annotations

import importlib.util
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / 'alo186' / 'deployment' / 'inject_portal_purchase_checkpoint_v213.py'
spec = importlib.util.spec_from_file_location('portal_purchase_checkpoint_v213', MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


def seed(site: Path) -> None:
    portal = site / 'elektrik-portali'
    portal.mkdir(parents=True)
    html = '''<!doctype html><html lang="tr"><head><meta charset="utf-8"></head><body><main>
<section><h2>Enerji ihtiyacı hesaplayıcı</h2><a href="https://www.amazon.com.tr/s?k=ups">142 Wh için uygun sınıfı incele</a></section>
<section><h2>Elektrik ürünlerini karşılaştır</h2>
<a href="https://www.amazon.com.tr/s?k=mini+ups" target="_blank" rel="sponsored noopener">Amazon’da Modem için mini UPS seçeneklerini karşılaştır</a>
<a href="https://www.amazon.com.tr/s?k=enerji+olcer">Amazon’da Priz tipi enerji ölçer seçeneklerini karşılaştır</a>
</section>
<section><h2>Rehberlerinizi seçin</h2></section>
</main></body></html>'''
    (portal / 'index.html').write_text(html, encoding='utf-8')
    (site / 'pages-release.json').write_text(json.dumps({'version': 1}), encoding='utf-8')
    (site / 'checksums.sha256').write_text('placeholder\n', encoding='utf-8')


def assert_page(text: str, base_path: str = '') -> None:
    assert text.count('<section class="portal-purchase-checkpoint" ' + module.MARKER) == 1
    assert text.count('data-portal-lane=') == 3
    assert text.count('data-portal-retest=') == 3
    assert 'Mevcut güvenli çözüm gerçek testte yeterliyse yeni ürün almayın.' in text
    assert 'ALO186 ürün satıcısı, EDAŞ veya kamu kurumu değildir.' in text
    assert 'Fiyat, stok, puan, satıcı ve garanti yayımlanmaz.' in text
    assert 'portal_purchase_checkpoint_view' in text
    assert 'portal_purchase_checkpoint_click' in text
    assert 'portal_purchase_retest_download' in text
    assert 'BEGIN:VCALENDAR' in text
    section = text[text.index('<section class="portal-purchase-checkpoint"'):text.index('Elektrik ürünlerini karşılaştır')]
    assert 'amazon.com.tr/' not in section.lower()
    assert 'amzn.to/' not in section.lower()
    expected = f'{base_path}/amazon-elektrik-urunleri/modem-ont-mini-ups-yedekleme-secici/' if base_path else '/amazon-elektrik-urunleri/modem-ont-mini-ups-yedekleme-secici/'
    assert expected in text
    assert text.index(module.MARKER) < text.index('Elektrik ürünlerini karşılaştır')
    assert 'Product' not in text
    assert 'Offer' not in text
    assert 'AggregateRating' not in text


def run_case(base_path: str) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        site = Path(tmp)
        seed(site)
        first = module.inject(site, base_path)
        assert first['ok'] is True
        assert first['version'] == 213
        assert first['injected'] is True
        assert first['directAmazonLinksObservedBeforeCheckpoint'] == 3
        assert first['directAmazonLinksChanged'] is False
        assert first['taskLaneCount'] == 3
        assert_page((site / module.TARGET).read_text(encoding='utf-8'), base_path)
        release = json.loads((site / 'pages-release.json').read_text(encoding='utf-8'))
        checkpoint = release['portalPurchaseCheckpoint']
        assert checkpoint['version'] == 213
        assert checkpoint['directAmazonLinksObservedBeforeCheckpoint'] == 3
        assert checkpoint['directAmazonLinksChanged'] is False
        assert checkpoint['directAmazonLinksInModule'] == 0
        assert checkpoint['affiliateDisclosureVisible'] is True
        assert checkpoint['noBuyVisible'] is True
        assert checkpoint['unsafeEquipmentBlockVisible'] is True
        assert checkpoint['retestReminder'] == 'ics_30_days'
        second = module.inject(site, base_path)
        assert second['injected'] is False
        assert second['directAmazonLinksObservedBeforeCheckpoint'] == 3
        assert second['directAmazonLinksChanged'] is False
        assert_page((site / module.TARGET).read_text(encoding='utf-8'), base_path)


def test_missing_portal_fails_closed() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        site = Path(tmp)
        try:
            module.inject(site, '')
        except FileNotFoundError:
            return
        raise AssertionError('Eksik portal artifactı fail-closed durmadı')


if __name__ == '__main__':
    run_case('')
    run_case('/chatgpt')
    run_case('/preview/alo186')
    test_missing_portal_fails_closed()
    print('ALO186 portal purchase checkpoint v213: PASS')
