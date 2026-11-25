terraform {
  required_version = ">= 1.6"

  required_providers {
    hcloud = {
      source  = "hetznercloud/hcloud"
      version = "~> 1.52"
    }
    # only for Cognito, where students sign in
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }

  # The state holds no passwords or keys: the server makes its own the first time it starts (start-qubit-notes.sh).
  # Keep it somewhere safe all the same, e.g. with backend.tf.example
}

# the Hetzner Cloud project's API token, from HCLOUD_TOKEN
provider "hcloud" {}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project   = var.name
      ManagedBy = "terraform"
    }
  }
}
