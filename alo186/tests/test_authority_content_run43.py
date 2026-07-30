from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

PAGES = {
    "jenerator-dusuk-yuk-wet-stacking-minimum-yuk": {
        "canonical": "https://www.alo186.com/haberler/jenerator-dusuk-yuk-wet-stacking-minimum-yuk",
        "tokens": ["Wet stacking", "Load bank", "ISO 8528-1", "Satın almama sınırı", "Mevcut içerikten görev ayrımı"],
        "sources": ["cat.com", "iso.org/standard/68539", "iso.org/standard/85962"],
    },
    "ev-sarj-acik-pen-arizasi-topraklama-korumasi": {
        "canonical": "https://www.alo186.com/haberler/ev-sarj-acik-pen-arizasi-topraklama-korumasi",
        "tokens": ["Open PEN fault", "OPDD", "IEC 60364-7-722", "Satın almama sınırı", "Mevcut içerikten görev ayrımı"],
        "sources": ["theiet.org", "shop.theiet.org", "webstore.iec.ch/en/publication/29958"],
    },
    "kompanzasyon-detuned-reaktor-yuzde-7-ne-demek": {
        "canonical": "https://www.alo186.com/haberler/kompanzasyon-detuned-reaktor-yuzde-7-ne-demek",
        "tokens": ["Detuned reactor", "190 Hz", "IEC 61642", "Satın almama sınırı", "Mevcut içerikten görev ayrımı"],
        "sources": ["webstore.iec.ch/en/publication/5681", "se.com/uk", "eshop.se.com"],
    },
}


def main() -> None:
    canonicals: set[str] = set()
    for slug, contract in PAGES.items():
        path = ROOT / "alo186/haberler" / slug / "index.html"
        assert path.is_file(), path
        html = path.read_text(encoding="utf-8")
        compact = html.replace(" ", "")
        canonical = contract["canonical"]
        assert canonical not in canonicals, canonical
        canonicals.add(canonical)
        assert f'rel="canonical"href="{canonical}"' in compact
        assert '"@type":"Article"' in compact
        assert '"@type":"FAQPage"' in compact
        assert '"@type":"BreadcrumbList"' in compact
        assert compact.count('"@type":"DefinedTerm"') >= 8
        assert compact.count('"@type":"Question"') >= 4
        assert "Doğrudan cevap:" in html
        assert "Birincil kaynaklar" in html
        assert "Profesyonel ön değerlendirme" in html
        assert "ALO186 bağımsız bilgi platformudur" in html
        for token in contract["tokens"]:
            assert token in html, (slug, token)
        for source in contract["sources"]:
            assert source in html, (slug, source)
        lower = html.casefold()
        for forbidden in ("amazon.com.tr", 'type="email"', 'type="tel"', 'type="text"', '"@type":"Offer"', "pricecurrency"):
            assert forbidden not in lower, (slug, forbidden)

    overlay_path = ROOT / "alo186/deployment/routing-overlays/content-authority-run43.json"
    overlay = json.loads(overlay_path.read_text(encoding="utf-8"))
    assert overlay["version"] == 76
    routes = overlay["routes"]
    assert len(routes) == 3
    assert {item["canonicalPath"] for item in routes} == {
        "/haberler/jenerator-dusuk-yuk-wet-stacking-minimum-yuk",
        "/haberler/ev-sarj-acik-pen-arizasi-topraklama-korumasi",
        "/haberler/kompanzasyon-detuned-reaktor-yuzde-7-ne-demek",
    }
    assert all(item["type"] == "article" for item in routes)
    print(json.dumps({"ok": True, "pages": len(PAGES), "routingVersion": overlay["version"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
