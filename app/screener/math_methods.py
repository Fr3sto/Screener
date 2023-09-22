
import datetime
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from .models import  Impulses, Currency, Candles, BigOrders,OrdersRealtime
from .db_request import getCandlesDF, getOrders

def atr(df, period):
    df['Max'] =  df['High'].rolling(period).max().shift().fillna(0)
    df['Min'] = df['Low'].rolling(period).min().shift().fillna(0)

    df['Atr'] = df['Max'] - df['Min']

    return df.drop(columns = ['Max','Min'])


def impulse_short(df_HighTF, pulse_percent=0.2):
    impulses = []
    result = []
    impulse = []
    rollback = []
    percent_return = 0.3
    percent_not_change = 0.3

    df_HighTF = atr(df_HighTF, period=300)
    list = df_HighTF.values.tolist()

    isDown = False
    min = 0
    max = 0
    height = 0
    curr_diff = 0
    count_trend_bar = 0
    count_after_trend_bar = 0

    priceStart = 0
    dateStart = datetime.datetime.now()
    priceEnd = 0
    dateEnd = datetime.datetime.now()
    iEnd = 0

    for i, x in enumerate(list):
        if isDown:
            if list[i][3] < min:
                min = list[i][3]
                height = max - min
                count_trend_bar += 1
                count_after_trend_bar = 0
                impulse.append(1)
                if len(rollback) != 0:
                    impulse.extend([1] * len(rollback))
                    rollback = []
                priceEnd = list[i][3]
                dateEnd = list[i][5]
            else:
                count_after_trend_bar += 1
                curr_diff = list[i][3] - min
                rollback.append(1)
                if (curr_diff > height * percent_return):
                    isDown = False

                    if (height > pulse_percent * list[i][6] and count_trend_bar > 1 and list[i][6] != 0):
                        impulses.append([priceStart, dateStart, priceEnd, dateEnd, i, 0])
                        result.extend(impulse)
                        result.extend([0] * len(rollback))
                    else:
                        result.extend([0] * len(impulse))
                        result.extend([0] * len(rollback))
                else:
                    count_stop_bar = 0

                    if (count_trend_bar < 10):
                        count_stop_bar = 4
                    else:
                        count_stop_bar = int(count_trend_bar * percent_not_change)

                    if (count_after_trend_bar > count_stop_bar):
                        isDown = False

                        if (height > pulse_percent * list[i][6] and count_trend_bar > 1 and list[i][6] != 0):
                            impulses.append([priceStart, dateStart, priceEnd, dateEnd, i, 0])
                            result.extend(impulse)
                            result.extend([0] * len(rollback))
                        else:
                            result.extend([0] * len(impulse))
                            result.extend([0] * len(rollback))
        else:
            if (list[i][3] < list[i - 1][3]):
                isDown = True
                min = list[i][0]
                max = list[i][3]
                height = max - min
                count_trend_bar = 1
                count_after_trend_bar = 0
                impulse = [1]
                rollback = []
                priceStart = list[i][0]
                dateStart = list[i][5]
            else:
                result.append(0)

    result.extend([0] * (df_HighTF.shape[0] - len(result)))
    df_HighTF['Impulse Short'] = result

    res_df = df_HighTF[df_HighTF['Impulse Short'] == 1]
    if res_df.empty:
        return [0, datetime.datetime.now(), 0, datetime.datetime.now(), 0, 0]
    else:
        impulses[-1][5] = True
        minPulse = float(impulses[-1][2])
        maxPulse = float(impulses[-1][0])
        for i in range(impulses[-1][4], len(result)):
            if list[i][3] < minPulse or list[i][3] > minPulse + (maxPulse - minPulse) * 0.5:
                impulses[-1][5] = False
                return impulses[-1]
        return impulses[-1]

def impulse_long(df_HighTF, pulse_percent = 0.2):

    impulses = []
    result = []
    impulse = []
    rollback = []
    percent_return = 0.3
    percent_not_change = 0.3


    df_HighTF = atr(df_HighTF, period = 300)
    list = df_HighTF.values.tolist()

    isUp = False
    min = 0
    max = 0
    height = 0
    curr_diff = 0
    count_trend_bar = 0
    count_after_trend_bar = 0

    priceStart = 0
    dateStart = datetime.datetime.now()
    priceEnd = 0
    dateEnd = datetime.datetime.now()
    iEnd = 0

    for i, x in enumerate(list):
        if isUp:
            if list[i][3] > max:
                max = list[i][3]
                height = max - min
                count_trend_bar += 1
                count_after_trend_bar = 0
                impulse.append(1)
                if len(rollback) != 0:
                    impulse.extend([1] * len(rollback))
                    rollback = []
                priceEnd = list[i][3]
                dateEnd = list[i][5]
            else:
                count_after_trend_bar += 1
                curr_diff = max - list[i][3]
                rollback.append(1)
                if(curr_diff > height * percent_return):
                    isUp = False

                    if(height > pulse_percent * list[i][6] and count_trend_bar > 1 and list[i][6] != 0):
                        impulses.append([priceStart, dateStart, priceEnd, dateEnd, i, 0])
                        result.extend(impulse)
                        result.extend([0] * len(rollback))
                    else:
                        result.extend([0] * len(impulse))
                        result.extend([0] * len(rollback))
                else:
                    count_stop_bar = 0

                    if(count_trend_bar < 10):
                        count_stop_bar = 4
                    else:
                        count_stop_bar = int(count_trend_bar * percent_not_change)
                    
                    if(count_after_trend_bar > count_stop_bar):
                        isUp = False

                        if(height > pulse_percent * list[i][6] and count_trend_bar > 1 and list[i][6] != 0):
                            impulses.append([priceStart, dateStart, priceEnd, dateEnd,i,0])
                            result.extend(impulse)
                            result.extend([0] * len(rollback))
                        else:
                            result.extend([0] * len(impulse))
                            result.extend([0] * len(rollback))
        else:
            if(list[i][3] > list[i-1][3]):
                isUp = True
                min = list[i][0]
                max = list[i][3]
                height = max - min
                count_trend_bar = 1
                count_after_trend_bar = 0
                impulse = [1]
                rollback = []
                priceStart = list[i][0]
                dateStart = list[i][5]
            else:
                result.append(0)

    result.extend([0] * (df_HighTF.shape[0] - len(result)))
    df_HighTF['Impulse Long'] = result

    res_df = df_HighTF[df_HighTF['Impulse Long'] == 1]
    if res_df.empty:
        return [0, datetime.datetime.now(), 0,datetime.datetime.now(), 0, 0]
    else:
        impulses[-1][5] = True
        minPulse = float(impulses[-1][0])
        maxPulse = float(impulses[-1][2])
        for i in range(impulses[-1][4], len(result)):
            if list[i][3] > maxPulse or list[i][3] < maxPulse - (maxPulse - minPulse)* 0.5:
                impulses[-1][5] = False
                return impulses[-1]
        return impulses[-1]
def getChartWithImpulse(df, impulse, tf):
    #fig = px.line(df, x = 'Date', y = 'Close')

    fig = go.Figure(data=[go.Candlestick(x=df['Date'],
                                         open=df['Open'], high=df['High'],
                                         low=df['Low'], close=df['Close'])])

    fig.update_layout(xaxis_rangeslider_visible=False)
    if impulse.priceStart != 0:
        dateStart = impulse.dateStart

        if (dateStart > df.iloc[0]['Date']):
            add_min = 0
            if tf == 1:
                add_min = 5
            elif tf == 5:
                add_min = 15
            elif tf == 15:
                add_min = 60
            elif tf == 30:
                add_min = 120
            elif tf == 60:
                add_min = 240

            dateEnd = impulse.dateEnd + datetime.timedelta(minutes=add_min)

            indexEnd = df.index[df['Date'] == dateEnd]
            indexStart = df.index[df['Date'] == dateStart]

            lastPrice = 0
            color = ''
            if impulse.type == 'L':
                lastPrice = df.loc[indexStart[0]:indexEnd[0], 'High'].max()
                color = 'LightGreen'
            else:
                lastPrice = df.loc[indexStart[0]:indexEnd[0], 'Low'].min()
                color = 'Red'


            fig.add_shape(type="rect",
                          x0=dateStart, y0=impulse.priceStart, x1=dateEnd, y1=lastPrice,
                          line=dict(color=color)
                          )

            if impulse.isOpen:
                if impulse.type == "L":
                    line = getLineB(df, dateEnd, diffIndex=10)
                    print(line)
                    if line[0] != 0:
                        fig.add_shape(type="line",
                                      x0=line[0], y0=line[1], x1=line[2], y1=line[3],
                                      line=dict(color="Green", width=3))
                else:
                    line = getLineU(df, dateEnd, diffIndex=10)
                    print(line)
                    if line[0] != 0:
                        fig.add_shape(type="line",
                                      x0=line[0], y0=line[1], x1=line[2], y1=line[3],
                                      line=dict(color="Red", width=3))

    # if len(bigOrders) != 0:
    #     # dfOrders = pd.DataFrame([vars(s) for s in bigOrders])
    #     #
    #     # dfOrders['date'] = dfOrders['date'].values.astype('<M8[m]')
    #     #
    #     # obj = px.scatter(dfOrders, x = 'date', y = 'price')
    #     x = [x.dateEnd for x in bigOrders]
    #     y = [x.price for x in bigOrders]
    #
    #
    #     listX = []
    #     listY = []
    #     for el in bigOrders:
    #         start_date = el.dateStart.replace(second=0, microsecond=0)
    #         end_date = el.dateEnd.replace(second=0, microsecond=0)
    #         mask = (df['Date'] >= start_date) & (df['Date'] <= end_date)
    #         dfR = df.loc[mask]
    #         for index, row in dfR.iterrows():
    #             listX.append(row['Date'])
    #             listY.append(el.price)
    #
    #
    #     fig.add_scatter(x = listX, y = listY, mode='markers', marker=dict(size=10, color="Green"))



    chart = fig.to_html()

    return chart

def getChartWithOrders(name):
    currency = Currency.objects.get(name=name)
    df = getCandlesDF(currency, 1)


    fig = go.Figure(data=[go.Candlestick(x=df['Date'],
                                         open=df['Open'], high=df['High'],
                                         low=df['Low'], close=df['Close'])])

    fig.update_layout(xaxis_rangeslider_visible=False)

    if BigOrders.objects.filter(symbol = currency,type = 'bids').exists():
        bigOrders = BigOrders.objects.filter(symbol = currency,type = 'bids')
        x = [x.dateEnd for x in bigOrders]
        y = [x.price for x in bigOrders]


        listX = []
        listY = []
        for el in bigOrders:
            start_date = el.dateStart.replace(second=0, microsecond=0)
            end_date = el.dateEnd.replace(second=0, microsecond=0)
            mask = (df['Date'] >= start_date) & (df['Date'] <= end_date)
            dfR = df.loc[mask]
            for index, row in dfR.iterrows():
                listX.append(row['Date'])
                listY.append(el.price)


        fig.add_scatter(x = listX, y = listY, mode='markers', marker=dict(size=10, color="Green"))

    if BigOrders.objects.filter(symbol = currency,type = 'asks').exists():
        bigOrders = BigOrders.objects.filter(symbol=currency, type='asks')
        x = [x.dateEnd for x in bigOrders]
        y = [x.price for x in bigOrders]

        listX = []
        listY = []
        for el in bigOrders:
            start_date = el.dateStart.replace(second=0, microsecond=0)
            end_date = el.dateEnd.replace(second=0, microsecond=0)
            mask = (df['Date'] >= start_date) & (df['Date'] <= end_date)
            dfR = df.loc[mask]
            for index, row in dfR.iterrows():
                listX.append(row['Date'])
                listY.append(el.price)

        fig.add_scatter(x=listX, y=listY, mode='markers', marker=dict(size=10, color="Red"))
    # ЗДЕСЬ ИДУТ ТЕКУЩИЕ ЗАЯВКИ
    if OrdersRealtime.objects.filter(symbol = currency,type = 'bids').exists():
        bigOrders = OrdersRealtime.objects.filter(symbol = currency,type = 'bids')
        x = [x.dateEnd for x in bigOrders]
        y = [x.price for x in bigOrders]


        listX = []
        listY = []
        for el in bigOrders:
            start_date = el.dateStart.replace(second=0, microsecond=0)
            end_date = el.dateEnd.replace(second=0, microsecond=0)
            mask = (df['Date'] >= start_date) & (df['Date'] <= end_date)
            dfR = df.loc[mask]
            for index, row in dfR.iterrows():
                listX.append(row['Date'])
                listY.append(el.price)


        fig.add_scatter(x = listX, y = listY, mode='markers', marker=dict(size=10, color="Green"))

    if OrdersRealtime.objects.filter(symbol = currency,type = 'asks').exists():
        bigOrders = OrdersRealtime.objects.filter(symbol=currency, type='asks')
        x = [x.dateEnd for x in bigOrders]
        y = [x.price for x in bigOrders]

        listX = []
        listY = []
        for el in bigOrders:
            start_date = el.dateStart.replace(second=0, microsecond=0)
            end_date = el.dateEnd.replace(second=0, microsecond=0)
            mask = (df['Date'] >= start_date) & (df['Date'] <= end_date)
            dfR = df.loc[mask]
            for index, row in dfR.iterrows():
                listX.append(row['Date'])
                listY.append(el.price)

        fig.add_scatter(x=listX, y=listY, mode='markers', marker=dict(size=10, color="Red"))



    chart = fig.to_html()

    return chart


def getLineB(df, dateEnd, countInGood = 10, diffIndex = 20, countTouch = 2):
    listLow = df[df['Date'] >= dateEnd]['Low']

    indexes = np.arange(len(listLow))

    lastDate = df['Date'].iat[-1]

    df = pd.DataFrame({'index': indexes, 'Low': listLow})
    array = df.to_numpy()

    array = array[array[:, 1].argsort()]

    startIndex = array[0][0]
    maxOfLow = array[0][1]
    maxOfIndexL = startIndex
    minOfIndexL = startIndex

    indexs = [startIndex]
    countIn = 1

    for el in array[1:]:
        if countIn > countInGood:
            return [0, 0, 0, 0]
        else:
            currIndex = el[0]
            currLow = el[1]

            isGood = True

            for ind in indexs:
                if abs(currIndex - ind) < diffIndex:
                    isGood = False
                    break

            if isGood:
                indexs.append(currIndex)

                if currLow > maxOfLow:
                    maxOfLow = currLow

                if currIndex > maxOfIndexL:
                    maxOfIndexL = currIndex

                if currIndex < minOfIndexL:
                    minOfIndexL = currIndex
            else:
                countIn += 1

                if currIndex > maxOfIndexL:
                    maxOfIndexL = currIndex

                if currIndex < minOfIndexL:
                    minOfIndexL = currIndex

            if len(indexs) >= countTouch:
                return [dateEnd, maxOfLow, lastDate, maxOfLow]

def getLineU(df, dateEnd, countInGood = 10, diffIndex = 20, countTouch = 2):
    listHigh = df[df['Date'] >= dateEnd]['High']

    indexes = np.arange(len(listHigh))

    lastDate = df['Date'].iat[-1]

    df = pd.DataFrame({'index': indexes, 'Low': listHigh})
    array = df.to_numpy()

    array = array[(-array[:, 1]).argsort()]
    startIndex = array[0][0]
    maxOfHigh = array[0][1]

    indexs = [startIndex]
    countIn = 1

    for el in array[1:]:
        if countIn > countInGood:
            return [0, 0, 0, 0]
        else:
            currIndex = el[0]
            currHigh = el[1]

            isGood = True

            for ind in indexs:
                if abs(currIndex - ind) < diffIndex:
                    isGood = False
                    break

            if isGood:
                indexs.append(currIndex)

                if currHigh < maxOfHigh:
                    maxOfHigh = currHigh

            else:
                countIn += 1

            if len(indexs) >= countTouch:
                return [dateEnd, maxOfHigh, lastDate, maxOfHigh]