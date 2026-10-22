# The students' uploads, where the app is its own platform: a private bucket only the server reads and writes. The
# server reaches it through a gateway endpoint, which costs nothing and keeps the traffic in the VPC
resource "aws_s3_bucket" "material" {
  count = local.standalone ? 1 : 0

  bucket_prefix = "${var.name}-material-"
  # emptied first when the deployment is destroyed only if deletion isn't protected
  force_destroy = !var.deletion_protection
}

resource "aws_s3_bucket_public_access_block" "material" {
  count = local.standalone ? 1 : 0

  bucket                  = aws_s3_bucket.material[0].id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "material" {
  count = local.standalone ? 1 : 0

  bucket = aws_s3_bucket.material[0].id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# a deleted or replaced upload is kept for a while, in case it was a mistake
resource "aws_s3_bucket_versioning" "material" {
  count = local.standalone ? 1 : 0

  bucket = aws_s3_bucket.material[0].id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "material" {
  count = local.standalone ? 1 : 0

  bucket = aws_s3_bucket.material[0].id
  rule {
    id     = "forget-old-versions"
    status = "Enabled"
    filter {}
    noncurrent_version_expiration {
      noncurrent_days = var.material_versions_days
    }
  }

  depends_on = [aws_s3_bucket_versioning.material]
}

resource "aws_vpc_endpoint" "s3" {
  vpc_id            = aws_vpc.app.id
  service_name      = "com.amazonaws.${var.region}.s3"
  vpc_endpoint_type = "Gateway"
  route_table_ids   = [aws_route_table.public.id]

  tags = { Name = "${var.name}-s3" }
}
