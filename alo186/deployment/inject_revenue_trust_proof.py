from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

TRUST_ROUTE = "/gelir-ve-bagimsizlik/"
SAMPLE_ROUTE = "/ornek-teslimler/"
MONITOR_ROUTE = "/hizmetler/elektrik-surekliligi-izleme/"
CORPORATE_ROUTE = "/kurumsal-elektrik-surekliligi-on-degerlendirme"
MARKER = 'data-alo186-revenue-proof="true"'
GATEWAY_MARKER = 'data-alo186-trust-proof-gateway="true"'


def normalize_base_path(value: str) -> str:
    cleaned = str(value or "").strip()
    if not cleaned or cleaned == "/":
        return ""
    return "/" + cleaned.strip("/")


def canonical_path(value: str, base_path: str) -> str:
    raw = "/" + str(value or "").strip().strip("/")
    trailing = str(value or "").strip().endswith("/") and raw != "/"
    if base_path and raw.startswith(base_path + "/"):
        raw = raw[len(base_path) :]
    if trailing and raw != "/" and not raw.endswith("/"):
        raw += "/"
    return raw


def public_url(base_path: str, route: str) -> str:
    route = "/" + route.lstrip("/")
    return f"{base_path}{route}" if base_path else route


def route_file(site: Path, route: str) -> Path:
    return site / route.strip("/") / "index.html"


def insert_before_end(html: str, block: str) -> tuple[str, bool]:
    if MARKER in html:
        return html, False
    for marker in ("</footer>", "</body>"):
        index = html.lower().rfind(marker)
        if index >= 0:
            return html[:index] + block + html[index:], True
    raise RuntimeError("HTML kapanış etiketi bulunamadı")


def trust_block(base_path: str, route_type: str, affiliate: bool) -> str:
    trust = public_url(base_path, TRUST_ROUTE)
    samples = public_url(base_path, SAMPLE_ROUTE)
    monitoring = public_url(base_path, MONITOR_ROUTE)
    if affiliate:
        lead = "Bu sayfadaki uygun satış ortaklığı bağlantıları ALO186'e komisyon kazandırabilir; komisyon teknik sıralamayı ve satın almama sonucunu değiştirmez."
    elif route_type == "service":
        lead = "Bu sayfa ücretli teknik hizmeti tanımlar; çalışma yalnız kapsam, ücret ve teslim koşulları yazılı olarak teyit edildikten sonra başlar."
    else:
        lead = "ALO186 bağımsız bilgi platformudur; resmî kurum, EDAŞ veya ürün satıcısı değildir."
    return f'''<aside {MARKER} style="max-width:1120px;margin:24px auto;padding:18px 20px;border:1px solid #b9c8dd;border-radius:16px;background:#f4f8fd;color:#21344f;font:15px/1.55 system-ui,-apple-system,Segoe UI,sans-serif"><strong style="display:block;color:#071631;margin-bottom:5px">Gelir, bağımsızlık ve teslim kanıtı</strong><p style="margin:0 0 9px">{lead} Mevcut ekipman güvenli ve yeterliyse yeni ürün veya hizmet satın almak zorunlu değildir.</p><div style="display:flex;flex-wrap:wrap;gap:12px"><a style="display:inline-flex;align-items:center;min-height:44px;color:#174bb9;font-weight:800" href="{trust}">Gelir ve bağımsızlık kuralları →</a><a style="display:inline-flex;align-items:center;min-height:44px;color:#174bb9;font-weight:800" href="{samples}">Kurgusal örnek teslimler →</a><a style="display:inline-flex;align-items:center;min-height:44px;color:#174bb9;font-weight:800" href="{monitoring}">Dönemsel teknik takip →</a></div></aside>'''


def gateway_block(base_path: str) -> str:
    trust = public_url(base_path, TRUST_ROUTE)
    samples = public_url(base_path, SAMPLE_ROUTE)
    monitoring = public_url(base_path, MONITOR_ROUTE)
    return f'''<section {GATEWAY_MARKER} style="max-width:1120px;margin:28px auto;padding:24px;border:1px solid #dce5ef;border-radius:22px;background:#fff;font:16px/1.55 system-ui,-apple-system,Segoe UI,sans-serif"><div style="max-width:820px"><span style="color:#174bb9;font-size:.78rem;font-weight:900;letter-spacing:.07em;text-transform:uppercase">Güven ve sürdürülebilir gelir</span><h2 style="margin:7px 0 10px;color:#071631;font-size:clamp(1.7rem,4vw,2.5rem)">Nasıl gelir elde edildiğini, hangi teslimi alacağınızı ve ne zaman geri dönmeniz gerektiğini görün.</h2></div><div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px;margin-top:18px"><a style="display:block;padding:18px;border:1px solid #dce5ef;border-radius:16px;color:#172137;text-decoration:none" href="{trust}"><strong style="color:#071631">Gelir ve Bağımsızlık</strong><p>Affiliate, ücretli hizmet ve sponsorluk kurallarını inceleyin.</p><b style="color:#174bb9">Şeffaflık merkezini aç →</b></a><a style="display:block;padding:18px;border:1px solid #dce5ef;border-radius:16px;color:#172137;text-decoration:none" href="{samples}"><strong style="color:#071631">Örnek Teknik Teslimler</strong><p>Gerçek müşteri iddiası taşımayan kurgusal rapor, matris ve fizibilite örneklerini görün.</p><b style="color:#174bb9">Teslim örneklerini aç →</b></a><a style="display:block;padding:18px;border:1px solid #dce5ef;border-radius:16px;color:#172137;text-decoration:none" href="{monitoring}"><strong style="color:#071631">Süreklilik İzleme</strong><p>Kesinti, bakım, kanıt ve açık aksiyonları aylık veya üç aylık döngüde yenileyin.</p><b style="color:#174bb9">Tekrarlayan hizmeti aç →</b></a></div></section>'''


def inject_gateway(site: Path, relative: Path, base_path: str) -> bool:
    path = site / relative
    if not path.is_file():
        return False
    html = path.read_text(encoding="utf-8", errors="ignore")
    if GATEWAY_MARKER in html:
        return False
    marker = "</main>"
    index = html.lower().rfind(marker)
    if index < 0:
        return False
    html = html[:index] + gateway_block(base_path) + html[index:]
    path.write_text(html, encoding="utf-8")
    return True


def update_release(site: Path, injected: int, gateway_cards: int, target_count: int) -> None:
    for filename in ("alo186-release.json", "pages-release.json"):
        path = site / filename
        if not path.is_file():
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["revenueTrustProofGrowth"] = {
            "version": 1,
            "trustRoute": TRUST_ROUTE,
            "sampleDeliverablesRoute": SAMPLE_ROUTE,
            "recurringServiceRoute": MONITOR_ROUTE,
            "targetRouteCount": target_count,
            "trustPanelsInjectedThisPass": injected,
            "gatewaySectionsInjectedThisPass": gateway_cards,
            "rawPersonalDataCollected": False,
            "automaticRenewal": False,
            "directStoreLinksAdded": 0,
            "commercialRankingFieldsUsed": [],
        }
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def recompute(site: Path) -> None:
    path = site / "checksums.sha256"
    if path.exists():
        path.unlink()
    lines = [
        f"{hashlib.sha256(item.read_bytes()).hexdigest()}  {item.relative_to(site).as_posix()}"
        for item in sorted(candidate for candidate in site.rglob("*") if candidate.is_file())
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(site: Path, base_path: str = "") -> dict:
    site = site.resolve()
    base_path = normalize_base_path(base_path)
    release = json.loads((site / "alo186-release.json").read_text(encoding="utf-8"))
    injected = 0
    target_count = 0
    missing: list[str] = []

    for item in release.get("routes", []):
        route = canonical_path(item.get("canonicalPath"), base_path)
        route_type = str(item.get("type") or "")
        affiliate = route == "/amazon-elektrik-urunleri" or route.startswith("/amazon-elektrik-urunleri/")
        target = affiliate or route_type == "service" or route == CORPORATE_ROUTE
        if not target or route in {TRUST_ROUTE, SAMPLE_ROUTE, MONITOR_ROUTE}:
            continue
        target_count += 1
        path = route_file(site, route)
        if not path.is_file():
            missing.append(route)
            continue
        html = path.read_text(encoding="utf-8", errors="ignore")
        updated, changed = insert_before_end(html, trust_block(base_path, route_type, affiliate))
        if changed:
            path.write_text(updated, encoding="utf-8")
            injected += 1

    if missing:
        raise FileNotFoundError("Gelir/güven paneli uygulanacak rotalar eksik: " + ", ".join(sorted(missing)))

    gateway_cards = int(inject_gateway(site, Path("index.html"), base_path))
    gateway_cards += int(inject_gateway(site, Path("elektrik-portali/index.html"), base_path))
    update_release(site, injected, gateway_cards, target_count)
    recompute(site)
    return {
        "ok": True,
        "basePath": base_path,
        "targetRouteCount": target_count,
        "trustPanelsInjected": injected,
        "gatewaySectionsInjected": gateway_cards,
        "trustRoute": public_url(base_path, TRUST_ROUTE),
        "sampleDeliverablesRoute": public_url(base_path, SAMPLE_ROUTE),
        "recurringServiceRoute": public_url(base_path, MONITOR_ROUTE),
        "directStoreLinksAdded": 0,
        "automaticRenewal": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="ALO186 ticari yüzeylerine gelir şeffaflığı, örnek teslim ve tekrarlayan hizmet keşfi ekler.")
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--base-path", default="")
    args = parser.parse_args()
    print(json.dumps(run(args.site, args.base_path), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
