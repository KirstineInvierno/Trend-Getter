provider "aws" {
  region = "eu-west-2"
}


terraform {
  backend "s3" {
    bucket = "your-terraform-state-bucket"
    key    = "terraform/terraform.tfstate"
    region = "eu-west-2"
  }
}


# VPCs and subnets for the RDS

data "aws_vpc" "main" {
  filter {
    name   = "tag:Name"
    values = ["c18-VPC"]
  }
}

data "aws_subnet" "public_1" {
  filter {
    name   = "tag:Name"
    values = ["c18-public-subnet-1"]
  }
}

data "aws_subnet" "public_2" {
  filter {
    name   = "tag:Name"
    values = ["c18-public-subnet-2"]
  }
}

data "aws_subnet" "public_3" {
  filter {
    name   = "tag:Name"
    values = ["c18-public-subnet-3"]
  }
}

resource "aws_db_subnet_group" "rds_subnet_group" {
  name = "c18-trend-getter-rds-subnet-group"
  subnet_ids = [
    data.aws_subnet.public_1.id,
    data.aws_subnet.public_2.id,
    data.aws_subnet.public_3.id
  ]

  tags = {
    Name = "RDS Subnet Group"
  }
}


# RDS security group

resource "aws_security_group" "rds_sg" {
  name        = "c18-trend-getter-rds-sg"
  description = "Allow RDS traffic"
  vpc_id      = data.aws_vpc.main.id

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}


# RDS

resource "aws_db_instance" "postgresql" {
  identifier              = "c18trendgetterrds"
  engine                  = "postgres"
  engine_version          = "17.4"
  instance_class          = "db.t3.small"
  allocated_storage       = 200
  storage_type            = "gp2"
  username                = var.DB_USERNAME
  password                = var.DB_PASSWORD
  db_name                 = "trendgetterdb"
  multi_az                = true
  publicly_accessible     = true
  skip_final_snapshot     = true
  vpc_security_group_ids  = [aws_security_group.rds_sg.id]
  db_subnet_group_name    = aws_db_subnet_group.rds_subnet_group.name
  backup_retention_period = 7
  deletion_protection     = false
}


# S3 bucket

resource "aws_s3_bucket" "c18-trend-getter-s3" {
  bucket = "c18-trend-getter-s3"
}


# ECRs

resource "aws_ecr_repository" "trend-getter-extract-and-load-ecr" {
  name                 = "trend-getter-extract-and-load-ecr"
  image_tag_mutability = "MUTABLE"
}

resource "aws_ecr_repository" "trend-getter-lambda-ecr" {
  name                 = "trend-getter-lambda-ecr"
  image_tag_mutability = "MUTABLE"
}


# EC2

resource "tls_private_key" "trend-getter-key" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

resource "aws_key_pair" "trend-getter-ec2-key" {
  key_name   = "c18-trend-getter-kp"
  public_key = tls_private_key.trend-getter-key.public_key_openssh

}

resource "aws_security_group" "trend-getter-ec2-sg" {
  name        = "c18-trend-getter-ec2-sg"
  description = "Allows connection to database from EC2 instance"
  vpc_id      = data.aws_vpc.main.id

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}


resource "aws_instance" "ec2" {
  ami                         = "ami-0f4f4482537714bd9"
  instance_type               = "t3.nano"
  subnet_id                   = data.aws_subnet.public_1.id
  associate_public_ip_address = true
  key_name                    = aws_key_pair.trend-getter-ec2-key.key_name
  vpc_security_group_ids      = [aws_security_group.trend-getter-ec2-sg.id]

  tags = {
    Name = "c18-trend-getter-extract-load-ec2"
  }
}