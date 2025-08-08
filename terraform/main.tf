provider "aws" {
  region = "eu-west-2"
}


terraform {
  backend "s3" {
    bucket = "c18-trend-getter-state-bucket"
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

resource "aws_ecr_repository" "c18-trend-getter-notifications-ecr" {
  name                 = "c18-trend-getter-notifications-ecr"
  image_tag_mutability = "MUTABLE"
}

resource "aws_ecr_repository" "c18-trend-getter-dashboard-ecr" {
  name                 = "c18-trend-getter-dashboard-ecr"
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


# Lambda function
# Permissions

data "aws_iam_policy_document" "lambda_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com", "scheduler.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

data "aws_iam_policy_document" "lambda_permissions" {
  statement {
    effect = "Allow"
    actions = [
      "s3:ListBucket",
      "s3:GetObject",
      "s3:PutObject",
      "s3:DeleteObject"
    ]
    resources = [
      "arn:aws:s3:::c18-trend-getter-s3",
      "arn:aws:s3:::c18-trend-getter-s3/*"
    ]
  }
  statement {
    effect = "Allow"
    actions = [
      "ses:SendEmail",
      "ses:SendRawEmail"
    ]
    resources = [
      "arn:aws:ses:eu-west-2:129033205317:identity/trendgetterupdates@gmail.com"
    ]
  }
  statement {
    effect = "Allow"
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    resources = ["arn:aws:logs:*:*:*"]
  }
  statement {
    effect = "Allow"
    actions = [
      "lambda:InvokeFunction",
      ## full access (delete after):
      "cloudformation:DescribeStacks",
      "cloudformation:ListStackResources",
      "cloudwatch:ListMetrics",
      "cloudwatch:GetMetricData",
      "ec2:DescribeSecurityGroups",
      "ec2:DescribeSubnets",
      "ec2:DescribeVpcs",
      "kms:ListAliases",
      "iam:GetPolicy",
      "iam:GetPolicyVersion",
      "iam:GetRole",
      "iam:GetRolePolicy",
      "iam:ListAttachedRolePolicies",
      "iam:ListRolePolicies",
      "iam:ListRoles",
      "lambda:*",
      "logs:DescribeLogGroups",
      "states:DescribeStateMachine",
      "states:ListStateMachines",
      "tag:GetResources",
      "xray:GetTraceSummaries",
      "xray:BatchGetTraces"
    ]
    resources = ["*"]
  }
  statement {
    effect = "Allow"
    actions = [
      "rds:*"
    ]
    resources = ["arn:aws:rds:eu-west-2:129033205317:db:c18trendgetterrds"]
  }
}

resource "aws_iam_role" "lambda_role" {
  name               = "c18-data-getter-lambda-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_role.json
}

resource "aws_iam_policy" "lambda_s3_policy" {
  name   = "c18-data-getter-lambda-s3-policy"
  policy = data.aws_iam_policy_document.lambda_permissions.json
}

resource "aws_iam_role_policy_attachment" "lambda_s3_attach" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_s3_policy.arn
}

resource "aws_lambda_permission" "allow_lambda" {
  statement_id  = "AllowExecutionFromETLLambda"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.lambda_function_notif.function_name
  principal     = "lambda.amazonaws.com"
  source_arn    = aws_lambda_function.lambda_function.arn
}

resource "aws_lambda_function" "lambda_function" {
  function_name = "c18-trend-getter-lambda-function"
  role          = aws_iam_role.lambda_role.arn
  package_type  = "Image"
  image_uri     = "129033205317.dkr.ecr.eu-west-2.amazonaws.com/trend-getter-lambda-ecr:latest"
  memory_size   = 10000
  timeout       = 600
  architectures = ["x86_64"]

  environment {
    variables = {
      DB_HOST     = var.DB_HOST
      DB_PORT     = var.DB_PORT
      DB_USER     = var.DB_USERNAME
      DB_PASSWORD = var.DB_PASSWORD
      DB_NAME     = var.DB_NAME
      DB_SCHEMA   = var.DB_SCHEMA
      HF_HOME     = "/tmp/hf/"
    }
  }
}

## Notifications lambda

data "aws_iam_policy_document" "lambda_role_notif" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

data "aws_iam_policy_document" "lambda_permissions_notif" {
  statement {
    effect = "Allow"
    actions = [
      "s3:ListBucket",
      "s3:GetObject",
      "s3:PutObject",
      "s3:DeleteObject"
    ]
    resources = [
      "arn:aws:s3:::c18-trend-getter-s3",
      "arn:aws:s3:::c18-trend-getter-s3/*"
    ]
  }
  statement {
    effect = "Allow"
    actions = [
      "ses:*"
    ]
    resources = [
      "*"
    ]
  }
}

resource "aws_iam_role" "lambda_role_notif" {
  name               = "c18-data-getter-notif-lambda-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_role_notif.json
}



resource "aws_lambda_function" "lambda_function_notif" {
  function_name = "c18-trend-getter-notifications-function"
  role          = aws_iam_role.lambda_role_notif.arn
  package_type  = "Image"
  image_uri     = "129033205317.dkr.ecr.eu-west-2.amazonaws.com/c18-trend-getter-notifications-ecr:v4"
  memory_size   = 7168
  timeout       = 300
  architectures = ["x86_64"]

  environment {
    variables = {
      DB_HOST      = var.DB_HOST
      DB_PORT      = var.DB_PORT
      DB_USER      = var.DB_USERNAME
      DB_PASSWORD  = var.DB_PASSWORD
      DB_NAME      = var.DB_NAME
      DB_SCHEMA    = var.DB_SCHEMA
      SENDER_EMAIL = "trendgetterupdates@gmail.com"
    }
  }
}

resource "aws_lambda_permission" "allow_s3" {
  statement_id  = "AllowExecutionFromS3"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.lambda_function.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.c18-trend-getter-s3.arn
}

resource "aws_s3_bucket_notification" "s3_trigger" {
  bucket = aws_s3_bucket.c18-trend-getter-s3.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.lambda_function.arn
    events              = ["s3:ObjectCreated:*"]
  }

  depends_on = [aws_lambda_permission.allow_s3]
}

resource "aws_iam_role" "step_function_role" {
  name = "step-function-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = "sts:AssumeRole",
        Effect = "Allow",
        Principal = {
          Service = "states.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_policy" "step_function_policy" {
  name = "step-function-lambda-invoke-policy"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "lambda:InvokeFunction"
        ],
        Resource = ["*"]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "step_function_attach_policy" {
  role       = aws_iam_role.step_function_role.name
  policy_arn = aws_iam_policy.step_function_policy.arn
}




resource "aws_sfn_state_machine" "etl_sm" {
  name     = "c18-trendgetter-etl-notif-sm"
  role_arn = aws_iam_role.step_function_role.arn
  definition = jsonencode({
    "Comment" = "A state machine invoking our two lambdas",
    "StartAt" = "InvokeETLLambda",
    "States" = {
      "InvokeETLLambda" = {
        "Type"     = "Task",
        "Resource" = "${aws_lambda_function.lambda_function.arn}",
        "Next"     = "InvokeNotificationLambda"
      },
      "InvokeNotificationLambda" = {
        "Type"     = "Task",
        "Resource" = "${aws_lambda_function.lambda_function_notif.arn}",
        "End"      = true
      }
    }
  })
}
## State machine trigger


resource "aws_s3_bucket_notification" "s3_eventbridge" {
  bucket = aws_s3_bucket.c18-trend-getter-s3.id

  eventbridge = true
}



resource "aws_iam_role" "eventbridge_invoke_stepfunction_role" {
  name = "c18-tg-event-sm-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement : [{
      Effect = "Allow",
      Principal = {
        Service = "events.amazonaws.com"
      },
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_policy" "eventbridge_invoke_stepfunction_policy" {
  name = "c18-tg-event-policy"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement : [
      {
        Effect   = "Allow",
        Action   = "states:StartExecution",
        Resource = aws_sfn_state_machine.etl_sm.arn
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "attach_eventbridge_invoke_stepfunction" {
  role       = aws_iam_role.eventbridge_invoke_stepfunction_role.name
  policy_arn = aws_iam_policy.eventbridge_invoke_stepfunction_policy.arn
}



resource "aws_cloudwatch_event_rule" "s3_put_event" {
  name        = "trigger-stepfunction-on-upload"
  description = "Triggers step function on S3 object creation"
  event_pattern = jsonencode({
    source        = ["aws.s3"],
    "detail-type" = ["Object Created"],
    detail = {
      bucket = {
        name = ["c18-trend-getter-s3"]
      }
    }
  })
}

resource "aws_cloudwatch_event_target" "trigger_stepfunction" {
  rule     = aws_cloudwatch_event_rule.s3_put_event.name
  arn      = aws_sfn_state_machine.etl_sm.arn
  role_arn = aws_iam_role.eventbridge_invoke_stepfunction_role.arn
}



resource "aws_iam_role" "ecs_task_execution" {
  name               = "c18-trendgetter-ecsTaskExecutionRole"
  assume_role_policy = data.aws_iam_policy_document.ecs_task_assume.json
}

data "aws_iam_policy_document" "ecs_task_assume" {
  statement {
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role_policy_attachment" "exec_policy" {
  role       = aws_iam_role.ecs_task_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}


resource "aws_cloudwatch_log_group" "streamlit" {
  name              = "/ecs/streamlit"
  retention_in_days = 14
}


resource "aws_security_group" "ecs" {
  name        = "c18-trendgetter-sg"
  description = "Allow inbound access to Streamlit"
  vpc_id      = data.aws_vpc.main.id

  ingress {
    from_port   = 8501
    to_port     = 8501
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


resource "aws_ecs_cluster" "cluster" {
  name = "c18-ecs-cluster"
}


resource "aws_ecs_task_definition" "streamlit" {
  family                   = "c18-trendgetter-streamlit-td"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "512"
  memory                   = "1024"
  execution_role_arn       = aws_iam_role.ecs_task_execution.arn
  task_role_arn            = aws_iam_role.ecs_task_execution.arn

  container_definitions = jsonencode([
    {
      name  = "c18-trendgetter-container"
      image = "${aws_ecr_repository.streamlit.repository_url}:latest"
      portMappings = [
        { containerPort = 8501, protocol = "tcp" }
      ]
      environment = [
        { name = "DB_HOST", value = "value" },
        { name = "DB_NAME", value = "trendgetterdb" },
        { name = "DB_USER", value = "trendgetter" },
        { name = "DB_PASSWORD", value = "trendypwd101" },
        { name = "DB_HOST", value = "c18trendgetterrds.c57vkec7dkkx.eu-west-2.rds.amazonaws.com" },
        { name = "DB_HOST", value = "5432" }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.streamlit.name
          "awslogs-region"        = "eu-west-2"
          "awslogs-stream-prefix" = "streamlit"
        }
      }
    }
  ])
}
resource "aws_ecs_service" "streamlit" {
  name            = "c18-trendgetter-streamlit-service"
  cluster         = aws_ecs_cluster.cluster.id
  task_definition = aws_ecs_task_definition.streamlit.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = [data.aws_subnet.public_1.id, data.aws_subnet.public_2.id]
    security_groups  = [aws_security_group.ecs.id]
    assign_public_ip = true
  }
}


