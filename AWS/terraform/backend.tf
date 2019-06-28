terraform {
  backend "s3" {
    bucket = "piweather"
    key = "terraform/terraformstate"
    region = "eu-central-1"
  }
}