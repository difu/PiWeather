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

# Begin render_actual_values_page

resource "aws_cloudwatch_event_target" "render_actual_values_page" {
    rule = aws_cloudwatch_event_rule.actual_weather_page_generation.name
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

# END render_actual_values_page

resource "aws_cloudwatch_event_target" "render_24h_values_page" {
    rule = aws_cloudwatch_event_rule.actual_24h_chart_generation.name
    arn = aws_lambda_function.generate_chart_24h.arn
}

resource "aws_lambda_permission" "allow_cloudwatch_to_call_render_24h_values_page" {
    statement_id = "AllowExecutionFromCloudWatch"
    action = "lambda:InvokeFunction"
    function_name = aws_lambda_function.generate_chart_24h.function_name
    principal = "events.amazonaws.com"
    source_arn = aws_cloudwatch_event_rule.actual_24h_chart_generation.arn
}

resource "aws_lambda_function" "generate_chart_24h" {
  filename = data.archive_file.generate_chart_24h_zip.output_path
  function_name = "generate_chart_24h"
  role = aws_iam_role.generate_chart_24h_policy_role.arn
  handler = "generate_chart_24h.lambda_handler"
  timeout = 10
  runtime = "python3.6"
  layers = [
    aws_lambda_layer_version.matplotlib_layer.id
  ]
  source_code_hash = base64sha256(file("../lambda/generate_chart_24h.py"))
}

data "archive_file" "generate_chart_24h_zip" {
  type = "zip"
  source_file = "../lambda/generate_chart_24h.py"
  output_path = "generate_chart_24h.zip"
}


resource "aws_iam_role" "generate_chart_24h_policy_role" {
  name = "generate_chart_24h_execution_role"
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

resource "aws_iam_role_policy_attachment" "generate_chart_24h_policy_attachment" {
  role      = aws_iam_role.generate_chart_24h_policy_role.name
  policy_arn = aws_iam_policy.generate_chart_24h_policy.arn
}

resource "aws_iam_policy" "generate_chart_24h_policy" {
  name        = "generate_chart_24h_policy"
  path        = "/lambda/"
  description = "What the 24h chart generator is allowed to to"

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
                "arn:aws:logs:eu-central-1:490111692662:log-group:/aws/lambda/chart24hgenerator:*"
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