from .api_request import create_client
from .db_request import (check_machine, getAllCurrency,
                         insertCandle,insertCandles,
                         getCandles, insertImpulse,
                         deleteAllCandlesAndImpulses, getCandlesDF,
                         get_keys, insertOrder, insertCandlesBulk)
from datetime import datetime
from binance.client import Client
from threading import Thread
from .math_methods import impulse_long
import pandas as pd
import time
import os
import numpy as np
import asyncio
from binance import AsyncClient, BinanceSocketManager


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
    print("Got Impulses")

def divide_chunks(l, n):
    # looping till length l
    for i in range(0, len(l), n):
        yield l[i:i + n]

def get_start_data(self, request):
    client = create_client()
    list_Currency = getAllCurrency()

    deleteAllCandlesAndImpulses()

    listCurr = list(divide_chunks(list_Currency, 6))
    print("Start Getting Data")

    result = dict()
    threads = list()
    for part in listCurr:
        t1 = Thread(target=getCandles, args=(result,client,part, Client.KLINE_INTERVAL_1MINUTE,1, 1000))
        threads.append(t1)
        t1.start()

        t5 = Thread(target=getCandles, args=(result,client, part, Client.KLINE_INTERVAL_5MINUTE,5, 1000))
        threads.append(t5)
        t5.start()

        t15 = Thread(target=getCandles, args=(result,client, part, Client.KLINE_INTERVAL_15MINUTE,15, 1000))
        threads.append(t15)
        t15.start()

        t60 = Thread(target=getCandles, args=(result,client, part, Client.KLINE_INTERVAL_1HOUR,60, 1000))
        threads.append(t60)
        t60.start()

    for index, thread in enumerate(threads):
        thread.join()

    print("Starting Insert Data")

    insertCandlesBulk(result)

    print("Got Data")


list_order = dict()
streams = []
async def streamDepth():
    client = await AsyncClient.create()
    bm = BinanceSocketManager(client)
    # start any sockets here, i.e a trade socket
    global streams
    ms = bm.multiplex_socket(streams)
    # then start receiving messages
    async with ms as tscm:
        while True:
            try:
                res = await tscm.recv()
                global list_order
                stream = res['stream']
                # asks = [float(el[1]) for el in msg['data']['a']]
                bids_q = [float(el[1]) for el in res['data']['bids']]
                bids_p = [float(el[0]) for el in res['data']['bids']]

                if list_order[stream].size > 100:
                    aver = list_order[stream].mean()
                    # print(aver)
                    max_q = np.max(bids_q)
                    if max_q > aver * 20:
                        await insertOrder(stream.split('@')[0].upper(), "L", datetime.now(), bids_p[np.argmax(bids_q)], max_q)
                        print(f"Name - {stream.split('@')[0].upper()}.Average - {aver}. Max - price - {bids_p[np.argmax(bids_q)]} - quantity - {max_q}")

                    list_order[stream] = list_order[stream][10:]

                list_order[stream] = np.concatenate((list_order[stream], bids_q))
            except KeyError as e:
                continue


    await client.close_connection()

def startStreamBook():
    print('Stream started')

    list_Curr = getAllCurrency()
    global list_order
    for curr in list_Curr:
        stream_name = f'{curr.name}@depth5@100ms'.lower()
        streams.append(stream_name)
        list_order[stream_name] = np.array([])

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(streamDepth())


def start_machine():
    client = create_client()
    list_Currency = list(divide_chunks(getAllCurrency(), 6))
    print('Machine started')


    last_minute = datetime.now().minute
    threads = list()
    while check_machine():
        if datetime.now().minute != last_minute:
            last_minute = datetime.now().minute
            print("Get Candles")
            result = dict()
            #print("Get 1Min")
            for part in list_Currency:
                t1 = Thread(target = getCandles, args=(result,client,part, Client.KLINE_INTERVAL_1MINUTE,1, 2, True))
                threads.append(t1)
                t1.start()
                if last_minute % 5 == 0:
                    #print("Get 5Min")
                    t5 = Thread(target=getCandles, args=(result,client, part, Client.KLINE_INTERVAL_5MINUTE,5, 2, True))
                    threads.append(t5)
                    t5.start()
                if last_minute % 15 == 0:
                    #print("Get 15Min")
                    t15 = Thread(target=getCandles, args=(result,client, part, Client.KLINE_INTERVAL_15MINUTE ,15, 2, True))
                    threads.append(t15)
                    t15.start()
                if last_minute == 0:
                    t60 = Thread(target=getCandles, args=(result,client, part, Client.KLINE_INTERVAL_1HOUR, 60, 2, True))
                    threads.append(t60)
                    t60.start()

            for index, thread in enumerate(threads):
                thread.join()

            threads.clear()

            print("Starting Insert Data")

            insertCandlesBulk(result)

            print("Got Candles")

            get_impulses()



    print("End machine")

def getCandles(result, client, list_currency, interval, tf, limit, isLast = False):
    for curr in list_currency:
        candles = client.get_klines(symbol=curr.name, interval=interval, limit = limit)
        if isLast:
            result[str(curr.name) + "-" + str(tf)] = candles[-2]
        else:
            result[str(curr.name) + "-" + str(tf)] = candles
