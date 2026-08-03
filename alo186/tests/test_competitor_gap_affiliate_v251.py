from __future__ import annotations

import json
import re
import tempfile
from pathlib import Path

from alo186.deployment.inject_competitor_gap_affiliate_v250 import apply as apply_v250
from alo186.deployment.inject_competitor_gap_affiliate_v251 import apply as apply_v251


def page(title: str) -> str:
    return (
        '<!doctype html><html lang="tr"><head><meta charset="utf-8">'
        f'<title>{title}</title></head><body><main><h1>{title}</h1></main></body></html>'
    )


def main() -> None:
    repo = Path(__file__).resolve().parents[2]
    with tempfile.TemporaryDirectory(prefix="alo186-v251-") as raw:
        site = Path(raw)
        routes = (
            ("amazon-elektrik-urunleri/kombi-yedek-enerji-urun-secici", "Kombi seçici"),
            ("edas-bul", "EDAŞ bul"),
            ("acil-numaralar", "Acil numaralar"),
            ("haberler/ups-mi-tasinabilir-guc-istasyonu-mu", "UPS mi güç istasyonu mu"),
            ("haberler/korumali-priz-ne-zaman-yeterli-degildir", "Korumalı priz"),
            ("karar-motoru", "Karar motoru"),
            ("hesaplama/kesinti-hazirlik-plani", "Kesinti hazırlık planı"),
            ("il/mugla", "Muğla elektrik kesintisi"),
            ("dagitim-sirketleri/adm-elektrik", "ADM Elektrik"),
        )
        for route, title in routes:
            target = site / route
            target.mkdir(parents=True)
            (target / "index.html").write_text(page(title), encoding="utf-8")
        (site / "robots.txt").write_text(
            "User-agent: *\nAllow: /\n\nSitemap: https://alo186.com/sitemap.xml\n",
            encoding="utf-8",
        )

        apply_v250(repo, site)
        first = apply_v251(repo, site)
        second = apply_v251(repo, site)

        assert first["version"] == 251
        assert second["validation"]["jsonLdSyntax"] == "pass"
        assert second["validation"]["visibleContentParity"] == "pass"
        assert second["validation"]["schemaOrgValidator"]["status"] == "pass"
        assert second["validation"]["googleRichResultsAssessment"]["status"] == "pass-with-feature-boundaries"
        assert second["validation"]["provinceServices"] == 81
        assert second["validation"]["serviceChannels"] == 81
        assert second["validation"]["servicePhone186"] == 81
        assert second["validation"]["privateEdasGovernmentService"] == 0
        assert second["validation"]["ssrAffiliateLinks"] >= 3

        kombi = (site / "amazon-elektrik-urunleri/kombi-yedek-enerji-urun-secici/index.html").read_text(encoding="utf-8")
        assert kombi.count('data-alo186-howto-visible-v251="true"') == 1
        assert kombi.count('data-alo186-schema-v250="true"') == 1
        assert kombi.count('data-alo186-ssr-affiliate-v250="true"') == 1
        for anchor in (
            "kombi-adim-acil",
            "kombi-adim-model",
            "kombi-adim-yuk",
            "kombi-adim-test",
            "kombi-adim-urun",
            "urun-kombi-ups",
            "urun-kombi-guc-istasyonu",
            "urun-priz-enerji-olcer",
        ):
            assert f'id="{anchor}"' in kombi
        assert kombi.count('rel="sponsored nofollow noopener"') == 3
        assert '"@type":"HowTo"' in kombi
        assert '"@type":"ItemList"' in kombi
        assert '"@type":"Product"' in kombi
        assert '"@type":"Offer"' not in kombi
        assert "aggregateRating" not in kombi
        assert kombi.count('"url":"https://alo186.com/amazon-elektrik-urunleri/kombi-yedek-enerji-urun-secici/#kombi-adim-') == 5

        edas = (site / "edas-bul/index.html").read_text(encoding="utf-8")
        assert edas.count('data-alo186-service-catalog-v250="true"') == 1
        assert edas.count('"@type":"ServiceChannel"') == 81
        assert edas.count('"telephone":"186"') == 81
        assert '"numberOfItems":81' in edas
        assert '"@type":"GovernmentService"' not in edas

        province = (site / "il/mugla/index.html").read_text(encoding="utf-8")
        company = (site / "dagitim-sirketleri/adm-elektrik/index.html").read_text(encoding="utf-8")
        assert province.count('data-alo186-local-service-v251="true"') == 1
        assert company.count('data-alo186-local-service-v251="true"') == 1
        assert '"@type":"Service"' in province and '"telephone":"186"' in province
        assert '"@type":"Organization"' in company and '"telephone":"186"' in company

        decision = (site / "karar-motoru/index.html").read_text(encoding="utf-8")
        preparation = (site / "hesaplama/kesinti-hazirlik-plani/index.html").read_text(encoding="utf-8")
        assert decision.count('data-alo186-ssr-decision-v251="true"') == 1
        assert preparation.count('data-alo186-ssr-preparedness-v251="true"') == 1
        assert "JavaScript olmadan güvenli başlangıç" in decision
        assert "JavaScript olmadan kesinti hazırlık kontrolü" in preparation
        assert "amazon.com.tr" not in decision.lower()
        assert "amazon.com.tr" not in preparation.lower()

        robots = (site / "robots.txt").read_text(encoding="utf-8")
        for agent in (
            "GPTBot",
            "OAI-SearchBot",
            "ChatGPT-User",
            "PerplexityBot",
            "ClaudeBot",
            "Bytespider",
            "Google-Extended",
        ):
            assert robots.count(f"User-agent: {agent}") == 1
            assert re.search(rf"User-agent: {re.escape(agent)}\nAllow: /", robots)

        report = json.loads((site / "alo186-schema-validation-v251.json").read_text(encoding="utf-8"))
        assert report["version"] == 251
        assert report["validation"]["offerEntities"] == 0
        assert report["validation"]["googleRichResultsAssessment"]["HowTo"].startswith("schema.org-valid")
        assert report["validation"]["googleRichResultsAssessment"]["Product"].startswith("generic product-class")

    print("ALO186 competitor-gap & affiliate v251: PASS")


if __name__ == "__main__":
    main()
