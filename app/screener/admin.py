from django.contrib import admin
from django.urls import path
from django.http import HttpResponseRedirect
from .models import Currency,BinanceKey, Machine, CurrencyTable, Candles
from .clientWork import start_machine, get_start_data, get_impulses
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



@admin.register(CurrencyTable)
class CurrencyTableAdmin(admin.ModelAdmin):
    list_display = ('symbol', 'tf1','tf5','tf15')
    change_list_template = 'admin/currency_table_changelist.html'

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [path('get_currency_from_db/', self.getCurrencyFromDB)]
        return my_urls + urls
    
    def getCurrencyFromDB(self,request):
        currency_list = Currency.objects.all()
        for currency in currency_list:
            CurrencyTable.objects.create(symbol = currency, tf1 = 0, tf5 = 0, tf15 = 0)
        return HttpResponseRedirect("../")

@admin.register(Machine)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('is_working','start_date')
    change_list_template = "admin/machine_changelist.html"

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [path('startStopMachine/', self.startStopMachine), path('getStartData/', self.getStartData), path('getImpulses/', self.getImpulses)]
        return my_urls + urls

    def getStartData(self, request):
        t1 = Thread(target=get_start_data, args=(self, request))
        t1.start()

        return HttpResponseRedirect("../")

    def getImpulses(self, request):
        t1 = Thread(target=get_impulses)
        t1.start()
        self.message_user(request, "Get Impulses starting. . .")
        t1.join()
        self.message_user(request, "Get Impulses done. . .")


        return HttpResponseRedirect("../")

    def startStopMachine(self,request):
        machine = Machine.objects.all().first()
        if machine.is_working:
            machine.is_working = False
        else:
            machine.is_working = True
        machine.save()

        if machine.is_working:
            self.message_user(request, "Bot is started")
            start_machine()
            
        else:
            self.message_user(request, "Bot is stopped")
        return HttpResponseRedirect("../")

@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('name', 'rank')
    change_list_template = "admin/currency_changelist.html"

    
    isGood = True

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [path('getCurrency/', self.getCurrency)]
        return my_urls + urls
    
    def startStopMachine(self,request):
        
        return HttpResponseRedirect("../")
    

    def getCurrency(self, request):
        cmc = CoinMarketCapAPI(api_key='cad5ef95-5be7-459c-881b-b65b012ae02d')
        rep = cmc.cryptocurrency_map() # See methods below

        df = pd.DataFrame(rep.data)

        df = df.sort_values(by = ['rank'])


        for index, row in df.iterrows():
            if(row['rank'] >= 100):
                break
            Currency.objects.create(name = row['symbol'] + 'USDT', rank = row['rank'])
        return HttpResponseRedirect("../")
