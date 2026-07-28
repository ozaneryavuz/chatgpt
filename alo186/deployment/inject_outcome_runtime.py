from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from pathlib import Path

MARKER = 'data-alo186-common-runtime="true"'
PENDING_MARKER = 'data-alo186-pending-context="true"'
OUTCOME_CARD_MARKER = 'data-alo186-outcome-card="true"'
PLAN_CARD_MARKER = 'data-alo186-plan-card="true"'
KIT_CARD_MARKER = 'data-alo186-kit-card="true"'
PLAN_HUB_MARKER = 'data-alo186-plan-hub-card="true"'
KIT_HUB_MARKER = 'data-alo186-kit-hub-card="true"'
OUTCOME_RELATIVE = Path("hesaplama/cozum-sonucu/index.html")
PLAN_RELATIVE = Path("hesaplama/elektrik-planim/index.html")
KIT_RELATIVE = Path("hesaplama/elektrik-kesintisi-kiti/index.html")
PORTAL_RELATIVE = Path("elektrik-portali/index.html")
GATEWAY_RELATIVE = Path("index.html")
PLAN_CANONICAL = "https://www.alo186.com/hesaplama/elektrik-planim/"
KIT_CANONICAL = "https://www.alo186.com/hesaplama/elektrik-kesintisi-kiti/"


def normalize_base_path(value: str) -> str:
    cleaned = (value or "").strip()
    if not cleaned or cleaned == "/":
        return ""
    return "/" + cleaned.strip("/")


def public_url(base_path: str, route: str) -> str:
    route = "/" + route.lstrip("/")
    return f"{base_path}{route}" if base_path else route


def prefix_links(text: str, base_path: str) -> str:
    if not base_path:
        return text
    return re.sub(
        r'(?P<attr>href|src)="/(?!/)(?P<path>[^"#]*)"',
        lambda match: f'{match.group("attr")}="{base_path}/{match.group("path")}"',
        text,
    )


def prefix_script_paths(text: str, base_path: str) -> str:
    if not base_path:
        return text
    base_segment = base_path.lstrip("/")
    pattern = re.compile(r'(?P<quote>["\'`])/(?P<path>(?!/)[a-zA-Z0-9_\-/.?=&%]*)')

    def replace(match: re.Match[str]) -> str:
        path = match.group("path")
        if path == base_segment or path.startswith(base_segment + "/"):
            return match.group(0)
        return f'{match.group("quote")}{base_path}/{path}'

    return pattern.sub(replace, text)


def inject_pages_meta(text: str, base_path: str) -> str:
    if base_path:
        if re.search(r'<meta\s+name="robots"', text, re.I):
            text = re.sub(r'(<meta\s+name="robots"\s+content=")[^"]*(")', r'\1noindex,follow\2', text, count=1, flags=re.I)
        else:
            text = text.replace("</head>", '<meta name="robots" content="noindex,follow">\n</head>', 1)
    manifest_url = public_url(base_path, "/manifest.webmanifest")
    if 'rel="manifest"' not in text:
        text = text.replace("</head>", f'<link rel="manifest" href="{manifest_url}">\n</head>', 1)
    if "data-alo186-pages-sw" not in text:
        sw_url = public_url(base_path, "/sw.js")
        scope = public_url(base_path, "/")
        tag = f"<script data-alo186-pages-sw>if('serviceWorker'in navigator){{addEventListener('load',()=>navigator.serviceWorker.register('{sw_url}',{{scope:'{scope}'}}).catch(()=>{{}}));}}</script>"
        text = text.replace("</body>", tag + "\n</body>", 1)
    return text


def append_sitemap_route(site: Path, canonical: str) -> None:
    sitemap = site / "sitemap.xml"
    if not sitemap.is_file():
        return
    text = sitemap.read_text(encoding="utf-8")
    if f"<loc>{canonical}</loc>" in text:
        return
    entry = f'  <url><loc>{canonical}</loc><lastmod>2026-07-28</lastmod><changefreq>weekly</changefreq><priority>0.9</priority></url>\n'
    sitemap.write_text(text.replace("</urlset>", entry + "</urlset>", 1), encoding="utf-8")


def append_release_route(site: Path, canonical_path: str, source: str, route_type: str = "tool") -> None:
    release_path = site / "alo186-release.json"
    if not release_path.is_file():
        return
    release = json.loads(release_path.read_text(encoding="utf-8"))
    routes = release.setdefault("routes", [])
    if not any(item.get("canonicalPath") == canonical_path for item in routes):
        routes.append({"canonicalPath": canonical_path, "source": source, "type": route_type})
    release["routeCount"] = len(routes)
    release_path.write_text(json.dumps(release, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def raise_tool_count(text: str, minimum: int) -> str:
    pattern = re.compile(r'(\d+) çekirdek araç')

    def replace(match: re.Match[str]) -> str:
        return f"{max(int(match.group(1)), minimum)} çekirdek araç"

    return pattern.sub(replace, text, count=1)


def ensure_plan_route(site: Path, base_path: str) -> bool:
    repo_root = Path(__file__).resolve().parents[2]
    source = repo_root / "alo186" / "hesaplama" / "elektrik-planim"
    target = site / "hesaplama" / "elektrik-planim"
    created = not (target / "index.html").is_file()
    target.mkdir(parents=True, exist_ok=True)
    for name in ("index.html", "styles.css", "core.js", "app.js", "growth-core.js", "growth.js"):
        src = source / name
        if not src.is_file():
            raise FileNotFoundError(f"Elektrik Planım kaynak dosyası eksik: {src}")
        shutil.copy2(src, target / name)

    plan_html = target / "index.html"
    text = prefix_links(plan_html.read_text(encoding="utf-8"), base_path)
    text = inject_pages_meta(text, base_path)
    plan_html.write_text(text, encoding="utf-8")
    for name in ("core.js", "app.js", "growth-core.js", "growth.js"):
        path = target / name
        path.write_text(prefix_script_paths(path.read_text(encoding="utf-8"), base_path), encoding="utf-8")

    append_sitemap_route(site, PLAN_CANONICAL)
    append_release_route(site, "/hesaplama/elektrik-planim/", "alo186/hesaplama/elektrik-planim/index.html")

    hub = site / "hesaplama" / "index.html"
    if hub.is_file():
        hub_text = raise_tool_count(hub.read_text(encoding="utf-8"), 32)
        if PLAN_HUB_MARKER not in hub_text:
            href = public_url(base_path, "/hesaplama/elektrik-planim/")
            card = f'<a class="tool-card" {PLAN_HUB_MARKER} href="{href}"><span class="eyebrow">Tek plan · öncelik · tekrar ziyaret</span><h2>Elektrik Planım</h2><p>Kesinti, çözüm, bakım, ürün ve kesinti kiti kayıtlarını tek kişisel verisiz öncelik planında birleştirin.</p><b>Bugünkü planı aç →</b></a>'
            hub_text = hub_text.replace('<section id="araclar" class="tool-grid">', '<section id="araclar" class="tool-grid">\n' + card, 1)
        hub.write_text(hub_text, encoding="utf-8")
    return created


def ensure_kit_route(site: Path, base_path: str) -> bool:
    repo_root = Path(__file__).resolve().parents[2]
    source = repo_root / "alo186" / "hesaplama" / "elektrik-kesintisi-kiti"
    target = site / "hesaplama" / "elektrik-kesintisi-kiti"
    created = not (target / "index.html").is_file()
    target.mkdir(parents=True, exist_ok=True)
    for name in ("index.html", "styles.css", "core.js", "app.js"):
        src = source / name
        if not src.is_file():
            raise FileNotFoundError(f"Elektrik Kesintisi Kiti kaynak dosyası eksik: {src}")
        shutil.copy2(src, target / name)
    pwa_source = repo_root / "alo186" / "hesaplama" / "pwa-install.js"
    pwa_target = site / "hesaplama" / "pwa-install.js"
    if not pwa_source.is_file():
        raise FileNotFoundError(f"PWA kurulum yardımcısı eksik: {pwa_source}")
    shutil.copy2(pwa_source, pwa_target)

    kit_html = target / "index.html"
    text = prefix_links(kit_html.read_text(encoding="utf-8"), base_path)
    text = inject_pages_meta(text, base_path)
    kit_html.write_text(text, encoding="utf-8")
    for path in (target / "core.js", target / "app.js", pwa_target):
        path.write_text(prefix_script_paths(path.read_text(encoding="utf-8"), base_path), encoding="utf-8")

    append_sitemap_route(site, KIT_CANONICAL)
    append_release_route(site, "/hesaplama/elektrik-kesintisi-kiti/", "alo186/hesaplama/elektrik-kesintisi-kiti/index.html")

    hub = site / "hesaplama" / "index.html"
    if hub.is_file():
        hub_text = raise_tool_count(hub.read_text(encoding="utf-8"), 33)
        if KIT_HUB_MARKER not in hub_text:
            href = public_url(base_path, "/hesaplama/elektrik-kesintisi-kiti/")
            card = f'<a class="tool-card" {KIT_HUB_MARKER} href="{href}"><span class="eyebrow">Envanter · eksik işlev · satış en son</span><h2>Elektrik Kesintisi Kiti</h2><p>Elinizdeki ekipmanı önce değerlendirin; yalnız eksik veya doğrulanması gereken işlevleri ücretsiz araç ve şeffaf ürün rotasına taşıyın.</p><b>Kesinti kitini analiz et →</b></a>'
            hub_text = hub_text.replace('<section id="araclar" class="tool-grid">', '<section id="araclar" class="tool-grid">\n' + card, 1)
        hub.write_text(hub_text, encoding="utf-8")
    return created


def card_marker(card: str) -> str:
    match = re.search(r'data-alo186-[a-z0-9-]+="true"', card, re.I)
    if not match:
        raise ValueError("ALO186 giriş kartı benzersiz marker içermeli")
    return match.group(0)


def insert_after_grid_open(text: str, cards: list[str]) -> tuple[str, int]:
    missing = [card for card in cards if card_marker(card) not in text]
    if not missing:
        return text, 0
    for match in re.finditer(r'<section\b[^>]*>', text, re.I):
        class_match = re.search(r'class=["\']([^"\']*)["\']', match.group(0), re.I)
        if class_match and "grid" in class_match.group(1).split():
            return text[: match.end()] + "\n" + "\n".join(missing) + text[match.end() :], len(missing)
    return text, 0


def outcome_card(base_path: str, gateway: bool = False) -> str:
    href = public_url(base_path, "/hesaplama/cozum-sonucu/")
    if gateway:
        return f'<a class="card" {OUTCOME_CARD_MARKER} href="{href}"><strong>Çözüm gerçekten işe yaradı mı?</strong><p>Öneri, ürün, bakım veya resmî kanal sonucunu kişisel veri vermeden kaydedin; tekrar eden problemi doğru rotaya taşıyın.</p><span>Sonucu kaydet ve izle →</span></a>'
    return f'<a class="card" {OUTCOME_CARD_MARKER} href="{href}"><span class="tag">Kapalı döngü · satın almama · tekrar önleme</span><h2>Çözüm Sonucu Merkezi</h2><p>Karar, hesap, ürün, bakım veya resmî kanalın gerçekten işe yarayıp yaramadığını izleyin; çözüldüyse yeni ürün önerilmez.</p><b>Sonucu kaydet ve tekrar riskini izle →</b></a>'


def plan_card(base_path: str, gateway: bool = False) -> str:
    href = public_url(base_path, "/hesaplama/elektrik-planim/")
    if gateway:
        return f'<a class="card" {PLAN_CARD_MARKER} href="{href}"><strong>Elektrik Planım</strong><p>Kesinti, kit, bakım, ürün yeniden kontrolü ve çözülmemiş işleri tek kişisel verisiz öncelik planında görün.</p><span>Bugünkü planı aç →</span></a>'
    return f'<a class="card" {PLAN_CARD_MARKER} href="{href}"><span class="tag">Tek plan · tekrar ziyaret · profesyonel hazırlık</span><h2>Elektrik Planım</h2><p>Yerel kesinti, kit, bakım, ürün ve çözüm kayıtlarını tek öncelik listesinde birleştirin; tekrar eden yüksek riskli sonuçları profesyonel pakete dönüştürün.</p><b>Bugünkü planı aç →</b></a>'


def kit_card(base_path: str, gateway: bool = False) -> str:
    href = public_url(base_path, "/hesaplama/elektrik-kesintisi-kiti/")
    if gateway:
        return f'<a class="card" {KIT_CARD_MARKER} href="{href}"><strong>Kesinti kitinizde ne eksik?</strong><p>Mevcut ekipmanı önce değerlendirin; yalnız gerçek boşluğu ücretsiz teknik araçla doğrulayın.</p><span>Eksik analizi oluştur →</span></a>'
    return f'<a class="card" {KIT_CARD_MARKER} href="{href}"><span class="tag">Envanter önce · satın almama · şeffaf affiliate</span><h2>Elektrik Kesintisi Kiti</h2><p>Powerbank, mini UPS, acil aydınlatma, duman alarmı, grup priz ve power station arasında yalnız eksik işlevi belirleyin.</p><b>Kesinti kitini analiz et →</b></a>'


def add_offline_routes(site: Path, base_path: str) -> list[str]:
    sw_path = site / "sw.js"
    if not sw_path.is_file():
        raise FileNotFoundError(f"GitHub Pages service worker eksik: {sw_path}")
    routes = [
        public_url(base_path, "/hesaplama/cozum-sonucu/"),
        public_url(base_path, "/hesaplama/elektrik-planim/"),
        public_url(base_path, "/hesaplama/elektrik-kesintisi-kiti/"),
    ]
    text = sw_path.read_text(encoding="utf-8")
    match = re.search(r"const CRITICAL=(\[.*?\]);", text, re.S)
    if not match:
        raise RuntimeError("Service worker CRITICAL rota dizisi bulunamadı")
    critical = json.loads(match.group(1))
    added = [route for route in routes if route not in critical]
    if added:
        critical.extend(added)
        sw_path.write_text(text[: match.start(1)] + json.dumps(critical, ensure_ascii=False) + text[match.end(1) :], encoding="utf-8")
    return added


def update_webmanifest(site: Path, base_path: str) -> None:
    manifest_path = site / "manifest.webmanifest"
    if not manifest_path.is_file():
        return
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    shortcuts = manifest.setdefault("shortcuts", [])
    desired = [
        {"name": "Elektrik Planım", "short_name": "Planım", "url": public_url(base_path, "/hesaplama/elektrik-planim/")},
        {"name": "Elektrik Kesintisi Kiti", "short_name": "Kesinti Kiti", "url": public_url(base_path, "/hesaplama/elektrik-kesintisi-kiti/")},
        {"name": "112 mi, 186 mı?", "short_name": "Karar Motoru", "url": public_url(base_path, "/karar-motoru/")},
    ]
    existing = {item.get("url") for item in shortcuts if isinstance(item, dict)}
    shortcuts.extend(item for item in desired if item["url"] not in existing)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def update_pages_release(site: Path, base_path: str, injected: int, pending_injected: int, cards_injected: int, offline_added: list[str], plan_created: bool, kit_created: bool) -> None:
    release_path = site / "pages-release.json"
    if not release_path.is_file():
        return
    release = json.loads(release_path.read_text(encoding="utf-8"))
    core_release = json.loads((site / "alo186-release.json").read_text(encoding="utf-8"))
    release["routeCount"] = core_release.get("routeCount")
    release["outcomeRuntime"] = {
        "version": 3,
        "basePath": base_path,
        "injectedPages": injected,
        "pendingContextInjected": pending_injected,
        "entryCardsInjected": cards_injected,
        "pendingRecordLimit": 6,
        "pendingTtlDays": 45,
        "offlineOutcomeRoute": public_url(base_path, "/hesaplama/cozum-sonucu/"),
        "offlinePlanRoute": public_url(base_path, "/hesaplama/elektrik-planim/"),
        "offlineOutageKitRoute": public_url(base_path, "/hesaplama/elektrik-kesintisi-kiti/"),
        "productTrustCircuit": True,
        "planRouteCreated": plan_created,
        "outageKitRouteCreated": kit_created,
        "pwaInstallHelper": True,
    }
    if offline_added:
        release["offlineCriticalRouteCount"] = int(release.get("offlineCriticalRouteCount") or 0) + len(offline_added)
    release_path.write_text(json.dumps(release, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def recompute_checksums(site: Path) -> None:
    checksum_path = site / "checksums.sha256"
    if checksum_path.exists():
        checksum_path.unlink()
    lines = [f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.relative_to(site).as_posix()}" for path in sorted(item for item in site.rglob("*") if item.is_file())]
    checksum_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def inject(site: Path, base_path: str) -> dict:
    base_path = normalize_base_path(base_path)
    plan_created = ensure_plan_route(site, base_path)
    kit_created = ensure_kit_route(site, base_path)
    common = site / "hesaplama" / "common.js"
    bridge = site / "hesaplama" / "outcome-bridge.js"
    pending_context = site / "hesaplama" / "cozum-sonucu" / "pending-context.js"
    plan_page = site / PLAN_RELATIVE
    kit_page = site / KIT_RELATIVE
    pwa_helper = site / "hesaplama" / "pwa-install.js"
    trust_core = site / "akilli-urun-secimi" / "outcome-trust-circuit-core.js"
    trust_ui = site / "akilli-urun-secimi" / "outcome-trust-circuit.js"
    for required, label in [
        (common, "Ortak hesaplama runtime"),
        (bridge, "Çözüm sonucu köprüsü"),
        (pending_context, "Bekleyen çözüm bağlamı tüketicisi"),
        (plan_page, "Elektrik Planım"),
        (kit_page, "Elektrik Kesintisi Kiti"),
        (pwa_helper, "PWA kurulum yardımcısı"),
        (trust_core, "Ürün güven devre kesicisi core"),
        (trust_ui, "Ürün güven devre kesicisi UI"),
    ]:
        if not required.is_file():
            raise FileNotFoundError(f"{label} eksik: {required}")

    common_url = public_url(base_path, "/hesaplama/common.js")
    pending_url = public_url(base_path, "/hesaplama/cozum-sonucu/pending-context.js")
    injected = already_present = pending_injected = cards_injected = 0
    missing_body = []
    for html_path in sorted(site.rglob("*.html")):
        relative = html_path.relative_to(site)
        text = html_path.read_text(encoding="utf-8", errors="ignore")
        if relative == PORTAL_RELATIVE:
            text, added = insert_after_grid_open(text, [outcome_card(base_path), plan_card(base_path), kit_card(base_path)])
            cards_injected += added
        elif relative == GATEWAY_RELATIVE:
            text, added = insert_after_grid_open(text, [outcome_card(base_path, True), plan_card(base_path, True), kit_card(base_path, True)])
            cards_injected += added
        tags = []
        if MARKER not in text:
            tags.append(f'<script {MARKER} src="{common_url}"></script>')
            injected += 1
        else:
            already_present += 1
        if relative == OUTCOME_RELATIVE and PENDING_MARKER not in text:
            tags.append(f'<script {PENDING_MARKER} src="{pending_url}"></script>')
            pending_injected += 1
        if tags:
            if "</body>" not in text:
                missing_body.append(relative.as_posix())
                continue
            text = text.replace("</body>", "\n".join(tags) + "\n</body>", 1)
        html_path.write_text(text, encoding="utf-8")
    if missing_body:
        raise RuntimeError("Ortak runtime için </body> bulunamayan HTML: " + ", ".join(missing_body[:20]))
    offline_added = add_offline_routes(site, base_path)
    update_webmanifest(site, base_path)
    update_pages_release(site, base_path, injected, pending_injected, cards_injected, offline_added, plan_created, kit_created)
    recompute_checksums(site)
    return {
        "ok": True,
        "basePath": base_path,
        "commonUrl": common_url,
        "pendingContextUrl": pending_url,
        "injectedPages": injected,
        "alreadyPresent": already_present,
        "pendingContextInjected": pending_injected,
        "entryCardsInjected": cards_injected,
        "offlineRoutesAdded": offline_added,
        "productTrustCircuit": True,
        "planRouteCreated": plan_created,
        "outageKitRouteCreated": kit_created,
        "pwaInstallHelper": True,
        "totalPages": injected + already_present,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="ALO186 ortak sonuç, plan, kesinti kiti ve güven runtime'ını bütün GitHub Pages HTML rotalarına ekler.")
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--base-path", default="")
    args = parser.parse_args()
    print(json.dumps(inject(args.site.resolve(), args.base_path), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
