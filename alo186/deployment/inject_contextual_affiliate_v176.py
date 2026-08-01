from __future__ import annotations

import argparse
import base64
import json
import zlib
from pathlib import Path

_PAYLOAD_DIR = Path(__file__).with_name("contextual-affiliate-v176-payload")
_GENERIC_TOOL_ROUTE = "/hesaplama/teknik-urun-karsilastirma/"


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


def materialize_catalog(site: Path) -> tuple[Path, list[dict[str, str]]]:
    target = Path(site) / "amazon-elektrik-urunleri/konuya-gore-urun-haritasi/catalog-v176.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    catalog = embedded_catalog()
    fallbacks = normalize_catalog_tool_routes(Path(site), catalog)
    rendered = json.dumps(catalog, ensure_ascii=False, indent=2) + "\n"
    if not target.is_file() or target.read_text(encoding="utf-8") != rendered:
        target.write_text(rendered, encoding="utf-8")
    return target, fallbacks


def run(site: Path, base_path: str = "") -> dict:
    _target, fallbacks = materialize_catalog(Path(site))
    result = _impl_run(Path(site), base_path)
    result["toolRouteFallbacks"] = fallbacks
    result["toolRouteFallbackCount"] = len(fallbacks)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="ALO186 bağlamsal affiliate ürün haritasını final artifacta ekler.")
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--base-path", default="")
    args = parser.parse_args()
    print(json.dumps(run(args.site.resolve(), args.base_path), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
