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

variable "state_bucket" {
  type        = string
  description = "remote state bucket from bootstrap"
}

variable "lock_table" {
  type        = string
  description = "remote state lock table from bootstrap"
}

variable "cluster_name" {
  type        = string
  description = "eks cluster name"
  default     = "pokemon-game-eks"
}
