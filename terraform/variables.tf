variable "DB_USERNAME" {
  type        = string
  description = "The username for the RDS database"
}

variable "DB_PASSWORD" {
  type        = string
  description = "The password for the RDS database"
  sensitive   = true
}

variable "DB_HOST" {
  type        = string
  description = "The hostname of the RDS database"
}

variable "DB_PORT" {
  type        = string
  description = "The port number used to connect to the RDS database"
}

variable "DB_NAME" {
  type        = string
  description = "The name of the RDS database"
}

variable "DB_SCHEMA" {
  type        = string
  description = "The schema within the RDS database"
}

variable "AWS_DEFAULT_REGION" {
  type        = string
  sensitive   = true
}