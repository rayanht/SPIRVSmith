terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "3.5.0"
    }
  }
}

provider "google" {
  credentials = file("spirvsmith_gcp.json")

  project = var.project_id
  region  = var.region
  zone = var.zone
}

provider "google-beta" {
  credentials = "${file("spirvsmith_gcp.json")}"

  project = var.project_id
  region  = var.region
  zone = var.zone
}


resource "google_service_account" "default" {
  account_id   = "service-account-id"
  display_name = "SPIRVSmith Service Account"
}

resource "google_artifact_registry_repository" "spirvsmith-repo" {
  provider = google-beta

  repository_id = "spirvsmith-images"
  description = "Docker repo for SPIRVSmith images"
  format = "DOCKER"
}

resource "google_compute_network" "vpc" {
  name                    = "spirvsmith-vpc"
  auto_create_subnetworks = "false"
}

resource "google_compute_subnetwork" "spirvsmith-network" {
  name          = "spirvsmith-network"
  network       = google_compute_network.vpc.name
  ip_cidr_range = "10.10.10.0/24"
}

resource "google_container_cluster" "primary" {
  name     = "spirvsmith-cluster"

  min_master_version       = var.cluster_version
  remove_default_node_pool = true
  initial_node_count       = 1

  network    = google_compute_network.vpc.name
  subnetwork = "spirvsmith-network"
}

resource "google_container_node_pool" "primary_nodes" {
  name       = "${google_container_cluster.primary.name}-node-pool"
  cluster    = google_container_cluster.primary.name
  node_count = var.gke_num_nodes
  version    = var.cluster_version

  management {
    auto_repair  = "true"
    auto_upgrade = "true"
  }

  node_config {
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform",
    ]

    labels = {
      env = var.project_id
    }

    service_account = google_service_account.default.email
    image_type      = "COS"
    machine_type    = var.machine_type
    disk_size_gb    = var.disk_size_gb
    disk_type       = var.disk_type
    preemptible     = false
    tags         = [
      "gke-node",
    ]

    metadata = {
      disable-legacy-endpoints = "true"
    }
  }
}