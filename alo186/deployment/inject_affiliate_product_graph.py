from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROUTE = "/urun-bilgi-grafigi/"
SOURCE = "alo186/urun-bilgi-grafigi/index.html"
GRAPH_FILE = Path("urun-bilgi-grafigi/product-graph.json")
BASE_EXTENSION = Path("akilli-urun-secimi/catalog-knowledge-extension.js")
SALES_EXTENSION = Path("akilli-urun-secimi/catalog-sales-extension.js")
GROWTH_EXTENSION = Path("akilli-urun-secimi/catalog-growth-run6.js")
GROWTH_RUN7_EXTENSION = Path("akilli-urun-secimi/catalog-growth-run7.js")
CAR_CHARGER_EXTENSION = Path("akilli-urun-secimi/catalog-car-charger-run54.js")
MARKER = 'data-alo186-product-graph-entry="true"'
SCRIPT_MARKER = 'data-alo186-product-graph-extension="true"'
REQUIRED = [
    Path("akilli-urun-secimi/catalog.js"),
    BASE_EXTENSION,
    SALES_EXTENSION,
    GROWTH_EXTENSION,
    GROWTH_RUN7_EXTENSION,
    CAR_CHARGER_EXTENSION,
    Path("urun-bilgi-grafigi/catalog.js"),
    Path("urun-bilgi-grafigi/catalog-knowledge-extension.js"),
    Path("urun-bilgi-grafigi/index.html"),
    Path("urun-bilgi-grafigi/app.js"),
    Path("urun-bilgi-grafigi/styles.css"),
]
TARGETS = [
    Path("amazon-elektrik-urunleri/index.html"),
    Path("akilli-urun-secimi/index.html"),
    Path("katalog-guven-durumu/index.html"),
    Path("elektrik-portali/index.html"),
]


def normalize_base_path(value: str) -> str:
    cleaned = str(value or "").strip()
    return "" if not cleaned or cleaned == "/" else "/" + cleaned.strip("/")


def public_url(base_path: str, route: str) -> str:
    return f"{base_path}/{route.lstrip('/')}" if base_path else "/" + route.lstrip("/")


def require_files(site: Path) -> None:
    missing = [str(path) for path in REQUIRED if not (site / path).is_file()]
    if missing:
        raise FileNotFoundError(f"Affiliate ürün grafiği bağımlılıkları eksik: {missing}")


def node_payload(site: Path) -> dict:
    require_files(site)
    core = site / "akilli-urun-secimi/catalog.js"
    base_extension = site / BASE_EXTENSION
    sales_extension = site / SALES_EXTENSION
    growth_extension = site / GROWTH_EXTENSION
    growth_run7_extension = site / GROWTH_RUN7_EXTENSION
    car_charger_extension = site / CAR_CHARGER_EXTENSION
    script = r"""
const catalog=require(process.argv[1]);
const graph=catalog.generateProductGraph();
const summary=catalog.knowledgeGraphSummary();
const schema=catalog.knowledgeGraph({now:new Date('2026-07-30T12:00:00Z')});
const out={
 graph:{
  version:graph.version,
  generatedAt:graph.generatedAt,
  canonicalUrl:graph.canonicalUrl,
  needs:graph.needs,
  categories:graph.categories,
  products:graph.products.map((product)=>({
   id:product.id,name:product.name,brand:product.brand,model:product.model,categoryId:product.categoryId,
   needIds:product.needIds||[],intentIds:product.intentIds||[],verificationStatus:product.verificationStatus,
   verifiedAt:product.verifiedAt,linkMode:product.linkMode,identifier:product.identifier,
   technicalProperties:product.technicalProperties,requiredEvidence:product.requiredEvidence||[],
   userNeed:product.userNeed||null,bestFor:product.bestFor||[],noBuyWhen:product.noBuyWhen||[],
   officialSource:product.officialSource,relatedTools:product.relatedTools||[],relatedGuides:product.relatedGuides||[],
   sourceNote:product.sourceNote
  }))
 },
 summary,
 schema
};
process.stdout.write(JSON.stringify(out));
"""
    result = subprocess.run(
        ["node", "-e", script, str(car_charger_extension)],
        cwd=site,
        check=True,
        text=True,
        capture_output=True,
    )
    payload = json.loads(result.stdout)
    graph = payload["graph"]
    summary = payload["summary"]
    schema = payload["schema"]
    if graph.get("canonicalUrl") != "https://www.alo186.com/urun-bilgi-grafigi/":
        raise RuntimeError("Affiliate ürün grafiği canonical sözleşmesi geçersiz")
    if summary.get("version") != "2026-07-30-v105":
        raise RuntimeError("Affiliate ürün grafiği v105 özet sözleşmesi geçersiz")
    if summary.get("productCount", 0) < 66 or summary.get("exactListingCount", 0) < 31:
        raise RuntimeError("Affiliate ürün grafiği v105 ürün kapsamı eksik")
    if not graph.get("needs") or not graph.get("categories") or not graph.get("products"):
        raise RuntimeError("Affiliate ürün grafiği boş üretildi")
    if not getattr(json, "dumps")(schema, ensure_ascii=False).startswith('{"@context":'):
        raise RuntimeError("Affiliate ürün JSON-LD üretilemedi")
    sources = [base_extension, sales_extension, growth_extension, growth_run7_extension, car_charger_extension]
    for source in sources:
        if not source.is_file():
            raise FileNotFoundError(source)
    return payload


def write_graph_and_schema(site: Path, payload: dict) -> None:
    graph_path = site / GRAPH_FILE
    graph_path.write_text(json.dumps(payload["graph"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    page = site / "urun-bilgi-grafigi/index.html"
    text = page.read_text(encoding="utf-8")
    pattern = re.compile(r'(<script id="affiliateProductGraphJsonLd" type="application/ld\+json">)(.*?)(</script>)', re.S)
    replacement = r"\1" + json.dumps(payload["schema"], ensure_ascii=False, separators=(",", ":")) + r"\3"
    text, count = pattern.subn(replacement, text, count=1)
    if count != 1:
        raise RuntimeError("Affiliate ürün JSON-LD hedef scripti bulunamadı")
    page.write_text(text, encoding="utf-8")


def inject_extension_scripts(site: Path, base_path: str) -> int:
    pages = [
        site / "urun-bilgi-grafigi/index.html",
        site / "akilli-urun-secimi/index.html",
        site / "amazon-elektrik-urunleri/index.html",
    ]
    sources = [
        (BASE_EXTENSION, "alo186-product-knowledge-base"),
        (SALES_EXTENSION, "alo186-product-knowledge-sales"),
        (GROWTH_EXTENSION, "alo186-product-knowledge-growth-run6"),
        (GROWTH_RUN7_EXTENSION, "alo186-product-knowledge-growth-run7"),
        (CAR_CHARGER_EXTENSION, "alo186-product-knowledge-v105"),
    ]
    count = 0
    for page in pages:
        if not page.is_file():
            continue
        text = page.read_text(encoding="utf-8")
        additions: list[str] = []
        for relative, marker_id in sources:
            if marker_id in text or f'src="{public_url(base_path, "/" + relative.as_posix())}"' in text:
                continue
            additions.append(
                f'<script id="{marker_id}" {SCRIPT_MARKER} '
                f'src="{public_url(base_path, "/" + relative.as_posix())}"></script>'
            )
        if additions and "</body>" in text:
            page.write_text(text.replace("</body>", "".join(additions) + "</body>", 1), encoding="utf-8")
            count += len(additions)
    return count


def entry_block(href: str, title: str, body: str) -> str:
    return (
        f'<section class="content-section" {MARKER}><div class="panel">'
        '<span class="eyebrow">Knowledge Graph · teknik kaynak · affiliate güven kapısı</span>'
        f'<h2>{title}</h2><p>{body}</p><div class="actions">'
        f'<a class="btn btn-secondary" href="{href}">Ürün bilgi grafiğini aç</a>'
        '</div><small>Fiyat, stok, puan ve komisyon sıralaması yoktur. Mevcut güvenli ürün yeterliyse yeni ürün almayın.</small>'
        '</div></section>'
    )


def inject_entries(site: Path, base_path: str) -> int:
    href = public_url(base_path, ROUTE)
    copy = {
        "amazon-elektrik-urunleri/index.html": (
            "Ürünleri ihtiyaç, teknik kanıt ve kaynak ilişkisiyle karşılaştırın",
            "Doğrulanmış ASIN ve üretici kaynaklı tam model düğümlerinin hangi ihtiyacı karşıladığını, hangi araçtan sonra açıldığını ve ne zaman satın alınmaması gerektiğini inceleyin.",
        ),
        "akilli-urun-secimi/index.html": (
            "Neden bu ürün? Bilgi grafiğinde görün",
            "Seçim sonucunu kullanıcı ihtiyacı, ürün kategorisi, üretici kaynağı, ASIN/model ayrımı ve satın almama koşuluyla izleyin.",
        ),
        "katalog-guven-durumu/index.html": (
            "Katalog güvenini ürün düğümü düzeyinde denetleyin",
            "Doğrulama tarihini, tam model araması ile ASIN ayrımını, profesyonel-only sınırları ve affiliate kapılarını açık grafikte inceleyin.",
        ),
        "elektrik-portali/index.html": (
            "Elektrik ürünleri için kaynaklı Knowledge Graph",
            "Ürün adıyla değil ihtiyaç, teknik kanıt, risk ve doğrulama statüsüyle başlayan şeffaf ürün yolunu açın.",
        ),
    }
    count = 0
    for relative in TARGETS:
        path = site / relative
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        if MARKER in text or "</main>" not in text:
            continue
        title, body = copy[relative.as_posix()]
        path.write_text(text.replace("</main>", entry_block(href, title, body) + "</main>", 1), encoding="utf-8")
        count += 1
    return count


def add_offline(site: Path, base_path: str) -> list[str]:
    path = site / "sw.js"
    if not path.is_file():
        return []
    text = path.read_text(encoding="utf-8")
    match = re.search(r"const CRITICAL=(\[.*?\]);", text, re.S)
    if not match:
        return []
    routes = json.loads(match.group(1))
    candidates = [public_url(base_path, ROUTE), public_url(base_path, "/urun-bilgi-grafigi/product-graph.json")]
    added = [route for route in candidates if route not in routes]
    if added:
        routes.extend(added)
        path.write_text(text[:match.start(1)] + json.dumps(routes, ensure_ascii=False) + text[match.end(1):], encoding="utf-8")
    return added


def update_manifest(site: Path, base_path: str) -> None:
    path = site / "manifest.webmanifest"
    if not path.is_file():
        return
    manifest = json.loads(path.read_text(encoding="utf-8"))
    shortcuts = manifest.setdefault("shortcuts", [])
    url = public_url(base_path, ROUTE)
    if not any(isinstance(item, dict) and item.get("url") == url for item in shortcuts):
        shortcuts.append({"name": "Affiliate Ürün Bilgi Grafiği", "short_name": "Ürün Grafiği", "url": url})
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def graph_metadata(base_path: str, payload: dict, cards: int, scripts: int, offline: list[str]) -> dict:
    graph = payload["graph"]
    summary = payload["summary"]
    return {
        "version": summary["version"],
        "route": public_url(base_path, ROUTE),
        "graph": public_url(base_path, "/urun-bilgi-grafigi/product-graph.json"),
        "needCount": len(graph["needs"]),
        "categoryCount": len(graph["categories"]),
        "productCount": len(graph["products"]),
        "exactAsinCount": summary["exactListingCount"],
        "manufacturerVerifiedSearchCount": summary["manufacturerSearchCount"],
        "publicProductCount": summary.get("publicProductCount"),
        "gatedCandidateCount": summary.get("gatedCandidateCount"),
        "userFocusedProductCount": summary.get("userFocusedProductCount"),
        "entryCardsInjected": cards,
        "extensionScriptsInjected": scripts,
        "offlineAssetsAdded": offline,
        "commercialRankingFieldsUsed": [],
        "noBuyOutcomePreserved": True,
        "directStoreLinksOnGraphJson": 0,
    }


def update_release(site: Path, base_path: str, payload: dict, cards: int, scripts: int, offline: list[str]) -> None:
    metadata = graph_metadata(base_path, payload, cards, scripts, offline)
    core_path = site / "alo186-release.json"
    core = json.loads(core_path.read_text(encoding="utf-8"))
    core["affiliateProductKnowledgeGraph"] = metadata
    core_path.write_text(json.dumps(core, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    pages_path = site / "pages-release.json"
    if pages_path.is_file():
        pages = json.loads(pages_path.read_text(encoding="utf-8"))
        pages["affiliateProductKnowledgeGraph"] = metadata
        pages["offlineCriticalRouteCount"] = int(pages.get("offlineCriticalRouteCount") or 0) + len(offline)
        pages_path.write_text(json.dumps(pages, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def recompute(site: Path) -> None:
    path = site / "checksums.sha256"
    if path.exists():
        path.unlink()
    files = sorted(item for item in site.rglob("*") if item.is_file())
    path.write_text("\n".join(f"{hashlib.sha256(item.read_bytes()).hexdigest()}  {item.relative_to(site).as_posix()}" for item in files) + "\n", encoding="utf-8")


def run(site: Path, base_path: str = "") -> dict:
    site = site.resolve()
    base_path = normalize_base_path(base_path)
    payload = node_payload(site)
    write_graph_and_schema(site, payload)
    scripts = inject_extension_scripts(site, base_path)
    cards = inject_entries(site, base_path)
    offline = add_offline(site, base_path)
    update_manifest(site, base_path)
    update_release(site, base_path, payload, cards, scripts, offline)
    recompute(site)
    return {"ok": True, "basePath": base_path, **graph_metadata(base_path, payload, cards, scripts, offline)}


def main() -> None:
    parser = argparse.ArgumentParser(description="ALO186 affiliate ürünlerini kaynaklı Product Knowledge Graph olarak yayımlar.")
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--base-path", default="")
    args = parser.parse_args()
    print(json.dumps(run(args.site, args.base_path), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
