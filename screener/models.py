from django.db import models
from django.utils import timezone

class BinanceKey(models.Model):
    api = models.CharField(max_length=65)
    secret = models.CharField(max_length=65)

class Currency(models.Model):
    name = models.CharField(max_length=20)
    rank = models.FloatField()

class Candles(models.Model):
    symbol = models.ForeignKey(Currency, on_delete=models.CASCADE)
    tf = models.IntegerField(default = 0)
    Open = models.FloatField()
    High = models.FloatField()
    Low = models.FloatField()
    Close = models.FloatField()
    Volume = models.FloatField()
    Date = models.BigIntegerField()

class Machine(models.Model):
    is_working = models.BooleanField(default=False)
    start_date = models.DateField(default=timezone.now)

class CurrencyTable(models.Model):
    symbol = models.ForeignKey(Currency, on_delete=models.CASCADE)
    tf1 = models.CharField(max_length=50)
    tf5 = models.CharField(max_length=50)
    tf15 = models.CharField(max_length=50)

class Impulses(models.Model):
    symbol = models.ForeignKey(Currency, on_delete=models.CASCADE)
    type = models.CharField(max_length=5)
    tf = models.IntegerField()
    priceStart = models.FloatField()
    dateStart = models.CharField(max_length=20)
    priceEnd = models.FloatField()
    dateEnd = models.CharField(max_length=20)
    isOpen = models.IntegerField(default = 0)
