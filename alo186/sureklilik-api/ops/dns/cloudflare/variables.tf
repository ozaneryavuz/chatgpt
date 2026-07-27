variable "cloudflare_api_token" {
  type        = string
  sensitive   = true
  description = "Zone DNS edit yetkili dar kapsamlı Cloudflare API tokenı."
}

variable "cloudflare_zone_id" {
  type        = string
  description = "alo186.com Cloudflare zone ID."
}

variable "zone_name" {
  type        = string
  default     = "alo186.com"
  description = "DNS zone adı."
}

variable "api_origin_hostname" {
  type        = string
  description = "Render tarafından verilen alo186-api.onrender.com benzeri origin host."
}

variable "proxy_api" {
  type        = bool
  default     = false
  description = "İlk TLS doğrulamasında false tutun; Render custom domain doğrulandıktan sonra isteğe bağlı true yapın."
}

variable "dmarc_value" {
  type        = string
  default     = "v=DMARC1; p=none; rua=mailto:dmarc@alo186.com; adkim=s; aspf=s; pct=100"
  description = "İlk gözlem politikası. Raporlar temizlendikten sonra quarantine/reject'e yükseltilir."
}

variable "smtp_dns_records" {
  description = "Postmark panelinin verdiği DKIM, return-path ve doğrulama kayıtları."
  type = map(object({
    type     = string
    name     = string
    content  = string
    ttl      = optional(number, 3600)
    proxied  = optional(bool, false)
    priority = optional(number)
  }))
  default = {}
}
