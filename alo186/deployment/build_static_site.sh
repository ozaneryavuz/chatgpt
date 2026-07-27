#!/bin/sh
set -eu

DESTINATION="${1:-_site}"
MODE="${2:-preview}"
ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
ALO_DIR="$ROOT_DIR/alo186"

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

cp "$ALO_DIR/robots.txt" "$DESTINATION/robots.txt"
cp "$ALO_DIR/sitemap.xml" "$DESTINATION/sitemap.xml"
cp "$ALO_DIR/deployment/apache.htaccess" "$DESTINATION/.htaccess"
cp "$ALO_DIR/deployment/404.html" "$DESTINATION/404.html"
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
robots.txt
sitemap.xml
.htaccess
404.html
"

printf '%s\n' "$required_files" | while IFS= read -r file; do
  [ -z "$file" ] && continue
  if [ ! -f "$DESTINATION/$file" ]; then
    echo "Yayın dosyası eksik: $file" >&2
    exit 1
  fi
done

(
  cd "$DESTINATION"
  find . -type f ! -name SHA256SUMS -print0 \
    | sort -z \
    | xargs -0 sha256sum > SHA256SUMS
)

printf 'ALO186 statik paket hazır: %s (%s)\n' "$DESTINATION" "$MODE"
