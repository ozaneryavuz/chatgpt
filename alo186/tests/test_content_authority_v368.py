from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def main() -> None:
    pages = {
        "spd": read("alo186/haberler/parafudr-on-sigorta-max-backup-fuse-secimi/index.html"),
        "bms": read("alo186/haberler/lityum-batarya-bms-hucre-dengesizligi-cell-imbalance/index.html"),
        "fan": read("alo186/haberler/ups-fan-fault-fan-inoperable-alarmi/index.html"),
    }
    routing = json.loads(read("alo186/deployment/routing-overlays/content-authority-v368-afci-oil-fan.json"))
    expected = {
        "/haberler/parafudr-on-sigorta-max-backup-fuse-secimi/",
        "/haberler/lityum-batarya-bms-hucre-dengesizligi-cell-imbalance/",
        "/haberler/ups-fan-fault-fan-inoperable-alarmi/",
    }
    assert routing["version"] == 368
    assert len(routing["routes"]) == 3
    assert {route["canonicalPath"] for route in routing["routes"]} == expected

    for page in pages.values():
        lowered = page.lower()
        assert '<meta name="robots" content="index,follow,max-image-preview:large">' in page
        assert '"@type":"Article"' in page
        assert '"@type":"FAQPage"' in page
        assert '"@type":"BreadcrumbList"' in page
        assert "Son doğrulama: 15 Ağustos 2026" in page
        assert "60 saniyelik karar" in page
        assert "Kaynaklar" in page
        assert "ALO186 bağımsız" in page
        assert "amazon.com.tr" not in lowered
        assert '"@type":"Product"' not in page
        assert '"@type":"Offer"' not in page
        assert "AggregateRating" not in page
        assert "priceCurrency" not in page

    spd = pages["spd"]
    for required in (
        "Max backup fuse",
        "SPD–üst koruma–Ik–backup fuse matrisi",
        "/haberler/parafudr-tip-1-tip-2-tip-3-koordinasyon-secimi/",
        "/haberler/parafudr-omur-sonu-gosterge-uzak-kontak-degisim-kabul/",
        "IEC 61643-11:2025",
    ):
        assert required in spd

    bms = pages["bms"]
    for required in (
        "Cell Imbalance",
        "Min/max hücre–delta–SoC–akım–alarm matrisi",
        "/haberler/inverter-akuyu-sarj-etmiyor-charge-disabled-bms/",
        "/haberler/bess-kullanilabilir-enerji-round-trip-verim-standby-kaybi-kabul/",
        "Victron Energy",
    ):
        assert required in bms

    fan = pages["fan"]
    for required in (
        "Fan Inoperable",
        "Alarm–fan–sıcaklık–yük kanıt matrisi",
        "/haberler/ups-bypass-unavailable-out-of-tolerance-ne-demek/",
        "/haberler/ups-akusu-sisti-sicak-koku-var-ne-yapmali/",
        "IEC 62040-1",
    ):
        assert required in fan

    print({
        "ok": True,
        "version": 368,
        "routes": 3,
        "merchantLinks": 0,
        "schemas": ["Article", "FAQPage", "BreadcrumbList"],
        "policy": "intent-separated / evidence-first / no-buy-first / professional-only energized work",
    })


if __name__ == "__main__":
    main()
