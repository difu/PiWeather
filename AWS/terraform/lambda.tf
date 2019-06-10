resource "aws_lambda_layer_version" "gdal_layer" {
  s3_bucket = "${aws_s3_bucket.internal_piweather_bucket.bucket}"
  s3_key    = "lambda/lambda_jinja2layer.zip"
  layer_name = "jinja2-layer"

  compatible_runtimes = ["python3.6"]
}