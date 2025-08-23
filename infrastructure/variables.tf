variable "project_id" {
  description = "GCP Project ID"
  type        = string

  validation {
    condition     = length(var.project_id) > 0
    error_message = "The project_id variable cannot be empty. Please provide a valid GCP Project ID."
  }
}

variable "region" {
  description = "Region for services like Cloud Run, Cloud Functions, etc."
  type        = string

  validation {
    condition     = length(var.region) > 0
    error_message = "The region variable cannot be empty. Please provide a valid region."
  }
}

variable "bq_location" {
  description = "Location for BigQuery (typically multi-regional like US or EU)"
  type        = string

  validation {
    condition     = length(var.bq_location) > 0
    error_message = "The bq_location variable cannot be empty. Please provide a valid BigQuery location."
  }
}

variable "service_name" {
  description = "The snake_case_service_name used for naming resources"
  type        = string

  validation {
    condition     = length(var.service_name) > 0
    error_message = "The service_name variable cannot be empty. Please provide a valid service name in snake_case."
  }
}

variable "service_name_kebab_case" {
  description = "The kebab-case-service-name used for naming resources"
  type        = string

  validation {
    condition     = length(var.service_name_kebab_case) > 0
    error_message = "The service_name_kebab_case variable cannot be empty. Please provide a valid service name in kebab-case."
  }
}

variable "service_account_run" {
  description = "The service account name for the pipeline service account"
  type        = string

  validation {
    condition     = length(var.service_account_run) > 5 && length(var.service_account_run) < 31
    error_message = "The service_account_run variable must be between 6 and 30 characters."
  }
}

variable "image" {
  description = "The image URL for the Cloud Run service"
  type        = string

  validation {
    condition     = length(var.image) > 0
    error_message = "The image variable cannot be empty. Please provide a valid image URL."
  }
}

variable "pipeline_bucket_name" {
  description = "The name of the GCS bucket used general storage"
  type        = string

  validation {
    condition     = length(var.pipeline_bucket_name) > 0
    error_message = "The pipeline_bucket_name variable cannot be empty. Please provide a valid GCS bucket name."
  }
}

variable "backup_bucket_name" {
  description = "The name of the GCS bucket used for BigQuery backups"
  type        = string

  validation {
    condition     = length(var.backup_bucket_name) > 0
    error_message = "The backup_bucket_name variable cannot be empty. Please provide a valid GCS bucket name."
  }
}

variable "search_service_url" {
  description = "The URL of the search service to call"
  type        = string

  validation {
    condition     = length(var.search_service_url) > 0
    error_message = "The search_service_url variable cannot be empty. Please provide a valid search service URL."
  }
}

variable "postgres_instance" {
  description = "The full Cloud SQL instance connection name (format: project:region:instance)"
  type        = string

  validation {
    condition     = length(var.postgres_instance) > 0
    error_message = "The postgres_instance variable cannot be empty. Please provide a valid Cloud SQL instance connection name."
  }
}

variable "postgres_instance_name" {
  description = "The Cloud SQL instance name only (without project:region prefix)"
  type        = string

  validation {
    condition     = length(var.postgres_instance_name) > 0
    error_message = "The postgres_instance_name variable cannot be empty. Please provide a valid Cloud SQL instance name."
  }
}

variable "postgres_db" {
  description = "The PostgreSQL database name for book-agent"
  type        = string

  validation {
    condition     = length(var.postgres_db) > 0
    error_message = "The postgres_db variable cannot be empty. Please provide a valid database name."
  }
}

variable "postgres_user" {
  description = "The PostgreSQL username for basic authentication"
  type        = string

  validation {
    condition     = length(var.postgres_user) > 0
    error_message = "The postgres_user variable cannot be empty. Please provide a valid PostgreSQL username."
  }
}

variable "postgres_password" {
  description = "The PostgreSQL password for basic authentication"
  type        = string
  sensitive   = true

  validation {
    condition     = length(var.postgres_password) > 0
    error_message = "The postgres_password variable cannot be empty. Please provide a valid PostgreSQL password."
  }
}