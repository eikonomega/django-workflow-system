"""
API endpoint definitions for views related to User Resources
Notes
-----
There are endpoint definitions here that may seem out of place
at first. In particular, those related to specific features
like Map-Your-Day, Workflows, etc.
The reason they exist here is that they are access via a specific
user resource.
"""
from django.urls import path

from ..views import user

from ..views.user.workflows import workflow_user_data_api_root

# Workflow User Endpoints
user_endpoints = [
    path("", workflow_user_data_api_root, name="workflow-user-data-root"),
    path(
        "self/workflows/engagements/",
        user.workflows.WorkflowCollectionEngagementsView.as_view(),
        name="user-workflow-collection-engagements",
    ),
    path(
        "self/workflows/engagements/<uuid:id>/",
        user.workflows.WorkflowCollectionEngagementView.as_view(),
        name="user-workflow-collection-engagement",
    ),
    path(
        "self/workflows/engagements/<uuid:id>/details/",
        user.workflows.WorkflowCollectionEngagementDetailsView.as_view(),
        name="user-workflow-collection-engagement-details",
    ),
    path(
        "self/workflows/engagements/<uuid:engagement_id>/details/<uuid:id>/",
        user.workflows.WorkflowCollectionEngagementDetailView.as_view(),
        name="user-workflow-collection-engagement-detail",
    ),
    path(
        "self/workflows/subscriptions/",
        user.workflows.WorkflowCollectionSubscriptionsView.as_view(),
        name="user-workflow-collection-subscriptions",
    ),
    path(
        "self/workflows/subscriptions/<uuid:id>/",
        user.workflows.WorkflowCollectionSubscriptionView.as_view(),
        name="user-workflow-collection-subscription",
    ),
    path(
        "self/workflows/assignments/",
        user.workflows.WorkflowCollectionAssignmentsView.as_view(),
        name="user-workflow-assignments",
    ),
    path(
        "self/workflows/assignments/<uuid:id>/",
        user.workflows.WorkflowCollectionAssignmentView.as_view(),
        name="user-workflow-assignment",
    ),
    path(
        "self/workflows/recommendations/",
        user.workflows.WorkflowCollectionRecommendationsView.as_view(),
        name="user-workflow-recommendations",
    ),
    path(
        "self/workflows/recommendations/<uuid:id>/",
        user.workflows.recommendation.WorkflowCollectionRecommendationView.as_view(),
        name="user-workflow-recommendation",
    ),
]
