from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.core import mail
from django.db import transaction
from django.test import TestCase
from django.test.utils import override_settings
from django.urls import reverse
from djnewsletter.helpers import send_email
from djnewsletter.models import Emails, EmailServers, Domains
from mock import patch
from rest_framework.test import APITestCase

from ifns.handlers import IFNSHandler
from ifns.models import Setting, Requisites
from ifns.tests.mocks.requests import SuccessResponse


class DummyBackendDJNewsletterEmailMessageTests(TestCase):
    def test_send_email(self):
        send_email(
            subject='Subject here',
            body='Here is the <b>message</b>',
            from_email='from@example.com',
            to=['some@email.com'],
        )

        emails = Emails.objects.all()
        self.assertEqual(emails.count(), 0)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Subject here')
        self.assertEqual(Emails.objects.count(), 0)


@override_settings(
    EMAIL_BACKEND='djnewsletter.backends.EmailBackend'
)
@patch('ifns.handlers.IFNSHandler.html_parser')
@patch('ifns.http.IFNSHttpClient.get_nalog')
@patch('ifns.http.IFNSHttpClient.download_file')
class TestIFNS(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.today = datetime.today()
        cls.user = User.objects.create_user(u"test", u"test@email.com", u"test", is_staff=True)
        cls.settings = Setting.objects.create(
            base_url="https://data.nalog.ru/opendata/7707329152-address/",
            current_config={
                "url": "",
                "file_date": "01.01.2001",
                "last_date": "01.01.2001",
                "definition": "https://data.nalog.ru/opendata/7707329152-address/structure-07142014.csv",
                "actuality_date": "01.01.2001"
            }
        )
        domain = Domains.objects.create(domain='email.com')
        cls.email_server = EmailServers.objects.create(
            email_default_from='email@example.com',
            email_host='some host',
            email_port=1234,
            email_username='lame',
            email_password='123',
            email_use_ssl=True,
            email_fail_silently=True,
            email_timeout=50,
            sending_method='smtp',
            is_active=True
        )
        cls.email_server.preferred_domains.add(domain)

    def setUp(self):
        pass

    def test_handler_download_successful_new_requisites(self, mock_download_file, mock_get_nalog, mock_html_parser):
        mock_download_file.return_value = SuccessResponse('data-22122020-structure-07142014.csv')
        with patch.object(transaction, 'on_commit', lambda f: f()):
            ifns_handler = IFNSHandler()
            ifns_handler.specifications = {
                'url': 'https://data.nalog.ru/opendata/7707329152-address/data-22012021-structure-07142014.csv',
                'definition': 'https://data.nalog.ru/opendata/7707329152-address/structure-07142014.csv',
                'last_date': (self.today - timedelta(days=5)).strftime("%d.%m.%Y"),
                'actuality_date': (self.today + timedelta(days=25)).strftime("%d.%m.%Y"),
            }
            ifns_handler.run()
            self.assertEqual(Requisites.objects.count(), 57)
            emails = Emails.objects.all()
            self.assertEqual(emails.count(), 0)
            response = self.client.get(reverse('get_ifns_requisites_by_code', args=['0533']))
            self.assertEqual(
                response.json(),
                {
                    'nalog_code': '0533', 'name': 'Межрайонная инспекция ФНС России № 10 по Республике Дагестан',
                    'address': ',368248,Дагестан Респ,Унцукульский р-н,,Шамилькала п,,,,', 'phone': '257-34271',
                    'additional_Info': 'Код ОКПО: 70498740. Режим работы: понедельник, среда с 9-00 до 18-00, '
                                       'вторник, четверг с 9-00 до 20-00, пятница с 9-00 до 16-45. Суббота, '
                                       'воскресенье-выходные дни',
                    'payment_receiver': 'УФК по Республике Дагестан (Межрайонная инспекция ФНС России № 10 по '
                                        'Республике Дагестан)',
                    'OKTMO_code': '82658300',
                    'receiver_inn': '0533010500',
                    'receiver_kpp': '053301001',
                    'bank_name': 'ОТДЕЛЕНИЕ-НБ РЕСПУБЛИКА ДАГЕСТАН',
                    'bank_account_bik': '048209001',
                    'bank_account_corr': '',
                    'bank_account_number': '40101810600000010021',
                    'registration_code': '05427',
                    'registration_name': 'ИФНС России по Ленинскому району г.Махачкалы',
                    'registration_address': ',367013,,, Махачкала г,, Гамидова пр-кт, д 69, корп б,',
                    'registration_phone': '8722-616568',
                    'registration_add_Info': 'Режим работы: с 9-00 до 18-00, пятница с 9-00 до 17-00, '
                                             'нерабочие дни: суббота, воскресенье',
                    'registration_code_2': '05427',
                    'registration_name_2': 'ИФНС России по Ленинскому району г.Махачкалы',
                    'registration_address_2': ',367013,,, Махачкала г,, Гамидова пр-кт, д 69, корп б,',
                    'registration_phone_2': '8722-616568',
                    'registration_add_Info_2': 'Режим работы: с 9-00 до 18-00, пятница с 9-00 до 17-00, '
                                               'нерабочие дни: суббота, воскресенье'
                }
            )

    def test_handler_download_successful_new_requisites_new_definition(
            self,
            mock_download_file,
            mock_get_nalog,
            mock_html_parser,
    ):
        mock_download_file.return_value = SuccessResponse('data-22122020-structure-07142014.csv')
        with patch.object(transaction, 'on_commit', lambda f: f()):
            ifns_handler = IFNSHandler()
            ifns_handler.specifications = {
                'url': 'https://data.nalog.ru/opendata/7707329152-address/data-22012021-structure-07142014.csv',
                'definition': 'https://data.nalog.ru/opendata/7707329152-address/structure-07142015.csv',
                'last_date': (self.today - timedelta(days=5)).strftime("%d.%m.%Y"),
                'actuality_date': (self.today + timedelta(days=25)).strftime("%d.%m.%Y"),
            }
            ifns_handler.run()
            self.assertEqual(Requisites.objects.count(), 57)
            emails = Emails.objects.all()
            self.assertEqual(emails.count(), 1)

            email_instance = emails[0]
            self.assertEqual(email_instance.recipient, "['test@email.com']")
            self.assertEqual(
                email_instance.subject,
                'Изменилось описание структуры данных сервиса загрузки реквизитов '
                'ИФНС https://data.nalog.ru/opendata/7707329152-address/',
            )
            self.assertEqual(
                email_instance.body,
                'Необходимо проверить изменения. Новая версия - https://data.nalog.ru/opendata/7707329152-address/'
                'data-22012021-structure-07142014.csv',
            )

    def test_handler_download_successful_new_requisites_actuality_date_lt_now(
            self,
            mock_download_file,
            mock_get_nalog,
            mock_html_parser,
    ):
        mock_download_file.return_value = SuccessResponse('data-22122020-structure-07142014.csv')
        with patch.object(transaction, 'on_commit', lambda f: f()):
            ifns_handler = IFNSHandler()
            ifns_handler.specifications = {
                'url': 'https://data.nalog.ru/opendata/7707329152-address/data-22012021-structure-07142014.csv',
                'definition': 'https://data.nalog.ru/opendata/7707329152-address/structure-07142014.csv',
                'last_date': (self.today - timedelta(days=5)).strftime("%d.%m.%Y"),
                'actuality_date': (self.today - timedelta(days=1)).strftime("%d.%m.%Y"),
            }
            ifns_handler.run()
            self.assertEqual(Requisites.objects.count(), 57)
            emails = Emails.objects.all()
            self.assertEqual(emails.count(), 1)

            email_instance = emails[0]
            self.assertEqual(email_instance.recipient, "['test@email.com']")
            self.assertEqual(
                email_instance.subject,
                'Получены неактуальные данные сервиса загрузки реквизитов ИФНС '
                'https://data.nalog.ru/opendata/7707329152-address/',
            )
            self.assertEqual(
                email_instance.body,
                'Срок актуальности {}'.format((self.today - timedelta(days=1)).strftime("%d.%m.%Y")),
            )

    def test_handler_download_error_download(
            self,
            mock_download_file,
            mock_get_nalog,
            mock_html_parser,
    ):
        mock_download_file.return_value = SuccessResponse('data-20012021-structure-07142014.csv')
        with patch.object(transaction, 'on_commit', lambda f: f()):
            ifns_handler = IFNSHandler()
            ifns_handler.specifications = {
                'url': 'https://data.nalog.ru/opendata/7707329152-address/data-20012021-structure-07142014.csv',
                'definition': 'https://data.nalog.ru/opendata/7707329152-address/structure-07142015.csv',
                'last_date': (self.today - timedelta(days=5)).strftime("%d.%m.%Y"),
                'actuality_date': (self.today + timedelta(days=25)).strftime("%d.%m.%Y"),
            }
            ifns_handler.run()
        self.assertEqual(Requisites.objects.count(), 0)
        emails = Emails.objects.all()
        self.assertEqual(emails.count(), 2)

        email_instance = emails[0]
        self.assertEqual(email_instance.recipient, "['test@email.com']")
        self.assertEqual(
            email_instance.subject,
            'Изменилось описание структуры данных сервиса загрузки реквизитов '
            'ИФНС https://data.nalog.ru/opendata/7707329152-address/',
        )
        self.assertEqual(
            email_instance.body,
            'Необходимо проверить изменения. Новая версия - https://data.nalog.ru/opendata/'
            '7707329152-address/data-20012021-structure-07142014.csv',
        )
        email_instance = emails[1]
        self.assertEqual(email_instance.recipient, "['test@email.com']")
        self.assertEqual(
            email_instance.subject,
            'Ошибка обработки данных ИФНС',
        )
        self.assertEqual(
            email_instance.body,
            'Ошибка обработки данных ИФНС: пустой файл',
        )
