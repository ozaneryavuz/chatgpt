from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from html import escape
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

CANONICAL_ORIGIN = "https://www.alo186.com"
TEXT_SUFFIXES = {".html", ".htm", ".css", ".js", ".json", ".webmanifest"}
CRITICAL_ROUTES = (
    "/",
    "/elektrik-portali/",
    "/edas-bul/",
    "/karar-motoru/",
    "/hesaplama/",
    "/hesaplama/kesinti-gunlugu/",
    "/kesintiye-hazirlik-atolyesi/",
    "/haberler/elektrik-kesintisi-cihaz-hasari-edas-basvurusu/",
    "/haberler/planli-elektrik-kesintisi-ne-kadar-once-bildirilir/",
    "/durum/",
    "/404.html",
)


class LinkCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        for key in ("href", "src", "action", "poster", "data-src", "data-href"):
            value = values.get(key)
            if value:
                self.links.append(value)
        srcset = values.get("srcset")
        if srcset:
            for item in srcset.split(","):
                candidate = item.strip().split(" ", 1)[0]
                if candidate:
                    self.links.append(candidate)


def normalize_base_path(value: str) -> str:
    cleaned = (value or "").strip()
    if not cleaned or cleaned == "/":
        return ""
    return "/" + cleaned.strip("/")


def public_url(base_path: str, route: str) -> str:
    if not route.startswith("/"):
        route = "/" + route
    if not base_path:
        return route
    if route == "/":
        return base_path + "/"
    return base_path + route


def route_exists(site: Path, route: str) -> bool:
    parsed = urlsplit(route)
    clean = parsed.path or "/"
    if clean == "/":
        return (site / "index.html").is_file()
    target = site / clean.lstrip("/")
    return target.is_file() or (target / "index.html").is_file()


def choose_bridge_target(route: str) -> str:
    path = urlsplit(route).path.lower()
    if path.startswith("/urun-rehberleri"):
        if any(token in path for token in ("ges", "solar", "panel")):
            return "/hesaplama/gunes-paneli-power-station-uygunluk/"
        if any(token in path for token in ("ups", "enerji-depolama", "power-station")):
            return "/hesaplama/yedek-guc-cozum-secici/"
        if any(token in path for token in ("ev", "sarj", "wallbox")):
            return "/hesaplama/ev-sarj-uygunluk/"
        if any(token in path for token in ("parafudr", "gerilim")):
            return "/hesaplama/parafudr-risk-testi/"
        return "/akilli-urun-secimi"
    if path.startswith(("/acil", "/elektrik-kesintisi", "/ariza")):
        return "/karar-motoru"
    if path.startswith(("/sektor-rehberi", "/haber", "/rehber")):
        return "/elektrik-portali"
    if path.startswith(("/iletisim", "/hakkimizda", "/yayin-ilkeleri", "/gizlilik")):
        return "/elektrik-portali"
    return "/elektrik-portali"


def collect_missing_internal_routes(site: Path) -> set[str]:
    missing: set[str] = set()
    for html_path in sorted(site.rglob("*.html")):
        parser = LinkCollector()
        parser.feed(html_path.read_text(encoding="utf-8", errors="ignore"))
        for reference in parser.links:
            parsed = urlsplit(reference)
            if parsed.scheme or reference.startswith(("//", "mailto:", "tel:", "javascript:", "data:", "blob:", "#")):
                continue
            if not parsed.path.startswith("/"):
                continue
            if route_exists(site, parsed.path):
                continue
            suffix = Path(parsed.path).suffix.lower()
            if suffix and suffix not in {".html", ".htm"}:
                continue
            missing.add(parsed.path.rstrip("/") or "/")
    return missing


def bridge_html(source_route: str, target_route: str, base_path: str) -> str:
    target_public = public_url(base_path, target_route)
    canonical = CANONICAL_ORIGIN + target_route
    return f"""<!doctype html>
<html lang="tr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <meta name="robots" content="noindex,follow">
  <meta name="referrer" content="strict-origin-when-cross-origin">
  <meta http-equiv="refresh" content="0;url={escape(target_public, quote=True)}">
  <link rel="canonical" href="{escape(canonical, quote=True)}">
  <title>ALO186 yönlendirme</title>
  <style>body{{font:17px/1.6 system-ui,sans-serif;max-width:48rem;margin:4rem auto;padding:0 1.2rem;color:#10243a}}a{{color:#164fc4;font-weight:800}}</style>
</head>
<body>
  <h1>İçerik yeni adresine taşındı</h1>
  <p><code>{escape(source_route)}</code> yolu artık güncel ALO186 karar akışına yönlendiriliyor.</p>
  <p><a href="{escape(target_public, quote=True)}">Güncel içeriği açın →</a></p>
  <script>location.replace({json.dumps(target_public, ensure_ascii=False)} + location.search + location.hash);</script>
</body>
</html>
"""


def create_route_bridges(site: Path, base_path: str) -> list[dict[str, str]]:
    bridges: list[dict[str, str]] = []
    for source_route in sorted(collect_missing_internal_routes(site)):
        if source_route == "/":
            continue
        target_route = choose_bridge_target(source_route)
        target = site / source_route.lstrip("/")
        if target.suffix.lower() in {".html", ".htm"}:
            target.parent.mkdir(parents=True, exist_ok=True)
            output = target
        else:
            target.mkdir(parents=True, exist_ok=True)
            output = target / "index.html"
        output.write_text(bridge_html(source_route, target_route, base_path), encoding="utf-8")
        bridges.append({"source": source_route, "target": target_route})
    return bridges


def gateway_html(base_path: str, noindex: bool) -> str:
    robots = "noindex,follow" if noindex else "index,follow,max-image-preview:large"
    links = {
        "edas": public_url(base_path, "/edas-bul/"),
        "decision": public_url(base_path, "/karar-motoru/"),
        "portal": public_url(base_path, "/elektrik-portali/"),
        "workshop": public_url(base_path, "/kesintiye-hazirlik-atolyesi/"),
        "status": public_url(base_path, "/durum/"),
    }
    return f"""<!doctype html>
<html lang="tr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
  <meta name="robots" content="{robots}">
  <meta name="referrer" content="strict-origin-when-cross-origin">
  <meta name="theme-color" content="#071631">
  <link rel="canonical" href="{CANONICAL_ORIGIN}/">
  <link rel="manifest" href="{public_url(base_path, '/manifest.webmanifest')}">
  <title>ALO186 — Elektrik kesintisi, doğru kanal ve güvenli hazırlık</title>
  <meta name="description" content="Elektrik kesintisinde 112, 186, EDAŞ veya elektrikçi ayrımını yapın; kişisel veri vermeden hesaplayıcı, rehber ve hazırlık araçlarına ulaşın.">
  <style>
    :root{{--navy:#071631;--blue:#1e5eff;--cyan:#28b9d8;--ink:#172238;--muted:#526178;--line:#dce5f0;--focus:#ffbf47}}
    *{{box-sizing:border-box}}body{{margin:0;font:17px/1.6 system-ui,-apple-system,Segoe UI,sans-serif;color:var(--ink);background:linear-gradient(180deg,#f5f8ff,#fff)}}
    a:focus-visible{{outline:4px solid var(--focus);outline-offset:4px}}.wrap{{max-width:1040px;margin:auto;padding:24px}}
    header{{background:var(--navy);color:#fff}}header .wrap{{display:flex;justify-content:space-between;align-items:center;gap:16px}}header a{{color:#fff}}
    main{{padding:clamp(36px,7vw,88px) 0}}h1{{font-size:clamp(2.4rem,7vw,5.6rem);line-height:.98;letter-spacing:-.055em;margin:.2em 0;color:var(--navy)}}
    .lead{{font-size:1.15rem;color:var(--muted);max-width:780px}}.alert{{margin:28px 0;padding:20px;border-radius:18px;background:#fff5cf;border:2px solid #e7ad22}}
    .grid{{display:grid;grid-template-columns:repeat(2,1fr);gap:16px;margin:28px 0}}.card{{display:flex;flex-direction:column;min-height:180px;padding:22px;border:1px solid var(--line);border-radius:20px;background:#fff;color:var(--ink);text-decoration:none;box-shadow:0 14px 36px rgba(8,32,67,.08)}}
    .card strong{{font-size:1.35rem;color:var(--navy)}}.card span{{margin-top:auto;color:#174bb9;font-weight:900;min-height:44px;display:flex;align-items:end}}.small{{color:var(--muted);font-size:.94rem}}
    @media(max-width:680px){{.grid{{grid-template-columns:1fr}}header .wrap{{align-items:flex-start;flex-direction:column}}}}
  </style>
</head>
<body>
<header><div class="wrap"><strong>ALO186 bağımsız elektrik bilgi ağı</strong><a href="{links['status']}">Yayın durumu</a></div></header>
<main><div class="wrap">
  <p class="small">Kişisel veri istemez · EDAŞ veya kamu kurumu değildir · Arıza kaydı almaz</p>
  <h1>Elektrik sorununda doğru sonraki adım.</h1>
  <p class="lead">Kesinti, cihaz hasarı, yedek güç veya elektrik güvenliği konusunda önce riski ayırın; sonra resmî kanal, ücretsiz hesaplayıcı veya teknik rehbere ilerleyin.</p>
  <div class="alert"><strong>Acil tehlike:</strong> Duman, alev, kopmuş hat veya elektrik çarpması riski varsa güvenli uzaklığa çıkın ve <strong>112</strong>’yi arayın. Bölgesel kesinti ve şebeke arızası için <strong>186</strong> veya resmî dağıtım şirketini kullanın.</div>
  <section class="grid" aria-label="ALO186 hızlı başlangıç">
    <a class="card" href="{links['decision']}"><strong>112 mi, 186 mı, elektrikçi mi?</strong><p>Belirtiye göre güvenli yönlendirme alın.</p><span>Karar motorunu aç →</span></a>
    <a class="card" href="{links['edas']}"><strong>Doğru EDAŞ’ı bulun</strong><p>81 il ve 973 ilçede resmî dağıtım kanalına ilerleyin.</p><span>EDAŞ bulucuyu aç →</span></a>
    <a class="card" href="{links['workshop']}"><strong>Kesintiye hazırlık atölyesi</strong><p>Mevcut çözümünüz yeterli mi, ücretsiz araç mı, profesyonel destek mi gerekli görün.</p><span>Hazırlık planını oluştur →</span></a>
    <a class="card" href="{links['portal']}"><strong>Tüm araç ve rehberler</strong><p>Hesaplayıcılar, teknik içerikler ve işletme sürekliliği araçları.</p><span>Elektrik Portalı’nı aç →</span></a>
  </section>
  <p class="small">GitHub Pages tabanlı bu sürüm, kritik rehberleri ilk ziyaretten sonra çevrimdışı erişim için önbelleğe alır.</p>
</div></main>
</body>
</html>
"""


def status_html(base_path: str) -> str:
    release_url = public_url(base_path, "/pages-release.json")
    canonical_release_url = public_url(base_path, "/alo186-release.json")
    portal_url = public_url(base_path, "/elektrik-portali/")
    return f"""<!doctype html>
<html lang="tr">
<head>
  <meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
  <meta name="robots" content="noindex,follow"><meta name="referrer" content="strict-origin-when-cross-origin">
  <link rel="canonical" href="{CANONICAL_ORIGIN}/durum"><title>ALO186 yayın durumu</title>
  <style>body{{font:17px/1.6 system-ui,sans-serif;max-width:60rem;margin:auto;padding:2rem;color:#132238}}.ok{{color:#08745b}}.bad{{color:#b42318}}code{{background:#eef3f8;padding:.15rem .35rem;border-radius:.35rem}}li{{margin:.55rem 0}}a{{color:#174bb9;font-weight:800}}</style>
</head><body>
<h1>ALO186 yayın ve çevrimdışı erişim durumu</h1>
<p>Bu sayfa GitHub Pages sürümünün hangi committen üretildiğini ve kritik rotaların erişimini tarayıcı içinde kontrol eder.</p>
<dl><dt>Geçerli host</dt><dd><code id="host"></code></dd><dt>Platform</dt><dd>GitHub Pages · statik ve sunucusuz</dd><dt>Çevrimiçi durum</dt><dd id="online"></dd></dl>
<h2>Yayın bilgisi</h2><pre id="release">Yükleniyor…</pre>
<h2>Kritik rota kontrolü</h2><ul id="routes"></ul>
<p><a href="{portal_url}">Elektrik Portalı’na dön →</a></p>
<script>
const routes={json.dumps([public_url(base_path, r) for r in CRITICAL_ROUTES], ensure_ascii=False)};
document.getElementById('host').textContent=location.host;
function online(){{document.getElementById('online').textContent=navigator.onLine?'Çevrimiçi':'Çevrimdışı — önbellekteki kritik içerikler kullanılabilir';}}
addEventListener('online',online);addEventListener('offline',online);online();
Promise.all([fetch({json.dumps(release_url)}).then(r=>r.json()),fetch({json.dumps(canonical_release_url)}).then(r=>r.json())]).then(([pages,core])=>{{document.getElementById('release').textContent=JSON.stringify({{pages,core}},null,2);}}).catch(err=>{{document.getElementById('release').textContent='Yayın bilgisi okunamadı: '+err;}});
const list=document.getElementById('routes');
Promise.all(routes.map(async route=>{{let ok=false,status='offline cache';try{{const response=await fetch(route,{{cache:'no-store'}});ok=response.ok;status=String(response.status);}}catch(e){{ok=!!(await caches.match(route));}}const li=document.createElement('li');li.className=ok?'ok':'bad';li.textContent=(ok?'✓ ':'✕ ')+route+' — '+status;list.appendChild(li);}}));
</script></body></html>"""


def webmanifest(base_path: str) -> dict:
    return {
        "name": "ALO186 Elektrik Bilgi Ağı",
        "short_name": "ALO186",
        "description": "Elektrik kesintisi, doğru kanal ve güvenli hazırlık araçları.",
        "start_url": public_url(base_path, "/"),
        "scope": public_url(base_path, "/"),
        "display": "standalone",
        "background_color": "#071631",
        "theme_color": "#071631",
        "icons": [
            {
                "src": public_url(base_path, "/alo186-mark.svg"),
                "sizes": "any",
                "type": "image/svg+xml",
                "purpose": "any maskable",
            }
        ],
    }


def service_worker(base_path: str, commit: str) -> str:
    cache_name = "alo186-emergency-" + (commit[:12] or "local")
    critical = [public_url(base_path, route) for route in CRITICAL_ROUTES]
    critical += [
        public_url(base_path, "/manifest.webmanifest"),
        public_url(base_path, "/alo186-mark.svg"),
        public_url(base_path, "/pages-release.json"),
        public_url(base_path, "/alo186-release.json"),
    ]
    return f"""const CACHE={json.dumps(cache_name)};
const BASE={json.dumps(base_path)};
const CRITICAL={json.dumps(critical, ensure_ascii=False)};
self.addEventListener('install',event=>{{event.waitUntil((async()=>{{const cache=await caches.open(CACHE);await Promise.allSettled(CRITICAL.map(url=>cache.add(url)));self.skipWaiting();}})());}});
self.addEventListener('activate',event=>{{event.waitUntil((async()=>{{for(const key of await caches.keys()){{if(key.startsWith('alo186-emergency-')&&key!==CACHE)await caches.delete(key);}}await self.clients.claim();}})());}});
async function networkFirst(request){{const cache=await caches.open(CACHE);try{{const response=await fetch(request);if(response&&response.ok)cache.put(request,response.clone());return response;}}catch(error){{return (await cache.match(request))||(await cache.match(BASE+'/404.html'));}}}}
self.addEventListener('fetch',event=>{{const request=event.request;if(request.method!=='GET')return;const url=new URL(request.url);if(url.origin!==location.origin)return;if(request.mode==='navigate'){{event.respondWith(networkFirst(request));return;}}event.respondWith((async()=>{{const cache=await caches.open(CACHE);const cached=await cache.match(request);const network=fetch(request).then(response=>{{if(response&&response.ok)cache.put(request,response.clone());return response;}}).catch(()=>cached);return cached||network;}})());}});
"""


def icon_svg() -> str:
    return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><rect width="512" height="512" rx="112" fill="#071631"/><path d="M286 44 116 292h116l-20 176 184-270H276z" fill="#28b9d8"/><text x="256" y="430" text-anchor="middle" font-family="system-ui,sans-serif" font-size="70" font-weight="800" fill="#fff">186</text></svg>'


def inject_meta_and_service_worker(html: str, base_path: str, noindex: bool) -> str:
    if noindex:
        if re.search(r'<meta\s+name=["\']robots["\']', html, re.I):
            html = re.sub(
                r'(<meta\s+name=["\']robots["\']\s+content=["\'])[^"\']*(["\'])',
                r'\1noindex,follow\2',
                html,
                count=1,
                flags=re.I,
            )
        else:
            html = html.replace("</head>", '<meta name="robots" content="noindex,follow">\n</head>', 1)
    if 'name="referrer"' not in html:
        html = html.replace("</head>", '<meta name="referrer" content="strict-origin-when-cross-origin">\n</head>', 1)
    if 'rel="manifest"' not in html:
        html = html.replace(
            "</head>",
            f'<link rel="manifest" href="{public_url(base_path, "/manifest.webmanifest")}">\n</head>',
            1,
        )
    if "data-alo186-pages-sw" not in html:
        registration = f"<script data-alo186-pages-sw>if('serviceWorker'in navigator){{addEventListener('load',()=>navigator.serviceWorker.register({json.dumps(public_url(base_path, '/sw.js'))},{{scope:{json.dumps(public_url(base_path, '/'))}}}).catch(()=>{{}}));}}</script>"
        html = html.replace("</body>", registration + "\n</body>", 1)
    return html


def prefix_root_references(text: str, base_path: str, known_top_levels: set[str]) -> str:
    if not base_path:
        return text
    pattern = re.compile(r'(?P<quote>["\'`])/(?P<rest>(?!/)[^"\'`\s<>]*)')

    def replace(match: re.Match[str]) -> str:
        rest = match.group("rest")
        first = rest.split("/", 1)[0].split("?", 1)[0].split("#", 1)[0]
        if rest == "" or first in known_top_levels:
            return f'{match.group("quote")}{base_path}/{rest}'
        return match.group(0)

    text = pattern.sub(replace, text)
    text = re.sub(r'url\(/(?!/)([^)]+)\)', lambda m: f'url({base_path}/{m.group(1)})', text)
    return text


def recompute_checksums(site: Path) -> None:
    checksum = site / "checksums.sha256"
    if checksum.exists():
        checksum.unlink()
    lines: list[str] = []
    for path in sorted(p for p in site.rglob("*") if p.is_file()):
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        lines.append(f"{digest}  {path.relative_to(site).as_posix()}")
    checksum.write_text("\n".join(lines) + "\n", encoding="utf-8")


def prepare(site: Path, base_path: str, repository: str, commit: str) -> dict:
    base_path = normalize_base_path(base_path)
    noindex = bool(base_path)
    for obsolete in (site / ".htaccess", site / "tailwindcss"):
        if obsolete.exists():
            obsolete.unlink()

    site.joinpath("index.html").write_text(gateway_html(base_path, noindex), encoding="utf-8")
    status_dir = site / "durum"
    status_dir.mkdir(parents=True, exist_ok=True)
    status_dir.joinpath("index.html").write_text(status_html(base_path), encoding="utf-8")

    bridges = create_route_bridges(site, base_path)
    site.joinpath("route-bridges.json").write_text(
        json.dumps({"count": len(bridges), "routes": bridges}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    core_release = json.loads((site / "alo186-release.json").read_text(encoding="utf-8"))
    owner, repo_name = repository.split("/", 1)
    pages_release = {
        "schemaVersion": 1,
        "hostingMode": "github-pages",
        "repository": repository,
        "commit": commit,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "canonicalHost": CANONICAL_ORIGIN,
        "customDomain": "www.alo186.com",
        "defaultPagesUrl": f"https://{owner}.github.io/{repo_name}/",
        "basePath": base_path,
        "routeCount": core_release.get("routeCount"),
        "routeBridgeCount": len(bridges),
        "offlineCriticalRouteCount": len(CRITICAL_ROUTES),
        "deviceDamageDeadline": core_release.get("deviceDamageDeadline"),
    }
    site.joinpath("pages-release.json").write_text(
        json.dumps(pages_release, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    site.joinpath("manifest.webmanifest").write_text(
        json.dumps(webmanifest(base_path), ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    site.joinpath("alo186-mark.svg").write_text(icon_svg(), encoding="utf-8")
    site.joinpath("sw.js").write_text(service_worker(base_path, commit), encoding="utf-8")

    known_top_levels = {path.name for path in site.iterdir()}
    for path in sorted(site.rglob("*")):
        if not path.is_file() or path.name in {"robots.txt", "sitemap.xml", "checksums.sha256"}:
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES and path.name != "sw.js":
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if path.suffix.lower() in {".html", ".htm"}:
            text = inject_meta_and_service_worker(text, base_path, noindex)
        text = prefix_root_references(text, base_path, known_top_levels)
        path.write_text(text, encoding="utf-8")

    recompute_checksums(site)
    return pages_release


def main() -> None:
    parser = argparse.ArgumentParser(description="ALO186 canonical bundle'ını GitHub Pages için hazırlar.")
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--base-path", default="")
    parser.add_argument("--repository", default="ozaneryavuz/chatgpt")
    parser.add_argument("--commit", default="local")
    args = parser.parse_args()
    release = prepare(args.site.resolve(), args.base_path, args.repository, args.commit)
    print(json.dumps(release, ensure_ascii=False))


if __name__ == "__main__":
    main()
