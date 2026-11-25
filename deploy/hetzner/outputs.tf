output "url" {
  description = "Where students open the app"
  value       = local.app_url
}

output "server_ipv4" {
  description = "The server's address, which stays when the server is replaced: the A record of the app's domain"
  value       = hcloud_primary_ip.server.ip_address
}

output "ssh" {
  description = "How the operator reaches the server"
  value       = "ssh root@${hcloud_primary_ip.server.ip_address}"
}

output "user_pool_id" {
  description = "The students' user pool, e.g. for: aws cognito-idp admin-create-user --user-pool-id <user_pool_id>"
  value       = aws_cognito_user_pool.students.id
}

output "cognito_domain" {
  description = "Where students sign in"
  value       = local.cognito_domain
}
