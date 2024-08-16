import requests
import time
from typing import Dict, Any, List

class AlphaSquaredAPIException(Exception):
    pass

class AlphaSquared:
    BASE_URL = "https://alphasquared.io/wp-json/as/v1"
    RATE_LIMIT = 6  # requests per minute

    def __init__(self, api_token: str):
        self.api_token = api_token
        self.last_request_time = 0
        self.request_count = 0

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

    def get_asset_info(self, asset_symbol: str) -> Dict[str, Any]:
        return self._make_request("asset-info", params={"symbol": asset_symbol})

    def get_strategy_values(self, strategy_name: str) -> Dict[str, Any]:
        return self._make_request("strategy-values", params={"strategy_name": strategy_name})

    def get_hypotheticals(self, asset_symbol: str) -> List[Dict[str, Any]]:
        return self._make_request(f"hypotheticals/{asset_symbol}")