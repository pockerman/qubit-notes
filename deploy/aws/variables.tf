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

variable "platform" {
  description = "What keeps the students' material, searches it and calls the AI: the app itself (standalone), or gogi"
  type        = string
  default     = "standalone"

  validation {
    condition     = contains(["standalone", "gogi"], var.platform)
    error_message = "platform is standalone or gogi."
  }
}

variable "material_versions_days" {
  description = "On its own platform, how many days the app's bucket keeps an upload that was deleted or replaced"
  type        = number
  default     = 30
}

variable "gogi_gateway_url" {
  description = "Where the platform is gogi, where the app calls it: gogi's gateway_address output, e.g. 203.0.113.9:443"
  type        = string
  default     = ""
}

variable "gogi_ca_certificate" {
  description = "Where the platform is gogi, the certificate to check its gateway against: gogi's ca_certificate output, e.g. file(\"gogi-ca.pem\")"
  type        = string
  default     = ""
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
  description = "More of the app's settings, e.g. { QUBIT_NOTES_LLM_MODEL = \"claude-sonnet-5-5\", QUBIT_NOTES_EMBEDDING_MODEL = \"voyage-3.5-lite\" }"
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
