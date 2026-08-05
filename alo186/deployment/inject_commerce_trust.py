from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

ROUTES = (
    "/amazon-elektrik-urunleri",
    "/amazon-elektrik-urunleri/powerbank-usb-c-secimi",
    "/amazon-elektrik-urunleri/akim-korumali-grup-priz-secimi",
    "/amazon-elektrik-urunleri/modem-mini-ups-secimi",
    "/amazon-elektrik-urunleri/acil-aydinlatma-duman-alarmi",
)
MARKER = 'data-alo186-commercial-trust="true"'
DISCLOSURE = re.compile(
    r'(<div\b[^>]*class=["\'][^"\']*\baffiliate-disclosure\b[^"\']*["\'][^>]*>.*?</div>)',
    re.I | re.S,
)
LEGACY_BOUNDARY = re.compile(
    r'(<div\b[^>]*data-alo186-commerce-trust(?:-[^=\s>]+)?=["\']true["\'][^>]*>.*?</div>)',
    re.I | re.S,
)
AFFILIATE_DISCLOSURE = '''<div class="affiliate-disclosure" data-alo186-affiliate-disclosure="true"><strong>Amazon Türkiye satış ortaklığı açıklaması:</strong> Bu sayfanın ilerletebildiği Amazon Türkiye bağlantıları satış ortaklığı bağlantısıdır. ALO186 nitelikli satın alımlardan komisyon kazanabilir; ürün sınıfları komisyon oranına göre sıralanmaz. Fiyat, stok, puan ve garanti bilgileri ALO186 tarafından doğrulanmış kabul edilmez; güncel bilgi mağazada kontrol edilmelidir.</div>'''
NOTICE = '''<div class="affiliate-disclosure commercial-trust-boundary" data-alo186-commercial-trust="true"><strong>Bağımsızlık ve satın almama sınırı:</strong> ALO186 bağımsız bilgi platformudur; EDAŞ, kamu kurumu veya ürün satıcısı değildir. Mevcut ekipman ihtiyacı güvenli biçimde karşılıyorsa yeni ürün satın almayın.</div>'''


def route_file(site: Path, route: str) -> Path:
    return site / route.strip("/") / "index.html"


def recompute(site: Path) -> None:
    path = site / "checksums.sha256"
    if path.exists():
        path.unlink()
    lines = [
        f"{hashlib.sha256(item.read_bytes()).hexdigest()}  {item.relative_to(site).as_posix()}"
        for item in sorted(candidate for candidate in site.rglob("*") if candidate.is_file())
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def update_release(site: Path, injected: int, restored_disclosures: int) -> None:
    for name in ("alo186-release.json", "pages-release.json"):
        path = site / name
        if not path.is_file():
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["commercialTrustBoundary"] = {
            "version": 2,
            "routeCount": len(ROUTES),
            "injectedThisPass": injected,
            "restoredAffiliateDisclosures": restored_disclosures,
            "officialInstitutionImpression": False,
            "affiliateRelationshipVisible": True,
            "noBuyOutcomeVisible": True,
            "staticBoundary": True,
        }
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def tag_legacy_boundary(html: str) -> tuple[str, bool]:
    match = LEGACY_BOUNDARY.search(html)
    if not match:
        return html, False
    tagged = match.group(1).replace(">", f" {MARKER}>", 1)
    return html[: match.start()] + tagged + html[match.end() :], True


def run(site: Path, base_path: str = "") -> dict:
    del base_path  # Metin ve canonical kimlik base-path'ten bağımsızdır.
    site = site.resolve()
    injected = 0
    restored_disclosures = 0
    checked = 0
    missing: list[str] = []
    for route in ROUTES:
        path = route_file(site, route)
        if not path.is_file():
            missing.append(route)
            continue
        checked += 1
        html = path.read_text(encoding="utf-8", errors="ignore")
        disclosure = DISCLOSURE.search(html)

        # Bazı üretim enjektörleri ticari metni sadeleştirirken mevcut v212 güven
        # sınırını korur. Affiliate açıklaması kaybolduysa fail-open davranmak
        # yerine görünür ve doğrulanabilir açıklamayı güven sınırının önüne geri koy.
        if not disclosure:
            boundary = LEGACY_BOUNDARY.search(html)
            if not boundary and MARKER not in html:
                raise RuntimeError(f"Ticari sayfada affiliate açıklaması bulunamadı: {route}")
            insert_at = boundary.start() if boundary else html.find(MARKER)
            if insert_at < 0:
                raise RuntimeError(f"Ticari sayfada güven sınırı bulunamadı: {route}")
            html = html[:insert_at] + AFFILIATE_DISCLOSURE + "\n  " + html[insert_at:]
            restored_disclosures += 1

        if MARKER not in html:
            html, tagged = tag_legacy_boundary(html)
            if not tagged:
                disclosure = DISCLOSURE.search(html)
                if not disclosure:
                    raise RuntimeError(f"Ticari sayfada affiliate açıklaması bulunamadı: {route}")
                html = html[: disclosure.end()] + "\n  " + NOTICE + html[disclosure.end() :]
            injected += 1

        path.write_text(html, encoding="utf-8")

    if missing:
        raise FileNotFoundError("Ticari güven sınırı uygulanacak rotalar eksik: " + ", ".join(missing))
    update_release(site, injected, restored_disclosures)
    recompute(site)
    return {
        "ok": True,
        "checkedRoutes": checked,
        "injectedRoutes": injected,
        "restoredAffiliateDisclosures": restored_disclosures,
        "remainingWithoutBoundary": 0,
        "officialInstitutionImpression": False,
        "affiliateRelationshipVisible": True,
        "noBuyOutcomeVisible": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="ALO186 ticari kategori sayfalarına statik bağımsızlık ve satın almama sınırı ekler.")
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--base-path", default="")
    args = parser.parse_args()
    print(json.dumps(run(args.site, args.base_path), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
