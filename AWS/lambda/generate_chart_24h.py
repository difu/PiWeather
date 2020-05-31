import sys

sys.path.append("/opt/")
import boto3
from boto3.dynamodb.conditions import Key
import io
import json

import dateutil.parser
import datetime

import matplotlib.pyplot as plt
import matplotlib.dates as mdates


def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb', region_name='eu-central-1')
    table = dynamodb.Table('WeatherData')

    the_sensors = {'Sensor/lacrosse/44/T', 'Sensor/lacrosse/44/RH'}

    timestamp_one_day_ago = datetime.datetime.now().replace(microsecond=0) - datetime.timedelta(hours=24)
    print(timestamp_one_day_ago.strftime("%Y-%m-%dT%H:%M:%S"))

    values_temp = []
    values_rh = []
    tss_temperature = []
    tss_humidity = []

    color_t = 'tab:red'
    color_rh = 'tab:blue'

    response_temperature = table.query(
        KeyConditionExpression=Key('Sensor').eq('Sensor/lacrosse/44/T') & Key('Timestamp').gte(
            timestamp_one_day_ago.strftime("%Y-%m-%dT%H:%M:%S"))
    )

    for i in response_temperature['Items']:
        # print("Count %s  Bla %s", str(count), i['payload'])
        value = i['payload']['value'][0]
        values_temp.append(value)
        ts = dateutil.parser.isoparse(i['Timestamp'])
        tss_temperature.append(ts)

    response_rh = table.query(
        KeyConditionExpression=Key('Sensor').eq('Sensor/lacrosse/44/RH') & Key('Timestamp').gte(
            timestamp_one_day_ago.strftime("%Y-%m-%dT%H:%M:%S"))
    )

    for i in response_rh['Items']:
        value = i['payload']['value'][0]
        values_rh.append(value)
        ts = dateutil.parser.isoparse(i['Timestamp'])
        tss_humidity.append(ts)

    fig, ax = plt.subplots()  # Create a figure containing a single axes.

    locator = mdates.AutoDateLocator(minticks=3, maxticks=3)
    formatter = mdates.ConciseDateFormatter(locator)
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)

    ax.set(xlabel="Date",
           title="Temperature, humidity of last 24h")

    ax.set_ylabel('Temp', color=color_t)

    ax.plot(tss_temperature, values_temp, color=color_t)

    ax2 = ax.twinx()
    ax2.xaxis.set_major_locator(locator)
    ax2.xaxis.set_major_formatter(formatter)
    ax2.set_ylabel('Humidity', color=color_rh)
    ax2.plot(tss_humidity, values_rh, color=color_rh)
    plt.setp(ax2.get_xticklabels(), visible=False)

    img_data = io.BytesIO()
    plt.savefig(img_data, format='png')
    img_data.seek(0)

    s3 = boto3.resource('s3')
    bucket = s3.Bucket('dfux.me')
    bucket.put_object(Body=img_data, ContentType='image/png', Key='weather/last24h.png')

    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }


if __name__ == '__main__':
    lambda_handler('', '')
