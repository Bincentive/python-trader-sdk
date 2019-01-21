from __future__ import unicode_literals

import pgpy
import requests

from .exceptions import (
    ApiError,
    ApiServerError,
    AuthenticationError,
    ConnectionError,
    TraderError,
)


class TraderClient(object):
    def __init__(self, email, password, testing=True):
        if testing:
            self.LOGIN_ENDPOINT = 'https://fs-sitapi.bincentive.com/member/api/member/login'
            self.TRADER_ENDPOINT = 'https://qdapps-sitapi.bincentive.com/'
        else:
            self.LOGIN_ENDPOINT = 'https://fs-api.bincentive.com/member/api/member/login'
            self.TRADER_ENDPOINT = 'https://qdapps-proapi.bincentive.com/'

        self.session = requests.Session()
        self.session.headers = {
            'User-Agent': 'bincentive-python-sdk',
            'Accept-Language': ''
        }

        payload = {
            'email': email,
            'password': password,
            'source': 1,
        }
        r = self.session.post(self.LOGIN_ENDPOINT, json=payload, timeout=5)
        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError:
            raise AuthenticationError('Invalid email or password')

        self.session.headers.update({
            'Authorization': 'Bearer {}'.format(r.json()['data']['token']),
        })

        self.pubkey, _ = pgpy.PGPKey.from_blob(r.json()['data']['publicKey'])
        # get subkey for encryption
        for _, v in self.pubkey.subkeys.items():
            self.subkey = v
            break

    def _request(self, method, endpoint, timeout, *args, **kwargs):
        try:
            r = self.session.request(method, endpoint, timeout=timeout, *args, **kwargs)
        except requests.exceptions.Timeout:
            raise TimeoutError()
        except requests.exceptions.ConnectionError:
            raise ConnectionError()

        if r.status_code == 450:
            raise ApiError(r.json()['message'])
        elif r.status_code == 500:
            raise ApiServerError()
        elif r.status_code != 200:
            raise TraderError()

        if r.status_code == 200:
            return r

    def _post(self, endpoint, json=None, timeout=None):
        return self._request('POST', endpoint, timeout, json=json)

    def get_strategy_list(self, timeout=None):
        endpoint = self.TRADER_ENDPOINT + 'api/trader/getApprovedStrategyList'
        r = self._post(endpoint, timeout=timeout)
        return r.json()['data']

    def get_exchange_list(self, timeout=None):
        """Get a list of exchange information."""
        endpoint = self.TRADER_ENDPOINT + 'api/common/getActiveExchangeList'
        r = self._post(endpoint, timeout=timeout)
        return r.json()['data']

    def add_market_order(self, strategy_id, exchange_id, base_currency, quote_currency, side, amount,
                         leverage=None, timeout=None):
        """Add a market order for a specific strategy.
        :param strategy_id: int
        :param exchange_id: int
        :param base_currency: e.g., 'BTC'
        :param quote_currency: e.g., 'USDT'
        :param side: 'BUY' or 'SELL'
        :param amount: the amount to sell or buy
        :param leverage: bitmex exchange leverage
        :param timeout: request timeout
        :return: Order number or None if no order is created.
        """
        endpoint = self.TRADER_ENDPOINT + 'api/order/addOrder'
        payload = {
            'strategyId': strategy_id,
            'exchangeId': exchange_id,
            'baseCurrency': base_currency,
            'quoteCurrency': quote_currency,
            'orderSide': side,
            'unit': amount,
            'leverage': leverage,
            'orderType': 'MARKET',
        }
        r = self._post(endpoint, json=payload, timeout=timeout)
        if r.status_code == 200:
            return r.json()['data']['orderId']
        else:
            return None

    def get_history_list(self, strategy_id, begin_time, end_time, account_type='real', timeout=None):
        """Get order history list.
        :param strategy_id: int
        :param begin_time: datetime object
        :param end_time: datetime object
        :param account_type: 'real' or 'virtual'
        :param timeout: request timeout
        :return: history list
        """
        convert_start_time = begin_time.isoformat()
        convert_end_time = end_time.isoformat()
        endpoint = self.TRADER_ENDPOINT + 'api/order/getHistoryList'
        payload = {
            'strategyId': strategy_id,
            'beginTime': convert_start_time,
            'endTime': convert_end_time,
            'accountType': account_type,
        }
        r = self._post(endpoint, json=payload, timeout=timeout)
        return r.json()['data']

    def add_api_key(self, api_key, api_secret_key, exchange_id, timeout=None):
        """Return True if successfully added api key."""
        endpoint = self.TRADER_ENDPOINT + 'api/member/addApiKey'
        payload = {
            'apiKey': api_key,
            'secretKey': str(self.subkey.encrypt(pgpy.PGPMessage.new(api_secret_key))),
            'exchangeId': exchange_id,
            'apiNickname': '',
            'fixApiAssign': True,
        }
        self._post(endpoint, json=payload, timeout=timeout)
        return True

    def get_api_key_list(self, timeout=None):
        """Get import api key list.
        """
        endpoint = self.TRADER_ENDPOINT + 'api/member/getApiKeyList'
        r = self._post(endpoint, timeout=timeout)
        return r.json()['data']

    def delete_api_key(self, exchange_id, timeout=None):
        """Delete exchange api key.
        :param exchange_id: int
        :param timeout: request timeout
        :return: True if api key is deleted.
        """
        endpoint = self.TRADER_ENDPOINT + 'api/member/deleteApiKey'
        payload = {
            'exchangeId': exchange_id
        }
        self._post(endpoint, json=payload, timeout=timeout)
        return True
