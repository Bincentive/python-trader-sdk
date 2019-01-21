# Setup

1. Clone this project from the git repo.
2. At project root, install this package by running  
   `$ pip install .`

# Usage

```python
from bincentive_trader.client import TraderClient

email = 'me@example.com'
password = 'super secret'

client = TraderClient(email, password, False)

```

Available client methods are listed in the Bincentive Client Methods section.
Each method has a `timeout` parameter that will cause a `bincentive_trader.exceptions.Timeout`
exception if no response is received in the specified seconds.

<a name="BincentiveClient"></a>

## Bincentive Client Methods
Bincentive Trader Client

**Kind**: global class  

* [BincentiveClient](#BincentiveClient)
    
    * [.get_strategy_list(timeout=None)](#BincentiveClient+get_strategy_list)
    * [.get_exchange_list(timeout=None)](#BincentiveClient+get_exchange_list)
    * [.add_market_order(strategy_id, exchange_id, base_currency, quote_currency, side, amount, leverage=None, timeout=None)](#BincentiveClient+add_market_order)
    * [.get_history_list(strategy_id, begin_time, end_time, account_type='real', timeout=None)](#BincentiveClient+get_history_list)
    * [.add_api_key(api_key, api_secret_key, exchange_id, timeout=None)](#BincentiveClient+add_api_key)
    * [.get_api_key_list(timeout=None)](#BincentiveClient+get_api_key_list)
    * [.delete_api_key(exchange_id, timeout=None)](#BincentiveClient+delete_api_key)
  

<a name="new_BincentiveClient_new"></a>

<a name="BincentiveClient+get_strategy_list"></a>

### bincentiveClient.get_strategy_list(timeout=None)
Gets the list of strategies

**Kind**: instance method of [<code>BincentiveClient</code>](#BincentiveClient)  


<a name="BincentiveClient+get_exchange_list"></a>

### bincentiveClient.get_exchange_list(timeout=None)
Gets the list of exchanges 

**Kind**: instance method of [<code>BincentiveClient</code>](#BincentiveClient) 

<a name="BincentiveClient+add_market_order"></a>

### bincentiveClient.add_market_order(strategy_id, exchange_id, base_currency, quote_currency, side, amount, leverage=None, timeout=None)
Adds an order for a specific strategy

**Kind**: instance method of [<code>BincentiveClient</code>](#BincentiveClient)  

| Param | Type |
| --- | --- |
| strategy_id | <code>number</code> | 
| exchange_id | <code>number</code> | 
| base_currency | <code>string</code> | 
| quote_currency | <code>string</code> | 
| side | <code>string</code> | 
| amount | <code>number</code> | 
| leverage | <code>number</code> |


<a name="BincentiveClient+get_history_list"></a>

### bincentiveClient.get_history_list(strategy_id, begin_time, end_time, account_type='real', timeout=None)
Gets the historical data of all transactions

**Kind**: instance method of [<code>BincentiveClient</code>](#BincentiveClient)  

| Param | Type |
| --- | --- |
| strategy_id | <code>number</code> | 
| begin_time | <code>string</code> | 
| end_time | <code>string</code> | 
| account_type | <code>string</code> | 


 
<a name="BincentiveClient+add_api_key"></a>

### bincentiveClient.add_api_key(api_key, api_secret_key, exchange_id, timeout=None)
Adds all the keys of each transaction

**Kind**: instance method of [<code>BincentiveClient</code>](#BincentiveClient)  

| Param | Type |
| --- | --- |
| api_key | <code>string</code> | 
| api_secret_key | <code>string</code> | 
| exchange_id | <code>number</code> | 


<a name="BincentiveClient+get_api_key_list"></a>

### bincentiveClient.get_api_key_list(timeout=None)
Gets API key list

**Kind**: instance method of [<code>BincentiveClient</code>](#BincentiveClient)  

<a name="BincentiveClient+delete_api_key"></a>

### bincentiveClient.delete_api_key(exchange_id, timeout=None)
Deletes all the keys of a transaction

**Kind**: instance method of [<code>BincentiveClient</code>](#BincentiveClient)  

| Param | Type |
| --- | --- |
| exchangeId | <code>number</code> | 




