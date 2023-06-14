# Generated by Django 4.1.2 on 2023-06-12 09:18

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MtgCard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='First Created')),
                ('last_updated', models.DateTimeField(auto_now=True, verbose_name='Last Updated')),
                ('latest_card_data', models.JSONField(blank=True, default=dict)),
                ('image_url', models.CharField(max_length=255)),
                ('price', models.CharField(blank=True, max_length=20, null=True)),
                ('type_line', models.CharField(max_length=255)),
                ('mana_cost', models.CharField(max_length=64)),
                ('search_text', models.CharField(db_index=True, max_length=255, unique=True)),
                ('external_id', models.CharField(blank=True, db_index=True, max_length=255, verbose_name='External ID (from Provider)')),
            ],
        ),
    ]