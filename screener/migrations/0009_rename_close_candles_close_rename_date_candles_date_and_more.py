# Generated by Django 4.0.8 on 2023-08-26 17:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('screener', '0008_candles_tf'),
    ]

    operations = [
        migrations.RenameField(
            model_name='candles',
            old_name='close',
            new_name='Close',
        ),
        migrations.RenameField(
            model_name='candles',
            old_name='date',
            new_name='Date',
        ),
        migrations.RenameField(
            model_name='candles',
            old_name='high',
            new_name='High',
        ),
        migrations.RenameField(
            model_name='candles',
            old_name='low',
            new_name='Low',
        ),
        migrations.RenameField(
            model_name='candles',
            old_name='open',
            new_name='Open',
        ),
        migrations.RenameField(
            model_name='candles',
            old_name='volume',
            new_name='Volume',
        ),
    ]