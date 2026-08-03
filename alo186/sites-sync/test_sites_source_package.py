#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
MODULE_PATH = HERE / "build_sites_source_package.py"


def load_module():
    spec = importlib.util.spec_from_file_location("alo186_sites_source_package", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Sites package modülü yüklenemedi")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")


def html_page(*, affiliate: bool = False) -> str:
    link = ""
    if affiliate:
        link = (
            '<a href="https://www.amazon.com.tr/s?k=mini+ups&tag=alo186rehber-21" '
            'rel="sponsored nofollow noopener">Amazon Türkiye</a>'
        )
    return (
        '<!doctype html><html lang="tr"><head>'
        '<title>Test</title><link rel="canonical" href="https://alo186.com/test">'
        '</head><body><h1>Test</h1>'
        'ALO186 bağımsız bilgilendirme platformudur; EDAŞ veya kamu kurumu değildir.'
        f'{link}</body></html>'
    )


def main() -> None:
    module = load_module()
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        repo = root / "repo"
        bundle = root / "bundle"
        out = root / "out"

        write(
            repo / "alo186/sites-sync/sites-source-manifest.json",
            (HERE / "sites-source-manifest.json").read_text(encoding="utf-8"),
        )
        write(
            repo / "alo186/sites-sync/sites-import-prompt.md",
            (HERE / "sites-import-prompt.md").read_text(encoding="utf-8"),
        )
        write(
            repo / "alo186/sites-sync/README.md",
            (HERE / "README.md").read_text(encoding="utf-8"),
        )
        routing = {
            "version": 1,
            "canonicalHost": "https://alo186.com",
            "routes": [
                {"source": "alo186/index.html", "canonicalPath": "/elektrik-portali", "type": "collection"},
                {"source": "alo186/turkiye-arama/index.html", "canonicalPath": "/edas-bul", "type": "tool"},
                {"source": "alo186/karar-motoru/index.html", "canonicalPath": "/karar-motoru", "type": "tool"},
                {"source": "alo186/hesaplama/index.html", "canonicalPath": "/hesaplama/", "type": "collection"},
                {"source": "alo186/hesaplama/demo/index.html", "canonicalPath": "/hesaplama/demo/", "type": "tool"},
            ],
        }
        write(
            repo / "alo186/deployment/routing-manifest.json",
            json.dumps(routing, ensure_ascii=False),
        )
        write(repo / "alo186/turkiye-arama/companies.js", "const provinceNames={}; const companies=[];")
        write(repo / "alo186/ai-cms/policy.json", '{"minimumQualityScore":85}')
        write(repo / "alo186/robots.txt", "User-agent: *\nAllow: /\n")
        write(repo / "alo186/sitemap.xml", "<urlset></urlset>")
        write(
            repo / "alo186/ai-cms/content/published-demo.json",
            json.dumps({"slug": "published-demo", "state": "published"}, ensure_ascii=False),
        )
        write(
            repo / "alo186/ai-cms/content/review-demo.json",
            json.dumps({"slug": "review-demo", "state": "review"}, ensure_ascii=False),
        )

        write(bundle / "index.html", html_page())
        for route in ("elektrik-portali", "edas-bul", "karar-motoru", "hesaplama", "hesaplama/demo"):
            write(bundle / route / "index.html", html_page())
        write(bundle / "hesaplama/demo/app.js", "console.log('ok');")
        write(bundle / "hesaplama/demo/test.js", "throw new Error('must not copy');")
        write(bundle / "amazon-elektrik-urunleri/demo/index.html", html_page(affiliate=True))
        write(bundle / "robots.txt", "User-agent: *\nAllow: /\n")
        write(bundle / "sitemap.xml", "<urlset></urlset>")

        province_slugs = ["mugla"] + [f"province-{index:02d}" for index in range(1, 81)]
        company_slugs = ["adm-elektrik"] + [f"company-{index:02d}" for index in range(1, 21)]
        for slug in province_slugs:
            write(bundle / "il" / slug / "index.html", html_page())
        for slug in company_slugs:
            write(bundle / "dagitim-sirketleri" / slug / "index.html", html_page())

        result = module.build(
            repo=repo,
            bundle=bundle,
            out=out,
            source_commit="1ebb04fdfbf85d99ae2f9b770cff8d58b7a9936c",
        )
        inventory = json.loads((out / "route-inventory.json").read_text(encoding="utf-8"))
        proof = json.loads((out / "source-integrity.json").read_text(encoding="utf-8"))

        assert result["ok"] is True
        assert result["provincePages"] == 81
        assert result["distributionCompanyPages"] == 21
        assert result["publishedAiCmsRecords"] == 1
        assert result["amazonTurkeyLinks"] == 1
        assert inventory["affiliateValidation"]["invalidRelLinks"] == 0
        assert inventory["affiliateValidation"]["locationAffiliateLinks"] == 0
        assert (out / "public/hesaplama/demo/app.js").is_file()
        assert not (out / "public/hesaplama/demo/test.js").exists()
        assert (out / "metadata/alo186/deployment/routing-manifest.json").is_file()
        assert (out / "metadata/ai-cms/content/published-demo.json").is_file()
        assert not (out / "metadata/ai-cms/content/review-demo.json").exists()
        assert proof["fileCount"] > 100
        print(json.dumps({
            "ok": True,
            "provincePages": result["provincePages"],
            "companyPages": result["distributionCompanyPages"],
            "publishedAiCmsRecords": result["publishedAiCmsRecords"],
            "affiliateRelGuard": True,
            "internalTestFileExcluded": True,
        }, ensure_ascii=False))


if __name__ == "__main__":
    main()
