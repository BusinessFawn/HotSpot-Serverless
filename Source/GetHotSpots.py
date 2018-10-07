import datetime
import os
from decimal import Decimal

import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError


def lambda_handler(event, context):
    print('event: {}'.format(event))
    present = datetime.datetime.now()
    two_hours_less = datetime.timedelta(hours=2)

    minus_two = present - two_hours_less

    print('present: {}'.format(present))
    oldest_record = "{}".format(minus_two)
    print("oldest_record: {}".format(oldest_record))
    lat = event['event'].get('lat')

    return_dict = {
        "locations": [
            {
                "lat": 35.772,
                "lng": -78.6441,
                "locationID": 13,
                "colorCode": 8,
                "hash": "My first hash..."
            },
            {
                "lat": 35.778,
                "lng": -78.645,
                "locationID": 12,
                "colorCode": 6,
                "hash": "A better hash..."
            },
            {
                "lat": 35.779,
                "lng": -78.6449,
                "locationID": 123,
                "colorCode": 5,
                "hash": "Last hash."
            }
        ]
    }
    if lat:
        dynamodb = boto3.resource("dynamodb")

        table = dynamodb.Table(os.getenv('TABLE_NAME'))
        lat = event['event'].get('lat', 35.7721)
        lat = Decimal('{:.1f}'.format(lat))
        lng = event['event'].get('lng', -78.6441)
        lng = Decimal('{:.1f}'.format(lng))
        view_range = event['event'].get('range', 0)
        print('lat: {}, lng: {}'.format(lat, lng))
        lat_lng_key = Key('lat_lng').eq('{}_{}'.format(lat, lng))
        date_key = Key('date_time').gt(oldest_record)
        print('key: {}_{}'.format(lat, lng))
        response = {"Items": []}

        try:
            # if view_range:
            floor = view_range
            outter = 0 - view_range
            print('floor: {}'.format(floor))
            while outter in range(floor, view_range + 1):
                print('Outter {}: '.format(outter))
                query_lng = lng + Decimal(outter * Decimal('.1'))
                print("lng: {}".format(query_lng))
                inner = 0 - view_range

                while inner in range(floor, view_range + 1):
                    print("inner: {}".format(inner))
                    print("lat: {}".format(lat))
                    query_lat = lat + Decimal(inner * Decimal('.1'))
                    print('lat_lng: {}_{}'.format(query_lat, query_lng))
                    lat_lng_key = Key('lat_lng').eq('{}_{}'.format(query_lat, query_lng))
                    response['Items'] += table.query(
                        KeyConditionExpression=lat_lng_key & date_key
                    )["Items"]
                    print('items: {}'.format(response))
                    inner += 1
                outter += 1
        except ClientError as e:
            print(e.response['Error']['Message'])
        else:
            items = response['Items']
            if items:
                return_dict['locations'] = items
    else:
        print('no item....')
    return return_dict


if __name__ == "__main__":

    os.environ['TABLE_NAME'] = "HotSpotAlpha"

    event_dict = {
        "event": {
            'lat': 123.2,
            'lng': 321.1
        }
    }
    context = {}
    print(lambda_handler(event_dict, context))