from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEPLOYMENT = ROOT / "alo186" / "deployment"
ENTRY = DEPLOYMENT / "build_static_site.py"


def load_builder():
    deployment_path = str(DEPLOYMENT)
    if deployment_path not in sys.path:
        sys.path.insert(0, deployment_path)
    spec = importlib.util.spec_from_file_location("alo186_build_static_site_v200", ENTRY)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_legacy_article_route_is_normalized_strictly() -> None:
    builder = load_builder()
    route = builder.validate_route(
        {
            "path": "/haberler/ornek-guvenli-haber",
            "file": "haberler/ornek-guvenli-haber/index.html",
            "intent": "örnek kullanıcı niyeti",
        },
        "fixture.json",
    )
    assert route == {
        "canonicalPath": "/haberler/ornek-guvenli-haber",
        "source": "alo186/haberler/ornek-guvenli-haber/index.html",
        "type": "article",
    }


def invalid_routes() -> list[dict]:
    return [
        {"path": "/hesaplama/ornek", "file": "hesaplama/ornek/index.html", "intent": "haber dışı rota"},
        {"path": "/haberler/ornek-a", "file": "haberler/ornek-b/index.html", "intent": "kaynak ve canonical uyuşmuyor"},
        {"path": "/haberler/ornek", "file": "haberler/ornek/index.html", "intent": ""},
        {"canonicalPath": "/haberler/eksik-modern", "path": "/haberler/eksik-modern", "file": "haberler/eksik-modern/index.html", "intent": "karışık şema"},
    ]


def test_invalid_or_mixed_legacy_routes_fail_closed() -> None:
    builder = load_builder()
    for route in invalid_routes():
        try:
            builder.validate_route(route, "invalid-fixture.json")
        except ValueError:
            continue
        raise AssertionError(f"Geçersiz legacy rota kabul edildi: {route!r}")


def test_current_manifest_builds_with_run123_and_v200_routes() -> None:
    builder = load_builder()
    manifest = builder.load_effective_manifest(ROOT)
    routes = {route["canonicalPath"]: route for route in manifest["routes"]}

    run123 = [
        "/haberler/ges-inverter-afci-dc-arc-fault-seri-ark-alarmi-teshis",
        "/haberler/kompanzasyon-harmonik-rezonans-kondansator-reaktor-asiri-akim-teshis",
        "/haberler/edas-12-saati-asan-elektrik-kesintisi-tazminati-odeme-kontrolu",
    ]
    for path in run123:
        assert routes[path]["type"] == "article"
        assert routes[path]["source"] == f"alo186/{path.strip('/')}/index.html"

    product_route = "/amazon-elektrik-urunleri/kamera-kayit-yuksek-dayanim-microsd-secimi/"
    assert routes[product_route] == {
        "canonicalPath": product_route,
        "source": "alo186/amazon-elektrik-urunleri/kamera-kayit-yuksek-dayanim-microsd-secimi/index.html",
        "type": "collection",
    }
    assert manifest["version"] >= 200


def test_run123_dual_shape_remains_explicit_and_aligned() -> None:
    overlay = json.loads(
        (ROOT / "alo186" / "deployment" / "routing-overlays" / "content-authority-run123.json").read_text(encoding="utf-8")
    )
    assert overlay["routes"]
    legacy_fields = {"path", "file", "intent"}
    modern_fields = {"source", "canonicalPath", "type"}
    for route in overlay["routes"]:
        assert legacy_fields <= set(route)
        assert modern_fields <= set(route)
        assert route["canonicalPath"] == route["path"]
        assert route["source"] == f"alo186/{route['file']}"
        assert route["type"] == "article"
        assert route["intent"].strip()


def main() -> None:
    test_legacy_article_route_is_normalized_strictly()
    test_invalid_or_mixed_legacy_routes_fail_closed()
    test_current_manifest_builds_with_run123_and_v200_routes()
    test_run123_dual_shape_remains_explicit_and_aligned()
    print(json.dumps({"ok": True, "legacyRoutes": "fail-closed", "dualShape": "aligned"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
