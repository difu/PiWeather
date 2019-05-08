# PiWeather

Collect and publish weather data with Raspberry Py and AWS IOT

## Raspberry

The scripts are all developed and tested with Python 3.5.

### publishLacross.py

Create ```config.ini``` from ```config.ini.example``` and edit your endpoint etc.


## AWS

Create a policy for the Raspberry, e.g. RaspberryPolicy

```
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "iot:Connect",
        "iot:Publish"
      ],
      "Resource": "*"
    }
  ]
}
```

Import your RaspberryPi:

```
terraform import aws_iot_thing.raspi Raspberry
```