variable "region" {
  type        = string
  description = "aws region"
  default     = "eu-central-1"
}

variable "project" {
  type        = string
  description = "name prefix"
  default     = "pokemon-game"
}

variable "github_repo" {
  type        = string
  description = "repository name"
  default     = "s1natex/Pokemon_Game"
}

variable "github_branch" {
  type        = string
  description = "branch name"
  default     = "main"
}
