# Generated by Django 4.0.8 on 2023-09-19 23:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('screener', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrdersRealtime',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=5)),
                ('dateStart', models.DateTimeField()),
                ('dateEnd', models.DateTimeField()),
                ('price', models.FloatField()),
                ('quantity', models.FloatField()),
                ('pow', models.FloatField(default=0)),
                ('symbol', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='screener.currency')),
            ],
        ),
    ]
