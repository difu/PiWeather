import sys
sys.path.append("/opt/")
import boto3
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
from datetime import datetime, timezone
from jinja2 import Template, TemplateNotFound, Environment, meta
import json

dynamodb = boto3.resource('dynamodb', region_name='eu-central-1')
table = dynamodb.Table('WeatherData')

s3_client = boto3.client('s3')

# ssm_client = boto3.client('ssm', region_name='eu-central-1')

the_sensors = {'Sensor/lacrosse/c0/T', 'Sensor/lacrosse/44/T', 'Sensor/lacrosse/44/RH'}


def get_value_keys_from_template(template):
    env = Environment()
    ast = env.parse(template)
    # print(meta.find_undeclared_variables(ast))
    return ast


def get_source(bucket, template):
    try:
        resp = s3_client.get_object(Bucket=bucket, Key=template)
    except ClientError as e:
        if "NoSuchKey" in e.__str__():
            raise TemplateNotFound(template)
        else:
            raise e
    body = resp['Body'].read()
    return body.decode('utf-8')


def get_latest_sensor_timestamp_and_value(sensor):
    response = table.query(
        KeyConditionExpression=Key('Sensor').eq(sensor),
        ScanIndexForward=False,
        Limit=1
    )
    if len(response['Items']) == 1:
        # print(response)
        value = response['Items'][0]['payload']['value'][0]
        date = response['Items'][0]['Timestamp']
        return {'Timestamp': date, 'Value': value}
    else:
        raise Exception('No or more than one results returned.')


def create_page_context():
    context = {}
    for sensor in the_sensors:

        key = sensor.replace('/', '_') + '_latest'
        context[key] = get_latest_sensor_timestamp_and_value(sensor)['Value']

        key = sensor.replace('/', '_') + '_latest_timestamp'
        context[key] = get_latest_sensor_timestamp_and_value(sensor)['Timestamp']

    context['page_last_rendered_timestamp'] = datetime.now()
    return context


def lambda_handler(event, context):
    main_template_src = get_source("internal.dfux.me", 'templates/weather/index.html')
#    print(main_template_src)
    get_value_keys_from_template(main_template_src)

    main_template = Template(main_template_src)

    page_context = create_page_context()
#    print(page_context)
    main_template_out = main_template.render(page_context) + '\r\n'
#    print(main_template_out)

    s3_client.put_object(Bucket='dfux.me', Key='weather/index.html', Body=main_template_out, ContentType='text/html')

    return {
        'statusCode': 200,
        'body': {}
    }


if __name__ == '__main__':
    lambda_handler('', '')
