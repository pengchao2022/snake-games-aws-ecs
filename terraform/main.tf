terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# 获取可用区
data "aws_availability_zones" "available" {
  state = "available"
}

# 随机密码生成（如果未提供密码）
resource "random_password" "db_password" {
  count   = var.db_password == "" ? 1 : 0
  length  = 16
  special = false
}

locals {
  db_password_final = var.db_password != "" ? var.db_password : random_password.db_password[0].result
  environment_lower = lower(var.environment)
  name_prefix       = "snake-game-${local.environment_lower}"
}