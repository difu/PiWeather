resource "aws_cloudwatch_event_rule" "actual_chart_generation" {
  name                = "actual_chart_generation"
  description         = "Triggers actual charts. Fires every five minutes"
  schedule_expression = "rate(5 minutes)"

  tags = {
    Project = "${var.project}"
  }
}
