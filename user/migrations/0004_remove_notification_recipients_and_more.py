# Generated by Django 5.1.2 on 2024-12-23 17:32

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0003_remove_notification_recipient_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="notification",
            name="recipients",
        ),
        migrations.AddField(
            model_name="notification",
            name="recipient",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="notifications",
                to=settings.AUTH_USER_MODEL,
            ),
            preserve_default=False,
        ),
    ]
