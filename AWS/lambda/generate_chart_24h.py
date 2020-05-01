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

    response = table.query(
        KeyConditionExpression=Key('Sensor').eq('Sensor/lacrosse/44/T') & Key('Timestamp').gte(
            timestamp_one_day_ago.strftime("%Y-%m-%dT%H:%M:%S"))
    )

    values = []
    tss = []

    for i in response['Items']:
        # print("Count %s  Bla %s", str(count), i['payload'])
        value = i['payload']['value'][0]
        values.append(value)
        ts = dateutil.parser.isoparse(i['Timestamp'])
        tss.append(ts)

    fig, ax = plt.subplots()  # Create a figure containing a single axes.

    locator = mdates.AutoDateLocator(minticks=3, maxticks=5)
    formatter = mdates.ConciseDateFormatter(locator)
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)

    ax.set(xlabel="Date",
           ylabel="Temperature",
           title="Temp of last 24h")

    ax.plot(tss, values)  # Plot some data on the axes.

    img_data = io.BytesIO()
    plt.savefig(img_data, format='png')
    img_data.seek(0)

    s3 = boto3.resource('s3')
    bucket = s3.Bucket('internal.dfux.me')
    bucket.put_object(Body=img_data, ContentType='image/png', Key='myPic.png')

    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }


if __name__ == '__main__':
    lambda_handler('', '')
