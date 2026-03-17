# ============================================================
# Chronopoli – Route53 DNS
# ============================================================

# Hosted zone for the domain
resource "aws_route53_zone" "main" {
  name    = var.domain_name
  comment = "Chronopoli platform DNS"

  tags = {
    Name        = "${var.project_name}-dns"
    Environment = var.environment
  }
}

# LMS: learn.chronopoli.io → CloudFront
resource "aws_route53_record" "lms" {
  zone_id = aws_route53_zone.main.zone_id
  name    = "${var.lms_subdomain}.${var.domain_name}"
  type    = "A"

  alias {
    name                   = aws_cloudfront_distribution.chronopoli.domain_name
    zone_id                = aws_cloudfront_distribution.chronopoli.hosted_zone_id
    evaluate_target_health = false
  }
}

# Studio: studio.chronopoli.io → EC2 directly (not behind CDN)
resource "aws_route53_record" "cms" {
  zone_id = aws_route53_zone.main.zone_id
  name    = "${var.cms_subdomain}.${var.domain_name}"
  type    = "A"
  ttl     = 300
  records = [aws_eip.chronopoli.public_ip]
}

# Preview: preview.learn.chronopoli.io → EC2
resource "aws_route53_record" "preview" {
  zone_id = aws_route53_zone.main.zone_id
  name    = "preview.${var.lms_subdomain}.${var.domain_name}"
  type    = "A"
  ttl     = 300
  records = [aws_eip.chronopoli.public_ip]
}

# ACM DNS validation records
resource "aws_route53_record" "acm_validation" {
  for_each = {
    for dvo in aws_acm_certificate.chronopoli.domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  }

  zone_id = aws_route53_zone.main.zone_id
  name    = each.value.name
  type    = each.value.type
  ttl     = 60
  records = [each.value.record]

  allow_overwrite = true
}

# ACM certificate validation
resource "aws_acm_certificate_validation" "chronopoli" {
  provider                = aws.us_east_1
  certificate_arn         = aws_acm_certificate.chronopoli.arn
  validation_record_fqdns = [for record in aws_route53_record.acm_validation : record.fqdn]
}
