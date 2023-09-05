# Generated by Django 4.0.8 on 2023-08-28 10:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('screener', '0009_rename_close_candles_close_rename_date_candles_date_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='CurrencyTable',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tf1', models.DateTimeField()),
                ('tf5', models.DateTimeField()),
                ('tf15', models.DateTimeField()),
                ('symbol', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='screener.currency')),
            ],
        ),
    ]