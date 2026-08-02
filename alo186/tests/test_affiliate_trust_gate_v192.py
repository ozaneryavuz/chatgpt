#!/usr/bin/env python3
"""Fail-closed trust contract for ALO186 direct affiliate category journeys."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
COMMERCE_ROOT = ROOT / "alo186/amazon-elektrik-urunleri"
RUNTIME = COMMERCE_ROOT / "commercial.js"
HUB = COMMERCE_ROOT / "index.html"

COERCIVE_PHRASES = (
    "ilk sepetinizi kurun",
    "hemen satın al",
    "stoklar tükenmeden",
    "son fırsat",
    "kaçırmayın",
    "en düşük fiyat",
    "garantili kazanç",
)


def compact(value: str) -> str:
    return " ".join(value.casefold().split())


def main() -> None:
    runtime = RUNTIME.read_text(encoding="utf-8")
    hub = HUB.read_text(encoding="utf-8")

    assert 'data-affiliate-url="${escapeAttr(product.url)}"' in runtime
    assert 'href="${escapeAttr(product.url)}"' not in runtime
    assert runtime.count('data-affiliate-confirm=') == 3
    assert "checks.every((checkbox) => checkbox.checked)" in runtime
    assert "link.href = link.dataset.affiliateUrl" in runtime
    assert "link.rel = 'sponsored nofollow noopener'" in runtime
    assert "affiliate_gate_passed" in runtime

    assert "Mevcut ürünüm yeterli — satın alma yapmayacağım" in runtime
    assert "affiliate_no_buy_selected" in runtime
    assert "existing_product_sufficient" in runtime
    assert "kişisel veri toplamaz" in runtime
    assert "tarayıcıda saklamaz" in runtime

    hub_text = compact(hub)
    assert re.search(
        r"mevcut.{0,120}(?:yeterli|ihtiyacı karşılıyorsa).{0,120}(?:satın alma yok|yeni ürün önerilmez|ürün yoluna ilerlenir)",
        hub_text,
    )
    assert "fiyat" in hub_text and "stok" in hub_text and "kopyalanmaz" in hub_text
    assert "aktif tehlikede satış yolu kapalı" in hub_text
    assert "/akilli-urun-secimi" in hub
    assert "amazon gelir ortağı" in hub_text
    for phrase in COERCIVE_PHRASES:
        assert phrase not in hub_text, f"Baskıcı ticari ifade bulundu: {phrase}"

    direct_pages: list[Path] = []
    for page in sorted(COMMERCE_ROOT.glob("*/index.html")):
        html = page.read_text(encoding="utf-8")
        if "data-category=" not in html or "data-fresh-products" not in html:
            continue
        direct_pages.append(page)
        lowered = compact(html)

        assert "commercial.js" in html, f"Ortak güven runtime'ı eksik: {page}"
        assert "affiliate-disclosure" in html, f"Affiliate açıklaması eksik: {page}"
        assert "satış ortaklığı" in lowered, f"Affiliate ilişkisi görünür değil: {page}"
        assert "fiyat" in lowered and "stok" in lowered, f"Güncel mağaza veri sınırı eksik: {page}"
        assert "/hesaplama/" in html or "/akilli-urun-secimi" in html, f"Teknik araç yolu eksik: {page}"
        assert re.search(
            r"satın almama|mevcut.{0,100}(?:yeterli|karşılıyorsa)|yeni ürün almak gerekmeyebilir",
            lowered,
        ), f"Satın almama sonucu eksik: {page}"
        assert not re.search(
            r'"@type"\s*:\s*"(?:Product|Offer|AggregateRating)"',
            html,
            flags=re.IGNORECASE,
        ), f"Doğrulanmamış ticari şema bulundu: {page}"
        for phrase in COERCIVE_PHRASES:
            assert phrase not in lowered, f"Baskıcı ticari ifade bulundu ({phrase}): {page}"

    assert direct_pages, "Üçlü kapıyı kullanan doğrudan ürün kategorisi bulunamadı."

    print(
        "PASS: affiliate bağlantıları üçlü ihtiyaç/uygunluk/açıklama kapısından sonra açılıyor; "
        f"{len(direct_pages)} doğrudan kategori teknik araç, satın almama, açıklama ve şema sınırını geçti."
    )


if __name__ == "__main__":
    main()
