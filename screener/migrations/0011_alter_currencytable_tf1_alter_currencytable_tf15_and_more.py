# Generated by Django 4.0.8 on 2023-08-28 10:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('screener', '0010_currencytable'),
    ]

    operations = [
        migrations.AlterField(
            model_name='currencytable',
            name='tf1',
            field=models.BigIntegerField(),
        ),
        migrations.AlterField(
            model_name='currencytable',
            name='tf15',
            field=models.BigIntegerField(),
        ),
        migrations.AlterField(
            model_name='currencytable',
            name='tf5',
            field=models.BigIntegerField(),
        ),
    ]
