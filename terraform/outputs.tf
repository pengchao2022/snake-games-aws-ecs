output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.main.id
}

output "public_subnet_ids" {
  description = "List of public subnet IDs"
  value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  description = "List of private subnet IDs"
  value       = aws_subnet.private[*].id
}

output "rds_endpoint" {
  description = "RDS instance endpoint"
  value       = aws_db_instance.snake_game.endpoint
}

output "rds_connection_string" {
  description = "RDS connection string (without password)"
  value       = "postgresql://${var.db_username}@${aws_db_instance.snake_game.endpoint}/${var.db_name}"
  sensitive   = true
}

output "database_url_ssm_parameter" {
  description = "SSM parameter name for database URL"
  value       = aws_ssm_parameter.database_url.name
}

output "database_password_ssm_parameter" {
  description = "SSM parameter name for database password"
  value       = aws_ssm_parameter.database_password.name
}

output "nat_gateway_ip" {
  description = "NAT Gateway public IP"
  value       = aws_eip.nat.public_ip
}


output "db_password" {
  description = "Database password (only if generated)"
  value       = local.db_password_final
  sensitive   = true
}

output "ecr_repository_url" {
  description = "ECR repository URL"
  value       = aws_ecr_repository.snake_game.repository_url
}

output "ecs_cluster_name" {
  description = "ECS cluster name"
  value       = aws_ecs_cluster.snake_game.name
}

output "ecs_service_name" {
  description = "ECS service name"
  value       = aws_ecs_service.snake_game.name
}

output "load_balancer_dns" {
  description = "Load Balancer DNS name"
  value       = aws_lb.snake_game.dns_name
}

output "load_balancer_arn" {
  description = "Load Balancer ARN"
  value       = aws_lb.snake_game.arn
}

output "target_group_arn" {
  description = "Target Group ARN"
  value       = aws_lb_target_group.snake_game.arn
}

output "ecs_task_execution_role_arn" {
  description = "ECS Task Execution Role ARN"
  value       = aws_iam_role.ecs_task_execution_role.arn
}

output "ecs_task_role_arn" {
  description = "ECS Task Role ARN"
  value       = aws_iam_role.ecs_task_role.arn
}