import json
import logging
import time
from datetime import datetime
from functools import lru_cache
from typing import Dict, Any, Iterator, Optional, Union

import requests


class AlphaSquaredAPIException(Exception):
    """Custom exception for AlphaSquared API errors."""


class AlphaSquared:
    """Main class for interacting with the AlphaSquared API."""

    BASE_URL = "https://alphasquared.io/wp-json/as/v1"
    RATE_LIMIT = 6  # requests per minute
    DEFAULT_CACHE_TTL = 300  # 5 minutes

    def __init__(self, api_token: str, cache_ttl: int = None, debug: bool = False):
        self.api_token = api_token
        self.last_request_time = 0
        self.request_count = 0
        self.logger = self._setup_logging(debug)
        self.cache_ttl = cache_ttl if cache_ttl is not None else self.DEFAULT_CACHE_TTL

    @staticmethod
    def _setup_logging(debug: bool = False):
        """
        Set up logging for the AlphaSquared client.
        
        :param debug: If True, set log level to DEBUG. Otherwise, use WARNING.
        :return: A configured logger instance.
        """
        logger = logging.getLogger(__name__)
        if debug:
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.WARNING)
        return logger

    def _make_request(self, endpoint: str, params: Dict[str, Any] = None, timeout: Optional[float] = None) -> Dict[str, Any]:
        self._check_rate_limit()
        # Send the token without Bearer prefix
        headers = {
            "Authorization": self.api_token,
            "User-Agent": "AlphaSquared-Python-Client/1.0",
            "Accept": "application/json"
        }
        url = f"{self.BASE_URL}/{endpoint}"
        
        try:
            # Log the request details for debugging
            self.logger.debug(f"Making request to {url} with params {params}")
            # Don't log headers in production as they may contain sensitive info
            self.logger.debug("Request headers: [REDACTED]")
            
            if timeout is not None:
                response = requests.get(url, headers=headers, params=params, timeout=timeout)
            else:
                response = requests.get(url, headers=headers, params=params)
            
            # Log the response for debugging
            self.logger.debug(f"Response status: {response.status_code}")
            self.logger.debug("Response headers: [REDACTED]")
            try:
                content_str = response.text if isinstance(getattr(response, "text", ""), str) else str(getattr(response, "text", ""))
                self.logger.debug(f"Response content: {content_str[:100]}...")  # Log first 100 chars
            except Exception:
                self.logger.debug("Response content: [unavailable]")
            
            if response.status_code != 200:
                error_message = f"API request failed: {response.status_code}"
                parsed = False
                # Try response.json() first
                try:
                    error_json = response.json()
                    if isinstance(error_json, (dict, list, str, int, float, bool)):
                        try:
                            error_message += f" - {json.dumps(error_json)}"
                        except TypeError:
                            error_message += f" - {str(error_json)}"
                        parsed = True
                except Exception:
                    parsed = False
                # Fallback to parsing response.text
                if not parsed:
                    raw_text = getattr(response, "text", "") or ""
                    try:
                        raw_json = json.loads(raw_text)
                        error_message += f" - {json.dumps(raw_json)}"
                    except Exception:
                        error_message += f" - {raw_text}"
                raise AlphaSquaredAPIException(error_message)
            
            # Try to parse the response as JSON
            try:
                return response.json()
            except json.JSONDecodeError:
                # If the response is not valid JSON, return a structured error
                self.logger.error(f"Invalid JSON response from API: {response.text[:100]}...")
                return {
                    "error": "Invalid JSON response from API",
                    "api_error": {
                        "message": "The API returned a response that could not be parsed as JSON",
                        "details": {"raw_response": response.text[:500]}  # Limit the size of the raw response
                    }
                }
                
        except requests.exceptions.RequestException as e:
            # Handle network errors
            error_message = f"Network error: {str(e)}"
            self.logger.error(error_message)
            raise AlphaSquaredAPIException(error_message)

    def _make_patch_request(
        self,
        endpoint: str,
        json_body: Dict[str, Any],
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Perform a PATCH request against the API with consistent error handling.
        Returns parsed JSON on 200 with body; returns {"status": "success"} on 204 or empty body.
        """
        self._check_rate_limit()
        headers = {
            "Authorization": self.api_token,
            "User-Agent": "AlphaSquared-Python-Client/1.0",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        url = f"{self.BASE_URL}/{endpoint}"
        try:
            self.logger.debug(f"Patching {url} with payload (truncated) {str(json_body)[:200]}")
            self.logger.debug("Request headers: [REDACTED]")
            if timeout is not None:
                response = requests.patch(url, headers=headers, params=params, json=json_body, timeout=timeout)
            else:
                response = requests.patch(url, headers=headers, params=params, json=json_body)

            self.logger.debug(f"Response status: {response.status_code}")
            self.logger.debug("Response headers: [REDACTED]")
            try:
                content_str = response.text if isinstance(getattr(response, "text", ""), str) else str(getattr(response, "text", ""))
                self.logger.debug(f"Response content: {content_str[:100]}...")
            except Exception:
                self.logger.debug("Response content: [unavailable]")

            # Success with no content
            if response.status_code == 204 or not response.text:
                if response.status_code == 200 or response.status_code == 204:
                    return {"status": "success"}

            if response.status_code != 200:
                error_message = f"API request failed: {response.status_code}"
                parsed = False
                try:
                    error_json = response.json()
                    if isinstance(error_json, (dict, list, str, int, float, bool)):
                        try:
                            error_message += f" - {json.dumps(error_json)}"
                        except TypeError:
                            error_message += f" - {str(error_json)}"
                        parsed = True
                except Exception:
                    parsed = False
                if not parsed:
                    raw_text = getattr(response, "text", "") or ""
                    try:
                        raw_json = json.loads(raw_text)
                        error_message += f" - {json.dumps(raw_json)}"
                    except Exception:
                        error_message += f" - {raw_text}"
                raise AlphaSquaredAPIException(error_message)

            try:
                return response.json()
            except json.JSONDecodeError:
                # No JSON body, treat as success
                return {"status": "success"}

        except requests.exceptions.RequestException as e:
            error_message = f"Network error: {str(e)}"
            self.logger.error(error_message)
            raise AlphaSquaredAPIException(error_message)

    @staticmethod
    def _require_exactly_one(*, strategy_name: Optional[str], strategy_id: Optional[int]) -> None:
        """Ensure exactly one of strategy_name or strategy_id is provided."""
        if bool(strategy_name) ^ bool(strategy_id):
            return
        raise AlphaSquaredAPIException("Provide exactly one of strategy_name or strategy_id.")

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
        error_details = {}
        error_message = str(e)
        
        # Try to extract JSON from the error message if it contains a separator
        if " - " in error_message:
            try:
                error_details = json.loads(error_message.split(" - ", 1)[1])
            except json.JSONDecodeError:
                # If JSON parsing fails, just use the raw error message
                error_details = {"message": error_message.split(" - ", 1)[1]}

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

    def get_strategy_actions(
        self,
        *,
        strategy_name: Optional[str] = None,
        strategy_id: Optional[int] = None,
        page: int = 1,
        per_page: int = 50,
        executed: Optional[Union[bool, str]] = None,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Retrieve a page of strategy actions from the AlphaSquared API.

        Parameters mirror the API; returns raw JSON dict.
        - Provide exactly one of strategy_name or strategy_id.
        - executed filter: True -> "true", False -> "false", "all" -> "all", None -> omitted.
        - Pagination: page>=1, per_page clamped to [1,100].
        """
        try:
            self._require_exactly_one(strategy_name=strategy_name, strategy_id=strategy_id)
        except AlphaSquaredAPIException as e:
            return self._handle_api_exception(e, "getting strategy actions (page 1)")

        safe_page = max(1, int(page))
        safe_per_page = max(1, min(int(per_page), 100))

        params: Dict[str, Any] = {"page": safe_page, "per_page": safe_per_page}
        if strategy_name:
            params["strategy_name"] = strategy_name
        if strategy_id is not None:
            params["strategy_id"] = strategy_id
        if executed is True:
            params["executed"] = "true"
        elif executed is False:
            params["executed"] = "false"
        elif executed == "all":
            params["executed"] = "all"

        try:
            return self._make_request("strategy-actions", params=params, timeout=timeout)
        except AlphaSquaredAPIException as e:
            return self._handle_api_exception(e, f"getting strategy actions (page {safe_page})")

    def iter_strategy_actions(
        self,
        *,
        strategy_name: Optional[str] = None,
        strategy_id: Optional[int] = None,
        per_page: int = 50,
        executed: Optional[Union[bool, str]] = None,
        timeout: Optional[float] = None,
    ) -> Iterator[Dict[str, Any]]:
        """
        Iterate through all strategy actions across pages. Yields raw action dicts.
        On error, yields a single error dict and stops.
        """
        try:
            self._require_exactly_one(strategy_name=strategy_name, strategy_id=strategy_id)
        except AlphaSquaredAPIException as e:
            yield self._handle_api_exception(e, "getting strategy actions (page 1)")
            return

        safe_per_page = max(1, min(int(per_page), 100))
        page = 1
        while True:
            params: Dict[str, Any] = {"page": page, "per_page": safe_per_page}
            if strategy_name:
                params["strategy_name"] = strategy_name
            if strategy_id is not None:
                params["strategy_id"] = strategy_id
            if executed is True:
                params["executed"] = "true"
            elif executed is False:
                params["executed"] = "false"
            elif executed == "all":
                params["executed"] = "all"

            try:
                data = self._make_request("strategy-actions", params=params, timeout=timeout)
            except AlphaSquaredAPIException as e:
                yield self._handle_api_exception(e, f"getting strategy actions (page {page})")
                return

            actions = data.get("actions") if isinstance(data, dict) else data
            if not actions:
                return

            for action in actions:
                yield action

            # Determine total_pages preference: nested pagination first, then top-level.
            total_pages: Optional[Union[int, str]] = None
            if isinstance(data, dict):
                pagination_meta = data.get("pagination") or {}
                total_pages = pagination_meta.get("total_pages") or data.get("total_pages")

            page += 1
            try:
                if total_pages and page > int(total_pages):
                    return
            except (TypeError, ValueError):
                # If total_pages is malformed, fallback to stopping only on empty list.
                pass

    def update_strategy_action_status(
        self,
        *,
        notification_id: Union[int, str],
        executed: bool = True,
        strategy_name: Optional[str] = None,
        strategy_id: Optional[int] = None,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Update the execution status of a strategy action. Returns raw dict.
        Provide exactly one of strategy_name or strategy_id.
        """
        try:
            self._require_exactly_one(strategy_name=strategy_name, strategy_id=strategy_id)
        except AlphaSquaredAPIException as e:
            return self._handle_api_exception(e, f"updating strategy action status for id {notification_id}")

        params: Dict[str, Any] = {}
        if strategy_name:
            params["strategy_name"] = strategy_name
        if strategy_id is not None:
            params["strategy_id"] = strategy_id

        payload = {"executed": bool(executed)}
        endpoint = f"strategy-actions/{str(notification_id)}"
        try:
            return self._make_patch_request(endpoint, json_body=payload, params=params, timeout=timeout)
        except AlphaSquaredAPIException as e:
            return self._handle_api_exception(e, f"updating strategy action status for id {notification_id}")

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
        
        # Check if the response contains an error
        if "error" in asset_info:
            self.logger.error(f"Error getting current risk for {asset}: {asset_info['error']}")
            return 0.0
            
        # Try to get the current_risk field
        current_risk = asset_info.get("current_risk")
        if current_risk is None:
            self.logger.warning(f"No 'current_risk' field found in response for {asset}")
            return 0.0
            
        try:
            return float(current_risk)
        except (ValueError, TypeError):
            self.logger.error(f"Could not convert 'current_risk' value '{current_risk}' to float for {asset}")
            return 0.0

    def get_strategy_value_for_risk(self, strategy_name: str, risk: float) -> tuple[str, float]:
        """
        Get the strategy action and value for a specific risk level, rounding down to the nearest defined risk level.

        :param strategy_name: The name of the strategy
        :param risk: The risk level (0-100, can be float)
        :return: A tuple containing the action ("buy" or "sell") and the value as a float
        """
        strategy_values = self.get_strategy_values(strategy_name)
        
        # Check if the response contains an error
        if "error" in strategy_values:
            self.logger.error(f"Error getting strategy values for {strategy_name}: {strategy_values['error']}")
            return "buy", 0.0
            
        buy_values = strategy_values.get("buy_values", {})
        sell_values = strategy_values.get("sell_values", {})
        
        if not buy_values and not sell_values:
            self.logger.warning(f"No buy or sell values found in strategy {strategy_name}")
            return "buy", 0.0
        
        # Extract risk levels from the keys
        risk_levels = []
        for k in buy_values.keys():
            try:
                if k.startswith("risk_"):
                    risk_levels.append(int(k.split('_')[1]))
            except (ValueError, IndexError):
                self.logger.warning(f"Invalid risk level format in key: {k}")
                
        for k in sell_values.keys():
            try:
                if k.startswith("risk_"):
                    risk_levels.append(int(k.split('_')[1]))
            except (ValueError, IndexError):
                self.logger.warning(f"Invalid risk level format in key: {k}")
                
        if not risk_levels:
            self.logger.warning(f"No valid risk levels found in strategy {strategy_name}")
            return "buy", 0.0
            
        # Find the nearest risk level that is less than or equal to the given risk
        nearest_risk = max([r for r in risk_levels if r <= risk], default=min(risk_levels))
        
        # Get the values for the nearest risk level
        buy_value_str = buy_values.get(f"risk_{nearest_risk}", "0")
        sell_value_str = sell_values.get(f"risk_{nearest_risk}", "0")
        
        # Convert to float, handling empty strings
        try:
            buy_value = float(buy_value_str) if buy_value_str else 0.0
        except (ValueError, TypeError):
            self.logger.warning(f"Invalid buy value '{buy_value_str}' for risk level {nearest_risk}")
            buy_value = 0.0
            
        try:
            sell_value = float(sell_value_str) if sell_value_str else 0.0
        except (ValueError, TypeError):
            self.logger.warning(f"Invalid sell value '{sell_value_str}' for risk level {nearest_risk}")
            sell_value = 0.0
        
        # Choose the side with the larger value; tie -> buy
        if buy_value > sell_value:
            return "buy", buy_value
        if sell_value > buy_value:
            return "sell", sell_value
        return "buy", buy_value

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