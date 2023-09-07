from binance.client import Client
from binance import ThreadedWebsocketManager
from .db_request import get_keys

def create_client():
    """ create trader with keys and return it """
    api_key, secret_key = get_keys()
    return Client(api_key, secret_key)