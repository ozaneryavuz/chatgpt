from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NEW = [
    {
        "slug": "ev-sarj-istasyonu-tip-b-rcd-rdc-dd-secimi",
        "required": ["Tip B", "Tip A", "RDC-DD", "6 mA DC", "30 mA", "yetkili elektrikçi"],
        "cta": "/hesaplama/ev-sarj-uygunluk/",
    },
    {
        "slug": "topraklama-direnci-ariza-cevrim-empedansi-farki",
        "required": ["RA", "Ze", "Zs", "R1 + R2", "otomatik açma", "RCD"],
        "cta": "/karar-motoru",
    },
    {
        "slug": "detuned-reaktor-aktif-harmonik-filtre-farki",
        "required": ["detuned reaktör", "aktif harmonik filtre", "rezonans", "5. harmonik", "THDi", "tuning frequency"],
        "cta": "/isletme-surekliligi",
    },
]


def update_manifest() -> None:
    path = ROOT / "alo186/deployment/routing-manifest.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["version"] = 33
    existing = {route["canonicalPath"] for route in data["routes"]}
    for item in NEW:
        canonical = f"/haberler/{item['slug']}"
        if canonical not in existing:
            data["routes"].append({
                "source": f"alo186/haberler/{item['slug']}/index.html",
                "canonicalPath": canonical,
                "type": "article",
            })
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def update_sitemap() -> None:
    path = ROOT / "alo186/sitemap.xml"
    text = path.read_text(encoding="utf-8")
    additions = []
    for item in NEW:
        url = f"https://www.alo186.com/haberler/{item['slug']}"
        if url not in text:
            additions.append(f"  <url><loc>{url}</loc><lastmod>2026-07-28</lastmod><changefreq>monthly</changefreq><priority>0.9</priority></url>")
    if additions:
        text = text.replace("</urlset>", "\n".join(additions) + "\n</urlset>")
    path.write_text(text, encoding="utf-8")


def js_entry(item: dict[str, object]) -> str:
    required = ",".join(repr(value) for value in item["required"])
    return f"  {{slug:'{item['slug']}',required:[{required}],cta:'{item['cta']}',fresh:true,portalOptional:true}}"


def update_authority_test() -> None:
    path = ROOT / "alo186/tests/test_authority_content.js"
    text = path.read_text(encoding="utf-8")
    marker = "  {slug:'ups-aku-string-dengesizligi-zayif-aku-nasil-anlasilir'"
    marker_start = text.find(marker)
    if marker_start < 0:
        raise RuntimeError("Authority test insertion marker not found")
    marker_end = text.find("\n", marker_start)
    if marker_end < 0:
        raise RuntimeError("Authority test marker line end not found")
    additions = []
    for item in NEW:
        if f"slug:'{item['slug']}'" not in text:
            additions.append(js_entry(item))
    if additions:
        existing_line = text[marker_start:marker_end]
        if not existing_line.rstrip().endswith(','):
            text = text[:marker_end] + ',' + text[marker_end:]
            marker_end += 1
        text = text[:marker_end] + "\n" + ",\n".join(additions) + text[marker_end:]
    text = re.sub(r"articles\.length,\d+,'İçerik kalite testi \d+ teknik makaleyi kapsamalı\.'", "articles.length,72,'İçerik kalite testi 72 teknik makaleyi kapsamalı.'", text)
    text = re.sub(r"routing\.routes\.filter\(route=>route\.type==='article'\)\.length,\d+,'Routing manifest \d+ teknik makale içermeli\.'", "routing.routes.filter(route=>route.type==='article').length,72,'Routing manifest 72 teknik makale içermeli.'", text)
    path.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    update_manifest()
    update_sitemap()
    update_authority_test()
    print("ALO186 authority inventory updated to 72 verified guides.")
