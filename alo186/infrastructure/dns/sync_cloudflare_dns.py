#!/usr/bin/env python3
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
        data: dict[str, object] = {
            "type": self.type,
            "name": self.name,
            "content": self.content,
            "ttl": self.ttl,
        }
        if self.proxied is not None and self.type in {"A", "AAAA", "CNAME"}:
            data["proxied"] = self.proxied
        return data


def env(name: str, *, required: bool = False, default: str = "") -> str:
    value = os.getenv(name, default).strip()
    if required and not value:
        raise SystemExit(f"{name} zorunludur.")
    return value


def records() -> list[Record]:
    domain = env("ALO186_DNS_DOMAIN", default="alo186.com")
    render_hostname = env("ALO186_RENDER_API_HOSTNAME", required=True).rstrip(".")
    proxy = env("ALO186_CLOUDFLARE_PROXY", default="false").lower() in {"1", "true", "yes"}
    result = [
        Record("CNAME", f"api.{domain}", render_hostname, proxied=proxy),
        Record("CAA", domain, "0 issue letsencrypt.org"),
        Record("CAA", domain, "0 issue pki.goog"),
        Record(
            "TXT",
            f"_dmarc.{domain}",
            env(
                "ALO186_DMARC_VALUE",
                default="v=DMARC1; p=none; pct=100; rua=mailto:dmarc@alo186.com; adkim=r; aspf=r",
            ),
        ),
    ]

    dkim_host = env("POSTMARK_DKIM_HOST")
    dkim_value = env("POSTMARK_DKIM_VALUE")
    if dkim_host and dkim_value:
        result.append(Record("TXT", dkim_host.rstrip("."), dkim_value))

    return_path_host = env("POSTMARK_RETURN_PATH_HOST")
    return_path_value = env("POSTMARK_RETURN_PATH_VALUE")
    if return_path_host and return_path_value:
        result.append(
            Record("CNAME", return_path_host.rstrip("."), return_path_value.rstrip("."), proxied=False)
        )
    return result


class Cloudflare:
    def __init__(self, zone_id: str, token: str) -> None:
        self.zone_id = zone_id
        self.token = token

    def request(self, method: str, path: str, payload: dict | None = None) -> dict:
        body = json.dumps(payload).encode("utf-8") if payload is not None else None
        request = urllib.request.Request(
            f"{API_BASE}{path}",
            data=body,
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

    def upsert(self, record: Record, *, apply: bool) -> str:
        existing = self.find(record)
        desired = record.payload()
        if len(existing) > 1:
            raise RuntimeError(f"Birden fazla eş kayıt var: {record.type} {record.name}")
        if existing:
            current = existing[0]
            same = current.get("content") == record.content
            if record.proxied is not None:
                same = same and current.get("proxied") == record.proxied
            if same:
                return f"SAME   {record.type} {record.name}"
            if apply:
                self.request(
                    "PUT",
                    f"/zones/{self.zone_id}/dns_records/{current['id']}",
                    desired,
                )
            return f"UPDATE {record.type} {record.name}"
        if apply:
            self.request("POST", f"/zones/{self.zone_id}/dns_records", desired)
        return f"CREATE {record.type} {record.name}"


def main() -> None:
    parser = argparse.ArgumentParser(description="ALO186 Cloudflare DNS kayıtlarını idempotent uzlaştırır.")
    parser.add_argument("--apply", action="store_true", help="Değişiklikleri gerçekten uygula; varsayılan dry-run.")
    args = parser.parse_args()

    token = env("CLOUDFLARE_API_TOKEN", required=True)
    zone_id = env("CLOUDFLARE_ZONE_ID", required=True)
    client = Cloudflare(zone_id, token)

    print("Mod:", "APPLY" if args.apply else "DRY-RUN")
    for record in records():
        print(client.upsert(record, apply=args.apply))

    print("SPF kaydı güvenlik nedeniyle otomatik değiştirilmedi; mevcut tek SPF kaydına sağlayıcı include değeri elle birleştirilmelidir.")
    if not args.apply:
        print("Uygulamak için --apply kullanın.")


if __name__ == "__main__":
    main()
