#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
SITE_SLUG = "alo186"
TARGET = "chatgpt-sites"
BRIDGE_VERSION = "1.1.0"
REPOSITORY = "ozaneryavuz/chatgpt"


class BridgeError(RuntimeError):
    pass


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise BridgeError(f"Dosya bulunamadı: {path}") from exc
    except json.JSONDecodeError as exc:
        raise BridgeError(f"Geçersiz JSON: {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise BridgeError(f"JSON kökü nesne olmalı: {path}")
    return value


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def package_digest(package: dict[str, Any]) -> str:
    unsigned = deepcopy(package)
    unsigned.pop("packageHash", None)
    return sha256_text(canonical_json(unsigned))


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def valid_https_url(value: Any) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    parsed = urlparse(value.strip())
    return (
        parsed.scheme == "https"
        and bool(parsed.hostname)
        and not parsed.username
        and not parsed.password
    )


def first_match(pattern: str, text: str) -> str:
    match = re.search(pattern, text, re.I | re.S)
    return html.unescape(match.group(1).strip()) if match else ""


def extract_jsonld(text: str) -> list[Any]:
    values: list[Any] = []
    blocks = re.findall(
        r'<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        text,
        re.I | re.S,
    )
    for block in blocks:
        try:
            values.append(json.loads(html.unescape(block.strip())))
        except json.JSONDecodeError as exc:
            raise BridgeError(f"Canonical HTML içinde geçersiz JSON-LD: {exc}") from exc
    return values


def schema_types(node: Any) -> set[str]:
    found: set[str] = set()
    if isinstance(node, dict):
        value = node.get("@type")
        if isinstance(value, str):
            found.add(value)
        elif isinstance(value, list):
            found.update(item for item in value if isinstance(item, str))
        for child in node.values():
            found.update(schema_types(child))
    elif isinstance(node, list):
        for child in node:
            found.update(schema_types(child))
    return found


def validate_source_commit(value: str) -> None:
    if not re.fullmatch(r"[0-9a-f]{7,40}", value):
        raise BridgeError("source commit 7-40 karakter küçük harf hex olmalı")


def content_paths(repo: Path, slug: str) -> tuple[Path, Path]:
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
        raise BridgeError("Geçersiz slug")
    return (
        repo / "alo186" / "ai-cms" / "content" / f"{slug}.json",
        repo / "alo186" / "haberler" / slug / "index.html",
    )


def validate_published_record(
    *,
    record: dict[str, Any],
    canonical_html: str,
    policy: dict[str, Any],
    slug: str,
) -> dict[str, Any]:
    errors: list[str] = []
    if record.get("slug") != slug:
        errors.append("record slug uyuşmuyor")
    if record.get("state") != "published":
        errors.append("yalnız published kayıt Sites paketine girebilir")

    editorial = record.get("editorial")
    if not isinstance(editorial, dict):
        errors.append("editorial nesnesi yok")
    else:
        if editorial.get("humanReviewRequired") is not True:
            errors.append("humanReviewRequired true olmalı")
        for key in ("approvedBy", "approvedAt", "publishedAt"):
            if not isinstance(editorial.get(key), str) or not editorial[key].strip():
                errors.append(f"{key} yok")
        approval_pr = editorial.get("approvalPr")
        if isinstance(approval_pr, bool) or not isinstance(approval_pr, int):
            errors.append("approvalPr geçersiz")

    minimum = int(policy.get("minimumQualityScore", 85))
    quality = record.get("quality")
    if not isinstance(quality, dict):
        errors.append("quality nesnesi yok")
    else:
        score = quality.get("score")
        required = quality.get("minimumRequired")
        if isinstance(score, bool) or not isinstance(score, int) or score < minimum:
            errors.append(f"quality score {minimum} altında")
        if isinstance(required, bool) or not isinstance(required, int) or required < minimum:
            errors.append("record minimumRequired politika eşiğinin altında")

    canonical_path = f"/haberler/{slug}"
    canonical_url = str(policy.get("canonicalHost", "https://alo186.com")) + canonical_path
    seo = record.get("seo")
    if not isinstance(seo, dict) or seo.get("canonicalPath") != canonical_path:
        errors.append("canonicalPath slug ile uyuşmuyor")
    if not isinstance(seo, dict) or seo.get("robots") != "index,follow,max-image-preview:large":
        errors.append("robots sözleşmesi bozuk")

    record_id = str(record.get("id", ""))
    if not record_id or f'data-ai-cms-id="{record_id}"' not in canonical_html:
        errors.append("canonical HTML AI CMS kimliğini taşımıyor")
    html_canonical = first_match(
        r'<link\b[^>]*rel=["\']canonical["\'][^>]*href=["\']([^"\']+)',
        canonical_html,
    )
    if html_canonical != canonical_url:
        errors.append("canonical HTML URL’si kayıtla uyuşmuyor")
    if len(re.findall(r"<h1\b", canonical_html, re.I)) != 1:
        errors.append("canonical HTML tek H1 taşımıyor")
    if re.search(
        r'<meta\b[^>]*name=["\']robots["\'][^>]*content=["\'][^"\']*noindex',
        canonical_html,
        re.I,
    ):
        errors.append("canonical HTML noindex olamaz")

    title = first_match(r"<title>(.*?)</title>", canonical_html)
    h1 = first_match(r"<h1\b[^>]*>(.*?)</h1>", canonical_html)
    h1 = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", h1))).strip()
    description = first_match(
        r'<meta\b[^>]*name=["\']description["\'][^>]*content=["\']([^"\']+)',
        canonical_html,
    )
    if title != record.get("title"):
        errors.append("HTML title içerik kaydıyla uyuşmuyor")
    if h1 != record.get("h1"):
        errors.append("HTML H1 içerik kaydıyla uyuşmuyor")
    if description != record.get("description"):
        errors.append("HTML description içerik kaydıyla uyuşmuyor")

    observed: set[str] = set()
    for payload in extract_jsonld(canonical_html):
        observed.update(schema_types(payload))
    required_types = {"Article", "FAQPage", "BreadcrumbList"}
    if not required_types <= observed:
        errors.append("Article, FAQPage ve BreadcrumbList eksik")
    blocked = observed & set(policy.get("forbiddenPublicSchemaTypes", []))
    if blocked:
        errors.append("yasak schema tipi: " + ", ".join(sorted(blocked)))

    for disclosure in policy.get("requiredPublicDisclosures", []):
        if disclosure not in canonical_html:
            errors.append(f"zorunlu açıklama eksik: {disclosure}")

    if errors:
        raise BridgeError("Sites paket doğrulaması başarısız:\n- " + "\n- ".join(errors))
    return {
        "canonicalPath": canonical_path,
        "canonicalUrl": canonical_url,
        "title": title,
        "h1": h1,
        "description": description,
        "schemaTypes": sorted(observed),
    }


def build_package(
    *,
    repo: Path,
    slug: str,
    source_commit: str,
    generated_at: str | None = None,
) -> tuple[dict[str, Any], str, dict[str, Any]]:
    validate_source_commit(source_commit)
    policy = load_json(repo / "alo186" / "ai-cms" / "policy.json")
    record_path, html_path = content_paths(repo, slug)
    record = load_json(record_path)
    try:
        canonical_html = html_path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise BridgeError(f"Canonical HTML bulunamadı: {html_path}") from exc
    verified = validate_published_record(
        record=record,
        canonical_html=canonical_html,
        policy=policy,
        slug=slug,
    )
    package: dict[str, Any] = {
        "schemaVersion": 1,
        "bridgeVersion": BRIDGE_VERSION,
        "target": TARGET,
        "siteSlug": SITE_SLUG,
        "sourceRepository": REPOSITORY,
        "sourceCommit": source_commit,
        "generatedAt": generated_at or utc_now(),
        "reviewPolicy": {
            "humanPreviewRequired": True,
            "automaticDeployAllowed": False,
            "undocumentedApiUseAllowed": False,
        },
        "operation": {
            "action": "create-or-update-route",
            "publish": False,
            "contentId": record["id"],
            "slug": slug,
            "route": verified["canonicalPath"],
            "canonicalUrl": verified["canonicalUrl"],
            "contentRecordPath": record_path.relative_to(repo).as_posix(),
            "canonicalHtmlPath": html_path.relative_to(repo).as_posix(),
            "contentRecordSha256": sha256_text(canonical_json(record)),
            "canonicalHtmlSha256": sha256_text(canonical_html),
            "title": verified["title"],
            "h1": verified["h1"],
            "description": verified["description"],
            "requiredSchemaTypes": ["Article", "FAQPage", "BreadcrumbList"],
            "observedSchemaTypes": verified["schemaTypes"],
            "requiredDisclosures": policy.get("requiredPublicDisclosures", []),
        },
        "receiptSchema": "alo186/ai-cms/schema/sites-receipt.schema.json",
    }
    package["packageHash"] = package_digest(package)
    return package, canonical_html, record


def render_prompt(package: dict[str, Any]) -> str:
    operation = package["operation"]
    return "\n".join(
        [
            "Use @Sites to edit the site with the slug alo186, with:",
            "",
            "Bu paket insan onaylı ALO186 AI CMS içeriğinin ChatGPT Sites önizleme aktarımıdır.",
            "Ekli canonical.html ve content-record.json dosyalarını kaynak kabul et.",
            f"Rota: {operation['route']}",
            f"Canonical: {operation['canonicalUrl']}",
            f"Title: {operation['title']}",
            f"H1: {operation['h1']}",
            f"Kaynak commit: {package['sourceCommit']}",
            f"Paket hash: {package['packageHash']}",
            "",
            "Önce önizleme oluştur; bu aşamada yayınlama.",
            "Canonical, tek H1, meta description, Article + FAQPage + BreadcrumbList, iç bağlantılar,",
            "kurumsal bağımsızlık açıklamaları ve güvenlik sınırlarını koru.",
            "Product, Offer, Person veya ProfilePage ekleme; fiyat, stok, puan veya garanti üretme.",
            "Kişisel veri toplama ve kullanıcı girdilerini analitiğe gönderme.",
            "Önizleme sonunda rota bazında kabul özeti üret ve açık yayın onayı bekle.",
            "",
        ]
    )


def receipt_template(package: dict[str, Any]) -> dict[str, Any]:
    operation = package["operation"]
    return {
        "schemaVersion": 1,
        "siteSlug": SITE_SLUG,
        "target": TARGET,
        "packageHash": package["packageHash"],
        "sourceCommit": package["sourceCommit"],
        "contentId": operation["contentId"],
        "contentRecordSha256": operation["contentRecordSha256"],
        "canonicalHtmlSha256": operation["canonicalHtmlSha256"],
        "canonicalUrl": operation["canonicalUrl"],
        "deploymentUrl": None,
        "publishedAt": None,
        "liveVerified": False,
        "verification": {
            "httpStatus": None,
            "canonicalMatched": False,
            "titleMatched": False,
            "h1Matched": False,
            "structuredDataPresent": False,
            "platformConfirmed": False,
        },
    }


def write_package(
    *,
    repo: Path,
    slug: str,
    source_commit: str,
    out_dir: Path,
) -> dict[str, Any]:
    package, canonical_html, record = build_package(
        repo=repo,
        slug=slug,
        source_commit=source_commit,
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "sites-package.json").write_text(
        json.dumps(package, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (out_dir / "canonical.html").write_text(canonical_html, encoding="utf-8")
    (out_dir / "content-record.json").write_text(
        json.dumps(record, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (out_dir / "sites-preview-prompt.md").write_text(
        render_prompt(package),
        encoding="utf-8",
    )
    (out_dir / "sites-receipt-template.json").write_text(
        json.dumps(receipt_template(package), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return package


def validate_receipt(
    receipt: dict[str, Any],
    package: dict[str, Any],
    canonical_html: str,
    content_record: dict[str, Any],
) -> None:
    errors: list[str] = []
    operation = package.get("operation") if isinstance(package.get("operation"), dict) else {}

    recalculated_package_hash = package_digest(package)
    if package.get("packageHash") != recalculated_package_hash:
        errors.append("sites-package.json packageHash yeniden hesaplamasıyla uyuşmuyor")
    recalculated_record_hash = sha256_text(canonical_json(content_record))
    if operation.get("contentRecordSha256") != recalculated_record_hash:
        errors.append("content-record.json SHA-256 paketle uyuşmuyor")
    recalculated_html_hash = sha256_text(canonical_html)
    if operation.get("canonicalHtmlSha256") != recalculated_html_hash:
        errors.append("canonical.html SHA-256 paketle uyuşmuyor")

    expected = {
        "siteSlug": package.get("siteSlug"),
        "target": package.get("target"),
        "packageHash": recalculated_package_hash,
        "sourceCommit": package.get("sourceCommit"),
        "contentId": operation.get("contentId"),
        "contentRecordSha256": recalculated_record_hash,
        "canonicalHtmlSha256": recalculated_html_hash,
        "canonicalUrl": operation.get("canonicalUrl"),
    }
    for key, value in expected.items():
        if receipt.get(key) != value:
            errors.append(f"{key} teslim dosyalarıyla uyuşmuyor")

    if receipt.get("schemaVersion") != 1:
        errors.append("schemaVersion 1 olmalı")
    if not valid_https_url(receipt.get("deploymentUrl")):
        errors.append("deploymentUrl geçerli HTTPS URL olmalı")
    try:
        published = datetime.fromisoformat(str(receipt.get("publishedAt")).replace("Z", "+00:00"))
        if published.tzinfo is None:
            raise ValueError("timezone gerekli")
    except (TypeError, ValueError):
        errors.append("publishedAt timezone içeren ISO tarih-saat olmalı")
    if receipt.get("liveVerified") is not True:
        errors.append("liveVerified true olmalı")

    verification = receipt.get("verification")
    if not isinstance(verification, dict):
        errors.append("verification nesnesi gerekli")
    else:
        if verification.get("httpStatus") != 200:
            errors.append("httpStatus 200 olmalı")
        for key in (
            "canonicalMatched",
            "titleMatched",
            "h1Matched",
            "structuredDataPresent",
            "platformConfirmed",
        ):
            if verification.get(key) is not True:
                errors.append(f"{key} true olmalı")

    if errors:
        raise BridgeError("Sites yayın makbuzu geçersiz:\n- " + "\n- ".join(errors))


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(
        description="ALO186 AI CMS → ChatGPT Sites insan onaylı yayın köprüsü"
    )
    result.add_argument("--repo", type=Path, default=REPO_ROOT)
    commands = result.add_subparsers(dest="command", required=True)

    package = commands.add_parser(
        "package",
        help="Published içerikten ChatGPT Sites önizleme artifactı üret",
    )
    package.add_argument("--slug", required=True)
    package.add_argument("--source-commit", required=True)
    package.add_argument("--out-dir", type=Path, required=True)

    receipt = commands.add_parser(
        "validate-receipt",
        help="Sites canlı yayın makbuzunu gerçek teslim dosyalarıyla karşılaştır",
    )
    receipt.add_argument("--receipt", type=Path, required=True)
    receipt.add_argument("--package", type=Path, required=True)
    receipt.add_argument("--canonical-html", type=Path)
    receipt.add_argument("--content-record", type=Path)
    return result


def main() -> None:
    args = parser().parse_args()
    try:
        if args.command == "package":
            package = write_package(
                repo=args.repo.resolve(),
                slug=args.slug,
                source_commit=args.source_commit,
                out_dir=args.out_dir.resolve(),
            )
            print(
                json.dumps(
                    {
                        "ok": True,
                        "siteSlug": package["siteSlug"],
                        "route": package["operation"]["route"],
                        "packageHash": package["packageHash"],
                        "publish": package["operation"]["publish"],
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )
            return

        package_path = args.package.resolve()
        canonical_path = (
            args.canonical_html.resolve()
            if args.canonical_html
            else package_path.parent / "canonical.html"
        )
        record_path = (
            args.content_record.resolve()
            if args.content_record
            else package_path.parent / "content-record.json"
        )
        receipt = load_json(args.receipt.resolve())
        package = load_json(package_path)
        try:
            canonical_html = canonical_path.read_text(encoding="utf-8")
        except FileNotFoundError as exc:
            raise BridgeError(f"Canonical teslim dosyası bulunamadı: {canonical_path}") from exc
        content_record = load_json(record_path)
        validate_receipt(receipt, package, canonical_html, content_record)
        print(
            json.dumps(
                {"ok": True, "contentId": receipt["contentId"]},
                ensure_ascii=False,
                indent=2,
            )
        )
    except BridgeError as exc:
        raise SystemExit(str(exc)) from exc


if __name__ == "__main__":
    main()
