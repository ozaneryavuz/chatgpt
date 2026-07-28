# Yedek Güç Toplam Sahip Olma Maliyeti Karşılaştırması

Bu modül UPS, taşınabilir power station, inverter-batarya sistemi ve jeneratörü kullanıcının kendi maliyet ve kesinti kayıtlarıyla karşılaştırır.

## Kullanıcı problemi

İlk satın alma fiyatı tek başına doğru çözümü göstermez. Araç aşağıdaki kalemleri aynı analiz döneminde görünür hâle getirir:

- satın alma ve kurulum,
- yıllık bakım,
- yıllık enerji veya yakıt,
- dönem içindeki batarya/ekipman yenilemeleri,
- kullanıcının tahmin ettiği kesinti etkisi,
- çözümün bu etkiyi karşılama oranı,
- toplam maliyet, önlenen etki, net fark ve yaklaşık geri ödeme.

Araç güncel piyasa fiyatı veya varsayılan ürün bedeli sağlamaz. Etkinleştirilen her çözüm için kullanıcıya ait maliyet dayanağı gerekir.

## Güvenlik ve ticari sınırlar

- Sıfır veya negatif net faydada sonuç “satın almayı ertele” olur.
- Tıbbi/yaşam destek yükü, sabit tesisat, trifaze/bilinmeyen faz ve 1.200 W üzeri sonuçlarda ticari rota kapalıdır.
- Jeneratör ve inverter-batarya sonuçları profesyonel doğrulama gerektirir.
- Doğrudan Amazon bağlantısı yoktur.
- Düşük riskli UPS/power station sonucunda dahi ürün merkezi, görünür satış ortaklığı açıklaması ve teknik yeniden doğrulama onayından sonra açılır.
- Fiyat, stok, satıcı puanı ve garanti bilgisi ALO186 üzerinde yayınlanmaz.

## Veri minimizasyonu

Ad, telefon, e-posta, adres, tesis/şirket adı, teklif veren firma veya serbest metin alınmaz. Teknik ve finansal girdiler yalnız tarayıcıda en fazla 30 gün tutulabilir. Tıbbi cihaz seçimi kalıcı depolamaya yazılmaz.

## Hesap özeti

Her çözüm için:

```text
TCO = satın alma + kurulum
    + analiz yılı × (yıllık bakım + yıllık işletme)
    + dönem içi yenileme sayısı × yenileme bedeli

Önlenen etki = analiz yılı × yıllık kesinti saati
             × saatlik etki × karşılama oranı

Net fark = önlenen etki - TCO
```

Yenileme analizin son gününe denk geliyorsa dönem içinde yeni bir yenileme olarak sayılmaz. Yaklaşık geri ödeme hesabı, dönem içindeki yenileme harcamalarını da dikkate alır.

## Test

```bash
node alo186/hesaplama/yedek-guc-maliyet-karsilastirma/test.js
```

Test kapsamı:

- yenileme sayısı ve geri ödeme,
- net faydaya göre sıralama,
- sıfır/negatif net faydada satın almama sonucu,
- en az iki çözüm zorunluluğu,
- maliyet dayanağı olmadan sonuç üretilmemesi,
- sabit tesisat, trifaze, yüksek güç, tıbbi yük, jeneratör ve inverter-bataryada affiliate yasağı,
- 30 günlük yerel kayıt ve tıbbi seçimin depolanmaması,
- canonical, veri minimizasyonu ve doğrudan Amazon bağlantısı yasağı.

## Sınırlar

Bu modül finansal danışmanlık, keşif, proje, ürün uygunluk onayı veya teklif doğrulaması değildir. Enflasyon, iskonto oranı, vergi, finansman ve para birimi riski için ayrı profesyonel analiz gerekebilir. Sonuçlar yalnız girilen varsayımların karşılaştırmasıdır.
