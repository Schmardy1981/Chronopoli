# ============================================================
# Chronopoli – AWS SES (Email)
# ============================================================

# Domain identity for sending emails
resource "aws_ses_domain_identity" "chronopoli" {
  domain = var.domain_name
}

# DKIM for email authentication
resource "aws_ses_domain_dkim" "chronopoli" {
  domain = aws_ses_domain_identity.chronopoli.domain
}

# Route53 records for SES domain verification
resource "aws_route53_record" "ses_verification" {
  zone_id = aws_route53_zone.main.zone_id
  name    = "_amazonses.${var.domain_name}"
  type    = "TXT"
  ttl     = 600
  records = [aws_ses_domain_identity.chronopoli.verification_token]
}

# Route53 records for DKIM
resource "aws_route53_record" "ses_dkim" {
  count   = 3
  zone_id = aws_route53_zone.main.zone_id
  name    = "${aws_ses_domain_dkim.chronopoli.dkim_tokens[count.index]}._domainkey.${var.domain_name}"
  type    = "CNAME"
  ttl     = 600
  records = ["${aws_ses_domain_dkim.chronopoli.dkim_tokens[count.index]}.dkim.amazonses.com"]
}

# MX record for receiving bounce notifications
resource "aws_route53_record" "ses_mail_from_mx" {
  zone_id = aws_route53_zone.main.zone_id
  name    = "mail.${var.domain_name}"
  type    = "MX"
  ttl     = 600
  records = ["10 feedback-smtp.${var.aws_region}.amazonses.com"]
}

# SPF record
resource "aws_route53_record" "ses_spf" {
  zone_id = aws_route53_zone.main.zone_id
  name    = "mail.${var.domain_name}"
  type    = "TXT"
  ttl     = 600
  records = ["v=spf1 include:amazonses.com ~all"]
}

# Mail-from domain
resource "aws_ses_domain_mail_from" "chronopoli" {
  domain           = aws_ses_domain_identity.chronopoli.domain
  mail_from_domain = "mail.${var.domain_name}"
}

# IAM user for SMTP credentials (Tutor needs SMTP user/pass)
resource "aws_iam_user" "ses_smtp" {
  name = "${var.project_name}-${var.environment}-ses-smtp"

  tags = {
    Name        = "${var.project_name}-ses-smtp"
    Environment = var.environment
  }
}

resource "aws_iam_user_policy" "ses_smtp" {
  name = "${var.project_name}-ses-send"
  user = aws_iam_user.ses_smtp.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ses:SendEmail",
          "ses:SendRawEmail",
        ]
        Resource = "*"
        Condition = {
          StringEquals = {
            "ses:FromAddress" = [
              "noreply@${var.domain_name}",
              "support@${var.domain_name}",
              "platform@${var.domain_name}",
            ]
          }
        }
      },
    ]
  })
}

resource "aws_iam_access_key" "ses_smtp" {
  user = aws_iam_user.ses_smtp.name
}
