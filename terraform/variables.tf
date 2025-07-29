variable "db_username" {
  type        = string
  description = "The username for the RDS database"
}

variable "db_password" {
  type        = string
  description = "The password for the RDS database"
  sensitive   = true
}
