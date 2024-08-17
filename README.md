# AlphaSquared Python Client

This is an unofficial Python client for the AlphaSquared API. It allows users to interact with the API to retrieve asset information, strategy values, and hypothetical data for cryptocurrency trading.

## Features

- Easy-to-use Python wrapper for the AlphaSquared API
- Supports authentication using API tokens
- Implements rate limiting to comply with API usage rules
- Provides methods to retrieve asset information, strategy values, and hypothetical data
- Includes error handling and logging functionality

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

## Error Handling

The client includes built-in error handling. You can check for errors in the API responses:

```python
result = api.get_asset_info("INVALID_ASSET")
if api.has_error(result):
    print("An error occurred:", result["error"])
```

## Rate Limiting

The client automatically handles rate limiting to ensure compliance with the API's usage rules (6 requests per minute).

## Documentation

For more information about the AlphaSquared API, consult the [official API documentation](https://alphasquared.io/api-docs).

## License

This project is licensed under the MIT License. See the LICENSE file for more information.

## Disclaimer

This project is not affiliated with, maintained, or endorsed by AlphaSquared. Use this software at your own risk. Trading cryptocurrencies carries a risk of financial loss. The developers of this software are not responsible for any financial losses or damages incurred while using this software.

## Support

For any issues, questions, or assistance, please open an issue on the GitHub repository or contact AlphaSquared support at admin@alphasquared.io.
