# Generated by Django 5.1.2 on 2024-11-28 20:16

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_alter_user_birthday_alter_user_date_joined_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='birthday',
            field=models.DateField(default=datetime.datetime(2024, 11, 28, 15, 16, 54, 400711)),
        ),
        migrations.AlterField(
            model_name='user',
            name='date_joined',
            field=models.DateTimeField(default=datetime.datetime(2024, 11, 28, 15, 16, 54, 400700)),
        ),
        migrations.AlterField(
            model_name='wraps',
            name='creation_date',
            field=models.DateTimeField(default=datetime.datetime(2024, 11, 28, 15, 16, 54, 401339)),
        ),
    ]
