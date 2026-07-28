#!/bin/sh
set -eu

DESTINATION="${1:-_site}"
MODE="${2:-preview}"
ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
ALO_DIR="$ROOT_DIR/alo186"
CANONICAL_ORIGIN="https://www.alo186.com"
LEGACY_ORIGIN="https://alo186.com"

case "$MODE" in
  preview|overlay) ;;
  *) echo "Kullanım: $0 <hedef-klasör> <preview|overlay>" >&2; exit 2 ;;
esac

rm -rf "$DESTINATION"
mkdir -p "$DESTINATION"

copy_directory() {
  source_path="$1"
  target_path="$2"
  mkdir -p "$DESTINATION/$target_path"
  cp -a "$source_path/." "$DESTINATION/$target_path/"
  rm -f "$DESTINATION/$target_path/README.md"
}

copy_page() {
  source_directory="$1"
  target_path="$2"
  copy_directory "$source_directory" "$target_path"
}

# Yalnız kullanıcıya sunulan statik modüller. API, test, kaynak raporları ve deployment
# dosyaları public artifact'a bilinçli olarak dahil edilmez.
mkdir -p "$DESTINATION/elektrik-portali"
cp "$ALO_DIR/index.html" "$DESTINATION/elektrik-portali/index.html"
cp "$ALO_DIR/styles.css" "$DESTINATION/elektrik-portali/styles.css"

copy_page "$ALO_DIR/turkiye-arama" "edas-bul"
copy_page "$ALO_DIR/karar-motoru" "karar-motoru"
copy_page "$ALO_DIR/hesaplama" "hesaplama"
copy_page "$ALO_DIR/urun-eslestirme" "akilli-urun-secimi"
copy_page "$ALO_DIR/sureklilik-paneli" "isletme-surekliligi"
copy_page "$ALO_DIR/fatura-analizi" "fatura-analizi"
copy_page "$ALO_DIR/yedek-guc-hesaplayici" "hesaplama/yedek-guc"
copy_page "$ALO_DIR/kesinti-maliyet-hesaplayici" "hesaplama/kesinti-maliyeti"

# Bütün kaynak doğrulamalı teknik makaleleri otomatik olarak artifact'a ekle.
# Yeni içerik eklendiğinde bu dosyada elle slug listesi güncelleme gerektirmez.
mkdir -p "$DESTINATION/haberler"
cp "$ALO_DIR/haberler/alo186-article.css" "$DESTINATION/haberler/alo186-article.css"
find "$ALO_DIR/haberler" -mindepth 2 -maxdepth 2 -type f -name index.html -print \
  | sort \
  | while IFS= read -r index_file; do
      article_dir=$(dirname "$index_file")
      article_slug=$(basename "$article_dir")
      copy_page "$article_dir" "haberler/$article_slug"
    done

cp "$ALO_DIR/robots.txt" "$DESTINATION/robots.txt"
cp "$ALO_DIR/sitemap.xml" "$DESTINATION/sitemap.xml"
cp "$ALO_DIR/deployment/apache.htaccess" "$DESTINATION/.htaccess"
cp "$ALO_DIR/deployment/404.html" "$DESTINATION/404.html"
cp "$ALO_DIR/deployment/tailwindcss" "$DESTINATION/tailwindcss"
touch "$DESTINATION/.nojekyll"

if [ "$MODE" = "preview" ]; then
  cat > "$DESTINATION/index.html" <<'HTML'
<!doctype html>
<html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="refresh" content="0;url=./elektrik-portali/"><title>ALO186 Araçları</title>
<link rel="canonical" href="https://www.alo186.com/elektrik-portali"></head>
<body><p><a href="./elektrik-portali/">ALO186 elektrik araçlarını açın</a>.</p></body></html>
HTML
fi

# Kaynak dosyaların ve dağıtılabilir artifact'ın canonical originini tekilleştir.
# Haricî bağlantılara ve göreli rotalara dokunmaz.
find "$DESTINATION" -type f \( \
  -name '*.html' -o -name '*.xml' -o -name '*.txt' -o -name '*.json' -o \
  -name '*.js' -o -name '*.css' -o -name '.htaccess' \
\) -print | while IFS= read -r file; do
  sed -i "s#${LEGACY_ORIGIN}#${CANONICAL_ORIGIN}#g" "$file"
done

# Kod ve hassas operasyon dosyalarının statik pakete sızmasını engelle.
for forbidden in sureklilik-api tests deployment .github; do
  if [ -e "$DESTINATION/$forbidden" ]; then
    echo "Yasak klasör artifact'a dahil edildi: $forbidden" >&2
    exit 1
  fi
done

required_files="
elektrik-portali/index.html
edas-bul/index.html
karar-motoru/index.html
hesaplama/index.html
akilli-urun-secimi/index.html
isletme-surekliligi/index.html
fatura-analizi/index.html
hesaplama/yedek-guc/index.html
hesaplama/kesinti-maliyeti/index.html
haberler/alo186-article.css
robots.txt
sitemap.xml
.htaccess
404.html
tailwindcss
"

printf '%s\n' "$required_files" | while IFS= read -r file; do
  [ -z "$file" ] && continue
  if [ ! -f "$DESTINATION/$file" ]; then
    echo "Yayın dosyası eksik: $file" >&2
    exit 1
  fi
done

# Kaynaktaki her teknik makalenin artifact içinde bire bir bulunduğunu doğrula.
source_article_count=$(find "$ALO_DIR/haberler" -mindepth 2 -maxdepth 2 -type f -name index.html | wc -l | tr -d ' ')
artifact_article_count=$(find "$DESTINATION/haberler" -mindepth 2 -maxdepth 2 -type f -name index.html | wc -l | tr -d ' ')
if [ "$source_article_count" != "$artifact_article_count" ]; then
  echo "Makale paketleme sayısı uyuşmuyor: kaynak=$source_article_count artifact=$artifact_article_count" >&2
  exit 1
fi
find "$ALO_DIR/haberler" -mindepth 2 -maxdepth 2 -type f -name index.html -print \
  | sort \
  | while IFS= read -r index_file; do
      article_slug=$(basename "$(dirname "$index_file")")
      if [ ! -f "$DESTINATION/haberler/$article_slug/index.html" ]; then
        echo "Teknik makale artifact'ta eksik: $article_slug" >&2
        exit 1
      fi
    done

# Eski apex canonical sinyalinin artifact içinde yeniden ortaya çıkmasını engelle.
if grep -R -n -F "$LEGACY_ORIGIN" "$DESTINATION" --exclude=SHA256SUMS >/tmp/alo186-legacy-origin.txt 2>/dev/null; then
  cat /tmp/alo186-legacy-origin.txt >&2
  echo "Yayın paketinde eski apex canonical origin kaldı." >&2
  exit 1
fi

if ! grep -Fq "Sitemap: ${CANONICAL_ORIGIN}/sitemap.xml" "$DESTINATION/robots.txt"; then
  echo "robots.txt www sitemap adresini taşımıyor." >&2
  exit 1
fi

if ! grep -Fq "$CANONICAL_ORIGIN" "$DESTINATION/sitemap.xml"; then
  echo "sitemap.xml www canonical origin taşımıyor." >&2
  exit 1
fi

if ! grep -Fq "RewriteRule ^ https://www.alo186.com%{REQUEST_URI}" "$DESTINATION/.htaccess"; then
  echo ".htaccess www canonical yönlendirmesini taşımıyor." >&2
  exit 1
fi

# Güvenlik başlıklarının production overlay içinde kaybolmasını engelle.
for required_header in \
  'Strict-Transport-Security' \
  'X-Content-Type-Options' \
  'Content-Security-Policy' \
  'Referrer-Policy' \
  'Permissions-Policy'; do
  if ! grep -Fq "$required_header" "$DESTINATION/.htaccess"; then
    echo ".htaccess güvenlik başlığı eksik: $required_header" >&2
    exit 1
  fi
done

(
  cd "$DESTINATION"
  find . -type f ! -name SHA256SUMS -print0 \
    | sort -z \
    | xargs -0 sha256sum > SHA256SUMS
)

printf 'ALO186 statik paket hazır: %s (%s, canonical=%s, articles=%s)\n' \
  "$DESTINATION" "$MODE" "$CANONICAL_ORIGIN" "$artifact_article_count"
