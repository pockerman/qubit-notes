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

# On its own platform, the app's keys of the model providers, which the operator puts here, so they're never in the
# state; the app needs the key of its LLM provider (anthropic by default), and of its embedding model's if that isn't
# one that runs in the app:
#   aws secretsmanager put-secret-value --secret-id qubit-notes/provider-keys \
#     --secret-string '{"anthropic":"sk-ant-...","voyage":"pa-...","openai":"sk-..."}'
resource "aws_secretsmanager_secret" "provider_keys" {
  count = local.standalone ? 1 : 0

  name                    = "${var.name}/provider-keys"
  description             = "The app's keys of the model providers, by provider"
  recovery_window_in_days = 0
}

# Where the platform is gogi, the key gogi gave the app, which the operator puts here once gogi has registered it:
#   aws secretsmanager put-secret-value --secret-id qubit-notes/gogi-api-key --secret-string gogi_...
resource "aws_secretsmanager_secret" "gogi_api_key" {
  count = local.standalone ? 0 : 1

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
  standalone         = var.platform == "standalone"

  platform_settings = local.standalone ? {
    QUBIT_NOTES_PLATFORM     = "standalone"
    QUBIT_NOTES_FILES_BUCKET = aws_s3_bucket.material[0].bucket
    # for the bucket: the container takes the server's role from its metadata
    AWS_DEFAULT_REGION = var.region
    } : {
    QUBIT_NOTES_PLATFORM     = "gogi"
    QUBIT_NOTES_GATEWAY_URL  = var.gogi_gateway_url
    QUBIT_NOTES_GOGI_CA_FILE = "/etc/qubit-notes/gogi-ca.pem"
  }
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
    provider_keys = local.standalone ? aws_secretsmanager_secret.provider_keys[0].name : ""
    gogi_api_key  = local.standalone ? "" : aws_secretsmanager_secret.gogi_api_key[0].name
    registry      = aws_secretsmanager_secret.registry.name
    registry_host = split("/", var.image)[0]
    environment = merge(var.app_settings, local.platform_settings, {
      QUBIT_NOTES_AUTH                 = "cognito"
      QUBIT_NOTES_COGNITO_REGION       = var.region
      QUBIT_NOTES_COGNITO_USER_POOL_ID = aws_cognito_user_pool.students.id
      QUBIT_NOTES_COGNITO_CLIENT_ID    = aws_cognito_user_pool_client.app.id
      QUBIT_NOTES_COGNITO_DOMAIN       = local.cognito_domain
    })
  })

  lifecycle {
    precondition {
      condition     = local.standalone || (var.gogi_gateway_url != "" && var.gogi_ca_certificate != "")
      error_message = "Where the platform is gogi, set gogi_gateway_url and gogi_ca_certificate."
    }
  }
}
