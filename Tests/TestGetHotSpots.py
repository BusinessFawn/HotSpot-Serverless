import json
import unittest
from unittest.mock import patch

from GetHotSpots import get_hot_spots_handler


class TestGetHotSpots(unittest.TestCase):

    @patch.dict({"TABLE": "TEST"})
    def setUp(self):
        pass

    @patch('boto3.resource')
    def test_get_hot_spots_handler(self, dynamo_mock):
        json_str = ''
        with open('TestData/GetHotSpotsData.json', 'r') as f:
            for line in f:
                json_str += line
        full_json = json.loads(json_str)
        mock_dynamo_response = full_json['dynamo-response']
        expected_response = full_json['expected-response']
        input_dict = full_json['input-response']
        dynamo_mock.return_value.Table.return_value.query.return_value = mock_dynamo_response
        self.assertDictEqual(get_hot_spots_handler(input_dict, {}), expected_response)


if __name__ == '__main__':
    unittest.main()
