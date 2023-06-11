# Generated by Django 4.1.2 on 2023-06-10 03:59

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Chat',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('chat_type', models.IntegerField(choices=[(1, 'Individual'), (2, 'Group')])),
                ('joined_date', models.DateTimeField(auto_now_add=True, verbose_name='Joined Date')),
                ('ended_date', models.DateTimeField(blank=True, null=True)),
                ('external_id', models.CharField(blank=True, db_index=True, max_length=255, verbose_name='External ID (from Provider)')),
            ],
        ),
    ]