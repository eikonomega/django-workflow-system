"""
URL route definitions for api_v2

Of importance (and perhaps in error) the OAuth2 endpoints are
including undernearth the `/api_v2` url segment.

In theory this will allow us to use a different OAuth2 mechanism
for future versions of the API with less friction.  We will see
how that plays out in practice.
"""

from django.conf.urls import include
from django.urls import path

from ..views import api_root

from .users import user_endpoints

from .workflows import workflow_endpoints


urlpatterns = [
    # path('oauth2/', include(oauth2_endpoints)),
    path('api-auth/', include('rest_framework.urls')),
    path('workflow_system/users/', include(user_endpoints)),
    path('workflow_system/', include(workflow_endpoints)),
    path('', api_root)
]
