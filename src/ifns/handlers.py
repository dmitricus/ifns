import csv
import io
import logging
import re
from collections import Counter
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from djnewsletter.helpers import send_email

from ifns.http import IFNSHttpClient
from ifns.models import Requisites


class IFNSHandler(IFNSHttpClient):

    def __init__(self):
        super(IFNSHandler, self).__init__()
        self.specifications = {}
        self.logger = logging.getLogger('ifns_handler')
        self.emails_for_notty = User.objects.filter(is_staff=True, is_active=True).values_list('email', flat=True)
        self.load_count = 0
        self.update_count = 0

    def run(self):
        self._handle()

    def _handle(self):
        self.logger.info('Start IFNSHandler')
        response_nalog = self.get_nalog()
        self.html_parser(response_nalog.content.decode('utf-8'))

        if self.is_specifications() and self.specifications['url']:
            self.specifications.update({'file_date': self.data_parser(self.specifications['url'])})

        self.send_email()

        response_file = self.download_file(self.specifications['url'])
        try:
            if self.is_empty_file(response_file):
                raise requests.RequestException('пустой файл')
            self.reset_version_to_zero()
            reader = csv.DictReader(
                io.StringIO(response_file.text),
                quotechar='"',
                delimiter=';',
                dialect=csv.excel_tab,
            )
            for row in reader:
                requisites = Requisites.objects.filter(nalog_code=row['GA']).first()
                if requisites:
                    self.update_requisites(requisites, row)
                    self.update_count += 1
                else:
                    self.create_requisites(row)
                    self.load_count += 1
            self.delete_version_is_zero()

        except (requests.RequestException, KeyError) as e:
            self.logger.exception('Ошибка загрузки реквизитов ИФНС - %s', e)
            self.send_email_error(e)
        except Exception as e:
            self.logger.exception('Ошибка обработки данных ИФНС - %s', e)
            self.send_email_error(e)

        self.logger.info('Stop IFNSHandler')

    def html_parser(self, html_file):
        parsed_html = BeautifulSoup(html_file, 'html5lib')
        table = parsed_html.findChildren('tbody')
        rows = table[0].findChildren(['th', 'tr'])
        for row in rows:
            cells = row.findChildren('td')
            for cell in cells:
                value = cell.text
                if value == '8':
                    self.specifications.update({'url': cells[2].text})
                elif value == '10':
                    self.specifications.update({'definition': cells[2].text})
                elif value == '12':
                    self.specifications.update({'last_date': cells[2].text})
                elif value == '14':
                    self.specifications.update({'actuality_date': cells[2].text})
            if self.is_specifications():
                break

    @staticmethod
    def convert_list_to_str(field):
        items = field.split(',')
        if isinstance(items, list):
            return items[0]
        return items

    @staticmethod
    def data_parser(text):
        """Парсинг даты в формате ddmmyyyy."""
        match = re.search(
            r'(0[1-9]|[1-2][0-9]|31(?!(?:0[2469]|11))|30(?!02))(0[1-9]|1[0-2])([12]\d{3})',
            text,
        )
        date_pars = datetime.strptime(match.group(), '%d%m%Y').date()
        return date_pars

    @staticmethod
    def is_empty_file(response):
        size = sum(len(chunk) for chunk in response.iter_content(8196))
        if size > 0:
            return False
        return True

    @staticmethod
    def reset_version_to_zero():
        Requisites.objects.all().update(version=0)

    @staticmethod
    def delete_version_is_zero():
        Requisites.objects.filter(version=0).delete()

    @staticmethod
    def is_any_changes(current, now):
        if current == now:
            return current
        return now

    def is_specifications(self):
        return Counter(self.specifications.keys()) == Counter(['url', 'definition', 'last_date', 'actuality_date'])

    def send_email(self):
        if self.specifications['definition'] != self.current_config['definition']:
            send_email(
                subject='Изменилось описание структуры данных сервиса загрузки реквизитов ИФНС {}'.format(
                    self.base_url
                ),
                body='Необходимо проверить изменения. Новая версия - {}'.format(self.specifications['url']),
                to=self.emails_for_notty,
            )
        if datetime.strptime(self.specifications['actuality_date'], '%d.%m.%Y') < datetime.now():
            send_email(
                subject='Получены неактуальные данные сервиса загрузки реквизитов ИФНС {}'.format(self.base_url),
                body='Срок актуальности {}'.format(self.specifications['actuality_date']),
                to=self.emails_for_notty,
            )

    def send_email_error(self, error_message):
        send_email(
            subject='Ошибка обработки данных ИФНС',
            body="Ошибка обработки данных ИФНС: {}".format(error_message),
            to=self.emails_for_notty,
        )

    def create_requisites(self, row):
        Requisites.objects.create(
            version=1,
            nalog_code=row['GA'],
            name=row['GB'],
            address=row['G1'],
            phone=row['G2'],
            additional_Info=row['G3'],
            payment_receiver=row['G4'],
            OKTMO_code=self.convert_list_to_str(row['G5']),
            receiver_inn=row['G6'],
            receiver_kpp=row['G7'],
            bank_name=row['G8'],
            bank_account_bik=row['G9'],
            bank_account_corr=row['G10'],
            bank_account_number=row['G11'],
            registration_code=row['G12'],
            registration_name=row['G13'],
            registration_address=row['G14'],
            registration_phone=row['G15'],
            registration_add_Info=row['G16'],
            registration_code_2=row['G17'],
            registration_name_2=row['G18'],
            registration_address_2=row['G19'],
            registration_phone_2=row['G20'],
            registration_add_Info_2=row['G21'],
        )

    def update_requisites(self, requisites, row):
        requisites.version = 1
        requisites.name = self.is_any_changes(requisites.name, row['GB'])
        requisites.address = self.is_any_changes(requisites.address, row['G1'])
        requisites.phone = self.is_any_changes(requisites.phone, row['G2'])
        requisites.additional_Info = self.is_any_changes(requisites.additional_Info, row['G3'])
        requisites.payment_receiver = self.is_any_changes(requisites.payment_receiver, row['G4'])
        requisites.OKTMO_code = self.is_any_changes(requisites.OKTMO_code, self.convert_list_to_str(row['G5']))
        requisites.receiver_inn = self.is_any_changes(requisites.receiver_inn, row['G6'])
        requisites.receiver_kpp = self.is_any_changes(requisites.receiver_kpp, row['G7'])
        requisites.bank_name = self.is_any_changes(requisites.bank_name, row['G8'])
        requisites.bank_account_bik = self.is_any_changes(requisites.bank_account_bik, row['G9'])
        requisites.bank_account_corr = self.is_any_changes(requisites.bank_account_corr, row['G10'])
        requisites.bank_account_number = self.is_any_changes(requisites.bank_account_number, row['G11'])
        requisites.registration_code = self.is_any_changes(requisites.registration_code, row['G12'])
        requisites.registration_name = self.is_any_changes(requisites.registration_name, row['G13'])
        requisites.registration_address = self.is_any_changes(requisites.registration_address, row['G14'])
        requisites.registration_phone = self.is_any_changes(requisites.registration_phone, row['G15'])
        requisites.registration_add_Info = self.is_any_changes(requisites.registration_add_Info, row['G16'])
        requisites.registration_code_2 = self.is_any_changes(requisites.registration_code_2, row['G17'])
        requisites.registration_name_2 = self.is_any_changes(requisites.registration_name_2, row['G18'])
        requisites.registration_address_2 = self.is_any_changes(requisites.registration_address_2, row['G19'])
        requisites.registration_phone_2 = self.is_any_changes(requisites.registration_phone_2, row['G20'])
        requisites.registration_add_Info_2 = self.is_any_changes(requisites.registration_add_Info_2, row['G21'])
        requisites.save()
