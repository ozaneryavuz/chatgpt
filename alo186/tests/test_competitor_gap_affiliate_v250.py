from __future__ import annotations

import json
import tempfile
from pathlib import Path

from alo186.deployment.inject_competitor_gap_affiliate_v250 import apply


def page(title: str) -> str:
    return (
        '<!doctype html><html lang="tr"><head><meta charset="utf-8">'
        f"<title>{title}</title></head><body><main><h1>{title}</h1></main></body></html>"
    )


def main() -> None:
    repo = Path(__file__).resolve().parents[2]
    with tempfile.TemporaryDirectory() as raw:
        site = Path(raw)
        for route, title in (
            ("amazon-elektrik-urunleri/kombi-yedek-enerji-urun-secici", "Kombi seçici"),
            ("edas-bul", "EDAŞ bul"),
            ("acil-numaralar", "Acil numaralar"),
            ("haberler/ups-mi-tasinabilir-guc-istasyonu-mu", "UPS mi güç istasyonu mu"),
            ("haberler/korumali-priz-ne-zaman-yeterli-degildir", "Korumalı priz"),
        ):
            target = site / route
            target.mkdir(parents=True)
            (target / "index.html").write_text(page(title), encoding="utf-8")
        (site / "robots.txt").write_text(
            "User-agent: *\nAllow: /\n\nSitemap: https://alo186.com/sitemap.xml\n",
            encoding="utf-8",
        )

        first = apply(repo, site)
        second = apply(repo, site)
        assert first["version"] == 250
        assert first["revision"] == 251
        assert second["validation"]["jsonLdSyntax"] == "pass"
        assert second["validation"]["ssrNamedModules"] == "pass"

        kombi = (
            site / "amazon-elektrik-urunleri/kombi-yedek-enerji-urun-secici/index.html"
        ).read_text(encoding="utf-8")
        assert kombi.count('data-alo186-schema-v250="true"') == 1
        assert kombi.count('data-alo186-ssr-affiliate-v250="true"') == 1
        assert kombi.count('id="akilli-yol-ssr"') == 1
        assert kombi.count('id="kisisel-hazirlik-kontrolu-ssr"') == 1
        assert kombi.count('rel="sponsored nofollow noopener"') == 3
        assert '<a id="urun-ups-3000va"' in kombi
        assert '<a id="urun-kombi-guc-istasyonu"' in kombi
        assert '<a id="urun-priz-enerji-olcer"' in kombi
        for schema_type in ("Question", "DefinedTerm", "HowTo", "Product", "ItemList"):
            assert f'"@type":"{schema_type}"' in kombi
        assert "Kesintide kombi nasıl korunur?" in kombi
        assert "Soru–Sorun–Çözüm–Ürün" in kombi
        assert "3000 VA ifadesi bir kategori ankrajıdır" in kombi
        assert '"offers"' not in kombi.lower()
        assert "aggregaterating" not in kombi.lower()

        edas = (site / "edas-bul/index.html").read_text(encoding="utf-8")
        assert edas.count('data-alo186-service-catalog-v250="true"') == 1
        assert '"numberOfItems":81' in edas
        assert '"@type":"Service"' in edas
        assert '"@type":"ServiceChannel"' in edas
        assert '"@type":"Organization"' in edas
        assert edas.count('"telephone":"186"') == 81
        assert "GovernmentService" not in edas

        emergency = (site / "acil-numaralar/index.html").read_text(encoding="utf-8")
        assert emergency.count('data-alo186-government-service-v250="true"') == 1
        assert '"@type":"GovernmentService"' in emergency

        robots = (site / "robots.txt").read_text(encoding="utf-8")
        for agent in ("GPTBot", "PerplexityBot", "ClaudeBot", "Bytespider", "Google-Extended"):
            assert f"User-agent: {agent}\nAllow: /" in robots

        report = json.loads(
            (site / "alo186-competitor-gap-affiliate-v250.json").read_text(encoding="utf-8")
        )
        assert report["revision"] == 251
        assert report["validation"]["affiliateRel"] == "pass"
        assert report["validation"]["newGoogleRichResultEligibility"] == []
        assert report["edas"]["governmentServiceForPrivateEdas"] is False
        assert report["edas"]["serviceChannels186"] == 81
        assert report["kombi"]["ssrModules"] == [
            "akilli-yol-ssr",
            "kisisel-hazirlik-kontrolu-ssr",
        ]

    print("ALO186 competitor-gap & affiliate v250 revision 251: PASS")


if __name__ == "__main__":
    main()
