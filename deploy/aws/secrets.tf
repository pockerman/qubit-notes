# What the server reads each time it starts the app: its settings, as a parameter, and its secrets
resource "aws_secretsmanager_secret" "database" {
  name                    = "${var.name}/database"
  description             = "The app's Postgres: host, port, database, username and password"
  recovery_window_in_days = 0
}

resource "aws_secretsmanager_secret_version" "database" {
  secret_id = aws_secretsmanager_secret.database.id
  secret_string = jsonencode({
    host     = aws_db_instance.app.address
    port     = aws_db_instance.app.port
    dbname   = aws_db_instance.app.db_name
    username = aws_db_instance.app.username
    password = random_password.database.result
  })
}

# The key gogi gave the app, which the operator puts here once gogi has registered it, so it's never in the state:
#   aws secretsmanager put-secret-value --secret-id qubit-notes/gogi-api-key --secret-string gogi_...
resource "aws_secretsmanager_secret" "gogi_api_key" {
  name                    = "${var.name}/gogi-api-key"
  description             = "The key gogi gave the app"
  recovery_window_in_days = 0
}

# Where the image is private, a token that can read it, put by the operator:
#   aws secretsmanager put-secret-value --secret-id qubit-notes/registry \
#     --secret-string '{"username":"<GitHub user>","token":"<token with read:packages>"}'
resource "aws_secretsmanager_secret" "registry" {
  name                    = "${var.name}/registry"
  description             = "A token for the registry of the app's image, if it's private"
  recovery_window_in_days = 0
}

locals {
  settings_parameter = "/${var.name}/settings"
}

resource "aws_ssm_parameter" "settings" {
  name        = local.settings_parameter
  description = "The app's settings, which its server reads when it starts the app"
  type        = "String"
  tier        = "Standard"
  value = jsonencode({
    image         = "${var.image}:${var.image_tag}"
    gogi_ca       = var.gogi_ca_certificate
    region        = var.region
    database      = aws_secretsmanager_secret.database.name
    gogi_api_key  = aws_secretsmanager_secret.gogi_api_key.name
    registry      = aws_secretsmanager_secret.registry.name
    registry_host = split("/", var.image)[0]
    environment = merge(var.app_settings, {
      QUBIT_NOTES_GATEWAY_URL          = var.gogi_gateway_url
      QUBIT_NOTES_GOGI_CA_FILE         = "/etc/qubit-notes/gogi-ca.pem"
      QUBIT_NOTES_AUTH                 = "cognito"
      QUBIT_NOTES_COGNITO_REGION       = var.region
      QUBIT_NOTES_COGNITO_USER_POOL_ID = aws_cognito_user_pool.students.id
      QUBIT_NOTES_COGNITO_CLIENT_ID    = aws_cognito_user_pool_client.app.id
      QUBIT_NOTES_COGNITO_DOMAIN       = local.cognito_domain
    })
  })
}
