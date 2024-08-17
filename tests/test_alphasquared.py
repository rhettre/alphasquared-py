import unittest
from unittest.mock import patch, Mock
import json
import logging
from alphasquared.alphasquared import AlphaSquared

class TestAlphaSquared(unittest.TestCase):
    def setUp(self):
        self.api = AlphaSquared("test_token")
        # Disable logging for tests
        logging.disable(logging.CRITICAL)

    def tearDown(self):
        # Re-enable logging after tests
        logging.disable(logging.NOTSET)

    @patch('alphasquared.alphasquared.requests.get')
    def test_get_asset_info_success(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"symbol": "BTC", "price": "50000"}
        mock_get.return_value = mock_response

        result = self.api.get_asset_info("BTC")
        self.assertEqual(result, {"symbol": "BTC", "price": "50000"})

    @patch('alphasquared.alphasquared.requests.get')
    def test_get_asset_info_failure(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = json.dumps({"code": "not_found", "message": "Asset not found"})
        mock_get.return_value = mock_response

        result = self.api.get_asset_info("INVALID")
        self.assertIn("error", result)
        self.assertIn("Asset not found", result["error"])

    @patch('alphasquared.alphasquared.requests.get')
    def test_get_strategy_values_success(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"strategy_name": "Test Strategy", "values": [1, 2, 3]}
        mock_get.return_value = mock_response

        result = self.api.get_strategy_values("Test Strategy")
        self.assertEqual(result, {"strategy_name": "Test Strategy", "values": [1, 2, 3]})

    @patch('alphasquared.alphasquared.requests.get')
    def test_get_strategy_values_failure(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = json.dumps({"code": "not_found", "message": "Strategy not found"})
        mock_get.return_value = mock_response

        result = self.api.get_strategy_values("Invalid Strategy")
        self.assertIn("error", result)
        self.assertIn("Strategy not found", result["error"])

    @patch('alphasquared.alphasquared.requests.get')
    def test_get_hypotheticals_success(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"asset": "BTC", "hypotheticals": [{"price": "50000", "risk": "0.5"}]}
        mock_get.return_value = mock_response

        result = self.api.get_hypotheticals("BTC")
        self.assertEqual(result, {"asset": "BTC", "hypotheticals": [{"price": "50000", "risk": "0.5"}]})

    @patch('alphasquared.alphasquared.requests.get')
    def test_get_hypotheticals_failure(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = json.dumps({"code": "not_found", "message": "Asset not found"})
        mock_get.return_value = mock_response

        result = self.api.get_hypotheticals("INVALID")
        self.assertIn("error", result)
        self.assertIn("Invalid asset", result["error"])

    def test_has_error(self):
        self.assertTrue(AlphaSquared.has_error({"error": "Test error"}))
        self.assertFalse(AlphaSquared.has_error({"data": "No error"}))

    def test_get_api_error(self):
        error_result = {"error": "Test error", "api_error": {"message": "API error", "details": {"code": 404}}}
        self.assertEqual(AlphaSquared.get_api_error(error_result), {"message": "API error", "details": {"code": 404}})
        self.assertEqual(AlphaSquared.get_api_error({"data": "No error"}), {})

    def test_rate_limiting(self):
        self.assertTrue(hasattr(self.api, '_check_rate_limit'))

if __name__ == '__main__':
    unittest.main()