from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

VERSION = 214
TARGET = Path("hesaplama/index.html")
MARKER = 'data-alo186-intent-tools-run135="true"'
ROUTES = (
    "/hesaplama/elektrik-kesintisi-tazminat-kontrolu/",
    "/hesaplama/ges-kesinti-yedekleme-mimarisi/",
    "/hesaplama/ev-sarj-kacak-akim-koruma-secici/",
)


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
        ("Kesinti · 12 saat · yıllık kayıt · 30 gün", "Elektrik Kesintisi Tazminat Kontrolü", "Uzun süreli ve yıllık kesinti tazminatı yollarını cihaz hasarı sürecinden ayırın; saklanacak kanıtları görün.", ROUTES[0], "Tazminat yolunu kontrol et"),
        ("GES · anti-islanding · batarya · EPS", "GES Kesinti Yedekleme Mimarisi", "İnverter topolojisi, kritik yük, batarya, transfer ve jeneratör katmanını ürün seçmeden önce doğrulayın.", ROUTES[1], "Yedekleme mimarisini oluştur"),
        ("EV · Mode 2/3 · 6 mA DC · RCD", "EV Şarj Kaçak Akım Koruma Seçici", "IC-CPD, RDC-DD, Tip A/Tip B ve ayrı devre gereğini tam model belgesi üzerinden ayırın.", ROUTES[2], "Koruma ön seçimini yap"),
    )
    return "\n".join(
        f'''<a class="tool-card" {MARKER} data-intent-tool="{index}" href="{public_url(base_path, route)}"><span class="eyebrow">{eyebrow}</span><h2>{title}</h2><p>{description}</p><b>{cta} →</b></a>'''
        for index, (eyebrow, title, description, route, cta) in enumerate(items, start=1)
    )


def inject_hub(path: Path, base_path: str) -> bool:
    if not path.is_file():
        raise FileNotFoundError(f"Hesaplama merkezi artifactı bulunamadı: {path}")
    text = path.read_text(encoding="utf-8", errors="strict")
    if MARKER in text:
        return False
    anchor = '<section id="araclar" class="tool-grid">'
    if anchor not in text:
        raise RuntimeError("Hesaplama merkezi araç grid başlangıcı bulunamadı")
    text = text.replace(anchor, anchor + "\n" + cards(base_path), 1)

    def raise_count(match: re.Match[str]) -> str:
        return f"{int(match.group(1)) + len(ROUTES)} çekirdek araç"

    text, replacements = re.subn(r"(\d+)\s+çekirdek araç", raise_count, text, count=1)
    if replacements != 1:
        raise RuntimeError("Hesaplama merkezi araç sayacı bulunamadı")
    path.write_text(text, encoding="utf-8")
    return True


def update_release(site: Path, base_path: str, injected: bool) -> None:
    path = site / "pages-release.json"
    if not path.is_file():
        return
    release = json.loads(path.read_text(encoding="utf-8"))
    release["intentToolsRun135"] = {
        "version": VERSION,
        "basePath": base_path,
        "hubInjected": injected,
        "toolCount": len(ROUTES),
        "routes": [public_url(base_path, route) for route in ROUTES],
        "directMarketplaceLinks": 0,
        "personalDataCollected": False,
        "failClosed": True,
    }
    path.write_text(json.dumps(release, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def recompute_checksums(site: Path) -> None:
    path = site / "checksums.sha256"
    if not path.exists():
        return
    path.unlink()
    lines = [
        f"{hashlib.sha256(item.read_bytes()).hexdigest()}  {item.relative_to(site).as_posix()}"
        for item in sorted(candidate for candidate in site.rglob("*") if candidate.is_file())
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def inject(site: Path, base_path: str) -> dict:
    base_path = normalize_base_path(base_path)
    injected = inject_hub(site / TARGET, base_path)
    update_release(site, base_path, injected)
    recompute_checksums(site)
    return {
        "ok": True,
        "version": VERSION,
        "basePath": base_path,
        "hubInjected": injected,
        "toolCount": len(ROUTES),
        "routes": [public_url(base_path, route) for route in ROUTES],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="ALO186 hesaplama merkezine run135 yüksek niyetli araç kartlarını ekler.")
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--base-path", default="")
    args = parser.parse_args()
    print(json.dumps(inject(args.site.resolve(), args.base_path), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
