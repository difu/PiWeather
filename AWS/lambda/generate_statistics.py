import sys

sys.path.append("/opt/")
import boto3
from boto3.dynamodb.conditions import Key, Attr
import json
import statistics
import datetime
import dateutil.tz

dynamodb = boto3.resource('dynamodb', region_name='eu-central-1')
table = dynamodb.Table('WeatherData')


def generate_daily_stats(sensor, start_date, days, force=False):
    """

    :param sensor: the sensor
    :param start_date: date in iso format
    :param days: number of days beginning from start_date
    :param force: if True the statistics will be re-calculated, if False existing values will not be changed
    :return:
    """

    dates = {}
    date_format = "%Y-%m-%dT"

    for i in range(days):
        the_date = datetime.datetime.strptime(start_date, date_format) + datetime.timedelta(days=i)
        date_only = the_date.strftime("%Y-%m-%dT")
        sensor_stats = sensor + "/daily_stats"

        response = table.query(
            KeyConditionExpression=Key('Sensor').eq(sensor_stats) & Key('Timestamp').eq(date_only)
        )

        if force is False and len(response["Items"]) > 0:
            return

        response = table.query(
            KeyConditionExpression=Key('Sensor').eq(sensor) & Key('Timestamp').begins_with(date_only)
        )
        count = 0
        values = []
        max_ts = ""
        min_ts = ""
        for item in response['Items']:
            # print("Count %s  Bla %s", str(count), i['payload'])
            value = item['payload']['value'][0]
            values.append(value)
            if value >= max(values):
                max_ts = item['Timestamp']
            if value <= min(values):
                min_ts = item['Timestamp']
            count = count + 1

        max_value = max(values)

        min_value = min(values)
        median_value = statistics.median(values)
        mean_value = statistics.mean(values)

        response = table.put_item(

            Item={
                'Sensor': sensor_stats,
                'Timestamp': date_only,
                'payload': {
                    'max': max_value,
                    'max_ts': max_ts,
                    'min': min_value,
                    'min_ts': min_ts,
                    'mean': mean_value,
                    'median': median_value
                }
            },
            ReturnValues="ALL_OLD"
        )
        # print(response)


if __name__ == "__main__":
    # lambda_handler('','')
    generate_daily_stats('Sensor/lacrosse/44/RH', '2020-05-31T', 1, False)
