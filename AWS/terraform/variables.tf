variable "aws_region" {
  description = "AWS region to launch servers."
  default     = "eu-central-1"
}

variable "project" {
  description = "The name of this project"
  default     = "PiWeather"
}

variable "lacrosse_topic" {
  description = "The name of the lacrosse topic where messages from lacrosse sensors are put in"
  default     = "/lacrosse"
}