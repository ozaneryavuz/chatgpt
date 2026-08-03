from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
home = (ROOT / "alo186/index.html").read_text(encoding="utf-8")
hub = (ROOT / "alo186/amazon-elektrik-urunleri/index.html").read_text(encoding="utf-8")

assert 'href="/elektrik-dayaniklilik-karti/"' in home
assert 'data-alo186-resilience-card-entry="true"' in home
assert 'kişisel verisiz' in home
assert 'kartı paylaşın' in home
assert '18+ karar rotası' not in hub
assert 'Güncel karar rotaları' in hub
assert '25 rehberin tamamını gör' not in home
assert '152 modeli doğrulanmış ürün için seçim kartları' not in home
assert 'Amazon Gelir Ortağı' in hub
assert 'Mevcut sistem yeterliyse satın alma yok' in hub
assert 'www.amazon.com.tr' not in home[home.index('data-alo186-resilience-card-entry'):home.index('data-alo186-resilience-card-entry') + 700]
print('ALO186 run6 trust and repeat visit: PASS')
