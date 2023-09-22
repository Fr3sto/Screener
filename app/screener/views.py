from django.shortcuts import render
from django.http import HttpResponse
from .models import  Impulses, Currency, Candles, BigOrders,OrdersRealtime

from .db_request import getCandlesDF, getOrders
from .math_methods import getChartWithImpulse,impulse_long,getChartWithOrders

from datetime import datetime, timedelta


import numpy as np

def index(request):
    result = []
    currency = Currency.objects.all()

    list_TF = [5,15,30,60]
    other_result = []
    for curr in currency:
        listImpulses = []
        isHaveImpulse = False
        for TF in list_TF:
            imp = Impulses.objects.get(symbol = curr, tf = TF, type = 'L')
            count_after_imp = 0
            if imp.isOpen:
                diff = datetime.now() - imp.dateEnd
                count_after_imp = np.round(diff.total_seconds() / 60 / TF,0)
                isHaveImpulse = True
            listImpulses.append({'impulse' : imp, 'count' :  count_after_imp, 'TF': TF})
        orderLMin = 0
        if OrdersRealtime.objects.filter(symbol = curr, type = 'bids').exists():
            orderL = OrdersRealtime.objects.get(symbol_id=curr, type='bids')
            orderLMin = np.round((orderL.dateEnd - orderL.dateStart).total_seconds() / 60, 0)
        orderSMin = 0
        if OrdersRealtime.objects.filter(symbol=curr, type='asks').exists():
            orderS = OrdersRealtime.objects.get(symbol_id=curr, type='asks')
            orderSMin = np.round((orderS.dateEnd - orderS.dateStart).total_seconds() / 60, 0)
        if isHaveImpulse:
            result.append({'name' : curr.name, 'impInfo' : listImpulses, 'orderL' : orderLMin,'orderS': orderSMin })
        else:
            other_result.append({'name': curr.name, 'impInfo': listImpulses, 'orderL' : orderLMin, 'orderS': orderSMin})

    result.extend(other_result)
    return render(request, 'screener/currency_table.html', {'result':result, 'listTF' : list_TF})

def single_currency(request, name):
    print(name)
    return render(request, 'screener/single_currency.html', {'name' : name})

def test_view(request,name, tf):
    currency = Currency.objects.get(name = name)
    df = getCandlesDF(currency, tf)
    imp = Impulses.objects.get(symbol = currency, tf = tf, type = 'L')
    #bigOrders = getOrders(currency)
    chart = getChartWithImpulse(df, imp, tf)
    return render(request, 'screener/test_view.html', {'chart': chart})

def chartOrder(request,name, type):
    chart = getChartWithOrders(name)
    return render(request, 'screener/test_view.html', {'chart': chart})