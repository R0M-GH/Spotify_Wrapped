# Generated by Django 5.1.2 on 2024-11-08 20:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='spotify_access_token',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='spotify_refresh_token',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]