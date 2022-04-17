variable "gcp_credentials" {
  type        = string
  sensitive   = true
  description = "Google Cloud service account credentials"
}

variable "project_id" {
  description = "Project id"
}

variable "region" {
  description = "Region"
}

variable "zone" {
  description = "Zone"
}

variable "machine_type" {
  type        = string
  description = "Type of the node compute engines."
}

variable "disk_size_gb" {
  type        = number
  description = "Size of the node's disk."
}

variable "disk_type" {
  type        = string
  description = "Type of the node's disk."
}

variable "cluster_version" {
  default = "1.20"
}
