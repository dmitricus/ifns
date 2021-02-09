import sentry_sdk
from django.conf import settings
from django.http import (
    HttpResponseBadRequest,
    HttpResponseNotFound,
    HttpResponseForbidden,
    HttpResponseGone,
    HttpResponseServerError,
    JsonResponse,
)
from django.views.generic import View


class Http400(Exception):
    pass


class Http404(Exception):
    pass


class Http403(Exception):
    pass


class Http410(Exception):
    pass


class Http500(Exception):
    pass


class SentryView(View):

    def __init__(self):
        self.error_code_dict = self._dict_error()
        super().__init__()

    def get(self, request, *args, **kwargs):
        from project.sentry import SentryConfig
        error_code = request.GET.get('error_code')
        if error_code in self.error_code_dict:
            return self._generate_error(error_code)
        sentry_config = SentryConfig().get_public_dsn()
        release = settings.SENTRY_CONFIG.get('release')
        return JsonResponse(
            {
                'message': {
                    'sentry_dsn': 'OK' if sentry_config else 'an empty sentry_dsn',
                    'release': 'OK' if release else 'an empty release',
                    'error_code parameters': list(self.error_code_dict.keys()),
                    'test error': 'sentry/?error_code=500'
                }
            },
        )

    @staticmethod
    def _dict_error():
        errors = {
            '400': [Http400, HttpResponseBadRequest],
            '404': [Http404, HttpResponseNotFound],
            '403': [Http403, HttpResponseForbidden],
            '410': [Http410, HttpResponseGone],
            '500': [Http500, HttpResponseServerError],
            'ZeroDivisionError': [ZeroDivisionError, HttpResponseServerError],
        }
        return errors

    def _generate_error(self, error_code):
        message_error = 'TEST ERROR ({})'.format(error_code)
        if error_code:
            try:
                raise self.error_code_dict[error_code][0](message_error)
            except self.error_code_dict[error_code][0] as e:
                sentry_sdk.capture_exception(e)
                return self.error_code_dict[error_code][1](
                    '<h1>{}</h1>'.format(message_error),
                    content_type='text/html',
                )
