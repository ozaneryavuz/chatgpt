from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass


API_BASE = "https://api.cloudflare.com/client/v4"


@dataclass(frozen=True)
class Record:
    type: str
    name: str
    content: str
    ttl: int = 60
    proxied: bool | None = None

    def payload(self) -> dict[str, object]:
        result: dict[str, object] = {
            "type": self.type,
            "name": self.name,
            "content": self.content,
            "ttl": self.ttl,
        }
        if self.proxied is not None and self.type in {"A", "AAAA", "CNAME"}:
            result["proxied"] = self.proxied
        return result


def env(name: str, *, required: bool = False, default: str = "") -> str:
    value = os.getenv(name, default).strip()
    if required and not value:
        raise SystemExit(f"{name} zorunludur.")
    return value


def desired_records() -> list[Record]:
    domain = env("ALO186_DNS_DOMAIN", default="alo186.com")
    render_hostname = env("ALO186_RENDER_API_HOSTNAME", required=True).rstrip(".")
    proxy = env("ALO186_CLOUDFLARE_PROXY", default="false").lower() in {"1", "true", "yes"}
    records = [
        Record("CNAME", f"api.{domain}", render_hostname, proxied=proxy),
        Record(
            "TXT",
            f"_dmarc.{domain}",
            env(
                "ALO186_DMARC_VALUE",
                default="v=DMARC1; p=none; pct=100; rua=mailto:dmarc@alo186.com; adkim=r; aspf=r",
            ),
            ttl=3600,
        ),
    ]

    optional = (
        ("CNAME", "POSTMARK_DKIM_HOST", "POSTMARK_DKIM_VALUE"),
        ("CNAME", "POSTMARK_RETURN_PATH_HOST", "POSTMARK_RETURN_PATH_VALUE"),
    )
    for record_type, host_key, value_key in optional:
        host, value = env(host_key), env(value_key)
        if bool(host) != bool(value):
            raise SystemExit(f"{host_key} ve {value_key} birlikte tanımlanmalıdır.")
        if host and value:
            records.append(Record(record_type, host.rstrip("."), value.rstrip("."), ttl=3600, proxied=False))
    return records


class Cloudflare:
    def __init__(self, zone_id: str, token: str) -> None:
        self.zone_id = zone_id
        self.token = token

    def request(self, method: str, path: str, payload: dict | None = None) -> dict:
        request = urllib.request.Request(
            f"{API_BASE}{path}",
            data=json.dumps(payload).encode("utf-8") if payload is not None else None,
            method=method,
            headers={
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                result = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Cloudflare API {exc.code}: {detail}") from exc
        if not result.get("success"):
            raise RuntimeError(f"Cloudflare API hatası: {result.get('errors')}")
        return result

    def find(self, record: Record) -> list[dict]:
        query = urllib.parse.urlencode({"type": record.type, "name": record.name, "per_page": 100})
        return self.request("GET", f"/zones/{self.zone_id}/dns_records?{query}").get("result", [])

    def reconcile(self, record: Record, *, apply: bool) -> str:
        existing = self.find(record)
        if len(existing) > 1:
            raise RuntimeError(f"Birden fazla eş DNS kaydı var: {record.type} {record.name}")
        payload = record.payload()
        if existing:
            current = existing[0]
            same = current.get("content") == record.content
            if record.proxied is not None:
                same = same and current.get("proxied") == record.proxied
            if same:
                return f"SAME   {record.type} {record.name}"
            if apply:
                self.request("PUT", f"/zones/{self.zone_id}/dns_records/{current['id']}", payload)
            return f"UPDATE {record.type} {record.name}"
        if apply:
            self.request("POST", f"/zones/{self.zone_id}/dns_records", payload)
        return f"CREATE {record.type} {record.name}"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="ALO186 Cloudflare DNS kayıtlarını sınırlandırılmış ve idempotent biçimde uzlaştırır."
    )
    parser.add_argument("--apply", action="store_true", help="Varsayılan dry-run yerine değişiklikleri uygula.")
    args = parser.parse_args()

    client = Cloudflare(
        env("CLOUDFLARE_ZONE_ID", required=True),
        env("CLOUDFLARE_API_TOKEN", required=True),
    )
    print("Mod:", "APPLY" if args.apply else "DRY-RUN")
    for record in desired_records():
        print(client.reconcile(record, apply=args.apply))
    print("SPF otomatik değiştirilmedi; mevcut tek SPF kaydında Postmark talimatı elle birleştirilmelidir.")


if __name__ == "__main__":
    main()
