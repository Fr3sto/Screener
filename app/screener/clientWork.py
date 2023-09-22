from .db_request import (getAllCurrency,
                         insertCandle,insertCandles,
                         getCandles, insertImpulse,
                         deleteAllCandlesAndImpulses, getCandlesDF,
                         get_keys, insertOrder, insertCandlesBulk,deleteIncorrectCurr,insertOrdersRealTimeOrUpdate,deleteOrdersRealTime,deleteAllOrdersRT)
from datetime import datetime
from threading import Thread,Timer
from .math_methods import impulse_long
import numpy as np
import time
import ccxt

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
    ex = ccxt.binance()

    list_Currency = getAllCurrency()

    deleteAllCandlesAndImpulses()

    listCurr = list(split(list_Currency, 3))
    print("Start Getting Data")


    partI = 0
    for part in listCurr:
        result = dict()
        threads = []
        t1 = Thread(target=getCandles, args=(result,ex,part, '1m',1, 500))
        threads.append(t1)

        t5 = Thread(target=getCandles, args=(result,ex, part, '5m',5, 500))
        threads.append(t5)

        t15 = Thread(target=getCandles, args=(result,ex, part, '15m',15, 500))
        threads.append(t15)

        t30 = Thread(target=getCandles, args=(result, ex, part, '30m', 30, 500))
        threads.append(t30)

        t60 = Thread(target=getCandles, args=(result,ex, part, '1h',60, 500))
        threads.append(t60)

        t120 = Thread(target=getCandles, args=(result, ex, part, '2h', 120, 500))
        threads.append(t120)

        t240 = Thread(target=getCandles, args=(result, ex, part, '4h', 240, 500))
        threads.append(t240)

        for x in threads:
            x.start()

        for x in threads:
            x.join()


        insertCandlesBulk(result)

        print('End part ',partI)
        partI += 1

    print("Got Data")





def split(a, n):
    k, m = divmod(len(a), n)
    return (a[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(n))

timers = []

class RepeatTimer(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)

good_orders = dict()
typeOrder = ['bids','asks']

def getPartOfBook(part, ex):
    for curr in part:
        symbol = curr.name
        try:
            order_book = ex.fetch_order_book(symbol + '/USDT', 30)
            for type in typeOrder:
                top_orders = np.array(order_book[type])
                aver_order = top_orders[top_orders[:, 1].argsort()][15][1]  # Sort and aver bids
                max_orders = top_orders[top_orders[:, 1] > aver_order * 10]  # Bids more then aver * 5
                if max_orders.size != 0:
                    if good_orders[type][symbol]:
                        keys = np.fromiter(good_orders[type][symbol].keys(), dtype=float)
                        diff = np.setdiff1d(keys, max_orders[0, :])

                        for el in diff:
                            if good_orders[type][symbol][el]['countSec'] >= 120:
                                print(f"Insert Big Order {symbol} Time {good_orders[type][symbol][el]['countSec']} sec")
                                insertOrder(symbol, type, good_orders[type][symbol][el]['dateStart'], good_orders[type][symbol][el]['dateEnd'],
                                el, good_orders[type][symbol][el]['quantity'], good_orders[type][symbol][el]['pow'])

                            deleteOrdersRealTime(symbol, type)
                            del good_orders[type][symbol][el]
                    for el in max_orders:
                        if el[0] in good_orders[type][symbol]:
                            lastTime = good_orders[type][symbol][el[0]]['countSec']
                            newTime = (datetime.now() - good_orders[type][symbol][el[0]]['dateStart']).seconds
                            good_orders[type][symbol][el[0]]['countSec'] = newTime
                            good_orders[type][symbol][el[0]]['quantity'] = el[1]
                            good_orders[type][symbol][el[0]]['dateEnd'] = datetime.now()
                            if newTime % 60 < 10 and lastTime % 60 > 50:
                                print(f"BIG ORDER ADD REAL-TIME Symbol {symbol} type {type}")
                                insertOrdersRealTimeOrUpdate(symbol, type, good_orders[type][symbol][el[0]]['dateStart'],
                                    good_orders[type][symbol][el[0]]['dateEnd'],
                                    el[0], good_orders[type][symbol][el[0]]['quantity'],
                                    good_orders[type][symbol][el[0]]['pow'])
                        else:
                            good_orders[type][symbol][el[0]] = {'countSec': 0, 'quantity': el[1],
                                                                'dateStart': datetime.now(),
                                                                'pow': np.round(el[1] / aver_order, 1)}
        except Exception as e:
            print(e)


def streaming_order(ex):
    print('Stream Order started')

    deleteAllOrdersRT()
    print('Old ordersRT deleted')

    list_Currency = list(split(getAllCurrency(), 10))

    for type in typeOrder:
        good_orders[type] = dict()
        for curr in getAllCurrency():
            good_orders[type][curr.name] = dict()

    for part in list_Currency:
        timer = RepeatTimer(5, getPartOfBook, args=(part, ex))
        timers.append(timer)
        timer.start()

def start_streams():
    ex = ccxt.binance()

    streaming_order(ex)

    th = Thread(target=streaming_kline, args=(ex,))
    th.start()


def streaming_kline(ex):
    print('Stream Kline started')

    list_Currency = getAllCurrency()

    last_minute = datetime.now().minute

    while True:
        if datetime.now().minute != last_minute:
            last_minute = datetime.now().minute
            last_hour = datetime.now().hour
            print("Get Candles")
            result = dict()
            threads = list()
            #print("Get 1Min")
            t1 = Thread(target=getCandles, args=(result, ex, list_Currency, '1m', 1, 2, True))
            threads.append(t1)
            if last_minute % 5 == 0:
                # print("Get 5Min")
                t5 = Thread(target=getCandles, args=(result, ex, list_Currency, '5m', 5, 2, True))
                threads.append(t5)
            if last_minute % 15 == 0:
                # print("Get 15Min")
                t15 = Thread(target=getCandles,
                             args=(result, ex, list_Currency, '15m', 15, 2, True))
                threads.append(t15)
            if last_minute % 30 == 0:
                # print("Get 15Min")
                t30 = Thread(target=getCandles,
                             args=(result, ex, list_Currency, '30m', 30, 2, True))
                threads.append(t30)
            if last_minute == 0:
                t60 = Thread(target=getCandles, args=(result, ex, list_Currency, '1h', 60, 2, True))
                threads.append(t60)
            if last_minute == 0 and (last_hour + 1) % 2 == 0:
                t120 = Thread(target=getCandles, args=(result, ex, list_Currency, '2h', 120, 2, True))
                threads.append(t120)
            if last_minute == 0 and (last_hour + 1) % 4 == 0:
                t240 = Thread(target=getCandles, args=(result, ex, list_Currency, '4h', 240, 2, True))
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

def getCandles(result, ex : ccxt.binance, list_currency, interval, tf, limit, isLast = False):
    for curr in list_currency:
        try:
            candles = ex.fetch_ohlcv(curr.name + '/USDT', limit = limit, timeframe=interval)
            if isLast:
                result[str(curr.name) + "-" + str(tf)] = candles[-2]
            else:
                #insertCandles(curr,tf,candles)
                result[str(curr.name) + "-" + str(tf)] = candles
        except Exception as e:
            print(e)
