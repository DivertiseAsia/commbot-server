# Generated by Django 4.1.2 on 2023-06-25 01:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('external_data_manager', '0002_mtgcard_image_url_ckd_mtgcard_price_ckd'),
    ]

    operations = [
        migrations.CreateModel(
            name='MtgStore',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('search_url', models.CharField(max_length=255)),
                ('item_locator', models.CharField(max_length=100)),
                ('item_price_locator', models.CharField(max_length=100)),
                ('item_name_locator', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='MtgStorePrice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.CharField(blank=True, max_length=20, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, verbose_name='Last Updated')),
                ('card', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='external_data_manager.mtgcard')),
                ('store', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='external_data_manager.mtgstore')),
            ],
        ),
        migrations.AddField(
            model_name='mtgcard',
            name='prices',
            field=models.ManyToManyField(through='external_data_manager.MtgStorePrice', to='external_data_manager.mtgstore'),
        ),
        migrations.CreateModel(
            name='AdditionalStep',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.IntegerField()),
                ('item_locator', models.CharField(max_length=100)),
                ('action', models.IntegerField(choices=[(1, 'Fill'), (2, 'Click')])),
                ('store', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='external_data_manager.mtgstore')),
            ],
            options={
                'unique_together': {('order', 'store')},
            },
        ),
    ]
