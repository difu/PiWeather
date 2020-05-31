import sys

sys.path.append("/opt/")
import boto3
from boto3.dynamodb.conditions import Key, Attr
import json

import datetime
import dateutil.tz

dynamodb = boto3.resource('dynamodb', region_name='eu-central-1')
table = dynamodb.Table('WeatherData')


def generate_daily_stats(start_date, days, force=False):
    """

    :param start_date:
    :param days:
    :param force: if True the statistics will be re-calculated, if False existing values will not be changed
    :return:
    """

    dates = {}
    date_format = "%Y-%m-%dT"

    for i in range(days):
        the_date = datetime.datetime.strptime(start_date, date_format) + datetime.timedelta(days=i)
        print(the_date.strftime("%Y-%m-%dT"))

        response = table.query(
            KeyConditionExpression=Key('Sensor').eq('Sensor/lacrosse/44/T') & Key('Timestamp').begins_with(the_date.strftime("%Y-%m-%dT"))
        )
        count = 0
        values = []
        max_ts = ""
        min_ts = ""
        for i in response['Items']:
            # print("Count %s  Bla %s", str(count), i['payload'])
            value = i['payload']['value'][0]
            values.append(value)
            if value >= max(values):
                max_ts = i['Timestamp']
            if value <= min(values):
                min_ts = i['Timestamp']
            count = count + 1

        print("Count:")
        print(count)
        print("Max")
        print(max(values))
        print(max_ts)

        print("Min")
        print(min(values))
        print(min_ts)


if __name__ == "__main__":
    # lambda_handler('','')
    generate_daily_stats('2020-05-30T', 1)
