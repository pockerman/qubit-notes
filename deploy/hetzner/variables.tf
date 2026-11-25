variable "name" {
  description = "The deployment's name: it names its server, volume, firewall and user pool"
  type        = string
  default     = "qubit-notes"
}

variable "location" {
  description = "The Hetzner location the server and its volume are in, e.g. nbg1, fsn1 or hel1"
  type        = string
  default     = "nbg1"
}

variable "server_type" {
  description = "The app's server; it runs the app, its Postgres and Caddy, so it wants 4 GB of memory"
  type        = string
  default     = "cx23"
}

variable "volume_gb" {
  description = "The volume that keeps everything the app has: its database, the students' uploads and the backups"
  type        = number
  default     = 20
}

variable "ssh_public_key" {
  description = "The operator's SSH public key, e.g. file(\"~/.ssh/id_ed25519.pub\"): the server takes no passwords"
  type        = string
}

variable "ssh_cidrs" {
  description = "Where the operator may reach the server with SSH from, e.g. [\"203.0.113.7/32\"]"
  type        = list(string)
  default     = ["0.0.0.0/0", "::/0"]
}

variable "domain" {
  description = "The app's address, e.g. notes.example.org, whose A record is the server_ipv4 output; <ip>.sslip.io if unset"
  type        = string
  default     = ""
}

variable "acme_email" {
  description = "Where Let's Encrypt writes about the app's certificate, e.g. when it can't be renewed; none if unset"
  type        = string
  default     = ""
}

variable "image" {
  description = "The app's image"
  type        = string
  default     = "ghcr.io/pockerman/qubit-notes"
}

variable "image_tag" {
  description = "The image's tag to run, e.g. main, sha-<commit> or a release's version"
  type        = string
  default     = "main"
}

variable "admins" {
  description = "Who may choose the AI's model and give the app its keys, from the app: students' usernames"
  type        = list(string)
  default     = []
}

variable "app_settings" {
  description = "More of the app's settings, e.g. { QUBIT_NOTES_LLM_MODEL = \"claude-sonnet-5-5\" }; never keys, which go in keys.env or the app"
  type        = map(string)
  default     = {}
}

variable "backup_days" {
  description = "How many of the nightly backups of the database the server keeps on its volume"
  type        = number
  default     = 7
}

variable "aws_region" {
  description = "The AWS region of the user pool students sign in with"
  type        = string
  default     = "eu-west-2"
}

variable "deletion_protection" {
  description = "Whether the volume, the server's address and the user pool are protected from being deleted, e.g. by terraform destroy"
  type        = bool
  default     = true
}

variable "self_sign_up" {
  description = "Whether students can sign themselves up; otherwise the operator makes their accounts"
  type        = bool
  default     = false
}
