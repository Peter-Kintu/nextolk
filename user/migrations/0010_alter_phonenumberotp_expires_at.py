# Generated by Django 5.0.6 on 2025-07-08 11:04

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0009_alter_video_options_alter_comment_user_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='phonenumberotp',
            name='expires_at',
            field=models.DateTimeField(default=datetime.datetime(2025, 7, 8, 11, 9, 35, 489835, tzinfo=datetime.timezone.utc)),
        ),
    ]
