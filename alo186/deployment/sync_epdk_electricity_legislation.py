#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import difflib
import hashlib
import html
import json
import re
import sys
import unicodedata
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

SOURCE_URL = "https://www.epdk.gov.tr/Detay/Icerik/23-2-3/elektrik-piyasasi"
SOURCE_HOSTS = {"epdk.gov.tr", "www.epdk.gov.tr"}
MIN_ENTRIES = 150
REQUIRED_TEXT = (
    "6446",
    "Elektrik Piyasası Tüketici Hizmetleri Yönetmeliği",
    "Elektrik Piyasasında Depolama Faaliyetleri Yönetmeliği",
    "Elektrik Piyasasında Toplayıcılık Faaliyeti Yönetmeliği",
    "Mülga",
)
CATEGORY_ORDER = (
    "Kanunlar", "Bakanlar Kurulu Kararları", "Mahkeme Kararları", "Yönetmelikler",
    "Tebliğler", "Usul ve Esaslar", "Yöntem ve Metodolojiler", "Kurul Kararları",
    "Tarife Kurul Kararları", "Diğer Mevzuatlar", "Mülga Tebliğler", "Mülga Yönetmelikler",
)
CHUNKS = (
    ("catalog-core.json", CATEGORY_ORDER[0:4]),
    ("catalog-rules.json", CATEGORY_ORDER[4:7]),
    ("catalog-decisions.json", CATEGORY_ORDER[7:9]),
    ("catalog-related.json", CATEGORY_ORDER[9:10]),
    ("catalog-historical.json", CATEGORY_ORDER[10:12]),
)
CATEGORY_MAP = {
    "kanunlar": "Kanunlar",
    "bakanlar kurulu kararlari": "Bakanlar Kurulu Kararları",
    "mahkeme kararlari": "Mahkeme Kararları",
    "yonetmelikler": "Yönetmelikler",
    "tebligler": "Tebliğler",
    "usul ve esaslar": "Usul ve Esaslar",
    "yontem ve metodolojiler": "Yöntem ve Metodolojiler",
    "elektrik piyasasi kurul kararlari": "Kurul Kararları",
    "kurul kararlari": "Kurul Kararları",
    "elektrik piyasasi tarife kurul kararlari": "Tarife Kurul Kararları",
    "tarife kurul kararlari": "Tarife Kurul Kararları",
    "elektrik piyasasi diger mevzuatlar": "Diğer Mevzuatlar",
    "diger mevzuatlar": "Diğer Mevzuatlar",
    "mulga tebligler": "Mülga Tebliğler",
    "mulga yonetmelikler": "Mülga Yönetmelikler",
}
GENERIC = {
    "usul ve esaslar", "kurul kararlari", "tarifeler", "diger", "digerleri", "basvuru",
    "yatirim", "edas", "gts", "teias", "epias", "euas", "gelir gereksinimi",
    "gelir tavani", "hesap plani", "hesap plani aciklamasi", "yenilenebilir enerji kaynaklari",
    "nukleer guc santralleri", "enerji verimliligi", "jeotermal kaynaklar", "ruzgar enerjisi",
    "dagitim faaliyeti", "iletim faaliyeti", "serbest tuketici", "yekdem", "osb ve eb",
    "mulga yonetmelikler ve tebligler",
}


def clean(value: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(value or "").replace("\xa0", " ")).strip(" \t\r\n-*•")


def norm(value: str) -> str:
    value = unicodedata.normalize("NFKD", clean(value).lower()).replace("ı", "i")
    return re.sub(r"[^a-z0-9]+", " ", "".join(c for c in value if not unicodedata.combining(c))).strip()


class Parser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.active = False
        self.done = False
        self.heading: str | None = None
        self.heading_text: list[str] = []
        self.category: str | None = None
        self.li: list[list[str]] = []
        self.rows: list[list[str]] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        tag = tag.lower()
        if tag in {"h2", "h3", "h4", "h5"}:
            self.heading, self.heading_text = tag, []
        elif tag == "li" and self.active and not self.done:
            self.li.append([])

    def handle_data(self, data: str) -> None:
        if self.heading:
            self.heading_text.append(data)
        if self.li and self.active and not self.done:
            self.li[-1].append(data)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if self.heading == tag:
            key = norm(" ".join(self.heading_text))
            if tag == "h2":
                if "elektrik piyasasi mevzuat listesi" in key:
                    self.active = True
                elif self.active and key in {"hakkimizda", "iletisim"}:
                    self.active, self.done = False, True
            elif self.active and not self.done and key in CATEGORY_MAP:
                self.category = CATEGORY_MAP[key]
            self.heading, self.heading_text = None, []
        elif tag == "li" and self.li and self.active and not self.done:
            title = clean(" ".join(self.li.pop()))
            if self.category and title:
                self.rows.append([title, self.category, status(title, self.category)])


def status(title: str, category: str) -> str:
    key = norm(title)
    if category.startswith("Mülga") or "mulga" in key:
        return "mulga"
    if any(x in key for x in ("eski hali", "eski versiyon", "ilk hali", "ilk versiyon", "2006 oncesi")):
        return "tarihsel"
    if "degisiklik" in key or "degistirilmesine" in key:
        return "degisiklik"
    return "resmi-listede"


def fetch(url: str, source_file: Path | None) -> str:
    if source_file:
        return source_file.read_text(encoding="utf-8")
    host = urllib.parse.urlparse(url).hostname
    if host not in SOURCE_HOSTS:
        raise RuntimeError(f"Resmî olmayan kaynak reddedildi: {host}")
    request = urllib.request.Request(url, headers={
        "User-Agent": "ALO186-Mevzuat-Radar/1.0 (+https://www.alo186.com/mevzuat/)",
        "Accept": "text/html,application/xhtml+xml",
    })
    with urllib.request.urlopen(request, timeout=45) as response:
        if response.status != 200:
            raise RuntimeError(f"EPDK kaynağı HTTP {response.status} döndürdü")
        if "html" not in response.headers.get("Content-Type", "").lower():
            raise RuntimeError("EPDK kaynağı HTML döndürmedi")
        return response.read().decode("utf-8", errors="replace")


def parse(source: str) -> list[list[str]]:
    parser = Parser()
    parser.feed(source)
    parser.close()
    seen, rows = set(), []
    for title, category, row_status in parser.rows:
        key = norm(title)
        if not 9 <= len(title) <= 520 or key in GENERIC or key.startswith("image"):
            continue
        unique = f"{norm(category)}::{key}"
        if unique in seen:
            continue
        seen.add(unique)
        rows.append([title, category, row_status])
    order = {name: i for i, name in enumerate(CATEGORY_ORDER)}
    rows.sort(key=lambda row: (order.get(row[1], 999), norm(row[0])))
    return rows


def validate(source: str, rows: list[list[str]]) -> None:
    plain = clean(re.sub(r"<[^>]+>", " ", source))
    missing = [token for token in REQUIRED_TEXT if token not in plain]
    if missing:
        raise RuntimeError(f"Zorunlu kaynak işaretleri eksik: {missing}")
    if len(rows) < MIN_ENTRIES:
        raise RuntimeError(f"Kapsam eşiği sağlanmadı: {len(rows)} < {MIN_ENTRIES}")
    categories = {row[1] for row in rows}
    required = {"Kanunlar", "Yönetmelikler", "Tebliğler", "Usul ve Esaslar", "Kurul Kararları", "Tarife Kurul Kararları", "Diğer Mevzuatlar", "Mülga Tebliğler", "Mülga Yönetmelikler"}
    if not required <= categories:
        raise RuntimeError(f"Kategori kapsamı eksik: {sorted(required - categories)}")


def load_rows(meta_path: Path) -> list[list[str]]:
    if not meta_path.is_file():
        return []
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    if isinstance(meta.get("entries"), list):
        return [[e["title"], e["category"], e["status"]] if isinstance(e, dict) else e for e in meta["entries"]]
    rows = []
    for item in meta.get("files", []):
        path = meta_path.parent / item["path"]
        if not path.is_file():
            raise RuntimeError(f"Mevcut katalog parçası eksik: {path}")
        rows.extend(json.loads(path.read_text(encoding="utf-8")).get("entries", []))
    return rows


def fp(rows: list[list[str]]) -> str:
    return hashlib.sha256(json.dumps(rows, ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()


def counts(rows: list[list[str]]) -> dict[str, int]:
    result = {name: 0 for name in CATEGORY_ORDER}
    for _, category, _ in rows:
        result[category] = result.get(category, 0) + 1
    return {name: value for name, value in result.items() if value}


def diff(old: list[list[str]], new: list[list[str]]) -> dict:
    old_map = {f"{norm(r[1])}::{norm(r[0])}": r for r in old}
    new_map = {f"{norm(r[1])}::{norm(r[0])}": r for r in new}
    added_keys, removed_keys = set(new_map) - set(old_map), set(old_map) - set(new_map)
    renamed, used_added, used_removed = [], set(), set()
    for removed_key in sorted(removed_keys):
        before, best, score = old_map[removed_key], None, 0.0
        for added_key in added_keys - used_added:
            after = new_map[added_key]
            if before[1] != after[1]:
                continue
            candidate = difflib.SequenceMatcher(None, norm(before[0]), norm(after[0])).ratio()
            if candidate > score:
                best, score = added_key, candidate
        if best and score >= .82:
            renamed.append({"before": old_map[removed_key], "after": new_map[best], "similarity": round(score, 3)})
            used_added.add(best)
            used_removed.add(removed_key)
    added = [new_map[k] for k in sorted(added_keys - used_added)]
    removed = [old_map[k] for k in sorted(removed_keys - used_removed)]
    changed = [{"before": old_map[k], "after": new_map[k]} for k in sorted(set(old_map) & set(new_map)) if old_map[k][2] != new_map[k][2]]
    return {"changed": bool(added or removed or renamed or changed), "addedCount": len(added), "removedCount": len(removed), "renamedCount": len(renamed), "changedCount": len(changed), "added": added, "removed": removed, "renamed": renamed, "modified": changed}


def write(meta_path: Path, rows: list[list[str]], checked_at: str, source_url: str) -> None:
    meta_path.parent.mkdir(parents=True, exist_ok=True)
    category_counts = counts(rows)
    files = []
    for filename, categories in CHUNKS:
        chunk_rows = [row for row in rows if row[1] in categories]
        (meta_path.parent / filename).write_text(json.dumps({"entryColumns": ["title", "category", "status"], "entries": chunk_rows}, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
        files.append({"path": filename, "count": len(chunk_rows), "categories": list(categories)})
    meta = {
        "schemaVersion": 3,
        "name": "ALO186 Elektrik Mevzuat Atlası",
        "source": {"publisher": "Enerji Piyasası Düzenleme Kurumu (EPDK)", "url": source_url, "title": "Elektrik Piyasası Mevzuat Listesi", "checkedAt": checked_at, "officialTextPrevails": True},
        "coverage": {"basis": "EPDK elektrik piyasası ana mevzuat listesindeki başlıkların tekilleştirilmiş kullanıcı odaklı indeksi", "uniqueEntryCount": len(rows), "duplicateTitlesCollapsed": True, "fullLegalTextMirrored": False, "historicalEntriesIncluded": True, "dailyOfficialDiffPlanned": True, "sourceFingerprint": fp(rows)},
        "categories": [{"name": name, "count": value} for name, value in category_counts.items()],
        "files": files,
    }
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")


def main() -> int:
    cli = argparse.ArgumentParser(description="EPDK Elektrik Piyasası mevzuat başlıklarını fail-closed biçimde senkronize eder.")
    cli.add_argument("--url", default=SOURCE_URL)
    cli.add_argument("--source-file", type=Path)
    cli.add_argument("--output", type=Path, required=True)
    cli.add_argument("--report", type=Path, required=True)
    cli.add_argument("--checked-at", default=dt.date.today().isoformat())
    cli.add_argument("--no-write", action="store_true")
    args = cli.parse_args()
    old = load_rows(args.output)
    source = fetch(args.url, args.source_file)
    rows = parse(source)
    validate(source, rows)
    changes = diff(old, rows)
    report = {"ok": True, "source": args.url, "checkedAt": args.checked_at, "entryCount": len(rows), "categoryCounts": counts(rows), "sourceFingerprint": fp(rows), **changes}
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if changes["changed"] and not args.no_write:
        write(args.output, rows, args.checked_at, args.url)
    print(json.dumps(report, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        raise
