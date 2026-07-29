from __future__ import annotations

import importlib.util
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEPLOYMENT = ROOT / "deployment"
if str(DEPLOYMENT) not in sys.path:
    sys.path.insert(0, str(DEPLOYMENT))

import prepare_github_pages as pages  # noqa: E402


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Modül yüklenemedi: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


synthetic = load_module(
    "alo186_synthetic_check", ROOT / "infra" / "observability" / "synthetic_check.py"
)


def assert_gateway(base_path: str, noindex: bool) -> None:
    html = pages.gateway_html(base_path, noindex)
    analysis = synthetic.analyze_device_damage_text(html)
    assert analysis["has10BusinessDayDamageClaim"] is True, analysis
    assert analysis["hasAlo186NoApplicationDisclaimer"] is True, analysis
    assert analysis["has30DayDamageClaim"] is False, analysis
    assert pages.DEVICE_DAMAGE_MARKER in html
    guide = pages.public_url(base_path, pages.DEVICE_DAMAGE_ROUTE)
    assert f'href="{guide}"' in html
    robots = "noindex,follow" if noindex else "index,follow,max-image-preview:large"
    assert f'content="{robots}"' in html

    with tempfile.TemporaryDirectory() as directory:
        site = Path(directory)
        (site / "index.html").write_text(html, encoding="utf-8")
        pages.validate_root_legal_deadline(site, pages.normalize_base_path(base_path))


def test_custom_domain_root_has_current_device_damage_deadline() -> None:
    assert_gateway("", False)


def test_project_path_root_keeps_noindex_and_prefixed_guide() -> None:
    assert_gateway("/chatgpt", True)


def test_core_source_is_preserved_for_reviewable_wrapper() -> None:
    core = DEPLOYMENT / "prepare_github_pages_core.py"
    assert core.is_file()
    text = core.read_text(encoding="utf-8")
    assert "def prepare(" in text
    assert "def gateway_html(" in text


if __name__ == "__main__":
    test_custom_domain_root_has_current_device_damage_deadline()
    test_project_path_root_keeps_noindex_and_prefixed_guide()
    test_core_source_is_preserved_for_reviewable_wrapper()
    print("PASS: Pages kök cihaz hasarı süresi, açıklama ve base-path doğrulandı.")
