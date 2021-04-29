# Django Workflow System

# Requirements

- Python (3.5, 3.6, 3.7, 3.8)
- Django (3.1+)

We **highly recommend** and only officially support the latest patch release of
each Python and Django series.

# Installation

`pip install django-workflow-system`

# Post-Install Setup

**Django Settings Additions**

```python
# You will need to add django_workflow_system and rest_framework to your installed apps
INSTALLED_APPS = [
    "django_workflow_system",
    "rest_framework",
    ...]

# You will need to add some authentication classes for DRF, more info can be found at https://www.django-rest-framework.org/api-guide/settings/
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        # "rest_framework.authentication.BasicAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}
```



[![crc-logo]][crc-site]

[crc-logo]: https://docs.crc.nd.edu/_static/CRC_Logo.png
[crc-site]: https://crc.nd.edu/