from django.apps import AppConfig


class WorkflowsConfig(AppConfig):
    name = 'workflows'

    def ready(self):
        print("Warning: DRF Authentication settings have not been set. "
              "The application will default to session auth and basic auth. "
              "See https://www.django-rest-framework.org/api-guide/authentication/#setting-the-authentication-scheme")
