# AWS 配置
aws_region  = "us-east-1"
environment = "development"

# VPC 配置
vpc_cidr             = "10.0.0.0/16"
public_subnet_cidrs  = ["10.0.1.0/24", "10.0.2.0/24"]
private_subnet_cidrs = ["10.0.101.0/24", "10.0.102.0/24"]

# 数据库配置
db_instance_class    = "db.t3.micro"
db_allocated_storage = 20
db_engine_version    = "14.12"
db_username          = "snakegame"
db_password          = "snake_1234"
db_name              = "snakegame"