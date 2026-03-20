# ============================================================
# Chronopoli – SQS Queues (Symposia Approval Pipeline)
# ============================================================

# Dead letter queue for failed approval messages
resource "aws_sqs_queue" "symposia_approval_dlq" {
  name                      = "${var.project_name}-symposia-approval-dlq-${var.environment}"
  message_retention_seconds = 1209600  # 14 days
  receive_wait_time_seconds = 0

  tags = merge(var.tags, {
    Component = "Symposia"
    Purpose   = "DeadLetterQueue"
  })
}

# Main approval queue
resource "aws_sqs_queue" "symposia_approval" {
  name                       = "${var.project_name}-symposia-approval-${var.environment}"
  message_retention_seconds  = 1209600  # 14 days
  visibility_timeout_seconds = 30
  receive_wait_time_seconds  = 10  # Long polling

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.symposia_approval_dlq.arn
    maxReceiveCount     = 3
  })

  tags = merge(var.tags, {
    Component = "Symposia"
    Purpose   = "ApprovalQueue"
  })
}

# Policy: Allow Lambda to send messages
resource "aws_sqs_queue_policy" "symposia_approval" {
  queue_url = aws_sqs_queue.symposia_approval.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "AllowLambdaSend"
        Effect    = "Allow"
        Principal = {
          AWS = aws_iam_role.symposia_lambda.arn
        }
        Action = [
          "sqs:SendMessage"
        ]
        Resource = aws_sqs_queue.symposia_approval.arn
      },
      {
        Sid       = "AllowEC2Receive"
        Effect    = "Allow"
        Principal = {
          AWS = "*"
        }
        Action = [
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage",
          "sqs:GetQueueAttributes"
        ]
        Resource = aws_sqs_queue.symposia_approval.arn
        Condition = {
          StringEquals = {
            "aws:SourceAccount" = data.aws_caller_identity.current.account_id
          }
        }
      }
    ]
  })
}
