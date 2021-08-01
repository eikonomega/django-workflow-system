# Django Workflow System

[![pypi-version]][pypi]

**Finally, an awesome Django Workflow System.**

Full documentation for the package is currently being written....but for now, here's what you need to get up and running.

**NOTE: THIS PROJECT IS STILL IN BETA, BREAKING CHANGES COULD BE INTRODUCED AT ANY TIME**

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

In your main urls.py file you will need to add the following line:
```python
path('api/', include('django_workflow_system.api.urls'))
```
`'api/'` can be whatever you want.

[pypi-version]: https://img.shields.io/pypi/v/django-workflow-system.svg
[pypi]: https://pypi.org/project/django-workflow-system/
