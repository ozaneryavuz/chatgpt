from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INDEX = ROOT / "alo186/elektrik-durum-merkezi/index.html"
APP = ROOT / "alo186/elektrik-durum-merkezi/app.js"
STYLE = ROOT / "alo186/elektrik-durum-merkezi/styles.css"
PAGES = ROOT / "alo186/deployment/prepare_github_pages.py"


def main() -> None:
    html = INDEX.read_text(encoding="utf-8")
    app = APP.read_text(encoding="utf-8")
    css = STYLE.read_text(encoding="utf-8")
    pages = PAGES.read_text(encoding="utf-8")

    for token in (
        "Doğru sonraki adımı bulun.",
        "Kişisel veri istemez",
        "Resmî kayıt oluşturmaz",
        "Tehlikede ticari yolu kapatır",
        '"featureList"',
        'rel="canonical" href="https://www.alo186.com/elektrik-durum-merkezi"',
    ):
        assert token in html, token

    for forbidden in ('type="email"', 'type="tel"', 'name="address"', 'name="subscriber"', 'amazon.com.tr'):
        assert forbidden not in html, forbidden

    for token in (
        "alo186.electricStatus.v1",
        "stepper",
        "progress-track",
        "step-actions",
        "URLSearchParams",
        "params.get('resume')==='1'",
        "renderResume",
        "applyRecord",
        "mobile-dock",
        "tel:112",
        "/edas-bul",
        "/hesaplama/elektrik-planim/",
    ):
        assert token in app, token

    assert "slice(0,6)" in app
    assert "30*24*60*60*1000" in app
    assert "amazon.com.tr" not in app

    for token in (
        ".resume-card",
        ".stepper",
        ".progress-track",
        ".mobile-dock",
        "max-width:760px",
        "min-height:50px",
        "prefers-reduced-motion",
    ):
        assert token in css, token

    for token in (
        'PRIMARY_START_ROUTE = "/elektrik-durum-merkezi/"',
        "_core.CRITICAL_ROUTES",
        "data-alo186-primary-start",
        "60 saniyede doğru elektrik rotası",
        "Tehlike varsa ticari yol kapanır",
        "update_primary_shortcut",
        'result["primaryStartMode"] = "progressive-disclosure"',
    ):
        assert token in pages, token

    print("ALO186 akıllı başlangıç ve progresif ürün tasarımı sözleşmeleri başarılı.")


if __name__ == "__main__":
    main()
