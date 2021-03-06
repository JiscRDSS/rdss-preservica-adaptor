data "template_file" "init" {
  template = "${file("${path.module}/init.tpl")}"

  vars {
    environment   = "${terraform.workspace}"
    systemd_unit  = "${var.systemd_unit}"
    env_file_path = "${var.env_file_path}"
  }
}

data "template_cloudinit_config" "config" {
  gzip          = false
  base64_encode = false

  part {
    content_type = "text/x-shellscript"
    content      = "${data.template_file.init.rendered}"
  }
}

resource "aws_iam_instance_profile" "profile" {
  name = "${var.project}-${terraform.workspace}-profile"
  role = "${var.role_name}"
}

resource "aws_launch_configuration" "config" {
  image_id             = "${var.ami}"
  instance_type        = "${var.type}"
  key_name             = "${var.key_name}"
  security_groups      = ["${var.security_groups}"]
  user_data            = "${data.template_cloudinit_config.config.rendered}"
  iam_instance_profile = "${aws_iam_instance_profile.profile.id}"

  root_block_device {
    volume_type = "gp2"
    volume_size = "32"
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_autoscaling_group" "group" {
  availability_zones        = "${var.availability_zones}"
  name                      = "${var.project}-${terraform.workspace}-${aws_launch_configuration.config.name}-config"
  min_size                  = "${var.min_size}"
  max_size                  = "${var.max_size}"
  desired_capacity          = "${var.desired_capacity}"
  health_check_grace_period = "${var.health_check_grace_period}"
  health_check_type         = "${var.health_check_type}"
  force_delete              = "${var.force_delete}"
  launch_configuration      = "${aws_launch_configuration.config.name}"
  vpc_zone_identifier       = ["${var.vpc_zone_identifier}"]

  lifecycle {
    create_before_destroy = true
  }

  tag {
    key                 = "Name"
    value               = "${var.project}-${terraform.workspace}-node"
    propagate_at_launch = true
  }

  tag {
    key                 = "Environment"
    value               = "${terraform.workspace}"
    propagate_at_launch = true
  }

  tag {
    key                 = "Project"
    value               = "${var.project}"
    propagate_at_launch = true
  }

  tag {
    key                 = "Service"
    value               = "${var.service}"
    propagate_at_launch = true
  }

  tag {
    key                 = "CostCentre"
    value               = "${var.cost_centre}"
    propagate_at_launch = true
  }

  tag {
    key                 = "Owner"
    value               = "${var.owner}"
    propagate_at_launch = true
  }

  tag {
    key                 = "ManagedBy"
    value               = "Terraform"
    propagate_at_launch = true
  }
}
