import unittest
from unittest.mock import patch, Mock
import json
import logging
from alphasquared.alphasquared import AlphaSquared
from time import sleep

class TestAlphaSquared(unittest.TestCase):
    def setUp(self):
        self.cache_ttl = 1  # 1 second for faster testing
        self.api = AlphaSquared("test_token", cache_ttl=self.cache_ttl)
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

    @patch('alphasquared.alphasquared.requests.get')
    def test_get_comprehensive_asset_data(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = [
            {"symbol": "BTC", "price": "50000", "current_risk": "40.5"},
            {"asset": "BTC", "hypotheticals": [{"price": "50000", "risk": "0.5"}]}
        ]
        mock_get.return_value = mock_response

        result = self.api.get_comprehensive_asset_data("BTC")
        self.assertEqual(result["asset_info"]["symbol"], "BTC")
        self.assertEqual(result["hypotheticals"]["asset"], "BTC")

    @patch('alphasquared.alphasquared.requests.get')
    def test_caching(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = [
            {"symbol": "BTC", "price": "50000", "current_risk": "40.5"},
            {"asset": "BTC", "hypotheticals": [{"price": "50000", "risk": "0.5"}]}
        ]
        mock_get.return_value = mock_response

        # First call
        self.api.get_comprehensive_asset_data("BTC")
        
        # Second call (should use cache)
        self.api.get_comprehensive_asset_data("BTC")
        
        # Assert that the API was only called once for each endpoint
        self.assertEqual(mock_get.call_count, 2)

    @patch('alphasquared.alphasquared.requests.get')
    def test_cache_expiration(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = [
            {"symbol": "BTC", "price": "50000", "current_risk": "40.5"},
            {"asset": "BTC", "hypotheticals": [{"price": "50000", "risk": "0.5"}]},
            {"symbol": "BTC", "price": "51000", "current_risk": "41.0"},
            {"asset": "BTC", "hypotheticals": [{"price": "51000", "risk": "0.6"}]}
        ]
        mock_get.return_value = mock_response

        # First call
        result1 = self.api.get_comprehensive_asset_data("BTC")
        
        # Wait for cache to expire
        sleep(self.cache_ttl + 0.1)
        
        # Second call (should not use cache)
        result2 = self.api.get_comprehensive_asset_data("BTC")
        
        self.assertNotEqual(result1["asset_info"]["price"], result2["asset_info"]["price"])
        self.assertEqual(mock_get.call_count, 4)

    @patch('alphasquared.alphasquared.requests.get')
    def test_force_refresh_asset_data(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = [
            {"symbol": "BTC", "price": "50000", "current_risk": "40.5"},
            {"asset": "BTC", "hypotheticals": [{"price": "50000", "risk": "0.5"}]},
            {"symbol": "BTC", "price": "51000", "current_risk": "41.0"},
            {"asset": "BTC", "hypotheticals": [{"price": "51000", "risk": "0.6"}]}
        ]
        mock_get.return_value = mock_response

        # First call
        result1 = self.api.get_comprehensive_asset_data("BTC")
        
        # Force refresh
        result2 = self.api.force_refresh_asset_data("BTC")
        
        self.assertNotEqual(result1["asset_info"]["price"], result2["asset_info"]["price"])
        self.assertEqual(mock_get.call_count, 4)

    def test_get_current_risk(self):
        self.api.get_asset_info = Mock(return_value={"current_risk": "42.5"})
        risk = self.api.get_current_risk("BTC")
        self.assertEqual(risk, 42.5)

    def test_get_strategy_value_for_risk(self):
        self.api.get_strategy_values = Mock(return_value={
            "buy_values": {"risk_50": "100"},
            "sell_values": {"risk_50": "90"}
        })
        buy_value = self.api.get_strategy_value_for_risk("Test Strategy", 50, "buy")
        sell_value = self.api.get_strategy_value_for_risk("Test Strategy", 50, "sell")
        self.assertEqual(buy_value, 100.0)
        self.assertEqual(sell_value, 90.0)

if __name__ == '__main__':
    unittest.main()