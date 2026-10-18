# Students sign in on the user pool's own pages, at an amazoncognito.com address, with the authorization code flow
# and PKCE (frontend/src/auth.ts). A student is their username, as in "share with tom"
resource "random_string" "domain" {
  length  = 6
  upper   = false
  special = false
}

resource "aws_cognito_user_pool" "students" {
  name                = var.name
  deletion_protection = var.deletion_protection ? "ACTIVE" : "INACTIVE"

  username_configuration {
    case_sensitive = false
  }

  admin_create_user_config {
    allow_admin_create_user_only = !var.self_sign_up
  }

  auto_verified_attributes = ["email"]

  account_recovery_setting {
    recovery_mechanism {
      name     = "verified_email"
      priority = 1
    }
  }

  password_policy {
    minimum_length                   = 12
    require_lowercase                = true
    require_uppercase                = true
    require_numbers                  = true
    require_symbols                  = false
    temporary_password_validity_days = 7
  }
}

resource "aws_cognito_user_pool_domain" "students" {
  # amazoncognito.com addresses are shared by everyone: the suffix makes this one the deployment's
  domain       = "${var.name}-${random_string.domain.result}"
  user_pool_id = aws_cognito_user_pool.students.id
}

locals {
  app_url        = "https://${aws_cloudfront_distribution.app.domain_name}/"
  cognito_domain = "https://${aws_cognito_user_pool_domain.students.domain}.auth.${var.region}.amazoncognito.com"
}

resource "aws_cognito_user_pool_client" "app" {
  name         = var.name
  user_pool_id = aws_cognito_user_pool.students.id

  # the browser holds the tokens: a public client, with no secret
  generate_secret                      = false
  allowed_oauth_flows_user_pool_client = true
  allowed_oauth_flows                  = ["code"]
  allowed_oauth_scopes                 = ["openid"]
  supported_identity_providers         = ["COGNITO"]
  callback_urls                        = [local.app_url]
  logout_urls                          = [local.app_url]
  explicit_auth_flows                  = ["ALLOW_REFRESH_TOKEN_AUTH"]

  access_token_validity  = 1
  id_token_validity      = 1
  refresh_token_validity = 30
  token_validity_units {
    access_token  = "hours"
    id_token      = "hours"
    refresh_token = "days"
  }

  prevent_user_existence_errors = "ENABLED"
  enable_token_revocation       = true
}
