from django.shortcuts import render
from django.http import HttpResponse
from .models import CurrencyTable, Impulses, Currency, Candles

from .db_request import getCandlesDF
from .math_methods import getChartWithImpulse,impulse_long

from datetime import datetime, timedelta

from pytz import timezone

import numpy as np

tz=timezone('Europe/Moscow')
def index(request):
    result = []
    currency = Currency.objects.all()
    for curr in currency:
        countC1 = 0
        countC5 = 0
        countC15 = 0
        imp1 = Impulses.objects.get(symbol = curr, tf = 1, type = 'L')
        if imp1.isOpen == 1:
            dateNow = datetime.now(tz)
            diffMin = dateNow - imp5.dateEnd + timedelta(hours=3)
            countC1 = np.round(diffMin.total_seconds() / 60,0)
        imp5 = Impulses.objects.get(symbol = curr, tf = 5, type = 'L')
        if imp5.isOpen == 1:
            dateNow = datetime.now(tz)
            diffMin = dateNow - imp5.dateEnd + timedelta(hours=3)
            countC5 = np.round(diffMin.total_seconds() / 60 / 5,0)
        imp15 = Impulses.objects.get(symbol = curr, tf = 15, type = 'L')
        if imp15.isOpen == 1:
            dateNow = datetime.now(tz)
            diffMin = dateNow - imp5.dateEnd + timedelta(hours=3)
            countC15 = np.round(diffMin.total_seconds() / 60 / 15,0)
        result.append({'name' : curr.name, 'tf1' : imp1,'countC1':countC1, 'tf5': imp5,'countC5':countC5, 'tf15':imp15, 'countC15':countC15})
    return render(request, 'screener/currency_table.html', {'result':result})

def single_currency(request, name):
    print(name)
    return render(request, 'screener/single_currency.html', {'name' : name})

def test_view(request,name, tf):

    df = getCandlesDF(name, tf)

    if tf == 1:
        df_Imp = getCandlesDF(name, 5)
        print(df_Imp)
        impulse = impulse_long(df_Imp)
        print(impulse)
        chart = getChartWithImpulse(df, impulse, tf)
        return render(request, 'screener/test_view.html', {'chart': chart})
    elif tf == 5:
        df_Imp = getCandlesDF(name, 15)
        print(df_Imp)
        impulse = impulse_long(df_Imp)
        print(impulse)
        chart = getChartWithImpulse(df, impulse, tf)
        return render(request, 'screener/test_view.html', {'chart': chart})
    elif tf == 15:
        df_Imp = getCandlesDF(name, 60)
        print(df_Imp)
        impulse = impulse_long(df_Imp)
        print(impulse)
        chart = getChartWithImpulse(df, impulse, tf)
        return render(request, 'screener/test_view.html', {'chart': chart})







    return render(request, 'screener/single_currency.html', {'name': name})