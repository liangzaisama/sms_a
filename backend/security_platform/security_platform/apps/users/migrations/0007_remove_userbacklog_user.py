# Generated by Django 2.2.4 on 2021-06-28 15:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_userbacklog_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userbacklog',
            name='user',
        ),
    ]
