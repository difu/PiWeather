# PiWeather

Collect and publish weather data with Raspberry Py and AWS IOT

## Raspberry

The scripts are all developed and tested with Python 3.5.

The data should be saved with an UTC timestamp, so set the timezone on the Raspberry

```
sudo timedatectl set-timezone UTC
```

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

### DynamoDB

#### Logs

Following log entries are supported:

For station events
```
Log/System
```

for example
```json
{
  "payload": "Switched Raspberry to UTC",
  "Sensor": "Log/System",
  "Timestamp": "2020-04-25T20:37:53"
}
```

For system events
```
Log/System
```

For weather events
```
Log/Weather
```
