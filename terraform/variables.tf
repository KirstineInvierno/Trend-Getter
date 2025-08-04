variable "DB_USERNAME" {
  type        = string
  description = "The username for the RDS database"
}

variable "DB_PASSWORD" {
  type        = string
  description = "The password for the RDS database"
  sensitive   = true
}