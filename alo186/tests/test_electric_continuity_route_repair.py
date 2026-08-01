from __future__ import annotations

import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEPLOYMENT = ROOT / "alo186" / "deployment"
sys.path.insert(0, str(DEPLOYMENT))

from build_static_site import copy_route, load_effective_manifest  # noqa: E402

LEGACY_PATH = "/hizmetler/elektrik-surekliligi/"
TARGET_PATH = "/kurumsal-elektrik-surekliligi-on-degerlendirme"
TARGET_URL = f"https://www.alo186.com{TARGET_PATH}"
SOURCE = ROOT / "alo186" / "hizmetler" / "elektrik-surekliligi" / "index.html"
TARGET_SOURCE = ROOT / "alo186" / "kurumsal-on-degerlendirme" / "index.html"


def test_route_bridge_is_safe_and_points_to_the_live_service() -> None:
    html = SOURCE.read_text(encoding="utf-8")

    assert '<meta name="robots" content="noindex,follow">' in html
    assert f'<link rel="canonical" href="{TARGET_URL}">' in html
    assert f'content="0; url={TARGET_PATH}"' in html
    assert f'href="{TARGET_PATH}"' in html
    assert "ALO186 bağımsız bilgi platformudur" in html
    assert "amazon" not in html.lower()
    assert "mailto:" not in html.lower()

    target_html = TARGET_SOURCE.read_text(encoding="utf-8")
    assert f'<link rel="canonical" href="{TARGET_URL}">' in target_html


def test_route_bridge_is_part_of_the_effective_production_manifest() -> None:
    manifest = load_effective_manifest(ROOT)
    matching = [route for route in manifest["routes"] if route["canonicalPath"] == LEGACY_PATH]

    assert matching == [
        {
            "source": "alo186/hizmetler/elektrik-surekliligi/index.html",
            "canonicalPath": LEGACY_PATH,
            "type": "legacy-route-bridge",
        }
    ]

    with tempfile.TemporaryDirectory() as temporary_directory:
        output = Path(temporary_directory)
        copy_route(ROOT, output, matching[0])
        published = output / "hizmetler" / "elektrik-surekliligi" / "index.html"
        assert published.is_file()
        assert TARGET_URL in published.read_text(encoding="utf-8")


def test_existing_service_calls_to_action_no_longer_resolve_to_a_missing_route() -> None:
    pattern = re.compile(r'href=["\']' + re.escape(LEGACY_PATH) + r'["\']')
    referencing_files: list[Path] = []

    for path in sorted((ROOT / "alo186").rglob("*.html")):
        if path == SOURCE:
            continue
        if pattern.search(path.read_text(encoding="utf-8")):
            referencing_files.append(path)

    # Bu rota tekil bir kenar durum değil; çok sayıda teknik sayfadaki hizmet CTA'sıdır.
    assert len(referencing_files) >= 10
    assert SOURCE.is_file()
