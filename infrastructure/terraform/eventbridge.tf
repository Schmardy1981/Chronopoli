# ============================================================
# Chronopoli – EventBridge Rules (Symposia Pipeline Trigger)
# ============================================================

# EventBridge rule: trigger on IVS recording completion
resource "aws_cloudwatch_event_rule" "ivs_recording_ended" {
  name        = "${var.project_name}-ivs-recording-ended-${var.environment}"
  description = "Triggers Symposia pipeline when an IVS recording ends"

  event_pattern = jsonencode({
    source      = ["aws.ivs"]
    detail-type = ["IVS Recording State Change"]
    detail = {
      recording_status = ["Recording End"]
    }
  })

  tags = merge(var.tags, {
    Component = "Symposia"
  })
}

# Target: Start Step Functions state machine
resource "aws_cloudwatch_event_target" "symposia_sfn" {
  rule     = aws_cloudwatch_event_rule.ivs_recording_ended.name
  arn      = aws_sfn_state_machine.symposia_pipeline.arn
  role_arn = aws_iam_role.eventbridge_symposia.arn

  input_transformer {
    input_paths = {
      s3_bucket = "$.detail.s3.bucket"
      s3_key    = "$.detail.s3.key"
      channel   = "$.detail.channel_name"
    }
    input_template = <<-EOT
      {
        "recording_s3_uri": "s3://<s3_bucket>/<s3_key>",
        "round_table_id": "<channel>",
        "district_codes": []
      }
    EOT
  }
}

# IAM Role for EventBridge to start Step Functions
resource "aws_iam_role" "eventbridge_symposia" {
  name = "${var.project_name}-eventbridge-symposia-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "events.amazonaws.com"
        }
      }
    ]
  })

  tags = merge(var.tags, {
    Component = "Symposia"
  })
}

resource "aws_iam_role_policy" "eventbridge_symposia_sfn" {
  name = "eventbridge-start-sfn"
  role = aws_iam_role.eventbridge_symposia.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "states:StartExecution"
        ]
        Resource = aws_sfn_state_machine.symposia_pipeline.arn
      }
    ]
  })
}
