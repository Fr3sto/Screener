from django.shortcuts import render
from django.http import HttpResponse
from .models import CurrencyTable, Impulses, Currency, Candles

from .db_request import getCandlesDF
from .math_methods import getChartWithImpulse,impulse_long



def index(request):
    result = []
    currency = Currency.objects.all()
    for curr in currency:
        imp1 = Impulses.objects.get(symbol = curr, tf = 1, type = 'L')
        imp5 = Impulses.objects.get(symbol = curr, tf = 5, type = 'L')
        #imp15 = Impulses.objects.get(symbol = curr, tf = 15, type = 'L')
        result.append({'name' : curr.name, 'tf1' : imp1, 'tf5': imp5})#, 'tf15':imp15})
    return render(request, 'screener/currency_table.html', {'result':result})

def single_currency(request, name):
    print(name)
    return render(request, 'screener/single_currency.html', {'name' : name})

def test_view(request,name, tf):

    df = getCandlesDF(name, tf)
    impulse = impulse_long(df, tf)

    chart = getChartWithImpulse(df,impulse,tf)

    return render(request, 'screener/test_view.html', {'chart' : chart})