# Generated by Django 4.1.2 on 2023-06-13 08:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('comm_manager', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='chat',
            name='is_mirrorreply_feature_on',
            field=models.BooleanField(default=False),
        ),
    ]