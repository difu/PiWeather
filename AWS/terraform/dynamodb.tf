resource "aws_dynamodb_table" "weather_data_table" {
  name           = "WeatherData"
  billing_mode   = "PROVISIONED"
  read_capacity  = 1
  write_capacity = 20
  hash_key       = "Sensor"
  range_key      = "Timestamp"

  attribute {
    name = "Sensor"
    type = "S"
  }

  attribute {
    name = "Timestamp"
    type = "S"
  }

  tags = {
    Project        = "${var.project}"
  }
}