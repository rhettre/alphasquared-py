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
            "buy_values": {"risk_50": "100", "risk_60": "120"},
            "sell_values": {"risk_50": "90", "risk_60": "80"}
        })
        
        # Test buy scenario
        action, value = self.api.get_strategy_value_for_risk("Test Strategy", 55)
        self.assertEqual(action, "buy")
        self.assertEqual(value, 100.0)
        
        # Test sell scenario (choose larger value -> still buy here)
        action, value = self.api.get_strategy_value_for_risk("Test Strategy", 65)
        self.assertEqual(action, "buy")
        self.assertEqual(value, 120.0)
        
        # Test equal values scenario (should default to buy)
        self.api.get_strategy_values = Mock(return_value={
            "buy_values": {"risk_50": "100"},
            "sell_values": {"risk_50": "100"}
        })
        action, value = self.api.get_strategy_value_for_risk("Test Strategy", 50)
        self.assertEqual(action, "buy")
        self.assertEqual(value, 100.0)
        
        # Test no values scenario
        self.api.get_strategy_values = Mock(return_value={
            "buy_values": {},
            "sell_values": {}
        })
        action, value = self.api.get_strategy_value_for_risk("Test Strategy", 50)
        self.assertEqual(action, "buy")
        self.assertEqual(value, 0.0)

    @patch('alphasquared.alphasquared.requests.get')
    def test_get_strategy_actions_success(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "actions": [
                {"id": 1, "type": "BUY", "amount": "100", "risk_level": 30},
                {"id": 2, "type": "SELL", "amount": "50", "risk_level": 80},
            ],
            "pagination": {"total": 2, "total_pages": 1, "current_page": 1, "per_page": 50},
        }
        mock_get.return_value = mock_response

        result = self.api.get_strategy_actions(strategy_name="My Strategy", page=1, per_page=50)
        self.assertIn("actions", result)
        self.assertEqual(len(result["actions"]), 2)
        self.assertEqual(result["pagination"]["total_pages"], 1)

    @patch('alphasquared.alphasquared.requests.get')
    def test_get_strategy_actions_param_building(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"actions": [], "pagination": {"total_pages": 1}}
        mock_get.return_value = mock_response

        # executed True maps to "true", clamp per_page to 100, page min 1
        self.api.get_strategy_actions(strategy_id=123, page=0, per_page=500, executed=True)
        args, kwargs = mock_get.call_args
        params = kwargs.get('params', {})
        self.assertEqual(params.get('page'), 1)
        self.assertEqual(params.get('per_page'), 100)
        self.assertEqual(params.get('strategy_id'), 123)
        self.assertEqual(params.get('executed'), 'true')

        # executed False maps to "false"
        self.api.get_strategy_actions(strategy_id=123, executed=False)
        _, kwargs = mock_get.call_args
        self.assertEqual(kwargs['params'].get('executed'), 'false')

        # executed "all" passes through
        self.api.get_strategy_actions(strategy_id=123, executed="all")
        _, kwargs = mock_get.call_args
        self.assertEqual(kwargs['params'].get('executed'), 'all')

        # executed None omits the param
        self.api.get_strategy_actions(strategy_id=123)
        _, kwargs = mock_get.call_args
        self.assertNotIn('executed', kwargs['params'])

    @patch('alphasquared.alphasquared.requests.get')
    def test_iter_strategy_actions_multiple_pages_with_nested_pagination(self, mock_get):
        # Page 1
        resp1 = Mock()
        resp1.status_code = 200
        resp1.json.return_value = {
            "actions": [{"id": 1, "type": "BUY"}, {"id": 2, "type": "SELL"}],
            "pagination": {"total": 3, "total_pages": 2, "current_page": 1, "per_page": 2},
        }
        # Page 2
        resp2 = Mock()
        resp2.status_code = 200
        resp2.json.return_value = {
            "actions": [{"id": 3, "type": "BUY"}],
            "pagination": {"total": 3, "total_pages": 2, "current_page": 2, "per_page": 2},
        }
        mock_get.side_effect = [resp1, resp2]

        actions = list(self.api.iter_strategy_actions(strategy_name="My Strategy", per_page=2))
        self.assertEqual(len(actions), 3)
        self.assertEqual(actions[0].get('id'), 1)
        self.assertEqual(actions[2].get('id'), 3)
        # Only two API calls should be made because total_pages=2
        self.assertEqual(mock_get.call_count, 2)

    @patch('alphasquared.alphasquared.requests.get')
    def test_iter_strategy_actions_error_yields_once(self, mock_get):
        # First page ok
        resp1 = Mock()
        resp1.status_code = 200
        resp1.json.return_value = {
            "actions": [{"id": 1, "type": "BUY"}],
            "pagination": {"total_pages": 3, "current_page": 1},
        }
        # Second page error (e.g., 429)
        resp2 = Mock()
        resp2.status_code = 429
        resp2.text = json.dumps({"code": "too_many_requests", "message": "Too Many Requests"})
        mock_get.side_effect = [resp1, resp2]

        yielded = list(self.api.iter_strategy_actions(strategy_id=7, per_page=1))
        # Expect first action dict and then a single error dict
        self.assertEqual(yielded[0].get('id'), 1)
        self.assertTrue(isinstance(yielded[1], dict) and 'error' in yielded[1])
        self.assertIn('Too Many Requests', yielded[1]['error'])
        self.assertEqual(len(yielded), 2)

    @patch('alphasquared.alphasquared.requests.patch')
    def test_update_strategy_action_status_success_with_json(self, mock_patch):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = json.dumps({"id": 1, "executed": True})
        mock_response.json.return_value = {"id": 1, "executed": True}
        mock_patch.return_value = mock_response

        res = self.api.update_strategy_action_status(notification_id=42, executed=True, strategy_name="S")
        self.assertFalse(self.api.has_error(res))
        self.assertTrue(res.get("executed"))
        # verify URL path and payload
        args, kwargs = mock_patch.call_args
        self.assertIn('/strategy-actions/42', args[0])
        self.assertEqual(kwargs['json'], {"executed": True})

    @patch('alphasquared.alphasquared.requests.patch')
    def test_update_strategy_action_status_success_empty_body(self, mock_patch):
        mock_response = Mock()
        mock_response.status_code = 204
        mock_response.text = ""
        mock_patch.return_value = mock_response

        res = self.api.update_strategy_action_status(notification_id="abc123", executed=True, strategy_id=9)
        self.assertEqual(res, {"status": "success"})
        args, kwargs = mock_patch.call_args
        self.assertIn('/strategy-actions/abc123', args[0])

    @patch('alphasquared.alphasquared.requests.patch')
    def test_update_strategy_action_status_error(self, mock_patch):
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = json.dumps({"message": "Action not found"})
        mock_patch.return_value = mock_response

        res = self.api.update_strategy_action_status(notification_id=999, executed=True, strategy_name="S")
        self.assertTrue(self.api.has_error(res))
        self.assertIn("not found", res["error"].lower())

    @patch('alphasquared.alphasquared.requests.get')
    def test_get_strategy_actions_timeout_forwarded(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"actions": [], "pagination": {"total_pages": 1}}
        mock_get.return_value = mock_response

        self.api.get_strategy_actions(strategy_id=1, timeout=5.5)
        _, kwargs = mock_get.call_args
        self.assertEqual(kwargs.get('timeout'), 5.5)

    @patch('alphasquared.alphasquared.requests.patch')
    def test_update_strategy_action_status_timeout_forwarded(self, mock_patch):
        mock_response = Mock()
        mock_response.status_code = 204
        mock_response.text = ""
        mock_patch.return_value = mock_response

        self.api.update_strategy_action_status(notification_id=1, executed=True, strategy_id=2, timeout=2.0)
        _, kwargs = mock_patch.call_args
        self.assertEqual(kwargs.get('timeout'), 2.0)

if __name__ == '__main__':
    unittest.main()