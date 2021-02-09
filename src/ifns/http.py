import logging
from itertools import takewhile

from cachecontrol import CacheControl
from django.utils.translation import gettext as _
from requests import Session
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from ifns.models import Setting


class RetryRequest(Retry):
    DEFAULT_METHOD_WHITELIST = frozenset(
        ["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE"]
    )

    RETRY_AFTER_STATUS_CODES = frozenset([413, 429, 503])

    DEFAULT_REDIRECT_HEADERS_BLACKLIST = frozenset(["Authorization"])

    def __init__(
            self,
            total=10,
            connect=None,
            read=None,
            redirect=None,
            status=None,
            method_whitelist=DEFAULT_METHOD_WHITELIST,
            status_forcelist=None,
            backoff_factor=0,
            raise_on_redirect=True,
            raise_on_status=True,
            history=None,
            respect_retry_after_header=True,
            remove_headers_on_redirect=DEFAULT_REDIRECT_HEADERS_BLACKLIST,
            max_backoff=3600
    ):
        super().__init__()
        self.total = total
        self.connect = connect
        self.read = read
        self.status = status

        if redirect is False or total is False:
            redirect = 0
            raise_on_redirect = False

        self.redirect = redirect
        self.status_forcelist = status_forcelist or set()
        self.method_whitelist = method_whitelist
        self.backoff_factor = backoff_factor
        self.raise_on_redirect = raise_on_redirect
        self.raise_on_status = raise_on_status
        self.history = history or tuple()
        self.respect_retry_after_header = respect_retry_after_header
        self.remove_headers_on_redirect = frozenset(
            [h.lower() for h in remove_headers_on_redirect]
        )
        self.max_backoff = max_backoff
        self.logger = logging.getLogger('RetryRequest')

    @staticmethod
    def convert(seconds):
        seconds = seconds % (24 * 3600)
        hour = seconds // 3600
        seconds %= 3600
        minutes = seconds // 60
        seconds %= 60
        return "%d:%02d:%02d" % (hour, minutes, seconds)

    def get_backoff_time(self):
        consecutive_errors_len = len(
            list(
                takewhile(lambda x: x.redirect_location is None, reversed(self.history))
            )
        )
        if consecutive_errors_len <= 1:
            return 0

        backoff_value = self.backoff_factor * (consecutive_errors_len - 1)
        self.logger.debug(
            _(
                'попытка № {} '
                'Следующая попытка через {} '
                'максимальное время {}'.format(
                    consecutive_errors_len,
                    self.convert(backoff_value),
                    self.convert(self.max_backoff)
                )
            )
        )
        return min(self.max_backoff, backoff_value)


class MakeRetrySessionMixin(object):
    total_retries = 5
    backoff_factor = 600
    status_forcelist = None
    cache_for_session = None
    cache_session = None
    retry_session = None

    def make_retry_session(self):
        self.retry_session = self._requests_retry_session()
        if self.cache_for_session:
            self.cache_session = CacheControl(self._requests_retry_session(), self.cache_for_session)

    def _requests_retry_session(self):
        if self.status_forcelist is None:
            self.status_forcelist = (404, 500, 502, 503, 504)

        session = Session()
        retry = RetryRequest(
            total=self.total_retries,
            backoff_factor=self.backoff_factor,
            status_forcelist=self.status_forcelist,
            method_whitelist=frozenset(['GET', 'POST']),
            max_backoff=3600
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)

        return session

    def retry_get(self, url, **kwargs):
        if self.cache_session:
            return self.cache_session.get(url=url, **kwargs)
        return self.retry_session.get(url=url, **kwargs)

    def retry_post(self, url, data=None, json=None, **kwargs):
        return self.retry_session.post(url=url, data=data, json=json, **kwargs)


class IFNSHttpClient(MakeRetrySessionMixin):
    def __init__(self):
        self.make_retry_session()
        self._setting = Setting.objects.first()
        self.base_url = self._setting.base_url
        self.current_config = self._setting.current_config

    def get_nalog(self, **kwargs):
        response = self.retry_get(self.base_url, **kwargs)
        response.raise_for_status()
        return response

    def download_file(self, url, **kwargs):
        response = self.retry_get(url, **kwargs)
        response.raise_for_status()
        return response
