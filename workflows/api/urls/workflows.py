"""
API endpoint definitions for Workflow Resources
"""
from django.urls import path

from ..views import workflows


workflow_endpoints = [
    path('', workflows.workflow_api_root, name='workflows-root-v3'),
    path('workflows/', workflows.WorkflowsView.as_view(), name='workflows-v3'),
    path('workflows/<uuid:id>/',
         workflows.WorkflowView.as_view(), name='workflow-v3'),
    path('authors/', workflows.WorkflowAuthorsView.as_view(),
         name='workflow-authors-v3'),
    path('authors/<uuid:id>/', workflows.WorkflowAuthorView.as_view(),
         name='workflow-author-v3'),
    path('collections/', workflows.WorkflowCollectionsView.as_view(),
         name='workflow-collections-v3'),
    path('collections/<uuid:id>/', workflows.WorkflowCollectionView.as_view(),
         name='workflow-collection-v3'),
]
