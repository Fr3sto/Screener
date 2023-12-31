from django.contrib import admin
from django.urls import path
from django.http import HttpResponseRedirect
from .models import Currency,BinanceKey, Machine, Candles, Impulses, BigOrders
from .clientWork import get_start_data, get_impulses,start_streams
import pandas as pd
from coinmarketcapapi import CoinMarketCapAPI
from threading import Thread
import os
import ccxt
import numpy as np

@admin.register(Candles)
class CandlesAdmin(admin.ModelAdmin):
    list_display = ('symbol', 'tf')

    change_list_template = 'admin/candles_table_changelist.html'

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [path('deleteCandles/', self.deleteCandles)]
        return my_urls + urls

    def deleteCandles(self, request):
        Candles.objects.all().delete()
        self.message_user(request, "Candles delete")
        return HttpResponseRedirect("../")
@admin.register(BinanceKey)
class BinanceKeyAdmin(admin.ModelAdmin):
    list_display = ('api', 'secret')



@admin.register(Machine)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('is_working','start_date')
    change_list_template = "admin/machine_changelist.html"

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [path('startStreams/', self.startStreams),
                   path('getStartData/', self.getStartData),
                   path('getImpulses/', self.getImpulses),
                   path('getOrderBook/', self.getOrderBook)]
        return my_urls + urls


        return HttpResponseRedirect("../")

    def getOrderBook(self, request):
        BigOrders.objects.all().delete()
        with open("orders.txt") as fp:
            Lines = fp.readlines()
            listOrder = []
            for line in Lines:
                line = line.split(';')
                try:
                    curr = Currency.objects.get(name=line[0])
                    order = BigOrders(symbol=curr, type=line[1], dateStart=line[2], dateEnd=line[3],
                                                     price=line[4], quantity=line[5], pow=line[6])
                    listOrder.append(order)
                except Exception as e:
                    pass

        BigOrders.objects.bulk_create(listOrder)

        self.message_user(request, "Orders inserted")
        return HttpResponseRedirect("../")
    def getStartData(self, request):
        t1 = Thread(target=get_start_data, args=(self, request))
        t1.start()
        t1.join()
        self.message_user(request, "Data inserted")

        return HttpResponseRedirect("../")

    def getImpulses(self, request):
        thread = Thread(target=get_impulses)
        thread.start()
        thread.join()
        self.message_user(request, "Impulses inserted")

        return HttpResponseRedirect("../")

    def startStreams(self,request):

        self.message_user(request, "Bot is started")

        start_streams()

        return HttpResponseRedirect("../")

@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('name', 'rank')
    change_list_template = "admin/currency_changelist.html"

    
    isGood = True

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [path('getCurrency/', self.getCurrency), path('deleteIncorCurr/', self.deleteIncorrCurrencies)]
        return my_urls + urls

    def deleteIncorrCurrencies(self, request):

        ex = ccxt.binance()

        markets = ex.load_markets()

        list_curr = Currency.objects.all()

        Currency.objects.filter(name = 'USDC').delete()
        Currency.objects.filter(name='TUSD').delete()
        Currency.objects.filter(name='BUSD').delete()
        Currency.objects.filter(name='USDP').delete()

        for curr in list_curr:
            if not curr.name + '/USDT' in markets:
                Currency.objects.filter(name = curr.name).delete()
            elif curr.name + '/USDT' in markets and markets[curr.name + '/USDT']['info']['status'] == 'BREAK':
                Currency.objects.filter(name = curr.name).delete()

        self.message_user(request, "Incorrect deleted")

        return HttpResponseRedirect("../")

    def getCurrency(self, request):
        try:
            Candles.objects.all().delete()
            Impulses.objects.all().delete()
            BigOrders.objects.all().delete()
            Currency.objects.all().delete()

            cmc = CoinMarketCapAPI(api_key='cad5ef95-5be7-459c-881b-b65b012ae02d')
            rep = cmc.cryptocurrency_map() # See methods below

            df = pd.DataFrame(rep.data)

            df = df.sort_values(by = ['rank'])

            for index, row in df.iterrows():
                if(row['rank'] > 100):
                    break

                curr = Currency.objects.create(name=row['symbol'], rank=row['rank'])
                curr.save()

            self.message_user(request, "Currencies added")
        except Exception as e:
            print(e)
        return HttpResponseRedirect("../")
