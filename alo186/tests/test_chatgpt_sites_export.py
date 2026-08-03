from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEPLOYMENT = ROOT / "alo186/deployment"
sys.path.insert(0, str(DEPLOYMENT))

from export_chatgpt_sites_bundle_v2 import export_bundle  # noqa: E402


def main() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        output = Path(temporary) / "alo186-chatgpt-sites"
        manifest = export_bundle(output, "test-commit")

        assert manifest["targetPlatform"] == "ChatGPT Sites"
        assert manifest["targetSourceOfTruth"] == "chatgpt-sites"
        assert manifest["canonicalHost"] == "https://alo186.com"
        assert manifest["sourceCommit"] == "test-commit"
        assert manifest["exporterVersion"] == 2

        stats = manifest["stats"]
        assert stats["effectiveRoutes"] >= 100, stats
        assert stats["importReady"] >= 50, stats
        assert stats["provincePages"] >= 81, stats
        assert stats["companyPages"] >= 21, stats
        assert stats["interactiveTools"] >= 10, stats
        assert stats["technicalArticles"] >= 10, stats
        assert stats["redirectCount"] >= 1, stats

        ready = manifest["pages"]
        ready_paths = {item["canonicalPath"] for item in ready}
        for required in ("/elektrik-portali", "/edas-bul", "/hesaplama/"):
            assert required in ready_paths, required

        aliases_payload = json.loads((DEPLOYMENT / "content-consolidations.json").read_text(encoding="utf-8"))
        aliases = {item["aliasPath"] for item in aliases_payload["consolidations"]}
        assert not aliases.intersection(ready_paths)

        policy = json.loads((DEPLOYMENT / "chatgpt-sites-export-policy.json").read_text(encoding="utf-8"))
        patterns = [str(item).casefold() for item in policy["reviewOnlyRoutePatterns"]]
        for item in ready:
            path = item["canonicalPath"].casefold()
            assert not any(pattern in path for pattern in patterns), item["canonicalPath"]
            assert item["title"]
            assert item["description"]
            assert item["h1"]
            assert item["sourceCopy"].startswith("source/")
            assert (output / item["sourceCopy"]).is_file()
            affiliate = item["affiliate"]
            if affiliate["hasAffiliateLinks"]:
                assert affiliate["safe"], item["canonicalPath"]
                assert affiliate["disclosureVisible"], item["canonicalPath"]
                assert affiliate["noBuyOutcomeVisible"], item["canonicalPath"]
                assert not affiliate["unsafeStaticLinks"], item["canonicalPath"]

        for path in output.rglob("*"):
            relative_parts = set(path.relative_to(output).parts)
            assert not ({"deployment", "tests", "audits", ".github"} & relative_parts)

        for required_file in (
            "sites-import.json",
            "SITE_BRIEF.md",
            "IMPORT_ORDER.md",
            "data/navigation.json",
            "data/location-services.json",
            "data/redirects.json",
            "review/review-index.json",
            "checksums.sha256",
        ):
            assert (output / required_file).is_file(), required_file

        locations = json.loads((output / "data/location-services.json").read_text(encoding="utf-8"))
        province_records = [item for item in locations if item["category"] == "location-province"]
        company_records = [item for item in locations if item["category"] == "location-company"]
        assert len(province_records) == 81
        assert len(company_records) == 21
        assert all(any("Service" in json.dumps(block, ensure_ascii=False) for block in item["jsonLd"]) for item in locations)
        assert all("amazon.com.tr" not in json.dumps(item, ensure_ascii=False).casefold() for item in locations)

        brief = (output / "SITE_BRIEF.md").read_text(encoding="utf-8")
        for token in (
            "ChatGPT Sites",
            "tek kaynak sistemidir",
            "Amazon Türkiye",
            "yeni ürün almayın",
            "kamu kurumu değildir",
        ):
            assert token in brief, token

        print(json.dumps({"ok": True, "stats": stats}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
