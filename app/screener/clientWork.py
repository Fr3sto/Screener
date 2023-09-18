from .api_request import create_client
from .db_request import (getAllCurrency,
                         insertCandle,insertCandles,
                         getCandles, insertImpulse,
                         deleteAllCandlesAndImpulses, getCandlesDF,
                         get_keys, insertOrder, insertCandlesBulk,deleteIncorrectCurr)
from datetime import datetime
from binance.client import Client
from binance import AsyncClient, DepthCacheManager
from threading import Thread
from .math_methods import impulse_long
import pandas as pd
import os
import numpy as np
import asyncio
from binance import  ThreadedDepthCacheManager
import sys
import time

def deleteIncorrectCurrencies():
    list_Currency = getAllCurrency()

    df_Curr = pd.DataFrame(list_Currency.values())

    client = create_client()
    info = client.get_all_tickers()

    list_symbols = np.array([])
    for x in info:
        list_symbols = np.append(list_symbols, x['symbol'])

    my_symbols = np.array(df_Curr['name'])
    diff = np.setdiff1d(my_symbols, list_symbols)
    deleteIncorrectCurr(diff)

def get_impulses():
    print("Get Impulses")
    list_Currency = getAllCurrency()

    for currency in list_Currency:
        df_Imp = getCandlesDF(currency, 5)
        impulse = impulse_long(df_Imp)
        insertImpulse(currency, 'L', 1, impulse)

        df_Imp = getCandlesDF(currency, 15)
        impulse = impulse_long(df_Imp)
        insertImpulse(currency, 'L', 5, impulse)

        df_Imp = getCandlesDF(currency, 60)
        impulse = impulse_long(df_Imp)
        insertImpulse(currency, 'L', 15, impulse)

        df_Imp = getCandlesDF(currency, 120)
        impulse = impulse_long(df_Imp)
        insertImpulse(currency, 'L', 30, impulse)

        df_Imp = getCandlesDF(currency, 240)
        impulse = impulse_long(df_Imp)
        insertImpulse(currency, 'L', 60, impulse)


    print("Got Impulses")

def split(a, n):
    k, m = divmod(len(a), n)
    return (a[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(n))

def get_start_data(self, request):
    client = create_client()
    list_Currency = getAllCurrency()

    deleteAllCandlesAndImpulses()

    listCurr = list(split(list_Currency, 3))
    print("Start Getting Data")


    partI = 0
    for part in listCurr:
        print('start Part ', part)
        result = dict()
        threads = []
        t1 = Thread(target=getCandles, args=(result,client,part, Client.KLINE_INTERVAL_1MINUTE,1, 500))
        threads.append(t1)

        t5 = Thread(target=getCandles, args=(result,client, part, Client.KLINE_INTERVAL_5MINUTE,5, 500))
        threads.append(t5)

        t15 = Thread(target=getCandles, args=(result,client, part, Client.KLINE_INTERVAL_15MINUTE,15, 500))
        threads.append(t15)

        t30 = Thread(target=getCandles, args=(result, client, part, Client.KLINE_INTERVAL_30MINUTE, 30, 500))
        threads.append(t30)

        t60 = Thread(target=getCandles, args=(result,client, part, Client.KLINE_INTERVAL_1HOUR,60, 500))
        threads.append(t60)

        t120 = Thread(target=getCandles, args=(result, client, part, Client.KLINE_INTERVAL_2HOUR, 120, 500))
        threads.append(t120)

        t240 = Thread(target=getCandles, args=(result, client, part, Client.KLINE_INTERVAL_4HOUR, 240, 500))
        threads.append(t240)

        for x in threads:
            x.start()

        for x in threads:
            x.join()


        insertCandlesBulk(result)

        print('End part ',partI)
        partI += 1



    # print('Start inserting data')
    #
    # insertCandlesBulk(result)

    print("Got Data")



good_orders = dict()


def handle_depth_cache(depth_cache):
    symbol = depth_cache.symbol
    try:
        top_bids = np.array(depth_cache.get_bids()[:30])  # Top 30 bids
        aver_bid = top_bids[top_bids[:, 1].argsort()][15][1]  # Sort and aver bids
        max_bids = top_bids[top_bids[:, 1] > aver_bid * 10]  # Bids more then aver * 5
        if max_bids.size != 0:
            if good_orders[symbol]:
                keys = np.fromiter(good_orders[symbol].keys(), dtype=float)
                diff = np.setdiff1d(keys, max_bids[0, :])

                for el in diff:
                    if good_orders[symbol][el]['countSec'] > 30:
                        print(
                            f'Inserting Symbol {symbol}. Price {el}, Quantity {good_orders[symbol][el]["quantity"]}, Pow - {good_orders[symbol][el]["pow"]} Time Live {good_orders[symbol][el]["countSec"]}sec')
                        th1 = Thread(target=insertOrder, args=(symbol,"L", good_orders[symbol][el]['dateStart'],good_orders[symbol][el]['dateEnd'],el,good_orders[symbol][el]['quantity'], good_orders[symbol][el]['pow']))
                        th1.start()
                        th1.join()
                    del good_orders[symbol][el]
            for el in max_bids:
                if el[0] in good_orders[symbol]:
                    good_orders[symbol][el[0]]['countSec'] = (datetime.now() - good_orders[symbol][el[0]]['dateStart']).seconds
                    good_orders[symbol][el[0]]['quantity'] = el[1]
                    good_orders[symbol][el[0]]['dateEnd'] = datetime.now()
                    #print(
                    #    f'Symbol {symbol}. Price {el[0]}, Quantity {good_orders[symbol][el[0]]["quantity"]}, Pow - {good_orders[symbol][el[0]]["pow"]} Time Live {good_orders[symbol][el[0]]["countSec"]}sec')
                else:
                    good_orders[symbol][el[0]] = {'countSec': 0, 'quantity': el[1], 'dateStart': datetime.now(),
                                                  'pow': np.round(el[1] / aver_bid, 1)}
    except Exception as e:
        pass




def streaming_book():
    try:
        print('Stream Book started')

        dcm = ThreadedDepthCacheManager()
        # start is required to initialise its internal loop
        dcm.start()

        global good_orders
        list_Curr = getAllCurrency()
        for curr in list_Curr:
            dcm.start_depth_cache(handle_depth_cache, symbol=curr.name)
            good_orders[curr.name] = dict()

        dcm.join()
    except Exception as e:
        print('EXCEPTION')
        print(e)


def start_streams():
    th = Thread(target=streaming_book)
    th.start()

    th = Thread(target=streaming_kline)
    th.start()


def streaming_kline():
    client = create_client()
    list_Currency = getAllCurrency()
    print('Stream Kline started')


    last_minute = datetime.now().minute

    while True:
        if datetime.now().minute != last_minute:
            last_minute = datetime.now().minute
            last_hour = datetime.now().hour
            print("Get Candles")
            result = dict()
            threads = list()
            #print("Get 1Min")
            t1 = Thread(target=getCandles, args=(result, client, list_Currency, Client.KLINE_INTERVAL_1MINUTE, 1, 2, True))
            threads.append(t1)
            if last_minute % 5 == 0:
                # print("Get 5Min")
                t5 = Thread(target=getCandles, args=(result, client, list_Currency, Client.KLINE_INTERVAL_5MINUTE, 5, 2, True))
                threads.append(t5)
            if last_minute % 15 == 0:
                # print("Get 15Min")
                t15 = Thread(target=getCandles,
                             args=(result, client, list_Currency, Client.KLINE_INTERVAL_15MINUTE, 15, 2, True))
                threads.append(t15)
            if last_minute % 30 == 0:
                # print("Get 15Min")
                t30 = Thread(target=getCandles,
                             args=(result, client, list_Currency, Client.KLINE_INTERVAL_30MINUTE, 30, 2, True))
                threads.append(t30)
            if last_minute == 0:
                t60 = Thread(target=getCandles, args=(result, client, list_Currency, Client.KLINE_INTERVAL_1HOUR, 60, 2, True))
                threads.append(t60)
            if last_minute == 0 and last_hour % 2 == 0:
                t120 = Thread(target=getCandles, args=(result, client, list_Currency, Client.KLINE_INTERVAL_2HOUR, 120, 2, True))
                threads.append(t120)
            if last_minute == 0 and last_hour % 4 == 0:
                t240 = Thread(target=getCandles, args=(result, client, list_Currency, Client.KLINE_INTERVAL_4HOUR, 240, 2, True))
                threads.append(t240)

            for x in threads:
                x.start()

            for x in threads:
                x.join()

            print("Starting Insert Data")

            insertCandlesBulk(result)

            print("Got Candles")

            get_impulses()

        time.sleep(1)



    print("End machine")

def getCandles(result, client, list_currency, interval, tf, limit, isLast = False):
    for curr in list_currency:
        try:
            candles = client.get_klines(symbol=curr.name, interval=interval, limit = limit)
            if isLast:
                result[str(curr.name) + "-" + str(tf)] = candles[-2]
            else:
                #insertCandles(curr,tf,candles)
                result[str(curr.name) + "-" + str(tf)] = candles
        except Exception as e:
            print(e)
