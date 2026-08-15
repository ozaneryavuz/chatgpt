from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LEGACY = ROOT / "alo186/hesaplama/kesinti-gunlugu/index.html"
CURRENT = ROOT / "alo186/hesaplama/elektrik-kesintisi-sure-gunlugu/index.html"
STATUS_CENTER = ROOT / "alo186/elektrik-durum-merkezi/index.html"
CURRENT_ROUTE = "/hesaplama/elektrik-kesintisi-sure-gunlugu/"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_legacy_outage_journal_is_noindex_compatibility_alias() -> None:
    html = read(LEGACY)
    assert 'content="noindex,follow"' in html
    assert 'rel="canonical" href="https://alo186.com/hesaplama/elektrik-kesintisi-sure-gunlugu/"' in html
    assert f'url={CURRENT_ROUTE}' in html
    assert f"location.replace('{CURRENT_ROUTE}')" in html
    assert "10 iş günü" not in html
    assert "tazminat ön kontrol" not in html.lower()


def test_current_outage_journal_remains_noncommercial_canonical_owner() -> None:
    html = read(CURRENT)
    assert 'rel="canonical" href="https://alo186.com/hesaplama/elektrik-kesintisi-sure-gunlugu/"' in html
    assert "affiliate bağlantısı içermez" in html
    assert '"@type":"Offer"' not in html
    assert '"price"' not in html
    assert '"priceCurrency"' not in html


def test_status_center_links_directly_to_current_journal_without_price_offer_schema() -> None:
    html = read(STATUS_CENTER)
    assert f'href="{CURRENT_ROUTE}"' in html
    assert '"isAccessibleForFree":true' in html
    assert '"@type":"Offer"' not in html
    assert '"price"' not in html
    assert '"priceCurrency"' not in html
    assert "EDAŞ veya kamu kurumu değildir" in html


def test_v366_has_no_new_merchant_surface() -> None:
    combined = read(LEGACY) + read(STATUS_CENTER)
    lowered = combined.lower()
    assert "amzn.to" not in lowered
    assert "amazon.com.tr" not in lowered
    assert 'rel="sponsored' not in lowered
