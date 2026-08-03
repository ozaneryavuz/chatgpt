from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ROUTES = {
    "/elektrik-dayaniklilik-karti/": {
        "source": ROOT / "alo186/elektrik-dayaniklilik-karti/index.html",
        "tokens": (
            "2 dakika · kişisel veri yok · ürün baskısı yok",
            "Ürün önermez. Önce plan, test ve doğru resmî kanal.",
            "Bu durumda puan oluşturulmaz ve hiçbir ticari yol açılmaz.",
            "Paylaşılan dayanıklılık kartı",
        ),
    },
    "/hesaplama/elektrik-ekipmani-tekrar-test-takvimi/": {
        "source": ROOT / "alo186/hesaplama/elektrik-ekipmani-tekrar-test-takvimi/index.html",
        "tokens": (
            "Tekrar ziyaret · bakım davranışı · ürün baskısı yok",
            "Doğrudan mağaza bağlantısı yok",
            "Mevcut ürün yeterliyse yenisini almayın",
            "Bu araçta affiliate veya mağaza bağlantısı bulunmaz.",
        ),
    },
}
FORBIDDEN = (
    "amazon.com.tr",
    '"@type":"Offer"',
    '"@type": "Offer"',
    '"@type":"Product"',
    '"@type": "Product"',
)


def route_file(site: Path, route: str) -> Path:
    return site / route.strip("/") / "index.html"


def validate_html(path: Path, route: str, tokens: tuple[str, ...], artifact: bool) -> None:
    assert path.is_file(), f"Rota eksik: {route} → {path}"
    html = path.read_text(encoding="utf-8")
    for token in tokens:
        assert token in html, f"Sözleşme eksik: {route}: {token}"
    for token in FORBIDDEN:
        assert token not in html, f"Ticari güven ihlali: {route}: {token}"
    assert f'<link rel="canonical" href="https://alo186.com{route}">' in html
    assert not re.search(r"\b(?:fiyat|stok|puan|garanti)\s*:", html, re.I)
    if artifact:
        assert "data-alo186-pages-sw" in html, f"Service worker kaydı eksik: {route}"
        assert "data-alo186-sitewide-ux" in html, f"Site geneli UX kaydı eksik: {route}"


def source_contracts() -> None:
    for route, spec in ROUTES.items():
        validate_html(spec["source"], route, spec["tokens"], False)

    app = (ROOT / "alo186/hesaplama/elektrik-ekipmani-tekrar-test-takvimi/app.js").read_text(encoding="utf-8")
    for token in (
        "BEGIN:VCALENDAR",
        "text/calendar;charset=utf-8",
        "equipment_retest_calendar_download",
        'status === "damaged"',
        "belirsizliği doğrudan satın alma gerekçesine dönüştürmeyin",
    ):
        assert token in app, f"Tekrar test uygulama sözleşmesi eksik: {token}"
    assert "localStorage" not in app
    assert "fetch(" not in app


def artifact_contracts(site: Path, base_path: str) -> None:
    for route, spec in ROUTES.items():
        validate_html(route_file(site, route), route, spec["tokens"], True)
    release = (site / "pages-release.json").read_text(encoding="utf-8")
    assert '"serviceWorkerRegistrationFinalization"' in release
    if base_path:
        for route in ROUTES:
            html = route_file(site, route).read_text(encoding="utf-8")
            assert f'"{base_path}/sw.js"' in html
            assert f'scope:"{base_path}/"' in html


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", type=Path)
    parser.add_argument("--base-path", default="")
    args = parser.parse_args()
    source_contracts()
    if args.site:
        artifact_contracts(args.site.resolve(), args.base_path.rstrip("/"))
    print("privacy-first return visit routes: PASS")


if __name__ == "__main__":
    main()
