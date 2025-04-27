import json
import logging
import unittest
from unittest.mock import patch, MagicMock

from alphasquared import AlphaSquared, AlphaSquaredAPIException


class TestAlphaSquared(unittest.TestCase):
    def setUp(self):
        # Store the original logger level
        self.original_level = logging.getLogger("alphasquared.alphasquared").getEffectiveLevel()
        # Disable logging during tests
        logging.getLogger("alphasquared.alphasquared").setLevel(logging.CRITICAL)
        self.api = AlphaSquared(api_token="test_token", debug=False)

    def tearDown(self):
        # Restore the original logger level
        logging.getLogger("alphasquared.alphasquared").setLevel(self.original_level)

    @patch("requests.get")
    def test_get_asset_info_success(self, mock_get):
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"name": "Bitcoin", "symbol": "BTC"}
        mock_get.return_value = mock_response

        result = self.api.get_asset_info("BTC")
        self.assertEqual(result, {"name": "Bitcoin", "symbol": "BTC"})

    @patch("requests.get")
    def test_get_asset_info_error(self, mock_get):
        # Mock error response
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = json.dumps({"error": "Unauthorized"})
        mock_response.json.return_value = {"error": "Unauthorized"}
        mock_get.return_value = mock_response

        with patch.object(self.api, '_handle_api_exception') as mock_handle:
            mock_handle.return_value = {"error": "API error", "api_error": {"message": "Unauthorized"}}
            result = self.api.get_asset_info("BTC")
            self.assertTrue("error" in result)
            self.assertTrue("api_error" in result)

    @patch("requests.get")
    def test_get_strategy_values_success(self, mock_get):
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "buy_values": {"risk_50": "100"},
            "sell_values": {"risk_50": "90"}
        }
        mock_get.return_value = mock_response

        result = self.api.get_strategy_values("test_strategy")
        self.assertEqual(result["buy_values"], {"risk_50": "100"})
        self.assertEqual(result["sell_values"], {"risk_50": "90"})

    @patch("requests.get")
    def test_get_strategy_values_error(self, mock_get):
        # Mock error response
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = json.dumps({"error": "Strategy not found"})
        mock_response.json.return_value = {"error": "Strategy not found"}
        mock_get.return_value = mock_response

        with patch.object(self.api, '_handle_api_exception') as mock_handle:
            mock_handle.return_value = {"error": "API error", "api_error": {"message": "Strategy not found"}}
            result = self.api.get_strategy_values("nonexistent_strategy")
            self.assertTrue("error" in result)
            self.assertTrue("api_error" in result)

    @patch("requests.get")
    def test_get_hypotheticals_success(self, mock_get):
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"hypotheticals": [{"value": 100}]}
        mock_get.return_value = mock_response

        result = self.api.get_hypotheticals("BTC")
        self.assertEqual(result, {"hypotheticals": [{"value": 100}]})

    @patch("requests.get")
    def test_get_hypotheticals_error(self, mock_get):
        # Mock error response
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = json.dumps({"error": "Invalid asset"})
        mock_response.json.return_value = {"error": "Invalid asset"}
        mock_get.return_value = mock_response

        with patch.object(self.api, '_handle_api_exception') as mock_handle:
            mock_handle.return_value = {"error": "API error", "api_error": {"message": "Invalid asset"}}
            result = self.api.get_hypotheticals("INVALID")
            self.assertTrue("error" in result)
            self.assertTrue("api_error" in result)

    @patch("requests.get")
    def test_get_current_risk_success(self, mock_get):
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"current_risk": 75.5}
        mock_get.return_value = mock_response

        result = self.api.get_current_risk("BTC")
        self.assertEqual(result, 75.5)

    @patch("requests.get")
    def test_get_current_risk_error(self, mock_get):
        # Mock error response
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = json.dumps({"error": "Internal server error"})
        mock_response.json.return_value = {"error": "Internal server error"}
        mock_get.return_value = mock_response

        with patch.object(self.api, '_handle_api_exception') as mock_handle:
            mock_handle.return_value = {"error": "API error", "api_error": {"message": "Internal server error"}}
            result = self.api.get_current_risk("BTC")
            self.assertEqual(result, 0.0)

    @patch("requests.get")
    def test_get_strategy_value_for_risk_success(self, mock_get):
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "buy_values": {"risk_50": "100", "risk_75": "150"},
            "sell_values": {"risk_50": "90", "risk_75": "140"}
        }
        mock_get.return_value = mock_response

        action, value = self.api.get_strategy_value_for_risk("test_strategy", 60)
        self.assertEqual(action, "buy")
        self.assertEqual(value, 100.0)

    @patch("requests.get")
    def test_get_strategy_value_for_risk_error(self, mock_get):
        # Mock error response
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = json.dumps({"error": "Strategy not found"})
        mock_response.json.return_value = {"error": "Strategy not found"}
        mock_get.return_value = mock_response

        with patch.object(self.api, '_handle_api_exception') as mock_handle:
            mock_handle.return_value = {"error": "API error", "api_error": {"message": "Strategy not found"}}
            action, value = self.api.get_strategy_value_for_risk("nonexistent_strategy", 50)
            self.assertEqual(action, "buy")
            self.assertEqual(value, 0.0)

    def test_has_error(self):
        self.assertTrue(AlphaSquared.has_error({"error": "Test error"}))
        self.assertFalse(AlphaSquared.has_error({"data": "Test data"}))

    def test_get_api_error(self):
        error = {"message": "Test error", "details": {"code": 500}}
        result = {"api_error": error}
        self.assertEqual(AlphaSquared.get_api_error(result), error)
        self.assertEqual(AlphaSquared.get_api_error({}), {})


if __name__ == "__main__":
    unittest.main() 