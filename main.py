import json
from enum import Enum
from typing import List, Union, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry


class TokenIndex(Enum):
    RESERVE = 0
    BIFROST = 1
    BITCOIN = 2
    ETHEREUM = 3
    AVALANCHE = 4


class Currencies(Enum):
    RESERVED = 0
    USD = 1
    KRW = 2
    EUR = 3


CoinId = str
CoinPrice = Union[float, int]


class CoinGecko:
    __API_URL_BASE = 'https://api.coingecko.com/api/v3/'

    def __init__(self, api_base_url: str = __API_URL_BASE):
        self.api_base_url = api_base_url
        self.request_timeout = 120
        self.session = requests.Session()
        retries = Retry(total=5, backoff_factor=0.5, status_forcelist=[502, 503, 504])
        self.session.mount('http://', HTTPAdapter(max_retries=retries))

        self.__coin_list: Optional[list] = None
        self.__coin_markets = dict()

    def __request(self, url):
        # print(url)
        try:
            response = self.session.get(url, timeout=self.request_timeout)
        except requests.exceptions.RequestException:
            raise

        try:
            response.raise_for_status()
            content = json.loads(response.content.decode('utf-8'))
            return content
        except Exception as e:
            # check if json (with error message) is returned
            try:
                content = json.loads(response.content.decode('utf-8'))
                raise ValueError(content)
            # if no json
            except json.decoder.JSONDecodeError:
                pass

            raise

    def __api_url_params(self, api_url, params, api_url_has_params=False):
        if params:
            # if api_url contains already params and there is already a '?' avoid
            # adding second '?' (api_url += '&' if '?' in api_url else '?'); causes
            # issues with request parametes (usually for endpoints with required
            # arguments passed as parameters)
            api_url += '&' if api_url_has_params else '?'
            for key, value in params.items():
                if type(value) == bool:
                    value = str(value).lower()

                api_url += "{0}={1}&".format(key, value)
            api_url = api_url[:-1]
        return api_url

    def ping(self):
        api_url = "{}ping".format(self.api_base_url)
        return self.__request(api_url)

    def get_coin_list(self, refresh: bool = False) -> List[CoinId]:
        if self.__coin_list is None or refresh:
            api_url = "{}coins/list".format(self.api_base_url)
            result = self.__request(api_url)
            self.__coin_list = [info["id"] for info in result]
        return self.__coin_list

    def get_market_info(self, ids: Union[List[str], str], with_sparkline: bool = False, refresh: bool = False):
        if isinstance(ids, str):
            ids = ids.split(",")

        # caching
        not_cached_ids = ids if refresh else list(set(ids) - set(self.__coin_markets.keys()))

        # request
        req_ids = ",".join(not_cached_ids)
        api_url = "{}coins/markets".format(self.api_base_url)
        api_url = self.__api_url_params(api_url, {"ids": req_ids, "sparkline": with_sparkline, "vs_currency": "usd"})
        result = self.__request(api_url)

        # store new items
        for market in result:
            self.__coin_markets[market["id"]] = market

        return [self.__coin_markets[id] for id in ids]

    def get_price(self, ids: Union[List[str], str], refresh: bool = False):
        if isinstance(ids, str):
            ids = ids.split(",")

        # get market info
        markets = self.get_market_info(ids, refresh=refresh)

        # get prices from the markets
        prices = dict()
        for market in markets:
            prices[market["id"]] = market["current_price"]
        return prices


if __name__ == "__main__":
    api = CoinGecko()
    resp = api.get_price("bifrost")
    print(resp)
