# ============================================================
# Chronopoli – Terraform Variables
# ============================================================

variable "aws_region" {
  description = "AWS region for deployment"
  type        = string
  default     = "me-central-1"
}

variable "environment" {
  description = "Deployment environment (production, staging)"
  type        = string
  default     = "production"
}

variable "project_name" {
  description = "Project name for resource tagging"
  type        = string
  default     = "chronopoli"
}

# EC2
variable "ec2_instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.xlarge"
}

variable "ec2_ami" {
  description = "Ubuntu 22.04 LTS AMI ID (region-specific)"
  type        = string
  default     = ""
}

variable "ec2_key_name" {
  description = "SSH key pair name"
  type        = string
}

variable "ec2_root_volume_size" {
  description = "Root EBS volume size in GB"
  type        = number
  default     = 50
}

variable "ec2_data_volume_size" {
  description = "Data EBS volume size in GB"
  type        = number
  default     = 100
}

variable "admin_ssh_cidr" {
  description = "CIDR block allowed for SSH access (e.g. your IP/32)"
  type        = string
}

# RDS
variable "rds_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.medium"
}

variable "rds_allocated_storage" {
  description = "RDS initial storage in GB"
  type        = number
  default     = 50
}

variable "rds_max_allocated_storage" {
  description = "RDS max auto-scaling storage in GB"
  type        = number
  default     = 200
}

variable "rds_db_name" {
  description = "Database name"
  type        = string
  default     = "openedx"
}

variable "rds_username" {
  description = "RDS master username"
  type        = string
  default     = "admin"
  sensitive   = true
}

variable "rds_password" {
  description = "RDS master password"
  type        = string
  sensitive   = true
}

variable "rds_multi_az" {
  description = "Enable Multi-AZ for RDS"
  type        = bool
  default     = true
}

# Domain
variable "domain_name" {
  description = "Root domain name"
  type        = string
  default     = "chronopoli.io"
}

variable "lms_subdomain" {
  description = "LMS subdomain"
  type        = string
  default     = "learn"
}

variable "cms_subdomain" {
  description = "CMS (Studio) subdomain"
  type        = string
  default     = "studio"
}

# Stripe (E-Commerce)
variable "stripe_secret_key" {
  description = "Stripe secret key (sk_live_...)"
  type        = string
  sensitive   = true
  default     = ""
}

variable "stripe_publishable_key" {
  description = "Stripe publishable key (pk_live_...)"
  type        = string
  default     = ""
}

variable "stripe_webhook_secret" {
  description = "Stripe webhook signing secret (whsec_...)"
  type        = string
  sensitive   = true
  default     = ""
}

variable "stripe_connect_client_id" {
  description = "Stripe Connect platform client ID"
  type        = string
  sensitive   = true
  default     = ""
}

# Tags
variable "tags" {
  description = "Common tags for all resources"
  type        = map(string)
  default = {
    Project     = "Chronopoli"
    ManagedBy   = "Terraform"
    Organization = "DBCC"
  }
}
