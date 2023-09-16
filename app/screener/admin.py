from django.contrib import admin
from django.urls import path
from django.http import HttpResponseRedirect
from .models import Currency,BinanceKey, Machine, Candles, Impulses, BigOrders
from .clientWork import start_machine, get_start_data, get_impulses, startStreamBook, deleteIncorrectCurrencies
import pandas as pd
from coinmarketcapapi import CoinMarketCapAPI
from threading import Thread


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
        my_urls = [path('startStopMachine/', self.startStopMachine),
                   path('getStartData/', self.getStartData),
                   path('getImpulses/', self.getImpulses),
                   path('startStreamBook/', self.startStreamBook)]
        return my_urls + urls

    def startStreamBook(self, request):
        t1 = Thread(target=startStreamBook)
        t1.start()

        return HttpResponseRedirect("../")
    def getStartData(self, request):
        t1 = Thread(target=get_start_data, args=(self, request))
        t1.start()

        return HttpResponseRedirect("../")

    def getImpulses(self, request):
        thread = Thread(target=get_impulses)
        thread.start()
        thread.join()


        return HttpResponseRedirect("../")

    def startStopMachine(self,request):

        self.message_user(request, "Bot is started")

        thread = Thread(target=start_machine)
        thread.start()

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
        deleteIncorrectCurrencies()
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
                if(row['rank'] >= 100):
                    break
                curr = Currency.objects.create(name = row['symbol'] + 'USDT', rank = row['rank'])
                curr.save()
        except Exception as e:
            print(e)
        return HttpResponseRedirect("../")
