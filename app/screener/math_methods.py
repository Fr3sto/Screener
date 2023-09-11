
from datetime import datetime, timedelta
import plotly.express as px

def atr(df, period = 10):
    df['Max'] =  df['High'].rolling(period).max().shift().fillna(0)
    df['Min'] = df['Low'].rolling(period).min().shift().fillna(0)

    df['Atr'] = df['Max'] - df['Min']

    return df.drop(columns = ['Max','Min'])

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
    dateStart = datetime.now()
    priceEnd = 0
    dateEnd = datetime.now()
    iEnd = 0

    for i, x in enumerate(list):
        if(isUp):
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
        return [0, '2020-01-01 00:00:00', 0,'2020-01-01 00:00:00', 0, 0]
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
    fig = px.line(df, x = 'Date', y = 'Close')

    if(impulse[0] != 0):
        dateStart = impulse[1]

        if (dateStart > df.iloc[0]['Date']):
            add_min = 0
            if tf == 1:
                add_min = 5
            elif tf == 5:
                add_min = 15
            elif tf == 15:
                add_min = 60

            dateEnd = impulse[3] + timedelta(minutes=add_min)

            fig.add_shape(type="rect",
                          x0=dateStart, y0=impulse[0], x1=dateEnd, y1=impulse[2],
                          line=dict(color="LightGreen")
                          )



    chart = fig.to_html()

    return chart