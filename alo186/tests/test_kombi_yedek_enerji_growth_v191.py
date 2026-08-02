#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PAGES = {
    "/hesaplama/kombi-elektrik-kesintisi-ups-guc-istasyonu-uygunlugu/": ROOT / "alo186/hesaplama/kombi-elektrik-kesintisi-ups-guc-istasyonu-uygunlugu/index.html",
    "/amazon-elektrik-urunleri/kombi-yedek-enerji-urun-secici/": ROOT / "alo186/amazon-elektrik-urunleri/kombi-yedek-enerji-urun-secici/index.html",
    "/sektor-rehberi/kombi-elektrik-kesintisi-30-90-gun-test-merkezi/": ROOT / "alo186/sektor-rehberi/kombi-elektrik-kesintisi-30-90-gun-test-merkezi/index.html",
}
OVERLAY = ROOT / "alo186/deployment/routing-overlays/191-kombi-yedek-enerji-growth.json"
AUDIT = ROOT / "alo186/audits/kombi-yedek-enerji-growth-v191-2026-08-02.md"

PROHIBITED_SCHEMA = ('"@type":"Product"', '"@type":"Offer"', '"@type":"AggregateRating"')
PROHIBITED_COMMERCE = (
    "güncel fiyat", "stokta", "yıldız", "puanı", "garanti süresi",
    "en ucuz", "indirimli fiyat", "satıcı puanı",
)


def script_text(html: str) -> str:
    return "\n".join(re.findall(r"<script>(.*?)</script>", html, re.S))


def main() -> None:
    assert OVERLAY.exists(), OVERLAY
    overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
    assert overlay["version"] == 191
    assert overlay["generatedAt"] == "2026-08-02"
    routes = overlay["routes"]
    assert len(routes) == 3
    assert {r["canonicalPath"] for r in routes} == set(PAGES)
    assert {r["type"] for r in routes} == {"calculator", "commerce-guide", "guide"}

    for canonical, path in PAGES.items():
        assert path.exists(), path
        html = path.read_text(encoding="utf-8")
        assert f'<link rel="canonical" href="https://alo186.com{canonical}">' in html
        assert '<meta name="viewport"' in html
        assert 'lang="tr"' in html
        assert 'ALO186' in html and 'Bağımsız' in html
        assert 'resmî kurum' in html or 'kamu kurumu' in html
        assert 'Product' not in html or all(x not in html for x in PROHIBITED_SCHEMA)
        for marker in PROHIBITED_SCHEMA:
            assert marker not in html, (path, marker)
        lower = html.lower()
        for phrase in PROHIBITED_COMMERCE:
            assert phrase not in lower, (path, phrase)
        assert "yeni ürün almayın" in lower or "yeni ürün önerilmez" in lower
        assert "187" in html and "112" in html
        assert "WebApplication" in html or "CollectionPage" in html
        assert "FAQPage" in html and "BreadcrumbList" in html
        assert script_text(html), path

    calculator = PAGES[next(k for k in PAGES if k.startswith("/hesaplama/"))].read_text(encoding="utf-8")
    assert "saf sinüs" in calculator.lower()
    assert "tam kombi modeli" in calculator.lower()
    assert "ticari yol kapalı" in calculator.lower()
    assert "device')!=='plug'" in calculator
    assert "available/run" in calculator
    assert "Mevcut düzen hedefi karşılıyor — yeni ürün almayın" in calculator

    selector = PAGES["/amazon-elektrik-urunleri/kombi-yedek-enerji-urun-secici/"].read_text(encoding="utf-8")
    assert selector.count('class="gatebox"') == 3
    assert "slice(0,3)" in selector
    assert "alo186rehber-21" in selector
    assert "sponsored nofollow noopener" in selector
    assert 'href="https://www.amazon.com.tr' not in selector
    assert selector.count("title:'") == 3
    assert "Mevcut düzen yeterli — yeni ürün almayın" in selector
    assert "Fiyat, stok, satıcı, puan, yorum, teslimat veya garanti bilgisi yayımlanmaz" in selector

    test_center = PAGES["/sektor-rehberi/kombi-elektrik-kesintisi-30-90-gun-test-merkezi/"].read_text(encoding="utf-8")
    assert test_center.count('class="task"') == 6
    assert "30 günlük kontrol ICS" in test_center
    assert "90 günlük prova ICS" in test_center
    assert "application/json" in test_center and "text/calendar" in test_center
    assert "localStorage" not in test_center
    assert "fetch(" not in test_center
    assert "resmî bakım periyodu değildir" in test_center

    audit = AUDIT.read_text(encoding="utf-8")
    assert "Seçilen en yüksek potansiyelli üç aksiyon" in audit
    assert "Mevcut düzen yeterliyse: yeni ürün almayın" in audit
    assert "Product / Offer / AggregateRating: kullanılmaz" in audit

    print("PASS: kombi yedek enerji v191 güven, routing, affiliate ve tekrar ziyaret sözleşmesi")


if __name__ == "__main__":
    main()
