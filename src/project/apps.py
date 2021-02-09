import sentry_sdk
from django.apps import AppConfig
from sentry_sdk.integrations.django import DjangoIntegration


class ProjectConfig(AppConfig):
    name = 'project'

    def ready(self):
        self._setup_sentry()

    def _setup_sentry(self):
        from project.sentry import SentryConfig

        sentry_config = SentryConfig().as_dict()
        sentry_sdk.init(
            dsn=sentry_config['dsn'],
            release=sentry_config['release'],
            send_default_pii=True,
            integrations=[
                DjangoIntegration(),
            ],
        )
