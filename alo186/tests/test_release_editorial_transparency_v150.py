from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TRUST_MARKER = 'data-alo186-editorial-trust="true"'
TRUST_JSONLD_MARKER = 'data-alo186-editorial-trust-jsonld="true"'
STATUS_ROUTE = "/yayin-durumu/"


def run(command: list[str]) -> None:
    subprocess.run(command, cwd=ROOT, check=True)


source_page = (ROOT / "alo186/yayin-durumu/index.html").read_text(encoding="utf-8")
source_prepare = (ROOT / "alo186/deployment/prepare_github_pages.py").read_text(encoding="utf-8")
source_release = (ROOT / "alo186/deployment/finalize_release_transparency.py").read_text(encoding="utf-8")
source_trust = (ROOT / "alo186/deployment/finalize_editorial_trust.py").read_text(encoding="utf-8")
source_smoke = (ROOT / "alo186/deployment/live_release_smoke.py").read_text(encoding="utf-8")
workflow = (ROOT / ".github/workflows/alo186-live-release-transparency-smoke.yml").read_text(encoding="utf-8")
overlay = json.loads((ROOT / "alo186/deployment/routing-overlays/150-release-editorial-transparency.json").read_text(encoding="utf-8"))

assert overlay["version"] == 150
assert overlay["routes"] == [{
    "source": "alo186/yayin-durumu/index.html",
    "canonicalPath": STATUS_ROUTE,
    "type": "status",
}]
for token in (
    "Yayın paketi hazırlanırken doğrulanıyor",
    "data-release-commit",
    "data-release-critical-routes",
    "data-release-json",
    "Bu kayıt neyi kanıtlar?",
    "Bu kayıt neyi kanıtlamaz?",
):
    assert token in source_page, token
for token in (
    "finalize_editorial_trust",
    "finalize_release_transparency",
    'release["editorialTrustV1"]',
    'release["releaseTransparencyV1"]',
):
    assert token in source_prepare, token
for token in (
    '"status": "ready"',
    '"deviceDamageDeadline": deadline',
    '"allCriticalRoutesPresent": True',
    '"personalDataStored": False',
):
    assert token in source_release, token
for token in (
    TRUST_MARKER,
    TRUST_JSONLD_MARKER,
    "Yayın durumunu doğrula",
    "Hata veya düzeltme bildir",
    '"namedIndividualClaimed": False',
):
    assert token in source_trust, token
for token in (
    "/release-status.json",
    "deviceDamageDeadline",
    "commitAccepted",
    "criticalRoutes",
    "--self-test",
):
    assert token in source_smoke, token
assert "ALO186 GitHub Pages — sunucusuz canlı yayın" in workflow
assert "secrets." not in workflow

run([sys.executable, "-m", "py_compile", "alo186/deployment/finalize_release_transparency.py"])
run([sys.executable, "-m", "py_compile", "alo186/deployment/finalize_editorial_trust.py"])
run([sys.executable, "-m", "py_compile", "alo186/deployment/live_release_smoke.py"])
run([sys.executable, "alo186/deployment/live_release_smoke.py", "--self-test"])

with tempfile.TemporaryDirectory(prefix="alo186-release-transparency-v150-") as folder:
    temp = Path(folder)
    canonical = temp / "canonical"
    run([
        sys.executable,
        "alo186/deployment/build_static_site.py",
        "--output",
        str(canonical),
        "--commit",
        "release-transparency-v150-test",
    ])
    canonical_release = json.loads((canonical / "alo186-release.json").read_text(encoding="utf-8"))
    assert canonical_release["routingVersion"] >= 150
    assert any(item["canonicalPath"] == STATUS_ROUTE for item in canonical_release["routes"])
    article_routes = [item for item in canonical_release["routes"] if item["type"] == "article"]
    assert len(article_routes) >= 50

    results = []
    for label, base_path in (("custom", ""), ("project", "/chatgpt")):
        target = temp / label
        subprocess.run(["cp", "-a", str(canonical), str(target)], check=True)
        run([
            sys.executable,
            "alo186/deployment/prepare_github_pages.py",
            "--site",
            str(target),
            "--base-path",
            base_path,
            "--repository",
            "ozaneryavuz/chatgpt",
            "--commit",
            "release-transparency-v150-test",
        ])

        status_path = target / "release-status.json"
        page_path = target / "yayin-durumu/index.html"
        assert status_path.is_file()
        assert page_path.is_file()
        status = json.loads(status_path.read_text(encoding="utf-8"))
        page = page_path.read_text(encoding="utf-8")
        pages_release = json.loads((target / "pages-release.json").read_text(encoding="utf-8"))

        assert status["status"] == "ready"
        assert status["commit"] == "release-transparency-v150-test"
        assert status["routingVersion"] >= 150
        assert status["routeCount"] == canonical_release["routeCount"]
        assert status["articleCount"] == len(article_routes)
        assert status["deviceDamageDeadline"] == "30 gün"
        assert status["allCriticalRoutesPresent"] is True
        assert status["verifiedCriticalRouteCount"] >= 7
        assert all(item["present"] for item in status["criticalRoutes"])
        expected_json_path = f"{base_path}/release-status.json" if base_path else "/release-status.json"
        expected_page_path = f"{base_path}/yayin-durumu/" if base_path else "/yayin-durumu/"
        assert status["artifactStatusPath"] == expected_json_path
        assert status["artifactStatusPagePath"] == expected_page_path
        assert "release-transparency-v150-test"[:12] in page
        assert "Yayın paketi hazır ve kritik rotalar doğrulandı" in page
        assert expected_json_path in page
        assert "Dataset" in page and "FAQPage" in page and "BreadcrumbList" in page

        trust_count = 0
        for route in article_routes:
            article = target / route["canonicalPath"].strip("/") / "index.html"
            text = article.read_text(encoding="utf-8")
            assert text.count(TRUST_MARKER) == 1, route["canonicalPath"]
            assert text.count(TRUST_JSONLD_MARKER) == 1, route["canonicalPath"]
            assert expected_page_path in text, route["canonicalPath"]
            assert "Hata veya düzeltme bildir" in text, route["canonicalPath"]
            trust_count += 1

        assert (target / "assets/alo186-editorial-trust.css").is_file()
        assert pages_release["editorialTrustV1"]["articleCount"] == len(article_routes)
        assert pages_release["editorialTrustV1"]["trustBlocksInjected"] == trust_count
        assert pages_release["editorialTrustV1"]["namedIndividualClaimed"] is False
        assert pages_release["releaseTransparencyV1"]["route"] == expected_page_path
        assert pages_release["releaseTransparencyV1"]["json"] == expected_json_path
        assert pages_release["releaseTransparencyV1"]["allCriticalRoutesPresent"] is True
        results.append({
            "target": label,
            "routeCount": status["routeCount"],
            "articleCount": status["articleCount"],
            "trustBlocks": trust_count,
            "criticalRoutes": status["verifiedCriticalRouteCount"],
        })

print(json.dumps({
    "ok": True,
    "routingVersion": 150,
    "releaseStatusJson": True,
    "articleEditorialTrust": True,
    "liveSmokeWorkflow": True,
    "targets": results,
}, ensure_ascii=False))
