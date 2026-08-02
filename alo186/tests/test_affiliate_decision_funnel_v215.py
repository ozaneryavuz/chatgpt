from __future__ import annotations

import importlib.util
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ALO186_ROOT = HERE.parent if (HERE.parent / 'deployment').is_dir() else HERE
MODULE_PATH = ALO186_ROOT / 'deployment' / 'inject_affiliate_decision_funnel_v215.py'
if not MODULE_PATH.is_file():
    MODULE_PATH = HERE / 'inject_affiliate_decision_funnel_v215.py'
CONTRACT_PATH = ALO186_ROOT / 'audits' / 'affiliate-event-contract-v215.json'
if not CONTRACT_PATH.is_file():
    CONTRACT_PATH = HERE / 'affiliate-event-contract-v215.json'

sys.path.insert(0, str(MODULE_PATH.parent))
spec = importlib.util.spec_from_file_location('affiliate_decision_funnel_v215', MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = module
spec.loader.exec_module(module)


def seed(site: Path) -> None:
    pages = {
        module.TARGETS[0].path: '''<!doctype html><html><head><meta charset="utf-8"></head><body><main><section><h2>Etiket okuma</h2></section><section><span>Güvenli ticari rota</span><h2>Teknik ürün merkezi</h2></section></main></body></html>''',
        module.TARGETS[1].path: '''<!doctype html><html><head><meta charset="utf-8"></head><body><main><section id="results"><input id="loadW" value="100"><input id="surgeFactor" value="1.2"><select id="mode"><option value="runtime" selected>runtime</option></select><input id="batteryWh" value="1000"><input id="efficiency" value="88"><input id="dod" value="80"><input id="aging" value="90"><input id="hours" value="4"><input id="reserve" value="20"><button id="calcBtn">Hesapla</button><div id="productRoute">Ürün yolu</div></section></main></body></html>''',
        module.TARGETS[2].path: '''<!doctype html><html><head><meta charset="utf-8"></head><body><main><form id="powerStationForm"><select id="loadType"><option value="router" selected>router</option></select><select id="ownership"><option value="candidate" selected>candidate</option><option value="owned">owned</option></select><input id="continuousPowerW" value="25"><input id="surgePowerW" value="40"><input id="targetHours" value="8"><input id="capacityWh" value="500"><input id="acContinuousW" value="500"><input id="acSurgeW" value="1000"><input id="efficiency" value="0.85"><input id="reservePct" value="15"><input id="damageFree" type="checkbox" checked><input id="indoorDryVentilated" type="checkbox" checked><input id="directConnection" type="checkbox" checked><input id="labelVerified" type="checkbox" checked><input id="pureSine" type="checkbox" checked><input id="manufacturerLoadApproved" type="checkbox" checked><input id="needsEarth" type="checkbox"><input id="earthVerified" type="checkbox"><input id="unattendedUse" type="checkbox"><input id="transferRequired" type="checkbox"><input id="epsSupported" type="checkbox"><input id="requiredTransferMs" value="30"><input id="transferMs" value="20"><button type="submit">Değerlendir</button></form></main></body></html>''',
    }
    for relative, content in pages.items():
        path = site / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding='utf-8')
    (site / 'pages-release.json').write_text(json.dumps({'version': 1}), encoding='utf-8')
    (site / 'checksums.sha256').write_text('placeholder\n', encoding='utf-8')


def assert_document_closures(text: str) -> None:
    for tag in ('head', 'main', 'body'):
        assert re.search(rf'</{tag}\s*>', text, re.I), tag
    assert text.lower().find('</head') < text.lower().find('<body')
    assert text.lower().find('<main') < text.lower().rfind('</main')
    assert text.lower().rfind('</main') < text.lower().rfind('</body')


def assert_page(text: str, flow: str, base_path: str) -> None:
    assert text.count(module.MARKER) == 1
    assert f'data-decision-flow="{flow}"' in text
    assert text.count('data-decision-tier-card=') == 3
    assert text.count('data-decision-action="selector"') == 3
    assert text.count('data-decision-placement="decision_tier_card"') == 3
    assert 'Kimler için?' in text
    assert 'Uygun değil' in text
    assert 'Önce kontrol et' in text
    assert 'Mevcut çözümüm testte yeterli — yeni ürün alma' in text
    assert 'Ticari yol kapatıldı.' in text
    assert 'Fiyat, stok, puan, satıcı ve garanti burada yayımlanmaz.' in text
    assert 'amazon.com.tr/' not in text.lower()
    assert 'amzn.to/' not in text.lower()
    css = f'{base_path}/assets/affiliate-decision-funnel-v215.css' if base_path else '/assets/affiliate-decision-funnel-v215.css'
    js = f'{base_path}/assets/affiliate-decision-funnel-v215.js' if base_path else '/assets/affiliate-decision-funnel-v215.js'
    assert css in text and js in text
    assert_document_closures(text)


def assert_contract() -> None:
    expected = module.event_contract()
    assert CONTRACT_PATH.is_file(), CONTRACT_PATH
    actual = json.loads(CONTRACT_PATH.read_text(encoding='utf-8'))
    assert actual == expected
    assert set(actual['events']) == set(module.EVENTS)
    assert actual['privacy']['requiresAnalyticsConsentForGa4'] is True
    assert actual['privacy']['rawDestinationUrlAllowed'] is False
    assert actual['privacy']['amazonSearchQueryAllowed'] is False
    assert actual['privacy']['asinAllowed'] is False
    assert actual['privacy']['freeTextAllowed'] is False
    assert actual['privacy']['numericElectricalInputsAllowed'] is False
    assert actual['privacy']['userOrDeviceIdentifierAllowed'] is False


def assert_runtime_asset(site: Path) -> None:
    asset = site / module.ASSET_JS
    js = asset.read_text(encoding='utf-8')
    for event in module.EVENTS:
        assert event in js
    assert "getConsent?.()==='granted'" in js
    assert 'numericElectricalInputs' not in js
    for forbidden in ('product_key', 'asin', 'search_query', 'email', 'phone', 'address'):
        assert forbidden not in js.lower()
    node = shutil.which('node')
    if node:
        subprocess.run([node, '--check', str(asset)], check=True)


def run_case(base_path: str) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        site = Path(tmp)
        seed(site)
        first = module.inject(site, base_path)
        assert first['ok'] is True
        assert first['version'] == 215
        assert first['basePath'] == base_path
        assert first['injectedFlows'] == ['mini_ups', 'ups_runtime', 'power_station']
        assert first['normalizedClosures'] == {}
        assert first['tierCount'] == 3
        assert first['directAmazonLinksAdded'] == 0
        assert first['rawDestinationUrlStored'] is False
        assert first['numericElectricalInputsStored'] is False
        assert first['userOrDeviceIdentifierStored'] is False
        for target in module.TARGETS:
            page = (site / target.path).read_text(encoding='utf-8')
            assert_page(page, target.flow, base_path)
            for tier, title, *_rest in module.TIER_COPY[target.flow]:
                assert f'data-decision-tier-card="{tier}"' in page
                assert title in page
        mini = (site / module.TARGETS[0].path).read_text(encoding='utf-8')
        assert 'data-decision-mini-controls' in mini
        assert 'Adaptör gerilimi tam okunuyor mu?' in mini
        assert all(f'name="{name}"' in mini for name in ('voltage', 'connector', 'devices', 'duration'))
        assert '<input' not in mini[mini.index('data-decision-mini-controls'):mini.index('</div>', mini.index('data-decision-mini-controls'))]
        ups = (site / module.TARGETS[1].path).read_text(encoding='utf-8')
        assert ups.index(module.MARKER) < ups.index('<div id="productRoute">')
        contract = json.loads((site / module.CONTRACT_NAME).read_text(encoding='utf-8'))
        assert contract == module.event_contract()
        release = json.loads((site / 'pages-release.json').read_text(encoding='utf-8'))
        funnel = release['affiliateDecisionFunnel']
        assert funnel['version'] == 215
        assert funnel['flows'] == ['mini_ups', 'ups_runtime', 'power_station']
        assert funnel['events'] == list(module.EVENTS)
        assert funnel['placements'] == list(module.PLACEMENTS)
        assert funnel['normalizedClosures'] == {}
        assert funnel['documentRepairPolicy'] == 'only-missing-closing-tags-with-valid-open-structure'
        assert funnel['noBuyOutcome'] is True
        assert funnel['commerceBlockOutcome'] is True
        assert funnel['directAmazonLinksAdded'] == 0
        assert_runtime_asset(site)
        second = module.inject(site, base_path)
        assert second['injectedFlows'] == []
        assert second['normalizedClosures'] == {}
        for target in module.TARGETS:
            assert_page((site / target.path).read_text(encoding='utf-8'), target.flow, base_path)


def run_artifact_normalization_case() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        site = Path(tmp)
        seed(site)

        mini_path = site / module.TARGETS[0].path
        mini = mini_path.read_text(encoding='utf-8')
        mini = mini.replace('</head>', '</HEAD >').replace('</main>', '').replace('</body>', '</BODY >')
        mini_path.write_text(mini, encoding='utf-8')

        ups_path = site / module.TARGETS[1].path
        ups_path.write_text(
            ups_path.read_text(encoding='utf-8').replace('</head>', ''),
            encoding='utf-8',
        )

        power_path = site / module.TARGETS[2].path
        power_path.write_text(
            power_path.read_text(encoding='utf-8').replace('</body>', ''),
            encoding='utf-8',
        )

        first = module.inject(site, '/chatgpt')
        expected = {
            'mini_ups': ['main'],
            'ups_runtime': ['head'],
            'power_station': ['body'],
        }
        assert first['normalizedClosures'] == expected, first
        for target in module.TARGETS:
            assert_page(
                (site / target.path).read_text(encoding='utf-8'),
                target.flow,
                '/chatgpt',
            )

        release = json.loads((site / 'pages-release.json').read_text(encoding='utf-8'))
        assert release['affiliateDecisionFunnel']['normalizedClosures'] == expected
        second = module.inject(site, '/chatgpt')
        assert second['injectedFlows'] == []
        assert second['normalizedClosures'] == {}
        retained = json.loads((site / 'pages-release.json').read_text(encoding='utf-8'))
        assert retained['affiliateDecisionFunnel']['normalizedClosures'] == expected


def test_missing_target_fails_closed() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        site = Path(tmp)
        try:
            module.inject(site, '')
        except FileNotFoundError:
            return
        raise AssertionError('Eksik karar hunisi hedefi fail-closed durmadı')


def test_truncated_document_fails_closed() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        site = Path(tmp)
        seed(site)
        path = site / module.TARGETS[0].path
        text = path.read_text(encoding='utf-8').replace('</body>', '').replace('</html>', '')
        path.write_text(text, encoding='utf-8')
        try:
            module.inject(site, '')
        except RuntimeError as error:
            assert 'güvenle' in str(error) or 'bulunamadı' in str(error)
            return
        raise AssertionError('Belirsiz biçimde kesilmiş HTML fail-closed durmadı')


if __name__ == '__main__':
    assert_contract()
    run_case('')
    run_case('/chatgpt')
    run_case('/preview/alo186')
    run_artifact_normalization_case()
    test_missing_target_fails_closed()
    test_truncated_document_fails_closed()
    print('ALO186 affiliate decision funnel v215: PASS')
