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
        print(date_only)

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

        print("Count:")
        print(count)
        print("Max")
        max_value = max(values)
        print(max_value)
        print(max_ts)

        print("Min")
        min_value = min(values)
        print(min_value)
        print(min_ts)

        print("median")
        median_value = statistics.median(values)
        print(median_value)
        print("mean")
        mean_value = statistics.mean(values)
        print(mean_value)

        # response = table.update_item(
        #
        #     ReturnValues="UPDATED_NEW"
        # )
        # print(response)


if __name__ == "__main__":
    # lambda_handler('','')
    generate_daily_stats('Sensor/lacrosse/44/T', '2020-05-31T', 1)
