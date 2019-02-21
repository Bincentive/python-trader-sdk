from __future__ import unicode_literals

import tzlocal
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
        # gets subkey for encryption
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
        """Gets the list of approved strategies."""
        endpoint = self.TRADER_ENDPOINT + 'api/trader/getApprovedStrategyList'
        r = self._post(endpoint, timeout=timeout)
        return r.json()['data']

    def get_exchange_list(self, timeout=None):
        """Gets the list of exchanges currently active."""
        endpoint = self.TRADER_ENDPOINT + 'api/common/getActiveExchangeList'
        r = self._post(endpoint, timeout=timeout)
        return r.json()['data']

    def add_market_order(self, strategy_id, exchange_id, base_currency, quote_currency, side, amount,
                         leverage=1, timeout=None):
        """Adds a market order for a specific strategy."""
        :param strategy_id: int
        :param exchange_id: int
        :param base_currency: e.g., 'BTC'
        :param quote_currency: e.g., 'USDT'
        :param side: 'BUY' or 'SELL'
        :param amount: the amount to sell or buy
        :param leverage: Bitmex exchange leverage. This parameter is used only on Bitmex exchange and can be set
                         to `None` if using other exchanges.
        :param timeout: request timeout
        :return: Signal id or None if no order was created.
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
            return r.json()['data']['signalId']
        else:
            return None

    def get_history_list(self, strategy_id, begin_time, end_time, account_type='real', timeout=None):
        """Gets the historical data of all transactions.
        :param strategy_id: int
        :param begin_time: datetime object. If no tzinfo is provided, defaults to local timezone.
        :param end_time: datetime object. If no tzinfo is provided, defaults to local timezone.
        :param account_type: 'real' or 'virtual'
        :param timeout: request timeout
        :return: history list
        """
        local_tz = tzlocal.get_localzone()
        if begin_time.tzinfo is None:
            begin_time = begin_time.astimezone(local_tz)
        if end_time.tzinfo is None:
            end_time = end_time.astimezone(local_tz)

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
        """Adds all the keys of each transaction."""
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
        """Gets API key list.
        """
        endpoint = self.TRADER_ENDPOINT + 'api/member/getApiKeyList'
        r = self._post(endpoint, timeout=timeout)
        return r.json()['data']

    def delete_api_key(self, exchange_id, timeout=None):
        """Deletes all the keys of a transaction.
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

    def get_account_asset(self, strategy_id, account_type='virtual', timeout=None):
        """Get account asset.
        :param strategy_id: int
        :param account_type: 'real' or 'virtual'
        :param timeout: request timeout
        :return: account asset
        """

        endpoint = self.TRADER_ENDPOINT + 'api/trader/getAccountAsset'
        payload = {
            'strategyId': strategy_id,
            'accountType': account_type,
        }
        r = self._post(endpoint, json=payload, timeout=timeout)
        return r.json()['data']

    def get_exchange_symbol_list(self, exchange_id, timeout=None):
        """Get exchange symbol list.
        :param exchange_id: int
        :param timeout: request timeout
        :return: exchange symbol list
        """

        endpoint = self.TRADER_ENDPOINT + 'api/common/getExchangeSymbolList'
        payload = {
            "exchangeId": exchange_id,
        }
        r = self._post(endpoint, json=payload, timeout=timeout)
        return r.json()['data']

    def get_currency_list(self, timeout=None):
        """Get exchange symbol list.
        :param exchange_id: int
        :param timeout: request timeout
        :return: exchange symbol list
        """

        endpoint = self.TRADER_ENDPOINT + 'api/common/getCurrencyList'
        r = self._post(endpoint, timeout=timeout)
        return r.json()['data']

