data "aws_caller_identity" "current" {}

data "aws_partition" "current" {}

data "aws_iam_policy_document" "ec2_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "server" {
  name               = "${var.name}-server"
  assume_role_policy = data.aws_iam_policy_document.ec2_assume.json
}

# SSM Session Manager, in place of SSH
resource "aws_iam_role_policy_attachment" "ssm" {
  role       = aws_iam_role.server.name
  policy_arn = "arn:${data.aws_partition.current.partition}:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

# what the server reads when it starts the app
data "aws_iam_policy_document" "server" {
  statement {
    sid       = "Settings"
    actions   = ["ssm:GetParameter"]
    resources = ["arn:${data.aws_partition.current.partition}:ssm:${var.region}:${data.aws_caller_identity.current.account_id}:parameter${local.settings_parameter}"]
  }

  statement {
    sid     = "Secrets"
    actions = ["secretsmanager:GetSecretValue"]
    resources = [
      aws_secretsmanager_secret.database.arn,
      aws_secretsmanager_secret.gogi_api_key.arn,
      aws_secretsmanager_secret.registry.arn,
    ]
  }
}

resource "aws_iam_role_policy" "server" {
  name   = "${var.name}-server"
  role   = aws_iam_role.server.id
  policy = data.aws_iam_policy_document.server.json
}

resource "aws_iam_instance_profile" "server" {
  name = "${var.name}-server"
  role = aws_iam_role.server.name
}
