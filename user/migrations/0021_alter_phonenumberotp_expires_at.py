# Generated by Django 5.0.6 on 2025-07-11 03:00

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0020_alter_phonenumberotp_expires_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='phonenumberotp',
            name='expires_at',
            field=models.DateTimeField(default=datetime.datetime(2025, 7, 11, 3, 5, 22, 856270, tzinfo=datetime.timezone.utc)),
        ),
    ]
