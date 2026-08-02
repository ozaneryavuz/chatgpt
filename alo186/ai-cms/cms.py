#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import html
import ipaddress
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit


REPO_ROOT = Path(__file__).resolve().parents[2]
CMS_ROOT = REPO_ROOT / "alo186/ai-cms"
POLICY_PATH = CMS_ROOT / "policy.json"
BRIEF_DIR = CMS_ROOT / "briefs"
CONTENT_DIR = CMS_ROOT / "content"
REVIEW_DIR = CMS_ROOT / "reviews"
PREVIEW_DIR = CMS_ROOT / "previews"
PROMPT_PATH = CMS_ROOT / "prompts/article-system.txt"
DRAFT_SCHEMA_PATH = CMS_ROOT / "schema/draft-output.schema.json"
ROUTING_MANIFEST = REPO_ROOT / "alo186/deployment/routing-manifest.json"
ROUTING_OVERLAYS = REPO_ROOT / "alo186/deployment/routing-overlays"
PUBLISHED_ROOT = REPO_ROOT / "alo186/haberler"
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SOURCE_ID_RE = re.compile(r"^S[1-9][0-9]*$")
EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)
PHONE_RE = re.compile(r"(?<!\d)(?:\+?90\s*)?0?5\d{2}[\s.-]?\d{3}[\s.-]?\d{2}[\s.-]?\d{2}(?!\d)")
TAG_RE = re.compile(r"<[^>]+>")
TITLE_RE = re.compile(r"<title\b[^>]*>(.*?)</title>", re.I | re.S)
H1_RE = re.compile(r"<h1\b[^>]*>(.*?)</h1>", re.I | re.S)
CANONICAL_RE = re.compile(r'<link\b[^>]*rel=["\']canonical["\'][^>]*href=["\']([^"\']+)', re.I)
STOPWORDS = {
    "ve", "veya", "ile", "için", "icin", "bir", "bu", "şu", "su", "nasıl", "nasil",
    "nedir", "mi", "mı", "mu", "mü", "ne", "de", "da", "en", "doğru", "dogru",
    "seçilir", "secilir", "rehberi", "kontrol", "alo186", "elektrik"
}


class CmsError(RuntimeError):
    pass


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def today() -> str:
    return dt.datetime.now(dt.timezone.utc).date().isoformat()


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise CmsError(f"Dosya bulunamadı: {path}") from exc
    except json.JSONDecodeError as exc:
        raise CmsError(f"Geçersiz JSON: {path}: {exc}") from exc


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def load_policy() -> dict[str, Any]:
    policy = read_json(POLICY_PATH)
    if policy.get("schemaVersion") != 1:
        raise CmsError("AI CMS policy schemaVersion=1 olmalıdır.")
    return policy


def ensure_slug(value: str) -> str:
    slug = value.strip().lower()
    if not SLUG_RE.fullmatch(slug) or not 6 <= len(slug) <= 96:
        raise CmsError("Slug 6–96 karakter ve yalnız küçük harf, sayı, tire içermelidir.")
    return slug


def parse_json_value(value: str | None, expected: type, label: str) -> Any:
    if value is None or not value.strip():
        return expected()
    raw = value.strip()
    if raw.startswith("@"):
        raw = Path(raw[1:]).read_text(encoding="utf-8")
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise CmsError(f"{label} geçerli JSON olmalıdır: {exc}") from exc
    if not isinstance(parsed, expected):
        raise CmsError(f"{label} {expected.__name__} olmalıdır.")
    return parsed


def brief_path(slug: str) -> Path:
    return BRIEF_DIR / f"{slug}.json"


def content_path(slug: str) -> Path:
    return CONTENT_DIR / f"{slug}.json"


def review_path(slug: str) -> Path:
    return REVIEW_DIR / f"{slug}.md"


def preview_path(slug: str) -> Path:
    return PREVIEW_DIR / f"{slug}.html"


def content_id(slug: str, requested_at: str) -> str:
    digest = hashlib.sha256(f"{slug}|{requested_at}".encode("utf-8")).hexdigest()[:16]
    return f"cms_{digest}"


def plain_text(value: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(TAG_RE.sub(" ", value))).strip()


def normalize_text(value: str) -> str:
    value = value.casefold().replace("ı", "i").replace("ğ", "g").replace("ü", "u").replace("ş", "s").replace("ö", "o").replace("ç", "c")
    return re.sub(r"[^a-z0-9]+", " ", value).strip()


def token_set(value: str) -> set[str]:
    return {token for token in normalize_text(value).split() if len(token) > 2 and token not in STOPWORDS}


def jaccard(left: str, right: str) -> float:
    a = token_set(left)
    b = token_set(right)
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def word_count(value: str) -> int:
    return len(re.findall(r"\b\w+\b", value, re.UNICODE))


def route_shape(route: dict[str, Any]) -> tuple[str, str, str] | None:
    if all(route.get(key) for key in ("canonicalPath", "source", "type")):
        return str(route["canonicalPath"]), str(route["source"]), str(route["type"])
    if all(route.get(key) for key in ("path", "file", "intent")):
        return str(route["path"]), f"alo186/{route['file']}", "article"
    return None


def route_inventory() -> dict[str, dict[str, str]]:
    documents = [ROUTING_MANIFEST]
    if ROUTING_OVERLAYS.is_dir():
        documents.extend(sorted(ROUTING_OVERLAYS.glob("*.json")))
    result: dict[str, dict[str, str]] = {}
    for document in documents:
        data = read_json(document)
        for raw in data.get("routes", []):
            shape = route_shape(raw)
            if not shape:
                continue
            canonical, source, route_type = shape
            result[canonical] = {"source": source, "type": route_type, "document": document.name}
    return result


def existing_documents(exclude_slug: str | None = None) -> list[dict[str, str]]:
    result: list[dict[str, str]] = []
    excluded_target = PUBLISHED_ROOT / exclude_slug / "index.html" if exclude_slug else None
    for path in sorted((REPO_ROOT / "alo186").rglob("index.html")):
        if "ai-cms" in path.parts or path == excluded_target:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        title_match = TITLE_RE.search(text)
        h1_match = H1_RE.search(text)
        if not title_match and not h1_match:
            continue
        canonical_match = CANONICAL_RE.search(text)
        result.append(
            {
                "path": canonical_match.group(1) if canonical_match else path.relative_to(REPO_ROOT).as_posix(),
                "title": plain_text(title_match.group(1)) if title_match else "",
                "h1": plain_text(h1_match.group(1)) if h1_match else "",
            }
        )
    return result


def source_is_safe(source: dict[str, Any]) -> tuple[bool, str]:
    url = str(source.get("url", ""))
    parsed = urlsplit(url)
    if parsed.scheme != "https" or not parsed.hostname:
        return False, "Kaynak URL HTTPS ve hostname içermelidir."
    hostname = parsed.hostname.casefold()
    if hostname in {"localhost", "localhost.localdomain"} or hostname.endswith(".local"):
        return False, "Yerel kaynak URL kullanılamaz."
    try:
        address = ipaddress.ip_address(hostname)
    except ValueError:
        return True, ""
    if address.is_private or address.is_loopback or address.is_link_local or address.is_reserved:
        return False, "Özel veya yerel IP kaynak URL olarak kullanılamaz."
    return True, ""


def validate_brief(brief: dict[str, Any], policy: dict[str, Any], require_sources: bool = False) -> list[str]:
    errors: list[str] = []
    required = {
        "schemaVersion", "id", "slug", "contentType", "state", "locale", "topic", "titleSeed",
        "intent", "primaryKeyword", "audience", "riskClass", "sources", "internalLinks", "commerce",
        "requestedAt", "requestedBy"
    }
    missing = sorted(required - set(brief))
    if missing:
        errors.append("Eksik brief alanları: " + ", ".join(missing))
        return errors
    try:
        ensure_slug(str(brief["slug"]))
    except CmsError as exc:
        errors.append(str(exc))
    if brief["schemaVersion"] != 1 or brief["state"] != "brief" or brief["locale"] != "tr-TR":
        errors.append("Brief schemaVersion=1, state=brief ve locale=tr-TR olmalıdır.")
    if brief["contentType"] not in policy["allowedContentTypes"]:
        errors.append("Desteklenmeyen içerik türü.")
    if brief["riskClass"] not in policy["allowedRiskClasses"]:
        errors.append("Desteklenmeyen risk sınıfı.")
    if not isinstance(brief["audience"], list) or not brief["audience"]:
        errors.append("En az bir hedef kitle gerekir.")
    if not isinstance(brief["sources"], list):
        errors.append("sources dizi olmalıdır.")
    if not isinstance(brief["internalLinks"], list) or len(brief["internalLinks"]) < policy["minimumInternalLinks"]:
        errors.append(f"En az {policy['minimumInternalLinks']} iç bağlantı gerekir.")
    source_ids: set[str] = set()
    for index, source in enumerate(brief.get("sources", []), start=1):
        if not isinstance(source, dict):
            errors.append(f"Kaynak {index} nesne olmalıdır.")
            continue
        source_id = str(source.get("id", ""))
        if not SOURCE_ID_RE.fullmatch(source_id) or source_id in source_ids:
            errors.append(f"Geçersiz veya yinelenen kaynak kimliği: {source_id!r}")
        source_ids.add(source_id)
        for key in ("publisher", "title", "url", "accessedAt", "primary", "factSummary"):
            if key not in source:
                errors.append(f"{source_id or index} kaynağında {key} eksik.")
        safe, reason = source_is_safe(source)
        if not safe:
            errors.append(f"{source_id or index}: {reason}")
        if len(str(source.get("factSummary", ""))) < 30:
            errors.append(f"{source_id or index}: factSummary en az 30 karakter olmalıdır.")
    if require_sources:
        minimum = int(policy["minimumSources"][brief["riskClass"]])
        if len(brief["sources"]) < minimum:
            errors.append(f"{brief['riskClass']} risk sınıfı için en az {minimum} kaynak gerekir.")
        if brief["riskClass"] in policy["primarySourceRequired"] and not any(source.get("primary") is True for source in brief["sources"]):
            errors.append("Bu risk sınıfı için en az bir birincil kaynak gerekir.")
    if brief["riskClass"] in policy["affiliateBlockedRiskClasses"] and brief["commerce"].get("enabled"):
        errors.append("Yüksek veya hukukî riskli içerikte ticari CTA açılamaz.")
    return errors


def make_brief(args: argparse.Namespace, policy: dict[str, Any]) -> dict[str, Any]:
    requested_at = utc_now()
    slug = ensure_slug(args.slug)
    sources = parse_json_value(args.sources_json, list, "sources-json")
    links = parse_json_value(args.internal_links_json, list, "internal-links-json")
    if not links:
        links = [
            {"label": "Elektrik Portalı", "path": "/elektrik-portali", "reason": "Kullanıcının ana işlem merkezine dönmesini sağlar."},
            {"label": "Ücretsiz hesaplayıcılar", "path": "/hesaplama/", "reason": "İçeriği uygulanabilir ücretsiz araçlara bağlar."},
        ]
    commerce_enabled = bool(args.commerce_category)
    commerce_policy = "after_tool" if commerce_enabled else "none"
    if args.risk_class in policy["affiliateBlockedRiskClasses"]:
        commerce_enabled = False
        commerce_policy = "none"
    return {
        "schemaVersion": 1,
        "id": content_id(slug, requested_at),
        "slug": slug,
        "contentType": args.content_type,
        "state": "brief",
        "locale": "tr-TR",
        "topic": args.topic.strip(),
        "titleSeed": args.title.strip(),
        "intent": args.intent.strip(),
        "primaryKeyword": args.primary_keyword.strip(),
        "audience": [item.strip() for item in args.audience.split(",") if item.strip()],
        "riskClass": args.risk_class,
        "sources": sources,
        "internalLinks": links,
        "commerce": {
            "enabled": commerce_enabled,
            "policy": commerce_policy,
            "category": args.commerce_category or None,
        },
        "requestedAt": requested_at,
        "requestedBy": args.requested_by.strip() or "github-workflow",
    }


class OpenAIResponsesClient:
    def __init__(self, api_key: str, base_url: str | None = None) -> None:
        if not api_key.strip():
            raise CmsError("OPENAI_API_KEY repository secretı zorunludur.")
        self.api_key = api_key.strip()
        self.base_url = (base_url or os.getenv("OPENAI_BASE_URL") or "https://api.openai.com/v1").rstrip("/")

    def create_structured(self, *, model: str, instructions: str, prompt: str, schema: dict[str, Any]) -> dict[str, Any]:
        schema = dict(schema)
        schema.pop("$schema", None)
        schema.pop("$id", None)
        payload = {
            "model": model,
            "store": False,
            "safety_identifier": "alo186-ai-cms",
            "prompt_cache_key": "alo186-ai-cms-v1",
            "instructions": instructions,
            "input": [{"role": "user", "content": [{"type": "input_text", "text": prompt}]}],
            "text": {
                "format": {
                    "type": "json_schema",
                    "name": "alo186_content_draft",
                    "description": "ALO186 kaynak bağlı teknik içerik taslağı",
                    "strict": True,
                    "schema": schema,
                },
                "verbosity": "medium",
            },
            "max_output_tokens": 12000,
        }
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        request = urllib.request.Request(
            f"{self.base_url}/responses",
            data=body,
            method="POST",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "ALO186-AI-CMS/1.0",
            },
        )
        last_error = ""
        for attempt in range(3):
            try:
                with urllib.request.urlopen(request, timeout=180) as response:
                    data = json.loads(response.read().decode("utf-8"))
                return self._extract(data)
            except urllib.error.HTTPError as exc:
                detail = exc.read().decode("utf-8", errors="replace")[:1200]
                last_error = f"HTTP {exc.code}: {detail}"
                if exc.code not in {408, 409, 429, 500, 502, 503, 504} or attempt == 2:
                    break
            except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
                last_error = str(exc)
                if attempt == 2:
                    break
            time.sleep(2 ** attempt)
        raise CmsError(f"OpenAI Responses API çağrısı başarısız: {last_error}")

    @staticmethod
    def _extract(data: dict[str, Any]) -> dict[str, Any]:
        if data.get("status") not in {"completed", None}:
            raise CmsError(f"AI yanıtı tamamlanmadı: {data.get('status')}")
        texts: list[str] = []
        refusals: list[str] = []
        for item in data.get("output", []):
            if item.get("type") != "message":
                continue
            for part in item.get("content", []):
                if part.get("type") == "output_text" and part.get("text"):
                    texts.append(str(part["text"]))
                if part.get("type") == "refusal":
                    refusals.append(str(part.get("refusal", "AI isteği reddetti.")))
        if refusals:
            raise CmsError("AI yanıtı reddedildi: " + " ".join(refusals))
        if not texts:
            raise CmsError("AI yanıtında output_text bulunamadı.")
        try:
            value = json.loads("".join(texts))
        except json.JSONDecodeError as exc:
            raise CmsError(f"AI structured output JSON olarak okunamadı: {exc}") from exc
        if not isinstance(value, dict):
            raise CmsError("AI structured output nesne olmalıdır.")
        return value


def nearest_existing(seed: str, limit: int = 12) -> list[dict[str, Any]]:
    scored = []
    for document in existing_documents():
        score = jaccard(seed, f"{document['title']} {document['h1']}")
        if score > 0:
            scored.append({**document, "similarity": round(score, 3)})
    return sorted(scored, key=lambda item: (-item["similarity"], item["path"]))[:limit]


def ai_prompt(brief: dict[str, Any]) -> str:
    context = {
        "task": "ALO186 için kaynak bağlı, uygulanabilir, kullanıcı güvenli Türkçe teknik içerik taslağı üret.",
        "brief": brief,
        "sourceRule": "Yalnız brief.sources içindeki factSummary alanlarını kullan ve her iddiayı ilgili S# kimliğiyle sourceRefs içine bağla.",
        "existingPotentiallySimilarContent": nearest_existing(
            f"{brief['titleSeed']} {brief['topic']} {brief['primaryKeyword']} {brief['intent']}"
        ),
        "editorialRequirements": {
            "minimumSections": 4,
            "minimumFaqs": 3,
            "approximateWords": "900-1500",
            "directAnswerFirst": True,
            "humanApprovalRequired": True,
            "doNotInventSources": True,
            "doNotUsePersonalData": True,
        },
    }
    return json.dumps(context, ensure_ascii=False, indent=2)


def assemble_record(brief: dict[str, Any], draft: dict[str, Any], model: str) -> dict[str, Any]:
    return {
        "schemaVersion": 1,
        "id": brief["id"],
        "slug": brief["slug"],
        "contentType": brief["contentType"],
        "state": "review",
        "locale": "tr-TR",
        "title": draft["title"],
        "h1": draft["h1"],
        "description": draft["description"],
        "intent": brief["intent"],
        "primaryKeyword": brief["primaryKeyword"],
        "audience": brief["audience"],
        "riskClass": brief["riskClass"],
        "directAnswer": draft["directAnswer"],
        "sections": draft["sections"],
        "faqs": draft["faqs"],
        "sources": brief["sources"],
        "internalLinks": brief["internalLinks"],
        "commerce": brief["commerce"],
        "editorial": {
            "createdBy": "ai-assisted",
            "model": model,
            "humanReviewRequired": True,
            "approvedBy": None,
            "approvedAt": None,
            "publishedAt": None,
            "approvalPr": None,
        },
        "seo": {
            "canonicalPath": f"/haberler/{brief['slug']}",
            "robots": "index,follow,max-image-preview:large",
            "lastModified": today(),
            "topics": draft["topics"],
        },
        "quality": {
            "score": 0,
            "minimumRequired": 85,
            "checks": {},
            "similarity": {"maximum": 0.0, "closestPath": None},
        },
    }


def all_public_text(record: dict[str, Any]) -> str:
    parts = [record.get("title", ""), record.get("h1", ""), record.get("description", ""), record.get("directAnswer", "")]
    for section in record.get("sections", []):
        parts.append(section.get("heading", ""))
        parts.extend(section.get("paragraphs", []))
        parts.extend(section.get("bullets", []))
    for faq in record.get("faqs", []):
        parts.extend([faq.get("question", ""), faq.get("answer", "")])
    return "\n".join(str(part) for part in parts)


def parse_date(value: str, label: str, errors: list[str]) -> dt.date | None:
    try:
        return dt.date.fromisoformat(value)
    except (TypeError, ValueError):
        errors.append(f"{label} YYYY-MM-DD biçiminde olmalıdır.")
        return None


def validate_record(record: dict[str, Any], *, write_quality: bool = False) -> dict[str, Any]:
    policy = load_policy()
    errors: list[str] = []
    warnings: list[str] = []
    required = {
        "schemaVersion", "id", "slug", "contentType", "state", "locale", "title", "h1", "description",
        "intent", "primaryKeyword", "audience", "riskClass", "directAnswer", "sections", "faqs", "sources",
        "internalLinks", "commerce", "editorial", "seo", "quality"
    }
    missing = sorted(required - set(record))
    if missing:
        errors.append("Eksik içerik alanları: " + ", ".join(missing))
        return {"ok": False, "errors": errors, "warnings": warnings, "score": 0, "checks": {}}

    try:
        slug = ensure_slug(str(record["slug"]))
    except CmsError as exc:
        errors.append(str(exc))
        slug = str(record.get("slug", "invalid"))
    if record["schemaVersion"] != 1 or record["locale"] != "tr-TR":
        errors.append("schemaVersion=1 ve locale=tr-TR zorunludur.")
    if record["contentType"] not in policy["allowedContentTypes"]:
        errors.append("Desteklenmeyen contentType.")
    if record["state"] not in policy["allowedStates"] or record["state"] == "brief":
        errors.append("İçerik kaydı review, approved, published veya archived olmalıdır.")
    if record["riskClass"] not in policy["allowedRiskClasses"]:
        errors.append("Desteklenmeyen riskClass.")

    title = str(record["title"]).strip()
    h1 = str(record["h1"]).strip()
    description = str(record["description"]).strip()
    direct = str(record["directAnswer"]).strip()
    if not 20 <= len(title) <= policy["maximumTitleCharacters"]:
        errors.append(f"Title 20–{policy['maximumTitleCharacters']} karakter olmalıdır.")
    if not 20 <= len(h1) <= 110:
        errors.append("H1 20–110 karakter olmalıdır.")
    if not policy["minimumDescriptionCharacters"] <= len(description) <= policy["maximumDescriptionCharacters"]:
        errors.append("Meta description 110–170 karakter olmalıdır.")
    if not 80 <= len(direct) <= policy["maximumDirectAnswerCharacters"]:
        errors.append("Doğrudan cevap 80–650 karakter olmalıdır.")
    expected_canonical = f"/haberler/{slug}"
    if record["seo"].get("canonicalPath") != expected_canonical:
        errors.append(f"Canonical path {expected_canonical} olmalıdır.")
    if record["seo"].get("robots") != "index,follow,max-image-preview:large":
        errors.append("Robots sözleşmesi geçersiz.")
    if len(record["seo"].get("topics", [])) < 3:
        errors.append("En az üç konu terimi gerekir.")

    sections = record.get("sections") if isinstance(record.get("sections"), list) else []
    faqs = record.get("faqs") if isinstance(record.get("faqs"), list) else []
    if len(sections) < policy["minimumSections"]:
        errors.append(f"En az {policy['minimumSections']} bölüm gerekir.")
    if len(faqs) < policy["minimumFaqs"]:
        errors.append(f"En az {policy['minimumFaqs']} SSS gerekir.")

    source_ids: set[str] = set()
    source_errors = False
    risk = record["riskClass"]
    maximum_age = int(policy["maximumSourceAgeDays"][risk])
    now_date = dt.datetime.now(dt.timezone.utc).date()
    for index, source in enumerate(record.get("sources", []), start=1):
        if not isinstance(source, dict):
            errors.append(f"Kaynak {index} nesne olmalıdır.")
            source_errors = True
            continue
        source_id = str(source.get("id", ""))
        if not SOURCE_ID_RE.fullmatch(source_id) or source_id in source_ids:
            errors.append(f"Geçersiz veya yinelenen kaynak kimliği: {source_id!r}")
            source_errors = True
        source_ids.add(source_id)
        safe, reason = source_is_safe(source)
        if not safe:
            errors.append(f"{source_id or index}: {reason}")
            source_errors = True
        accessed = parse_date(str(source.get("accessedAt", "")), f"{source_id}.accessedAt", errors)
        if accessed is not None:
            age = (now_date - accessed).days
            if age < 0 or age > maximum_age:
                errors.append(f"{source_id}: kaynak erişim yaşı {age} gün; {risk} sınırı {maximum_age} gündür.")
                source_errors = True
        if len(str(source.get("factSummary", ""))) < 30:
            errors.append(f"{source_id}: factSummary en az 30 karakter olmalıdır.")
            source_errors = True
    minimum_sources = int(policy["minimumSources"][risk])
    if len(record.get("sources", [])) < minimum_sources:
        errors.append(f"{risk} risk sınıfı için en az {minimum_sources} kaynak gerekir.")
        source_errors = True
    if risk in policy["primarySourceRequired"] and not any(source.get("primary") is True for source in record.get("sources", [])):
        errors.append("Bu risk sınıfı için en az bir birincil kaynak gerekir.")
        source_errors = True

    used_refs: set[str] = set()
    content_shape_errors = False
    section_ids: set[str] = set()
    for index, section in enumerate(sections, start=1):
        section_id = str(section.get("id", ""))
        if not SLUG_RE.fullmatch(section_id) or section_id in section_ids:
            errors.append(f"Bölüm {index}: geçersiz veya yinelenen id.")
            content_shape_errors = True
        section_ids.add(section_id)
        if len(str(section.get("heading", ""))) < 8:
            errors.append(f"Bölüm {index}: heading çok kısa.")
            content_shape_errors = True
        paragraphs = section.get("paragraphs", [])
        if not isinstance(paragraphs, list) or not paragraphs or any(len(str(item)) < 40 for item in paragraphs):
            errors.append(f"Bölüm {index}: en az bir 40+ karakter paragraf gerekir.")
            content_shape_errors = True
        refs = section.get("sourceRefs", [])
        if not refs:
            errors.append(f"Bölüm {index}: sourceRefs eksik.")
            content_shape_errors = True
        for ref in refs:
            used_refs.add(str(ref))
            if ref not in source_ids:
                errors.append(f"Bölüm {index}: bilinmeyen kaynak referansı {ref}.")
                content_shape_errors = True
    for index, faq in enumerate(faqs, start=1):
        if len(str(faq.get("question", ""))) < 12 or len(str(faq.get("answer", ""))) < 40:
            errors.append(f"SSS {index}: soru veya cevap çok kısa.")
            content_shape_errors = True
        refs = faq.get("sourceRefs", [])
        if not refs:
            errors.append(f"SSS {index}: sourceRefs eksik.")
            content_shape_errors = True
        for ref in refs:
            used_refs.add(str(ref))
            if ref not in source_ids:
                errors.append(f"SSS {index}: bilinmeyen kaynak referansı {ref}.")
                content_shape_errors = True
    unused_sources = source_ids - used_refs
    if unused_sources:
        warnings.append("Metinde kullanılmayan kaynaklar: " + ", ".join(sorted(unused_sources)))

    inventory = route_inventory()
    expected_source = f"alo186/haberler/{slug}/index.html"
    collision = inventory.get(expected_canonical)
    target_file = PUBLISHED_ROOT / slug / "index.html"
    if collision and collision["source"] != expected_source:
        errors.append(f"Canonical rota başka kaynağa ait: {collision['source']}")
    if target_file.is_file():
        target_text = target_file.read_text(encoding="utf-8", errors="ignore")
        if f'data-ai-cms-id="{record["id"]}"' not in target_text:
            errors.append("Hedef haber klasörü AI CMS kaydına ait olmayan mevcut içerik taşıyor.")

    missing_links: list[str] = []
    if len(record.get("internalLinks", [])) < policy["minimumInternalLinks"]:
        errors.append(f"En az {policy['minimumInternalLinks']} iç bağlantı gerekir.")
    route_keys = set(inventory)
    for link in record.get("internalLinks", []):
        path = str(link.get("path", "")).split("?", 1)[0].split("#", 1)[0]
        candidates = {path, path.rstrip("/"), path.rstrip("/") + "/"}
        if not any(candidate in route_keys for candidate in candidates):
            missing_links.append(path)
    if missing_links:
        errors.append("Routing envanterinde olmayan iç bağlantılar: " + ", ".join(sorted(set(missing_links))))

    public_text = all_public_text(record)
    folded = public_text.casefold()
    forbidden_hits = [claim for claim in policy["forbiddenClaims"] if claim.casefold() in folded]
    if forbidden_hits:
        errors.append("Yasak kesinlik/kurum iddiaları: " + ", ".join(forbidden_hits))
    if EMAIL_RE.search(public_text) or PHONE_RE.search(public_text):
        errors.append("Yayımlanabilir içerikte kişisel e-posta veya cep telefonu kalıbı bulundu.")
    commerce = record.get("commerce", {})
    commerce_safe = True
    if risk in policy["affiliateBlockedRiskClasses"] and commerce.get("enabled"):
        errors.append("Yüksek veya hukukî riskli içerikte ticari CTA açılamaz.")
        commerce_safe = False
    if commerce.get("enabled") and commerce.get("policy") != "after_tool":
        errors.append("Ticari içerik yalnız after_tool politikasıyla açılabilir.")
        commerce_safe = False

    seed = f"{title} {h1} {record.get('primaryKeyword', '')}"
    maximum_similarity = 0.0
    closest_path: str | None = None
    for document in existing_documents(exclude_slug=slug):
        score = jaccard(seed, f"{document['title']} {document['h1']}")
        if score > maximum_similarity:
            maximum_similarity = score
            closest_path = document["path"]
    if maximum_similarity >= float(policy["similarityBlockThreshold"]):
        errors.append(f"İçerik kanibalizasyon riski {maximum_similarity:.2f}: {closest_path}")

    total_words = word_count(public_text)
    keyword = normalize_text(str(record.get("primaryKeyword", "")))
    metadata_ok = (
        20 <= len(title) <= policy["maximumTitleCharacters"]
        and 20 <= len(h1) <= 110
        and policy["minimumDescriptionCharacters"] <= len(description) <= policy["maximumDescriptionCharacters"]
        and keyword
        and keyword in normalize_text(f"{title} {h1}")
    )
    direct_ok = 80 <= len(direct) <= policy["maximumDirectAnswerCharacters"]
    depth_ok = len(sections) >= policy["minimumSections"] and total_words >= 650 and not content_shape_errors
    sources_ok = not source_errors and not any("bilinmeyen kaynak" in error for error in errors)
    safety_ok = not forbidden_hits and not EMAIL_RE.search(public_text) and not PHONE_RE.search(public_text) and commerce_safe
    links_ok = len(record.get("internalLinks", [])) >= policy["minimumInternalLinks"] and not missing_links
    uniqueness_ok = maximum_similarity < float(policy["similarityBlockThreshold"])
    structured_ok = len(faqs) >= policy["minimumFaqs"] and len(record["seo"].get("topics", [])) >= 3
    checks = {
        "metadata": metadata_ok,
        "directAnswer": direct_ok,
        "contentDepth": depth_ok,
        "sources": sources_ok,
        "safety": safety_ok,
        "internalLinks": links_ok,
        "uniqueness": uniqueness_ok,
        "structuredData": structured_ok,
    }
    score = sum(int(policy["qualityWeights"][name]) for name, passed in checks.items() if passed)

    editorial = record.get("editorial", {})
    if editorial.get("humanReviewRequired") is not True:
        errors.append("humanReviewRequired=true zorunludur.")
    if record["state"] in {"approved", "published"}:
        reviewer = str(editorial.get("approvedBy") or "")
        if not reviewer or reviewer.casefold() in {"ai", "automation", "github-actions[bot]"}:
            errors.append("Approved/published içerikte gerçek insan editör kimliği gerekir.")
        if not editorial.get("approvedAt") or not editorial.get("approvalPr"):
            errors.append("Approved/published içerikte approvedAt ve approvalPr zorunludur.")
        if score < int(policy["minimumQualityScore"]):
            errors.append(f"Kalite puanı {score}; minimum {policy['minimumQualityScore']}.")
    if record["state"] == "published" and not editorial.get("publishedAt"):
        errors.append("Published içerikte publishedAt zorunludur.")
    if record["state"] == "review" and score < int(policy["minimumQualityScore"]):
        warnings.append(f"Taslak kalite puanı {score}; onay için minimum {policy['minimumQualityScore']}.")

    record["quality"] = {
        "score": score,
        "minimumRequired": int(policy["minimumQualityScore"]),
        "checks": checks,
        "similarity": {"maximum": round(maximum_similarity, 4), "closestPath": closest_path},
    }
    if write_quality:
        write_json(content_path(slug), record)
    return {
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "score": score,
        "checks": checks,
        "similarity": record["quality"]["similarity"],
        "totalWords": total_words,
    }


def citation_html(refs: list[str], source_numbers: dict[str, int]) -> str:
    links = []
    for ref in refs:
        if ref in source_numbers:
            number = source_numbers[ref]
            links.append(f'<a href="#source-{html.escape(ref)}" aria-label="Kaynak {number}">[{number}]</a>')
    return f'<sup class="citations">{" ".join(links)}</sup>' if links else ""


def jsonld(record: dict[str, Any], canonical_url: str) -> str:
    approved_date = str(record["editorial"].get("approvedAt") or record["seo"]["lastModified"])[:10]
    graph = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "Article",
                "headline": record["h1"],
                "description": record["description"],
                "datePublished": approved_date,
                "dateModified": record["seo"]["lastModified"],
                "inLanguage": "tr-TR",
                "mainEntityOfPage": canonical_url,
                "author": {"@type": "Organization", "name": "ALO186"},
                "publisher": {"@type": "Organization", "name": "ALO186", "url": load_policy()["canonicalHost"]},
                "publishingPrinciples": load_policy()["canonicalHost"].rstrip("/") + "/yayin-ilkeleri",
                "about": [{"@type": "DefinedTerm", "name": topic} for topic in record["seo"]["topics"]],
                "citation": [source["url"] for source in record["sources"]],
            },
            {
                "@type": "FAQPage",
                "mainEntity": [
                    {
                        "@type": "Question",
                        "name": faq["question"],
                        "acceptedAnswer": {"@type": "Answer", "text": faq["answer"]},
                    }
                    for faq in record["faqs"]
                ],
            },
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "ALO186", "item": load_policy()["canonicalHost"]},
                    {"@type": "ListItem", "position": 2, "name": "Teknik makaleler", "item": load_policy()["canonicalHost"].rstrip("/") + "/haberler/"},
                    {"@type": "ListItem", "position": 3, "name": record["h1"], "item": canonical_url},
                ],
            },
        ],
    }
    return json.dumps(graph, ensure_ascii=False, separators=(",", ":"))


def render_html(record: dict[str, Any], *, preview: bool = False) -> str:
    policy = load_policy()
    canonical_url = policy["canonicalHost"].rstrip("/") + record["seo"]["canonicalPath"]
    source_numbers = {source["id"]: index for index, source in enumerate(record["sources"], start=1)}
    primary_refs = [source["id"] for source in record["sources"] if source.get("primary")][:2]
    if not primary_refs and record["sources"]:
        primary_refs = [record["sources"][0]["id"]]
    sections = []
    for section in record["sections"]:
        paragraphs = "".join(
            f'<p>{html.escape(str(paragraph))}{citation_html(section["sourceRefs"], source_numbers)}</p>'
            for paragraph in section["paragraphs"]
        )
        bullets = ""
        if section.get("bullets"):
            bullets = '<ul class="checklist">' + "".join(f"<li>{html.escape(str(item))}</li>" for item in section["bullets"]) + "</ul>"
        sections.append(f'<section id="{html.escape(section["id"])}"><h2>{html.escape(section["heading"])}</h2>{paragraphs}{bullets}</section>')
    faq_html = "".join(
        f'<details><summary>{html.escape(faq["question"])}</summary><p>{html.escape(faq["answer"])}{citation_html(faq["sourceRefs"], source_numbers)}</p></details>'
        for faq in record["faqs"]
    )
    sources_html = "".join(
        f'<li id="source-{html.escape(source["id"])}"><a href="{html.escape(source["url"], quote=True)}" target="_blank" rel="external noopener">{html.escape(source["publisher"])} — {html.escape(source["title"])}</a><span>Erişim: {html.escape(source["accessedAt"])}</span></li>'
        for source in record["sources"]
    )
    related_html = "".join(
        f'<a class="button secondary" href="{html.escape(link["path"], quote=True)}">{html.escape(link["label"])}</a>'
        for link in record["internalLinks"]
    )
    robots = "noindex,nofollow" if preview else record["seo"]["robots"]
    preview_banner = '<div class="danger"><strong>AI CMS önizleme:</strong> Bu taslak yayımlanmamıştır ve insan editör onayı bekler.</div>' if preview else ""
    public_date = record["editorial"].get("publishedAt") or record["editorial"].get("approvedAt") or utc_now()
    return f'''<!doctype html>
<html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><title>{html.escape(record["title"])}</title><meta name="description" content="{html.escape(record["description"], quote=True)}"><meta name="robots" content="{robots}"><meta name="theme-color" content="#071631"><link rel="canonical" href="{html.escape(canonical_url, quote=True)}"><link rel="stylesheet" href="/haberler/alo186-article.css"><script type="application/ld+json">{jsonld(record, canonical_url)}</script></head>
<body data-ai-cms-id="{html.escape(record["id"])}" data-ai-cms-version="1" data-risk-class="{html.escape(record["riskClass"])}"><header class="top"><div class="wrap"><a class="brand" href="/"><span>186</span><div><strong>ALO186</strong><small>Bağımsız elektrik bilgi ağı</small></div></a><nav aria-label="Ana bağlantılar"><a href="/haberler/">Teknik makaleler</a><a href="/elektrik-portali">Elektrik Portalı</a><a href="/arama/">Teknik arama</a></nav></div></header><main class="wrap" id="ana-icerik"><article>{preview_banner}<header class="hero"><span class="eyebrow">AI destekli CMS · insan editör onayı · {html.escape(record["riskClass"])} risk</span><h1>{html.escape(record["h1"])}</h1><p class="lead">{html.escape(record["description"])}</p><div class="meta"><span>Son güncelleme: {html.escape(str(public_date)[:10])}</span><span>Kaynak sayısı: {len(record["sources"])}</span><span>Kalite puanı: {record["quality"]["score"]}/100</span></div></header><div class="answer"><strong>Doğrudan cevap</strong>{html.escape(record["directAnswer"])}{citation_html(primary_refs, source_numbers)}</div><div class="warning"><strong>Yayın yöntemi:</strong> AI destekli taslak insan editör onayıyla yayımlanmıştır. ALO186 bağımsız bilgilendirme platformudur; EDAŞ, EPDK, TEDAŞ, kamu kurumu, resmî başvuru kanalı veya ürün satıcısı değildir.</div><div class="layout"><div class="article">{''.join(sections)}<section class="faq" id="sss"><h2>Sık sorulan sorular</h2>{faq_html}</section><section id="ilgili"><h2>İlgili ücretsiz araç ve rehberler</h2><div class="buttons">{related_html}</div></section><section class="sources" id="kaynaklar"><h2>Kaynaklar ve doğrulama</h2><ol>{sources_html}</ol><p>Kaynak erişim tarihleri içerik kaydında izlenir. Güncellik sınırı risk sınıfına göre fail-closed kontrol edilir.</p></section></div><aside class="toc"><strong>İçindekiler</strong>{''.join(f'<a href="#{html.escape(section["id"])}">{html.escape(section["heading"])}</a>' for section in record["sections"])}<a href="#sss">Sık sorulanlar</a><a href="#kaynaklar">Kaynaklar</a></aside></div></article></main><footer class="footer"><div class="wrap"><strong>ALO186</strong><p>Elektrik çarpması, yangın, duman, ark veya düşmüş iletkende güvenli alana geçin ve 112’yi arayın. Dağıtım şebekesi arızalarında 186 veya bölgenizdeki resmî dağıtım şirketi kanalını kullanın.</p></div></footer></body></html>'''


def review_markdown(record: dict[str, Any], report: dict[str, Any], risk_notes: list[str] | None = None) -> str:
    checks = "\n".join(f"- {'✅' if passed else '❌'} {name}" for name, passed in report["checks"].items())
    sources = "\n".join(
        f"- **{source['id']} · {source['publisher']}** — [{source['title']}]({source['url']}) — erişim {source['accessedAt']} — {'birincil' if source['primary'] else 'ikincil'}"
        for source in record["sources"]
    )
    sections = "\n\n".join(
        f"## {section['heading']}\n\n" + "\n\n".join(section["paragraphs"]) + ("\n\n" + "\n".join(f"- {item}" for item in section["bullets"]) if section["bullets"] else "") + f"\n\n_Kaynaklar: {', '.join(section['sourceRefs'])}_"
        for section in record["sections"]
    )
    faqs = "\n\n".join(f"### {faq['question']}\n\n{faq['answer']}\n\n_Kaynaklar: {', '.join(faq['sourceRefs'])}_" for faq in record["faqs"])
    notes = "\n".join(f"- {item}" for item in (risk_notes or [])) or "- AI ek risk notu üretmedi."
    errors = "\n".join(f"- ❌ {item}" for item in report["errors"]) or "- Yok"
    warnings = "\n".join(f"- ⚠️ {item}" for item in report["warnings"]) or "- Yok"
    return f"""# ALO186 AI CMS inceleme paketi — {record['slug']}

> Bu dosya canonical yayına dahil edilmez. PR incelemesi ve insan onayı için üretilmiştir.

## Durum

- State: **{record['state']}**
- Risk: **{record['riskClass']}**
- Model: **{record['editorial']['model']}**
- Kalite: **{report['score']}/100**
- Benzerlik: **{report['similarity']['maximum']:.2f}** — {report['similarity']['closestPath'] or 'yakın sayfa yok'}
- Kelime: **{report['totalWords']}**

## Kalite kapıları

{checks}

### Hatalar

{errors}

### Uyarılar

{warnings}

## AI risk notları

{notes}

## Kaynaklar

{sources}

## SEO

- Title: `{record['title']}`
- H1: `{record['h1']}`
- Description: `{record['description']}`
- Canonical: `{record['seo']['canonicalPath']}`
- Birincil anahtar kelime: `{record['primaryKeyword']}`

## Doğrudan cevap

{record['directAnswer']}

{sections}

## Sık sorulan sorular

{faqs}

## İnsan onay komutu

PR sahibinin veya repository yetkilisinin yorumu:

```text
/cms approve {record['slug']}
```

Onay iş akışı kalite puanı, kaynak güncelliği, iç linkler, kanibalizasyon ve risk sınırlarını yeniden çalıştırmadan canonical dosya üretmez.
"""


def approve_record(record: dict[str, Any], reviewer: str, pr_number: int) -> dict[str, Any]:
    reviewer = reviewer.strip()
    if not reviewer or reviewer.casefold() in {"ai", "automation", "github-actions[bot]"} or reviewer.endswith("[bot]"):
        raise CmsError("İnsan editör onayı gerekir; bot/AI onayı kabul edilmez.")
    report = validate_record(record, write_quality=False)
    if report["errors"]:
        raise CmsError("Onay öncesi doğrulama başarısız:\n- " + "\n- ".join(report["errors"]))
    minimum = int(load_policy()["minimumQualityScore"])
    if report["score"] < minimum:
        raise CmsError(f"Kalite puanı {report['score']}; onay için minimum {minimum}.")
    record["state"] = "approved"
    record["editorial"]["approvedBy"] = reviewer
    record["editorial"]["approvedAt"] = utc_now()
    record["editorial"]["approvalPr"] = pr_number
    record["seo"]["lastModified"] = today()
    final_report = validate_record(record, write_quality=False)
    if final_report["errors"]:
        raise CmsError("Onay kaydı doğrulanamadı:\n- " + "\n- ".join(final_report["errors"]))
    return record


def next_routing_version() -> int:
    versions = []
    for path in [ROUTING_MANIFEST, *sorted(ROUTING_OVERLAYS.glob("*.json"))]:
        try:
            versions.append(int(read_json(path).get("version", 0)))
        except CmsError:
            continue
    return max(versions or [1]) + 1


def publish_record(record: dict[str, Any]) -> dict[str, Any]:
    if record["state"] != "approved":
        raise CmsError("Yalnız approved içerik yayımlanabilir.")
    report = validate_record(record, write_quality=False)
    if report["errors"]:
        raise CmsError("Yayın öncesi doğrulama başarısız:\n- " + "\n- ".join(report["errors"]))
    record["state"] = "published"
    record["editorial"]["publishedAt"] = utc_now()
    record["seo"]["lastModified"] = today()
    record["quality"] = {
        "score": report["score"],
        "minimumRequired": load_policy()["minimumQualityScore"],
        "checks": report["checks"],
        "similarity": report["similarity"],
    }
    target = PUBLISHED_ROOT / record["slug"] / "index.html"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_html(record), encoding="utf-8")
    overlay = {
        "version": next_routing_version(),
        "generatedAt": today(),
        "routes": [
            {
                "source": f"alo186/haberler/{record['slug']}/index.html",
                "canonicalPath": record["seo"]["canonicalPath"],
                "type": "article",
            }
        ],
        "aiCms": {
            "schemaVersion": 1,
            "contentId": record["id"],
            "humanApproved": True,
            "approvalPr": record["editorial"]["approvalPr"],
            "qualityScore": record["quality"]["score"],
        },
    }
    write_json(ROUTING_OVERLAYS / f"ai-cms-{record['slug']}.json", overlay)
    write_json(content_path(record["slug"]), record)
    preview = preview_path(record["slug"])
    if preview.exists():
        preview.unlink()
    final_report = validate_record(record, write_quality=False)
    if final_report["errors"]:
        raise CmsError("Yayın çıktısı doğrulanamadı:\n- " + "\n- ".join(final_report["errors"]))
    return {"record": record, "report": final_report, "target": str(target.relative_to(REPO_ROOT))}


def dashboard(output: Path) -> dict[str, Any]:
    rows = []
    for path in sorted(CONTENT_DIR.glob("*.json")):
        record = read_json(path)
        report = validate_record(record, write_quality=False)
        rows.append(
            {
                "slug": record["slug"],
                "state": record["state"],
                "risk": record["riskClass"],
                "score": report["score"],
                "ok": report["ok"],
                "errors": len(report["errors"]),
                "warnings": len(report["warnings"]),
                "sources": len(record["sources"]),
                "lastModified": record["seo"]["lastModified"],
            }
        )
    body = "".join(
        f"<tr><td>{html.escape(row['slug'])}</td><td>{html.escape(row['state'])}</td><td>{html.escape(row['risk'])}</td><td>{row['score']}</td><td>{'✅' if row['ok'] else '❌'}</td><td>{row['sources']}</td><td>{html.escape(row['lastModified'])}</td></tr>"
        for row in rows
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        f'''<!doctype html><html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>ALO186 AI CMS Dashboard</title><style>body{{font:16px system-ui;margin:2rem;color:#10213b}}table{{border-collapse:collapse;width:100%}}th,td{{padding:.7rem;border:1px solid #dbe3ed;text-align:left}}th{{background:#eef3f9}}.meta{{color:#56657a}}</style></head><body><h1>ALO186 AI CMS</h1><p class="meta">Bu dashboard yalnız workflow artifactı olarak üretilir; canlı site rotası değildir.</p><table><thead><tr><th>Slug</th><th>State</th><th>Risk</th><th>Kalite</th><th>Geçerli</th><th>Kaynak</th><th>Güncelleme</th></tr></thead><tbody>{body}</tbody></table></body></html>''',
        encoding="utf-8",
    )
    return {"records": len(rows), "invalid": sum(1 for row in rows if not row["ok"]), "rows": rows}


def cmd_new(args: argparse.Namespace) -> None:
    policy = load_policy()
    brief = make_brief(args, policy)
    errors = validate_brief(brief, policy, require_sources=False)
    if errors:
        raise CmsError("Brief doğrulaması başarısız:\n- " + "\n- ".join(errors))
    path = brief_path(brief["slug"])
    if path.exists() and not args.force:
        raise CmsError(f"Brief zaten var: {path}. --force olmadan üzerine yazılmaz.")
    if content_path(brief["slug"]).exists() and not args.force:
        raise CmsError("Aynı slug için içerik kaydı zaten var.")
    write_json(path, brief)
    print(json.dumps({"ok": True, "brief": str(path.relative_to(REPO_ROOT)), "id": brief["id"]}, ensure_ascii=False))


def cmd_ai_draft(args: argparse.Namespace) -> None:
    policy = load_policy()
    slug = ensure_slug(args.slug)
    brief = read_json(brief_path(slug))
    errors = validate_brief(brief, policy, require_sources=True)
    if errors:
        raise CmsError("AI taslağı öncesi brief doğrulaması başarısız:\n- " + "\n- ".join(errors))
    model = args.model or os.getenv("ALO186_AI_CMS_MODEL") or policy["defaultModel"]
    client = OpenAIResponsesClient(os.getenv("OPENAI_API_KEY", ""))
    draft = client.create_structured(
        model=model,
        instructions=PROMPT_PATH.read_text(encoding="utf-8"),
        prompt=ai_prompt(brief),
        schema=read_json(DRAFT_SCHEMA_PATH),
    )
    record = assemble_record(brief, draft, model)
    report = validate_record(record, write_quality=False)
    record["quality"] = {
        "score": report["score"],
        "minimumRequired": policy["minimumQualityScore"],
        "checks": report["checks"],
        "similarity": report["similarity"],
    }
    write_json(content_path(slug), record)
    REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    review_path(slug).write_text(review_markdown(record, report, draft.get("riskNotes", [])), encoding="utf-8")
    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    preview_path(slug).write_text(render_html(record, preview=True), encoding="utf-8")
    print(json.dumps({"ok": not report["errors"], "slug": slug, "model": model, "score": report["score"], "errors": report["errors"], "warnings": report["warnings"]}, ensure_ascii=False))


def cmd_validate(args: argparse.Namespace) -> None:
    paths = [content_path(ensure_slug(args.slug))] if args.slug else sorted(CONTENT_DIR.glob("*.json"))
    if not paths:
        print(json.dumps({"ok": True, "records": 0}, ensure_ascii=False))
        return
    reports = []
    failed = False
    for path in paths:
        record = read_json(path)
        report = validate_record(record, write_quality=args.write)
        reports.append({"slug": record["slug"], **report})
        failed = failed or bool(report["errors"])
    print(json.dumps({"ok": not failed, "records": len(reports), "reports": reports}, ensure_ascii=False, indent=2))
    if failed:
        raise SystemExit(1)


def cmd_review_pack(args: argparse.Namespace) -> None:
    slug = ensure_slug(args.slug)
    record = read_json(content_path(slug))
    report = validate_record(record, write_quality=args.write)
    REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    review_path(slug).write_text(review_markdown(record, report), encoding="utf-8")
    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    preview_path(slug).write_text(render_html(record, preview=True), encoding="utf-8")
    print(json.dumps({"ok": True, "review": str(review_path(slug).relative_to(REPO_ROOT)), "preview": str(preview_path(slug).relative_to(REPO_ROOT)), "score": report["score"]}, ensure_ascii=False))


def cmd_approve(args: argparse.Namespace) -> None:
    slug = ensure_slug(args.slug)
    record = read_json(content_path(slug))
    if record["state"] != "review":
        raise CmsError("Yalnız review durumundaki içerik onaylanabilir.")
    approved = approve_record(record, args.reviewer, args.pr)
    write_json(content_path(slug), approved)
    report = validate_record(approved, write_quality=True)
    review_path(slug).write_text(review_markdown(approved, report), encoding="utf-8")
    print(json.dumps({"ok": True, "slug": slug, "state": "approved", "score": report["score"], "approvalPr": args.pr}, ensure_ascii=False))


def cmd_publish(args: argparse.Namespace) -> None:
    slug = ensure_slug(args.slug)
    result = publish_record(read_json(content_path(slug)))
    print(json.dumps({"ok": True, "slug": slug, "state": "published", "score": result["report"]["score"], "target": result["target"]}, ensure_ascii=False))


def cmd_dashboard(args: argparse.Namespace) -> None:
    result = dashboard(Path(args.output))
    print(json.dumps(result, ensure_ascii=False, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ALO186 Git-native, kaynak bağlı ve insan onaylı AI CMS")
    sub = parser.add_subparsers(dest="command", required=True)

    new = sub.add_parser("new", help="Yeni içerik briefi oluştur")
    new.add_argument("--slug", required=True)
    new.add_argument("--title", required=True)
    new.add_argument("--topic", required=True)
    new.add_argument("--intent", required=True)
    new.add_argument("--primary-keyword", required=True)
    new.add_argument("--audience", required=True, help="Virgülle ayrılmış hedef kitle")
    new.add_argument("--risk-class", choices=["low", "medium", "high", "legal"], required=True)
    new.add_argument("--content-type", choices=["article", "guide"], default="article")
    new.add_argument("--sources-json", default="[]", help="JSON veya @dosya")
    new.add_argument("--internal-links-json", default="[]", help="JSON veya @dosya")
    new.add_argument("--commerce-category", default="")
    new.add_argument("--requested-by", default="github-workflow")
    new.add_argument("--force", action="store_true")
    new.set_defaults(func=cmd_new)

    draft = sub.add_parser("ai-draft", help="OpenAI Responses API ile kaynak bağlı taslak üret")
    draft.add_argument("--slug", required=True)
    draft.add_argument("--model", default="")
    draft.set_defaults(func=cmd_ai_draft)

    validate = sub.add_parser("validate", help="Bir veya bütün içerik kayıtlarını doğrula")
    validate.add_argument("--slug", default="")
    validate.add_argument("--write", action="store_true", help="Kalite sonucunu kayda yaz")
    validate.set_defaults(func=cmd_validate)

    review = sub.add_parser("review-pack", help="Markdown inceleme paketi ve noindex önizleme üret")
    review.add_argument("--slug", required=True)
    review.add_argument("--write", action="store_true")
    review.set_defaults(func=cmd_review_pack)

    approve = sub.add_parser("approve", help="İnsan editör onayını kaydet")
    approve.add_argument("--slug", required=True)
    approve.add_argument("--reviewer", required=True)
    approve.add_argument("--pr", required=True, type=int)
    approve.set_defaults(func=cmd_approve)

    publish = sub.add_parser("publish", help="Onaylı kaydı canonical HTML ve routing overlay olarak yayımla")
    publish.add_argument("--slug", required=True)
    publish.set_defaults(func=cmd_publish)

    dash = sub.add_parser("dashboard", help="Özel editorial dashboard artifactı üret")
    dash.add_argument("--output", default="/tmp/alo186-ai-cms-dashboard.html")
    dash.set_defaults(func=cmd_dashboard)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    try:
        args.func(args)
    except CmsError as exc:
        print(f"AI CMS hatası: {exc}", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
