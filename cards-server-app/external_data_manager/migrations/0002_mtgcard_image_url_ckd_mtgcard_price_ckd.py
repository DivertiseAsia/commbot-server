# Generated by Django 4.1.2 on 2023-06-20 05:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('external_data_manager', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='mtgcard',
            name='image_url_ckd',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='mtgcard',
            name='price_ckd',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
