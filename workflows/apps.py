from django.apps import AppConfig
from django.conf import settings


class WorkflowsConfig(AppConfig):
    name = 'workflows'

    def ready(self):
        if settings.AUTHENTICATION_BACKENDS == ['django.contrib.auth.backends.ModelBackend']:
            print("Warning: DRF Authentication settings have not been set. "
                  "The application will default to session auth and basic auth. "
                  "For more information see https://www.django-rest-framework.org/api-guide/authentication/#setting-the-authentication-scheme")
