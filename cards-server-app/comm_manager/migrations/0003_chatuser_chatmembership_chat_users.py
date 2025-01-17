# Generated by Django 4.1.2 on 2023-07-26 03:08

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('comm_manager', '0002_chat_is_mirrorreply_feature_on'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChatUser',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('external_id', models.CharField(blank=True, db_index=True, max_length=255, verbose_name='External ID (from Provider)')),
                ('display_name', models.CharField(blank=True, max_length=255, null=True)),
                ('last_pulled_date', models.DateTimeField(blank=True, null=True, verbose_name='Last Pulled Via API Date')),
            ],
        ),
        migrations.CreateModel(
            name='ChatMembership',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_seen_date', models.DateTimeField(auto_now_add=True, verbose_name='First Seen Date')),
                ('ended_date', models.DateTimeField(blank=True, null=True)),
                ('chat', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='comm_manager.chat')),
                ('chat_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='comm_manager.chatuser')),
            ],
        ),
        migrations.AddField(
            model_name='chat',
            name='users',
            field=models.ManyToManyField(through='comm_manager.ChatMembership', to='comm_manager.chatuser'),
        ),
    ]
