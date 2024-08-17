import requests
import time
import logging
import json
from typing import Dict, Any

class AlphaSquaredAPIException(Exception):
    """Custom exception for AlphaSquared API errors."""

class AlphaSquared:
    """Main class for interacting with the AlphaSquared API."""

    BASE_URL = "https://alphasquared.io/wp-json/as/v1"
    RATE_LIMIT = 6  # requests per minute

    def __init__(self, api_token: str):
        self.api_token = api_token
        self.last_request_time = 0
        self.request_count = 0
        self.logger = self._setup_logging()

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

    @staticmethod
    def has_error(result: Dict[str, Any]) -> bool:
        """Check if the result contains an error."""
        return "error" in result

    @staticmethod
    def get_api_error(result: Dict[str, Any]) -> Dict[str, Any]:
        """Get the API error details from the result."""
        return result.get("api_error", {})