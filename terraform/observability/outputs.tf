output "dashboard_name" {
  value = aws_cloudwatch_dashboard.main.dashboard_name
}

output "log_group_root" {
  value = aws_cloudwatch_log_group.app.name
}
