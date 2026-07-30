from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

PAGES = {
    "parafudr-on-sigorta-backup-fuse-nasil-secilir": {
        "canonical": "https://www.alo186.com/haberler/parafudr-on-sigorta-backup-fuse-nasil-secilir",
        "tokens": ["Backup fuse", "SCCR", "IEC 61643-11:2025", "Satın almama sınırı", "Mevcut içerikten görev ayrımı"],
        "sources": ["webstore.iec.ch/en/publication/65314", "se.com/us/en/download/document/0100CT2401-SEC-06", "dehn-international.com/store"],
    },
    "kacak-akim-rolesi-secicilik-s-tipi-nasil-calisir": {
        "canonical": "https://www.alo186.com/haberler/kacak-akim-rolesi-secicilik-s-tipi-nasil-calisir",
        "tokens": ["Selective RCD", "S-type RCD", "IEC 61008-1:2024", "Satın almama sınırı", "Mevcut içerikten görev ayrımı"],
        "sources": ["webstore.iec.ch/en/publication/67980", "se.com/ie/en/product-range/906", "FAQ000281380", "empower.abb.com"],
    },
    "enerji-depolama-ul-9540-ul-9540a-nfpa-855-farki": {
        "canonical": "https://www.alo186.com/haberler/enerji-depolama-ul-9540-ul-9540a-nfpa-855-farki",
        "tokens": ["UL 9540", "UL 9540A", "NFPA 855", "Satın almama sınırı", "Mevcut içerikten görev ayrımı"],
        "sources": ["shopulstandards.com", "ul.com/services/ul-9540a", "ul.com/services/energy-storage", "link.nfpa.org/all-publications/855/2026"],
    },
}


def main() -> None:
    canonicals: set[str] = set()
    titles: set[str] = set()
    for slug, contract in PAGES.items():
        path = ROOT / "alo186/haberler" / slug / "index.html"
        assert path.is_file(), path
        html = path.read_text(encoding="utf-8")
        compact = html.replace(" ", "")
        canonical = contract["canonical"]
        assert canonical not in canonicals, canonical
        canonicals.add(canonical)
        title = html.split("<title>", 1)[1].split("</title>", 1)[0]
        assert title not in titles, title
        titles.add(title)
        assert f'rel="canonical"href="{canonical}"' in compact
        assert 'name="description"' in html
        assert 'name="robots" content="index,follow,max-image-preview:large"' in html
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
        for forbidden in ("amazon.com.tr", 'type="email"', 'type="tel"', 'type="text"', '"@type":"offer"', "pricecurrency"):
            assert forbidden not in lower, (slug, forbidden)

    overlay_path = ROOT / "alo186/deployment/routing-overlays/content-authority-run44.json"
    overlay = json.loads(overlay_path.read_text(encoding="utf-8"))
    assert overlay["version"] == 78
    routes = overlay["routes"]
    assert len(routes) == 3
    expected = {f"/haberler/{slug}" for slug in PAGES}
    assert {item["canonicalPath"] for item in routes} == expected
    assert all(item["type"] == "article" for item in routes)
    assert len({item["source"] for item in routes}) == 3
    print(json.dumps({"ok": True, "pages": len(PAGES), "routingVersion": overlay["version"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
