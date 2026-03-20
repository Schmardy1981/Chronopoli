# ============================================================
# Chronopoli – AWS Systems Manager Parameter Store
# Stores secrets for Stripe, ElevenLabs, HeyGen, and other
# services. Retrieved at runtime by Django via boto3.
# ============================================================

# --- Stripe ---

resource "aws_ssm_parameter" "stripe_secret_key" {
  name        = "/chronopoli/stripe/secret_key"
  description = "Stripe secret key for payment processing"
  type        = "SecureString"
  value       = var.stripe_secret_key

  tags = {
    Project     = var.project_name
    Environment = var.environment
    Service     = "stripe"
  }
}

resource "aws_ssm_parameter" "stripe_webhook_secret" {
  name        = "/chronopoli/stripe/webhook_secret"
  description = "Stripe webhook signing secret"
  type        = "SecureString"
  value       = var.stripe_webhook_secret

  tags = {
    Project     = var.project_name
    Environment = var.environment
    Service     = "stripe"
  }
}

resource "aws_ssm_parameter" "stripe_connect_client_id" {
  name        = "/chronopoli/stripe/connect_client_id"
  description = "Stripe Connect platform client ID for partner payouts"
  type        = "SecureString"
  value       = var.stripe_connect_client_id

  tags = {
    Project     = var.project_name
    Environment = var.environment
    Service     = "stripe"
  }
}

resource "aws_ssm_parameter" "stripe_publishable_key" {
  name        = "/chronopoli/stripe/publishable_key"
  description = "Stripe publishable key (safe for frontend)"
  type        = "String"
  value       = var.stripe_publishable_key

  tags = {
    Project     = var.project_name
    Environment = var.environment
    Service     = "stripe"
  }
}
