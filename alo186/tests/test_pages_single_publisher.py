from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = ROOT / ".github/workflows"
STANDARD = WORKFLOWS / "alo186-github-pages.yml"
BOOTSTRAP = WORKFLOWS / "alo186-pages-autobootstrap-live.yml"
DEPLOYMENT = ROOT / "alo186/deployment"
sys.path.insert(0, str(DEPLOYMENT))

import inject_live_quality_v218_compat as live_quality  # noqa: E402


def validate_origin_normalization() -> dict[str, object]:
    with tempfile.TemporaryDirectory(prefix="alo186-origin-normalization-") as folder:
        site = Path(folder)
        plan = site / "elektrik-planim/index.html"
        kit = site / "urun-rehberleri/elektrik-kesintisi-kiti/index.html"
        plan.parent.mkdir(parents=True)
        kit.parent.mkdir(parents=True)

        plan.write_text(
            '''<!doctype html><html lang="tr"><head>
            <link rel="canonical" href="https://www.alo186.com/elektrik-planim">
            <link rel="alternate" hreflang="tr-TR" href="https://www.alo186.com/elektrik-planim">
            <meta property="og:url" content="http://www.alo186.com/elektrik-planim">
            </head><body><main id="main-content"><h1>Plan</h1></main></body></html>''',
            encoding="utf-8",
        )
        kit.write_text(
            '''<!doctype html><html lang="tr"><head>
            <link rel="canonical" href="https://www.alo186.com/urun-rehberleri/elektrik-kesintisi-kiti">
            </head><body><main id="main-content"><h1>Kit</h1></main></body></html>''',
            encoding="utf-8",
        )
        (site / "sitemap.xml").write_text(
            '''<?xml version="1.0" encoding="UTF-8"?>
            <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
              <url><loc>https://www.alo186.com/elektrik-planim</loc></url>
              <url><loc>http://www.alo186.com/urun-rehberleri/elektrik-kesintisi-kiti</loc></url>
            </urlset>''',
            encoding="utf-8",
        )
        (site / "robots.txt").write_text(
            "User-agent: *\nSitemap: https://www.alo186.com/sitemap.xml\n",
            encoding="utf-8",
        )
        asset = site / "assets/reference.js"
        asset.parent.mkdir(parents=True)
        asset.write_text(
            'const documentationExample = "https://www.alo186.com/example";\n',
            encoding="utf-8",
        )

        first = live_quality.normalize_canonical_origin(site)
        assert first["filesChanged"] == 4, first
        assert first["replacementCount"] == 7, first
        assert sorted(first["changedFiles"]) == [
            "elektrik-planim/index.html",
            "robots.txt",
            "sitemap.xml",
            "urun-rehberleri/elektrik-kesintisi-kiti/index.html",
        ]

        for path in (plan, kit, site / "sitemap.xml", site / "robots.txt"):
            text = path.read_text(encoding="utf-8")
            assert "https://www.alo186.com" not in text
            assert "http://www.alo186.com" not in text
            assert "https://alo186.com" in text

        assert "https://www.alo186.com/example" in asset.read_text(
            encoding="utf-8"
        )

        second = live_quality.normalize_canonical_origin(site)
        assert second["filesChanged"] == 0, second
        assert second["replacementCount"] == 0, second
        return first


def main() -> None:
    publishers: list[str] = []
    for path in sorted(WORKFLOWS.glob("*.y*ml")):
        if path.name.startswith("alo186-one-shot-"):
            continue
        text = path.read_text(encoding="utf-8")
        if "actions/deploy-pages@" in text:
            publishers.append(path.name)

    assert publishers == ["alo186-github-pages.yml"], publishers

    standard = STANDARD.read_text(encoding="utf-8")
    assert standard.count("actions/deploy-pages@") == 1
    assert "alo186-pages-production" in standard
    assert "alo186-pages-pr-{0}" in standard
    assert "cancel-in-progress: false" in standard
    assert "python alo186/tests/test_pages_single_publisher.py" in standard
    assert "Pages deployment ve canlı origin yetkisini ayrıştır" in standard
    assert "verify_live_origin.py" in standard
    assert "containsExpectedCommit" not in standard
    assert "hosting_mode" in standard
    assert "if [ \"$hosting_mode\" = 'github-pages' ]" in standard
    assert "verify_contextual_affiliate_live_v177.py" in standard
    assert "deferred-external-live-authority" in standard
    assert "alo186-full-live-receipt" in standard
    assert "--attempts 36" not in standard

    bootstrap = BOOTSTRAP.read_text(encoding="utf-8")
    assert "actions/deploy-pages@" not in bootstrap
    assert "actions: write" in bootstrap
    assert "deployments: read" in bootstrap
    assert "group: alo186-pages-production" in bootstrap
    assert "cancel-in-progress: false" in bootstrap
    assert "containsExpectedCommit" in bootstrap
    assert "exactCommitReceiptAvailable" in bootstrap
    assert "origin_probe_ok" in bootstrap
    assert "steps.origin_state.outputs.origin_probe_ok == 'true'" in bootstrap
    assert "pages_deployment_succeeded" in bootstrap
    assert "listDeployments" in bootstrap
    assert "listDeploymentStatuses" in bootstrap
    assert "waiting_for_dns_cutover:" in bootstrap
    assert "origin_probe_failed:" in bootstrap
    assert "alo186-dns-cutover-required" in bootstrap
    assert "Otomatik Pages yeniden-dispatch: **durduruldu**" in bootstrap
    assert "dispatch_pages:" in bootstrap
    assert "needs.probe.outputs.hosting_mode == 'github-pages'" in bootstrap
    assert "needs.probe.outputs.pages_deployment_succeeded != 'true'" in bootstrap
    assert "needs.probe.outputs.pages_deployment_succeeded == 'true'" in bootstrap
    assert "workflow_id: 'alo186-github-pages.yml'" in bootstrap
    assert "ref: 'main'" in bootstrap
    assert "first Pages artifact" in bootstrap or "İlk Pages artifact" in bootstrap

    normalization = validate_origin_normalization()

    print(
        json.dumps(
            {
                "ok": True,
                "publisherCount": len(publishers),
                "publisher": publishers[0],
                "sharedProductionConcurrency": "alo186-pages-production",
                "bootstrapRole": "probe-state-machine-and-dispatch",
                "externalDnsRedispatchLoopClosed": True,
                "hostingAuthorityReceiptRequired": True,
                "firstPagesArtifactDeadlockClosed": True,
                "invalidOriginCannotMarkSitesCurrent": True,
                "lateGeneratedCanonicalOriginNormalized": True,
                "originNormalizationReplacementCount": normalization[
                    "replacementCount"
                ],
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
