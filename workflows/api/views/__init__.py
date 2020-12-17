"""
SECURITY INFO
Default Authentication/Permission for API views are defined
in the settings files for your environment. Make sure that you are
aware of what is set there.

You can override these defaults on a per class basis by added
class attributes like so:
    from rest_framework import status, permissions, authentication
    from oauth2_provider.contrib.rest_framework import (
        TokenHasReadWriteScope, TokenHasScope, IsAuthenticatedOrTokenHasScope)
    from oauth2_provider.contrib.rest_framework import (
        authentication as oauth2_authentication,
        permissions as oauth2_permissions)

    # Inside you APIView classes set the following attributes...
    authentication_classes = [
        authentication.SessionAuthentication,
        oauth2_authentication.OAuth2Authentication
    ]

    permission_classes = [
        oauth2_permissions.IsAuthenticatedOrTokenHasScope]
"""

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse


@api_view(['GET'])
def api_root(request, format=None):
    """
    Overview of available resources in this API.
    """
    return Response({
        'workflows': reverse(
            'workflows-root-v3', request=request, format=format)
    })
