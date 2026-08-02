from __future__ import annotations

import contextlib
import datetime as dt
import importlib.util
import io
import json
import os
import sys
import tempfile
import threading
import unittest
from argparse import Namespace
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "alo186/ai-cms/cms.py"
spec = importlib.util.spec_from_file_location("alo186_ai_cms", MODULE_PATH)
assert spec and spec.loader
cms = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cms)


class FakeResponsesHandler(BaseHTTPRequestHandler):
    payloads: list[dict] = []
    draft: dict = {}

    def log_message(self, _format: str, *_args) -> None:
        return

    def do_POST(self) -> None:  # noqa: N802
        length = int(self.headers.get("Content-Length", "0"))
        payload = json.loads(self.rfile.read(length).decode("utf-8"))
        type(self).payloads.append(payload)
        body = json.dumps(
            {
                "status": "completed",
                "output": [
                    {
                        "type": "message",
                        "content": [
                            {"type": "output_text", "text": json.dumps(type(self).draft, ensure_ascii=False)}
                        ],
                    }
                ],
            },
            ensure_ascii=False,
        ).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


@contextlib.contextmanager
def fake_responses(draft: dict):
    FakeResponsesHandler.payloads = []
    FakeResponsesHandler.draft = draft
    server = ThreadingHTTPServer(("127.0.0.1", 0), FakeResponsesHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


@contextlib.contextmanager
def sandbox():
    originals = {
        name: getattr(cms, name)
        for name in (
            "REPO_ROOT",
            "CMS_ROOT",
            "POLICY_PATH",
            "BRIEF_DIR",
            "CONTENT_DIR",
            "REVIEW_DIR",
            "PREVIEW_DIR",
            "PROMPT_PATH",
            "DRAFT_SCHEMA_PATH",
            "ROUTING_MANIFEST",
            "ROUTING_OVERLAYS",
            "PUBLISHED_ROOT",
        )
    }
    with tempfile.TemporaryDirectory() as directory:
        repo = Path(directory)
        cms.REPO_ROOT = repo
        cms.CMS_ROOT = repo / "alo186/ai-cms"
        cms.POLICY_PATH = cms.CMS_ROOT / "policy.json"
        cms.BRIEF_DIR = cms.CMS_ROOT / "briefs"
        cms.CONTENT_DIR = cms.CMS_ROOT / "content"
        cms.REVIEW_DIR = cms.CMS_ROOT / "reviews"
        cms.PREVIEW_DIR = cms.CMS_ROOT / "previews"
        cms.PROMPT_PATH = cms.CMS_ROOT / "prompts/article-system.txt"
        cms.DRAFT_SCHEMA_PATH = cms.CMS_ROOT / "schema/draft-output.schema.json"
        cms.ROUTING_MANIFEST = repo / "alo186/deployment/routing-manifest.json"
        cms.ROUTING_OVERLAYS = repo / "alo186/deployment/routing-overlays"
        cms.PUBLISHED_ROOT = repo / "alo186/haberler"

        cms.CMS_ROOT.mkdir(parents=True, exist_ok=True)
        cms.ROUTING_OVERLAYS.mkdir(parents=True, exist_ok=True)
        cms.PUBLISHED_ROOT.mkdir(parents=True, exist_ok=True)
        (cms.CMS_ROOT / "prompts").mkdir(parents=True, exist_ok=True)
        (cms.CMS_ROOT / "schema").mkdir(parents=True, exist_ok=True)
        (repo / "alo186/elektrik-portali").mkdir(parents=True, exist_ok=True)
        (repo / "alo186/hesaplama").mkdir(parents=True, exist_ok=True)
        (repo / "alo186/elektrik-portali/index.html").write_text(
            '<!doctype html><title>Elektrik Portalı</title><h1>Elektrik Portalı</h1><link rel="canonical" href="https://alo186.com/elektrik-portali">',
            encoding="utf-8",
        )
        (repo / "alo186/hesaplama/index.html").write_text(
            '<!doctype html><title>Ücretsiz hesaplayıcılar</title><h1>Elektrik hesaplayıcıları</h1><link rel="canonical" href="https://alo186.com/hesaplama/">',
            encoding="utf-8",
        )
        cms.ROUTING_MANIFEST.parent.mkdir(parents=True, exist_ok=True)
        cms.write_json(
            cms.ROUTING_MANIFEST,
            {
                "version": 218,
                "canonicalHost": "https://alo186.com",
                "routes": [
                    {"source": "alo186/elektrik-portali/index.html", "canonicalPath": "/elektrik-portali", "type": "collection"},
                    {"source": "alo186/hesaplama/index.html", "canonicalPath": "/hesaplama/", "type": "collection"},
                ],
            },
        )
        policy = json.loads((ROOT / "alo186/ai-cms/policy.json").read_text(encoding="utf-8"))
        cms.write_json(cms.POLICY_PATH, policy)
        cms.PROMPT_PATH.write_text("Yalnız JSON üret.", encoding="utf-8")
        cms.DRAFT_SCHEMA_PATH.write_text(
            (ROOT / "alo186/ai-cms/schema/draft-output.schema.json").read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        try:
            yield repo
        finally:
            for name, value in originals.items():
                setattr(cms, name, value)


def sources(count: int = 2, primary: bool = False) -> list[dict]:
    accessed = dt.datetime.now(dt.timezone.utc).date().isoformat()
    return [
        {
            "id": f"S{index}",
            "publisher": f"Birincil Kurum {index}",
            "title": f"Teknik kaynak belgesi {index}",
            "url": f"https://example{index}.org/technical-source",
            "accessedAt": accessed,
            "primary": primary and index == 1,
            "factSummary": "Bu kaynak, güvenli inceleme için kullanılacak teknik sınırları, doğrulama gereksinimlerini ve kullanıcıya aktarılabilecek temel olguları açıklar.",
        }
        for index in range(1, count + 1)
    ]


def long_paragraph(seed: str) -> str:
    sentence = (
        f"{seed} için kullanıcı önce etiket değerlerini, üretici sınırlarını ve sistemin gerçek çalışma koşullarını birlikte doğrulamalıdır. "
        "Tek bir sayı veya ürün başlığı güvenli karar için yeterli değildir; ölçüm, bakım geçmişi ve ilgili resmî kaynaklar birbirinden ayrılmalıdır. "
        "Belirsiz bilgi bulunduğunda tehlikeli müdahale yapılmamalı, enerji kesilmeli ve yetkili uzman değerlendirmesine geçilmelidir. "
    )
    return sentence * 4


def draft_output() -> dict:
    return {
        "title": "Modem Mini UPS Uygunluk ve Süre Kontrolü Rehberi",
        "h1": "Modem mini UPS seçiminde gerilim, polarite ve süre nasıl doğrulanır?",
        "description": "Modem ve fiber ONT için mini UPS seçiminde gerilim, polarite, jak, toplam güç ve hedef süreyi kaynak bağlı kontrol adımlarıyla doğrulayın.",
        "directAnswer": "Modem mini UPS seçiminde cihazların etiket gerilimi, merkez polaritesi, jak ölçüsü ve toplam gücü tam eşleşmelidir. Kapasite hesabı bu uyumluluk doğrulamasından sonra yapılmalı; belirsizlikte ürün kullanılmamalıdır.",
        "sections": [
            {
                "id": f"adim-{index}",
                "heading": f"Teknik doğrulama adımı {index}",
                "paragraphs": [long_paragraph(f"Adım {index}")],
                "bullets": ["Etiket değerini kaydedin.", "Belirsizliği uzmanla doğrulayın."],
                "sourceRefs": ["S1", "S2"],
            }
            for index in range(1, 5)
        ],
        "faqs": [
            {
                "question": f"Mini UPS kontrolünde sık sorulan soru {index} nedir?",
                "answer": "Yanıt yalnız etiket, üretici belgesi ve kaynakta açıklanan teknik sınırlar birlikte doğrulandığında verilebilir; tek bir özellik uygunluk kanıtı değildir.",
                "sourceRefs": ["S1" if index % 2 else "S2"],
            }
            for index in range(1, 4)
        ],
        "topics": ["mini UPS", "fiber ONT", "DC polarite", "çalışma süresi"],
        "riskNotes": ["Yanlış polarite cihaz hasarına yol açabilir.", "Belirsizlikte doğrudan ürün CTA açılmamalıdır."],
    }


def brief() -> dict:
    now = cms.utc_now()
    return {
        "schemaVersion": 1,
        "id": cms.content_id("modem-mini-ups-kontrolu", now),
        "slug": "modem-mini-ups-kontrolu",
        "contentType": "article",
        "state": "brief",
        "locale": "tr-TR",
        "topic": "Modem ve fiber ONT için mini UPS uygunluğu",
        "titleSeed": "Modem Mini UPS Uygunluk Rehberi",
        "intent": "Kullanıcı satın almadan önce gerilim, polarite, jak ve süre uygunluğunu doğrulamak istiyor.",
        "primaryKeyword": "modem mini UPS",
        "audience": ["Ev kullanıcıları", "Uzaktan çalışanlar"],
        "riskClass": "medium",
        "sources": sources(2),
        "internalLinks": [
            {"label": "Elektrik Portalı", "path": "/elektrik-portali", "reason": "Ana işlem merkezine dönüş sağlar."},
            {"label": "Ücretsiz hesaplayıcılar", "path": "/hesaplama/", "reason": "Teknik hesabı ücretsiz araçlara bağlar."},
        ],
        "commerce": {"enabled": False, "policy": "none", "category": None},
        "requestedAt": now,
        "requestedBy": "test-editor",
    }


class CmsTests(unittest.TestCase):
    def test_brief_and_structured_responses_contract(self) -> None:
        with sandbox():
            item = brief()
            self.assertEqual(cms.validate_brief(item, cms.load_policy(), require_sources=True), [])
            with fake_responses(draft_output()) as base_url:
                client = cms.OpenAIResponsesClient("test-secret-never-log", base_url)
                value = client.create_structured(
                    model="gpt-5-mini",
                    instructions="Yalnız JSON",
                    prompt=cms.ai_prompt(item),
                    schema=cms.read_json(cms.DRAFT_SCHEMA_PATH),
                )
            self.assertEqual(value["title"], draft_output()["title"])
            payload = FakeResponsesHandler.payloads[0]
            self.assertIs(payload["store"], False)
            self.assertEqual(payload["text"]["format"]["type"], "json_schema")
            self.assertIs(payload["text"]["format"]["strict"], True)
            self.assertEqual(payload["model"], "gpt-5-mini")
            self.assertNotIn("test-secret-never-log", json.dumps(payload))

    def test_review_quality_approval_and_publish_flow(self) -> None:
        with sandbox():
            item = brief()
            record = cms.assemble_record(item, draft_output(), "gpt-5-mini")
            cms.write_json(cms.content_path(record["slug"]), record)
            report = cms.validate_record(record, write_quality=True)
            self.assertTrue(report["ok"], report)
            self.assertGreaterEqual(report["score"], 85)
            self.assertTrue(report["checks"]["sources"])
            self.assertTrue(report["checks"]["contentDepth"])
            with self.assertRaises(cms.CmsError):
                cms.approve_record(record, "github-actions[bot]", 42)

            approved = cms.approve_record(record, "ozaneryavuz", 42)
            cms.write_json(cms.content_path(record["slug"]), approved)
            result = cms.publish_record(approved)
            self.assertEqual(result["record"]["state"], "published")
            target = cms.PUBLISHED_ROOT / record["slug"] / "index.html"
            page = target.read_text(encoding="utf-8")
            self.assertIn(f'data-ai-cms-id="{record["id"]}"', page)
            self.assertIn("AI destekli taslak insan editör onayıyla yayımlanmıştır", page)
            self.assertIn("ALO186 bağımsız bilgilendirme platformudur", page)
            self.assertIn('rel="external noopener"', page)
            self.assertIn("FAQPage", page)
            self.assertNotIn('"@type":"Person"', page)
            self.assertNotIn('"@type":"Product"', page)
            self.assertNotIn('"@type":"Offer"', page)
            overlay = cms.read_json(cms.ROUTING_OVERLAYS / f"ai-cms-{record['slug']}.json")
            self.assertTrue(overlay["aiCms"]["humanApproved"])
            self.assertEqual(overlay["routes"][0]["canonicalPath"], f"/haberler/{record['slug']}")

    def test_high_risk_commerce_and_duplicate_content_fail_closed(self) -> None:
        with sandbox() as repo:
            item = brief()
            item["riskClass"] = "high"
            item["sources"] = sources(3, primary=True)
            item["commerce"] = {"enabled": True, "policy": "after_tool", "category": "mini_ups"}
            record = cms.assemble_record(item, draft_output(), "gpt-5-mini")
            report = cms.validate_record(record)
            self.assertFalse(report["ok"])
            self.assertTrue(any("ticari CTA" in error for error in report["errors"]))

            item["commerce"] = {"enabled": False, "policy": "none", "category": None}
            existing = repo / "alo186/haberler/existing/index.html"
            existing.parent.mkdir(parents=True, exist_ok=True)
            existing.write_text(
                f'<!doctype html><title>{record["title"]}</title><h1>{record["h1"]}</h1><link rel="canonical" href="https://alo186.com/haberler/existing">',
                encoding="utf-8",
            )
            record = cms.assemble_record(item, draft_output(), "gpt-5-mini")
            duplicate = cms.validate_record(record)
            self.assertTrue(any("kanibalizasyon" in error for error in duplicate["errors"]))

    def test_review_pack_preview_and_private_dashboard(self) -> None:
        with sandbox():
            record = cms.assemble_record(brief(), draft_output(), "gpt-5-mini")
            cms.write_json(cms.content_path(record["slug"]), record)
            report = cms.validate_record(record, write_quality=True)
            review = cms.review_markdown(record, report, draft_output()["riskNotes"])
            self.assertIn(f"/cms approve {record['slug']}", review)
            self.assertIn("AI risk notları", review)
            preview = cms.render_html(record, preview=True)
            self.assertIn('meta name="robots" content="noindex,nofollow"', preview)
            self.assertIn("AI CMS önizleme", preview)
            output = cms.CMS_ROOT / "dashboard.html"
            summary = cms.dashboard(output)
            self.assertEqual(summary["records"], 1)
            dashboard_html = output.read_text(encoding="utf-8")
            self.assertIn("workflow artifactı", dashboard_html)
            self.assertNotIn("OPENAI_API_KEY", dashboard_html)

    def test_cli_errors_do_not_leak_openai_key(self) -> None:
        with sandbox(), patch.dict(os.environ, {"OPENAI_API_KEY": "secret-key-must-not-leak"}, clear=False):
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                with self.assertRaises(SystemExit):
                    cms.main.__wrapped__() if hasattr(cms.main, "__wrapped__") else (_ for _ in ()).throw(SystemExit(1))
            self.assertNotIn("secret-key-must-not-leak", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
