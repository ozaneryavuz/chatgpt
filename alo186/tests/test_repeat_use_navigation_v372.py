from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
ALO = ROOT / "alo186"


def read(rel: str) -> str:
    path = ALO / rel
    assert path.is_file(), path
    return path.read_text(encoding="utf-8")


def test_legacy_outage_journal_is_noindex_and_redirects_to_preferred_tool():
    html = read("hesaplama/kesinti-gunlugu/index.html")
    assert 'content="noindex,follow"' in html
    assert '<link rel="canonical" href="https://alo186.com/hesaplama/kesinti-gunlugu/">' in html
    assert "location.replace('/hesaplama/elektrik-kesintisi-sure-gunlugu/')" in html
    assert 'content="0;url=/hesaplama/elektrik-kesintisi-sure-gunlugu/"' in html


def test_repeat_use_hub_is_noncommercial_and_links_core_return_paths():
    html = read("tekrar-kullanilan-araclar/index.html")
    low = html.casefold()
    for route in (
        "/hesaplama/elektrik-kesintisi-sure-gunlugu/",
        "/elektrik-kesintisi-haklari-merkezi/",
        "/fatura-ve-sayac-kontrol-merkezi/",
        "/ev-elektrik-guvenlik-kontrol-merkezi/",
        "/enerji-tasarrufu-kontrol-merkezi/",
        "/hesaplama/urun-almadan-once-uygunluk-kontrolu/",
    ):
        assert route in html
    assert "amazon.com.tr" not in low
    assert "amzn.to" not in low
    assert "mevcut çözüm yeterliyse yeni ürün almayın" in low
    assert "resmî kurum değildir" in low


def test_product_precheck_fails_closed_before_commerce():
    html = read("hesaplama/urun-almadan-once-uygunluk-kontrolu/index.html")
    low = html.casefold()
    assert "amazon.com.tr" not in low
    assert "amzn.to" not in low
    assert "/amazon-elektrik-urunleri/" in html
    assert "bu araçta doğrudan amazon veya başka bir mağaza bağlantısı yoktur" in low
    assert "fiyat, stok, puan veya garanti bilgisi yayımlamaz" in low
    assert "aktif elektriksel tehlikede ürün araştırmayın" in low
    assert "yeni ürün almayın" in low
    for forbidden in ("fetch(", "localstorage", "sessionstorage", "geolocation"):
        assert forbidden not in low


def test_v372_governance_and_routing_contract():
    gov = json.loads(read("content/commerce/repeat-use-navigation-v372.json"))
    routing = json.loads(read("deployment/routing-overlays/repeat-use-navigation-v372.json"))
    assert gov["version"] == 372
    assert gov["commerce"]["new_affiliate_classes"] == 0
    assert gov["commerce"]["new_merchant_links"] == 0
    assert gov["commerce"]["direct_merchant_links_on_new_routes"] == 0
    assert gov["canonical_cleanup"]["preferred"] == "/hesaplama/elektrik-kesintisi-sure-gunlugu/"
    assert gov["canonical_cleanup"]["legacy_indexing"] == "noindex,follow"
    assert gov["canonical_cleanup"]["legacy_redirects_to_preferred"] is True
    assert routing["version"] == 372
    canonical_paths = {route["canonicalPath"] for route in routing["routes"]}
    assert canonical_paths == {
        "/tekrar-kullanilan-araclar/",
        "/hesaplama/urun-almadan-once-uygunluk-kontrolu/",
    }


def main() -> None:
    checks = (
        test_legacy_outage_journal_is_noindex_and_redirects_to_preferred_tool,
        test_repeat_use_hub_is_noncommercial_and_links_core_return_paths,
        test_product_precheck_fails_closed_before_commerce,
        test_v372_governance_and_routing_contract,
    )
    for check in checks:
        check()
    print({"ok": True, "version": 372, "checks": len(checks), "newMerchantLinks": 0})


if __name__ == "__main__":
    main()
