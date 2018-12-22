# Setup

1. Clone this project from git repo.
2. At project root, install this package by running  
   `$ pip install .`

# Usage

```python
from bincentive_trader.client import TraderClient

email = 'me@exambple.com'
password = 'super secret'
testing = True  # Change this to False if you're using mainnet. 

client = TraderClient(email, password, testing)

```

Available clients methods are:
- get_strategy_list(timeout=None)
- get_exchange_list(timeout=None)
- add_market_order(strategy_id, exchange_id, base_currency, quote_currency, side, amount, leverage=None, timeout=None)
- get_history_list(strategy_id, begin_time, end_time, timeout=None)
- add_api_key(api_key, api_secret_key, exchange_id, timeout=None)
- get_api_key_list(timeout=None)
- delete_api_key(exchange_id, timeout=None)

Each method has a `timeout` parameter that will cause a `bincentive_trader.exceptions.Timeout`
exception if no response is received in specified seconds.


