from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

DEPLOYMENT = Path(__file__).resolve().parents[1] / "deployment"
sys.path.insert(0, str(DEPLOYMENT))

from finalize_pages_service_worker import MARKER, finalize, finalize_and_record  # noqa: E402


def page(body: str = "<main>ok</main>") -> str:
    return f"<!doctype html><html><head><title>x</title></head><body>{body}</body></html>"


def run_case(base_path: str) -> None:
    with tempfile.TemporaryDirectory() as temporary:
        site = Path(temporary)
        (site / "haberler/a").mkdir(parents=True)
        (site / "haberler/b").mkdir(parents=True)
        (site / "index.html").write_text(page(), encoding="utf-8")
        (site / "haberler/a/index.html").write_text(page(), encoding="utf-8")
        preserved = page(f'<script {MARKER}></script>')
        (site / "haberler/b/index.html").write_text(preserved, encoding="utf-8")
        (site / "pages-release.json").write_text(
            json.dumps({"basePath": base_path}), encoding="utf-8"
        )

        first = finalize_and_record(site, base_path)
        assert first["checkedPages"] == 3
        assert first["injectedPages"] == 2
        assert first["preservedPages"] == 1

        expected_sw = f"{base_path}/sw.js" if base_path else "/sw.js"
        expected_scope = f"{base_path}/" if base_path else "/"
        for html_path in site.rglob("*.html"):
            html = html_path.read_text(encoding="utf-8")
            assert html.count(MARKER) == 1, html_path
            if html_path.as_posix().endswith("haberler/b/index.html"):
                continue
            assert f'register("{expected_sw}"' in html, html_path
            assert f'scope:"{expected_scope}"' in html, html_path

        receipt = json.loads((site / "pages-release.json").read_text(encoding="utf-8"))
        recorded = receipt["serviceWorkerRegistrationFinalization"]
        assert recorded["checkedPages"] == 3
        assert recorded["basePath"] == base_path
        assert (site / "checksums.sha256").is_file()

        second = finalize(site, base_path)
        assert second["injectedPages"] == 0
        assert second["preservedPages"] == 3
        for html_path in site.rglob("*.html"):
            assert html_path.read_text(encoding="utf-8").count(MARKER) == 1


def invalid_html_is_rejected() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        site = Path(temporary)
        (site / "index.html").write_text("<!doctype html><html><body>broken", encoding="utf-8")
        try:
            finalize(site, "")
        except RuntimeError as exc:
            assert "geçersiz HTML" in str(exc)
        else:
            raise AssertionError("Kapanmamış HTML fail-closed reddedilmeliydi")


if __name__ == "__main__":
    run_case("")
    run_case("/chatgpt")
    invalid_html_is_rejected()
    print("final service worker registration: PASS")
