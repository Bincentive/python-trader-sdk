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
            self.TRADER_ENDPOINT = 'https://bi-gateway-go-sit.bincentive.com'
        else:
            self.LOGIN_ENDPOINT = 'https://fs-api.bincentive.com/member/api/member/login'
            self.TRADER_ENDPOINT = 'https://bi-gateway-go-prod.bincentive.com'

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
    
    def _get(self, endpoint, timeout=None):
        return self._request('GET', endpoint, timeout)   
    
    def _delete(self, endpoint, timeout=None):
        return self._request('DELETE', endpoint, timeout)       
    
    def _put(self, endpoint, json=None, timeout=None):
        return self._request('PUT', endpoint, timeout, json=json)    

    def get_strategy_list(self, timeout=None):
        """Gets the list of approved strategies."""
        endpoint = self.TRADER_ENDPOINT + '/api/v1/user/StrategyNameList'
        r = self._get(endpoint, timeout=timeout)
        return r.json()['data']

    def get_exchange_list(self, timeout=None):
        """Gets the list of exchanges currently active."""
        endpoint = self.TRADER_ENDPOINT + '/api/v1/common/ExchangeList'
        r = self._get(endpoint, timeout=timeout)
        return r.json()['data']

    def get_history_list(self, strategy_id, startDate, endDate, timeout=None):
        """Gets the historical data of all transactions.
        :param strategy_id: int
        :param startDate: str, YYYY-MM-DD 
        :param endDate: str, YYYY-MM-DD 
        :param timeout: request timeout
        :return: history list
        """
        endpoint = self.TRADER_ENDPOINT + '/api/v1/user/OrderList?strategyId={}&startDate={}&endDate={}'.format(strategy_id, startDate, endDate)
        r = self._get(endpoint, timeout=timeout)
        return r.json()['data']

    def add_api_key(self, api_key, api_secret_key, strategyId, timeout=None):
        """Adds all the keys of each transaction."""
        endpoint = self.TRADER_ENDPOINT + '/api/v1/user/ApiKey'
        payload = {
            'apiKey': api_key,
            'secretKey': str(self.subkey.encrypt(pgpy.PGPMessage.new(api_secret_key))),
            'strategyId': strategyId,
        }
        r = self._post(endpoint, json=payload, timeout=timeout)
        return r.json()['data']

    def get_api_key_list(self, timeout=None):
        """Gets API key list.
        """
        endpoint = self.TRADER_ENDPOINT + '/api/v1/user/ApiKey'
        r = self._get(endpoint, timeout=timeout)
        return r.json()['data']

    def delete_api_key(self, strategyId, timeout=None):
        """Deletes all the keys of a transaction.
        :param strategyId: int
        :param timeout: request timeout
        :return: True if api key is deleted.
        """
        endpoint = self.TRADER_ENDPOINT + '/api/v1/user/ApiKey?strategyId={}'.format(strategyId)
        r = self._delete(endpoint, timeout=timeout)
        return r.json()['data']
    '''
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
    '''
    def get_exchange_symbol_list(self, exchange_id, timeout=None):
        """Get exchange symbol list.
        :param exchange_id: int
        :param timeout: request timeout
        :return: exchange symbol list
        """
        endpoint = self.TRADER_ENDPOINT + '/api/v1/common/SymbolList?exchangeId={}'.format(exchange_id)
        r = self._get(endpoint, timeout=timeout)
        return r.json()['data']
    '''
    def get_currency_list(self, timeout=None):
        """Get exchange symbol list.
        :param exchange_id: int
        :param timeout: request timeout
        :return: exchange symbol list
        """
        endpoint = self.TRADER_ENDPOINT + 'api/common/getCurrencyList'
        r = self._post(endpoint, timeout=timeout)
        return r.json()['data']
    '''
    def set_position(self, strategy_id, Ratio, LimitPrice, timeout=None):
        """Adds a market order for a specific strategy.
        :param strategy_id: int
        :param Ratio: float
        :param LimitPrice: float
        :return: Signal id or None if no order was created.
        """
        endpoint = self.TRADER_ENDPOINT + '/api/v1/strategy/SetPosition'
        payload = {
            'strategyId': strategy_id,
            'Ratio': Ratio,
            'LimitPrice': LimitPrice
            }
        r = self._post(endpoint, json=payload, timeout=timeout)
        if r.status_code == 200:
            return r.json()['data']['id']
        else:
            return None
