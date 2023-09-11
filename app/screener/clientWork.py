from .api_request import create_client
from .db_request import check_machine, getAllCurrency, insertCandle,insertCandles, getCandles, insertImpulse, deleteAllCandles
from datetime import datetime
from binance.client import Client
from threading import Thread
from .math_methods import impulse_long
import pandas as pd
import time
import os

def get_start_data(self, request):
    client = create_client()
    list_Currency = getAllCurrency()

    deleteAllCandles()

    #ДОБАВИТЬ ВСЕ СТАРЫЕ СВЕЧИ В БАЗУ ДАННЫХ
    tStart = time.time()
    countDone = 0
    clear = lambda: os.system('cls')
    for currency in list_Currency:
        print("Instrument ", currency.name)
        print('get historical TF 1')
        list_Candles = client.get_klines(symbol=currency.name, interval=Client.KLINE_INTERVAL_1MINUTE, limit = 1000)
        print('insert historical TF 1')
        insertCandles(currency, 1, list_Candles)
        print('get historical TF 5')
        list_Candles = client.get_klines(symbol=currency.name, interval=Client.KLINE_INTERVAL_5MINUTE, limit = 1000)
        print('insert historical TF 5')
        insertCandles(currency, 5, list_Candles)
        print('get historical TF 15')
        list_Candles = client.get_klines(symbol=currency.name, interval=Client.KLINE_INTERVAL_15MINUTE, limit = 1000)
        print('insert historical TF 15')
        insertCandles(currency, 15, list_Candles)
        clear()
        countDone += 1
        tCountDone = time.time()
        eachCount = (tCountDone - tStart) / countDone
        needTime = (len(list_Currency) - countDone) * eachCount
        print('Need Sec - ', convertSecToMin(int(needTime)))
        print('Done ',countDone,'/',len(list_Currency))
        self.message_user(request, 'Done ',countDone,'/',len(list_Currency))

def convertSecToMin(seconds):
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
     
    return "%d:%02d:%02d" % (hour, minutes, seconds)


def start_machine():
    client = create_client()
    list_Currency = getAllCurrency()

    print('Machine started')

    

    t1 = Thread(target=checkMin, args=(client,list_Currency))
    t1.start()
    
    pass

def checkMin(client, list_Currency):
    last_minute = datetime.now().minute
    while check_machine():
        if datetime.now().minute != last_minute: # новая минута
            last_minute = datetime.now().minute
            # нужно проверка каждого тф
            t1 = Thread(target=get1MinKline, args=(client, list_Currency))
            t1.start()
            if last_minute % 5 == 0:
                t5 = Thread(target=get5MinKline, args=(client, list_Currency))
                t5.start()
            if last_minute % 15 == 0:
                t15 = Thread(target = get15MinKline, args=(client, list_Currency))
                t15.start()


def get1MinKline(client, list_Currency):
    print('get 1 min')
    for currency in list_Currency:
        candle = client.get_klines(symbol=currency.name, interval=Client.KLINE_INTERVAL_1MINUTE, limit = 2)[-2]
        insertCandle(currency.name, 1, candle)
    print('got 1 min')

    print('get Impulse Long 1')
    
    for currency in list_Currency:
        Candles = getCandles(currency, 1).values()
        df_Candles = pd.DataFrame(Candles)
        df_Candles = df_Candles.drop(['id', 'symbol_id','tf'], axis = 1)
        df_Candles['Date'] = [datetime.fromtimestamp(int(str(x)[0:10])) for x in df_Candles['Date']]
        df_Candles = df_Candles.sort_values(by=['Date'])
        impulse = impulse_long(df_Candles, 1)
        insertImpulse(currency, 'L', 1, impulse)
        #print('Symbol - ',currency.name,'Date Impulse - ', date_long)
    print('got Impulse Long 1')

def get5MinKline(client, list_Currency):
    print('get 5 min')
    for currency in list_Currency:
        candle = client.get_klines(symbol=currency.name, interval=Client.KLINE_INTERVAL_5MINUTE, limit = 2)[-2]
        insertCandle(currency.name, 5, candle)
    print('got 5 min')

    print('get Impulse Long 5')
    
    for currency in list_Currency:
        Candles = getCandles(currency, 5).values()
        df_Candles = pd.DataFrame(Candles)
        df_Candles = df_Candles.drop(['id', 'symbol_id','tf'], axis = 1)
        df_Candles['Date'] = [datetime.fromtimestamp(int(str(x)[0:10])) for x in df_Candles['Date']]
        df_Candles = df_Candles.sort_values(by=['Date'])
        impulse = impulse_long(df_Candles, 5)
        insertImpulse(currency, 'L', 5, impulse)
    print('got Impulse Long 5')
    
    

def get15MinKline(client, list_Currency):
    print('get 15 min')
    for currency in list_Currency:
        candle = client.get_klines(symbol=currency.name, interval=Client.KLINE_INTERVAL_15MINUTE, limit = 2)[-2]
        insertCandle(currency.name, 15, candle)
    print('got 15 min')

    print('get Impulse Long 15')
    
    for currency in list_Currency:
        Candles = getCandles(currency, 15).values()
        df_Candles = pd.DataFrame(Candles)
        df_Candles = df_Candles.drop(['id', 'symbol_id','tf'], axis = 1)
        df_Candles['Date'] = [datetime.fromtimestamp(int(str(x)[0:10])) for x in df_Candles['Date']]
        df_Candles = df_Candles.sort_values(by=['Date'])
        impulse = impulse_long(df_Candles, 15)
        insertImpulse(currency, 'L', 15, impulse)
    print('got Impulse Long 15')