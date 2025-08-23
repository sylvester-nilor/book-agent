terraform {
  # Temporarily using local backend until GCS bucket is created
  # backend "gcs" {}
}

data "google_compute_default_service_account" "default" {
  project = var.project_id
}

# -------------------------------------------------------------------------
# Enable Required APIs
# -------------------------------------------------------------------------

resource "google_project_service" "enable_firestore" {
  project = var.project_id
  service = "firestore.googleapis.com"
}

resource "google_project_service" "enable_cloud_run" {
  project = var.project_id
  service = "run.googleapis.com"
}

resource "google_project_service" "enable_bigquery" {
  project = var.project_id
  service = "bigquery.googleapis.com"
}

resource "google_project_service" "enable_storage" {
  project = var.project_id
  service = "storage.googleapis.com"
}

resource "google_project_service" "enable_generative_ai" {
  project = var.project_id
  service = "generativelanguage.googleapis.com"
}

resource "google_project_service" "enable_vertex_ai" {
  project = var.project_id
  service = "aiplatform.googleapis.com"
}

resource "google_project_service" "enable_sql_admin" {
  project = var.project_id
  service = "sqladmin.googleapis.com"
}



# -------------------------------------------------------------------------
# Service Account: Cloud Run Service Account
# -------------------------------------------------------------------------

resource "google_service_account" "cloud_run_app_sa" {
  project      = var.project_id
  account_id   = var.service_account_run
  display_name = "Cloud Run service account"

  depends_on = [
    google_project_service.enable_firestore,
    google_project_service.enable_cloud_run,
    google_project_service.enable_bigquery,
    google_project_service.enable_storage,
    google_project_service.enable_generative_ai,
    google_project_service.enable_vertex_ai
  ]
}

resource "google_project_iam_member" "pipeline_sa_bigquery" {
  project = var.project_id
  role    = "roles/bigquery.dataEditor"
  member  = "serviceAccount:${google_service_account.cloud_run_app_sa.email}"
}

resource "google_project_iam_member" "pipeline_sa_bigquery_job" {
  project = var.project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.cloud_run_app_sa.email}"
}

resource "google_project_iam_member" "pipeline_sa_gcs" {
  project = var.project_id
  role    = "roles/storage.objectAdmin"
  member  = "serviceAccount:${google_service_account.cloud_run_app_sa.email}"
}

# Grant access to read from book_to_struct_v1 dataset
resource "google_project_iam_member" "pipeline_sa_book_to_struct_reader" {
  project = var.project_id
  role    = "roles/bigquery.dataViewer"
  member  = "serviceAccount:${google_service_account.cloud_run_app_sa.email}"
}

# Grant access to use the paragraph-to-embedding connection for the shared model
resource "google_project_iam_member" "pipeline_sa_paragraph_embedding_connection_user" {
  project = var.project_id
  role    = "roles/bigquery.connectionUser"
  member  = "serviceAccount:${google_service_account.cloud_run_app_sa.email}"
}

# Grant Firestore permissions to the Cloud Run service account
resource "google_project_iam_member" "pipeline_sa_firestore" {
  project = var.project_id
  role    = "roles/datastore.user"
  member  = "serviceAccount:${google_service_account.cloud_run_app_sa.email}"
}

resource "google_project_iam_member" "pipeline_sa_generative_ai" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.cloud_run_app_sa.email}"
}

# Grant Cloud SQL Client permissions
resource "google_project_iam_member" "pipeline_sa_cloudsql_client" {
  project = var.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.cloud_run_app_sa.email}"
}



# -------------------------------------------------------------------------
# PostgreSQL Database and User
# -------------------------------------------------------------------------

# Create database for book-agent
resource "google_sql_database" "book_agent_db" {
  project  = var.project_id
  name     = var.postgres_db
  instance = var.postgres_instance_name

  depends_on = [google_project_service.enable_sql_admin]
}

# Create IAM database user for the service account (without .gserviceaccount.com suffix)
resource "google_sql_user" "book_agent_user" {
  project  = var.project_id
  name     = replace(google_service_account.cloud_run_app_sa.email, ".gserviceaccount.com", "")
  instance = var.postgres_instance_name
  type     = "CLOUD_IAM_SERVICE_ACCOUNT"

  depends_on = [google_sql_database.book_agent_db]
}

# -------------------------------------------------------------------------
# Firestore Database
# -------------------------------------------------------------------------

resource "google_firestore_database" "database" {
  project     = var.project_id
  name        = "(default)"
  location_id = "us-central1"
  type        = "FIRESTORE_NATIVE"

  depends_on = [google_project_service.enable_firestore]
}

# -------------------------------------------------------------------------
# BigQuery Config
# -------------------------------------------------------------------------

resource "google_bigquery_dataset" "raw_dataset" {
  project     = var.project_id
  dataset_id  = "${var.service_name}_raw"
  location    = var.bq_location
  max_time_travel_hours = 168  # 7 days
  description = "Dataset to hold all raw data ingested"

  depends_on = [google_project_service.enable_bigquery]
}

resource "google_bigquery_dataset" "curated_dataset" {
  project     = var.project_id
  dataset_id  = "${var.service_name}_curated"
  location    = var.bq_location
  max_time_travel_hours = 168  # 7 days
  description = "Dataset meant to hold working data"
}

resource "google_bigquery_dataset" "prod_dataset" {
  project     = var.project_id
  dataset_id  = var.service_name
  location    = var.bq_location
  max_time_travel_hours = 168  # 7 days
  description = "Data product meant for consumption by other pipelines or humans"
}

resource "google_bigquery_dataset" "backup_dataset" {
  project     = var.project_id
  dataset_id  = "${var.service_name}_backup"
  location    = var.bq_location
  max_time_travel_hours = 168  # 7 days
  description = "Backup Dataset"
}

# Raw Dataset IAM Bindings
resource "google_bigquery_dataset_iam_member" "raw_dataset_run" {
  project    = var.project_id
  dataset_id = google_bigquery_dataset.raw_dataset.dataset_id
  role       = "roles/bigquery.dataEditor"
  member     = "serviceAccount:${google_service_account.cloud_run_app_sa.email}"
}

# Curated Dataset IAM Bindings
resource "google_bigquery_dataset_iam_member" "curated_dataset_run" {
  project    = var.project_id
  dataset_id = google_bigquery_dataset.curated_dataset.dataset_id
  role       = "roles/bigquery.dataEditor"
  member     = "serviceAccount:${google_service_account.cloud_run_app_sa.email}"
}

# Prod Dataset IAM Bindings
resource "google_bigquery_dataset_iam_member" "prod_dataset_run" {
  project    = var.project_id
  dataset_id = google_bigquery_dataset.prod_dataset.dataset_id
  role       = "roles/bigquery.dataEditor"
  member     = "serviceAccount:${google_service_account.cloud_run_app_sa.email}"
}

# Backup Dataset IAM Bindings
resource "google_bigquery_dataset_iam_member" "backup_dataset_run" {
  project    = var.project_id
  dataset_id = google_bigquery_dataset.backup_dataset.dataset_id
  role = "roles/bigquery.dataOwner"
  member     = "serviceAccount:${google_service_account.cloud_run_app_sa.email}"
}

resource "google_bigquery_connection" "book_agent_connection" {
  project       = var.project_id
  connection_id = "book_agent_v1_connection"
  location      = "US"
  cloud_resource {}
}

# Grant Vertex AI User role to the connection's service account
resource "google_project_iam_member" "connection_vertex_ai_user" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_bigquery_connection.book_agent_connection.cloud_resource[0].service_account_id}"
}

# -------------------------------------------------------------------------
# General Bucket Config
# -------------------------------------------------------------------------

resource "google_storage_bucket" "pipeline_bucket" {
  project  = var.project_id
  location = var.region
  name     = var.pipeline_bucket_name

  depends_on = [google_project_service.enable_storage]
}

# -------------------------------------------------------------------------
# GCS Backup Bucket Config
# -------------------------------------------------------------------------

resource "google_storage_bucket" "bigquery_backup_bucket" {
  project  = var.project_id
  location = var.region
  name     = var.backup_bucket_name

  retention_policy {
    retention_period = 31536000  # 1 year in seconds
  }

  lifecycle_rule {
    action {
      type          = "SetStorageClass"
      storage_class = "NEARLINE"
    }
    condition {
      age = 30
    }
  }

  lifecycle_rule {
    action {
      type          = "SetStorageClass"
      storage_class = "COLDLINE"
    }
    condition {
      age = 90
    }
  }

  lifecycle_rule {
    action {
      type          = "SetStorageClass"
      storage_class = "ARCHIVE"
    }
    condition {
      age = 365
    }
  }
}

# -------------------------------------------------------------------------
# Cloud Run Service
# -------------------------------------------------------------------------

resource "google_cloud_run_service" "cloud_run_app" {
  name     = var.service_name_kebab_case
  project  = var.project_id
  location = var.region

  depends_on = [
    google_project_service.enable_cloud_run,
    google_firestore_database.database
  ]

  template {
    spec {
      containers {
        image = var.image
        env {
          name  = "GCP_PROJECT"
          value = var.project_id
        }
        env {
          name  = "PIPELINE_BUCKET_NAME"
          value = var.pipeline_bucket_name
        }
        env {
          name  = "BACKUP_BUCKET_NAME"
          value = var.backup_bucket_name
        }
        env {
          name  = "SEARCH_SERVICE_URL"
          value = var.search_service_url
        }
        env {
          name  = "POSTGRES_INSTANCE"
          value = var.postgres_instance
        }
        env {
          name  = "POSTGRES_DB"
          value = var.postgres_db
        }
        env {
          name  = "POSTGRES_USER"
          value = var.postgres_user
        }
        env {
          name  = "POSTGRES_PASSWORD"
          value = var.postgres_password
        }
      }
      service_account_name = google_service_account.cloud_run_app_sa.email
      timeout_seconds      = 1800
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}

# Allow the book-agent service account to invoke the search service
resource "google_cloud_run_service_iam_member" "book_agent_search_invoker" {
  project  = var.project_id
  location = var.region
  service  = "search-v1"
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_service_account.cloud_run_app_sa.email}"
}

# Allow specific developers to test the book-agent service directly
resource "google_cloud_run_service_iam_member" "developer_access" {
  project  = var.project_id
  location = var.region
  service  = google_cloud_run_service.cloud_run_app.name
  role     = "roles/run.invoker"
  member   = "user:sylvester@nilor.cool"
}