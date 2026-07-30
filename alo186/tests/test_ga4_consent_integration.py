from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEPLOYMENT_DIR = HERE.parent / "deployment"
sys.path.insert(0, str(DEPLOYMENT_DIR if DEPLOYMENT_DIR.is_dir() else HERE))

import inject_ga4_consent as ga4

COOKIE_OLD = (
    "ALO186 reklam çerezi veya davranışsal hedefleme kullanmaz. Site içindeki temel "
    "yönlendirmelerin yararını ölçmek için çerez bırakmayan ve kalıcı cihaz ya da oturum "
    "kimliği üretmeyen günlük toplu sayaçlar kullanılır."
)
COOKIE_DETAIL_OLD = (
    "Bu ölçüm; olay türü, herkese açık sayfa sınıfı ve hazırlık planı gibi sınırlı kategorilerle çalışır. "
    "Serbest metin, tam URL sorgusu, e-posta, telefon, açık adres, abonelik bilgisi veya hassas konum ölçüme eklenmez."
)
KVKK_OLD = (
    "Site yararını ve yönlendirme akışını geliştirmek için çerezsiz toplu olay sayaçları kullanılabilir. "
    "Olay türü ile herkese açık sayfa sınıfı, şirket veya hazırlık planı gibi sınırlı kategoriler günlük "
    "toplam sayıya dönüştürülür; kullanıcı ya da oturum kimliği, tam URL sorgusu, form metni, e-posta, "
    "telefon, açık adres ve hassas konum bu ölçüm kaydına eklenmez."
)
KVKK_RETENTION_OLD = (
    "Günlük toplu kullanım sayaçları hizmeti geliştirme amacıyla en fazla 90 gün saklanır. "
    "Bunlar kişi veya cihaz profili oluşturmak, davranışsal reklam göstermek ya da tekil kullanıcıyı izlemek için kullanılmaz."
)


def make_site(root: Path) -> Path:
    site = root / "site"
    (site / "yasal" / "cerez").mkdir(parents=True)
    (site / "yasal" / "kvkk-aydinlatma").mkdir(parents=True)
    (site / "hesaplama" / "ups").mkdir(parents=True)
    pages = {
        site / "index.html": "<!doctype html><html><head><title>A</title></head><body><a href='/edas-bul'>EDAŞ</a></body></html>",
        site / "hesaplama" / "ups" / "index.html": "<!doctype html><html><head><title>B</title></head><body><a rel='sponsored' href='https://amazon.com.tr/x'>Ürün</a></body></html>",
        site / "yasal" / "cerez" / "index.html": f"<!doctype html><html><head><title>Çerez</title></head><body><p>{COOKIE_OLD}</p><p>{COOKIE_DETAIL_OLD}</p></body></html>",
        site / "yasal" / "kvkk-aydinlatma" / "index.html": f"<!doctype html><html><head><title>KVKK</title></head><body><p>{KVKK_OLD}</p><p>{KVKK_RETENTION_OLD}</p></body></html>",
    }
    for path, content in pages.items():
        path.write_text(content, encoding="utf-8")
    for name in ("alo186-release.json", "pages-release.json"):
        (site / name).write_text(
            json.dumps(
                {
                    "canonicalHost": "https://alo186.com",
                    "liveTechnicalQuality": {"personalDataCollectionAdded": False},
                }
            ),
            encoding="utf-8",
        )
    return site


class InjectGa4ConsentTests(unittest.TestCase):
    def test_disabled_without_measurement_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            site = make_site(Path(tmp))
            report = ga4.run(site, "", "")
            self.assertFalse(report["enabled"])
            self.assertEqual(report["instrumentedHtmlCount"], 0)
            self.assertNotIn(ga4.MARKER, (site / "index.html").read_text(encoding="utf-8"))
            release = json.loads((site / "pages-release.json").read_text(encoding="utf-8"))
            self.assertFalse(release["analytics"]["enabled"])
            self.assertFalse(release["liveTechnicalQuality"]["personalDataCollectionAdded"])

    def test_invalid_measurement_id_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            site = make_site(Path(tmp))
            with self.assertRaises(ValueError):
                ga4.run(site, "", "AW-17532551119")

    def test_opt_in_ga4_is_injected_everywhere_and_legal_copy_updates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            site = make_site(Path(tmp))
            report = ga4.run(site, "/chatgpt", "G-ABC1234567")
            self.assertTrue(report["enabled"])
            self.assertEqual(report["htmlCount"], 4)
            self.assertEqual(report["instrumentedHtmlCount"], 4)
            self.assertEqual(report["newlyInjectedHtmlCount"], 4)
            self.assertEqual(
                sorted(report["legalPagesUpdated"]),
                ["yasal/cerez/index.html", "yasal/kvkk-aydinlatma/index.html"],
            )
            for path in site.rglob("*.html"):
                html = path.read_text(encoding="utf-8")
                self.assertIn(ga4.MARKER, html)
                self.assertIn("G-ABC1234567", html)
                self.assertIn("/chatgpt/yasal/cerez", html)
                self.assertNotIn("AW-17532551119", html)
                self.assertLess(html.index(ga4.MARKER), html.lower().index("</body>"))
            cookie = (site / "yasal" / "cerez" / "index.html").read_text(encoding="utf-8")
            kvkk = (site / "yasal" / "kvkk-aydinlatma" / "index.html").read_text(encoding="utf-8")
            self.assertNotIn(COOKIE_OLD, cookie)
            self.assertNotIn(COOKIE_DETAIL_OLD, cookie)
            self.assertNotIn(KVKK_OLD, kvkk)
            self.assertNotIn(KVKK_RETENTION_OLD, kvkk)
            self.assertIn("yalnız kullanıcı “Analitiğe izin ver”", cookie)
            self.assertIn("Rıza verilmezse Google etiketi yüklenmez", kvkk)
            release = json.loads((site / "pages-release.json").read_text(encoding="utf-8"))
            self.assertTrue(release["analytics"]["enabled"])
            self.assertEqual(release["analytics"]["measurementId"], "G-ABC1234567")
            self.assertTrue(release["liveTechnicalQuality"]["personalDataCollectionAdded"])
            self.assertFalse(release["liveTechnicalQuality"]["directPersonalDataFieldsAdded"])
            self.assertTrue((site / "checksums.sha256").is_file())

    def test_injection_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            site = make_site(Path(tmp))
            ga4.run(site, "", "G-ABC1234567")
            report = ga4.run(site, "", "G-ABC1234567")
            self.assertEqual(report["instrumentedHtmlCount"], 4)
            self.assertEqual(report["newlyInjectedHtmlCount"], 0)
            self.assertEqual((site / "index.html").read_text(encoding="utf-8").count(ga4.MARKER), 2)

    def test_embedded_javascript_parses(self) -> None:
        if shutil.which("node") is None:
            self.skipTest("node yok")
        bundle = ga4.consent_bundle("G-ABC1234567", "/yasal/cerez", "")
        self.assertIn("page_location:sanitizedLocation()", bundle)
        self.assertIn("clearAnalyticsCookies", bundle)
        scripts = re.findall(r"<script[^>]*>(.*?)</script>", bundle, flags=re.S | re.I)
        self.assertEqual(len(scripts), 1)
        with tempfile.TemporaryDirectory() as tmp:
            script = Path(tmp) / "analytics.js"
            script.write_text(scripts[0], encoding="utf-8")
            result = subprocess.run(["node", "--check", str(script)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
