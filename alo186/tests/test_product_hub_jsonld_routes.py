from __future__ import annotations

import html as html_lib
import json
import os
import re
from pathlib import Path
from urllib.parse import urlparse

REPO_ROOT = Path(__file__).resolve().parents[2]
ORIGIN = "https://alo186.com"
ROUTE_PREFIX = "/amazon-elektrik-urunleri/"
EXPECTED_PATHS = {
    "/amazon-elektrik-urunleri/modem-ont-mini-ups-yedekleme-secici/",
    "/amazon-elektrik-urunleri/nas-ups-usb-snmp-uygunluk-secici/",
    "/amazon-elektrik-urunleri/guvenlik-kamerasi-nvr-poe-ups-secici/",
    "/amazon-elektrik-urunleri/alarm-paneli-aku-uygunluk-secici/",
    "/amazon-elektrik-urunleri/cpap-yedek-guc-uygunluk-secici/",
    "/amazon-elektrik-urunleri/mobil-hotspot-4g-5g-yedek-internet-secici/",
}
GENERIC_ACCESSORY_PATTERN = re.compile(
    r"(?:usb-c hub|hafıza kartı|sd kart|webcam|kulaklık|bluetooth hoparlör|"
    r"hdmi|displayport|ses adaptörü|audio interface|mouse|klavye|"
    r"yazıcı sarf|laptop soğutucu)",
    re.IGNORECASE,
)


def resolve_site_root() -> Path:
    configured = os.environ.get("ALO186_SITE_ROOT", "").strip()
    candidates = []
    if configured:
        configured_path = Path(configured).resolve()
        candidates.extend((configured_path, configured_path / "alo186"))
    candidates.extend((REPO_ROOT / "alo186", REPO_ROOT))

    for candidate in candidates:
        if (candidate / "amazon-elektrik-urunleri/index.html").is_file():
            return candidate
    raise AssertionError("ALO186 site kökü bulunamadı")


SITE_ROOT = resolve_site_root()
HUB_PATH = SITE_ROOT / "amazon-elektrik-urunleri/index.html"


def normalize_route(path: str) -> str:
    normalized = "/" + path.strip("/") + "/"
    return normalized if normalized != "//" else "/"


def load_item_list_urls() -> tuple[str, set[str]]:
    source = HUB_PATH.read_text(encoding="utf-8")
    match = re.search(
        r'<script\s+type="application/ld\+json">\s*(.*?)\s*</script>',
        source,
        flags=re.DOTALL,
    )
    assert match, "Ürün merkezi JSON-LD bloğu bulunamadı"
    payload = json.loads(html_lib.unescape(match.group(1)))
    graph = payload.get("@graph")
    assert isinstance(graph, list), "JSON-LD @graph dizisi eksik"
    item_list = next(
        (
            item
            for item in graph
            if isinstance(item, dict)
            and item.get("@type") == "ItemList"
            and item.get("name") == "Yüksek niyetli güvenli ürün seçim rotaları"
        ),
        None,
    )
    assert item_list, "Öncelikli ürün seçimi ItemList düğümü bulunamadı"
    entries = item_list.get("itemListElement")
    assert isinstance(entries, list) and entries, "ItemList rotaları boş"
    urls = {
        entry.get("url")
        for entry in entries
        if isinstance(entry, dict) and isinstance(entry.get("url"), str)
    }
    assert len(urls) == len(entries), "ItemList URL alanları eksik veya yineleniyor"
    return source, urls


def route_document(path: str) -> Path:
    relative = normalize_route(path).strip("/")
    return SITE_ROOT / relative / "index.html"


def visible_product_routes(source: str) -> set[str]:
    routes: set[str] = set()
    for href in re.findall(r'href=["\']([^"\']+)["\']', source, flags=re.IGNORECASE):
        parsed = urlparse(html_lib.unescape(href).strip())
        if parsed.scheme or parsed.netloc:
            continue
        if parsed.query or parsed.fragment:
            continue
        if not parsed.path.startswith(ROUTE_PREFIX):
            continue
        route = normalize_route(parsed.path)
        if route == ROUTE_PREFIX:
            continue
        routes.add(route)
    return routes


def canonical_url(source: str) -> str:
    match = re.search(
        r'<link\b[^>]*\brel=["\']canonical["\'][^>]*\bhref=["\']([^"\']+)["\']',
        source,
        flags=re.IGNORECASE,
    )
    if not match:
        match = re.search(
            r'<link\b[^>]*\bhref=["\']([^"\']+)["\'][^>]*\brel=["\']canonical["\']',
            source,
            flags=re.IGNORECASE,
        )
    assert match, "Canonical bağlantı bulunamadı"
    return html_lib.unescape(match.group(1)).strip()


def test_product_hub_jsonld_routes_are_canonical_clickable_and_published() -> None:
    source, urls = load_item_list_urls()
    paths: set[str] = set()

    for url in urls:
        parsed = urlparse(url)
        assert f"{parsed.scheme}://{parsed.netloc}" == ORIGIN, f"Canonical origin sapması: {url}"
        assert parsed.path.startswith(ROUTE_PREFIX), f"Ürün merkezi rota ayıracı eksik: {url}"
        assert parsed.path.endswith("/"), f"Canonical rota son eğik çizgiyi korumuyor: {url}"
        assert parsed.query == "" and parsed.fragment == "", f"JSON-LD rotası temiz değil: {url}"
        assert f'href="{parsed.path}"' in source, f"JSON-LD rotasının görünür eş bağlantısı yok: {url}"

        document = route_document(parsed.path)
        assert document.is_file(), f"JSON-LD rotası yayın kaynağında yok: {parsed.path}"
        route_source = document.read_text(encoding="utf-8")
        assert canonical_url(route_source) == url, f"Hedef canonical eşleşmiyor: {url}"
        assert "Amazon Gelir Ortağı" in route_source or "Amazon satış ortaklığı" in route_source, (
            f"Affiliate açıklaması görünür değil: {url}"
        )
        assert "satın almama" in route_source.lower() or "yeni ürün alınmamalıdır" in route_source.lower(), (
            f"Satın almama sonucu eksik: {url}"
        )
        assert "resmî kurum" in route_source.lower(), f"Bağımsızlık açıklaması eksik: {url}"
        assert '"@type":"Product"' not in route_source and '"@type":"Offer"' not in route_source, (
            f"Doğrulanmamış ticari şema kullanılmış: {url}"
        )
        paths.add(parsed.path)

    assert paths == EXPECTED_PATHS
    assert "https://alo186.com/amazon-elektrik-urunlerimodem" not in source
    assert "https://alo186.com/amazon-elektrik-urunlerinas" not in source
    assert "https://alo186.com/amazon-elektrik-urunleriguvenlik" not in source
    assert "https://alo186.com/amazon-elektrik-urunlerialarm" not in source
    assert "https://alo186.com/amazon-elektrik-urunlericpap" not in source
    assert "https://alo186.com/amazon-elektrik-urunlerimobil" not in source


def test_every_visible_product_route_exists_and_self_canonicalizes() -> None:
    source = HUB_PATH.read_text(encoding="utf-8")
    routes = visible_product_routes(source)
    assert routes, "Ürün merkezinde görünür ürün rotası bulunamadı"

    missing: list[str] = []
    canonical_errors: list[str] = []
    for route in sorted(routes):
        document = route_document(route)
        if not document.is_file():
            missing.append(route)
            continue
        target_source = document.read_text(encoding="utf-8", errors="ignore")
        target_canonical = urlparse(canonical_url(target_source))
        if f"{target_canonical.scheme}://{target_canonical.netloc}" != ORIGIN:
            canonical_errors.append(f"{route} -> {target_canonical.geturl()}")
            continue
        if normalize_route(target_canonical.path) != route or target_canonical.query or target_canonical.fragment:
            canonical_errors.append(f"{route} -> {target_canonical.geturl()}")

    assert not missing, "Ürün merkezinde 404 üretecek görünür rotalar: " + ", ".join(missing)
    assert not canonical_errors, "Görünür rota canonical sapmaları: " + ", ".join(canonical_errors)


def test_task_first_priority_precedes_catalog_and_excludes_generic_accessories() -> None:
    source = HUB_PATH.read_text(encoding="utf-8")
    disclosure_index = source.find("affiliate-disclosure")
    priority_index = source.find('aria-labelledby="priorityTitle"')
    core_index = source.find('aria-labelledby="coreTitle"')
    assert -1 not in (disclosure_index, priority_index, core_index), "Görev öncelikli ürün merkezi bölümleri eksik"
    assert disclosure_index < priority_index < core_index, (
        "Affiliate açıklaması ve görev öncelikli rotalar genel katalogdan önce gelmeli"
    )

    priority_section = source[priority_index:core_index]
    generic_match = GENERIC_ACCESSORY_PATTERN.search(html_lib.unescape(priority_section))
    assert generic_match is None, (
        "Genel teknoloji aksesuarı yüksek öncelikli elektrik görevlerine sızmış: "
        + (generic_match.group(0) if generic_match else "")
    )
    assert EXPECTED_PATHS.issubset(visible_product_routes(priority_section)), (
        "Yüksek niyetli altı güvenli rota görev öncelikli bölümde görünür değil"
    )


if __name__ == "__main__":
    test_product_hub_jsonld_routes_are_canonical_clickable_and_published()
    test_every_visible_product_route_exists_and_self_canonicalizes()
    test_task_first_priority_precedes_catalog_and_excludes_generic_accessories()
    print(
        json.dumps(
            {
                "ok": True,
                "priorityRoutes": len(EXPECTED_PATHS),
                "visibleRoutes": len(visible_product_routes(HUB_PATH.read_text(encoding="utf-8"))),
                "origin": ORIGIN,
                "siteRoot": str(SITE_ROOT),
            },
            ensure_ascii=False,
        )
    )
