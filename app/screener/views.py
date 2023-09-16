from django.shortcuts import render
from django.http import HttpResponse
from .models import  Impulses, Currency, Candles, BigOrders

from .db_request import getCandlesDF, getOrders
from .math_methods import getChartWithImpulse,impulse_long

from datetime import datetime, timedelta


import numpy as np

def index(request):
    result = []
    currency = Currency.objects.all()

    list_TF = [1,5,15,30,60]
    for curr in currency:
        listImpulses = []
        for TF in list_TF:
            imp = Impulses.objects.get(symbol = curr, tf = TF, type = 'L')
            count_after_imp = 0
            if imp.isOpen:
                diff = datetime.now() - imp.dateEnd + timedelta(hours=3)
                count_after_imp = np.round(diff.total_seconds() / 60 / TF,0)
            listImpulses.append({'impulse' : imp, 'count' :  count_after_imp, 'TF': TF})
        result.append({'name' : curr.name, 'impInfo' : listImpulses})
    return render(request, 'screener/currency_table.html', {'result':result, 'listTF' : list_TF})

def single_currency(request, name):
    print(name)
    return render(request, 'screener/single_currency.html', {'name' : name})

def test_view(request,name, tf):
    currency = Currency.objects.get(name = name)
    df = getCandlesDF(currency, tf)
    imp = Impulses.objects.get(symbol = currency, tf = tf, type = 'L')
    bigOrders = getOrders(currency)
    chart = getChartWithImpulse(df, imp, bigOrders, tf)
    return render(request, 'screener/test_view.html', {'chart': chart})