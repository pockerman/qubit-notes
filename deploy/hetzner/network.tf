# The server's address is its own resource, so it stays the same when the server is replaced: the app's domain, its
# certificate and the user pool's callback all name it
resource "hcloud_primary_ip" "server" {
  name              = var.name
  type              = "ipv4"
  location          = var.location
  auto_delete       = false
  delete_protection = var.deletion_protection
}

resource "hcloud_firewall" "server" {
  name = var.name

  # the app, over HTTPS, and plain HTTP, which Caddy sends on to HTTPS and Let's Encrypt checks the domain with
  rule {
    direction  = "in"
    protocol   = "tcp"
    port       = "80"
    source_ips = ["0.0.0.0/0", "::/0"]
  }

  rule {
    direction  = "in"
    protocol   = "tcp"
    port       = "443"
    source_ips = ["0.0.0.0/0", "::/0"]
  }

  # HTTP/3
  rule {
    direction  = "in"
    protocol   = "udp"
    port       = "443"
    source_ips = ["0.0.0.0/0", "::/0"]
  }

  rule {
    direction  = "in"
    protocol   = "tcp"
    port       = "22"
    source_ips = var.ssh_cidrs
  }
}

locals {
  domain  = var.domain != "" ? var.domain : "${replace(hcloud_primary_ip.server.ip_address, ".", "-")}.sslip.io"
  app_url = "https://${local.domain}/"
}
