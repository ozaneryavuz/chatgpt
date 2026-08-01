# ALO186 marka logosu performans sözleşmesi

## Canlı bulgu

Canlı HTML'de `fetchpriority="high"`, `loading="eager"` ve `decoding="async"` zaten bulunuyor. Korunması gereken bu yükleme önceliği değil, asıl düzeltilecek alan görsel adayının boyutudur:

- logo ekranda yaklaşık `162 × 28 px` gösteriliyor;
- bileşen `749 × 130` intrinsic ölçü yayımlıyor;
- tarayıcıya `640–1200 px` adayları sunuluyor;
- sonuçta küçük bir başlık logosu için gereksiz büyük `/_vinext/image` yanıtı indirilebiliyor.

Bu düzeltme istemci tarafındaki sonradan çalışan JavaScript ile yapılmamalıdır. Tarayıcı görsel isteğini başlatmadan önce doğru `width`, `height`, `sizes`, `srcset` ve `fetchpriority` değerlerini ilk HTML içinde görmelidir.

## ChatGPT Sites / Vinext kaynak bileşeni

Logo bileşeni aşağıdaki sözleşmeye getirilmelidir:

```tsx
<Image
  src="/brand/alo186-logo.png"
  alt="ALO186.com"
  width={162}
  height={28}
  sizes="(max-width: 480px) 150px, 162px"
  quality={70}
  loading="eager"
  fetchPriority="high"
  decoding="async"
  className="brand-logo"
/>
```

```css
.brand-logo {
  display: block;
  width: 162px;
  height: auto;
  max-width: 100%;
}

@media (max-width: 480px) {
  .brand-logo {
    width: 150px;
  }
}
```

Kritik noktalar:

1. `width={749}` / `height={130}` değerleri kaldırılmalı; bileşen ölçüsü gerçek slotla eşleşmelidir.
2. `sizes` kesin slot genişliğini bildirmeli; `100vw` veya sizes'sız kullanım bırakılmamalıdır.
3. İlk ekrandaki logo için `fetchPriority="high"` ve `loading="eager"` korunmalıdır.
4. `quality={70}` yeterli başlangıç değeridir; metin kenarları görsel kontrolden sonra 65–75 aralığında tutulabilir.
5. Vinext yanıtının `Content-Type` başlığı `image/avif` veya `image/webp` olmalıdır. PNG dönmeye devam ederse aşağıdaki açık `<picture>` çözümüne geçilmelidir.

## Vinext modern format üretmezse

162, 324 ve tercihen 486 piksel genişliğinde AVIF/WebP dosyaları üretilip kaynak açık biçimde bildirilmelidir:

```html
<picture>
  <source
    type="image/avif"
    srcset="/brand/alo186-logo-162.avif 162w,
            /brand/alo186-logo-324.avif 324w,
            /brand/alo186-logo-486.avif 486w">
  <source
    type="image/webp"
    srcset="/brand/alo186-logo-162.webp 162w,
            /brand/alo186-logo-324.webp 324w,
            /brand/alo186-logo-486.webp 486w">
  <img
    src="/brand/alo186-logo-162.webp"
    srcset="/brand/alo186-logo-162.webp 162w,
            /brand/alo186-logo-324.webp 324w,
            /brand/alo186-logo-486.webp 486w"
    sizes="(max-width: 480px) 150px, 162px"
    alt="ALO186.com"
    width="162"
    height="28"
    loading="eager"
    fetchpriority="high"
    decoding="async"
    class="brand-logo">
</picture>
```

## Kabul ölçütleri

- İlk HTML içinde `fetchpriority="high"` bulunur.
- `loading="eager"` ve `decoding="async"` korunur.
- Intrinsic ölçü en fazla `324 × 56 px`, tercih edilen değer `162 × 28 px` olur.
- `sizes` masaüstünde 162 px, küçük ekranda 150 px slotu bildirir.
- Lighthouse ağı sırasında 1200 px logo adayı seçilmez.
- Yanıt AVIF/WebP olur veya küçük aday nedeniyle transfer boyutu kabul edilebilir seviyeye iner.
- Görsel en-boy oranı ve başlık yerleşimi bozulmaz; CLS oluşmaz.

Depodaki doğrulama:

```bash
python alo186/tests/test_brand_logo_performance.py
python alo186/deployment/verify_brand_logo.py --url https://alo186.com/ --strict
```
