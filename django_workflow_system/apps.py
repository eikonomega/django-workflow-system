from django.apps import AppConfig
from django.conf import settings


class DjangoWorkflowSystemConfig(AppConfig):
    name = "django_workflow_system"

    def ready(self):
        warning = (
            "Warning: Some Django Rest Framework settings have not been set. We recommend "
            "setting them to avoid any unwanted security gaps. For more information see "
            "https://www.django-rest-framework.org/api-guide/authentication/#setting-"
            "the-authentication-scheme"
        )

        try:
            rest_framework_settings = settings.REST_FRAMEWORK
        except AttributeError:
            print(warning)
            return

        rest_framework_settings_keys = rest_framework_settings.keys()

        if "DEFAULT_AUTHENTICATION_CLASSES" not in rest_framework_settings_keys:
            print(warning)
            return

        if "DEFAULT_PERMISSION_CLASSES" not in rest_framework_settings_keys:
            print(warning)
            return
