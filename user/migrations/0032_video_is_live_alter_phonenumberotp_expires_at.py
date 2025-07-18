# Generated by Django 5.0.6 on 2025-07-12 20:11

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0031_alter_phonenumberotp_expires_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='video',
            name='is_live',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='phonenumberotp',
            name='expires_at',
            field=models.DateTimeField(default=datetime.datetime(2025, 7, 12, 20, 16, 32, 321272, tzinfo=datetime.timezone.utc)),
        ),
    ]
