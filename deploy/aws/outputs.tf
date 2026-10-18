output "url" {
  description = "Where students open the app"
  value       = local.app_url
}

output "server_public_ip" {
  description = "Where the app calls gogi from: add it to gogi's client_cidrs, as <ip>/32"
  value       = aws_eip.server.public_ip
}

output "instance_id" {
  description = "The server, to reach with: aws ssm start-session --target <instance_id>"
  value       = aws_instance.server.id
}

output "user_pool_id" {
  description = "The students' user pool, e.g. for: aws cognito-idp admin-create-user --user-pool-id <user_pool_id>"
  value       = aws_cognito_user_pool.students.id
}

output "cognito_domain" {
  description = "Where students sign in"
  value       = local.cognito_domain
}

output "gogi_api_key_secret" {
  description = "Where to put the key gogi gave the app"
  value       = aws_secretsmanager_secret.gogi_api_key.name
}

output "registry_secret" {
  description = "Where to put a token for the image, if it's private"
  value       = aws_secretsmanager_secret.registry.name
}
