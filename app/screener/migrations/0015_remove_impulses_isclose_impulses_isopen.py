# Generated by Django 4.0.8 on 2023-08-30 16:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('screener', '0014_impulses_isclose'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='impulses',
            name='isClose',
        ),
        migrations.AddField(
            model_name='impulses',
            name='isOpen',
            field=models.IntegerField(default=0),
        ),
    ]