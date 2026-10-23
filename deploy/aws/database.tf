# The app's own data: notes, summaries and quizzes, and, on its own platform, its courses, the students' material
# (searched with pgvector, which the app turns on) and the conversations with the assistant. The uploaded files are
# kept in S3 (files.tf), or in gogi
resource "random_password" "database" {
  length  = 32
  special = false
}

resource "aws_db_subnet_group" "app" {
  name       = var.name
  subnet_ids = aws_subnet.private[*].id
}

resource "aws_db_instance" "app" {
  identifier     = var.name
  engine         = "postgres"
  engine_version = "16"
  instance_class = var.db_instance_class

  allocated_storage     = var.db_allocated_storage_gb
  max_allocated_storage = var.db_allocated_storage_gb * 10
  storage_type          = "gp3"
  storage_encrypted     = true

  db_name  = "qubit_notes"
  username = "qubit_notes"
  password = random_password.database.result

  db_subnet_group_name   = aws_db_subnet_group.app.name
  vpc_security_group_ids = [aws_security_group.database.id]
  publicly_accessible    = false

  backup_retention_period    = var.db_backup_days
  auto_minor_version_upgrade = true
  deletion_protection        = var.deletion_protection
  skip_final_snapshot        = false
  final_snapshot_identifier  = "${var.name}-final"
}
