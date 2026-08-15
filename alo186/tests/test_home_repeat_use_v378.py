from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ALO = ROOT / "alo186"
HOME = ALO / "index.html"
REPEAT_HUB = ALO / "tekrar-kullanilan-araclar" / "index.html"

CANONICAL_JOURNAL = "/hesaplama/elektrik-kesintisi-sure-gunlugu/"
LEGACY_JOURNAL = "/hesaplama/kesinti-gunlugu/"


class HomeRepeatUseV378Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.home = HOME.read_text(encoding="utf-8")
        self.repeat = REPEAT_HUB.read_text(encoding="utf-8")

    def test_home_uses_current_outage_journal_canonical(self) -> None:
        self.assertIn(CANONICAL_JOURNAL, self.home)
        self.assertNotIn(f'href="{LEGACY_JOURNAL}"', self.home)
        self.assertIn(CANONICAL_JOURNAL, self.repeat)

    def test_repeat_use_module_is_prominent_and_before_commerce(self) -> None:
        marker = 'data-alo186-repeat-use="true"'
        self.assertIn(marker, self.home)
        repeat_pos = self.home.index(marker)
        library_pos = self.home.index('data-alo186-resource-library="true"')
        revenue_pos = self.home.index('class="revenue-sprint"')
        self.assertLess(repeat_pos, library_pos)
        self.assertLess(repeat_pos, revenue_pos)

    def test_repeat_use_module_has_four_event_based_routes(self) -> None:
        required = (
            "/tekrar-kullanilan-araclar/",
            CANONICAL_JOURNAL,
            "/fatura-ve-sayac-kontrol-merkezi/",
            "/ev-elektrik-guvenlik-kontrol-merkezi/",
        )
        for href in required:
            self.assertIn(f'href="{href}"', self.home, href)
        for phrase in ("Her yeni kesintide", "Her yeni faturada", "Yeni cihaz, tadilat veya belirti"):
            self.assertIn(phrase, self.home, phrase)

    def test_repeat_use_module_is_no_commerce(self) -> None:
        start = self.home.index('<section class="task-start repeat-use-start"')
        end = self.home.index("</section>", start) + len("</section>")
        block = self.home[start:end].casefold()
        for forbidden in (
            "amazon.com.tr",
            "amzn.to",
            "alo186rehber-21",
            'rel="sponsored',
            '"@type":"product"',
            '"@type":"offer"',
            "pricecurrency",
        ):
            self.assertNotIn(forbidden, block, forbidden)

    def test_trust_and_independence_contract_remains_visible(self) -> None:
        for phrase in (
            "ALO186 arıza kaydı almaz",
            "Bağımsız bilgilendirme platformudur; EDAŞ veya kamu kurumu değildir.",
            "Ticari ilişki görünür",
            "Satın almama geçerli sonuç",
            "Güvenlik gelirden önce",
        ):
            self.assertIn(phrase, self.home, phrase)
        self.assertIn("Bu merkezde doğrudan Amazon veya başka bir mağaza bağlantısı yoktur.", self.repeat)
        self.assertIn("Mevcut çözüm yeterliyse yeni ürün almayın.", self.repeat)

    def test_home_has_no_direct_merchant_link(self) -> None:
        hrefs = re.findall(r'href="([^"]+)"', self.home, flags=re.I)
        merchant = [href for href in hrefs if "amazon.com.tr" in href or "amzn.to" in href]
        self.assertFalse(merchant, merchant)


if __name__ == "__main__":
    unittest.main()
