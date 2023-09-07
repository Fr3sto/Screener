from .models import BinanceKey, Machine, Currency,Candles, CurrencyTable, Impulses
from datetime import datetime
import pandas as pd

def get_keys():
    binance_keys = BinanceKey.objects.all().first()
    return binance_keys.api, binance_keys.secret

def check_machine():
    """ return true/false if bot is working """
    return Machine.objects.all().first().is_working


def deleteAllCandles():
    Candles.objects.all().delete()
def getAllCurrency():
    return Currency.objects.all()

def getCandles(currency, tf):
    candles = Candles.objects.filter(symbol = currency, tf = tf)
    return candles

def getCandlesDF(name, tf):
    currency = Currency.objects.get(name = name)
    candles = Candles.objects.filter(symbol = currency, tf = tf).values()
    df_Candles = pd.DataFrame(candles)
    df_Candles = df_Candles.drop(['id', 'symbol_id','tf'], axis = 1)
    df_Candles['Date'] = [datetime.fromtimestamp(int(str(x)[0:10])) for x in df_Candles['Date']]
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

def insertCandle(symbol, tf, candle):
    currency = Currency.objects.get(name = symbol)
    candle = Candles.objects.create(symbol = currency,tf = tf, Date = candle[0], Open = candle[1], High = candle[2], Low = candle[3], Close = candle[4], Volume = candle[5])
    candle.save()

def insertCandles(currency, tf, listCandles):
    result_candle = []
    for candle in listCandles:
        result_candle.append(Candles(symbol = currency, tf = tf, Date = candle[0], Open = candle[1], High = candle[2], Low = candle[3], Close = candle[4], Volume = candle[5]))
    
    Candles.objects.bulk_create(result_candle)
        # if not Candles.objects.filter(symbol = currency, tf = tf, Date = candle[0]).exists():
        #     obj = Candles.objects.create(symbol = currency, tf = tf, Date = candle[0], Open = candle[1], High = candle[2], Low = candle[3], Close = candle[4], Volume = candle[5])

