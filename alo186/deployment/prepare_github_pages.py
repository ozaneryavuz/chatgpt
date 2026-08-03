from __future__ import annotations

import json
import re
import shutil
from pathlib import Path
from urllib.parse import urlsplit

import prepare_github_pages_core as _core
from finalize_article_discovery import run as finalize_article_discovery
from finalize_editorial_trust import run as finalize_editorial_trust
from finalize_live_quality import CANONICAL_HOST, CANONICAL_ORIGIN as LIVE_CANONICAL_ORIGIN
from finalize_release_transparency import run as finalize_release_transparency
from finalize_user_experience import run as finalize_user_experience
from prepare_github_pages_core import *  # noqa: F401,F403


# prepare_github_pages_core içindeki eski www sabiti wildcard import sırasında bu
# modülün CANONICAL_ORIGIN adını gölgelememelidir. Canlı site www'den apex'e
# yönlendiği için hem dışa aktarılan sabit hem de core runtime tek kaynağa bağlanır.
CANONICAL_ORIGIN = LIVE_CANONICAL_ORIGIN
DEVICE_DAMAGE_MARKER = 'data-alo186-device-damage-deadline="true"'
DEVICE_DAMAGE_ROUTE = "/haberler/elektrik-kesintisi-cihaz-hasari-edas-basvurusu/"
PRIMARY_START_MARKER = 'data-alo186-primary-start="true"'
PRIMARY_START_ROUTE = "/elektrik-durum-merkezi/"
UX_MARKER = 'data-alo186-sitewide-ux="true"'
UX_CSS_SOURCE = Path("alo186/assets/alo186-ux.css")
UX_JS_SOURCE = Path("alo186/assets/alo186-ux.js")
UPS_RUNTIME_ALIAS = "/hesaplama/ups-calisma-suresi"
UPS_RUNTIME_TARGET = "/hesaplama/yedek-guc-cozum-secici/"
_original_gateway_html = _core.gateway_html
_original_choose_bridge_target = _core.choose_bridge_target
_original_prepare = _core.prepare

# Gateway ve yeni bridge'ler canlı son origin ile doğar. Mevcut kaynak sitemap ve
# canonical değerlerinin toplu www -> apex normalizasyonu ise bütün growth
# enjektörleri tamamlandıktan sonra finalize_live_quality katmanında yapılır.
_core.CANONICAL_ORIGIN = LIVE_CANONICAL_ORIGIN

if PRIMARY_START_ROUTE not in _core.CRITICAL_ROUTES:
    _core.CRITICAL_ROUTES = (_core.CRITICAL_ROUTES[0], PRIMARY_START_ROUTE, *_core.CRITICAL_ROUTES[1:])


def choose_bridge_target(route: str) -> str:
    """Eski UPS süre bağlantısını en yakın güncel karar aracına taşır."""

    path = urlsplit(route).path.rstrip("/") or "/"
    if path == UPS_RUNTIME_ALIAS:
        return UPS_RUNTIME_TARGET
    return _original_choose_bridge_target(route)


def install_sitewide_ux(site: Path, base_path: str) -> dict:
    repo_root = Path(__file__).resolve().parents[2]
    assets = site / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    for source_relative in (UX_CSS_SOURCE, UX_JS_SOURCE):
        source = repo_root / source_relative
        if not source.is_file():
            raise FileNotFoundError(f"Site geneli UX assetı eksik: {source}")
        shutil.copy2(source, assets / source.name)

    css_url = _core.public_url(base_path, "/assets/alo186-ux.css")
    js_url = _core.public_url(base_path, "/assets/alo186-ux.js")
    injected = 0
    skipped = 0
    for path in sorted(site.rglob("*.html")):
        text = path.read_text(encoding="utf-8")
        if UX_MARKER in text:
            skipped += 1
            continue
        if "</head>" not in text or "</body>" not in text:
            raise RuntimeError(f"UX katmanı için geçersiz HTML: {path.relative_to(site)}")
        link = f'<link rel="stylesheet" href="{css_url}" {UX_MARKER}>'
        script = f'<script src="{js_url}" defer {UX_MARKER}></script>'
        text = text.replace("</head>", link + "\n</head>", 1)
        text = text.replace("</body>", script + "\n</body>", 1)
        path.write_text(text, encoding="utf-8")
        injected += 1
    if not injected and not skipped:
        raise RuntimeError("Site geneli UX katmanı için HTML sayfası bulunamadı.")
    return {"injectedPages": injected, "alreadyInjectedPages": skipped, "css": css_url, "js": js_url}


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
        '<strong id="device-damage-deadline">Cihaz hasarında başvuru süresi 30 gündür</strong>'
        '<p>Dağıtım şebekesinden kaynaklandığını düşündüğünüz cihaz veya teçhizat hasarı için '
        'zararın ortaya çıktığı tarihten itibaren <strong>30 gün içinde</strong> ilgili dağıtım '
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
    return html.replace(anchor, notice + "\n" + anchor + "\n" + primary, 1)


def validate_root_legal_deadline(site: Path, base_path: str) -> None:
    root = site / "index.html"
    if not root.is_file():
        raise FileNotFoundError(f"Pages kök sayfası eksik: {root}")
    html = root.read_text(encoding="utf-8")
    required = (
        DEVICE_DAMAGE_MARKER,
        "Cihaz hasarında başvuru süresi 30 gündür",
        "zararın ortaya çıktığı tarihten itibaren <strong>30 gün içinde</strong>",
        "ALO186 başvuru, ihbar veya hasar kaydı almaz",
        f'href="{_core.public_url(base_path, DEVICE_DAMAGE_ROUTE)}"',
    )
    missing = [item for item in required if item not in html]
    if missing:
        raise RuntimeError("Pages kök hukuki süre koruması eksik: " + ", ".join(missing))
    if re.search(r"\b(?:10\s*iş\s*gün|on\s*iş\s*gün)\b", html, re.IGNORECASE):
        raise RuntimeError("Pages kökünde cihaz hasarı başvurusu için eski 10 iş günü ifadesi kalamaz.")


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
    canonical_release_path = site / "alo186-release.json"
    if not canonical_release_path.is_file():
        raise FileNotFoundError("Makale merkezi için alo186-release.json bulunamadı.")
    canonical_release = json.loads(canonical_release_path.read_text(encoding="utf-8"))

    result = _original_prepare(site, base_path, repository, commit)
    normalized = _core.normalize_base_path(base_path)
    article_discovery = finalize_article_discovery(site, normalized, canonical_release)
    editorial_trust = finalize_editorial_trust(site, normalized, canonical_release)
    release_transparency = finalize_release_transparency(
        site,
        normalized,
        canonical_release,
        repository,
        commit,
    )
    audit = finalize_user_experience(site, normalized)
    ux = install_sitewide_ux(site, normalized)
    validate_root_legal_deadline(site, normalized)
    validate_root_primary_start(site, normalized)
    update_primary_shortcut(site, normalized)

    release_path = site / "pages-release.json"
    release = json.loads(release_path.read_text(encoding="utf-8")) if release_path.is_file() else dict(result)
    release["canonicalHost"] = LIVE_CANONICAL_ORIGIN
    release["customDomain"] = CANONICAL_HOST
    release["rootDeviceDamageDeadline"] = "30 gün"
    release["rootNoApplicationDisclaimer"] = True
    release["primaryStartRoute"] = _core.public_url(normalized, PRIMARY_START_ROUTE)
    release["primaryStartMode"] = "progressive-disclosure"
    release["sitewideUx"] = ux
    release["sitewideUserExperienceAudit"] = audit
    release["articleDiscoveryV1"] = article_discovery
    release["editorialTrustV1"] = editorial_trust
    release["releaseTransparencyV1"] = release_transparency
    release["liveOriginNormalizationStage"] = "after-all-growth-injectors"
    if release_path.is_file():
        release_path.write_text(json.dumps(release, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    _core.recompute_checksums(site)
    return release


_core.choose_bridge_target = choose_bridge_target
_core.gateway_html = gateway_html
_core.prepare = prepare


def main() -> None:
    _core.main()


if __name__ == "__main__":
    main()
