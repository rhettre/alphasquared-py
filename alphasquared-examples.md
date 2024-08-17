Here's an example in Python for the asset-info endpoint:
```python
import requests
def get_asset_info(token, asset_symbol='BTC'):
    url = f'https://alphasquared.io/wp-json/as/v1/asset-info?symbol={asset_symbol}'
    headers = {
        'Authorization': token
```

The new Endpoint is much safer and more flexible because we now return way more data:
```json
{'id': '1', 'asset_id': 'bitcoin', 'symbol': 'btc', 'name': 'Bitcoin', 'current_risk': '43.70', 'avg_risk_30d': '41.17', 'current_price': '66569.09', 'market_cap': '1313162037542', 'market_cap_rank': '1', 'price_change_percentage_24h': '3.96', 'price_change_percentage_7d_in_currency': '13.38', 'price_change_percentage_14d_in_currency': '17.07', 'price_change_percentage_30d_in_currency': '1.32', 'market_cap_change_24h': '49942403316', 'market_cap_change_percentage_24h': '3.95', 'circulating_supply': '19728181.00000000', 'total_supply': '21000000.00000000', 'max_supply': '21000000.00000000', 'ath': '73738.00', 'ath_change_percentage': '-9.76', 'last_updated': '2024-07-20 10:29:02', 'risk_change_percentage_7d': '15.19', 'risk_change_percentage_14d': '12.70', 'risk_change_percentage_30d': '-11.28'}
```

As you can see, there's also corresponding price and some averages. You SHOULD check the price from the exchange's price deviation to verify that AlphaSquared is serving the correct risk
We also now support hypotheticals, which is a way to check what risk would correspond to what price.

```python
import requests

def get_hypotheticals(token, asset_symbol='BTC'):
    url = f'https://alphasquared.io/wp-json/as/v1/hypotheticals/{asset_symbol}'
    headers = {
        'Authorization': token
```

This can be used to automatically set limit orders

Lastly, the Strategies Endpoint allows you to retrieve your personal Strategy values based on the strategy name
```python
import requests

def get_strategy_values(token, strategy_name='Bullrun2024'):
    url = f'https://alphasquared.io/wp-json/as/v1/strategy-values?strategy_name={strategy_name}'
    headers = {
        'Authorization': token
```
This way you can tweak your strategy on our website anytime and there's no need to hardcode a strategy into the python code

Putting everything together, here is the logic for how buying and selling is calculated
```python
import requests

def get_asset_info(token, asset_symbol):
    url = f'https://alphasquared.io/wp-json/as/v1/asset-info?symbol={asset_symbol}'
    headers = {
        'Authorization': token
```