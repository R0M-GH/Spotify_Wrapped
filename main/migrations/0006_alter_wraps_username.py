# Generated by Django 5.1.2 on 2024-11-24 18:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_alter_user_spotify_access_token_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wraps',
            name='username',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
    ]
