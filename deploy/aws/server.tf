# The server runs the app's image as qubit-notes.service, on port 80. It keeps no data of its own, so it can be
# replaced at any time. The operator reaches it with SSM Session Manager: it has no SSH
data "aws_ssm_parameter" "al2023" {
  name = "/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64"
}

resource "aws_eip" "server" {
  domain = "vpc"

  tags = { Name = var.name }
}

resource "aws_instance" "server" {
  ami                    = data.aws_ssm_parameter.al2023.insecure_value
  instance_type          = var.instance_type
  subnet_id              = aws_subnet.public.id
  vpc_security_group_ids = [aws_security_group.server.id]
  iam_instance_profile   = aws_iam_instance_profile.server.name

  user_data = templatefile("${path.module}/cloud-init.yaml", {
    start_script = base64encode(templatefile("${path.module}/start-qubit-notes.sh", {
      region = var.region
      # by its name: the parameter is written after CloudFront and Cognito, which come after the server
      settings = local.settings_parameter
    }))
  })
  user_data_replace_on_change = true

  root_block_device {
    volume_size = 20
    volume_type = "gp3"
    encrypted   = true
  }

  metadata_options {
    http_tokens = "required"
  }

  tags = { Name = var.name }

  lifecycle {
    # a newer Amazon Linux is taken when the server is next replaced, not as soon as it's published
    ignore_changes = [ami]
  }
}

resource "aws_eip_association" "server" {
  allocation_id = aws_eip.server.id
  instance_id   = aws_instance.server.id
}
