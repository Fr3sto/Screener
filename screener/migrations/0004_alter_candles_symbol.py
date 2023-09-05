# Generated by Django 4.0.8 on 2023-08-24 16:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('screener', '0003_candles'),
    ]

    operations = [
        migrations.AlterField(
            model_name='candles',
            name='symbol',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='screener.currency'),
        ),
    ]