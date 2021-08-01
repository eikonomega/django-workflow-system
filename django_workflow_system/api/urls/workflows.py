"""
API endpoint definitions for Workflow Resources
"""
from django.urls import path

from ..views import workflows, workflow_api_root

workflow_endpoints = [
    path("", workflow_api_root, name="workflow-system-root"),
    path("workflows/", workflows.WorkflowsView.as_view(), name="workflows"),
    path("workflows/<uuid:id>/", workflows.WorkflowView.as_view(), name="workflow"),
    path("authors/", workflows.WorkflowAuthorsView.as_view(), name="workflow-authors"),
    path(
        "authors/<uuid:id>/",
        workflows.WorkflowAuthorView.as_view(),
        name="workflow-author",
    ),
    path(
        "collections/",
        workflows.WorkflowCollectionsView.as_view(),
        name="workflow-collections",
    ),
    path(
        "collections/<uuid:id>/",
        workflows.WorkflowCollectionView.as_view(),
        name="workflow-collection",
    ),
]
