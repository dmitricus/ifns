from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils.translation import ugettext_lazy, gettext_lazy as _


class DateTimeTracking(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата создания'))
    changed_at = models.DateTimeField(auto_now=True, verbose_name=_('Дата изменения'))

    class Meta:
        abstract = True


def jsonfield_setting_default_value():
    return {
        "url": "",
        "file_date": "01.01.2001",
        "last_date": "01.01.2001",
        "definition": "https://data.nalog.ru/opendata/7707329152-address/structure-07142014.csv",
        "actuality_date": "01.01.2001"
    }


def base_url_setting_default_value():
    return 'https://data.nalog.ru/opendata/7707329152-address/'


class Setting(DateTimeTracking):
    base_url = models.CharField(max_length=500, default=base_url_setting_default_value)
    current_config = JSONField(
        verbose_name=_('Текущий конфиг настроек'),
        default=jsonfield_setting_default_value
    )

    class Meta:
        verbose_name = _('Настройки загрузки реквизитов ИФНС')
        verbose_name_plural = _('Настройки загрузки реквизитов ИФНС')

    def __str__(self):
        return str(ugettext_lazy('Настройки загрузки реквизитов ИФНС'))


class Requisites(models.Model):
    version = models.IntegerField(default=1, verbose_name=_('Версия'))
    nalog_code = models.CharField(max_length=255, verbose_name=_('Код ИФНС'))
    name = models.CharField(max_length=255, null=True, verbose_name=_('Наименование'))
    address = models.CharField(max_length=255, null=True, verbose_name=_('Адрес'))
    phone = models.CharField(max_length=255, null=True, verbose_name=_('Телефон'))
    additional_Info = models.CharField(max_length=255, null=True, verbose_name=_('Доп. информация'))
    payment_receiver = models.CharField(max_length=255, null=True, verbose_name=_('Получатель платежа'))
    OKTMO_code = models.CharField(max_length=8, null=True, verbose_name=_('Код ОКТМО бюджетополучателя'))
    receiver_inn = models.CharField(max_length=12, null=True, verbose_name=_('ИНН получателя'))
    receiver_kpp = models.CharField(max_length=9, null=True, verbose_name=_('КПП получателя'))
    bank_name = models.CharField(max_length=255, null=True, verbose_name=_('Банк получателя'))
    bank_account_bik = models.CharField(max_length=9, null=True, verbose_name=_('БИК'))
    bank_account_corr = models.CharField(max_length=200, null=True, verbose_name=_('Корр. счет №'))
    bank_account_number = models.CharField(max_length=200, null=True, verbose_name=_('Счет №'))
    registration_code = models.CharField(max_length=255, null=True, verbose_name=_('Код регистрирующего органа'))
    registration_name = models.CharField(max_length=255, null=True, verbose_name=_('Наименование'))
    registration_address = models.CharField(max_length=255, null=True, verbose_name=_('Адрес'))
    registration_phone = models.CharField(max_length=255, null=True, verbose_name=_('Телефон'))
    registration_add_Info = models.CharField(max_length=255, null=True, verbose_name=_('Доп. информация'))
    registration_code_2 = models.CharField(max_length=255, null=True, verbose_name=_('Код регистрирующего органа'))
    registration_name_2 = models.CharField(max_length=255, null=True, verbose_name=_('Наименование'))
    registration_address_2 = models.CharField(max_length=255, null=True, verbose_name=_('Адрес'))
    registration_phone_2 = models.CharField(max_length=255, null=True, verbose_name=_('Телефон'))
    registration_add_Info_2 = models.CharField(max_length=255, null=True, verbose_name=_('Доп. информация'))

    class Meta:
        verbose_name = _('Реквизиты ИФНС')
        verbose_name_plural = _('Реквизиты ИФНС')

    def __str__(self):
        return self.nalog_code


class PreviousConfig(DateTimeTracking):
    config = JSONField(verbose_name=_('Настройки'))

    class Meta:
        verbose_name = _('Предыдущие настройки загрузки реквизитов ИФНС')
        verbose_name_plural = _('Предыдущие настройки загрузки реквизитов ИФНС')

    def __str__(self):
        return str(_('Предыдущие настройки загрузки реквизитов ИФНС'))
