# ============================================================
# Chronopoli – Lambda Functions (Symposia Pipeline)
# ============================================================

# --- S3 Bucket for Lambda Outputs ---

resource "aws_s3_bucket" "symposia_outputs" {
  bucket = "${var.project_name}-symposia-outputs-${var.environment}"

  tags = merge(var.tags, {
    Component = "Symposia"
    Service   = "Lambda"
  })
}

resource "aws_s3_bucket_versioning" "symposia_outputs" {
  bucket = aws_s3_bucket.symposia_outputs.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "symposia_outputs" {
  bucket = aws_s3_bucket.symposia_outputs.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "symposia_outputs" {
  bucket = aws_s3_bucket.symposia_outputs.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# --- Shared IAM Role for all Symposia Lambdas ---

resource "aws_iam_role" "symposia_lambda" {
  name = "${var.project_name}-symposia-lambda-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

  tags = merge(var.tags, {
    Component = "Symposia"
  })
}

# CloudWatch Logs
resource "aws_iam_role_policy_attachment" "symposia_lambda_logs" {
  role       = aws_iam_role.symposia_lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# S3 access (read recordings, write outputs)
resource "aws_iam_role_policy" "symposia_lambda_s3" {
  name = "symposia-s3-access"
  role = aws_iam_role.symposia_lambda.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.symposia_outputs.arn,
          "${aws_s3_bucket.symposia_outputs.arn}/*",
          aws_s3_bucket.ivs_recordings.arn,
          "${aws_s3_bucket.ivs_recordings.arn}/*"
        ]
      }
    ]
  })
}

# AWS Transcribe
resource "aws_iam_role_policy" "symposia_lambda_transcribe" {
  name = "symposia-transcribe-access"
  role = aws_iam_role.symposia_lambda.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "transcribe:StartTranscriptionJob",
          "transcribe:GetTranscriptionJob"
        ]
        Resource = "*"
      }
    ]
  })
}

# Amazon Bedrock (Claude)
resource "aws_iam_role_policy" "symposia_lambda_bedrock" {
  name = "symposia-bedrock-access"
  role = aws_iam_role.symposia_lambda.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel"
        ]
        Resource = "arn:aws:bedrock:${var.aws_region}::foundation-model/anthropic.claude-*"
      }
    ]
  })
}

# SQS (send to approval queue)
resource "aws_iam_role_policy" "symposia_lambda_sqs" {
  name = "symposia-sqs-access"
  role = aws_iam_role.symposia_lambda.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "sqs:SendMessage"
        ]
        Resource = aws_sqs_queue.symposia_approval.arn
      }
    ]
  })
}

# SES (send notification emails)
resource "aws_iam_role_policy" "symposia_lambda_ses" {
  name = "symposia-ses-access"
  role = aws_iam_role.symposia_lambda.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ses:SendEmail",
          "ses:SendRawEmail"
        ]
        Resource = "*"
      }
    ]
  })
}

# --- Lambda Deployment Packages (zip archives) ---

data "archive_file" "transcribe" {
  type        = "zip"
  source_dir  = "${path.module}/../lambdas/transcribe"
  output_path = "${path.module}/../lambdas/.build/transcribe.zip"
}

data "archive_file" "check_transcription" {
  type        = "zip"
  source_dir  = "${path.module}/../lambdas/check_transcription"
  output_path = "${path.module}/../lambdas/.build/check_transcription.zip"
}

data "archive_file" "analyze" {
  type        = "zip"
  source_dir  = "${path.module}/../lambdas/analyze"
  output_path = "${path.module}/../lambdas/.build/analyze.zip"
}

data "archive_file" "opinion_paper" {
  type        = "zip"
  source_dir  = "${path.module}/../lambdas/opinion_paper"
  output_path = "${path.module}/../lambdas/.build/opinion_paper.zip"
}

data "archive_file" "linkedin" {
  type        = "zip"
  source_dir  = "${path.module}/../lambdas/linkedin"
  output_path = "${path.module}/../lambdas/.build/linkedin.zip"
}

data "archive_file" "instagram" {
  type        = "zip"
  source_dir  = "${path.module}/../lambdas/instagram"
  output_path = "${path.module}/../lambdas/.build/instagram.zip"
}

data "archive_file" "partner_report" {
  type        = "zip"
  source_dir  = "${path.module}/../lambdas/partner_report"
  output_path = "${path.module}/../lambdas/.build/partner_report.zip"
}

data "archive_file" "notify" {
  type        = "zip"
  source_dir  = "${path.module}/../lambdas/notify"
  output_path = "${path.module}/../lambdas/.build/notify.zip"
}

# --- Lambda Functions ---

resource "aws_lambda_function" "symposia_transcribe" {
  function_name    = "${var.project_name}-symposia-transcribe-${var.environment}"
  role             = aws_iam_role.symposia_lambda.arn
  handler          = "handler.handler"
  runtime          = "python3.11"
  timeout          = 60
  memory_size      = 256
  filename         = data.archive_file.transcribe.output_path
  source_code_hash = data.archive_file.transcribe.output_base64sha256

  environment {
    variables = {
      S3_BUCKET_OUTPUTS = aws_s3_bucket.symposia_outputs.id
      AWS_REGION_NAME   = var.aws_region
    }
  }

  tags = merge(var.tags, {
    Component = "Symposia"
    Step      = "1-Transcribe"
  })
}

resource "aws_lambda_function" "symposia_check_transcription" {
  function_name    = "${var.project_name}-symposia-check-transcription-${var.environment}"
  role             = aws_iam_role.symposia_lambda.arn
  handler          = "handler.handler"
  runtime          = "python3.11"
  timeout          = 60
  memory_size      = 256
  filename         = data.archive_file.check_transcription.output_path
  source_code_hash = data.archive_file.check_transcription.output_base64sha256

  environment {
    variables = {
      S3_BUCKET_OUTPUTS = aws_s3_bucket.symposia_outputs.id
      AWS_REGION_NAME   = var.aws_region
    }
  }

  tags = merge(var.tags, {
    Component = "Symposia"
    Step      = "2-CheckTranscription"
  })
}

resource "aws_lambda_function" "symposia_analyze" {
  function_name    = "${var.project_name}-symposia-analyze-${var.environment}"
  role             = aws_iam_role.symposia_lambda.arn
  handler          = "handler.handler"
  runtime          = "python3.11"
  timeout          = 300
  memory_size      = 512
  filename         = data.archive_file.analyze.output_path
  source_code_hash = data.archive_file.analyze.output_base64sha256

  environment {
    variables = {
      S3_BUCKET_OUTPUTS = aws_s3_bucket.symposia_outputs.id
      AWS_REGION_NAME   = var.aws_region
    }
  }

  tags = merge(var.tags, {
    Component = "Symposia"
    Step      = "3-Analyze"
  })
}

resource "aws_lambda_function" "symposia_opinion_paper" {
  function_name    = "${var.project_name}-symposia-opinion-paper-${var.environment}"
  role             = aws_iam_role.symposia_lambda.arn
  handler          = "handler.handler"
  runtime          = "python3.11"
  timeout          = 300
  memory_size      = 1024
  filename         = data.archive_file.opinion_paper.output_path
  source_code_hash = data.archive_file.opinion_paper.output_base64sha256

  environment {
    variables = {
      S3_BUCKET_OUTPUTS = aws_s3_bucket.symposia_outputs.id
      AWS_REGION_NAME   = var.aws_region
    }
  }

  tags = merge(var.tags, {
    Component = "Symposia"
    Step      = "4-OpinionPaper"
  })
}

resource "aws_lambda_function" "symposia_linkedin" {
  function_name    = "${var.project_name}-symposia-linkedin-${var.environment}"
  role             = aws_iam_role.symposia_lambda.arn
  handler          = "handler.handler"
  runtime          = "python3.11"
  timeout          = 60
  memory_size      = 256
  filename         = data.archive_file.linkedin.output_path
  source_code_hash = data.archive_file.linkedin.output_base64sha256

  environment {
    variables = {
      S3_BUCKET_OUTPUTS = aws_s3_bucket.symposia_outputs.id
      AWS_REGION_NAME   = var.aws_region
    }
  }

  tags = merge(var.tags, {
    Component = "Symposia"
    Step      = "5a-LinkedIn"
  })
}

resource "aws_lambda_function" "symposia_instagram" {
  function_name    = "${var.project_name}-symposia-instagram-${var.environment}"
  role             = aws_iam_role.symposia_lambda.arn
  handler          = "handler.handler"
  runtime          = "python3.11"
  timeout          = 60
  memory_size      = 256
  filename         = data.archive_file.instagram.output_path
  source_code_hash = data.archive_file.instagram.output_base64sha256

  environment {
    variables = {
      S3_BUCKET_OUTPUTS = aws_s3_bucket.symposia_outputs.id
      AWS_REGION_NAME   = var.aws_region
    }
  }

  tags = merge(var.tags, {
    Component = "Symposia"
    Step      = "5b-Instagram"
  })
}

resource "aws_lambda_function" "symposia_partner_report" {
  function_name    = "${var.project_name}-symposia-partner-report-${var.environment}"
  role             = aws_iam_role.symposia_lambda.arn
  handler          = "handler.handler"
  runtime          = "python3.11"
  timeout          = 60
  memory_size      = 256
  filename         = data.archive_file.partner_report.output_path
  source_code_hash = data.archive_file.partner_report.output_base64sha256

  environment {
    variables = {
      S3_BUCKET_OUTPUTS = aws_s3_bucket.symposia_outputs.id
      AWS_REGION_NAME   = var.aws_region
    }
  }

  tags = merge(var.tags, {
    Component = "Symposia"
    Step      = "5c-PartnerReport"
  })
}

resource "aws_lambda_function" "symposia_notify" {
  function_name    = "${var.project_name}-symposia-notify-${var.environment}"
  role             = aws_iam_role.symposia_lambda.arn
  handler          = "handler.handler"
  runtime          = "python3.11"
  timeout          = 60
  memory_size      = 256
  filename         = data.archive_file.notify.output_path
  source_code_hash = data.archive_file.notify.output_base64sha256

  environment {
    variables = {
      S3_BUCKET_OUTPUTS      = aws_s3_bucket.symposia_outputs.id
      AWS_REGION_NAME        = var.aws_region
      SQS_APPROVAL_QUEUE_URL = aws_sqs_queue.symposia_approval.url
      STAFF_EMAIL            = var.symposia_staff_email
    }
  }

  tags = merge(var.tags, {
    Component = "Symposia"
    Step      = "6-Notify"
  })
}
