resource "aws_iot_topic_rule" "lacrosse_rule" {
  name        = "${var.project}LacrosseRuleToDynamo"
  description = "ingest incoming lacrosse data into weather data table"
  enabled     = true
  sql         = "SELECT value FROM '${var.lacrosse_topic}'"

  sql_version = "2016-03-23"

  dynamodb {
    hash_key_field = "Sensor"
    hash_key_value = "$${Sensor}"
    range_key_field = "Timestamp"
    range_key_value = "$${Timestamp}"
    role_arn = "${aws_iam_role.iot.arn}"
    table_name = "${aws_dynamodb_table.weather_data_table.name}"
  }
}

resource "aws_iam_role" "iot" {
  name = "${var.project}-ToDynamo-iot-role"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "iot.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy" "iot_allow_dynamo_policy" {
  name = "${var.project}-iot-dynamo-policy"
  role = "${aws_iam_role.iot.id}"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:PutItem",
        "dynamodb:UpdateItem"
      ],
      "Resource": [
        "${aws_dynamodb_table.weather_data_table.arn}"
      ]
    }
  ]
}
EOF
}