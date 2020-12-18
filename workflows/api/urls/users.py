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
from django.conf.urls import url
from django.urls import path

from ..views import user

# Workflow User Endpoints
user_endpoints = [
    path('self/workflows/engagements/',
         user.workflows.WorkflowCollectionEngagementsView.as_view(),
         name='user-workflow-collection-engagements-v3'),
    path('self/workflows/engagements/<uuid:id>/',
         user.workflows.WorkflowCollectionEngagementView.as_view(),
         name='user-workflow-collection-engagement-v3'),
    path('self/workflows/engagements/<uuid:id>/details/',
         user.workflows.WorkflowCollectionEngagementDetailsView.as_view(),
         name='user-workflow-collection-engagement-details-v3'),
    path('self/workflows/engagements/<uuid:engagement_id>/details/<uuid:id>/',
         user.workflows.WorkflowCollectionEngagementDetailView.as_view(),
         name='user-workflow-collection-engagement-detail-v3'),
    path('self/workflows/subscriptions/',
         user.workflows.WorkflowCollectionSubscriptionsView.as_view(),
         name='user-workflow-collection-subscriptions-v3'),
    path('self/workflows/subscriptions/<uuid:id>/',
         user.workflows.WorkflowCollectionSubscriptionView.as_view(),
         name='user-workflow-collection-subscription-v3'),
    path('self/workflows/assignments/',
         user.workflows.WorkflowCollectionAssignmentsView.as_view(),
         name='user-workflow-assignments-v3'),
    path('self/workflows/assignments/<uuid:id>/',
         user.workflows.WorkflowCollectionAssignmentView.as_view(),
         name='user-workflow-assignment-v3')
]
