variable "cloudflare_api_token" {
  description = "Alo186 zone için en az yetkili Cloudflare DNS API tokenı."
  type        = string
  sensitive   = true
}

variable "zone_id" {
  description = "alo186.com Cloudflare zone ID."
  type        = string
  sensitive   = true
}

variable "zone_name" {
  description = "DNS zone adı."
  type        = string
  default     = "alo186.com"
}

variable "render_api_hostname" {
  description = "Render tarafından verilen API hostname; örn. alo186-continuity-api.onrender.com."
  type        = string
}

variable "api_proxied" {
  description = "Render custom-domain doğrulaması tamamlanana kadar false tutulmalıdır."
  type        = bool
  default     = false
}

variable "postmark_dkim_name" {
  description = "Postmark panelindeki DKIM CNAME kayıt adı. Boşsa oluşturulmaz."
  type        = string
  default     = ""
}

variable "postmark_dkim_content" {
  description = "Postmark DKIM CNAME hedefi."
  type        = string
  default     = ""
}

variable "postmark_return_path_name" {
  description = "Postmark Return-Path CNAME kayıt adı. Boşsa oluşturulmaz."
  type        = string
  default     = ""
}

variable "postmark_return_path_content" {
  description = "Postmark Return-Path CNAME hedefi."
  type        = string
  default     = ""
}

variable "manage_dmarc" {
  description = "Mevcut DMARC kaydı yoksa true yapın."
  type        = bool
  default     = false
}

variable "dmarc_content" {
  description = "DMARC TXT içeriği. İlk aşamada p=none ile gözlem önerilir."
  type        = string
  default     = "v=DMARC1; p=none; rua=mailto:dmarc@alo186.com; adkim=s; aspf=s"
}
