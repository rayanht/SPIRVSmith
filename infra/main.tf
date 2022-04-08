terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "4.16.0"
    }
  }
}

provider "google" {
  credentials = var.gcp_credentials

  project = var.project_id
  region  = var.region
  zone    = var.zone
}

provider "google-beta" {
  credentials = var.gcp_credentials

  project = var.project_id
  region  = var.region
  zone    = var.zone
}


resource "google_service_account" "default" {
  account_id   = "spirv-default"
  display_name = "SPIRVSmith Service Account"
}

resource "google_compute_network" "default_network" {
  name = "spirvsmith-primary-network"
}

resource "google_artifact_registry_repository" "spirvsmith_repo" {
  provider = google-beta

  location      = var.region
  repository_id = "spirvsmith-docker-images"
  description   = "Docker repo for SPIRVSmith images"
  format        = "DOCKER"
}

resource "google_compute_instance" "spirvsmith_primary" {
  name         = "spirvsmith-primary"
  description  = "SPIRVSmith generating node"
  machine_type = var.machine_type

  boot_disk {
    initialize_params {
      image = "cos-cloud/cos-stable"
    }
  }

  metadata = {
    gce-container-declaration = <<EOT
spec:
  containers:
    - image: python:3.10-slim
      name: containervm
      securityContext:
        privileged: false
      stdin: false
      tty: false
      volumeMounts: []
      restartPolicy: Always
      volumes: []
EOT
    google-logging-enabled    = "true"
  }
  network_interface {
    network = google_compute_network.default_network.name
  }
}

resource "google_bigquery_dataset" "spirv_dataset" {
  dataset_id                  = "spirv"
  friendly_name               = "Shaders metadata"
  location                    = "US"
  default_table_expiration_ms = 3600000
}

resource "google_bigquery_table" "spirv_metadata_table" {
  dataset_id          = google_bigquery_dataset.spirv_dataset.dataset_id
  table_id            = "metadata"
  deletion_protection = false # Schema is subject to change for now

  schema = <<EOF
[
  {
    "name": "shader_id",
    "type": "STRING",
    "mode": "REQUIRED",
    "description": "Shader identifier. Not a primary key."
  },
  {
    "name": "expected_reports",
    "type": "INT64",
    "mode": "REQUIRED",
    "description": "Number of reports to be expected by the aggregator node before checking for a mismatch."
  },
  {
    "name": "buffer_dump",
    "type": "STRING",
    "mode": "NULLABLE",
    "description": "A single reported buffer dump. Initially NULL."
  },
  {
    "name": "platform_os",
    "type": "STRING",
    "mode": "NULLABLE",
    "description": "One of Linux or MacOS"
  },
  {
    "name": "platform_hardware_type",
    "type": "STRING",
    "mode": "NULLABLE",
    "description": "One of Intel CPU/AMD CPU/Nvidia GPU/Radeon GPU"
  },
  {
    "name": "platform_hardware_info",
    "type": "STRING",
    "mode": "NULLABLE",
    "description": "Detailed hardware report (i.e. driver version, hardware model etc...)"
  },
  {
    "name": "platform_backend",
    "type": "STRING",
    "mode": "NULLABLE",
    "description": "e.g. Vulkan or SwiftShader"
  }
]
EOF

}
resource "google_pubsub_schema" "spirv_shader_pubsub_schema" {
  name       = "spirv_shader_pubsub_schema"
  type       = "PROTOCOL_BUFFER"
  definition = "syntax = \"proto3\";\nmessage ShaderGenerated {\nstring shader_id = 1;\n}"
}

resource "google_pubsub_topic" "spirv_shader_pubsub_topic" {
  name = "spirv_shader_pubsub_topic"

  depends_on = [google_pubsub_schema.spirv_shader_pubsub_schema]
  schema_settings {
    schema   = "projects/spirvsmith/schemas/spirv_shader_pubsub_schema"
    encoding = "JSON"
  }
}

resource "google_pubsub_subscription" "example" {
  name  = "spirv_shader_pubsub_subscription"
  topic = google_pubsub_topic.spirv_shader_pubsub_topic.name

  # 20 minutes
  message_retention_duration = "1200s"
  retain_acked_messages      = true

  ack_deadline_seconds = 20

  expiration_policy {
    ttl = "300000.5s"
  }

  retry_policy {
    minimum_backoff = "10s"
  }

  enable_message_ordering = false
}
