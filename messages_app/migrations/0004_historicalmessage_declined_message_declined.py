# Generated by Django 4.2.11 on 2024-06-09 18:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('messages_app', '0003_historicalmessage'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalmessage',
            name='declined',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='message',
            name='declined',
            field=models.BooleanField(default=False),
        ),
    ]
