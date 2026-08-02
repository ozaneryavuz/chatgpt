from __future__ import annotations

import hashlib
import html
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

TOOL_DIR = Path(__file__).resolve().parent
DEFAULT_CONFIG = TOOL_DIR / "config.json"
DEFAULT_QUEUE = TOOL_DIR / "queue.json"
READY_STATES = {"ready", "drafted", "validated", "sites-ready", "published"}
DRAFT_STATES = {"drafted", "validated", "sites-ready", "published"}
STOPWORDS = {"ama", "ancak", "bir", "bu", "bunu", "da", "daha", "de", "en", "gibi", "için", "ile", "ise", "kaç", "kadar", "mı", "mi", "mu", "mü", "nasıl", "ne", "neden", "olarak", "olan", "olmalı", "olur", "ve", "veya", "ya", "yani", "yapılır", "gerekir", "nedir", "hangi", "sonra", "önce", "var", "yok"}
SYNONYMS = {"akü": "batarya", "aku": "batarya", "battery": "batarya", "şarj": "sarj", "şarjı": "sarj", "kaçak": "rcd", "rolesi": "rcd", "rölesi": "rcd", "gerilim": "voltaj", "volt": "voltaj", "jenerator": "jeneratör", "güneş": "ges", "fotovoltaik": "ges", "depolama": "bess", "sanal": "vpp", "toplayıcı": "vpp"}


@dataclass(frozen=True)
class Finding:
    level: str
    code: str
    subject: str
    detail: str


@dataclass(frozen=True)
class InventoryItem:
    route: str
    canonical: str
    title: str
    h1: str
    description: str
    source: str
    schema_types: tuple[str, ...]


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"Dosya bulunamadı: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Geçersiz JSON: {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise SystemExit(f"JSON kökü nesne olmalı: {path}")
    return value


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def stable_hash(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def normalize_route(value: str) -> str:
    route = (value or "").strip()
    if not route:
        return ""
    parsed = urlparse(route)
    route = parsed.path if parsed.scheme or parsed.netloc else route
    route = re.sub(r"/{2,}", "/", "/" + route.lstrip("/"))
    if route != "/" and route.endswith("/index.html"):
        route = route[:-10]
    elif route != "/" and route.endswith(".html"):
        route = route[:-5]
    return route if route == "/" else route.rstrip("/")


def route_to_source(repo: Path, route: str) -> Path:
    route = normalize_route(route)
    return repo / "alo186" / ("index.html" if route == "/" else route.lstrip("/") + "/index.html")


def first_match(pattern: str, text: str) -> str:
    match = re.search(pattern, text, re.I | re.S)
    return html.unescape(match.group(1).strip()) if match else ""


def strip_markup(text: str) -> str:
    text = re.sub(r"<(script|style)\b.*?</\1>", " ", text, flags=re.I | re.S)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", text))).strip()


def extract_jsonld(text: str) -> list[Any]:
    out: list[Any] = []
    for block in re.findall(r'<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', text, re.I | re.S):
        try:
            out.append(json.loads(html.unescape(block.strip())))
        except json.JSONDecodeError:
            pass
    return out


def collect_schema_types(node: Any) -> set[str]:
    out: set[str] = set()
    if isinstance(node, dict):
        value = node.get("@type")
        if isinstance(value, str):
            out.add(value)
        elif isinstance(value, list):
            out.update(str(item) for item in value if isinstance(item, (str, int, float)))
        for child in node.values():
            out.update(collect_schema_types(child))
    elif isinstance(node, list):
        for child in node:
            out.update(collect_schema_types(child))
    return out


def tokens(value: str) -> set[str]:
    out: set[str] = set()
    for token in re.findall(r"[a-z0-9çğıöşü]+", (value or "").casefold()):
        token = SYNONYMS.get(token, token)
        if len(token) >= 3 and token not in STOPWORDS:
            out.add(token)
    return out


def similarity(left: str, right: str) -> float:
    a, b = tokens(left), tokens(right)
    return len(a & b) / len(a | b) if a and b else 0.0
