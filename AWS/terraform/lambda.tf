resource "aws_lambda_layer_version" "jinja2_layer" {
  s3_bucket = aws_s3_bucket.internal_piweather_bucket.bucket
  s3_key    = "lambda/lambda_jinja2layer.zip"
  layer_name = "jinja2-layer"

  compatible_runtimes = ["python3.6"]
}

resource "aws_lambda_layer_version" "matplotlib_layer" {
  s3_bucket = aws_s3_bucket.internal_piweather_bucket.bucket
  s3_key    = "lambda/lambda_matplotlib_layer.zip"
  layer_name = "matplotlib-layer"

  compatible_runtimes = ["python3.6"]
}

resource "aws_cloudwatch_event_target" "check_foo_every_five_minutes" {
    rule = aws_cloudwatch_event_rule.actual_weather_page_generation.name
    target_id = "check_foo"
    arn = aws_lambda_function.render_actual_values_page.arn
}

resource "aws_lambda_permission" "allow_cloudwatch_to_call_render_actual_page_value" {
    statement_id = "AllowExecutionFromCloudWatch"
    action = "lambda:InvokeFunction"
    function_name = aws_lambda_function.render_actual_values_page.function_name
    principal = "events.amazonaws.com"
    source_arn = aws_cloudwatch_event_rule.actual_weather_page_generation.arn
}

resource "aws_lambda_function" "render_actual_values_page" {
  filename = data.archive_file.render_actual_values_page_zip.output_path
  function_name = "render_actual_values_page"
  role = aws_iam_role.render_actual_values_page_role.arn
  handler = "render_actual_values_page.lambda_handler"
  runtime = "python3.6"
  layers = [
    aws_lambda_layer_version.jinja2_layer.id
  ]
  source_code_hash = base64sha256(file("../lambda/render_actual_values_page.py"))
}

data "archive_file" "render_actual_values_page_zip" {
  type = "zip"
  source_file = "../lambda/render_actual_values_page.py"
  output_path = "render_actual_values_page.zip"
}

resource "aws_iam_role" "render_actual_values_page_role" {
  name = "lambda_execution_role"
  path = "/LAMBDA/"
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "render_actual_values_page_policy_attachment" {
  role      = aws_iam_role.render_actual_values_page_role.name
  policy_arn = aws_iam_policy.render_actual_values_page_policy.arn
}

resource "aws_iam_policy" "render_actual_values_page_policy" {
  name        = "render_actual_values_page_policy"
  path        = "/lambda/"
  description = "What the render actual page is allowed to to"

  policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:BatchGetItem",
                "dynamodb:ConditionCheckItem",
                "dynamodb:ListTagsOfResource",
                "dynamodb:Scan",
                "dynamodb:DescribeStream",
                "dynamodb:Query",
                "dynamodb:DescribeTimeToLive",
                "logs:PutLogEvents",
                "dynamodb:DescribeGlobalTableSettings",
                "logs:CreateLogStream",
                "dynamodb:DescribeTable",
                "dynamodb:DescribeGlobalTable",
                "dynamodb:GetShardIterator",
                "dynamodb:GetItem",
                "dynamodb:DescribeContinuousBackups",
                "dynamodb:DescribeBackup",
                "dynamodb:GetRecords"
            ],
            "Resource": [
                "arn:aws:dynamodb:*:*:table/*",
                "arn:aws:logs:eu-central-1:490111692662:log-group:/aws/lambda/testJinja2:*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:DescribeReservedCapacityOfferings",
                "dynamodb:ListGlobalTables",
                "dynamodb:ListTables",
                "dynamodb:DescribeReservedCapacity",
                "dynamodb:ListBackups",
                "dynamodb:DescribeLimits",
                "dynamodb:ListStreams"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": "logs:CreateLogGroup",
            "Resource": "arn:aws:logs:eu-central-1:490111692662:*"
        },
        {
            "Effect": "Allow",
            "Action": [
                      "s3:Get*",
                      "s3:List*",
                      "s3:Put*"
            ],
            "Resource": "arn:aws:s3:::*"
        }
    ]
}
    EOF
}