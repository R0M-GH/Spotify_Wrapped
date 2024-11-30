# Generated by Django 5.1.1 on 2024-11-30 00:29

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0004_alter_user_birthday_alter_user_date_joined_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="birthday",
            field=models.DateField(
                default=datetime.datetime(2024, 11, 29, 19, 29, 7, 920771)
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="date_joined",
            field=models.DateTimeField(
                default=datetime.datetime(2024, 11, 29, 19, 29, 7, 920761)
            ),
        ),
        migrations.AlterField(
            model_name="wraps",
            name="creation_date",
            field=models.DateTimeField(
                default=datetime.datetime(2024, 11, 29, 19, 29, 7, 921660)
            ),
        ),
    ]
