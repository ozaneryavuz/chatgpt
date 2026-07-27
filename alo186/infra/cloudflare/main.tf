locals {
  api_fqdn = "api.${var.zone_name}"
}

resource "cloudflare_dns_record" "api" {
  zone_id = var.zone_id
  name    = local.api_fqdn
  type    = "CNAME"
  content = var.render_api_hostname
  ttl     = 1
  proxied = var.api_proxied
  comment = "ALO186 Elektrik Sürekliliği API — Render origin"
  tags    = ["owner:alo186", "service:continuity-api"]
}

resource "cloudflare_dns_record" "postmark_dkim" {
  count   = var.postmark_dkim_name != "" && var.postmark_dkim_content != "" ? 1 : 0
  zone_id = var.zone_id
  name    = var.postmark_dkim_name
  type    = "CNAME"
  content = var.postmark_dkim_content
  ttl     = 3600
  proxied = false
  comment = "Postmark DKIM doğrulaması"
  tags    = ["owner:alo186", "service:email"]
}

resource "cloudflare_dns_record" "postmark_return_path" {
  count   = var.postmark_return_path_name != "" && var.postmark_return_path_content != "" ? 1 : 0
  zone_id = var.zone_id
  name    = var.postmark_return_path_name
  type    = "CNAME"
  content = var.postmark_return_path_content
  ttl     = 3600
  proxied = false
  comment = "Postmark custom Return-Path doğrulaması"
  tags    = ["owner:alo186", "service:email"]
}

resource "cloudflare_dns_record" "dmarc" {
  count   = var.manage_dmarc ? 1 : 0
  zone_id = var.zone_id
  name    = "_dmarc.${var.zone_name}"
  type    = "TXT"
  content = var.dmarc_content
  ttl     = 3600
  proxied = false
  comment = "ALO186 DMARC politikası"
  tags    = ["owner:alo186", "service:email-security"]
}
