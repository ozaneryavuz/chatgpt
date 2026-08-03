from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEPLOYMENT = ROOT / "alo186/deployment"
sys.path.insert(0, str(DEPLOYMENT))

import build_static_site  # noqa: E402
import build_static_site_core  # noqa: E402
import materialize_location_pages_v253  # noqa: E402
import sitemap_hreflang  # noqa: E402

SITEMAP_NS = {
    "sm": sitemap_hreflang.SITEMAP_NAMESPACE,
    "xhtml": sitemap_hreflang.XHTML_NAMESPACE,
}


def sitemap_records(path: Path) -> dict[str, list[tuple[str, str]]]:
    root = ET.parse(path).getroot()
    records: dict[str, list[tuple[str, str]]] = {}
    for url in root.findall("sm:url", SITEMAP_NS):
        loc = url.findtext("sm:loc", namespaces=SITEMAP_NS)
        assert loc
        records[loc] = [
            (link.attrib["hreflang"], link.attrib["href"])
            for link in url.findall("xhtml:link", SITEMAP_NS)
        ]
    return records


def expect_failure(callback, fragment: str) -> None:
    try:
        callback()
    except ValueError as exc:
        assert fragment.casefold() in str(exc).casefold(), (fragment, str(exc))
    else:
        raise AssertionError(f"Beklenen ValueError oluşmadı: {fragment}")


def main() -> None:
    manifest = build_static_site.load_effective_manifest(ROOT)
    payload = json.loads(
        (DEPLOYMENT / "language-alternates.json").read_text(encoding="utf-8")
    )
    pairs = sitemap_hreflang.validate_language_alternates(payload, manifest)
    assert len(pairs) == 10
    assert (
        build_static_site.write_effective_sitemap
        is sitemap_hreflang.write_effective_sitemap
    )
    assert (
        build_static_site_core.write_effective_sitemap
        is sitemap_hreflang.write_effective_sitemap
    )

    canonical_host = manifest["canonicalHost"].rstrip("/")
    expected_routes = {route["canonicalPath"] for route in manifest["routes"]}
    expected_manifest_urls = {canonical_host + route for route in expected_routes}
    provinces, companies = materialize_location_pages_v253.load_catalog(ROOT)
    expected_location_urls = {
        canonical_host + f"/il/{materialize_location_pages_v253.normalize_slug(city)}"
        for city in provinces.values()
    }
    expected_location_urls.update(
        canonical_host + f"/dagitim-sirketleri/{company.slug}"
        for company in companies
    )
    expected_final_urls = expected_manifest_urls | expected_location_urls

    with tempfile.TemporaryDirectory(prefix="alo186-hreflang-") as directory:
        output = Path(directory) / "site"
        subprocess.run(
            [
                sys.executable,
                str(DEPLOYMENT / "build_static_site.py"),
                "--repo-root",
                str(ROOT),
                "--output",
                str(output),
                "--commit",
                "sitemap-hreflang-test",
            ],
            check=True,
            cwd=ROOT,
        )
        sitemap = output / "sitemap.xml"
        text = sitemap.read_text(encoding="utf-8")
        assert 'xmlns:xhtml="http://www.w3.org/1999/xhtml"' in text
        records = sitemap_records(sitemap)
        assert set(records) == expected_final_urls
        assert len(records) == len(expected_routes) + 102

        for pair in pairs:
            turkish_url = canonical_host + pair["turkishPath"]
            english_url = canonical_host + pair["englishPath"]
            expected_links = [
                ("tr-TR", turkish_url),
                ("en", english_url),
                ("x-default", turkish_url),
            ]
            assert records[turkish_url] == expected_links, turkish_url
            assert records[english_url] == expected_links, english_url

        linked_urls = {loc for loc, links in records.items() if links}
        assert len(linked_urls) == 20
        assert sum(len(links) for links in records.values()) == 60
        assert all(not records[url] for url in expected_location_urls)

    duplicate = copy.deepcopy(payload)
    duplicate["pairs"][1]["englishPath"] = duplicate["pairs"][0]["englishPath"]
    expect_failure(
        lambda: sitemap_hreflang.validate_language_alternates(duplicate, manifest),
        "Yinelenen İngilizce",
    )

    missing = copy.deepcopy(payload)
    missing["pairs"][0]["englishPath"] = "/en/not-a-real-route/"
    expect_failure(
        lambda: sitemap_hreflang.validate_language_alternates(missing, manifest),
        "routing manifestte bulunmuyor",
    )

    wrong_default = copy.deepcopy(payload)
    wrong_default["pairs"][0]["xDefaultPath"] = "/en/"
    expect_failure(
        lambda: sitemap_hreflang.validate_language_alternates(wrong_default, manifest),
        "x-default",
    )

    print(
        json.dumps(
            {
                "ok": True,
                "languagePairs": len(pairs),
                "linkedUrls": 20,
                "alternateLinks": 60,
                "canonicalHost": canonical_host,
                "generatedLocationUrls": len(expected_location_urls),
                "finalSitemapUrls": len(expected_final_urls),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
