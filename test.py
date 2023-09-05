from binance.client import Client
from screener.api_request import get_keys

def create_client():
    """ create trader with keys and return it """
    api_key, secret_key = get_keys()
    print(api_key)
    return Client(api_key, secret_key)


create_client()