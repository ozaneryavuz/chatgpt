from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path

import inject_contextual_affiliate_growth_v177_core as _core
from inject_contextual_affiliate_growth_v177_core import *  # noqa: F401,F403

PRODUCT_MAP_ROUTE = "amazon-elektrik-urunleri/konuya-gore-urun-haritasi/index.html"
PRODUCT_MAP_PLACEHOLDER = 'data-alo186-product-map-placeholder="true"'
PRODUCT_MAP_PRODUCTS = ("modem_mini_ups", "flashlight", "powerbank_pd")


def product_map_html(base_path: str) -> str:
    module = _core.section_html(PRODUCT_MAP_ROUTE, PRODUCT_MAP_PRODUCTS, base_path)
    module = module.replace(
        '<p class="alo186-contextual-commerce__disclosure">',
        (
            '<p class="alo186-contextual-commerce__disclosure" '
            f'data-affiliate-tag="{html.escape(_core.TAG)}">'
        ),
        1,
    )
    return (
        module.replace(
            "Sonuca bağlı ürün seçenekleri",
            "Göreve göre kontrollü ürün başlangıçları",
            1,
        )
        .replace(
            "Bu rehberde doğrulanan ihtiyaca göre ürün sınıfları",
            "Üç sık ihtiyaç için teknik ürün başlangıçları",
            1,
        )
        .replace(
            "Önce mevcut ekipmanı test edin. Yalnız gerçek bir açık kaldıysa teknik rehberi inceleyin; mağaza bağlantısı üç onaydan sonra açılır. ALO186 fiyat, stok, puan, satıcı, teslimat veya garanti bilgisi yayımlamaz.",
            "Bu merkez genel alışveriş listesi değildir. İnternet sürekliliği, güvenli kesinti aydınlatması ve taşınabilir USB-C enerji için önce ücretsiz teknik rehberi açın. Yalnız ölçülmüş bir eksik kalırsa mağaza seçenekleri üç onaydan sonra açılır; fiyat, stok, puan, satıcı, teslimat ve garanti bilgileri Amazon Türkiye üzerinde yeniden doğrulanır.",
            1,
        )
    )


def inject_product_map(site: Path, base_path: str) -> dict[str, object]:
    path = site / PRODUCT_MAP_ROUTE
    if not path.is_file():
        return {
            "productMapInjectedRouteCount": 0,
            "productMapAlreadyInjectedRouteCount": 0,
            "productMapMissingRouteCount": 1,
        }

    source = path.read_text(encoding="utf-8")
    if _core.MARKER in source:
        return {
            "productMapInjectedRouteCount": 0,
            "productMapAlreadyInjectedRouteCount": 1,
            "productMapMissingRouteCount": 0,
        }
    if PRODUCT_MAP_PLACEHOLDER not in source:
        raise RuntimeError(
            "ALO186 v177 ürün haritası placeholder sözleşmesi eksik: "
            + PRODUCT_MAP_ROUTE
        )

    css_tag = (
        f'<link rel="stylesheet" href="{html.escape(_core.public_url(base_path, "/" + _core.CSS_FILE))}" '
        'data-alo186-contextual-affiliate-css-v177="true">'
    )
    js_tag = (
        f'<script defer src="{html.escape(_core.public_url(base_path, "/" + _core.JS_FILE))}" '
        'data-alo186-contextual-affiliate-js-v177="true"></script>'
    )
    updated = _core.inject_asset(source, css_tag, "</head>")
    pattern = re.compile(
        r'<section\b(?=[^>]*\bdata-alo186-product-map-placeholder=["\']true["\'])[^>]*>\s*</section>',
        re.IGNORECASE | re.DOTALL,
    )
    updated, replaced = pattern.subn(product_map_html(base_path), updated, count=1)
    if replaced != 1:
        raise RuntimeError(
            "ALO186 v177 ürün haritası placeholder tekil olarak değiştirilemedi: "
            + PRODUCT_MAP_ROUTE
        )
    updated = _core.inject_asset(updated, js_tag, "</body>")
    path.write_text(updated, encoding="utf-8")
    return {
        "productMapInjectedRouteCount": 1,
        "productMapAlreadyInjectedRouteCount": 0,
        "productMapMissingRouteCount": 0,
    }


def audit_product_map(site: Path, base_path: str) -> dict[str, object]:
    failures: list[str] = []
    path = site / PRODUCT_MAP_ROUTE
    if not path.is_file():
        failures.append(f"Ürün haritası rotası eksik: {PRODUCT_MAP_ROUTE}")
        text = ""
    else:
        text = path.read_text(encoding="utf-8")

    marker_count = text.count(_core.MARKER)
    card_count = text.count('class="alo186-contextual-product"')
    gate_count = text.count("data-affiliate-gate=")
    if marker_count != 1:
        failures.append(f"Ürün haritası v177 marker sayısı yanlış: {marker_count}")
    if PRODUCT_MAP_PLACEHOLDER in text:
        failures.append("Ürün haritası placeholder yayında kaldı")
    if card_count != len(PRODUCT_MAP_PRODUCTS):
        failures.append(f"Ürün haritası kart sayısı yanlış: {card_count}")
    if gate_count != 3:
        failures.append(f"Ürün haritası üçlü güven kapısı eksik: {gate_count}")
    if _core.DISCLOSURE not in text:
        failures.append("Ürün haritası Amazon açıklaması eksik")
    if _core.TAG not in text:
        failures.append("Ürün haritası satış ortaklığı kimliği eksik")
    if _core.public_url(base_path, "/" + _core.CSS_FILE) not in text:
        failures.append("Ürün haritası CSS bağlantısı eksik")
    if _core.public_url(base_path, "/" + _core.JS_FILE) not in text:
        failures.append("Ürün haritası JS bağlantısı eksik")
    if re.search(
        r'<a\b[^>]*href=["\']https?://(?:www\.)?(?:amazon\.com\.tr|amzn\.to)',
        text,
        re.IGNORECASE,
    ):
        failures.append("Ürün haritasında kapısız mağaza bağlantısı var")
    if re.search(
        r'"@type"\s*:\s*"(?:Product|Offer|AggregateRating)"',
        text,
        re.IGNORECASE,
    ):
        failures.append("Ürün haritasında doğrulanmamış ticari şema var")
    for key in PRODUCT_MAP_PRODUCTS:
        if f'data-product-class="{key}"' not in text:
            failures.append(f"Ürün haritası sınıfı eksik: {key}")

    if failures:
        raise RuntimeError(
            "ALO186 v177 ürün haritası denetimi başarısız:\n- "
            + "\n- ".join(failures)
        )
    return {
        "productMapRoute": "/" + PRODUCT_MAP_ROUTE.removesuffix("index.html"),
        "productMapModuleCount": marker_count,
        "productMapPlacementCount": card_count,
        "productMapGateCount": gate_count,
        "productMapProductClassCount": len(PRODUCT_MAP_PRODUCTS),
    }


def update_product_map_release(
    path: Path,
    state: dict[str, object],
    audit_report: dict[str, object],
) -> None:
    if not path.is_file():
        return
    payload = json.loads(path.read_text(encoding="utf-8"))
    release = payload.setdefault("contextualAffiliateGrowth", {})
    release.update(
        {
            "productMapRoute": audit_report["productMapRoute"],
            "productMapInjectedRouteCount": state[
                "productMapInjectedRouteCount"
            ],
            "productMapAlreadyInjectedRouteCount": state[
                "productMapAlreadyInjectedRouteCount"
            ],
            "productMapMissingRouteCount": state["productMapMissingRouteCount"],
            "productMapPlacementCount": audit_report[
                "productMapPlacementCount"
            ],
            "productMapGateCount": audit_report["productMapGateCount"],
            "productMapProductClasses": list(PRODUCT_MAP_PRODUCTS),
            "productMapAffiliateTag": _core.TAG,
            "productMapExistingProductFirst": True,
        }
    )
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def audit(site: Path, base_path: str = "") -> dict[str, object]:
    site = site.resolve()
    base_path = _core.normalize_base_path(base_path)
    guide_report = _core.audit(site, base_path)
    map_report = audit_product_map(site, base_path)
    return {**guide_report, **map_report}


def run(site: Path, base_path: str = "") -> dict[str, object]:
    site = site.resolve()
    base_path = _core.normalize_base_path(base_path)
    guide_report = _core.run(site, base_path)
    map_state = inject_product_map(site, base_path)
    if map_state["productMapMissingRouteCount"]:
        raise RuntimeError(
            "ALO186 v177 ürün haritası artifact rotası eksik: "
            + PRODUCT_MAP_ROUTE
        )
    map_report = audit_product_map(site, base_path)
    report = {**guide_report, **map_state, **map_report}
    for release_name in ("alo186-release.json", "pages-release.json"):
        update_product_map_release(site / release_name, map_state, map_report)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "ALO186 yüksek niyetli rehberlerine ve ürün haritasına üç kapılı "
            "bağlamsal ürün sınıfları ekler."
        )
    )
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--base-path", default="")
    args = parser.parse_args()
    print(json.dumps(run(args.site, args.base_path), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
