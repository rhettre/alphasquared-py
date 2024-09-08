import json
import logging
import time
from datetime import datetime
from functools import lru_cache
from typing import Dict, Any

import requests


class AlphaSquaredAPIException(Exception):
    """Custom exception for AlphaSquared API errors."""


class AlphaSquared:
    """Main class for interacting with the AlphaSquared API."""

    BASE_URL = "https://alphasquared.io/wp-json/as/v1"
    RATE_LIMIT = 6  # requests per minute
    DEFAULT_CACHE_TTL = 300  # 5 minutes

    def __init__(self, api_token: str, cache_ttl: int = None):
        self.api_token = api_token
        self.last_request_time = 0
        self.request_count = 0
        self.logger = self._setup_logging()
        self.cache_ttl = cache_ttl if cache_ttl is not None else self.DEFAULT_CACHE_TTL

    @staticmethod
    def _setup_logging():
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        self._check_rate_limit()
        headers = {"Authorization": self.api_token}
        url = f"{self.BASE_URL}/{endpoint}"
        response = requests.get(url, headers=headers, params=params)

        if response.status_code != 200:
            raise AlphaSquaredAPIException(f"API request failed: {response.status_code} - {response.text}")

        return response.json()

    def _check_rate_limit(self):
        current_time = time.time()
        if current_time - self.last_request_time >= 60:
            self.last_request_time = current_time
            self.request_count = 0

        if self.request_count >= self.RATE_LIMIT:
            sleep_time = 60 - (current_time - self.last_request_time)
            if sleep_time > 0:
                time.sleep(sleep_time)
            self.last_request_time = time.time()
            self.request_count = 0

        self.request_count += 1

    def _handle_api_exception(self, e: AlphaSquaredAPIException, context: str) -> Dict[str, Any]:
        error_details = json.loads(str(e).split(" - ", 1)[1]) if " - " in str(e) else {}

        if context.startswith("getting hypotheticals"):
            asset = context.split("for ")[-1]
            error_message = f"Invalid asset: {asset}. Please provide a valid cryptocurrency symbol (e.g., 'BTC' or 'ETH')."
        elif context.startswith("getting strategy values"):
            strategy = context.split("for ")[-1]
            error_message = f"Strategy not found: {strategy}. Please check the strategy name and try again."
        else:
            error_message = f"Error in {context}: {error_details.get('message', str(e))}"

        self.logger.error(error_message)

        return {
            "error": error_message,
            "api_error": {
                "message": str(e),
                "details": error_details
            }
        }

    def get_asset_info(self, asset_symbol: str) -> Dict[str, Any]:
        """Get information for a specific asset."""
        try:
            return self._make_request("asset-info", params={"symbol": asset_symbol})
        except AlphaSquaredAPIException as e:
            return self._handle_api_exception(e, f"getting asset info for {asset_symbol}")

    def get_strategy_values(self, strategy_name: str) -> Dict[str, Any]:
        """Get values for a specific strategy."""
        try:
            return self._make_request("strategy-values", params={"strategy_name": strategy_name})
        except AlphaSquaredAPIException as e:
            return self._handle_api_exception(e, f"getting strategy values for {strategy_name}")

    def get_hypotheticals(self, asset_symbol: str) -> Dict[str, Any]:
        """Get hypothetical values for a specific asset."""
        try:
            return self._make_request(f"hypotheticals/{asset_symbol}")
        except AlphaSquaredAPIException as e:
            return self._handle_api_exception(e, f"getting hypotheticals for {asset_symbol}")

    @lru_cache(maxsize=32)
    def _cached_comprehensive_asset_data(self, asset: str, timestamp: int) -> Dict[str, Any]:
        return self._get_comprehensive_asset_data_uncached(asset)

    def get_comprehensive_asset_data(self, asset: str) -> Dict[str, Any]:
        timestamp = int(datetime.now().timestamp() // self.cache_ttl)
        return self._cached_comprehensive_asset_data(asset, timestamp)

    def _get_comprehensive_asset_data_uncached(self, asset: str) -> Dict[str, Any]:
        """
        Fetch comprehensive data for a given asset, including asset info and hypotheticals.

        :param asset: The asset symbol (e.g., 'BTC', 'ETH')
        :return: A dictionary containing asset info and hypotheticals
        """
        asset_info = self.get_asset_info(asset)
        hypotheticals = self.get_hypotheticals(asset)

        return {
            "asset_info": asset_info,
            "hypotheticals": hypotheticals
        }

    def get_current_risk(self, asset: str) -> float:
        """
        Get the current risk value for a given asset.

        :param asset: The asset symbol (e.g., 'BTC', 'ETH')
        :return: The current risk value as a float
        """
        asset_info = self.get_asset_info(asset)
        return float(asset_info.get("current_risk", 0))

    def get_strategy_value_for_risk(self, strategy_name: str, risk: float) -> tuple[str, float]:
        """
        Get the strategy action and value for a specific risk level, rounding down to the nearest defined risk level.

        :param strategy_name: The name of the strategy
        :param risk: The risk level (0-100, can be float)
        :return: A tuple containing the action ("buy" or "sell") and the value as a float
        """
        strategy_values = self.get_strategy_values(strategy_name)
        buy_values = strategy_values.get("buy_values", {})
        sell_values = strategy_values.get("sell_values", {})
        
        risk_levels = sorted(set([int(k.split('_')[1]) for k in buy_values.keys()] + 
                                 [int(k.split('_')[1]) for k in sell_values.keys()]))
        nearest_risk = max([r for r in risk_levels if r <= risk], default=min(risk_levels))
        
        buy_value = float(buy_values.get(f"risk_{nearest_risk}", "0") or 0)
        sell_value = float(sell_values.get(f"risk_{nearest_risk}", "0") or 0)
        
        if buy_value > sell_value:
            return "buy", buy_value
        elif sell_value > buy_value:
            return "sell", sell_value
        else:
            return "buy", 0.0

    def force_refresh_asset_data(self, asset: str) -> Dict[str, Any]:
        self._cached_comprehensive_asset_data.cache_clear()
        return self.get_comprehensive_asset_data(asset)

    @staticmethod
    def has_error(result: Dict[str, Any]) -> bool:
        """Check if the result contains an error."""
        return "error" in result

    @staticmethod
    def get_api_error(result: Dict[str, Any]) -> Dict[str, Any]:
        """Get the API error details from the result."""
        return result.get("api_error", {})