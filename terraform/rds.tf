# RDS 安全组
resource "aws_security_group" "rds" {
  name        = "${local.name_prefix}-rds-sg"
  description = "Security group for Snake Game RDS"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "${local.name_prefix}-rds-sg"
    Environment = var.environment
    Project     = "snake-game"
  }
}

# RDS 子网组
resource "aws_db_subnet_group" "snake_game" {
  name       = "${local.name_prefix}-db-subnet-group"
  subnet_ids = aws_subnet.private[*].id

  tags = {
    Name        = "${local.name_prefix}-db-subnet-group"
    Environment = var.environment
    Project     = "snake-game"
  }
}

# RDS 实例
resource "aws_db_instance" "snake_game" {
  identifier        = "${local.name_prefix}-db"
  instance_class    = var.db_instance_class
  allocated_storage = var.db_allocated_storage
  engine            = "postgres"
  engine_version    = var.db_engine_version
  username          = var.db_username
  password          = local.db_password_final
  db_name           = var.db_name
  port              = 5432

  publicly_accessible = false
  skip_final_snapshot = true
  deletion_protection = var.environment == "production" ? true : false

  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.snake_game.name

  parameter_group_name = "default.postgres15"
  multi_az             = var.environment == "production" ? true : false

  backup_retention_period = 7
  backup_window           = "03:00-04:00"
  maintenance_window      = "Mon:04:00-Mon:05:00"

  tags = {
    Name        = "${local.name_prefix}-database"
    Environment = var.environment
    Project     = "snake-game"
  }
}

# 数据库连接信息的 SSM 参数
resource "aws_ssm_parameter" "database_url" {
  name  = "/snake-game/${var.environment}/database-url"
  type  = "SecureString"
  value = "postgresql://${var.db_username}:${local.db_password_final}@${aws_db_instance.snake_game.endpoint}/${var.db_name}"

  tags = {
    Environment = var.environment
    Project     = "snake-game"
  }
}

# 数据库密码的 SSM 参数
resource "aws_ssm_parameter" "database_password" {
  name  = "/snake-game/${var.environment}/database-password"
  type  = "SecureString"
  value = local.db_password_final

  tags = {
    Environment = var.environment
    Project     = "snake-game"
  }
}