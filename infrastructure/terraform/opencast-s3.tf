# ============================================================
# Chronopoli – S3 Bucket for Opencast Video Storage
# ============================================================

resource "aws_s3_bucket" "opencast_video" {
  bucket = "${var.project_name}-opencast-video-${var.environment}"

  tags = {
    Name        = "${var.project_name}-opencast-video-${var.environment}"
    Environment = var.environment
    Service     = "opencast"
  }
}

resource "aws_s3_bucket_versioning" "opencast_video" {
  bucket = aws_s3_bucket.opencast_video.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_public_access_block" "opencast_video" {
  bucket = aws_s3_bucket.opencast_video.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

resource "aws_s3_bucket_policy" "opencast_video_public_read" {
  bucket = aws_s3_bucket.opencast_video.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "PublicReadGetObject"
        Effect    = "Allow"
        Principal = "*"
        Action    = "s3:GetObject"
        Resource  = "${aws_s3_bucket.opencast_video.arn}/*"
      },
    ]
  })

  depends_on = [aws_s3_bucket_public_access_block.opencast_video]
}

# Add Opencast S3 bucket to EC2 IAM policy
resource "aws_iam_role_policy" "opencast_s3_access" {
  name = "${var.project_name}-opencast-s3-access"
  role = aws_iam_role.chronopoli.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket",
        ]
        Resource = [
          aws_s3_bucket.opencast_video.arn,
          "${aws_s3_bucket.opencast_video.arn}/*",
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "transcribe:StartTranscriptionJob",
          "transcribe:GetTranscriptionJob",
          "transcribe:ListTranscriptionJobs",
        ]
        Resource = "*"
      },
    ]
  })
}
