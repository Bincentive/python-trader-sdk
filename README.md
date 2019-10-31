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

<a name="BincentiveClient+set_position"></a>

### bincentiveClient.set_position(self, strategy_id, Ratio, LimitPrice, timeout=None)
Set a position ratio for a specific strategy to send the order

**Kind**: instance method of [<code>BincentiveClient</code>](#BincentiveClient)  

| Param | Type |
| --- | --- |
| strategy_id | <code>number</code> | 
| Ratio | <code>number</code> | 
| LimitPrice | <code>number</code> | 

sample code

```python

stgy_id = your_strategy_id
r = 0.3

order_id = client.set_position(strategy_id=stgy_id, Ratio=r, LimitPrice=1)

```