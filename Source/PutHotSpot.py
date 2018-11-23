import datetime
import os
from decimal import Decimal

import boto3
from botocore.exceptions import ClientError


def put_hot_spot_handler(event, context):
    print('event: {}'.format(event))
    dynamodb = boto3.resource("dynamodb")

    table = dynamodb.Table(os.getenv('TABLE_NAME'))
    lat = Decimal(str(event.get('lat', 35.7721)))
    lng = Decimal(str(event.get('lng', -78.6441)))
    location_id = str(event.get('locationID', ''))
    input_hash = str(event.get('hash', 'no hash'))
    print("lat, lng: {} {}".format(lat, lng))
    date_time = datetime.datetime.now()
    color_code = event.get('colorCode', '1')

    key = '{:.1f}_{:.1f}'.format(lat, lng)
    print('key: {}'.format(key))
    response = {}

    if location_id:
        print('looking for a location: {}'.format(location_id))
        two_hours_less = datetime.timedelta(hours=2)
        minus_two = date_time - two_hours_less
        query_response = table.query(IndexName='locationID-date_time-index',
                                     KeyConditionExpression='locationID = :location_id and date_time > :date_time_value',
                                     FilterExpression='lat_lng = :lat_lng_value',
                                     ExpressionAttributeValues={
                                         ":location_id": location_id,
                                         ":date_time_value": '{}'.format(minus_two),
                                         ':lat_lng_value': key
                                     })
        print('response.... {}'.format(query_response))
        if not query_response['Items']:
            location_id = context.aws_request_id
    else:
        location_id = context.aws_request_id

    try:
        response = table.put_item(
            Item={
                'lat_lng': key,
                'lat': lat,
                'lng': lng,
                'date_time': "{}".format(date_time),
                'locationID': location_id,
                'hash': input_hash,
                'colorCode': color_code
            }
        )
        print("response: {}".format(response))
    except ClientError as e:
        print("error: {}".format(e.response['Error']['Message']))

    if response:
        return_dict = {
            "response": "success",
            "locationID": location_id
        }
    else:
        return_dict = {"message": "error"}

    print('return_dict: {}'.format(return_dict))
    return return_dict


if __name__ == '__main__':
    class Context:
        def __init__(self):
            self.aws_request_id = '123123123123'


    os.environ['TABLE_NAME'] = "HotSpotDynamoDbTable-HotSpotTable-F6VB59AJ2YDK"

    event_dict = {
        'lat': 123.2,
        'lng': 321.1,
        'colorCode': 1,
        "locationID": '123123123123'

    }
    context = Context()
    print(put_hot_spot_handler(event_dict, context))
