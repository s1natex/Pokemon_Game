output "state_bucket" {
  value = aws_s3_bucket.state.bucket
}

output "lock_table" {
  value = aws_dynamodb_table.locks.name
}

output "oidc_provider_arn" {
  value = aws_iam_openid_connect_provider.gha.arn
}

output "terraform_ci_role_arn" {
  value = aws_iam_role.terraform_ci_readonly.arn
}

output "terraform_cd_role_arn" {
  value = aws_iam_role.terraform_cd_deploy.arn
}
