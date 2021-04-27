"""Convenience imports and helper functions."""
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

from .assignment import (
    WorkflowCollectionAssignmentsView,
    WorkflowCollectionAssignmentView,
)
from .engagement import (
    WorkflowCollectionEngagementsView,
    WorkflowCollectionEngagementView,
)
from .engagement_detail import (
    WorkflowCollectionEngagementDetailsView,
    WorkflowCollectionEngagementDetailView,
)

from .recommendation import (
    WorkflowCollectionRecommendationsView,
    WorkflowCollectionRecommendationView,
)

from .subscription import (
    WorkflowCollectionSubscriptionsView,
    WorkflowCollectionSubscriptionView,
)


__all__ = [
    "WorkflowCollectionAssignmentsView",
    "WorkflowCollectionAssignmentView",
    "WorkflowCollectionEngagementsView",
    "WorkflowCollectionEngagementView",
    "WorkflowCollectionEngagementDetailsView",
    "WorkflowCollectionEngagementDetailView",
    "WorkflowCollectionRecommendationsView",
    "WorkflowCollectionRecommendationView",
    "WorkflowCollectionSubscriptionsView",
    "WorkflowCollectionSubscriptionView",
    "workflow_user_data_api_root",
]


@api_view(["GET"])
def workflow_user_data_api_root(request, format=None):
    """
    Overview of available resources in this API.
    """
    return Response(
        {
            "user-workflow-collection-assignments": reverse(
                "user-workflow-assignments", request=request, format=format
            ),
            "user-workflow-collection-engagements": reverse(
                "user-workflow-collection-engagements", request=request, format=format
            ),
            "user-workflow-collection-recommendations": reverse(
                "user-workflow-recommendations", request=request, format=format
            ),
            "user-workflow-collection-subscriptions": reverse(
                "user-workflow-collection-subscriptions", request=request, format=format
            ),
        }
    )
