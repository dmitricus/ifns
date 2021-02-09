from urllib.parse import urlparse, urlunparse

from django.conf import settings

from .exceptions import InvalidDsnError


class SentryConfig:
    def __init__(self):
        self.dsn = settings.SENTRY_CONFIG.get('dsn')
        self.release = settings.SENTRY_CONFIG.get('release')

    def as_dict(self):
        return {
            'dsn': self.get_public_dsn(),
            'release': self.release,
        }

    def get_public_dsn(self):
        if not self.dsn:
            return self.dsn

        url_obj = urlparse(self.dsn)
        if not all([url_obj.username, url_obj.hostname]):
            raise InvalidDsnError(self.dsn)

        # Удаляем секретный ключ из DSN, если он там присутствует
        netloc = '{}@{}'.format(url_obj.username, url_obj.hostname)
        if url_obj.port:
            netloc += ':{}'.format(url_obj.port)

        return urlunparse([
            url_obj.scheme,
            netloc,
            url_obj.path,
            '',
            '',
            '',
        ])
