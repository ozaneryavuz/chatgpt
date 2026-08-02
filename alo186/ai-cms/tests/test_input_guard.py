from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "alo186/ai-cms/input_guard.py"
spec = importlib.util.spec_from_file_location("alo186_ai_cms_input_guard", MODULE_PATH)
assert spec and spec.loader
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)


def valid_tckn(first_nine: str = "100000001") -> str:
    digits = [int(char) for char in first_nine]
    tenth = ((sum(digits[0:9:2]) * 7) - sum(digits[1:8:2])) % 10
    eleventh = (sum(digits) + tenth) % 10
    return first_nine + str(tenth) + str(eleventh)


def safe_brief() -> dict:
    return {
        "schemaVersion": 1,
        "slug": "modem-mini-ups-kontrolu",
        "titleSeed": "Modem Mini UPS Uygunluk Rehberi",
        "topic": "Modem ve fiber ONT için mini UPS uygunluğu",
        "intent": "Kullanıcı satın almadan önce gerilim, polarite, jak ve süre uygunluğunu doğrulamak istiyor.",
        "primaryKeyword": "modem mini UPS",
        "audience": ["Ev kullanıcıları", "Uzaktan çalışanlar"],
        "sources": [
            {
                "id": "S1",
                "publisher": "Üretici teknik dokümantasyonu",
                "title": "DC çıkış ve bağlantı teknik kılavuzu",
                "url": "https://docs.example.org/products/12v-2a-guide?revision=2026-08",
                "accessedAt": "2026-08-02",
                "primary": True,
                "factSummary": "Kaynak, cihazın gerilim, akım, merkez polaritesi ve jak uyumluluğunun birlikte doğrulanması gerektiğini açıklar.",
            }
        ],
        "internalLinks": [
            {
                "label": "Modem internet yedekleme hesabı",
                "path": "/hesaplama/modem-internet-yedekleme/",
                "reason": "Kullanıcının güç ve süre hesabına geçmesini sağlar.",
            }
        ],
    }


class InputGuardTests(unittest.TestCase):
    def test_safe_editorial_brief_passes_without_echoing_values(self) -> None:
        payload = safe_brief()
        self.assertEqual(guard.scan(payload), [])
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "brief.json"
            path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
            result = guard.validate_brief_file(path)
        self.assertTrue(result["ok"])
        self.assertIs(result["personalDataSent"], False)
        self.assertNotIn(payload["sources"][0]["factSummary"], json.dumps(result, ensure_ascii=False))

    def test_email_phone_iban_and_labeled_identifiers_fail_closed(self) -> None:
        cases = {
            "email": "İletişim için kisi@example.com adresini kullanın.",
            "phone": "Saha sorumlusu +90 532 123 45 67 numarasındadır.",
            "iban": "Ödeme hesabı TR33 0006 1005 1978 6457 8413 26.",
            "installation": "Tesisat no: 1234567890",
        }
        for label, value in cases.items():
            with self.subTest(label=label):
                payload = safe_brief()
                payload["sources"][0]["factSummary"] = value
                violations = guard.scan(payload)
                self.assertTrue(violations, value)
                self.assertFalse(any(value in violation for violation in violations))

    def test_valid_tckn_checksum_is_detected_but_arbitrary_11_digits_are_not(self) -> None:
        identity = valid_tckn()
        self.assertTrue(guard.tckn_valid(identity))
        payload = safe_brief()
        payload["intent"] = f"Kayıtta {identity} kimliği bulunuyor."
        self.assertTrue(any("T.C. kimlik" in item for item in guard.scan(payload)))

        payload["intent"] = "Teknik model numarası 12345678901 olarak yazılmıştır."
        self.assertFalse(any("T.C. kimlik" in item for item in guard.scan(payload)))

    def test_forbidden_personal_data_keys_are_rejected_without_values_in_errors(self) -> None:
        payload = safe_brief()
        payload["customerNumber"] = "987654321"
        payload["address"] = "Örnek Mahallesi Örnek Sokak"
        violations = guard.scan(payload)
        self.assertTrue(any("customerNumber" in item for item in violations))
        self.assertTrue(any("address" in item for item in violations))
        self.assertFalse(any("987654321" in item for item in violations))
        self.assertFalse(any("Örnek Mahallesi" in item for item in violations))

    def test_guard_error_reports_field_paths_only(self) -> None:
        payload = safe_brief()
        secret_value = "ozel.kisi@example.com"
        payload["sources"][0]["factSummary"] = secret_value
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "brief.json"
            path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
            with self.assertRaises(guard.GuardError) as raised:
                guard.validate_brief_file(path)
        message = str(raised.exception)
        self.assertIn("sources.0.factSummary", message)
        self.assertNotIn(secret_value, message)


if __name__ == "__main__":
    unittest.main()
