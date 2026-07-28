from __future__ import annotations

import contextlib
import functools
import hashlib
import json
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from alo186.deployment.verify_live_release import (
    DEFAULT_CRITICAL_PATHS,
    parse_checksums,
    route_bundle_path,
    verify,
)

COMMIT = "a" * 40


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_bundle(root: Path, *, commit: str = COMMIT) -> None:
    for route in DEFAULT_CRITICAL_PATHS:
        target = root / route_bundle_path(route)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(f"<!doctype html><title>{route}</title><h1>{route}</h1>\n", encoding="utf-8")

    release = {
        "schemaVersion": 3,
        "commit": commit,
        "canonicalHost": "https://www.alo186.com",
        "routeCount": 42,
        "deviceDamageDeadline": "10 iş günü",
        "publicArtifactPolicy": {
            "sourceDocsExcluded": True,
            "testsExcluded": True,
            "packageMetadataExcluded": True,
        },
    }
    (root / "alo186-release.json").write_text(
        json.dumps(release, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    files = sorted(path for path in root.rglob("*") if path.is_file())
    lines = [f"{sha256(path)}  {path.relative_to(root).as_posix()}" for path in files]
    (root / "checksums.sha256").write_text("\n".join(lines) + "\n", encoding="utf-8")


@contextlib.contextmanager
def serve(directory: Path):
    handler = functools.partial(SimpleHTTPRequestHandler, directory=str(directory))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        host, port = server.server_address
        yield f"http://{host}:{port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_parse_checksums_and_route_mapping():
    parsed = parse_checksums("a" * 64 + "  elektrik-portali/index.html\n")
    assert parsed["elektrik-portali/index.html"] == "a" * 64
    assert route_bundle_path("/elektrik-portali") == "elektrik-portali/index.html"
    assert route_bundle_path("/hesaplama/") == "hesaplama/index.html"


def test_exact_live_bundle_passes(tmp_path: Path):
    local = tmp_path / "local"
    live = tmp_path / "live"
    write_bundle(local)
    write_bundle(live)
    with serve(live) as base_url:
        report = verify(base_url=base_url, bundle=local, expected_commit=COMMIT)
    assert report["ok"] is True, report["failures"]
    assert all(item.get("matched", True) for item in report["results"])


def test_stale_release_commit_fails(tmp_path: Path):
    local = tmp_path / "local"
    live = tmp_path / "live"
    write_bundle(local)
    write_bundle(live, commit="b" * 40)
    with serve(live) as base_url:
        report = verify(base_url=base_url, bundle=local, expected_commit=COMMIT)
    assert report["ok"] is False
    assert any("canlı release commit farklı" in item for item in report["failures"])


def test_route_byte_drift_fails(tmp_path: Path):
    local = tmp_path / "local"
    live = tmp_path / "live"
    write_bundle(local)
    write_bundle(live)
    target = live / "karar-motoru/index.html"
    target.write_text(target.read_text(encoding="utf-8") + "<!-- drift -->\n", encoding="utf-8")
    with serve(live) as base_url:
        report = verify(base_url=base_url, bundle=local, expected_commit=COMMIT)
    assert report["ok"] is False
    assert any("canlı route byte drift: /karar-motoru" in item for item in report["failures"])


def test_missing_release_metadata_is_explicit(tmp_path: Path):
    local = tmp_path / "local"
    live = tmp_path / "live"
    write_bundle(local)
    write_bundle(live)
    (live / "alo186-release.json").unlink()
    with serve(live) as base_url:
        report = verify(base_url=base_url, bundle=local, expected_commit=COMMIT)
    assert report["ok"] is False
    assert any("production GitHub artifact'ını sunmuyor" in item for item in report["failures"])


def test_diagnostic_mode_allows_route_bytes_but_not_manifest_drift(tmp_path: Path):
    local = tmp_path / "local"
    live = tmp_path / "live"
    write_bundle(local)
    write_bundle(live)
    target = live / "edas-bul/index.html"
    target.write_text(target.read_text(encoding="utf-8") + "<!-- injected -->\n", encoding="utf-8")
    with serve(live) as base_url:
        report = verify(
            base_url=base_url,
            bundle=local,
            expected_commit=COMMIT,
            allow_content_drift=True,
        )
    assert report["ok"] is True, report["failures"]
    row = next(item for item in report["results"] if item.get("path") == "/edas-bul")
    assert row["matched"] is False
