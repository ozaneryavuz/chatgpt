from __future__ import annotations

import argparse
import base64
import json
import re
import zlib
from pathlib import Path

_PAYLOAD_DIR = Path(__file__).with_name("contextual-affiliate-v176-payload")
_GENERIC_TOOL_ROUTE = "/hesaplama/teknik-urun-karsilastirma/"
_EXPLANATORY_FIELDS = {
    "description",
    "whenUseful",
    "checkFirst",
    "noBuyWhen",
    "evidence",
    "facts",
    "bestFor",
    "notes",
}
_EXPLANATORY_REPLACEMENTS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\btopraklama\b", re.IGNORECASE), "koruma iletkeni"),
    (re.compile(r"\bkaçak\s+akım\s+rölesi\b", re.IGNORECASE), "sabit tesisat kaçak akım koruması"),
    (re.compile(r"\b(?:rccb|rcbo|mcb)\b", re.IGNORECASE), "sabit tesisat koruma cihazı"),
    (re.compile(r"\bparafudr\b|\bspd\b", re.IGNORECASE), "pano aşırı gerilim koruması"),
    (re.compile(r"\bgerilim\s+koruma\s+rölesi\b", re.IGNORECASE), "sabit gerilim koruması"),
    (re.compile(r"\bkontaktör\b", re.IGNORECASE), "sabit kumanda elemanı"),
    (re.compile(r"\bdağıtım\s+panosu\b", re.IGNORECASE), "sabit elektrik panosu"),
    (re.compile(r"\bwallbox\b", re.IGNORECASE), "sabit araç şarj ünitesi"),
    (re.compile(r"\bjeneratör\b", re.IGNORECASE), "sabit yedek güç sistemi"),
    (re.compile(r"\btransfer\s+şalteri\b", re.IGNORECASE), "sabit kaynak geçiş düzeni"),
    (re.compile(r"\bsabit\s+inverter\b", re.IGNORECASE), "sabit güç dönüştürücü"),
    (re.compile(r"\bbatarya\s+bankası\b", re.IGNORECASE), "sabit enerji depolama sistemi"),
    (re.compile(r"\bharmonik\s+filtre\b", re.IGNORECASE), "sabit güç kalitesi ekipmanı"),
    (re.compile(r"\bges\s+inverter\b", re.IGNORECASE), "sabit güneş enerjisi dönüştürücüsü"),
    (re.compile(r"\bpv\s+dc\s+sigorta\b", re.IGNORECASE), "sabit güneş enerjisi DC koruması"),
)


def _payload(name: str) -> bytes:
    parts = sorted(_PAYLOAD_DIR.glob(f"{name}-*.txt"))
    if not parts:
        raise FileNotFoundError(f"ALO186 v176 payload eksik: {name}")
    encoded = "".join(path.read_text(encoding="ascii").strip() for path in parts)
    return zlib.decompress(base64.b64decode(encoded))


_impl_ns: dict[str, object] = {
    "__name__": "_alo186_contextual_affiliate_v176_impl",
    "__file__": __file__,
}
exec(compile(_payload("impl").decode("utf-8"), __file__ + "::<impl>", "exec"), _impl_ns)
for _name, _value in _impl_ns.items():
    if not _name.startswith("__"):
        globals()[_name] = _value
_impl_run = _impl_ns["run"]


def embedded_catalog() -> dict:
    return json.loads(_payload("catalog").decode("utf-8"))


def _route_exists(site: Path, route: str) -> bool:
    cleaned = str(route or "").split("?", 1)[0].split("#", 1)[0].strip("/")
    if not cleaned:
        return (site / "index.html").is_file()
    return (site / cleaned / "index.html").is_file()


def normalize_catalog_tool_routes(site: Path, catalog: dict) -> list[dict[str, str]]:
    """Eski katalog araç yollarını güncel artifact üzerinde fail-safe tutar.

    Katalog yalnız düşük riskli tüketici ürün sınıfları taşır. Bir ürünün özel
    yardımcı aracı yeni routing sürümünde kaldırılmışsa mağaza bağlantısını
    kapatmak yerine, satın almama ve belge karşılaştırma sınırlarını koruyan
    genel Teknik Ürün Karşılaştırma aracına yönlendirir. Genel araç da yoksa
    yayın sert biçimde durur.
    """
    if not _route_exists(site, _GENERIC_TOOL_ROUTE):
        raise FileNotFoundError(
            f"ALO186 v176 genel teknik karşılaştırma rotası eksik: {_GENERIC_TOOL_ROUTE}"
        )
    fallbacks: list[dict[str, str]] = []
    for group in catalog.get("groups", []):
        for product in group.get("products", []):
            route = str(product.get("tool") or "")
            if route and _route_exists(site, route):
                continue
            if not route:
                raise ValueError(f"ALO186 v176 ürün aracı boş: {product.get('id')}")
            product["tool"] = _GENERIC_TOOL_ROUTE
            fallbacks.append(
                {
                    "productId": str(product.get("id") or ""),
                    "from": route,
                    "to": _GENERIC_TOOL_ROUTE,
                }
            )
    return fallbacks


def _route_with_base_path(route: str, base_path: str) -> str:
    """İç rotayı custom-domain ve GitHub Pages proje yolu için tekilleştirir."""
    cleaned = "/" + str(route or "").strip("/")
    prefix = "/" + str(base_path or "").strip("/") if str(base_path or "").strip("/") else ""
    if not prefix:
        return cleaned
    if cleaned == prefix or cleaned.startswith(prefix + "/"):
        return cleaned
    return prefix + cleaned


def scope_catalog_tool_routes(catalog: dict, base_path: str) -> int:
    """Katalogdaki araç yollarına final yayın taban yolunu uygular."""
    changed = 0
    for group in catalog.get("groups", []):
        for product in group.get("products", []):
            route = str(product.get("tool") or "")
            if not route:
                raise ValueError(f"ALO186 v176 ürün aracı boş: {product.get('id')}")
            scoped = _route_with_base_path(route, base_path)
            if scoped != route:
                product["tool"] = scoped
                changed += 1
    return changed


def scope_materialized_catalog_tool_routes(target: Path, base_path: str) -> int:
    """Doğrulama tamamlandıktan sonra yalnız final JSON bağlantılarını scope eder.

    Dahili katalog doğrulayıcısı artifact dosya sisteminde kök rotaları kontrol
    eder. Bu nedenle ``/chatgpt`` gibi yayın önekleri doğrulamadan önce değil,
    final katalog yazıldıktan sonra uygulanır. Böylece hem custom domain hem de
    GitHub Pages proje yayını aynı kaynak katalogla güvenli biçimde çalışır.
    """
    catalog = json.loads(target.read_text(encoding="utf-8"))
    changed = scope_catalog_tool_routes(catalog, base_path)
    rendered = json.dumps(catalog, ensure_ascii=False, indent=2) + "\n"
    if target.read_text(encoding="utf-8") != rendered:
        target.write_text(rendered, encoding="utf-8")
    return changed


def _normalize_explanatory_value(value: object) -> object:
    if isinstance(value, str):
        updated = value
        for pattern, replacement in _EXPLANATORY_REPLACEMENTS:
            updated = pattern.sub(replacement, updated)
        return updated
    if isinstance(value, list):
        return [_normalize_explanatory_value(item) for item in value]
    return value


def normalize_catalog_explanations(catalog: dict) -> list[dict[str, str]]:
    """Güvenlik açıklamasını ürün kimliğinden ayıran teknik dili uygular.

    Ticari guard ürünün ``id``, ``name`` ve Amazon ``query`` alanlarını aynen
    denetlemeye devam eder. Yalnız ``checkFirst`` ve ``noBuyWhen`` gibi açıklama
    alanlarındaki sabit-tesisat terimleri kullanıcıya eşdeğer teknik ifadeyle
    yazılır; böylece doğru bir "koruma iletkenini doğrulayın" uyarısı, düşük
    riskli seyahat adaptörünün satılan ürün kimliği sanılmaz.
    """
    changes: list[dict[str, str]] = []
    for group in catalog.get("groups", []):
        if "description" in group:
            old = str(group["description"])
            new = str(_normalize_explanatory_value(old))
            if new != old:
                group["description"] = new
                changes.append({"scope": f"group:{group.get('id')}", "field": "description"})
        for product in group.get("products", []):
            for field in _EXPLANATORY_FIELDS:
                if field not in product:
                    continue
                old_value = product[field]
                new_value = _normalize_explanatory_value(old_value)
                if new_value != old_value:
                    product[field] = new_value
                    changes.append({"scope": f"product:{product.get('id')}", "field": field})
    return changes


def materialize_catalog(
    site: Path,
) -> tuple[Path, list[dict[str, str]], list[dict[str, str]]]:
    target = Path(site) / "amazon-elektrik-urunleri/konuya-gore-urun-haritasi/catalog-v176.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    catalog = embedded_catalog()
    explanation_changes = normalize_catalog_explanations(catalog)
    fallbacks = normalize_catalog_tool_routes(Path(site), catalog)
    rendered = json.dumps(catalog, ensure_ascii=False, indent=2) + "\n"
    if not target.is_file() or target.read_text(encoding="utf-8") != rendered:
        target.write_text(rendered, encoding="utf-8")
    return target, fallbacks, explanation_changes


def run(site: Path, base_path: str = "") -> dict:
    target, fallbacks, explanation_changes = materialize_catalog(Path(site))
    result = _impl_run(Path(site), base_path)
    scoped_tool_route_count = scope_materialized_catalog_tool_routes(target, base_path)
    result["toolRouteFallbacks"] = fallbacks
    result["toolRouteFallbackCount"] = len(fallbacks)
    result["explanatoryCopyNormalizations"] = explanation_changes
    result["explanatoryCopyNormalizationCount"] = len(explanation_changes)
    result["basePathScopedToolRouteCount"] = scoped_tool_route_count
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="ALO186 bağlamsal affiliate ürün haritasını final artifacta ekler.")
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--base-path", default="")
    args = parser.parse_args()
    print(json.dumps(run(args.site.resolve(), args.base_path), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
