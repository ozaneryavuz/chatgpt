from __future__ import annotations

import json
import re
from pathlib import Path

import prepare_github_pages_core as _core
from prepare_github_pages_core import *  # noqa: F401,F403


CANONICAL_ORIGIN = "https://alo186.com"
LEGACY_ORIGIN = "https://www.alo186.com"
LEGACY_HOST = "www.alo186.com"
CANONICAL_HOST = "alo186.com"
QUALITY_MARKER = 'data-alo186-technical-quality="true"'
QUALITY_STYLE = (
    '<style data-alo186-technical-quality="true">'
    ':where(img,svg,video,canvas,iframe){max-inline-size:100%}'
    ':where(img,video,canvas){block-size:auto}'
    ':where(pre,code){overflow-wrap:anywhere;white-space:pre-wrap}'
    ':where(table){max-inline-size:100%}'
    ':where(.table-wrap,[role="region"][aria-label*="tablo" i]){max-inline-size:100%;overflow-x:auto;-webkit-overflow-scrolling:touch}'
    ':where(a,button,input,select,textarea,summary){touch-action:manipulation}'
    '@media(max-width:720px){:where(h1,h2,h3,p,a,button,summary,th,td){overflow-wrap:anywhere}}'
    '@media(prefers-reduced-motion:reduce){html:focus-within{scroll-behavior:auto!important}}'
    '</style>'
)
DEVICE_DAMAGE_MARKER = 'data-alo186-device-damage-deadline="true"'
DEVICE_DAMAGE_ROUTE = "/haberler/elektrik-kesintisi-cihaz-hasari-edas-basvurusu/"
PRIMARY_START_MARKER = 'data-alo186-primary-start="true"'
PRIMARY_START_ROUTE = "/elektrik-durum-merkezi/"

# Canlı GitHub Pages katmanı apex alan adına 301 ile sonuçlanıyor. Üretilen
# canonical, JSON-LD, bridge ve gateway değerleri ilk andan itibaren son URL'yi
# göstermeli; aksi hâlde her sayfa www -> apex yönlendirme zinciri üretir.
_core.CANONICAL_ORIGIN = CANONICAL_ORIGIN
_original_gateway_html = _core.gateway_html
_original_prepare = _core.prepare

if PRIMARY_START_ROUTE not in _core.CRITICAL_ROUTES:
    _core.CRITICAL_ROUTES = (_core.CRITICAL_ROUTES[0], PRIMARY_START_ROUTE, *_core.CRITICAL_ROUTES[1:])


def gateway_html(base_path: str, noindex: bool) -> str:
    """Pages kökünü güvenli, kullanıcı niyetli ve devam edilebilir başlangıca dönüştürür."""

    html = _original_gateway_html(base_path, noindex)
    if DEVICE_DAMAGE_MARKER in html or PRIMARY_START_MARKER in html:
        return html

    style = (
        ".legal-deadline{margin:0 0 28px;padding:20px;border-radius:18px;"
        "background:#eef7ff;border:2px solid #4c7bd9}"
        ".legal-deadline strong{display:block;color:var(--navy);font-size:1.2rem}"
        ".legal-deadline p{margin:.55rem 0;color:#263a59}"
        ".legal-deadline a{display:inline-flex;align-items:center;min-height:44px;"
        "color:#174bb9;font-weight:900}"
        ".primary-start{grid-column:1/-1;min-height:220px;border:2px solid #28b9d8;"
        "background:linear-gradient(135deg,#071631,#12386a);color:#fff}"
        ".primary-start strong{color:#fff;font-size:clamp(1.55rem,4vw,2.35rem)}"
        ".primary-start p{color:#d7e7ff;max-width:720px}"
        ".primary-start span{color:#7fe6ff;font-size:1.05rem}"
        ".primary-start small{display:block;margin-bottom:8px;color:#7fe6ff;font-weight:900;"
        "text-transform:uppercase;letter-spacing:.08em}"
    )
    if "</style>" not in html:
        raise RuntimeError("Pages gateway inline stil kapanışı bulunamadı.")
    html = html.replace("</style>", style + "</style>", 1)

    html = html.replace(
        '<h1>Elektrik sorununda doğru sonraki adım.</h1><p class="lead">Kesinti, cihaz hasarı, yedek güç veya elektrik güvenliği konusunda önce riski ayırın; sonra resmî kanal, ücretsiz hesaplayıcı veya teknik rehbere ilerleyin.</p>',
        '<h1>60 saniyede doğru elektrik rotası.</h1><p class="lead">Belirtiyi seçin; ALO186 önce can güvenliğini, sonra 112, 186, EDAŞ, elektrikçi, kanıt ve yedek güç seçeneklerini ayırsın. Kişisel veri istemez, resmî kayıt oluşturmaz.</p>',
        1,
    )

    guide_url = _core.public_url(base_path, DEVICE_DAMAGE_ROUTE)
    notice = (
        f'<section class="legal-deadline" {DEVICE_DAMAGE_MARKER} '
        'aria-labelledby="device-damage-deadline">'
        '<strong id="device-damage-deadline">Cihaz hasarında başvuru süresi 10 iş günüdür</strong>'
        '<p>Dağıtım şebekesinden kaynaklandığını düşündüğünüz cihaz veya teçhizat hasarı için '
        'zararın ortaya çıktığı tarihten itibaren <strong>10 iş günü içinde</strong> ilgili dağıtım '
        'şirketinin resmî kanalına başvurun. ALO186 başvuru, ihbar veya hasar kaydı almaz.</p>'
        f'<a href="{guide_url}">Belge ve başvuru rehberini aç →</a>'
        '</section>'
    )
    status_url = _core.public_url(base_path, PRIMARY_START_ROUTE)
    primary = (
        f'<a class="card primary-start" {PRIMARY_START_MARKER} href="{status_url}">'
        '<small>Önerilen başlangıç</small>'
        '<strong>Elektrik Durum Merkezi</strong>'
        '<p>Kesinti, gerilim, sayaç, pano, cihaz hasarı veya UPS–jeneratör olayını dört kısa adımda sınıflandırın. '
        'Tehlike varsa ticari yol kapanır; son kaydınıza daha sonra aynı cihazdan devam edebilirsiniz.</p>'
        '<span>60 saniyelik yönlendirmeyi başlat →</span>'
        '</a>'
    )
    anchor = '<section class="grid" aria-label="ALO186 hızlı başlangıç">'
    if anchor not in html:
        raise RuntimeError("Pages gateway hızlı başlangıç alanı bulunamadı.")
    html = html.replace(anchor, notice + "\n" + anchor + "\n" + primary, 1)
    return html


def normalize_live_origin(site: Path) -> int:
    """Yayın artifactındaki bütün mutlak site referanslarını gerçek son hosta taşır."""

    changed = 0
    allowed_suffixes = {".html", ".htm", ".xml", ".txt", ".json", ".js", ".css", ".webmanifest"}
    for path in sorted(site.rglob("*")):
        if not path.is_file() or (path.suffix.lower() not in allowed_suffixes and path.name not in {"robots.txt", "sitemap.xml"}):
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        updated = text.replace(LEGACY_ORIGIN, CANONICAL_ORIGIN).replace(LEGACY_HOST, CANONICAL_HOST)
        if updated != text:
            path.write_text(updated, encoding="utf-8")
            changed += 1
    return changed


def inject_quality_hardening(site: Path) -> int:
    """Görsel, tablo ve uzun metinlerin dar görünümde sayfa genişliğini aşmasını önler."""

    changed = 0
    for path in sorted(site.rglob("*.html")):
        html = path.read_text(encoding="utf-8", errors="ignore")
        if QUALITY_MARKER in html:
            continue
        if "</head>" not in html:
            raise RuntimeError(f"HTML head kapanışı bulunamadı: {path.relative_to(site)}")
        path.write_text(html.replace("</head>", QUALITY_STYLE + "\n</head>", 1), encoding="utf-8")
        changed += 1
    return changed


def validate_live_quality_contracts(site: Path) -> None:
    failures: list[str] = []
    indexable_count = 0
    for path in sorted(site.rglob("*.html")):
        html = path.read_text(encoding="utf-8", errors="ignore")
        relative = path.relative_to(site).as_posix()
        if QUALITY_MARKER not in html:
            failures.append(f"Responsive kalite stili eksik: {relative}")
        if LEGACY_HOST in html or LEGACY_ORIGIN in html:
            failures.append(f"www host artifactta kaldı: {relative}")
        robots_match = re.search(r'<meta\s+name=["\']robots["\']\s+content=["\']([^"\']+)', html, re.I)
        noindex = bool(robots_match and "noindex" in robots_match.group(1).casefold())
        if noindex:
            continue
        indexable_count += 1
        canonicals = re.findall(r'<link\s+rel=["\']canonical["\']\s+href=["\']([^"\']+)', html, re.I)
        if len(canonicals) != 1:
            failures.append(f"Indexlenebilir sayfada canonical sayısı {len(canonicals)}: {relative}")
        elif not canonicals[0].startswith(CANONICAL_ORIGIN + "/"):
            failures.append(f"Canonical apex hostta değil: {relative} -> {canonicals[0]}")

    robots_path = site / "robots.txt"
    sitemap_path = site / "sitemap.xml"
    if not robots_path.is_file() or f"Sitemap: {CANONICAL_ORIGIN}/sitemap.xml" not in robots_path.read_text(encoding="utf-8"):
        failures.append("robots.txt apex sitemap adresini taşımıyor")
    if not sitemap_path.is_file():
        failures.append("sitemap.xml eksik")
    else:
        sitemap = sitemap_path.read_text(encoding="utf-8")
        if LEGACY_HOST in sitemap or LEGACY_ORIGIN in sitemap:
            failures.append("sitemap.xml www host taşıyor")
        if f"<loc>{CANONICAL_ORIGIN}/" not in sitemap:
            failures.append("sitemap.xml apex canonical URL taşımıyor")

    release_path = site / "pages-release.json"
    if release_path.is_file():
        release = json.loads(release_path.read_text(encoding="utf-8"))
        if release.get("canonicalHost") != CANONICAL_ORIGIN:
            failures.append("pages-release canonicalHost apex değil")
        if release.get("customDomain") != CANONICAL_HOST:
            failures.append("pages-release customDomain apex değil")
    else:
        failures.append("pages-release.json eksik")

    if indexable_count == 0:
        failures.append("Indexlenebilir HTML bulunamadı")
    if failures:
        raise RuntimeError("Canlı teknik kalite sözleşmesi başarısız:\n- " + "\n- ".join(failures[:80]))


def validate_root_legal_deadline(site: Path, base_path: str) -> None:
    root = site / "index.html"
    if not root.is_file():
        raise FileNotFoundError(f"Pages kök sayfası eksik: {root}")
    html = root.read_text(encoding="utf-8")
    required = (
        DEVICE_DAMAGE_MARKER,
        "Cihaz hasarında başvuru süresi 10 iş günüdür",
        "zararın ortaya çıktığı tarihten itibaren <strong>10 iş günü içinde</strong>",
        "ALO186 başvuru, ihbar veya hasar kaydı almaz",
        f'href="{_core.public_url(base_path, DEVICE_DAMAGE_ROUTE)}"',
    )
    missing = [item for item in required if item not in html]
    if missing:
        raise RuntimeError("Pages kök hukuki süre koruması eksik: " + ", ".join(missing))
    if re.search(r"\b30\s*(?:takvim\s*)?gün\b", html, re.IGNORECASE):
        raise RuntimeError("Pages kökünde cihaz hasarı bağlamında 30 gün ifadesi kalamaz.")


def validate_root_primary_start(site: Path, base_path: str) -> None:
    root = site / "index.html"
    html = root.read_text(encoding="utf-8")
    required = (
        PRIMARY_START_MARKER,
        "60 saniyede doğru elektrik rotası",
        "Elektrik Durum Merkezi",
        "Tehlike varsa ticari yol kapanır",
        f'href="{_core.public_url(base_path, PRIMARY_START_ROUTE)}"',
    )
    missing = [item for item in required if item not in html]
    if missing:
        raise RuntimeError("Pages kök akıllı başlangıç tasarımı eksik: " + ", ".join(missing))


def update_primary_shortcut(site: Path, base_path: str) -> None:
    manifest_path = site / "manifest.webmanifest"
    if not manifest_path.is_file():
        return
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    shortcuts = manifest.setdefault("shortcuts", [])
    url = _core.public_url(base_path, PRIMARY_START_ROUTE)
    if not any(item.get("url") == url for item in shortcuts if isinstance(item, dict)):
        shortcuts.insert(0, {"name": "Elektrik Durum Merkezi", "short_name": "Doğru rota", "url": url})
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def prepare(site: Path, base_path: str, repository: str, commit: str) -> dict:
    result = _original_prepare(site, base_path, repository, commit)
    normalized = _core.normalize_base_path(base_path)
    validate_root_legal_deadline(site, normalized)
    validate_root_primary_start(site, normalized)
    update_primary_shortcut(site, normalized)
    origin_files_changed = normalize_live_origin(site)
    hardened_html_count = inject_quality_hardening(site)

    result["canonicalHost"] = CANONICAL_ORIGIN
    result["customDomain"] = CANONICAL_HOST
    result["rootDeviceDamageDeadline"] = "10 iş günü"
    result["rootNoApplicationDisclaimer"] = True
    result["primaryStartRoute"] = _core.public_url(normalized, PRIMARY_START_ROUTE)
    result["primaryStartMode"] = "progressive-disclosure"
    result["canonicalOriginFilesChanged"] = origin_files_changed
    result["responsiveHtmlHardened"] = hardened_html_count

    release_path = site / "pages-release.json"
    if release_path.is_file():
        release = json.loads(release_path.read_text(encoding="utf-8"))
        release.update(result)
        release_path.write_text(json.dumps(release, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        result = release

    validate_live_quality_contracts(site)
    _core.recompute_checksums(site)
    return result


_core.gateway_html = gateway_html
_core.prepare = prepare


def main() -> None:
    _core.main()


if __name__ == "__main__":
    main()
