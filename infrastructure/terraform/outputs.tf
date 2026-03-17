# ============================================================
# Chronopoli – Terraform Outputs
# ============================================================

output "ec2_public_ip" {
  description = "Elastic IP of the EC2 instance"
  value       = aws_eip.chronopoli.public_ip
}

output "ec2_instance_id" {
  description = "EC2 instance ID"
  value       = aws_instance.chronopoli.id
}

output "rds_endpoint" {
  description = "RDS MySQL endpoint"
  value       = aws_db_instance.chronopoli.endpoint
}

output "rds_address" {
  description = "RDS MySQL address (hostname only)"
  value       = aws_db_instance.chronopoli.address
}

output "s3_media_bucket" {
  description = "S3 media bucket name"
  value       = aws_s3_bucket.media.id
}

output "s3_static_bucket" {
  description = "S3 static assets bucket name"
  value       = aws_s3_bucket.static.id
}

output "s3_backups_bucket" {
  description = "S3 backups bucket name"
  value       = aws_s3_bucket.backups.id
}

output "cloudfront_domain" {
  description = "CloudFront distribution domain name"
  value       = aws_cloudfront_distribution.chronopoli.domain_name
}

output "cloudfront_distribution_id" {
  description = "CloudFront distribution ID"
  value       = aws_cloudfront_distribution.chronopoli.id
}

output "security_group_id" {
  description = "EC2 security group ID"
  value       = aws_security_group.chronopoli.id
}

# Route53
output "route53_zone_id" {
  description = "Route53 hosted zone ID"
  value       = aws_route53_zone.main.zone_id
}

output "route53_nameservers" {
  description = "Route53 nameservers (set these at your domain registrar)"
  value       = aws_route53_zone.main.name_servers
}

# SES
output "ses_smtp_endpoint" {
  description = "SES SMTP endpoint for Tutor config"
  value       = "email-smtp.${var.aws_region}.amazonaws.com"
}

output "ses_smtp_username" {
  description = "SES SMTP username (IAM access key)"
  value       = aws_iam_access_key.ses_smtp.id
}

output "ses_smtp_password" {
  description = "SES SMTP password (IAM secret converted to SMTP password)"
  value       = aws_iam_access_key.ses_smtp.ses_smtp_password_v4
  sensitive   = true
}

# Engineer helper: generate production.env from Terraform outputs
output "engineer_env_config" {
  description = "Copy this block into your production.env file"
  sensitive   = true
  value       = <<-EOT

    # === AUTO-GENERATED FROM TERRAFORM OUTPUTS ===
    # Copy these values into /data/chronopoli/production.env

    CHRONOPOLI_DOMAIN=${var.domain_name}
    CHRONOPOLI_LMS_HOST=${var.lms_subdomain}.${var.domain_name}
    CHRONOPOLI_CMS_HOST=${var.cms_subdomain}.${var.domain_name}
    AWS_REGION=${var.aws_region}

    # EC2
    EC2_PUBLIC_IP=${aws_eip.chronopoli.public_ip}

    # RDS MySQL
    MYSQL_HOST=${aws_db_instance.chronopoli.address}
    MYSQL_PORT=3306
    MYSQL_ROOT_USERNAME=${var.rds_username}
    MYSQL_ROOT_PASSWORD=<your-rds-password>

    # S3
    S3_MEDIA_BUCKET=${aws_s3_bucket.media.id}
    S3_STATIC_BUCKET=${aws_s3_bucket.static.id}
    S3_BACKUPS_BUCKET=${aws_s3_bucket.backups.id}

    # SES Email
    SMTP_HOST=email-smtp.${var.aws_region}.amazonaws.com
    SMTP_PORT=587
    SMTP_USERNAME=${aws_iam_access_key.ses_smtp.id}
    SMTP_PASSWORD=<run: terraform output -raw ses_smtp_password>

    # CloudFront
    CLOUDFRONT_DOMAIN=${aws_cloudfront_distribution.chronopoli.domain_name}

    # Route53 Nameservers (set at registrar):
    # ${join(", ", aws_route53_zone.main.name_servers)}
  EOT
}
