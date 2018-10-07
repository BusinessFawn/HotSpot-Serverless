import os
from datetime import datetime
from decimal import Decimal

import boto3
from botocore.exceptions import ClientError


def lambda_handler(event, context):
    print('event: {}'.format(event))
    dynamodb = boto3.resource("dynamodb")

    table = dynamodb.Table(os.getenv('TABLE_NAME'))
    lat = Decimal(str(event.get('lat', 35.7721)))
    lng = Decimal(str(event.get('lng', -78.6441)))
    id = context.aws_request_id
    hash = event.get('hash', 'no hash')
    print("lat, lng: {} {}".format(lat, lng))
    date_time = datetime.now()
    color_code = event.get('colorCode', '1')

    key = '{:.1f}_{:.1f}'.format(lat, lng)
    print('key: {}'.format(key))
    response = {}

    try:
        response = table.put_item(
            Item={
                'lat_lng': key,
                'lat': lat,
                'lng': lng,
                'date_time': "{}".format(date_time),
                'locationID': id,
                'hash': hash,
                'colorCode': color_code
            }
        )
        print("response: {}".format(response))
    except ClientError as e:
        print("error: {}".format(e.response['Error']['Message']))

    if response:
        return {
            "response": "success",
            "locationID": id
        }
    else:
        return {"message": "error"}


if __name__ == '__main__':
    class Context:
        def __init__(self):
            self.aws_request_id = '123'


    os.environ['TABLE_NAME'] = "HotSpotAlpha"

    event_dict = {
        'lat': 123.2,
        'lng': 321.1,
        'colorCode': 1

    }
    context = Context()
    print(lambda_handler(event_dict, context))
