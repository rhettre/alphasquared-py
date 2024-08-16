from alphasquared import AlphaSquared

# Usage example:
api = AlphaSquared("NxIECs9TCBW88AxXKg9WQE9HvYE1iQxD8HysmPWm")

btc_info = api.get_asset_info("BTC")
print(btc_info)

eth_hypotheticals = api.get_hypotheticals("ETH")
print(eth_hypotheticals)
