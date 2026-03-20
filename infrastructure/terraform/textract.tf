# ============================================================
# Chronopoli – AWS Textract + External API Keys (SSM)
# For Digital Twin document processing (Phase 14)
# ============================================================

# IAM policy: allow EC2 (and Lambda) to call Textract
resource "aws_iam_role_policy" "textract_access" {
  name = "${var.project_name}-textract-access"
  role = aws_iam_role.chronopoli.id  # EC2 instance role from main.tf

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "textract:DetectDocumentText",
        "textract:AnalyzeDocument",
        "textract:StartDocumentTextDetection",
        "textract:GetDocumentTextDetection",
      ]
      Resource = "*"
    }]
  })
}

# IAM policy: allow EC2 to call Bedrock (for AI Tutor + analysis)
resource "aws_iam_role_policy" "bedrock_access" {
  name = "${var.project_name}-bedrock-access"
  role = aws_iam_role.chronopoli.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel",
          "bedrock:InvokeModelWithResponseStream",
        ]
        Resource = "arn:aws:bedrock:${var.aws_region}::foundation-model/*"
      },
      {
        Effect = "Allow"
        Action = [
          "bedrock-agent:Retrieve",
          "bedrock-agent:RetrieveAndGenerate",
        ]
        Resource = "*"
      },
    ]
  })
}

# --- SSM Parameters for External API Keys ---

resource "aws_ssm_parameter" "elevenlabs_api_key" {
  name        = "/chronopoli/elevenlabs/api_key"
  description = "ElevenLabs API key for voice cloning (Digital Twin)"
  type        = "SecureString"
  value       = var.elevenlabs_api_key

  tags = {
    Project     = var.project_name
    Environment = var.environment
    Service     = "masterclass"
  }
}

resource "aws_ssm_parameter" "heygen_api_key" {
  name        = "/chronopoli/heygen/api_key"
  description = "HeyGen API key for avatar video generation (Digital Twin)"
  type        = "SecureString"
  value       = var.heygen_api_key

  tags = {
    Project     = var.project_name
    Environment = var.environment
    Service     = "masterclass"
  }
}

resource "aws_ssm_parameter" "anthropic_api_key" {
  name        = "/chronopoli/anthropic/api_key"
  description = "Anthropic API key for Claude (Lambda pipeline + Presenton)"
  type        = "SecureString"
  value       = var.anthropic_api_key

  tags = {
    Project     = var.project_name
    Environment = var.environment
    Service     = "symposia"
  }
}
