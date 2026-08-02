from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PAGE_DIR = ROOT / "alo186" / "elektrik-dayaniklilik-karti"
HTML_PATH = PAGE_DIR / "index.html"
CSS_PATH = PAGE_DIR / "styles.css"
JS_PATH = PAGE_DIR / "app.js"
OVERLAY_PATH = ROOT / "alo186" / "deployment" / "routing-overlays" / "zero-traffic-activation-v224.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def test_route_contract() -> None:
    overlay = json.loads(OVERLAY_PATH.read_text(encoding="utf-8"))
    require(overlay["version"] == 224, "Routing overlay version 224 olmalı")
    require(overlay["generatedAt"] == "2026-08-03", "Routing tarihi sabit ve açık olmalı")
    require(len(overlay["routes"]) == 1, "MVP tek canonical rota üretmeli")
    route = overlay["routes"][0]
    require(route["source"] == "alo186/elektrik-dayaniklilik-karti/index.html", "Kaynak rota yanlış")
    require(route["canonicalPath"] == "/elektrik-dayaniklilik-karti/", "Canonical rota yanlış")
    require(route["type"] == "tool", "Rota tool sınıfında olmalı")


def test_html_contract() -> None:
    html = HTML_PATH.read_text(encoding="utf-8")
    lowered = html.casefold()
    require('data-alo186-zero-traffic-v224="true"' in html, "Sıfır trafik aktivasyon işareti eksik")
    require('<link rel="canonical" href="https://alo186.com/elektrik-dayaniklilik-karti/">' in html, "Apex canonical eksik")
    require("Elektrik Dayanıklılık Kartı" in html, "Ürün adı eksik")
    require("2 dakika" in html, "Hızlı aktivasyon vaadi eksik")
    require('id="assessment"' in html and 'id="results"' in html, "Değerlendirme veya sonuç yüzeyi eksik")
    require('id="immediateDanger"' in html and 'href="tel:112"' in html, "112 güvenlik kapısı eksik")
    require("186" in html and "/edas-bul" in html, "186 / resmî EDAŞ yönü eksik")
    require('id="shareButton"' in html and 'id="copyButton"' in html, "Davet/paylaşım döngüsü eksik")
    require('id="relativeButton"' in html, "Yakın konumu aktivasyon döngüsü eksik")
    require("/hesaplama/elektrik-surekliligi-pasaportu/" in html, "B2B pasaport handoff'u eksik")
    require("Ürün önermez" in html and "Satın alma varsayımı yok" in html, "Satın almama/güven sınırı eksik")
    require("WebApplication" in html and "FAQPage" in html and "BreadcrumbList" in html, "Gerekli görünür içerikle uyumlu schema eksik")

    forbidden_commerce = ("amazon.", "amzn.", "affiliate", "salesrank", "aggregaterating")
    for token in forbidden_commerce:
        require(token not in lowered, f"Aktivasyon rotasında ticari token yasak: {token}")
    require('"@type":"Product"'.casefold() not in lowered, "Product schema yasak")
    require('"@type":"Offer"'.casefold() not in lowered, "Offer schema yasak")

    form_names = set(re.findall(r'<(?:input|select|textarea)\b[^>]*\bname\s*=\s*["\']([^"\']+)["\']', html, re.IGNORECASE))
    allowed_form_names = {"locationType", "lighting", "phone", "internet", "cold", "contact", "test", "official"}
    require(form_names <= allowed_form_names, f"Kişisel veya beklenmeyen form alanı bulundu: {sorted(form_names - allowed_form_names)}")
    require("<textarea" not in lowered, "Serbest metin alanı MVP'de olmamalı")
    require('type="text"' not in lowered and 'type="email"' not in lowered and 'type="tel"' not in lowered,
            "Kişisel veri toplayabilecek metin alanları yasak")


def test_javascript_contract() -> None:
    js = JS_PATH.read_text(encoding="utf-8")
    required_tokens = (
        "resilience_card_start",
        "resilience_card_complete",
        "resilience_card_share",
        "resilience_card_business_handoff",
        "resilience_card_official_channel",
        "window.dataLayer",
        "window.location.hash",
        "navigator.share",
        "navigator.clipboard",
        "localStorage",
        "storageGet",
        "storageSet",
        "storageRemove",
        "TextEncoder",
        "TextDecoder",
        "history.replaceState",
    )
    for token in required_tokens:
        require(token in js, f"JS aktivasyon sözleşmesi eksik: {token}")

    forbidden_network = ("fetch(", "XMLHttpRequest", "sendBeacon", "WebSocket(", "EventSource(")
    for token in forbidden_network:
        require(token not in js, f"Yanıtları dışarı gönderebilecek ağ API'si yasak: {token}")

    require("dataLayer.push(answers" not in js and "payload: answers" not in js,
            "Analitik katmanına ham yanıtlar yazılamaz")
    require("localStorage.setItem(STORAGE_KEY, JSON.stringify(answers" not in js,
            "Yerel depolamaya ham yanıtlar yazılamaz")

    result = subprocess.run(["node", "--check", str(JS_PATH)], check=False, capture_output=True, text=True)
    require(result.returncode == 0, f"JavaScript sözdizimi geçersiz: {result.stderr}")


def test_css_contract() -> None:
    css = CSS_PATH.read_text(encoding="utf-8")
    require("@media print" in css, "Yazdırılabilir paylaşım kartı stili eksik")
    require("@media (max-width: 720px)" in css, "Mobil sözleşme eksik")
    require("min-height: 44px" in css, "Dokunma hedefi en az 44px olmalı")
    require(":focus-visible" in css, "Klavye odak görünürlüğü eksik")
    require("prefers-reduced-motion" in css, "Azaltılmış hareket tercihi eksik")


def main() -> None:
    for path in (HTML_PATH, CSS_PATH, JS_PATH, OVERLAY_PATH):
        require(path.is_file(), f"Dosya eksik: {path}")
    test_route_contract()
    test_html_contract()
    test_javascript_contract()
    test_css_contract()
    print(json.dumps({
        "version": 224,
        "canonical": "https://alo186.com/elektrik-dayaniklilik-karti/",
        "personalDataFields": 0,
        "directCommerceLinks": 0,
        "shareLoop": True,
        "relativeLocationLoop": True,
        "businessHandoff": True,
        "status": "passed",
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
