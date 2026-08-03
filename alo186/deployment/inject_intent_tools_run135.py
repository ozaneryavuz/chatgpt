from __future__ import annotations

import argparse
import hashlib
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlsplit

import inject_private_search as private_search

VERSION = 216
TARGET = Path("hesaplama/index.html")
PRODUCT_HUB = Path("amazon-elektrik-urunleri/index.html")
MARKER = 'data-alo186-intent-tools-run135="true"'
MALFORMED_PRODUCT_URL = re.compile(
    r"https://alo186\.com/amazon-elektrik-urunleri(?=[a-z0-9])",
    re.I,
)
ROUTES = (
    "/hesaplama/elektrik-kesintisi-tazminat-kontrolu/",
    "/hesaplama/ges-kesinti-yedekleme-mimarisi/",
    "/hesaplama/ev-sarj-kacak-akim-koruma-secici/",
)
FORBIDDEN = (
    '"@type":"Product"',
    '"@type":"Offer"',
    '"@type":"AggregateRating"',
    "amazon.com.tr",
    "alo186rehber-21",
    "priceCurrency",
    "availability",
)
SECURE_CONDITION = "rawHours===''||!Number.isFinite(hours)||hours<0||hours>8760"
SECURE_VALID_ASSIGNMENT = "const valid=rawHours!==''&&Number.isFinite(hours)&&hours>=0&&hours<=8760;"
SECURE_VALID_BRANCH = "if(!valid)"


def normalize_base_path(value: str) -> str:
    cleaned = (value or "").strip()
    if not cleaned or cleaned == "/":
        return ""
    return "/" + cleaned.strip("/")


def public_url(base_path: str, route: str) -> str:
    route = "/" + route.lstrip("/")
    return f"{base_path}{route}" if base_path else route


def cards(base_path: str) -> str:
    items = (
        (
            "Kesinti · 12 saat · yıllık kayıt · 30 gün",
            "Elektrik Kesintisi Tazminat Kontrolü",
            "Uzun süreli ve yıllık kesinti tazminatı yollarını cihaz hasarı sürecinden ayırın; saklanacak kanıtları görün.",
            ROUTES[0],
            "Tazminat yolunu kontrol et",
        ),
        (
            "GES · anti-islanding · batarya · EPS",
            "GES Kesinti Yedekleme Mimarisi",
            "İnverter topolojisi, kritik yük, batarya, transfer ve jeneratör katmanını ürün seçmeden önce doğrulayın.",
            ROUTES[1],
            "Yedekleme mimarisini oluştur",
        ),
        (
            "EV · Mode 2/3 · 6 mA DC · RCD",
            "EV Şarj Kaçak Akım Koruma Seçici",
            "IC-CPD, RDC-DD, Tip A/Tip B ve ayrı devre gereğini tam model belgesi üzerinden ayırın.",
            ROUTES[2],
            "Koruma ön seçimini yap",
        ),
    )
    return "\n".join(
        f'<a class="tool-card" {MARKER} data-intent-tool="{index}" href="{public_url(base_path, route)}"><span class="eyebrow">{eyebrow}</span><h2>{title}</h2><p>{description}</p><b>{cta} →</b></a>'
        for index, (eyebrow, title, description, route, cta) in enumerate(items, start=1)
    )


def jsonld_payloads(html: str) -> list[dict]:
    payloads: list[dict] = []
    for raw in re.findall(
        r'<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        html,
        re.I | re.S,
    ):
        parsed = json.loads(raw)
        if isinstance(parsed, dict):
            payloads.append(parsed)
    return payloads


def normalize_product_hub_jsonld(site: Path) -> int:
    path = site / PRODUCT_HUB
    if not path.is_file():
        raise FileNotFoundError(f"Ürün merkezi artifactı bulunamadı: {path}")
    text = path.read_text(encoding="utf-8", errors="strict")
    updated, count = MALFORMED_PRODUCT_URL.subn(
        "https://alo186.com/amazon-elektrik-urunleri/",
        text,
    )
    if MALFORMED_PRODUCT_URL.search(updated):
        raise RuntimeError("Ürün merkezi JSON-LD rota ayıracı düzeltilemedi")
    payloads = jsonld_payloads(updated)
    if not payloads:
        raise RuntimeError("Ürün merkezi JSON-LD bulunamadı veya ayrıştırılamadı")
    if count:
        path.write_text(updated, encoding="utf-8")
    return count


def has_secure_outage_validation(text: str) -> bool:
    return SECURE_CONDITION in text or (
        SECURE_VALID_ASSIGNMENT in text and SECURE_VALID_BRANCH in text
    )


def harden_outage_input(site: Path) -> bool:
    path = site / ROUTES[0].strip("/") / "index.html"
    if not path.is_file():
        raise FileNotFoundError(f"Kesinti tazminatı aracı bulunamadı: {path}")
    text = path.read_text(encoding="utf-8", errors="strict")
    changed = False
    if 'max="8760"' not in text:
        text = text.replace('id="hours" type="number" min="0"', 'id="hours" type="number" min="0" max="8760"', 1)
        changed = True
    if "const rawHours=input.value.trim();" not in text:
        old = "const input=document.getElementById('hours');\n    const hours=Number(input.value);"
        new = "const input=document.getElementById('hours');\n    const rawHours=input.value.trim();\n    const hours=rawHours===''?Number.NaN:Number(rawHours);"
        if old not in text:
            raise RuntimeError("Kesinti süresi sayısal dönüşüm kalıbı bulunamadı")
        text = text.replace(old, new, 1)
        changed = True
    if not has_secure_outage_validation(text):
        old_condition = "!Number.isFinite(hours)||hours<0||hours>8760"
        if old_condition not in text:
            old_condition = "!Number.isFinite(h)||h<0"
        if old_condition not in text:
            raise RuntimeError("Kesinti süresi doğrulama kalıbı bulunamadı")
        text = text.replace(old_condition, SECURE_CONDITION, 1)
        changed = True
    if changed:
        path.write_text(text, encoding="utf-8")
    return changed


def inject_hub(path: Path, base_path: str) -> bool:
    if not path.is_file():
        raise FileNotFoundError(f"Hesaplama merkezi artifactı bulunamadı: {path}")
    text = path.read_text(encoding="utf-8", errors="strict")
    marker_count = text.count(MARKER)
    cards_added = False
    if marker_count == 0:
        anchor = '<section id="araclar" class="tool-grid">'
        if anchor not in text:
            raise RuntimeError("Hesaplama merkezi araç grid başlangıcı bulunamadı")
        text = text.replace(anchor, anchor + "\n" + cards(base_path), 1)
        cards_added = True
    elif marker_count != len(ROUTES):
        raise RuntimeError(f"Run135 kartları kısmi durumda: {marker_count}/{len(ROUTES)}")

    actual_tool_count = text.count('class="tool-card"')
    if actual_tool_count < len(ROUTES):
        raise RuntimeError("Hesaplama merkezi gerçek araç kartı sayısı geçersiz")
    counter_values = [int(value) for value in re.findall(r"(\d+)\s+çekirdek araç", text)]
    if not counter_values:
        raise RuntimeError("Hesaplama merkezi araç sayacı bulunamadı")
    if any(value != actual_tool_count for value in counter_values):
        text, replacements = re.subn(
            r"\d+\s+çekirdek araç",
            f"{actual_tool_count} çekirdek araç",
            text,
        )
        if replacements != len(counter_values):
            raise RuntimeError("Hesaplama merkezi statik ve çalışma zamanı sayaçları birlikte güncellenemedi")

    path.write_text(text, encoding="utf-8")
    return cards_added


def update_release(site: Path, base_path: str, added: bool, search_result: dict, product_hub_fixes: int) -> None:
    path = site / "pages-release.json"
    if not path.is_file():
        raise FileNotFoundError(f"Pages release kaydı bulunamadı: {path}")
    release = json.loads(path.read_text(encoding="utf-8"))
    hub = (site / TARGET).read_text(encoding="utf-8", errors="strict")
    hub_present = hub.count(MARKER) == len(ROUTES)
    release["intentToolsRun135"] = {
        "version": VERSION,
        "basePath": base_path,
        "hubInjected": hub_present,
        "hubAddedThisRun": added,
        "toolCount": len(ROUTES),
        "routes": [public_url(base_path, route) for route in ROUTES],
        "searchIndexGenerated": bool(search_result.get("ok")),
        "searchEntryCount": int(search_result.get("entryCount") or 0),
        "productHubJsonLdFixes": product_hub_fixes,
        "directMarketplaceLinks": 0,
        "personalDataCollected": False,
        "failClosed": True,
        "acceptedValidationForms": ["inline_fail_closed", "named_valid_boolean"],
    }
    path.write_text(json.dumps(release, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def recompute_checksums(site: Path) -> None:
    path = site / "checksums.sha256"
    if path.exists():
        path.unlink()
    lines = [
        f"{hashlib.sha256(item.read_bytes()).hexdigest()}  {item.relative_to(site).as_posix()}"
        for item in sorted(candidate for candidate in site.rglob("*") if candidate.is_file())
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def validate(site: Path, base_path: str) -> dict:
    base_path = normalize_base_path(base_path)
    for route in ROUTES:
        page = site / route.strip("/") / "index.html"
        if not page.is_file():
            raise FileNotFoundError(f"Run135 rota artifactta eksik: {page}")
        html = page.read_text(encoding="utf-8", errors="strict")
        for forbidden in FORBIDDEN:
            if forbidden in html:
                raise RuntimeError(f"{route}: yasak ticari alan bulundu: {forbidden}")

    outage = (site / ROUTES[0].strip("/") / "index.html").read_text(encoding="utf-8")
    for token in (
        "const rawHours=input.value.trim()",
        "rawHours===''?Number.NaN:Number(rawHours)",
        "30 gün",
    ):
        if token not in outage:
            raise RuntimeError(f"Kesinti aracı fail-closed sözleşmesi eksik: {token}")
    if not has_secure_outage_validation(outage):
        raise RuntimeError("Kesinti aracı fail-closed süre doğrulaması eksik")

    product_hub = (site / PRODUCT_HUB).read_text(encoding="utf-8", errors="strict")
    if MALFORMED_PRODUCT_URL.search(product_hub):
        raise RuntimeError("Ürün merkezi JSON-LD içinde birleşmiş rota bulundu")
    jsonld_payloads(product_hub)

    sitemap_path = site / "sitemap.xml"
    sitemap_root = ET.parse(sitemap_path).getroot()
    sitemap_paths = {
        (urlsplit((node.text or "").strip()).path.rstrip("/") or "/") + ("/" if urlsplit((node.text or "").strip()).path.rstrip("/") else "")
        for node in sitemap_root.findall(".//{*}loc")
        if (node.text or "").strip()
    }
    for route in ROUTES:
        if route not in sitemap_paths:
            raise RuntimeError(f"Run135 rota sitemapte eksik: {route}")

    search_path = site / "arama/search-index.json"
    search = json.loads(search_path.read_text(encoding="utf-8"))
    active = {
        str(item.get("canonicalPath") or "").rstrip("/") + "/"
        for item in search.get("entries", [])
        if isinstance(item, dict) and item.get("canonicalPath")
    }
    for route in ROUTES:
        if route not in active:
            raise RuntimeError(f"Run135 rota Teknik Arama indeksinde eksik: {route}")

    hub = (site / TARGET).read_text(encoding="utf-8", errors="strict")
    if hub.count(MARKER) != len(ROUTES):
        raise RuntimeError("Hesaplama Merkezi run135 kart sayısı 3 değil")
    for route in ROUTES:
        expected = public_url(base_path, route)
        if f'href="{expected}"' not in hub:
            raise RuntimeError(f"Hesaplama Merkezi kartı eksik: {expected}")
    actual_tool_count = hub.count('class="tool-card"')
    counter_values = [int(value) for value in re.findall(r"(\d+)\s+çekirdek araç", hub)]
    if not counter_values or any(value != actual_tool_count for value in counter_values):
        raise RuntimeError(
            f"Hesaplama Merkezi statik/çalışma zamanı sayaçları gerçek kart sayısıyla uyuşmuyor: "
            f"kart={actual_tool_count}, sayaçlar={counter_values}"
        )

    release = json.loads((site / "pages-release.json").read_text(encoding="utf-8"))
    contract = release.get("intentToolsRun135") or {}
    if int(contract.get("version") or 0) < VERSION:
        raise RuntimeError("pages-release intentToolsRun135 sürümü eksik")
    if contract.get("toolCount") != len(ROUTES) or contract.get("failClosed") is not True:
        raise RuntimeError("pages-release run135 güven sözleşmesi eksik")
    if contract.get("searchIndexGenerated") is not True:
        raise RuntimeError("pages-release run135 arama indeksi kanıtı eksik")
    return {
        "ok": True,
        "version": VERSION,
        "basePath": base_path,
        "routes": list(ROUTES),
        "searchEntryCount": len(active),
        "sitemapWellFormed": True,
        "productHubJsonLdValid": True,
        "hubToolCount": actual_tool_count,
        "outageValidationForm": "named_valid_boolean" if SECURE_VALID_ASSIGNMENT in outage else "inline_fail_closed",
    }


def inject(site: Path, base_path: str) -> dict:
    site = site.resolve()
    base_path = normalize_base_path(base_path)
    product_hub_fixes = normalize_product_hub_jsonld(site)
    outage_hardened = harden_outage_input(site)
    hub_added = inject_hub(site / TARGET, base_path)
    search_result = private_search.run(site, base_path)
    update_release(site, base_path, hub_added, search_result, product_hub_fixes)
    recompute_checksums(site)
    validation = validate(site, base_path)
    return {
        **validation,
        "outageInputHardened": outage_hardened,
        "hubAddedThisRun": hub_added,
        "productHubJsonLdFixes": product_hub_fixes,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="ALO186 run135 karar araçlarını keşif ve fail-closed yayın katmanına ekler.")
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--base-path", default="")
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()
    result = validate(args.site.resolve(), args.base_path) if args.validate_only else inject(args.site.resolve(), args.base_path)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
