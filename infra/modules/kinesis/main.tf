resource "aws_kinesis_stream" "stream" {
  name                = "${var.name}"
  shard_count         = "${var.shard_count}"
  retention_period    = "${var.retention_period}"
  shard_level_metrics = "${var.shard_level_metricsc}"

  tags {
    "Name"        = "${var.name}"
    "Environment" = "${terraform.env}"
    "Project"     = "${var.project}"
    "Service"     = "${var.service}"
    "CostCentre"  = "${var.cost_centre}"
    "Owner"       = "${var.owner}"
    "ManagedBy"   = "Terraform"
  }
}
