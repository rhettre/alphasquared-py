# AlphaSquared Python Client

This is an unofficial Python client for the AlphaSquared API. It allows users to interact with the API to retrieve asset information, strategy values, and hypothetical data for cryptocurrency trading.

## Features

- Easy-to-use Python wrapper for the AlphaSquared API
- Supports authentication using API tokens
- Implements rate limiting to comply with API usage rules
- Provides methods to retrieve asset information, strategy values, and hypothetical data
- Includes error handling and logging functionality
- Fetch comprehensive asset data (price, risk, market cap, etc.)
- Get custom strategy values
- Built-in caching to reduce API calls
- Automatic rate limiting to comply with API rules
- Configurable logging with debug mode for development

## Installation

Install the package using pip:

```bash
pip install alphasquared-py
```

## Authentication

To use the AlphaSquared API, you need to obtain an API token from your AlphaSquared account dashboard. Once you have your token, you can authenticate as follows:

```python
from alphasquared import AlphaSquared

api = AlphaSquared("YOUR_API_TOKEN")
```

You can also enable debug mode for more detailed logging during development:

```python
api = AlphaSquared("YOUR_API_TOKEN", debug=True)
```
The client sends your token in the `Authorization` header as-is (no `Bearer` prefix required).

## Usage

### Retrieving Asset Information

```python
btc_info = api.get_asset_info("BTC")
print(btc_info)
```

### Getting Strategy Values

```python
strategy_values = api.get_strategy_values("My Custom Strat")
print(strategy_values)
```

### Fetching Hypothetical Data

```python
eth_hypotheticals = api.get_hypotheticals("ETH")
print(eth_hypotheticals)
```

### Fetching Comprehensive Asset Data

```python
btc_comprehensive = api.get_comprehensive_asset_data("BTC")
print(btc_comprehensive)
```

### Getting Strategy Action and Value for a Specific Risk Level

```python
action, value = api.get_strategy_value_for_risk("My Custom Strat", 50)
print(f"Action: {action}, Value: {value}")
```
Notes:
- Rounds the input risk down to the nearest defined risk bucket in your strategy.
- Chooses the side (buy/sell) with the larger value at that bucket; ties default to buy.

### Getting Current Risk Level

```python
current_risk = api.get_current_risk("BTC")
print(current_risk)
```

### Getting Strategy Action and Value Based on Current Risk

This example demonstrates how to get the current risk for an asset, then use that risk level to determine the strategy action and value:

```python
# Get the current risk for BTC
btc_risk = api.get_current_risk("BTC")
print(f"Current BTC Risk: {btc_risk}")

# Define your strategy name in AlphaSquared
strategy_name = "My Custom Strat"

# Get the strategy action and value for the current risk
action, value = api.get_strategy_value_for_risk(strategy_name, btc_risk)
print(f"For risk {btc_risk}: Action = {action.upper()}, Value = {value}")
```

## Error Handling

The client includes built-in error handling. You can check for errors in the API responses:

```python
result = api.get_asset_info("INVALID_ASSET")
if api.has_error(result):
    print("An error occurred:", result["error"])
```

## Rate Limiting

The client automatically handles rate limiting to ensure compliance with the API's usage rules (6 requests per minute).

## Caching

The client uses caching to reduce the number of API calls. You can set the cache TTL (time-to-live) when initializing the client. The default cache TTL is 5 minutes.

```python
api = AlphaSquared("YOUR_API_TOKEN", cache_ttl=300)  # 5 minutes
```

## Logging

The client includes configurable logging functionality. By default, logging is set to WARNING level. You can enable debug mode for more detailed logging during development:

```python
api = AlphaSquared("YOUR_API_TOKEN", debug=True)
```

In production, sensitive information in request headers and responses is automatically redacted in logs.

### Strategy Actions

The client supports retrieving strategy action signals and updating their execution status.

- Actions are returned as raw dicts; fields are not coerced.
- Known action types include BUY, SELL, and Irregular Buy.
- All timestamps from the API should be treated as UTC.

Fetch a single page (paginated):

```python
latest = api.get_strategy_actions(strategy_name="My Strategy", page=1, per_page=50, executed=False)
for act in latest.get("actions", []):
    print(act)
```
Executed filter:
- `executed=True` → requests items marked executed
- `executed=False` → requests pending items (recommended for polling)
- `executed="all"` → returns both executed and pending

Iterate across all pages (history):

```python
for act in api.iter_strategy_actions(strategy_id=12345, per_page=100):
    # Process each action dict
    pass
```

Mark an action as executed (PATCH):

```python
res = api.update_strategy_action_status(notification_id=9876, executed=True, strategy_name="My Strategy")
if api.has_error(res):
    print("Failed:", res["error"])
```

Operational notes:

- Concurrency: multiple pollers can double-execute before either updates status. Consider a single worker or external coordination.
- Stateless polling: prefer `executed=False` when fetching to avoid repeatedly seeing executed items; after executing on your exchange, patch the item to `executed=True`.

End-to-end example:

```python
page = api.get_strategy_actions(strategy_name="My Strategy", executed=False)
for action in page.get("actions", []):
    # Execute trade on your exchange here
    api.update_strategy_action_status(notification_id=action.get("notificationId"), executed=True, strategy_name="My Strategy")
```
Tip: In the example script `main.py`, a `DO_PATCH` flag is used to prevent side effects during demos. In production, call `update_strategy_action_status(..., executed=True)` only after your exchange order succeeds.

## Documentation

For more information about the AlphaSquared API, consult the [official API documentation](https://alphasquared.io/api-docs).

## License

This project is licensed under the MIT License. See the LICENSE file for more information.

## Disclaimer

This project is not affiliated with, maintained, or endorsed by AlphaSquared. Use this software at your own risk. Trading cryptocurrencies carries a risk of financial loss. The developers of this software are not responsible for any financial losses or damages incurred while using this software.

## Support

For any issues, questions, or assistance, please open an issue on the GitHub repository or contact AlphaSquared support at admin@alphasquared.io.