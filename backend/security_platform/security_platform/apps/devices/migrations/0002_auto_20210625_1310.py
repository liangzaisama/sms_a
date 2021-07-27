# Generated by Django 2.2.4 on 2021-06-25 13:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('devices', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deviceinfo',
            name='gis_basic_info',
            field=models.CharField(blank=True, max_length=200, verbose_name='gis点位信息(x,y)'),
        ),
        migrations.AlterField(
            model_name='deviceinfo',
            name='gis_field',
            field=models.CharField(blank=True, max_length=200, verbose_name='gis基础信息'),
        ),
    ]
