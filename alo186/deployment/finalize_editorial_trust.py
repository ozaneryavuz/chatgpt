from __future__ import annotations

import html
import json
import shutil
from pathlib import Path
from typing import Any


TRUST_MARKER = 'data-alo186-editorial-trust="true"'
TRUST_JSONLD_MARKER = 'data-alo186-editorial-trust-jsonld="true"'
STYLE_MARKER = 'data-alo186-editorial-trust-style="true"'
STYLE_SOURCE = Path("alo186/assets/alo186-editorial-trust.css")


def public_url(base_path: str, route: str) -> str:
    prefix = "/" + str(base_path or "").strip("/") if str(base_path or "").strip("/") else ""
    path = "/" + str(route or "").lstrip("/")
    return (prefix + path).replace("//", "/")


def install_style(site: Path, base_path: str) -> str:
    repo_root = Path(__file__).resolve().parents[2]
    source = repo_root / STYLE_SOURCE
    if not source.is_file():
        raise FileNotFoundError(f"Editoryal güven stili eksik: {source}")
    target_dir = site / "assets"
    target_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target_dir / source.name)
    return public_url(base_path, f"/assets/{source.name}")


def inject_block(source: str, base_path: str, style_url: str) -> str:
    if TRUST_MARKER in source:
        return source
    if "</head>" not in source:
        raise RuntimeError("Editoryal güven katmanı için head kapanışı bulunamadı.")
    style = f'<link rel="stylesheet" href="{html.escape(style_url, quote=True)}" {STYLE_MARKER}>'
    source = source.replace("</head>", style + "\n</head>", 1)

    principles = public_url(base_path, "/yayin-ilkeleri")
    sources = public_url(base_path, "/kaynaklar")
    status = public_url(base_path, "/yayin-durumu/")
    correction = public_url(base_path, "/iletisim")
    block = (
        f'<aside class="alo186-editorial-trust" {TRUST_MARKER} aria-label="Teknik yayın ve düzeltme yöntemi">'
        '<strong>Bu teknik rehber nasıl hazırlanır?</strong>'
        '<p>ALO186, birincil kurum, standart ve üretici kaynaklarını önceliklendirir; kaynak ve son doğrulama tarihi değişebilen konularda görünür tutulur. '
        'Can güvenliği, yetkili uygulama ve “yeni ürün almama” sınırları ticari sonuçtan önce gelir. İçerik, saha ölçümü veya resmî kurum kararının yerine geçmez.</p>'
        '<nav aria-label="Yayın güveni bağlantıları">'
        f'<a href="{html.escape(principles, quote=True)}">Yayın yöntemi</a>'
        f'<a href="{html.escape(sources, quote=True)}">Kaynak yaklaşımı</a>'
        f'<a href="{html.escape(status, quote=True)}">Yayın durumunu doğrula</a>'
        f'<a href="{html.escape(correction, quote=True)}">Hata veya düzeltme bildir</a>'
        '</nav></aside>'
    )
    insertion = source.rfind("</article>")
    closing = "</article>"
    if insertion < 0:
        insertion = source.rfind("</main>")
        closing = "</main>"
    if insertion < 0:
        raise RuntimeError("Editoryal güven katmanı için article/main kapanışı bulunamadı.")
    source = source[:insertion] + block + source[insertion:]

    schema = {
        "@context": "https://schema.org",
        "@type": "Organization",
        "@id": "https://alo186.com/#organization",
        "name": "ALO186",
        "url": "https://alo186.com",
        "description": "Bağımsız elektrik bilgi ve yönlendirme platformu.",
        "publishingPrinciples": "https://alo186.com/yayin-ilkeleri",
        "sameAs": ["https://github.com/ozaneryavuz/chatgpt"],
    }
    trust_jsonld = (
        f'<script type="application/ld+json" {TRUST_JSONLD_MARKER}>'
        + json.dumps(schema, ensure_ascii=False, separators=(",", ":"))
        + "</script>"
    )
    source = source.replace("</head>", trust_jsonld + "\n</head>", 1)
    if closing not in source:
        raise RuntimeError("Editoryal güven kapanış kontrolü başarısız.")
    return source


def run(site: Path, base_path: str, canonical_release: dict[str, Any]) -> dict[str, Any]:
    style_url = install_style(site, base_path)
    injected = 0
    already_present = 0
    article_count = 0
    for route in canonical_release.get("routes", []):
        if route.get("type") != "article":
            continue
        article_count += 1
        canonical_path = str(route.get("canonicalPath") or "")
        target = site / canonical_path.strip("/") / "index.html"
        if not target.is_file():
            raise FileNotFoundError(f"Editoryal güven için makale artifactı eksik: {canonical_path}")
        source = target.read_text(encoding="utf-8", errors="ignore")
        if TRUST_MARKER in source:
            already_present += 1
            continue
        transformed = inject_block(source, base_path, style_url)
        if transformed.count(TRUST_MARKER) != 1 or transformed.count(TRUST_JSONLD_MARKER) != 1:
            raise RuntimeError(f"Editoryal güven katmanı tekilleştirilemedi: {canonical_path}")
        target.write_text(transformed, encoding="utf-8")
        injected += 1

    if article_count < 50:
        raise RuntimeError(f"Editoryal güven kapsamındaki makale sayısı beklenenden küçük: {article_count}")
    if injected + already_present != article_count:
        raise RuntimeError("Editoryal güven kapsamı bütün makaleleri içermiyor.")
    return {
        "articleCount": article_count,
        "trustBlocksInjected": injected,
        "alreadyPresent": already_present,
        "style": style_url,
        "publicationPrinciples": public_url(base_path, "/yayin-ilkeleri"),
        "sources": public_url(base_path, "/kaynaklar"),
        "releaseStatus": public_url(base_path, "/yayin-durumu/"),
        "corrections": public_url(base_path, "/iletisim"),
        "namedIndividualClaimed": False,
        "personalDataStored": False,
    }
