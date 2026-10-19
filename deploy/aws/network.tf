# One VPC: the server in a public subnet, with an Elastic IP for its calls out (gogi lets that address in), and
# Postgres in two private subnets, as RDS asks for two availability zones. CloudFront reaches the server privately,
# through a VPC origin: nothing else can reach it
data "aws_availability_zones" "available" {
  state = "available"
}

locals {
  zones = slice(data.aws_availability_zones.available.names, 0, 2)
}

resource "aws_vpc" "app" {
  cidr_block           = "10.41.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = { Name = var.name }
}

resource "aws_internet_gateway" "app" {
  vpc_id = aws_vpc.app.id

  tags = { Name = var.name }
}

resource "aws_subnet" "public" {
  vpc_id            = aws_vpc.app.id
  cidr_block        = "10.41.0.0/24"
  availability_zone = local.zones[0]

  tags = { Name = "${var.name}-public" }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.app.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.app.id
  }

  tags = { Name = "${var.name}-public" }
}

resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}

resource "aws_subnet" "private" {
  count             = 2
  vpc_id            = aws_vpc.app.id
  cidr_block        = "10.41.${10 + count.index}.0/24"
  availability_zone = local.zones[count.index]

  tags = { Name = "${var.name}-private-${count.index}" }
}

resource "aws_security_group" "server" {
  name        = "${var.name}-server"
  description = "The app's server: HTTP from CloudFront only"
  vpc_id      = aws_vpc.app.id

  tags = { Name = "${var.name}-server" }
}

# the security group CloudFront makes in the VPC for its VPC origins: only this distribution's traffic comes from it
data "aws_security_group" "cloudfront" {
  vpc_id = aws_vpc.app.id
  name   = "CloudFront-VPCOrigins-Service-SG"

  depends_on = [aws_cloudfront_vpc_origin.app]
}

resource "aws_vpc_security_group_ingress_rule" "cloudfront" {
  security_group_id            = aws_security_group.server.id
  description                  = "The app, from CloudFront"
  ip_protocol                  = "tcp"
  from_port                    = 80
  to_port                      = 80
  referenced_security_group_id = data.aws_security_group.cloudfront.id
}

# the image, gogi, Cognito's keys, AWS' own APIs
resource "aws_vpc_security_group_egress_rule" "server" {
  security_group_id = aws_security_group.server.id
  description       = "Anywhere"
  ip_protocol       = "-1"
  cidr_ipv4         = "0.0.0.0/0"
}

resource "aws_security_group" "database" {
  name        = "${var.name}-database"
  description = "The app's Postgres, from its server only"
  vpc_id      = aws_vpc.app.id

  tags = { Name = "${var.name}-database" }
}

resource "aws_vpc_security_group_ingress_rule" "database" {
  security_group_id            = aws_security_group.database.id
  description                  = "Postgres, from the server"
  ip_protocol                  = "tcp"
  from_port                    = 5432
  to_port                      = 5432
  referenced_security_group_id = aws_security_group.server.id
}
