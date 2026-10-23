output "url" {
  description = "Where students open the app"
  value       = local.app_url
}

output "server_public_ip" {
  description = "Where the app calls out from, e.g. to gogi: add it to gogi's client_cidrs, as <ip>/32"
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

output "provider_keys_secret" {
  description = "On its own platform, where to put the app's keys of the model providers"
  value       = one(aws_secretsmanager_secret.provider_keys[*].name)
}

output "material_bucket" {
  description = "On its own platform, the bucket of the students' uploads"
  value       = one(aws_s3_bucket.material[*].bucket)
}

output "gogi_api_key_secret" {
  description = "Where the platform is gogi, where to put the key gogi gave the app"
  value       = one(aws_secretsmanager_secret.gogi_api_key[*].name)
}

output "registry_secret" {
  description = "Where to put a token for the image, if it's private"
  value       = aws_secretsmanager_secret.registry.name
}
