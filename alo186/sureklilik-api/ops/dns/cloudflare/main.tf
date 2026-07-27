resource "cloudflare_dns_record" "api" {
  zone_id = var.cloudflare_zone_id
  name    = "api.${var.zone_name}"
  type    = "CNAME"
  content = var.api_origin_hostname
  proxied = var.proxy_api
  ttl     = var.proxy_api ? 1 : 300
  comment = "ALO186 Elektrik Sürekliliği API production origin"
}

resource "cloudflare_dns_record" "dmarc" {
  zone_id = var.cloudflare_zone_id
  name    = "_dmarc.${var.zone_name}"
  type    = "TXT"
  content = var.dmarc_value
  proxied = false
  ttl     = 3600
  comment = "ALO186 transactional email DMARC policy"
}

resource "cloudflare_dns_record" "smtp" {
  for_each = var.smtp_dns_records

  zone_id  = var.cloudflare_zone_id
  name     = each.value.name
  type     = upper(each.value.type)
  content  = each.value.content
  proxied  = each.value.proxied
  ttl      = each.value.proxied ? 1 : each.value.ttl
  priority = each.value.priority
  comment  = "ALO186 Postmark sender authentication: ${each.key}"
}
