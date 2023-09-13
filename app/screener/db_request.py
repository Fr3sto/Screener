from .models import BinanceKey, Machine, Currency,Candles, CurrencyTable, Impulses, BigOrders
from datetime import datetime
import pandas as pd
import pytz
from pytz import timezone
from asgiref.sync import sync_to_async

tz = pytz.timezone('Europe/Moscow')
def get_keys():
    binance_keys = BinanceKey.objects.all().first()
    return binance_keys.api, binance_keys.secret

def check_machine():
    """ return true/false if bot is working """
    return Machine.objects.all().first().is_working


def deleteAllCandlesAndImpulses():
    Candles.objects.all().delete()
    Impulses.objects.all().delete()
def getAllCurrency():
    return Currency.objects.all()

def getCandles(currency, tf):
    candles = Candles.objects.filter(symbol = currency, tf = tf)
    return candles

def getCandlesDF(currency, tf):
    candles = Candles.objects.filter(symbol = currency, tf = tf).values()
    df_Candles = pd.DataFrame(candles)
    df_Candles = df_Candles.drop(['id', 'symbol_id','tf'], axis = 1)
    df_Candles = df_Candles.sort_values(by=['Date'])
    return df_Candles

def insertImpulse(currency, type, tf, list):
    if not Impulses.objects.filter(symbol = currency, tf = tf, type = type).exists():
        impulse = Impulses.objects.create(symbol = currency,tf = tf, type = type, priceStart = list[0], dateStart = list[1], priceEnd = list[2], dateEnd = list[3], isOpen = list[5])
        impulse.save()
    else:
         impulse = Impulses.objects.get(symbol = currency, tf = tf, type = type)
         impulse.priceStart = list[0]
         impulse.dateStart = list[1]
         impulse.priceEnd = list[2]
         impulse.dateEnd = list[3]
         impulse.isOpen = list[5]
         impulse.save()

def insertDate(currency, value, tf):
        curr_table = CurrencyTable.objects.get(symbol = currency)
        if tf == 1:
            curr_table.tf1 = value
        elif tf == 5:
            curr_table.tf5 = value
        elif tf == 15:
            curr_table.tf15 = value
        curr_table.save()


@sync_to_async
def insertOrder(symbol, type, date, price, quantity):
    curr = Currency.objects.get(name = symbol)
    order = BigOrders.objects.create(symbol = curr, type = type,date = date, price = price, quantity = quantity)
    order.save()

def getOrders(currency):
    return BigOrders.objects.filter(symbol = currency)

def insertCandle(currency, tf, candle):
    date = datetime.fromtimestamp(int(str(candle[0])[0:10]))
    candle = Candles.objects.create(symbol = currency,tf = tf, Date = date, Open = candle[1], High = candle[2], Low = candle[3], Close = candle[4], Volume = candle[5])
    candle.save()


def insertCandles(symbol, tf, listCandles):
    currency = Currency.objects.get(name = symbol)
    result_candle = []
    for candle in listCandles:
        date = datetime.fromtimestamp(int(str(candle[0])[0:10]))
        result_candle.append(Candles(symbol = currency, tf = tf, Date = date, Open = candle[1], High = candle[2], Low = candle[3], Close = candle[4], Volume = candle[5]))
    
    Candles.objects.bulk_create(result_candle)

def insertCandlesBulk(resultCandles):
    list_candles = []
    for key, value in resultCandles.items():
        symbol = key.split('-')[0]
        currency = Currency.objects.get(name = symbol)
        tf = key.split('-')[1]

        for candle in value:
            date = datetime.fromtimestamp(int(str(candle[0])[0:10]))
            list_candles.append(Candles(symbol = currency, tf = tf, Date = date, Open = candle[1], High = candle[2], Low = candle[3], Close = candle[4], Volume = candle[5]))

    Candles.objects.bulk_create(list_candles)