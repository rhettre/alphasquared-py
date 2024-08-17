# AlphaSquared API Documentation

## Contents
- [AlphaSquared API Documentation](#alphasquared-api-documentation)
  - [Contents](#contents)
  - [1. Overview](#1-overview)
  - [2. Accessing the API](#2-accessing-the-api)
    - [2.1 API Endpoint (General Asset Info)](#21-api-endpoint-general-asset-info)
    - [2.2 API Endpoint Strategies](#22-api-endpoint-strategies)
    - [2.3 Hypotheticals Endpoint](#23-hypotheticals-endpoint)
    - [2.4 Authentication](#24-authentication)
    - [2.5 Obtaining Your API Token](#25-obtaining-your-api-token)
    - [2.6 Rate Limits](#26-rate-limits)
  - [3. API Response Examples](#3-api-response-examples)
    - [3.1 Asset Info](#31-asset-info)
    - [3.2 Strategy Values](#32-strategy-values)
    - [3.3 Hypothetical Values](#33-hypothetical-values)
  - [4 Tying to Subscription](#4-tying-to-subscription)
    - [5 Daily Token Management](#5-daily-token-management)
  - [6 Using the API](#6-using-the-api)
    - [6.1 Asset Info Data](#61-asset-info-data)
    - [6.2 Retrieve Strategy Values](#62-retrieve-strategy-values)
    - [6.3 Retrieve Hypothetical Values](#63-retrieve-hypothetical-values)
  - [7 Support](#7-support)
  - [8 Notice Regarding API Token Use and Data Sharing](#8-notice-regarding-api-token-use-and-data-sharing)
    - [8.1 Confidentiality and Proper Use of AlphaSquared API](#81-confidentiality-and-proper-use-of-alphasquared-api)
    - [8.2 Personal Use Only](#82-personal-use-only)
    - [8.3 Data Confidentiality](#83-data-confidentiality)
    - [8.4 Acknowledgement of Terms](#84-acknowledgement-of-terms)

## 1. Overview

Welcome to the AlphaSquared API. This API provides you with access to the latest risk value data and your personal Strategies. The API is designed to be easy to use while ensuring secure and efficient access to data.

## 2. Accessing the API

### 2.1 API Endpoint (General Asset Info)

- **URL**: `https://alphasquared.com/wp-json/as/v1/asset-info`
- **Method**: GET
- **Query Parameters**: `symbol`: Asset_Ticker (e.g. BTC, ETH, SOL, SPX etc.)
- **Description**: Use this endpoint to retrieve the latest risk values and other information for a specified asset. Replace 'Asset_Ticker' with the ticker symbol of the asset you are querying.

### 2.2 API Endpoint Strategies

- **URL**: `https://alphasquared.com/wp-json/as/v1/strategy-values`
- **Method**: GET
- **Query Parameters**: `strategy_name`: Your_Strategy_Name

### 2.3 Hypotheticals Endpoint

- **URL**: `https://alphasquared.com/wp-json/as/v1/hypotheticals/Ticker`
- **Method**: GET
- **Description**: Use this endpoint to retrieve hypothetical risk values for a specified asset. Replace 'Ticker' with the ticker symbol of the asset you are querying, such as BTC, ETH, SOL etc.

### 2.4 Authentication

- **Type**: Token-based
- **Usage**: Include your unique API token in the request header.
- **Header Format**: `Authorization: YOUR_API_TOKEN`

### 2.5 Obtaining Your API Token

Upon registration or account creation, you will receive an API token. This token is unique to your user account and must be included in every API request for authentication. You can view and regenerate your token from your account dashboard at https://alphasquared.io/user_dashboard

### 2.6 Rate Limits

To ensure fair usage and optimal performance, the API enforces rate limits:

- **Limit**: 6 requests per minute per user
- **Exceeding Limit**: Additional requests within the same minute will be denied.

## 3. API Response Examples

### 3.1 Asset Info

The API returns detailed asset information in JSON format.

- Response Example for the Asset_Ticker «ETH»:
```json
{ "id": "4", "asset_id": "ethereum", "symbol": "eth", "name": "Ethereum", "current_risk": "36.51",
"avg_risk_30d": "38.22", "current_price": "3400.03", "market_cap": "408650600030",
"market_cap_rank": "2", "price_change_percentage_24h": "-1.20",
"price_change_percentage_7d_in_currency": "10.70",
"price_change_percentage_14d_in_currency": "16.68",
"price_change_percentage_30d_in_currency": "-4.40",
"market_cap_change_24h": "-4776696071", "market_cap_change_percentage_24h": "-1.16",
"circulating_supply": "120224183.73336000", "total_supply": "120224183.73336000",
"max_supply": null, "ath": "4878.26", "ath_change_percetage": "-30.30",
"last_updated": "2024-07-19 11:23:03", "risk_change_percentage_7d": "19.27",
"risk_change_percentage_14d": "7.35", "risk_change_percentage_30d": "-11.47" }
```

### 3.2 Strategy Values

The API returns strategy-related risk and action thresholds based on the provided strategy name.

- Response Example for Strategy Name 'Bullrun2024':
```json
{ "strategy_name": "Bullrun2024",
"buy_values": {
"risk_0": "600", "risk_5": "600", "risk_10": "600", "risk_15": "525", "risk_20": "525", "risk_25":
"450", "risk_30": "450", "risk_35": "375", "risk_40": "375", "risk_45": "300", "risk_50": "300",
"risk_55": "225", "risk_60": "225", "risk_65": "150", "risk_70": "100", "risk_75": "", "risk_80": "",
"risk_85": "", "risk_90": "", "risk_95": "", "risk_100": "" },
"sell_values": {
"risk_0": "", "risk_5": "", "risk_10": "", "risk_15": "", "risk_20": "", "risk_25": "", "risk_30": "",
"risk_35": "", "risk_40": "", "risk_45": "", "risk_50": "", "risk_55": "", "risk_60": "", "risk_65": "",
"risk_70": "", "risk_75": "", "risk_80": "5", "risk_85": "10", "risk_90": "15", "risk_95": "20", "risk_100":
"25" }}
```

### 3.3 Hypothetical Values

The API returns hypothetical risk values for various assets in JSON format.

- Response Example for the Ticker 'ETH':
```json
[ {"id":"1","risk_level":"2.50","value":"1556.25"}, {"id":"2","risk_level":"5.00","value":"1787.50"},
{"id":"3","risk_level":"10.00","value":"2134.38"}, {"id":"4","risk_level":"15.00","value":"2365.63"},
{"id":"5","risk_level":"20.00","value":"2596.88"}, {"id":"6","risk_level":"25.00","value":"2828.13"},
{"id":"7","risk_level":"30.00","value":"3059.38"}, {"id":"8","risk_level":"35.00","value":"3290.63"},
{"id":"9","risk_level":"40.00","value":"3579.69"}, {"id":"10","risk_level":"45.00","value":"3810.94"},
{"id":"11","risk_level":"50.00","value":"4042.19"}, {"id":"12","risk_level":"55.00","value":"4273.44"},
{"id":"13","risk_level":"60.00","value":"4562.50"}, {"id":"14","risk_level":"65.00","value":"4793.75"},
{"id":"15","risk_level":"70.00","value":"5082.81"}, {"id":"16","risk_level":"75.00","value":"5314.06"},
{"id":"17","risk_level":"80.00","value":"5603.13"}, {"id":"18","risk_level":"85.00","value":"5950.00"},
{"id":"19","risk_level":"90.00","value":"6412.50"}, {"id":"20","risk_level":"95.00","value":"6990.63"},
{"id":"21","risk_level":"97.50","value":"7568.75"}]
```

## 4 Tying to Subscription

Your access to the API is directly tied to your subscription plan:
• Eligible Plans: Only users with active and paid subscription plans have
access to the API.
• Users without paid access will have their API tokens invalidated and will not
be able to access the API.

### 5 Daily Token Management

A daily automated process checks the subscription status of all users. If your subscription is downgraded to the "No Access Plan," your API token will be
automatically deleted, and you will lose access to the API.

## 6 Using the API

### 6.1 Asset Info Data

To use the API, make a GET request to the API endpoint with your token included in the header. The response will contain the latest risk value data.

• Example Request (using curl):
```bash
curl -H "Authorization: YOUR_API_TOKEN" https://alphasquared.io/wp-json/as/v1/asset-
info?symbol=Asset_Ticker”
```
When encountering errors, make sure your browser has correctly copied the curl
example and make sure you’ve replaced the Token and Asset_Ticker
Placeholders.

### 6.2 Retrieve Strategy Values

To use the API, make a GET request to the API endpoint with your token included in the header. The response will contain the buy and sell values for the specified strategy based on its name.
strategy based on its name.

• Example Request (using curl):
```bash
curl -H "Authorization: YOUR_API_TOKEN" https://alphasquared.io/wp-json/as/v1/strategy-
values?strategy_name=Your_Strategy_Name
```

### 6.3 Retrieve Hypothetical Values
To use the API to retrieve hypothetical values for a specified asset, make a GET
request to the API endpoint with your token included in the header. The response
will contain the hypothetical risk values for the specified asset based on its ticker
symbol.
Example Request (using curl):
```bash
curl -H "Authorization: YOUR_API_TOKEN" https://alphasquared.io/wp-json/as/v1/hypotheticals/ETH
```

## 7 Support
For any issues, questions, or assistance, please reach out to our support team through our website or contact us directly at admin@alphasquared.io.

## 8 Notice Regarding API Token Use and Data Sharing

### 8.1 Confidentiality and Proper Use of AlphaSquared API
As a valued member of AlphaSquared, you are entrusted with access to our proprietary risk value data through our API service. It is imperative to understand and adhere to the following terms regarding the use of your unique API token and the data accessed through our API:

### 8.2 Personal Use Only
- **Strictly Personal:** The API token provided to you is for your personal use only. It grants you access to valuable data that is part of your AlphaSquared membership benefits.
- **No Sharing Policy:** The token is unique to your account and should remain confidential.

### 8.3 Data Confidentiality
- **Usage Limitation:** The data obtained through the AlphaSquared API, including risk value information, is exclusive to your personal use. It is not to be shared, distributed, or disseminated in any form to individuals or entities outside of your personal use. This excludes personal trading bots on exchanges or similar services.
- **Monitoring for Compliance:** We actively monitor the use of API tokens and data access patterns to ensure compliance with these terms.
- **Legal Action:** Failure to adhere to these terms, including unauthorized sharing of your API token or data, will prompt immediate revocation of your API access and may lead to legal action against you. We reserve the right to pursue all available legal remedies to protect our proprietary information.

### 8.4 Acknowledgement of Terms
By generating and using an API token from AlphaSquared, you acknowledge and agree to these terms. You commit to using the API and the data it provides solely for your private use as part of your AlphaSquared membership. Any breach of these terms will be taken seriously and may result in legal consequences.