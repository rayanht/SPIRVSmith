terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "3.5.0"
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
  name = "spirvsmith-network"
}

resource "google_artifact_registry_repository" "spirvsmith_repo" {
  provider = google-beta

  location      = var.region
  repository_id = "spirvsmith-images"
  description   = "Docker repo for SPIRVSmith images"
  format        = "DOCKER"
}

resource "google_compute_instance" "spirvsmith_primary" {
  name                      = "spirvsmith-primary"
  description               = "SPIRVSmith generating node"
  machine_type              = var.machine_type

  boot_disk {
    initialize_params {
      image = "cos-cloud/cos-stable"
    }
  }

  network_interface {
    network = google_compute_network.default_network.name
  }
}