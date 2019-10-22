import unittest
from decimal import Decimal
from unittest.mock import patch

from PutHotSpot import unpack_values


class TestGetHotSpots(unittest.TestCase):

    @patch.dict({"TABLE": "TEST"})
    def setUp(self):
        pass

    @patch('datetime.datetime')
    @patch('boto3.resource')
    def test_put_hot_spot(self, mock_resource, mock_datetime):
        # lat, lng, location_id, input_hash, date_time, color_code, key
        mock_datetime.now.return_value = '01-01-2019:20:18:00.000'
        lat = Decimal(str(35.7721))
        lng = Decimal(str(-78.6441))
        location_id = ''
        input_hash = ''
        date_time = '01-01-2019:20:18:00.000'
        color_code = 1
        key = '35.8_-78.6'
        results = unpack_values({})
        self.assertEqual(results, (lat, lng, location_id, input_hash, date_time, color_code, key))


if __name__ == '__main__':
    unittest.main()
