from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEPLOYMENT = ROOT / "alo186/deployment"
sys.path.insert(0, str(DEPLOYMENT))
import inject_contextual_affiliate_v176 as contextual  # noqa: E402

WORK = Path("/tmp/alo186-contextual-affiliate-v176")
CANONICAL = WORK / "canonical"
ROUTE = "/amazon-elektrik-urunleri/konuya-gore-urun-haritasi/"


def run(*args: str, stdout: Path | None = None) -> None:
    command = [sys.executable, *args]
    print("+", " ".join(command), flush=True)
    if stdout:
        with stdout.open("w", encoding="utf-8") as handle:
            subprocess.run(command, cwd=ROOT, check=True, stdout=handle)
    else:
        subprocess.run(command, cwd=ROOT, check=True)


def verify(site: Path, base_path: str) -> dict:
    release = json.loads((site / "alo186-release.json").read_text(encoding="utf-8"))
    metrics = release["contextualAffiliateV176"]
    assert metrics["catalogProductClassCount"] == 86
    assert metrics["groupCount"] == 13
    assert metrics["contextualPageCount"] >= 55
    assert metrics["contextualCardCount"] >= 165
    assert metrics["contextualCardCount"] <= metrics["contextualPageCount"] * 3
    assert metrics["uniqueProductsPlaced"] >= 65
    assert metrics["personalDataCollectionAdded"] is False
    assert metrics["officialInstitutionClaimed"] is False
    map_html = (site / ROUTE.strip("/") / "index.html").read_text(encoding="utf-8")
    assert contextual.MAP_MARKER in map_html
    assert map_html.count('data-product-card="true"') == 86
    assert map_html.count('data-affiliate-action="shop"') == 86
    assert map_html.count("alo186rehber-21") >= 86
    marker_pages = 0
    cards = 0
    for path in site.rglob("index.html"):
        html = path.read_text(encoding="utf-8", errors="ignore")
        if contextual.CONTEXT_MARKER not in html:
            continue
        marker_pages += 1
        count = html.count('data-product-card="true"')
        assert 1 <= count <= 3
        cards += count
        assert "satış ortaklığı" in html.casefold()
        assert "mevcut güvenli ürün yeterliyse yeni ürün almayın" in html.casefold()
    assert marker_pages == metrics["contextualPageCount"]
    assert cards == metrics["contextualCardCount"]
    second = contextual.run(site, base_path)
    assert second["mapChanged"] is False
    assert second["hubChanged"] is False
    return metrics


def main() -> None:
    if WORK.exists():
        shutil.rmtree(WORK)
    WORK.mkdir(parents=True)
    run("alo186/deployment/build_static_site.py", "--output", str(CANONICAL), "--commit", "contextual-v176-test")
    summaries = {}
    for name, base in (("custom", ""), ("project", "/chatgpt")):
        site = WORK / name
        shutil.copytree(CANONICAL, site)
        run("alo186/deployment/prepare_github_pages.py", "--site", str(site), "--base-path", base, "--repository", "ozaneryavuz/chatgpt", "--commit", "contextual-v176-test")
        run("alo186/deployment/inject_outcome_runtime.py", "--site", str(site), "--base-path", base)
        run("alo186/deployment/inject_shortlist_growth.py", "--site", str(site), "--base-path", base)
        run("alo186/deployment/inject_contextual_affiliate_v176.py", "--site", str(site), "--base-path", base, stdout=WORK / f"{name}-contextual.json")
        run("alo186/deployment/smoke_github_pages.py", "--site", str(site), "--base-path", base)
        run("alo186/deployment/guard_commerce_routes_v3.py", "--site", str(site), stdout=WORK / f"{name}-guard.json")
        guard = json.loads((WORK / f"{name}-guard.json").read_text(encoding="utf-8"))
        assert guard["ok"] is True and guard["errorCount"] == 0
        summaries[name] = verify(site, base)
    print(json.dumps({"ok": True, **summaries}, ensure_ascii=False))


if __name__ == "__main__":
    main()
