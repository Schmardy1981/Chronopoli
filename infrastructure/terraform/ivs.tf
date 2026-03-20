# ============================================================
# Chronopoli – IVS Recording Configuration (Symposia Pipeline)
# ============================================================

# S3 bucket for IVS recording storage
resource "aws_s3_bucket" "ivs_recordings" {
  bucket = "${var.project_name}-ivs-recordings-${var.environment}"

  tags = merge(var.tags, {
    Component = "Symposia"
    Service   = "IVS"
  })
}

resource "aws_s3_bucket_versioning" "ivs_recordings" {
  bucket = aws_s3_bucket.ivs_recordings.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "ivs_recordings" {
  bucket = aws_s3_bucket.ivs_recordings.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "ivs_recordings" {
  bucket = aws_s3_bucket.ivs_recordings.id

  rule {
    id     = "archive-old-recordings"
    status = "Enabled"

    transition {
      days          = 90
      storage_class = "GLACIER"
    }

    expiration {
      days = 365
    }
  }
}

resource "aws_s3_bucket_public_access_block" "ivs_recordings" {
  bucket = aws_s3_bucket.ivs_recordings.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# S3 bucket policy granting IVS service write access
resource "aws_s3_bucket_policy" "ivs_recordings" {
  bucket = aws_s3_bucket.ivs_recordings.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "AllowIVSRecordingWrite"
        Effect    = "Allow"
        Principal = {
          Service = "ivs.amazonaws.com"
        }
        Action = [
          "s3:PutObject",
          "s3:PutObjectAcl"
        ]
        Resource = "${aws_s3_bucket.ivs_recordings.arn}/*"
        Condition = {
          StringEquals = {
            "aws:SourceAccount" = data.aws_caller_identity.current.account_id
          }
        }
      }
    ]
  })
}

# IVS Recording Configuration
resource "aws_ivs_recording_configuration" "symposia" {
  name = "${var.project_name}-symposia-${var.environment}"

  destination_configuration {
    s3 {
      bucket_name = aws_s3_bucket.ivs_recordings.id
    }
  }

  thumbnail_configuration {
    recording_mode = "INTERVAL"
    target_interval_seconds = 60
  }

  tags = merge(var.tags, {
    Component = "Symposia"
  })
}

# Data source for account ID (used in bucket policy)
data "aws_caller_identity" "current" {}
