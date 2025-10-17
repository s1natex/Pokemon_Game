resource "aws_cloudwatch_log_group" "app" {
  name              = "/eks/${var.project}/app"
  retention_in_days = var.log_retention_days
}

resource "aws_cloudwatch_log_group" "frontend" {
  name              = "/eks/${var.project}/app/frontend"
  retention_in_days = var.log_retention_days
}

resource "aws_cloudwatch_log_group" "pokemon_manager" {
  name              = "/eks/${var.project}/app/pokemon-manager"
  retention_in_days = var.log_retention_days
}

resource "aws_cloudwatch_log_group" "scheduler" {
  name              = "/eks/${var.project}/app/scheduler"
  retention_in_days = var.log_retention_days
}

resource "aws_cloudwatch_log_group" "pokemon_fetcher" {
  name              = "/eks/${var.project}/app/pokemon-fetcher"
  retention_in_days = var.log_retention_days
}

resource "aws_cloudwatch_log_group" "battle_manager" {
  name              = "/eks/${var.project}/app/battle-manager"
  retention_in_days = var.log_retention_days
}

resource "aws_cloudwatch_log_group" "trainer_manager" {
  name              = "/eks/${var.project}/app/trainer-manager"
  retention_in_days = var.log_retention_days
}
