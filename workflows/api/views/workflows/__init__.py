from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

from ..workflows.author import WorkflowAuthorsView, WorkflowAuthorView
from ..workflows.collection import (
    WorkflowCollectionsView, WorkflowCollectionView)
from ..workflows.workflow import WorkflowsView, WorkflowView

@api_view(['GET'])
def workflow_api_root(request, format=None):
    """
    Overview of available resources in this API.
    """
    return Response({
        'workflows': reverse('workflows-v3', request=request, format=format),
        'workflow-authors': reverse('workflow-authors-v3', request=request, format=format),
        'workflow-collections': reverse('workflow-collections-v3', request=request, format=format),
    })

__all__ = [
    'WorkflowAuthorsView',
    'WorkflowAuthorView',
    'WorkflowsView',
    'WorkflowView',
    'WorkflowCollectionsView',
    'WorkflowCollectionView',
    'workflow_api_root',
]
