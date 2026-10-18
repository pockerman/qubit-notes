variable "region" {
  description = "The AWS region qubit-notes runs in; CloudFront must support VPC origins there"
  type        = string
  default     = "eu-west-2"
}

variable "name" {
  description = "The deployment's name: it prefixes its resources and secrets"
  type        = string
  default     = "qubit-notes"
}

variable "gogi_gateway_url" {
  description = "Where the app calls gogi: gogi's gateway_address output, e.g. 203.0.113.9:443"
  type        = string
}

variable "gogi_ca_certificate" {
  description = "The certificate to check gogi's gateway against: gogi's ca_certificate output, e.g. file(\"gogi-ca.pem\")"
  type        = string
}

variable "image" {
  description = "The app's image"
  type        = string
  default     = "ghcr.io/pockerman/qubit-notes"
}

variable "image_tag" {
  description = "The image's tag to run, e.g. main, sha-<commit> or a release's version; the server runs it once restarted"
  type        = string
  default     = "main"
}

variable "app_settings" {
  description = "More of the app's settings, e.g. { QUBIT_NOTES_LLM_MODEL = \"claude-sonnet-5-5\" }"
  type        = map(string)
  default     = {}
}

variable "instance_type" {
  description = "The app's server"
  type        = string
  default     = "t3.small"
}

variable "db_instance_class" {
  description = "The app's Postgres server"
  type        = string
  default     = "db.t4g.micro"
}

variable "db_allocated_storage_gb" {
  description = "Postgres' storage; it grows on its own up to ten times this"
  type        = number
  default     = 20
}

variable "db_backup_days" {
  description = "How many days of Postgres' backups are kept"
  type        = number
  default     = 7
}

variable "deletion_protection" {
  description = "Whether Postgres and the user pool are protected from being deleted, e.g. by terraform destroy"
  type        = bool
  default     = true
}

variable "self_sign_up" {
  description = "Whether students can sign themselves up; otherwise the operator makes their accounts"
  type        = bool
  default     = false
}
