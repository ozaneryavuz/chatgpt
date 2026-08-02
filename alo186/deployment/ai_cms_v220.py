from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import html
import json
import os
import re
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Iterable

VERSION = 220
CMS_ROOT = Path("alo186/cms")
CONFIG_PATH = CMS_ROOT / "config.json"
SOURCE_POLICY_PATH = CMS_ROOT / "source-policy.json"
CONTENT_SCHEMA_PATH = CMS_ROOT / "content-schema.json"
REQUESTS_DIR = CMS_ROOT / "requests"
DRAFTS_DIR = CMS_ROOT / "drafts"
APPROVED_DIR = CMS_ROOT / "approved"
ARCHIVE_DIR = CMS_ROOT / "archive"
PUBLICATION_LOG_PATH = CMS_ROOT / "publication-log.json"
PROMPT_PATH = CMS_ROOT / "prompts/editorial-system.txt"
API_ENDPOINT = "https://api.openai.com/v1/responses"
CANONICAL_HOST = "https://alo186.com"
DEFAULT_MODEL = "gpt-5-mini"

PERSON_SCHEMA_RE = re.compile(
    r'''(?:["']@type["']\s*:\s*["'](?:Person|ProfilePage)["']|/uzman/)''',
    re.IGNORECASE,
)
EMAIL_RE = re.compile(r"(?<![\w.+-])[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}(?![\w.-])", re.I)
PHONE_RE = re.compile(r"(?<!\d)(?:(?:\+90)|0)\s*\(?\d{3}\)?[\s.-]*\d{3}[\s.-]*\d{2}[\s.-]*\d{2}(?!\d)")
PRIVATE_KEY_RE = re.compile(r"(?:sk-[A-Za-z0-9_-]{20,}|BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY)")
TRACKING_QUERY_RE = re.compile(r"^(?:utm_|fbclid$|gclid$|ref$|tag$)", re.I)
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
REQUEST_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]{2,80}$")
ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

TURKISH_ASCII = str.maketrans(
    {"ç": "c", "ğ": "g", "ı": "i", "ö": "o", "ş": "s", "ü": "u",
     "Ç": "c", "Ğ": "g", "İ": "i", "Ö": "o", "Ş": "s", "Ü": "u"}
)

ARTICLE_OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "title", "meta_description", "slug", "search_intent", "audience",
        "risk_level", "commercial_intent", "direct_answer", "safety_notice",
        "sections", "checklist", "faq", "sources", "editorial_notes",
    ],
    "properties": {
        "title": {"type": "string", "minLength": 20, "maxLength": 90},
        "meta_description": {"type": "string", "minLength": 70, "maxLength": 170},
        "slug": {"type": "string", "pattern": "^[a-z0-9]+(?:-[a-z0-9]+)*$"},
        "search_intent": {"type": "string", "minLength": 10, "maxLength": 180},
        "audience": {"type": "string", "minLength": 3, "maxLength": 120},
        "risk_level": {"type": "string", "enum": ["low", "medium", "high"]},
        "commercial_intent": {"type": "string", "enum": ["none", "informational", "comparison"]},
        "direct_answer": {"type": "string", "minLength": 180, "maxLength": 900},
        "safety_notice": {"type": "string", "minLength": 80, "maxLength": 700},
        "sections": {
            "type": "array", "minItems": 3, "maxItems": 10,
            "items": {
                "type": "object", "additionalProperties": False,
                "required": ["heading", "body"],
                "properties": {
                    "heading": {"type": "string", "minLength": 4, "maxLength": 100},
                    "body": {"type": "string", "minLength": 120, "maxLength": 2500},
                },
            },
        },
        "checklist": {
            "type": "array", "minItems": 3, "maxItems": 12,
            "items": {"type": "string", "minLength": 10, "maxLength": 280},
        },
        "faq": {
            "type": "array", "minItems": 3, "maxItems": 8,
            "items": {
                "type": "object", "additionalProperties": False,
                "required": ["question", "answer"],
                "properties": {
                    "question": {"type": "string", "minLength": 10, "maxLength": 180},
                    "answer": {"type": "string", "minLength": 60, "maxLength": 700},
                },
            },
        },
        "sources": {
            "type": "array", "minItems": 2, "maxItems": 12,
            "items": {
                "type": "object", "additionalProperties": False,
                "required": ["title", "publisher", "url", "source_type", "supports"],
                "properties": {
                    "title": {"type": "string", "minLength": 5, "maxLength": 240},
                    "publisher": {"type": "string", "minLength": 2, "maxLength": 160},
                    "url": {"type": "string", "minLength": 12, "maxLength": 600},
                    "source_type": {
                        "type": "string",
                        "enum": ["official", "regulation", "standard", "manufacturer", "academic"],
                    },
                    "supports": {"type": "string", "minLength": 10, "maxLength": 300},
                },
            },
        },
        "editorial_notes": {
            "type": "array", "minItems": 1, "maxItems": 12,
            "items": {"type": "string", "minLength": 5, "maxLength": 400},
        },
    },
}


class CmsError(RuntimeError):
    pass


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def today() -> str:
    return dt.date.today().isoformat()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise CmsError(f"Dosya bulunamadı: {path}") from exc
    except json.JSONDecodeError as exc:
        raise CmsError(f"Geçersiz JSON ({path}): {exc}") from exc


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=False) + "\n"
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
        handle.write(rendered)
        temporary = Path(handle.name)
    temporary.replace(path)


def load_config(repo_root: Path) -> dict[str, Any]:
    config = read_json(repo_root / CONFIG_PATH)
    if config.get("cmsVersion") != VERSION:
        raise CmsError(f"CMS sürümü yanlış: {config.get('cmsVersion')}; beklenen={VERSION}")
    if config.get("workflow", {}).get("autoPublish") is not False:
        raise CmsError("AI CMS autoPublish=false olmak zorunda")
    privacy = config.get("privacy", {})
    if privacy.get("personalProfilesAllowed") is not False:
        raise CmsError("AI CMS kişisel profil yayımlayamaz")
    if privacy.get("personalContactAllowed") is not False:
        raise CmsError("AI CMS kişisel iletişim bilgisi yayımlayamaz")
    schema = read_json(repo_root / CONTENT_SCHEMA_PATH)
    if schema.get("x-alo186-cms-version") != VERSION or schema.get("additionalProperties") is not False:
        raise CmsError("AI CMS içerik şeması sürüm veya kapalılık sözleşmesini ihlal ediyor")
    return config


def load_source_policy(repo_root: Path) -> dict[str, Any]:
    policy = read_json(repo_root / SOURCE_POLICY_PATH)
    if policy.get("version") != VERSION:
        raise CmsError("Kaynak politikası sürümü CMS ile aynı olmalı")
    return policy


def slugify(value: str) -> str:
    value = value.translate(TURKISH_ASCII).casefold()
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    value = re.sub(r"-+", "-", value)
    return value[:90].strip("-")


def canonical_path(slug: str) -> str:
    return f"/haberler/{slug}"


def iter_strings(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for key, item in value.items():
            yield str(key)
            yield from iter_strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from iter_strings(item)


def privacy_findings(value: Any) -> list[str]:
    joined = "\n".join(iter_strings(value))
    if not isinstance(value, str):
        joined += "\n" + json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    findings: list[str] = []
    if PERSON_SCHEMA_RE.search(joined):
        findings.append("Person/ProfilePage veya /uzman/ ifadesi")
    if EMAIL_RE.search(joined):
        findings.append("e-posta adresi")
    if PHONE_RE.search(joined):
        findings.append("kişisel telefon numarası")
    if PRIVATE_KEY_RE.search(joined):
        findings.append("gizli anahtar veya özel anahtar")
    forbidden_keys = {"author_name", "reviewer_name", "person", "profile", "personal_email", "personal_phone"}
    if isinstance(value, dict):
        stack = [value]
        while stack:
            current = stack.pop()
            for key, item in current.items():
                if str(key).casefold() in forbidden_keys:
                    findings.append(f"yasak kişisel alan: {key}")
                if isinstance(item, dict):
                    stack.append(item)
                elif isinstance(item, list):
                    stack.extend(child for child in item if isinstance(child, dict))
    return sorted(set(findings))


def clean_source_url(raw_url: str) -> str:
    parsed = urllib.parse.urlsplit(raw_url.strip())
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise CmsError(f"Kaynak URL http/https olmalı: {raw_url}")
    if parsed.username or parsed.password:
        raise CmsError(f"Kaynak URL kimlik bilgisi taşıyamaz: {raw_url}")
    query = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
    clean_query = [(key, value) for key, value in query if not TRACKING_QUERY_RE.search(key)]
    return urllib.parse.urlunsplit(
        (parsed.scheme.casefold(), parsed.netloc.casefold(), parsed.path or "/", urllib.parse.urlencode(clean_query), "")
    )


def domain_allowed(url: str, source_type: str, policy: dict[str, Any]) -> bool:
    host = (urllib.parse.urlsplit(url).hostname or "").casefold().rstrip(".")
    if not host:
        return False
    if source_type in {"official", "regulation"}:
        suffixes = [str(item).casefold() for item in policy.get("officialDomainSuffixes", [])]
        exact = [str(item).casefold() for item in policy.get("officialDomains", [])]
        return host in exact or any(host == suffix.lstrip(".") or host.endswith(suffix) for suffix in suffixes)
    if source_type == "academic":
        suffixes = [str(item).casefold() for item in policy.get("academicDomainSuffixes", [])]
        return any(host == suffix.lstrip(".") or host.endswith(suffix) for suffix in suffixes)
    if source_type in {"standard", "manufacturer"}:
        return bool(host) and not host.endswith(("amazon.com.tr", "amazon.com", "hepsiburada.com", "trendyol.com"))
    return False


def validate_request(record: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {"request_id", "status", "topic", "primary_question", "audience", "objective", "risk_level", "commercial_intent"}
    missing = sorted(required - set(record))
    if missing:
        errors.append("eksik alanlar: " + ", ".join(missing))
    request_id = str(record.get("request_id", ""))
    if request_id and not REQUEST_ID_RE.fullmatch(request_id):
        errors.append("request_id küçük harf, sayı ve tire içermeli")
    if record.get("status") not in {"idea", "research", "cancelled"}:
        errors.append("istek durumu idea/research/cancelled olmalı")
    if record.get("risk_level") not in {"low", "medium", "high"}:
        errors.append("risk_level low/medium/high olmalı")
    if record.get("commercial_intent") not in {"none", "informational", "comparison"}:
        errors.append("commercial_intent geçersiz")
    if len(str(record.get("primary_question", "")).strip()) < 10:
        errors.append("primary_question çok kısa")
    findings = privacy_findings(record)
    errors.extend(f"gizlilik ihlali: {item}" for item in findings)
    return errors


def validate_article(
    record: dict[str, Any],
    config: dict[str, Any],
    policy: dict[str, Any],
    *,
    publishable: bool,
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    required = {
        "cms_version", "request_id", "status", "content_type", "language", "slug",
        "canonical_path", "title", "meta_description", "search_intent", "audience",
        "risk_level", "commercial_intent", "direct_answer", "safety_notice", "sections",
        "checklist", "faq", "sources", "editorial", "generation",
    }
    missing = sorted(required - set(record))
    if missing:
        errors.append("eksik alanlar: " + ", ".join(missing))
        return errors, warnings
    if record.get("cms_version") != VERSION:
        errors.append("cms_version yanlış")
    if record.get("content_type") != "article":
        errors.append("v220 yalnız article derler")
    if record.get("language") != "tr-TR":
        errors.append("language tr-TR olmalı")
    slug = str(record.get("slug", ""))
    if not SLUG_RE.fullmatch(slug):
        errors.append("slug geçersiz")
    if record.get("canonical_path") != canonical_path(slug):
        errors.append("canonical_path slug ile uyumsuz")
    status = record.get("status")
    if status not in {"draft", "approved", "rejected", "published"}:
        errors.append("içerik durumu geçersiz")
    if publishable and status != "approved":
        errors.append("derleme için status=approved gerekli")
    title = str(record.get("title", "")).strip()
    meta = str(record.get("meta_description", "")).strip()
    answer = str(record.get("direct_answer", "")).strip()
    safety = str(record.get("safety_notice", "")).strip()
    if not 20 <= len(title) <= 90:
        errors.append("title 20-90 karakter olmalı")
    if not 70 <= len(meta) <= 170:
        errors.append("meta_description 70-170 karakter olmalı")
    if not 180 <= len(answer) <= 900:
        errors.append("direct_answer 180-900 karakter olmalı")
    if not 80 <= len(safety) <= 700:
        errors.append("safety_notice 80-700 karakter olmalı")
    if record.get("risk_level") not in {"low", "medium", "high"}:
        errors.append("risk_level geçersiz")
    if record.get("commercial_intent") not in {"none", "informational", "comparison"}:
        errors.append("commercial_intent geçersiz")
    sections = record.get("sections")
    if not isinstance(sections, list) or not 3 <= len(sections) <= 10:
        errors.append("sections 3-10 öğe olmalı")
    else:
        for index, section in enumerate(sections, 1):
            if not isinstance(section, dict) or len(str(section.get("heading", "")).strip()) < 4 or len(str(section.get("body", "")).strip()) < 120:
                errors.append(f"section {index} eksik/kısa")
    checklist = record.get("checklist")
    if not isinstance(checklist, list) or not 3 <= len(checklist) <= 12:
        errors.append("checklist 3-12 öğe olmalı")
    faq = record.get("faq")
    if not isinstance(faq, list) or not 3 <= len(faq) <= 8:
        errors.append("faq 3-8 öğe olmalı")
    else:
        for index, item in enumerate(faq, 1):
            if not isinstance(item, dict) or len(str(item.get("question", "")).strip()) < 10 or len(str(item.get("answer", "")).strip()) < 60:
                errors.append(f"faq {index} eksik/kısa")
    sources = record.get("sources")
    minimum_sources = int(config.get("quality", {}).get("minimumSources", 2))
    if not isinstance(sources, list):
        errors.append("sources liste olmalı")
        sources = []
    if len(sources) < minimum_sources:
        target = errors if publishable else warnings
        target.append(f"en az {minimum_sources} kaynak gerekli")
    clean_urls: set[str] = set()
    official_count = 0
    for index, source in enumerate(sources, 1):
        if not isinstance(source, dict):
            errors.append(f"source {index} nesne olmalı")
            continue
        try:
            normalized = clean_source_url(str(source.get("url", "")))
        except CmsError as exc:
            errors.append(f"source {index}: {exc}")
            continue
        if normalized in clean_urls:
            errors.append(f"source {index}: yinelenen URL")
        clean_urls.add(normalized)
        source["url"] = normalized
        source_type = str(source.get("source_type", ""))
        if source_type in {"official", "regulation"}:
            official_count += 1
        if not domain_allowed(normalized, source_type, policy):
            target = errors if publishable else warnings
            target.append(f"source {index}: alan adı kaynak politikasına uymuyor")
        if len(str(source.get("supports", "")).strip()) < 10:
            errors.append(f"source {index}: supports alanı kısa")
    if publishable and record.get("risk_level") in {"medium", "high"} and official_count < 1:
        errors.append("orta/yüksek riskli içerikte en az bir resmî veya mevzuat kaynağı gerekli")
    editorial = record.get("editorial")
    if not isinstance(editorial, dict):
        errors.append("editorial nesnesi eksik")
    else:
        if publishable and editorial.get("approval_state") != "approved":
            errors.append("approval_state=approved gerekli")
        if publishable and editorial.get("approval_scope") != "institutional":
            errors.append("approval_scope=institutional gerekli")
        if publishable and editorial.get("evidence_complete") is not True:
            errors.append("evidence_complete=true gerekli")
        for date_field in ("created_at", "reviewed_at"):
            value = str(editorial.get(date_field, ""))
            if value and not ISO_DATE_RE.fullmatch(value):
                errors.append(f"editorial.{date_field} YYYY-MM-DD olmalı")
    generation = record.get("generation")
    if not isinstance(generation, dict):
        errors.append("generation nesnesi eksik")
    elif generation.get("personal_data_used") is not False:
        errors.append("generation.personal_data_used=false olmalı")
    findings = privacy_findings(record)
    errors.extend(f"gizlilik ihlali: {item}" for item in findings)
    joined = "\n".join(iter_strings(record))
    forbidden_claims = config.get("quality", {}).get("forbiddenClaims", [])
    for claim in forbidden_claims:
        if str(claim).casefold() in joined.casefold():
            errors.append(f"yasak iddia: {claim}")
    return sorted(set(errors)), sorted(set(warnings))


def build_user_prompt(request_record: dict[str, Any], policy: dict[str, Any]) -> str:
    trusted = {
        "officialDomains": policy.get("officialDomains", []),
        "officialDomainSuffixes": policy.get("officialDomainSuffixes", []),
        "academicDomainSuffixes": policy.get("academicDomainSuffixes", []),
    }
    return (
        "ALO186 için aşağıdaki içerik isteğini araştır ve yapılandırılmış bir teknik makale taslağı üret.\n"
        "Kullanıcı güvenliği, resmî kaynak ayrımı ve uygulanabilir karar desteği önceliklidir.\n"
        "Kişisel isim, kişisel profil, e-posta, telefon veya açık adres kullanma.\n"
        "Fiyat, stok, puan, teslimat ve kesin sonuç iddiası üretme.\n"
        "Her kaynak için hangi iddiayı desteklediğini 'supports' alanında açıkla.\n"
        "Resmî veya birincil kaynak bulamıyorsan bunu editorial_notes içinde açıkça belirt.\n\n"
        f"İÇERİK İSTEĞİ:\n{json.dumps(request_record, ensure_ascii=False, indent=2)}\n\n"
        f"KAYNAK POLİTİKASI ÖZETİ:\n{json.dumps(trusted, ensure_ascii=False, indent=2)}"
    )


def extract_output_text(response: dict[str, Any]) -> str:
    direct = response.get("output_text")
    if isinstance(direct, str) and direct.strip():
        return direct.strip()
    chunks: list[str] = []
    for item in response.get("output", []):
        if not isinstance(item, dict):
            continue
        for content in item.get("content", []):
            if isinstance(content, dict) and content.get("type") == "output_text":
                text_value = content.get("text")
                if isinstance(text_value, str):
                    chunks.append(text_value)
    if not chunks:
        raise CmsError("OpenAI yanıtında yapılandırılmış metin bulunamadı")
    return "\n".join(chunks).strip()


def extract_citation_urls(response: Any) -> list[str]:
    found: set[str] = set()
    if isinstance(response, dict):
        if response.get("type") == "url_citation" and isinstance(response.get("url"), str):
            try:
                found.add(clean_source_url(response["url"]))
            except CmsError:
                pass
        for value in response.values():
            found.update(extract_citation_urls(value))
    elif isinstance(response, list):
        for value in response:
            found.update(extract_citation_urls(value))
    return sorted(found)


def call_openai(
    request_record: dict[str, Any],
    system_prompt: str,
    policy: dict[str, Any],
    *,
    model: str,
    api_key: str,
    endpoint: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    payload = {
        "model": model,
        "instructions": system_prompt,
        "input": [
            {
                "role": "user",
                "content": [{"type": "input_text", "text": build_user_prompt(request_record, policy)}],
            }
        ],
        "tools": [{"type": "web_search"}],
        "text": {
            "format": {
                "type": "json_schema",
                "name": "alo186_article_draft",
                "description": "ALO186 için kaynaklı, güvenlik sınırlı ve kurumsal incelemeye hazır makale taslağı",
                "strict": True,
                "schema": ARTICLE_OUTPUT_SCHEMA,
            }
        },
    }
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        endpoint,
        data=data,
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": f"ALO186-AI-CMS/{VERSION}",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=180) as response_handle:
            response = json.loads(response_handle.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")[:2000]
        raise CmsError(f"OpenAI API HTTP {exc.code}: {body}") from exc
    except urllib.error.URLError as exc:
        raise CmsError(f"OpenAI API bağlantı hatası: {exc}") from exc
    try:
        generated = json.loads(extract_output_text(response))
    except json.JSONDecodeError as exc:
        raise CmsError(f"OpenAI yapılandırılmış çıktı JSON değil: {exc}") from exc
    meta = {
        "response_id": response.get("id"),
        "model": response.get("model", model),
        "status": response.get("status"),
        "citation_urls": extract_citation_urls(response),
        "usage": response.get("usage", {}),
    }
    return generated, meta


def scaffold_from_request(request_record: dict[str, Any]) -> dict[str, Any]:
    topic = str(request_record["topic"]).strip()
    question = str(request_record["primary_question"]).strip()
    slug = slugify(str(request_record.get("preferred_slug") or topic))
    direct = (
        f"{question} sorusunun güvenli ve doğrulanmış cevabı için sistem türü, kurulu güç, koruma düzeni ve resmî işlem kanalı birlikte değerlendirilmelidir. "
        "Bu çevrimdışı taslak yalnız editoryal iskelet oluşturur; teknik değerler ve uygulanabilir sonuçlar birincil kaynaklarla doğrulanmadan yayımlanamaz."
    )
    return {
        "title": topic[:90],
        "meta_description": (
            f"{topic} konusunda güvenli karar adımları, doğrulanması gereken teknik veriler, resmî kaynaklar ve uygulanabilir kontrol listesi."
        )[:170],
        "slug": slug,
        "search_intent": question,
        "audience": request_record["audience"],
        "risk_level": request_record["risk_level"],
        "commercial_intent": request_record["commercial_intent"],
        "direct_answer": direct,
        "safety_notice": (
            "Bu taslak uzaktan arıza teşhisi veya saha uygulama talimatı değildir. Elektrik çarpması, duman, aktif ark, yanık kokusu veya kopmuş iletken varsa yaklaşmadan güvenli alana geçilmeli ve uygun acil/resmî kanal kullanılmalıdır."
        ),
        "sections": [
            {"heading": "Sorunu doğru sınıflandırma", "body": "Bu bölüm kullanıcı belirtisini, şebeke işlemini, sabit tesisat riskini ve ürün seçimini birbirinden ayıracak kaynaklı açıklamalarla tamamlanmalıdır."},
            {"heading": "Kontrol edilmesi gereken teknik veriler", "body": "Bu bölüm kurulu güç, yük profili, koruma cihazları, ölçüm sonuçları ve üretici sınırları gibi karar için gerekli verileri açıklamalıdır."},
            {"heading": "Güvenli sonraki adım", "body": "Bu bölüm kullanıcıya hangi durumda resmî kuruma, hangi durumda yetkili uzmana ve hangi durumda yalnız hazırlık kontrol listesine yönelmesi gerektiğini anlatmalıdır."},
        ],
        "checklist": [
            "Can güvenliği riski olup olmadığını kontrol edin.",
            "Resmî işlem gerekiyorsa ilgili kurumun güncel kanalını doğrulayın.",
            "Sabit tesisat veya pano müdahalesini yetkili uzmana bırakın.",
        ],
        "faq": [
            {"question": "Bu taslak doğrudan uygulanabilir mi?", "answer": "Hayır. Çevrimdışı iskelet, kaynak ve kurumsal inceleme tamamlanmadan yayınlanamaz veya saha talimatı olarak kullanılamaz."},
            {"question": "Hangi kaynaklar kullanılmalı?", "answer": "Öncelikle mevzuat, resmî kurum, dağıtım şirketi, standart ve üretici teknik dokümanları kullanılmalıdır."},
            {"question": "Ürün bağlantısı otomatik eklenir mi?", "answer": "Hayır. AI CMS v220 fiyat, stok, puan veya affiliate bağlantısı üretmez; ticari yönlendirme ayrı güvenlik kontrolünden geçer."},
        ],
        "sources": [],
        "editorial_notes": ["Çevrimdışı iskelet: kaynak araştırması ve teknik doğrulama eksik."],
    }


def wrap_generated(
    request_record: dict[str, Any],
    generated: dict[str, Any],
    *,
    model: str,
    provider_mode: str,
    response_meta: dict[str, Any] | None,
    prompt_hash: str,
) -> dict[str, Any]:
    slug = slugify(str(generated.get("slug") or request_record.get("preferred_slug") or request_record["topic"]))
    sources = generated.get("sources", [])
    citation_urls = (response_meta or {}).get("citation_urls", [])
    source_urls: list[str] = []
    for source in sources if isinstance(sources, list) else []:
        if isinstance(source, dict) and isinstance(source.get("url"), str):
            try:
                source["url"] = clean_source_url(source["url"])
                source["verified_at"] = today()
                source_urls.append(source["url"])
            except CmsError:
                pass
    citation_hosts = {urllib.parse.urlsplit(url).netloc for url in citation_urls}
    source_hosts = {urllib.parse.urlsplit(url).netloc for url in source_urls}
    evidence_complete = (
        provider_mode == "api"
        and bool(source_urls)
        and bool(citation_urls)
        and source_hosts.issubset(citation_hosts)
    )
    return {
        "cms_version": VERSION,
        "request_id": request_record["request_id"],
        "status": "draft",
        "content_type": "article",
        "language": "tr-TR",
        "slug": slug,
        "canonical_path": canonical_path(slug),
        "title": generated.get("title", ""),
        "meta_description": generated.get("meta_description", ""),
        "search_intent": generated.get("search_intent", request_record["primary_question"]),
        "audience": generated.get("audience", request_record["audience"]),
        "risk_level": generated.get("risk_level", request_record["risk_level"]),
        "commercial_intent": generated.get("commercial_intent", request_record["commercial_intent"]),
        "direct_answer": generated.get("direct_answer", ""),
        "safety_notice": generated.get("safety_notice", ""),
        "sections": generated.get("sections", []),
        "checklist": generated.get("checklist", []),
        "faq": generated.get("faq", []),
        "sources": sources,
        "editorial": {
            "approval_state": "pending",
            "approval_scope": "institutional",
            "evidence_complete": evidence_complete,
            "created_at": today(),
            "reviewed_at": "",
            "review_notes": generated.get("editorial_notes", []),
            "auto_publish": False,
        },
        "generation": {
            "provider": "openai-responses" if provider_mode == "api" else "offline-scaffold",
            "model": model,
            "generated_at": utc_now(),
            "response_id": (response_meta or {}).get("response_id"),
            "prompt_sha256": prompt_hash,
            "web_search_requested": provider_mode == "api",
            "citation_urls": citation_urls,
            "personal_data_used": False,
            "affiliate_links_generated": False,
        },
    }


def generate(
    repo_root: Path,
    request_path: Path,
    output_path: Path | None,
    *,
    model: str,
    offline_scaffold: bool,
) -> dict[str, Any]:
    config = load_config(repo_root)
    policy = load_source_policy(repo_root)
    request_record = read_json(request_path)
    request_errors = validate_request(request_record)
    if request_errors:
        raise CmsError("İçerik isteği geçersiz: " + "; ".join(request_errors))
    if request_record.get("status") == "cancelled":
        raise CmsError("İptal edilmiş istek üretilemez")
    system_prompt = (repo_root / PROMPT_PATH).read_text(encoding="utf-8")
    prompt_hash = sha256_text(system_prompt + "\n" + build_user_prompt(request_record, policy))
    response_meta: dict[str, Any] | None = None
    if offline_scaffold:
        generated = scaffold_from_request(request_record)
        provider_mode = "offline"
    else:
        api_key = os.environ.get(config.get("provider", {}).get("apiKeyEnv", "OPENAI_API_KEY"), "").strip()
        if not api_key:
            raise CmsError("OPENAI_API_KEY tanımlı değil; çevrimdışı iskelet için --offline-scaffold kullanın")
        endpoint = os.environ.get("OPENAI_BASE_URL", config.get("provider", {}).get("endpoint", API_ENDPOINT)).rstrip("/")
        if endpoint.endswith("/v1"):
            endpoint += "/responses"
        elif not endpoint.endswith("/responses"):
            endpoint += "/v1/responses" if endpoint == "https://api.openai.com" else "/responses"
        generated, response_meta = call_openai(
            request_record, system_prompt, policy, model=model, api_key=api_key, endpoint=endpoint
        )
        provider_mode = "api"
    wrapped = wrap_generated(
        request_record,
        generated,
        model=model,
        provider_mode=provider_mode,
        response_meta=response_meta,
        prompt_hash=prompt_hash,
    )
    errors, warnings = validate_article(wrapped, config, policy, publishable=False)
    if errors:
        raise CmsError("Üretilen taslak geçersiz: " + "; ".join(errors))
    target = output_path or (repo_root / DRAFTS_DIR / f"{request_record['request_id']}.json")
    write_json(target, wrapped)
    return {
        "ok": True,
        "cmsVersion": VERSION,
        "mode": provider_mode,
        "requestId": request_record["request_id"],
        "draft": target.relative_to(repo_root).as_posix() if target.is_relative_to(repo_root) else str(target),
        "warnings": warnings,
        "evidenceComplete": wrapped["editorial"]["evidence_complete"],
        "autoPublished": False,
    }


def paragraphs(text: str) -> str:
    blocks = [part.strip() for part in re.split(r"\n{2,}", text) if part.strip()]
    return "\n".join(f"<p>{html.escape(block)}</p>" for block in blocks)


def render_article(record: dict[str, Any]) -> str:
    canonical = CANONICAL_HOST + record["canonical_path"]
    published = record["editorial"].get("created_at") or today()
    modified = record["editorial"].get("reviewed_at") or published
    section_html = "\n".join(
        f'<section id="bolum-{index}"><h2>{html.escape(section["heading"])}</h2>{paragraphs(section["body"])}</section>'
        for index, section in enumerate(record["sections"], 1)
    )
    checklist_html = "\n".join(f"<li>{html.escape(item)}</li>" for item in record["checklist"])
    faq_html = "\n".join(
        f'<details><summary>{html.escape(item["question"])}</summary><p>{html.escape(item["answer"])}</p></details>'
        for item in record["faq"]
    )
    source_html = "\n".join(
        f'<li><a href="{html.escape(source["url"], quote=True)}" rel="noopener noreferrer" target="_blank">{html.escape(source["title"])}</a>'
        f' <span>— {html.escape(source["publisher"])}; doğrulama: {html.escape(source.get("verified_at", modified))}</span>'
        f'<br><small>Desteklediği husus: {html.escape(source["supports"])}</small></li>'
        for source in record["sources"]
    )
    faq_entities = [
        {"@type": "Question", "name": item["question"],
         "acceptedAnswer": {"@type": "Answer", "text": item["answer"]}}
        for item in record["faq"]
    ]
    schema = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "Article", "@id": canonical + "#article", "url": canonical,
                "headline": record["title"], "description": record["meta_description"],
                "inLanguage": "tr-TR", "datePublished": published, "dateModified": modified,
                "author": {"@type": "Organization", "@id": CANONICAL_HOST + "/#organization", "name": "ALO186"},
                "publisher": {"@type": "Organization", "@id": CANONICAL_HOST + "/#organization", "name": "ALO186"},
                "mainEntityOfPage": {"@type": "WebPage", "@id": canonical + "#webpage"},
                "citation": [source["url"] for source in record["sources"]],
            },
            {
                "@type": "BreadcrumbList", "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "ALO186", "item": CANONICAL_HOST + "/elektrik-portali"},
                    {"@type": "ListItem", "position": 2, "name": "Teknik rehberler", "item": CANONICAL_HOST + "/haberler"},
                    {"@type": "ListItem", "position": 3, "name": record["title"], "item": canonical},
                ],
            },
            {"@type": "FAQPage", "mainEntity": faq_entities},
        ],
    }
    return f'''<!doctype html>
<html lang="tr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{html.escape(record["title"])}</title>
  <meta name="description" content="{html.escape(record["meta_description"], quote=True)}">
  <meta name="robots" content="index,follow,max-image-preview:large">
  <meta name="generator" content="ALO186 AI CMS v{VERSION}; institutional review required">
  <link rel="canonical" href="{canonical}">
  <link rel="stylesheet" href="/haberler/alo186-article.css">
  <script type="application/ld+json">{json.dumps(schema, ensure_ascii=False, separators=(",", ":"))}</script>
</head>
<body data-ai-cms-version="{VERSION}" data-ai-cms-approved="true">
<a class="skip-link" href="#icerik">İçeriğe geç</a>
<header class="site-header"><a href="/elektrik-portali" aria-label="ALO186 ana sayfa">ALO186</a></header>
<main id="icerik" class="article-shell">
  <nav aria-label="Sayfa yolu"><a href="/elektrik-portali">Ana sayfa</a> / Teknik rehber</nav>
  <article>
    <p class="eyebrow">Kurumsal olarak doğrulanmış teknik rehber</p>
    <h1>{html.escape(record["title"])}</h1>
    <p class="article-meta">Yayın: {published} · Son kurumsal kontrol: {modified} · Risk seviyesi: {html.escape(record["risk_level"])}</p>
    <section class="direct-answer" aria-labelledby="dogrudan-cevap">
      <h2 id="dogrudan-cevap">Doğrudan cevap</h2>
      {paragraphs(record["direct_answer"])}
    </section>
    <aside class="safety-notice" aria-label="Güvenlik sınırı"><strong>Güvenlik sınırı:</strong> {html.escape(record["safety_notice"])}</aside>
    {section_html}
    <section id="kontrol-listesi"><h2>Uygulanabilir kontrol listesi</h2><ul>{checklist_html}</ul></section>
    <section id="sik-sorulan-sorular"><h2>Sık sorulan sorular</h2>{faq_html}</section>
    <section id="kaynaklar"><h2>Kaynaklar ve doğrulama kapsamı</h2><ol>{source_html}</ol></section>
    <aside class="editorial-note"><strong>Yayın ilkesi:</strong> Bu içerik kişisel profil kullanılmadan, kurumsal kaynak ve güvenlik kontrolüyle yayımlanmıştır. Fiyat, stok, puan veya otomatik affiliate bağlantısı üretilmemiştir. <a href="/kaynaklar">Kaynak yaklaşımı</a></aside>
  </article>
</main>
<footer><p>ALO186 bağımsız bilgilendirme platformudur; EDAŞ veya kamu kurumu değildir.</p></footer>
</body>
</html>
'''


def publication_log(repo_root: Path) -> dict[str, Any]:
    path = repo_root / PUBLICATION_LOG_PATH
    if path.is_file():
        payload = read_json(path)
        if not isinstance(payload, dict) or not isinstance(payload.get("entries"), list):
            raise CmsError("publication-log.json geçersiz")
        if payload.get("cmsVersion") != VERSION:
            raise CmsError("publication-log.json CMS sürümü yanlış")
        return payload
    return {"cmsVersion": VERSION, "entries": []}


def compile_article(repo_root: Path, article_path: Path, *, force: bool = False) -> dict[str, Any]:
    config = load_config(repo_root)
    policy = load_source_policy(repo_root)
    record = read_json(article_path)
    errors, warnings = validate_article(record, config, policy, publishable=True)
    if errors:
        raise CmsError("Onaylı içerik derlenemedi: " + "; ".join(errors))
    slug = record["slug"]
    page_path = repo_root / "alo186/haberler" / slug / "index.html"
    overlay_path = repo_root / "alo186/deployment/routing-overlays" / f"ai-cms-{slug}-v{VERSION}.json"
    if (page_path.exists() or overlay_path.exists()) and not force:
        raise CmsError(f"Hedef zaten var; üzerine yazmak için --force gerekli: {slug}")
    rendered = render_article(record)
    if privacy_findings(rendered):
        raise CmsError("Derlenen HTML gizlilik kapısından geçemedi")
    page_path.parent.mkdir(parents=True, exist_ok=True)
    page_path.write_text(rendered, encoding="utf-8")
    overlay = {
        "version": VERSION,
        "generatedAt": today(),
        "routes": [{
            "source": f"alo186/haberler/{slug}/index.html",
            "canonicalPath": record["canonical_path"],
            "type": "article",
        }],
        "aiCms": {
            "requestId": record["request_id"],
            "approvalScope": "institutional",
            "autoPublished": False,
            "personalProfilePublished": False,
            "affiliateLinksGenerated": False,
            "contentSha256": sha256_text(rendered),
        },
    }
    write_json(overlay_path, overlay)
    log = publication_log(repo_root)
    log["cmsVersion"] = VERSION
    entries = [item for item in log["entries"] if item.get("slug") != slug]
    entries.append({
        "request_id": record["request_id"],
        "slug": slug,
        "canonical_path": record["canonical_path"],
        "compiled_at": utc_now(),
        "content_sha256": sha256_text(rendered),
        "source_count": len(record["sources"]),
        "approval_scope": "institutional",
        "auto_published": False,
        "personal_profile_published": False,
    })
    log["entries"] = sorted(entries, key=lambda item: item["slug"])
    write_json(repo_root / PUBLICATION_LOG_PATH, log)
    return {
        "ok": True,
        "cmsVersion": VERSION,
        "page": page_path.relative_to(repo_root).as_posix(),
        "overlay": overlay_path.relative_to(repo_root).as_posix(),
        "canonical": CANONICAL_HOST + record["canonical_path"],
        "warnings": warnings,
        "autoPublished": False,
    }


def validate_repository(repo_root: Path) -> dict[str, Any]:
    config = load_config(repo_root)
    policy = load_source_policy(repo_root)
    errors: list[str] = []
    warnings: list[str] = []
    counts = {"requests": 0, "drafts": 0, "approved": 0, "publishedRecords": 0}
    for path in sorted((repo_root / REQUESTS_DIR).glob("*.json")):
        counts["requests"] += 1
        for error in validate_request(read_json(path)):
            errors.append(f"{path.relative_to(repo_root)}: {error}")
    for directory, publishable, key in ((DRAFTS_DIR, False, "drafts"), (APPROVED_DIR, True, "approved")):
        for path in sorted((repo_root / directory).glob("*.json")):
            counts[key] += 1
            article_errors, article_warnings = validate_article(read_json(path), config, policy, publishable=publishable)
            errors.extend(f"{path.relative_to(repo_root)}: {item}" for item in article_errors)
            warnings.extend(f"{path.relative_to(repo_root)}: {item}" for item in article_warnings)
    log_path = repo_root / PUBLICATION_LOG_PATH
    if log_path.is_file():
        log = publication_log(repo_root)
        counts["publishedRecords"] = len(log["entries"])
        for entry in log["entries"]:
            slug = str(entry.get("slug", ""))
            if not SLUG_RE.fullmatch(slug):
                errors.append(f"publication log slug geçersiz: {slug}")
            page = repo_root / "alo186/haberler" / slug / "index.html"
            overlay = repo_root / "alo186/deployment/routing-overlays" / f"ai-cms-{slug}-v{VERSION}.json"
            if not page.is_file():
                errors.append(f"publication log sayfası eksik: {slug}")
            if not overlay.is_file():
                errors.append(f"publication log overlay eksik: {slug}")
    return {
        "ok": not errors,
        "cmsVersion": VERSION,
        "counts": counts,
        "warnings": sorted(set(warnings)),
        "errors": sorted(set(errors)),
        "autoPublish": False,
        "personalProfilesAllowed": False,
    }


def audit_repository(repo_root: Path) -> dict[str, Any]:
    errors: list[str] = []
    inspected: list[str] = []
    paths: list[Path] = []
    for directory in (CMS_ROOT, Path("alo186/haberler"), Path("alo186/deployment/routing-overlays")):
        root = repo_root / directory
        if root.is_dir():
            paths.extend(path for path in root.rglob("*") if path.is_file())
    for path in sorted(set(paths)):
        relative = path.relative_to(repo_root).as_posix()
        if path.suffix.lower() not in {".json", ".html", ".txt", ".md", ".yml", ".yaml"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        is_cms_file = relative.startswith("alo186/cms/")
        is_cms_page = 'data-ai-cms-version="220"' in text
        is_cms_overlay = path.name.startswith("ai-cms-") and path.name.endswith(f"-v{VERSION}.json")
        if not (is_cms_file or is_cms_page or is_cms_overlay):
            continue
        inspected.append(relative)
        findings = privacy_findings(text)
        errors.extend(f"{relative}: gizlilik ihlali: {finding}" for finding in findings)
        if is_cms_page:
            if 'data-ai-cms-approved="true"' not in text:
                errors.append(f"{relative}: onay kanıtı eksik")
            if '"@type":"Organization"' not in text:
                errors.append(f"{relative}: Organization schema eksik")
            if '"@type":"Person"' in text or "ProfilePage" in text:
                errors.append(f"{relative}: kişi şeması yasak")
            if re.search(r"(?:mailto:|tel:)", text, re.I):
                errors.append(f"{relative}: kişisel iletişim bağlantısı yasak")
            if re.search(r"(?:amazon\.|amzn\.)", text, re.I):
                errors.append(f"{relative}: CMS otomatik affiliate bağlantısı üretemez")
    return {
        "ok": not errors,
        "cmsVersion": VERSION,
        "inspectedFileCount": len(inspected),
        "inspectedFiles": inspected,
        "errors": sorted(set(errors)),
        "personalProfilePublished": False,
        "autoPublished": False,
    }


def init_request(args: argparse.Namespace, repo_root: Path) -> dict[str, Any]:
    request_id = args.request_id or f"{today()}-{slugify(args.topic)[:50]}"
    record = {
        "request_id": request_id,
        "status": "idea",
        "topic": args.topic.strip(),
        "primary_question": args.primary_question.strip(),
        "audience": args.audience.strip(),
        "objective": args.objective.strip(),
        "risk_level": args.risk_level,
        "commercial_intent": args.commercial_intent,
        "preferred_slug": slugify(args.preferred_slug or args.topic),
        "required_sources": [],
        "internal_links": [],
        "exclusions": [
            "Kişisel isim, profil veya iletişim bilgisi",
            "Doğrulanmamış fiyat, stok, teslimat ve puan",
            "Uzaktan kesin arıza teşhisi",
        ],
        "notes": [],
        "created_at": today(),
    }
    errors = validate_request(record)
    if errors:
        raise CmsError("Yeni istek geçersiz: " + "; ".join(errors))
    path = repo_root / REQUESTS_DIR / f"{request_id}.json"
    if path.exists():
        raise CmsError(f"İstek zaten var: {path}")
    write_json(path, record)
    return {"ok": True, "cmsVersion": VERSION, "request": path.relative_to(repo_root).as_posix()}


def command_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ALO186 privacy-first Git-native AI CMS")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    sub = parser.add_subparsers(dest="command", required=True)

    validate_parser = sub.add_parser("validate")
    validate_parser.add_argument("--report", type=Path)

    audit_parser = sub.add_parser("audit")
    audit_parser.add_argument("--report", type=Path)

    init_parser = sub.add_parser("init-request")
    init_parser.add_argument("--request-id")
    init_parser.add_argument("--topic", required=True)
    init_parser.add_argument("--primary-question", required=True)
    init_parser.add_argument("--audience", default="Türkiye'deki elektrik kullanıcıları")
    init_parser.add_argument("--objective", default="Güvenli ve uygulanabilir karar desteği")
    init_parser.add_argument("--risk-level", choices=["low", "medium", "high"], default="medium")
    init_parser.add_argument("--commercial-intent", choices=["none", "informational", "comparison"], default="informational")
    init_parser.add_argument("--preferred-slug")

    generate_parser = sub.add_parser("generate")
    generate_parser.add_argument("--request", type=Path, required=True)
    generate_parser.add_argument("--output", type=Path)
    generate_parser.add_argument("--model", default=os.environ.get("ALO186_AI_CMS_MODEL", DEFAULT_MODEL))
    generate_parser.add_argument("--offline-scaffold", action="store_true")

    compile_parser = sub.add_parser("compile")
    compile_parser.add_argument("--article", type=Path, required=True)
    compile_parser.add_argument("--force", action="store_true")

    return parser


def emit(report: dict[str, Any], report_path: Path | None = None) -> None:
    output = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if report_path:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(output, encoding="utf-8")
    print(output, end="")


def main() -> None:
    parser = command_parser()
    args = parser.parse_args()
    repo_root = args.repo_root.resolve()
    try:
        if args.command == "validate":
            report = validate_repository(repo_root)
            emit(report, args.report)
        elif args.command == "audit":
            report = audit_repository(repo_root)
            emit(report, args.report)
        elif args.command == "init-request":
            report = init_request(args, repo_root)
            emit(report)
        elif args.command == "generate":
            request_path = args.request if args.request.is_absolute() else repo_root / args.request
            output_path = None if not args.output else (args.output if args.output.is_absolute() else repo_root / args.output)
            report = generate(
                repo_root,
                request_path,
                output_path,
                model=args.model,
                offline_scaffold=args.offline_scaffold,
            )
            emit(report)
        elif args.command == "compile":
            article_path = args.article if args.article.is_absolute() else repo_root / args.article
            report = compile_article(repo_root, article_path, force=args.force)
            emit(report)
        else:
            raise CmsError(f"Bilinmeyen komut: {args.command}")
    except CmsError as exc:
        emit({"ok": False, "cmsVersion": VERSION, "error": str(exc)})
        raise SystemExit(1) from exc
    if not report.get("ok", False):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
