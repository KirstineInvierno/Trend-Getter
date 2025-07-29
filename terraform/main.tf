provider "aws" {
  region = "eu-west-2"
}

data "aws_vpc" "main" {
  filter {
    name   = "tag:Name"
    values = ["c18-VPC"]
  }
}

data "aws_subnet" "private_1" {
  filter {
    name   = "tag:Name"
    values = ["c18-private-subnet-1"]
  }
}

data "aws_subnet" "private_2" {
  filter {
    name   = "tag:Name"
    values = ["c18-private-subnet-2"]
  }
}

data "aws_subnet" "private_3" {
  filter {
    name   = "tag:Name"
    values = ["c18-private-subnet-3"]
  }
}

resource "aws_db_subnet_group" "rds_subnet_group" {
  name = "rds-subnet-group"
  subnet_ids = [
    data.aws_subnet.private_1.id,
    data.aws_subnet.private_2.id,
    data.aws_subnet.private_3.id
  ]

  tags = {
    Name = "RDS Subnet Group"
  }
}

resource "aws_security_group" "rds_sg" {
  name        = "c18-trend-getter-rds-sg"
  description = "Allow RDS traffic"
  vpc_id      = data.aws_vpc.main.id

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/16"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_db_instance" "postgres" {
  identifier              = "c18-trend-getter-rds"
  engine                  = "postgresql"
  engine_version          = "17.4"
  instance_class          = "db.t3.small"
  allocated_storage       = 200
  storage_type            = "gp2"
  username                = var.DB_USERNAME
  password                = var.DB_PASSWORD
  db_name                 = "trend-getter-db"
  multi_az                = true
  publicly_accessible     = false
  skip_final_snapshot     = true
  vpc_security_group_ids  = [aws_security_group.rds_sg.id]
  db_subnet_group_name    = aws_db_subnet_group.rds_subnet_group.name
  backup_retention_period = 7
  deletion_protection     = false
}
