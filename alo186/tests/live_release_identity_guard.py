from __future__ import annotations

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urljoin, urlsplit

import requests

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = ROOT / "alo186/deployment/live-domain-integration.json"
USER_AGENT = "ALO186-Live-Release-Identity-Guard/2.0 (+https://alo186.com)"


def get(session: requests.Session, url: str, *, redirects: bool = True) -> requests.Response:
    response = session.get(url, timeout=35, allow_redirects=redirects)
    return response


def fail(message: str, **evidence: object) -> None:
    payload = {"ok": False, "message": message, "evidence": evidence}
    print(json.dumps(payload, ensure_ascii=False, indent=2), file=sys.stderr)
    raise SystemExit(1)


def canonical_host_from_sitemap(xml_text: str) -> set[str]:
    root = ET.fromstring(xml_text)
    return {
        f"{urlsplit(node.text.strip()).scheme}://{urlsplit(node.text.strip()).netloc}"
        for node in root.findall(".//{*}loc")
        if node.text and node.text.strip()
    }


def run(manifest_path: Path) -> dict:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    serving_origin = manifest["productionOrigin"].rstrip("/")
    canonical_origin = manifest["canonicalOrigin"].rstrip("/")
    apex_origin = manifest["apexOrigin"].rstrip("/")
    www_origin = manifest["wwwOrigin"].rstrip("/")
    minimum_route_count = int(manifest["minimumReleaseRouteCount"])
    required_routes = list(dict.fromkeys(manifest["requiredRoutes"]))

    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT, "Accept-Language": "tr-TR,tr;q=0.9"})

    origin_results: dict[str, dict[str, object]] = {}
    for origin in (apex_origin, www_origin):
        response = get(session, origin + "/")
        origin_results[origin] = {
            "status": response.status_code,
            "finalUrl": response.url,
            "redirects": len(response.history),
            "chain": [{"status": item.status_code, "url": item.url, "location": item.headers.get("location")} for item in response.history],
        }
        if response.status_code != 200:
            fail("Canlı origin 200 ile sonuçlanmadı.", origin=origin, result=origin_results[origin])

    final_origins = {
        f"{urlsplit(item['finalUrl']).scheme}://{urlsplit(item['finalUrl']).netloc}"
        for item in origin_results.values()
    }
    if final_origins != {serving_origin}:
        fail("Apex ve www tek canlı serving origin üzerinde birleşmiyor.", expected=serving_origin, actual=sorted(final_origins), results=origin_results)
    if serving_origin != canonical_origin:
        fail(
            "Canlı serving origin ile build canonical origin ayrışmış durumda; indeks sinyalleri ve yayın kimliği iki hosta bölünüyor.",
            servingOrigin=serving_origin,
            canonicalOrigin=canonical_origin,
            remediation="DNS/GitHub Pages custom domain tek hostta birleştirilmeli; ardından canonical, sitemap ve redirects aynı origin kullanmalı.",
        )

    release_url = urljoin(serving_origin + "/", "pages-release.json")
    release_response = get(session, release_url)
    if release_response.status_code != 200:
        fail("Canlı alan adı güncel Pages yayın kimliği dosyasını sunmuyor.", url=release_url, status=release_response.status_code, finalUrl=release_response.url)
    try:
        release = release_response.json()
    except ValueError as exc:
        fail("pages-release.json geçerli JSON değil.", url=release_url, error=str(exc), sample=release_response.text[:500])
    if int(release.get("routeCount") or 0) < minimum_route_count:
        fail("Canlı yayın routeCount güncel build eşiğinin altında.", expectedMinimum=minimum_route_count, actual=release.get("routeCount"), release=release)
    if release.get("deviceDamageDeadline") != "10 iş günü" or release.get("rootDeviceDamageDeadline") != "10 iş günü":
        fail("Canlı yayın kimliği cihaz hasarı için güncel 10 iş günü korumasını taşımıyor.", release=release)
    if str(release.get("canonicalHost", "")).rstrip("/") != canonical_origin:
        fail("Canlı yayın kimliğindeki canonicalHost manifestle uyuşmuyor.", expected=canonical_origin, actual=release.get("canonicalHost"))

    route_results: list[dict[str, object]] = []
    for route in required_routes:
        url = urljoin(serving_origin + "/", route.lstrip("/"))
        response = get(session, url)
        record = {"route": route, "status": response.status_code, "finalUrl": response.url, "redirects": len(response.history)}
        route_results.append(record)
        if response.status_code != 200:
            fail("Zorunlu canlı rota 200 döndürmüyor.", result=record)

    portal_url = urljoin(serving_origin + "/", "elektrik-portali")
    portal = get(session, portal_url).text
    if re.search(r"cihaz.{0,120}\b30\s*(?:takvim\s*)?gün\b", portal, re.IGNORECASE | re.DOTALL):
        fail("Canlı portal cihaz hasarı için eski 30 gün ifadesini yayımlıyor.", url=portal_url)
    if "10 iş günü" not in portal.casefold():
        fail("Canlı portal görünür 10 iş günü uyarısını taşımıyor.", url=portal_url)

    home = get(session, serving_origin + "/").text.casefold()
    if "bağımsız" not in home or "kamu kurumu değildir" not in home:
        fail("Canlı ana sayfada bağımsızlık ve resmî kurum olmadığı açıklaması birlikte görünmüyor.", url=serving_origin + "/")

    sitemap_url = urljoin(serving_origin + "/", "sitemap.xml")
    sitemap_response = get(session, sitemap_url)
    if sitemap_response.status_code != 200:
        fail("Canlı sitemap.xml alınamadı.", status=sitemap_response.status_code, url=sitemap_url)
    try:
        sitemap_origins = canonical_host_from_sitemap(sitemap_response.text)
    except Exception as exc:  # noqa: BLE001
        fail("Canlı sitemap.xml ayrıştırılamadı.", url=sitemap_url, error=str(exc))
    if sitemap_origins != {canonical_origin}:
        fail("Sitemap URL hostu canonical origin ile uyuşmuyor.", expected=canonical_origin, actual=sorted(sitemap_origins))

    robots_url = urljoin(serving_origin + "/", "robots.txt")
    robots_response = get(session, robots_url)
    if robots_response.status_code != 200:
        fail("Canlı robots.txt alınamadı.", status=robots_response.status_code, url=robots_url)
    sitemap_refs = re.findall(r"(?im)^\s*sitemap\s*:\s*(\S+)", robots_response.text)
    if sitemap_url not in sitemap_refs and urljoin(canonical_origin + "/", "sitemap.xml") not in sitemap_refs:
        fail("robots.txt güncel sitemap konumunu bildirmiyor.", robots=robots_response.text[:2000], expected=[sitemap_url, urljoin(canonical_origin + "/", "sitemap.xml")])

    result = {
        "ok": True,
        "version": manifest["version"],
        "servingOrigin": serving_origin,
        "canonicalOrigin": canonical_origin,
        "releaseRouteCount": release.get("routeCount"),
        "deviceDamageDeadline": release.get("deviceDamageDeadline"),
        "requiredRoutes": route_results,
        "originResults": origin_results,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="ALO186 canlı release identity ve domain birleşimi kabul kapısı")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    args = parser.parse_args()
    run(args.manifest.resolve())


if __name__ == "__main__":
    main()
