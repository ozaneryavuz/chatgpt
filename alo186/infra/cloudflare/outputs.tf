output "api_hostname" {
  value       = cloudflare_dns_record.api.name
  description = "Üretim API hostname."
}

output "api_target" {
  value       = cloudflare_dns_record.api.content
  description = "Render origin CNAME hedefi."
}

output "api_proxied" {
  value       = cloudflare_dns_record.api.proxied
  description = "Cloudflare proxy durumu."
}
