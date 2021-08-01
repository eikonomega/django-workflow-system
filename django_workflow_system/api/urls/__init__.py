"""
URL route definitions for api_v2

Of importance (and perhaps in error) the OAuth2 endpoints are
including underneath the `/api_v2` url segment.

In theory this will allow us to use a different OAuth2 mechanism
for future versions of the API with less friction.  We will see
how that plays out in practice.
"""

from django.conf.urls import include
from django.urls import path


from .users import user_endpoints

from .workflows import workflow_endpoints
from ..views import workflow_api_root
from django_workflow_system.views import get_user_input_type_helper

urlpatterns = [
    path(
        "step_user_input_type_helper/",
        get_user_input_type_helper,
        name="step_user_input_type_helper",
    ),
    path("workflow_system/users/", include(user_endpoints)),
    path("workflow_system/", include(workflow_endpoints)),
    path("", workflow_api_root),
]
