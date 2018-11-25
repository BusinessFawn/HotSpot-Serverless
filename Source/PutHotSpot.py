import datetime
import os
from decimal import Decimal

import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.getenv('TABLE_NAME'))


def put_hot_spot_handler(event, context):
    print('starting to read.. event: {}'.format(event))
    updated_existing_item = False
    if event.get('locationID', ''):
        print('found locationID: {}'.format(event.get('locationID')))
        updated_existing_item = update_existing_item(event)

    if not updated_existing_item:
        print('item not updatedable, moving on with new locationID')
        event['locationID'] = context.aws_request_id
    return put_new_location(event)


def update_existing_item(input_dict: dict):
    lat, lng, location_id, input_hash, date_time, color_code, key = unpack_values(input_dict)

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
        return False
    print('found Items...')
    old_date_time = query_response['Items'][0]['date_time']
    del_response = table.delete_item(Key={'lat_lng': key, 'date_time': old_date_time})
    print('del response: {}'.format(del_response))
    return True


def put_new_location(input_dict: dict):
    lat, lng, location_id, input_hash, date_time, color_code, key = unpack_values(input_dict)
    response = ''
    try:
        new_put_item = {
            'lat_lng': key,
            'lat': lat,
            'lng': lng,
            'date_time': "{}".format(date_time),
            'locationID': location_id,
            'colorCode': color_code
        }
        if input_hash:
            new_put_item['hash'] = input_hash
        response = table.put_item(
            Item=new_put_item
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


def unpack_values(input_dict: dict) -> tuple:
    print('event: {}'.format(input_dict))
    lat = Decimal(str(input_dict.get('lat', 35.7721)))
    lng = Decimal(str(input_dict.get('lng', -78.6441)))
    location_id = str(input_dict.get('locationID', ''))
    input_hash = str(input_dict.get('hash', ''))
    print("lat, lng: {} {}".format(lat, lng))
    date_time = datetime.datetime.now()
    color_code = input_dict.get('colorCode', 1)

    key = '{:.1f}_{:.1f}'.format(lat, lng)
    print('key: {}'.format(key))

    return lat, lng, location_id, input_hash, date_time, color_code, key


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
    test_context = Context()
    print(put_hot_spot_handler(event_dict, test_context))
