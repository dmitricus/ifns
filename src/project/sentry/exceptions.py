class SentryConfigError(Exception):
    pass


class InvalidDsnError(SentryConfigError):
    def __init__(self, dsn):
        self.dsn = dsn

    def __str__(self):
        return 'Неправильный Sentry DSN: {}'.format(self.dsn)
