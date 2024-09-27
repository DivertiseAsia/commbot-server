# Generated by Django 4.1.2 on 2023-10-14 14:54

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('comm_manager', '0004_chatmessage'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatmessage',
            name='received_date',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='Received Date'),
            preserve_default=False,
        ),
    ]