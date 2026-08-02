#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

TOOL_DIR = Path(__file__).resolve().parents[1]
MODULE_PATH = TOOL_DIR / "cms.py"
if str(TOOL_DIR) not in sys.path:
    sys.path.insert(0, str(TOOL_DIR))

import core
import inventory as cms_inventory
import planning
import validation


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def page(route: str, title: str, h1: str | None = None) -> str:
    canonical = "https://alo186.com" + (route if route.startswith("/") else "/" + route)
    return f'''<!doctype html><html lang="tr"><head><meta charset="utf-8"><title>{title}</title><meta name="description" content="{title} için kullanıcıya somut sonuç sağlayan açıklama."><link rel="canonical" href="{canonical}"><script type="application/ld+json">{{"@context":"https://schema.org","@type":["WebPage","FAQPage"]}}</script></head><body><main><h1>{h1 or title}</h1></main></body></html>'''


def fixture_repo(root: Path) -> None:
    routes = {
        "/": ("ALO186", "ALO186 elektrik bilgi ağı"),
        "/elektrik-portali": ("Elektrik Portalı", "Elektrik Portalı"),
        "/hesaplama": ("Hesaplama Merkezi", "Elektrik Hesaplama Merkezi"),
        "/karar-motoru": ("Karar Motoru", "Elektrik sorununu sınıflandır"),
        "/edas-bul": ("EDAŞ Bul", "Dağıtım şirketini bul"),
        "/hesaplama/yedek-guc": ("Yedek Güç Hesabı", "Yedek güç kapasitesini hesapla"),
        "/kurumsal-elektrik-surekliligi-on-degerlendirme": ("Kurumsal Ön Değerlendirme", "Elektrik sürekliliği ön değerlendirmesi"),
        "/haberler/mevcut-ups-rehberi": ("UPS bakım bypass rehberi", "UPS bakım bypass ve statik bypass farkı"),
    }
    for route, values in routes.items():
        target = core.route_to_source(root, route)
        write(target, page(route, values[0], values[1]))
    manifest = {
        "version": 1,
        "routes": [
            {"canonicalPath": route, "source": core.route_to_source(root, route).relative_to(root).as_posix(), "type": "page"}
            for route in routes
        ],
    }
    write(root / "alo186/deployment/routing-manifest.json", json.dumps(manifest, ensure_ascii=False))


def valid_item(item_id: str, route: str, cluster: str, score: int = 90) -> dict:
    return {
        "id": item_id,
        "status": "ready",
        "topic": "ups",
        "cluster": cluster,
        "contentType": "tool",
        "title": f"{item_id.replace('-', ' ').title()} karar ve kanıt aracı",
        "task": f"{item_id} konusunda kullanıcı belirtileri güvenli biçimde sınıflandırıp ölçülebilir kanıt listesini ve doğru sonraki adımı oluşturmak için özgün bir görev akışı kurar.",
        "intentBoundary": f"{item_id} mevcut genel rehberleri veya ürün karşılaştırmalarını tekrar etmez; yalnız bu yeni kullanıcı görevinin sonucu, kanıt dosyası ve kabul sınırına odaklanır.",
        "proposedRoute": route,
        "supportingOf": None,
        "audience": "Ev ve işletme kullanıcıları",
        "scores": {
            "searchDemand": score,
            "taskUrgency": score,
            "taskCompletionValue": score,
            "authorityFit": score,
            "contentGap": score,
            "commercialFit": score,
            "internalLinkFit": score,
            "sourceConfidence": score,
        },
        "sources": [
            {"url": f"https://iec.example/{item_id}/1", "publisher": "IEC", "class": "standard", "primary": True, "verifiedAt": "2026-08-02", "claims": ["teknik gereklilik"]},
            {"url": f"https://manufacturer.example/{item_id}/2", "publisher": "Üretici", "class": "manufacturer", "primary": True, "verifiedAt": "2026-08-02", "claims": ["ürün kabul sınırı"]},
            {"url": f"https://research.example/{item_id}/3", "publisher": "Araştırma", "class": "research", "primary": False, "verifiedAt": "2026-08-02", "claims": ["ek kanıt"]},
        ],
        "internalLinks": [
            "/elektrik-portali",
            "/hesaplama",
            "/karar-motoru",
            "/edas-bul",
            "/hesaplama/yedek-guc",
            "/kurumsal-elektrik-surekliligi-on-degerlendirme",
        ],
        "schemaTypes": ["WebApplication", "FAQPage", "BreadcrumbList"],
        "conversion": {
            "primaryCta": "Sonuç planını oluştur",
            "secondaryCta": "Teknik kapsamı gör",
            "events": [item_id.replace("-", "_") + "_result"],
            "affiliateAllowed": False,
        },
        "safetyBoundary": "Enerjili pano ve sabit tesisata kullanıcı müdahalesi önerilmez; riskte enerji kesilir ve yetkin teknik destek kullanılır.",
        "draft": None,
    }


def load_config() -> dict:
    return json.loads((TOOL_DIR / "config.json").read_text(encoding="utf-8"))


def audit(root: Path, items: list[dict]) -> tuple[list[core.Finding], list[dict], list[core.InventoryItem]]:
    config = load_config()
    inventory, inventory_findings = cms_inventory.build_inventory(root)
    queue = {"version": 220, "generatedAt": "2026-08-02", "items": items}
    findings, enriched = validation.validate_queue(queue, config, inventory, inventory_findings, date(2026, 8, 2))
    return findings, enriched, inventory


def test_empty_queue_and_inventory() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        fixture_repo(root)
        findings, items, inventory = audit(root, [])
        assert items == []
        assert inventory
        assert not [finding for finding in findings if finding.level == "error"], findings


def test_rank_top_three_with_cluster_diversity() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        fixture_repo(root)
        items = [
            valid_item("alpha-power-proof", "/hesaplama/alpha-power-proof/", "backup", 99),
            valid_item("beta-power-proof", "/hesaplama/beta-power-proof/", "backup", 98),
            valid_item("gamma-grid-proof", "/hesaplama/gamma-grid-proof/", "grid", 97),
            valid_item("delta-solar-proof", "/hesaplama/delta-solar-proof/", "solar", 96),
            valid_item("epsilon-ev-proof", "/hesaplama/epsilon-ev-proof/", "ev", 95),
        ]
        findings, enriched, _ = audit(root, items)
        errors = [finding for finding in findings if finding.level == "error"]
        assert not errors, errors
        selected = planning.rank_ready(enriched, findings, load_config(), 3)
        assert [item["id"] for item in selected] == ["alpha-power-proof", "gamma-grid-proof", "delta-solar-proof"]


def test_exact_route_collision_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        fixture_repo(root)
        item = valid_item("route-collision-proof", "/hesaplama/yedek-guc/", "backup")
        findings, _, _ = audit(root, [item])
        assert any(finding.code == "route_collision" for finding in findings)


def test_published_low_score_fails_closed() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        fixture_repo(root)
        item = valid_item("published-score-proof", "/haberler/mevcut-ups-rehberi/", "backup", 20)
        item["status"] = "published"
        findings, _, _ = audit(root, [item])
        assert any(finding.code == "score_below_publish_threshold" for finding in findings)


def test_array_schema_bypass_is_blocked() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        fixture_repo(root)
        item = valid_item("schema-array-proof", "/hesaplama/schema-array-proof/", "backup")
        item["status"] = "drafted"
        item["draft"] = {"jsonLd": {"@context": "https://schema.org", "@type": ["WebApplication", "Offer"]}}
        findings, _, _ = audit(root, [item])
        assert any(finding.code == "forbidden_schema_in_draft" and "Offer" in finding.detail for finding in findings)


def test_stale_source_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        fixture_repo(root)
        item = valid_item("stale-source-proof", "/hesaplama/stale-source-proof/", "backup")
        item["sources"][0]["verifiedAt"] = "2025-01-01"
        findings, _, _ = audit(root, [item])
        assert any(finding.code == "source_stale" for finding in findings)


def test_sites_package_never_auto_publishes() -> None:
    config = load_config()
    brief = {"contentId": "safe-package-proof", "route": "/hesaplama/safe-package-proof/", "draftSchema": "draft.schema.json"}
    package = planning.make_sites_package([brief], config, "abcdef1")
    assert package["reviewPolicy"]["automaticDeployAllowed"] is False
    assert package["reviewPolicy"]["humanPreviewRequired"] is True
    assert all(operation["publish"] is False for operation in package["operations"])
    assert package["siteSlug"] == "alo186"


def test_cli_plan_outputs_private_artifact() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "repo"
        root.mkdir()
        fixture_repo(root)
        queue = root / "queue.json"
        queue.write_text(json.dumps({"version": 220, "items": []}), encoding="utf-8")
        out = root / "private-output"
        command = [
            sys.executable,
            str(MODULE_PATH),
            "--repo", str(root),
            "--config", str(TOOL_DIR / "config.json"),
            "--queue", str(queue),
            "--today", "2026-08-02",
            "plan",
            "--out-dir", str(out),
            "--source-commit", "abcdef1",
        ]
        subprocess.run(command, check=True, capture_output=True, text=True)
        assert (out / "audit-report.json").is_file()
        assert (out / "sites-package.json").is_file()
        assert (out / "sites-publish-prompt.md").is_file()
        assert (out / "dashboard.html").is_file()
        package = json.loads((out / "sites-package.json").read_text(encoding="utf-8"))
        assert package["operations"] == []
        assert not str(out).startswith(str(root / "alo186"))


def main() -> None:
    tests = [
        test_empty_queue_and_inventory,
        test_rank_top_three_with_cluster_diversity,
        test_exact_route_collision_fails,
        test_published_low_score_fails_closed,
        test_array_schema_bypass_is_blocked,
        test_stale_source_fails,
        test_sites_package_never_auto_publishes,
        test_cli_plan_outputs_private_artifact,
    ]
    for test in tests:
        test()
    print(f"ALO186 AI CMS v220: {len(tests)} test PASS")


if __name__ == "__main__":
    main()
