output "api_fqdn" {
  value       = cloudflare_dns_record.api.name
  description = "ALO186 API tam alan adı."
}

output "api_origin" {
  value       = cloudflare_dns_record.api.content
  description = "Render origin hostname."
}

output "smtp_record_names" {
  value       = [for record in cloudflare_dns_record.smtp : record.name]
  description = "Terraform tarafından yönetilen Postmark DNS kayıtları."
}
