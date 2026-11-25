# The server runs the app, its Postgres and Caddy with Docker Compose (compose.yaml), as qubit-notes.service. Everything
# they keep is on the volume, so the server can be replaced at any time, as it is when its settings change: the
# volume and the address are kept, and taken by the new server
resource "hcloud_ssh_key" "operator" {
  name       = var.name
  public_key = var.ssh_public_key
}

resource "hcloud_volume" "data" {
  name              = "${var.name}-data"
  size              = var.volume_gb
  location          = var.location
  format            = "ext4"
  delete_protection = var.deletion_protection
}

locals {
  # the app's settings that aren't secret; its secrets are made on the server (start-qubit-notes.sh)
  settings = merge(var.app_settings, {
    QUBIT_NOTES_PLATFORM             = "standalone"
    QUBIT_NOTES_ADMINS               = join(",", var.admins)
    QUBIT_NOTES_AUTH                 = "cognito"
    QUBIT_NOTES_COGNITO_REGION       = var.aws_region
    QUBIT_NOTES_COGNITO_USER_POOL_ID = aws_cognito_user_pool.students.id
    QUBIT_NOTES_COGNITO_CLIENT_ID    = aws_cognito_user_pool_client.app.id
    QUBIT_NOTES_COGNITO_DOMAIN       = local.cognito_domain
  })
}

resource "hcloud_server" "app" {
  name         = var.name
  server_type  = var.server_type
  location     = var.location
  image        = "ubuntu-24.04"
  ssh_keys     = [hcloud_ssh_key.operator.id]
  firewall_ids = [hcloud_firewall.server.id]

  public_net {
    ipv4_enabled = true
    ipv4         = hcloud_primary_ip.server.id
    ipv6_enabled = true
  }

  user_data = templatefile("${path.module}/cloud-init.yaml", {
    volume_device = "/dev/disk/by-id/scsi-0HC_Volume_${hcloud_volume.data.id}"
    settings      = base64encode(join("", [for key, value in local.settings : "${key}=${value}\n"]))
    compose = base64encode(templatefile("${path.module}/compose.yaml", {
      image = "${var.image}:${var.image_tag}"
    }))
    caddyfile = base64encode(templatefile("${path.module}/Caddyfile", {
      domain     = local.domain
      acme_email = var.acme_email
    }))
    start_script  = base64encode(file("${path.module}/start-qubit-notes.sh"))
    backup_script = base64encode(templatefile("${path.module}/backup-qubit-notes.sh", { backup_days = var.backup_days }))
  })

  labels = { project = var.name }
}

resource "hcloud_volume_attachment" "data" {
  volume_id = hcloud_volume.data.id
  server_id = hcloud_server.app.id
  # cloud-init mounts it, where the app looks for it
  automount = false
}
