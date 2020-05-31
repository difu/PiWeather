resource "aws_cloudwatch_event_rule" "actual_24h_chart_generation" {
  name                = "actual_chart_generation"
  description         = "Triggers actual 24h charts. Fires every 15 minutes"
  schedule_expression = "rate(15 minutes)"

  tags = {
    Project = var.project
  }
}

resource "aws_cloudwatch_event_rule" "actual_weather_page_generation" {
  name                = "actual_weather_page_generation"
  description         = "Triggers weather page rendering. Fires every ten minutes"
  schedule_expression = "rate(10 minutes)"

  tags = {
    Project = var.project
  }
}
