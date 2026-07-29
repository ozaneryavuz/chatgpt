from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEPLOYMENT = REPO_ROOT / "alo186/deployment"
sys.path.insert(0, str(DEPLOYMENT))

from guard_commerce_routes import validate_site  # noqa: E402


def write_base(root: Path) -> None:
    canonical = root / "akilli-urun-secimi" / "index.html"
    canonical.parent.mkdir(parents=True, exist_ok=True)
    canonical.write_text("<html><body>Güvenli ürün merkezi</body></html>", encoding="utf-8")
    alias = root / "amazon-elektrik-urunleri" / "index.html"
    alias.parent.mkdir(parents=True, exist_ok=True)
    alias.write_text(
        '<html><head><link rel="canonical" href="https://www.alo186.com/akilli-urun-secimi"></head>'
        '<body data-alo186-content-alias="true"><a href="/akilli-urun-secimi">Güncel içerik</a></body></html>',
        encoding="utf-8",
    )


def assert_rejected(html: str, expected: str) -> None:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        write_base(root)
        page = root / "test" / "index.html"
        page.parent.mkdir(parents=True, exist_ok=True)
        page.write_text(html, encoding="utf-8")
        try:
            validate_site(root)
        except AssertionError as error:
            payload = json.loads(str(error))
            assert any(expected in item for item in payload["errors"]), payload
        else:
            raise AssertionError(f"Güvensiz fixture reddedilmedi: {expected}")


def main() -> None:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        write_base(root)
        page = root / "safe" / "index.html"
        page.parent.mkdir(parents=True, exist_ok=True)
        page.write_text(
            '<html><body data-alo186-affiliate-gate="qualified">'
            '<p><strong>Reklam / satış ortaklığı:</strong> Nitelikli satın alımlardan komisyon kazanılabilir.</p>'
            '<p>USB-C powerbank teknik eşleşmesi.</p>'
            '<a href="https://www.amazon.com.tr/s?k=usb-c-powerbank" rel="sponsored nofollow noopener">'
            'Şeffaf satış ortaklığı aramasını aç</a></body></html>',
            encoding="utf-8",
        )
        result = validate_site(root)
        assert result["ok"] is True
        assert result["errorCount"] == 0

    assert_rejected(
        '<html><body data-alo186-affiliate-gate="qualified"><p>Satış ortaklığı bağlantısıdır.</p>'
        '<a href="https://www.amazon.com.tr/s?k=powerbank" rel="nofollow">Ürün</a></body></html>',
        "eksik rel tokenları",
    )
    assert_rejected(
        '<html><body><p>Satış ortaklığı bağlantısıdır.</p>'
        '<a href="https://www.amazon.com.tr/s?k=powerbank" rel="sponsored nofollow noopener">Ürün</a></body></html>',
        "nitelikli affiliate kapısı",
    )
    assert_rejected(
        '<html><body data-alo186-affiliate-gate="qualified"><p>Satış ortaklığı bağlantısıdır.</p>'
        '<p>RCCB ve RCBO pano seçimi</p>'
        '<a href="https://www.amazon.com.tr/s?k=rccb" rel="sponsored nofollow noopener">Ürün</a></body></html>',
        "yüksek riskli/sabit tesisat",
    )

    print(json.dumps({"ok": True, "safeFixture": 1, "blockedFixtures": 3}, ensure_ascii=False))


if __name__ == "__main__":
    main()
