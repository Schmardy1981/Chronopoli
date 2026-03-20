# ============================================================
# Chronopoli – Amazon Bedrock Knowledge Base + OpenSearch Serverless
# Powers the AI Tutor (Phase 13) with RAG over all platform content.
# ============================================================

# S3 bucket for AI Tutor knowledge base content
resource "aws_s3_bucket" "knowledge" {
  bucket = "${var.project_name}-knowledge-${var.environment}"

  tags = {
    Name        = "${var.project_name}-knowledge"
    Environment = var.environment
    Service     = "ai-tutor"
  }
}

resource "aws_s3_bucket_versioning" "knowledge" {
  bucket = aws_s3_bucket.knowledge.id
  versioning_configuration { status = "Enabled" }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "knowledge" {
  bucket = aws_s3_bucket.knowledge.id
  rule {
    apply_server_side_encryption_by_default { sse_algorithm = "AES256" }
  }
}

# Folder structure for knowledge base ingestion
# opinion-papers/       ← PDFs from Symposia pipeline
# course-content/       ← Course module text exported from OpenEdX
# round-table-transcripts/ ← Full transcripts
# partner-materials/    ← Partner-uploaded content
# masterclass-docs/     ← Expert documents for Digital Twins

# --- OpenSearch Serverless (Vector Store for Bedrock) ---

resource "aws_opensearchserverless_security_policy" "encryption" {
  name = "${var.project_name}-tutor-encryption"
  type = "encryption"
  policy = jsonencode({
    Rules = [{
      ResourceType = "collection"
      Resource     = ["collection/${var.project_name}-tutor"]
    }]
    AWSOwnedKey = true
  })
}

resource "aws_opensearchserverless_security_policy" "network" {
  name = "${var.project_name}-tutor-network"
  type = "network"
  policy = jsonencode([{
    Rules = [{
      ResourceType = "collection"
      Resource     = ["collection/${var.project_name}-tutor"]
    }, {
      ResourceType = "dashboard"
      Resource     = ["collection/${var.project_name}-tutor"]
    }]
    AllowFromPublic = true
  }])
}

resource "aws_opensearchserverless_collection" "tutor" {
  name = "${var.project_name}-tutor"
  type = "VECTORSEARCH"

  depends_on = [
    aws_opensearchserverless_security_policy.encryption,
    aws_opensearchserverless_security_policy.network,
  ]

  tags = {
    Name        = "${var.project_name}-tutor-vectors"
    Environment = var.environment
    Service     = "ai-tutor"
  }
}

# --- IAM Role for Bedrock Knowledge Base ---

resource "aws_iam_role" "bedrock_kb" {
  name = "${var.project_name}-bedrock-kb-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "bedrock.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })

  tags = {
    Name        = "${var.project_name}-bedrock-kb-role"
    Environment = var.environment
  }
}

resource "aws_iam_role_policy" "bedrock_kb_s3" {
  name = "${var.project_name}-bedrock-kb-s3"
  role = aws_iam_role.bedrock_kb.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = ["s3:GetObject", "s3:ListBucket"]
      Resource = [
        aws_s3_bucket.knowledge.arn,
        "${aws_s3_bucket.knowledge.arn}/*",
      ]
    }]
  })
}

resource "aws_iam_role_policy" "bedrock_kb_opensearch" {
  name = "${var.project_name}-bedrock-kb-opensearch"
  role = aws_iam_role.bedrock_kb.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["aoss:APIAccessAll"]
      Resource = [aws_opensearchserverless_collection.tutor.arn]
    }]
  })
}

# --- Bedrock Knowledge Base ---
# NOTE: aws_bedrockagent_knowledge_base requires the Bedrock Agent provider
# which may not be available in all regions. If me-central-1 doesn't support
# Bedrock, deploy this in eu-west-1 and use cross-region S3 replication.

resource "aws_bedrockagent_knowledge_base" "tutor" {
  name     = "${var.project_name}-tutor-kb"
  role_arn = aws_iam_role.bedrock_kb.arn

  knowledge_base_configuration {
    type = "VECTOR"
    vector_knowledge_base_configuration {
      embedding_model_arn = "arn:aws:bedrock:${var.aws_region}::foundation-model/amazon.titan-embed-text-v2:0"
    }
  }

  storage_configuration {
    type = "OPENSEARCH_SERVERLESS"
    opensearch_serverless_configuration {
      collection_arn    = aws_opensearchserverless_collection.tutor.arn
      vector_index_name = "${var.project_name}-knowledge-index"
      field_mapping {
        vector_field   = "embedding"
        text_field     = "AMAZON_BEDROCK_TEXT_CHUNK"
        metadata_field = "AMAZON_BEDROCK_METADATA"
      }
    }
  }

  tags = {
    Name        = "${var.project_name}-tutor-kb"
    Environment = var.environment
  }
}

resource "aws_bedrockagent_data_source" "s3_knowledge" {
  knowledge_base_id = aws_bedrockagent_knowledge_base.tutor.id
  name              = "${var.project_name}-s3-knowledge"

  data_source_configuration {
    type = "S3"
    s3_configuration {
      bucket_arn = aws_s3_bucket.knowledge.arn
    }
  }

  vector_ingestion_configuration {
    chunking_configuration {
      chunking_strategy = "FIXED_SIZE"
      fixed_size_chunking_configuration {
        max_tokens         = 300
        overlap_percentage = 20
      }
    }
  }
}

# --- Outputs ---

output "bedrock_knowledge_base_id" {
  value       = aws_bedrockagent_knowledge_base.tutor.id
  description = "Bedrock Knowledge Base ID — set in Tutor config as BEDROCK_KNOWLEDGE_BASE_ID"
}

output "bedrock_data_source_id" {
  value       = aws_bedrockagent_data_source.s3_knowledge.id
  description = "Bedrock Data Source ID — set in Tutor config as BEDROCK_DATA_SOURCE_ID"
}

output "opensearch_collection_endpoint" {
  value       = aws_opensearchserverless_collection.tutor.collection_endpoint
  description = "OpenSearch Serverless collection endpoint"
}

output "knowledge_bucket_name" {
  value       = aws_s3_bucket.knowledge.id
  description = "S3 bucket for AI Tutor knowledge content"
}
