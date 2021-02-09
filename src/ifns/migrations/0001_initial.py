# Generated by Django 2.2.14 on 2021-01-22 10:56

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import ifns.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PreviousConfig',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('changed_at', models.DateTimeField(auto_now=True, verbose_name='Дата изменения')),
                ('config', django.contrib.postgres.fields.jsonb.JSONField(verbose_name='Настройки')),
            ],
            options={
                'verbose_name': 'Предыдущие настройки загрузки реквизитов ИФНС',
                'verbose_name_plural': 'Предыдущие настройки загрузки реквизитов ИФНС',
            },
        ),
        migrations.CreateModel(
            name='Requisites',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('version', models.IntegerField(default=1, verbose_name='Версия')),
                ('nalog_code', models.CharField(max_length=255, verbose_name='Код ИФНС')),
                ('name', models.CharField(max_length=255, null=True, verbose_name='Наименование')),
                ('address', models.CharField(max_length=255, null=True, verbose_name='Адрес')),
                ('phone', models.CharField(max_length=255, null=True, verbose_name='Телефон')),
                ('additional_Info', models.CharField(max_length=255, null=True, verbose_name='Доп. информация')),
                ('payment_receiver', models.CharField(max_length=255, null=True, verbose_name='Получатель платежа')),
                ('OKTMO_code', models.CharField(max_length=8, null=True, verbose_name='Код ОКТМО бюджетополучателя')),
                ('receiver_inn', models.CharField(max_length=12, null=True, verbose_name='ИНН получателя')),
                ('receiver_kpp', models.CharField(max_length=9, null=True, verbose_name='КПП получателя')),
                ('bank_name', models.CharField(max_length=255, null=True, verbose_name='Банк получателя')),
                ('bank_account_bik', models.CharField(max_length=9, null=True, verbose_name='БИК')),
                ('bank_account_corr', models.CharField(max_length=200, null=True, verbose_name='Корр. счет №')),
                ('bank_account_number', models.CharField(max_length=200, null=True, verbose_name='Счет №')),
                ('registration_code', models.CharField(max_length=255, null=True, verbose_name='Код регистрирующего органа')),
                ('registration_name', models.CharField(max_length=255, null=True, verbose_name='Наименование')),
                ('registration_address', models.CharField(max_length=255, null=True, verbose_name='Адрес')),
                ('registration_phone', models.CharField(max_length=255, null=True, verbose_name='Телефон')),
                ('registration_add_Info', models.CharField(max_length=255, null=True, verbose_name='Доп. информация')),
                ('registration_code_2', models.CharField(max_length=255, null=True, verbose_name='Код регистрирующего органа')),
                ('registration_name_2', models.CharField(max_length=255, null=True, verbose_name='Наименование')),
                ('registration_address_2', models.CharField(max_length=255, null=True, verbose_name='Адрес')),
                ('registration_phone_2', models.CharField(max_length=255, null=True, verbose_name='Телефон')),
                ('registration_add_Info_2', models.CharField(max_length=255, null=True, verbose_name='Доп. информация')),
            ],
            options={
                'verbose_name': 'Реквизиты ИФНС',
                'verbose_name_plural': 'Реквизиты ИФНС',
            },
        ),
        migrations.CreateModel(
            name='Setting',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('changed_at', models.DateTimeField(auto_now=True, verbose_name='Дата изменения')),
                ('base_url', models.CharField(default=ifns.models.base_url_setting_default_value, max_length=500)),
                ('current_config', django.contrib.postgres.fields.jsonb.JSONField(default=ifns.models.jsonfield_setting_default_value, verbose_name='Текущий конфиг настроек')),
            ],
            options={
                'verbose_name': 'Настройки загрузки реквизитов ИФНС',
                'verbose_name_plural': 'Настройки загрузки реквизитов ИФНС',
            },
        ),
    ]
